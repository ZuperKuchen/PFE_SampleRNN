import argparse
import numpy as np
import os
import pandas as pd


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--midi_dir', '-m', type=str, default='./maestro/midi', help='Directory where midi files are stored')
    parser.add_argument('--wav_dir', '-w', type=str, default='./maestro/wav', help='Directory where wav files are stored')
    parser.add_argument('--out_dir', '-o', type=str, default='./maestro', help='Directory where to create csv file')

    args = parser.parse_args()

    midi = []
    wav = []

    #midi
    for midi_file in os.listdir(args.midi_dir):
        if midi_file.endswith(".mid") or midi_file.endswith(".midi"):
            (raw_name, ext) = os.path.splitext(midi_file)

            midi.append(midi_file)

            # wav_file = args.wav_dir + raw_name + '.wav'
            wav_file = raw_name + '.wav'

            wav.append(wav_file)


    results = pd.DataFrame(data = {'midi': midi, 'wav': wav})

    results.to_csv(args.out_dir + 'metadata.csv', index=False)
