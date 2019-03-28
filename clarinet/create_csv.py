import argparse
import numpy as np
import os
import pandas as pd

#This script creates a csv file corresponding to the data linked in.
#The format is one column for midi, one column for wav.

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Preprocessing',\
     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--in_dir', '-i', type=str, default='./maestro/',\
     help='Directory where dataset stored')

    args = parser.parse_args()

    midi = []
    wav = []

    midi_dir = args.in_dir + 'midi/'
    wav_dir = args.in_dir + 'wav/'

    #midi
    for midi_file in os.listdir(midi_dir):
        if midi_file.endswith(".mid") or midi_file.endswith(".midi"):
            (raw_name, ext) = os.path.splitext(midi_file)

            midi.append(midi_file)

            wav_file = raw_name + '.wav'

            wav.append(wav_file)


    results = pd.DataFrame(data = {'midi': midi, 'wav': wav})

    results.to_csv(args.in_dir + 'metadata.csv', index=False, header=False)
