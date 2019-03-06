import argparse
import librosa, librosa.display
import matplotlib.pyplot as plt
import numpy as np
import numpy.fft as fft
import os
import sys


def compute_mel_spec(midi_path , wav_path, sample_rate, frame_size):
    #use timidity to convert the MIDI to a wav equivalent
    command = "timidity " + midi_path + " -Ow -o" + wav_path
    os.system(command)


    #spectral representation of the signal
    [signal, sample_rate] = librosa.load(wav_path)

    mel_spec = librosa.feature.melspectrogram(y = signal, sr = sample_rate)

    max_freq = sample_rate / 2.0
    #displaying the computed mel_spectrogram
    plt.figure(figsize=(10,4))
    librosa.display.specshow(librosa.power_to_db(mel_spec, ref=np.max), y_axis='mel', fmax=max_freq, x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel spectrogram')
    plt.tight_layout()
    #plt.show()
    #save under 'mel_spec_name.png' format
    plt.savefig('mel_spec_' + midi_path[0:len(midi_path) - 4] + '.png')

    #TODO save mel_spec in .npy file

    return mel_spec



#main
if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='computing mel spectrograms', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    #parser.add_argument('--midi_path', type=str, default='./', help='Midi Files Path') #TODO change directory
    parser.add_argument('--sample_rate', type=int, default=44100, help='Sample rate')
    parser.add_argument('--frame_size', type=int, default=1024, help='Frame size')
    #parser.add_argument('--mel_path', type=str, default='./', help='Folder to save .npy mel spectrograms') #TODO change directory

    #TEMP to rm
    parser.add_argument('--midi_file', type=str, default='mary.mid', help='midi filename')
    #

    args = parser.parse_args()

    sample_rate = args.sample_rate
    frame_size = args.frame_size
    midi_path = args.midi_file
    wav_path = midi_path[0:len(midi_path) - 4] + ".wav"


    print("sys.argv : ", sys.argv, "len : ",len(sys.argv))
    print("SR : ",sample_rate)
    print("FS : ",frame_size)
    print("midi filename : ",midi_path)
    print("wav filename : ", wav_path)

    compute_mel_spec(midi_path , wav_path, sample_rate, frame_size)



    #----------------------------------------------
    #obsolete ?

    #fft_amp = np.abs(librosa.core.stft(signal, frame_size))

    #TOREMOVE: debug display
    #print fft_amp.shape
    #plt.figure(figsize=(12, 8))
    #librosa.display.specshow(fft_amp, y_axis='linear')
    #plt.show()
    #print sample_rate
