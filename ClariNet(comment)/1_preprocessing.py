from concurrent.futures import ProcessPoolExecutor
from functools import partial
import numpy as np
import os
import librosa
from multiprocessing import cpu_count
import argparse


def build_from_path(in_dir, out_dir, num_workers=1): #2 split metadata files, launch process utterance function with wav path and corresponding text, return sum of append.
    executor = ProcessPoolExecutor(max_workers=num_workers) #create object for asynchronimous call (depending of the number of cpu) 
    futures = []
    index = 1
    with open(os.path.join(in_dir, 'metadata.csv'), encoding='utf-8') as f: #open metadata.csv and for every line in the file 
        for line in f:
            parts = line.strip().split('|')#cut after see a '|'
            wav_path = os.path.join(in_dir, 'wavs', '%s.wav' % parts[0]) #join name wav
            text = parts[2] #correspond to the text writen in the csv file
            futures.append(executor.submit( #store in futures array the result of process utterance (use executor object to launch asynchronimous call and partial function)  
                partial(_process_utterance, out_dir, index, wav_path, text)))
            index += 1
    return [future.result() for future in futures]


def _process_utterance(out_dir, index, wav_path, text):#3 compute mel spectrogram for corresponding wav, do something after ?, write spectrogram and return audio_filename, mel_filename, timesteps, text. 
    # Load the audio to a numpy array:
    wav, sr = librosa.load(wav_path, sr=22050) 

    wav = wav / np.abs(wav).max() * 0.999
    out = wav
    constant_values = 0.0
    out_dtype = np.float32
    n_fft = 1024
    hop_length = 256
    reference = 20.0
    min_db = -100

    # Compute a mel-scale spectrogram from the trimmed wav:
    # (N, D)
    mel_spectrogram = librosa.feature.melspectrogram(wav, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=80, fmin=125, fmax=7600).T #(audio time, sampling rate, spectrogram, length of the FFT window, number of Mel bands to generate, lowest frequency (in Hz), highest frequency (in Hz))

    # mel_spectrogram = np.round(mel_spectrogram, decimals=2)
    mel_spectrogram = 20 * np.log10(np.maximum(1e-4, mel_spectrogram)) - reference #recadrage ? 
    mel_spectrogram = np.clip((mel_spectrogram - min_db) / (-min_db), 0, 1) #clip = Clip (limit) the values in an array. Given an interval, values outside the interval are clipped to the interval edges 

    pad = (out.shape[0] // hop_length + 1) * hop_length - out.shape[0] # ? 
    pad_l = pad // 2
    pad_r = pad // 2 + pad % 2

    # zero pad for quantized signal
    out = np.pad(out, (pad_l, pad_r), mode="constant", constant_values=constant_values)
    N = mel_spectrogram.shape[0]
    assert len(out) >= N * hop_length

    # time resolution adjustment
    # ensure length of raw audio is multiple of hop_size so that we can use
    # transposed convolution to upsample
    out = out[:N * hop_length]
    assert len(out) % hop_length == 0

    timesteps = len(out)

    # Write the spectrograms to disk:
    audio_filename = 'ljspeech-audio-%05d.npy' % index
    mel_filename = 'ljspeech-mel-%05d.npy' % index
    np.save(os.path.join(out_dir, audio_filename),
            out.astype(out_dtype), allow_pickle=False)
    np.save(os.path.join(out_dir, mel_filename),
            mel_spectrogram.astype(np.float32), allow_pickle=False)

    # Return a tuple describing this training example:
    return audio_filename, mel_filename, timesteps, text


def preprocess(in_dir, out_dir, num_workers): #1 recursive directory creation function + launch buid from path function + launch write metadata function to write in out dir
    os.makedirs(out_dir, exist_ok=True)
    metadata = build_from_path(in_dir, out_dir, num_workers)
    write_metadata(metadata, out_dir)


def write_metadata(metadata, out_dir): #4 write metadata result in file + print informations
    with open(os.path.join(out_dir, 'train.txt'), 'w', encoding='utf-8') as f:
        for m in metadata:
            f.write('|'.join([str(x) for x in m]) + '\n')
    frames = sum([m[2] for m in metadata])
    sr = 22050
    hours = frames / sr / 3600
    print('Wrote %d utterances, %d time steps (%.2f hours)' % (len(metadata), frames, hours))
    print('Max input length:  %d' % max(len(m[3]) for m in metadata))
    print('Max output length: %d' % max(m[2] for m in metadata))


if __name__ == "__main__": #0 parsing arguments + count nb cpu + launch preprocess function
    parser = argparse.ArgumentParser(description='Preprocessing',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--in_dir', '-i', type=str, default='./', help='In Directory')
    parser.add_argument('--out_dir', '-o', type=str, default='./', help='Out Directory')
    args = parser.parse_args()

    num_workers = cpu_count()
    preprocess(args.in_dir, args.out_dir, num_workers)


#La classe ProcessPoolExecutor est une sous-classe Executor qui utilise un pool de processus pour exécuter des appels de manière asynchrone. ProcessPoolExecutor utilise le module de multitraitement, ce qui lui permet de contourner le verrou d'interprète global, mais signifie également que seuls les objets pouvant être sélectionnés peuvent être exécutés et renvoyés.
