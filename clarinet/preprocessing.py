from concurrent.futures import ProcessPoolExecutor
from functools import partial
import numpy as np
import os
import librosa
from multiprocessing import cpu_count
import argparse
import pretty_midi
import time

# cpt = 0 #TO RM

def midi2wav(midi_path):
    #remove the .mid or .midi extension
    (filename, ext) = os.path.splitext(midi_path)

    wav_name = filename + '.wav'

    #use timidity to convert the MIDI to a wav equivalent
    command = "timidity " + midi_path + " -Ow -o" + wav_name + " > stderr"
    os.system(command)

    wav , sr = librosa.load(wav_name, sr=22050) #TODO sr = 44100 ?

    command = "rm " + wav_name

    os.system(command)

    return wav

def build_from_path(in_dir, out_dir, dataset_name, num_workers=1):
    executor = ProcessPoolExecutor(max_workers=num_workers)
    futures = []
    index = 1
    with open(os.path.join(in_dir, 'metadata.csv'), encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')

            midi_path = os.path.join(in_dir, 'midi','%s' % parts[0])
            wav_path = os.path.join(in_dir, 'wav', '%s' % parts[1])

            futures.append(executor.submit(
                partial(_process_utterance, out_dir, index, wav_path, midi_path, dataset_name))) #modified
            index += 1
    print(midi_path + " , " + wav_path)
    print(cpt)
    return [future.result() for future in futures]


def _process_utterance(out_dir, index, wav_path, midi_path, dataset_name):
    # Load the audio to a numpy array:
    wav, sr = librosa.load(wav_path, sr=22050) #TODO sr = 44100 ?

    wav = wav / np.abs(wav).max() * 0.999
    out = wav

    # Load the audio from the midi to a numpy array
    wav_midi = midi2wav(midi_path)
    wav_midi = wav_midi / np.abs(wav_midi).max() * 0.999

    constant_values = 0.0
    out_dtype = np.float32
    n_fft = 1024
    hop_length = 256
    reference = 20.0
    min_db = -100
    #TODO compute fmax according to sr ?

    # Compute a mel-scale spectrogram from the trimmed wav:
    # (N, D)
    mel_spectrogram = librosa.feature.melspectrogram(wav_midi, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=80, fmin=125, fmax=7600).T

    # mel_spectrogram = np.round(mel_spectrogram, decimals=2)
    mel_spectrogram = 20 * np.log10(np.maximum(1e-4, mel_spectrogram)) - reference
    mel_spectrogram = np.clip((mel_spectrogram - min_db) / (-min_db), 0, 1)

    pad = (out.shape[0] // hop_length + 1) * hop_length - out.shape[0]
    pad_l = pad // 2
    pad_r = pad // 2 + pad % 2

    # zero pad for quantized signal
    out = np.pad(out, (pad_l, pad_r), mode="constant", constant_values=constant_values)
    N = mel_spectrogram.shape[0]
    try:
        assert len(out) >= N * hop_length
    except:
        except_size = N * hop_length
        print(wav_path)
        print(str(len(out)) + " sup or equal to %d" % except_size)
        diff = except_size - len(out)
        ratio = except_size / len(out)
        print("diff: " + str(diff) + " ratio: " + str(ratio))
        # cpt += 1

    # time resolution adjustment
    # ensure length of raw audio is multiple of hop_size so that we can use
    # transposed convolution to upsample
    out = out[:N * hop_length]
    assert len(out) % hop_length == 0

    timesteps = len(out)

    # Write the spectrograms to disk:
    audio_filename = dataset_name + '-audio-%05d.npy' % index #modified
    mel_filename = dataset_name + '-mel-%05d.npy' % index #modified
    midi_filename = dataset_name + '-midi-%05d.npy' % index #added

    np.save(os.path.join(out_dir, audio_filename),
            out.astype(out_dtype), allow_pickle=False)
    np.save(os.path.join(out_dir, mel_filename),
            mel_spectrogram.astype(np.float32), allow_pickle=False)

    ## TODO: something to the .mid file ( midi_path)? # TODO: be sure to open the corresponding midi/wav files
    midi_data = pretty_midi.PrettyMIDI(midi_path)

    midi_numpy = midi_data.get_piano_roll() #Added
    np.save(os.path.join(out_dir, midi_filename),
            midi_numpy.astype(np.float32), allow_pickle=False)

    # Return a tuple describing this training example:
    return audio_filename, mel_filename, timesteps, midi_filename #modified


def preprocess(in_dir, out_dir, num_workers, dataset_name):
    os.makedirs(out_dir, exist_ok=True)
    metadata = build_from_path(in_dir, out_dir, num_workers, dataset_name)
    write_metadata(metadata, out_dir)


def write_metadata(metadata, out_dir):
    with open(os.path.join(out_dir, 'train.txt'), 'w', encoding='utf-8') as f:
        for m in metadata:
            f.write('|'.join([str(x) for x in m]) + '\n')
    frames = sum([m[2] for m in metadata])
    sr = 22050
    hours = frames / sr / 3600
    print('Wrote %d utterances, %d time steps (%.2f hours)' % (len(metadata), frames, hours))
    print('Max input length:  %d' % max(len(m[3]) for m in metadata))
    print('Max output length: %d' % max(m[2] for m in metadata))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocessing',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--in_dir', '-i', type=str, default='./maestro/', help='In Directory')
    parser.add_argument('--out_dir', '-o', type=str, default='./DATASETS/maestro/', help='Out Directory')
    parser.add_argument('--name', '-n', type=str, default='./DATASETS/maestro/', help='Dataset name')

    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)


    num_workers = cpu_count()
    start = time.time()

    preprocess(args.in_dir, args.out_dir, args.name, num_workers)

    end = time.time()
    print("--- %s seconds ---" % (end - start))
