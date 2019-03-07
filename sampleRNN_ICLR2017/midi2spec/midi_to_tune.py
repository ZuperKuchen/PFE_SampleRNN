import argparse
import librosa, librosa.display
import matplotlib.pyplot as plt
import numpy as np
import numpy.fft as fft
import os
import sys


def compute_mel_spec(midi_path , wav_path, png_path, mel_path, sample_rate, frame_size):

    for midi in os.listdir(midi_path):

        #remove the .mid or .midi extension
        (filename, ext) = os.path.splitext(midi)

        wav_name = filename + '.wav'

        #use timidity to convert the MIDI to a wav equivalent
        command = "timidity " + midi_path + midi + " -Ow -o" + wav_path + wav_name
        os.system(command)

        #spectral representation of the signal
        [signal, sample_rate] = librosa.load(wav_path + wav_name)

        mel_spec = librosa.feature.melspectrogram(y = signal, sr = sample_rate)

        max_freq = sample_rate / 2.0


        #ClariNet version of mel spectrogram
        reference = 20.0
        min_db = -100

        mel_spectrogram = mel_spec
        mel_spectrogram = 20 * np.log10(np.maximum(1e-4, mel_spectrogram)) - reference
        mel_spectrogram = np.clip((mel_spectrogram - min_db) / (-min_db), 0, 1)


        #displaying the computed mel_spectrogram simple version
        plt.figure(figsize=(10,4))
        librosa.display.specshow(librosa.power_to_db(mel_spec, ref=np.max), y_axis='mel', fmax=max_freq, x_axis='time')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Mel spectrogram')
        plt.tight_layout()
        #plt.show()
        #save under 'mel_spec_name.png' format
        png_filename = png_path + 'mel_spec_' + filename + '.png'
        plt.savefig(png_filename)


        #displaying the computed mel_spectrogram ClariNet version
        plt.figure(figsize=(10,4))
        librosa.display.specshow(librosa.power_to_db(mel_spectrogram, ref=np.max), y_axis='mel', fmax=max_freq, x_axis='time')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Mel spectrogram ClariNet')
        plt.tight_layout()
        #plt.show()
        #save under 'mel_spec_name.png' format
        png_filename = png_path + 'mel_spec2_' + filename + '.png'
        plt.savefig(png_filename)


        # Write the spectrogram to disk:
        mel_filename = 'mel_' + filename + '.npy'
        print('mel_filename : ', mel_filename)
        np.save(os.path.join(mel_path, mel_filename), mel_spec.astype(np.float32))
        # np.save(os.path.join(mel_path, mel_filename), mel_spec.astype(np.float32, allow_pickle=False))



#main
if __name__ == '__main__':
    #argument parser
    parser = argparse.ArgumentParser(description='computing mel spectrograms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--midi_path', type=str, default='./MIDI/', help='Midi Files Path')
    parser.add_argument('--sample_rate', type=int, default=44100, help='Sample rate')
    parser.add_argument('--frame_size', type=int, default=1024, help='Frame size')
    parser.add_argument('--mel_path', type=str, default='./mel_spec/', help='Folder to save .npy mel spectrograms')
    parser.add_argument('--png_path', type=str, default='./png_mel/', help='Folder to save .png mel spectrograms')
    parser.add_argument('--wav_path', type=str, default='./WAV/', help='Folder to save .wav converted midi files')

    args = parser.parse_args()

    sample_rate = args.sample_rate
    frame_size = args.frame_size
    midi_path = args.midi_path
    wav_path = args.wav_path
    png_path = args.png_path
    mel_path = args.mel_path

    print("SR : ",sample_rate)
    print("FS : ",frame_size)
    print("midi folder : ",midi_path)
    print("wav folder : ", wav_path)
    print(".npy folder : ", mel_path)
    print(".png folder : ", png_path)

    # Init directories
    if not os.path.isdir(args.wav_path):
        os.makedirs(args.wav_path)
    if not os.path.isdir(args.midi_path):
        os.makedirs(args.midi_path)
    if not os.path.isdir(args.mel_path):
        os.makedirs(args.mel_path)
    if not os.path.isdir(args.png_path):
        os.makedirs(args.png_path)


    compute_mel_spec(midi_path, wav_path, png_path, mel_path, sample_rate, frame_size)
