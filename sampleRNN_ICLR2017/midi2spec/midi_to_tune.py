import numpy as np
import numpy.fft as fft
import librosa, librosa.display
import matplotlib.pyplot as plt

#main
if __name__ == '__main__':
    import sys
    import os

    sample_rate = 44100
    frame_size = 1024
    path = "none"

    if len(sys.argv) >= 2:
        i = 1
        while i < len(sys.argv):
            if sys.argv[i] == '-fs':
                frame_size = int(sys.argv[i+1])
                i = i+1
            else:
                if sys.argv[i] == '-sr':
                    sample_rate = int(sys.argv[i+1])
                    i = i+1
                else :
                    path = sys.argv[i]
            i = i+1

    print sample_rate
    print frame_size
    print path

    #use timidity to convert the MIDI to a wav equivalent
    command = "timidity " + path + " -Ow -o tmp.wav"
    os.system(command)

    #spectral representation of the signal
    [signal, sample_rate] = librosa.load("tmp.wav")

    fft_amp = np.abs(librosa.core.stft(signal, frame_size))

    #TOREMOVE: debug display
    #print fft_amp.shape
    #plt.figure(figsize=(12, 8))
    #librosa.display.specshow(fft_amp, y_axis='linear')
    #plt.show()
    #print sample_rate
