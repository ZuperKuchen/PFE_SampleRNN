import argparse
import numpy as np
import os
import os.path

#this script rename files at format "track[number].midi" and "track[number].wav" 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--midi_dir', '-m', type=str, default='./maestro/midi/', help='Directory where midi files are stored')
    parser.add_argument('--wav_dir', '-w', type=str, default='./maestro/wav/', help='Directory where wav files are stored')

    args = parser.parse_args()

    #track number
    i = 0

    for file in os.listdir(args.midi_dir):
        if file.endswith(".mid") or file.endswith(".midi"):
            (old_name, ext) = os.path.splitext(file)

            old_midi_name = args.midi_dir + file
            old_wav_name = args.wav_dir + old_name + ".wav"

            new_name = 'track_' + str(i)
            new_midi_name = args.midi_dir +  new_name + '.mid'
            new_wav_name = args.wav_dir + new_name + '.wav'

            # rename midi file
            os.rename(old_midi_name, new_midi_name)

            #rename wav file
            os.rename(old_wav_name, new_wav_name)

            i += 1



    print('number of renamed tracks : ', i)
