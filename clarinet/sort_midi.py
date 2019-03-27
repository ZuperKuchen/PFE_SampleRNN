import os
import argparse
from mido import MidiFile
import shutil as sh

#script that sort midi depending on the length of the midi track. This allows to get dataset with tracks of a length inferior to 30 seconds for example.
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Preprocessing', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--in_dir', '-i', type=str, default='./essen/midi/', help='In Directory')
    parser.add_argument('--out_dir', '-o', type=str, default='./sort_essen/', help='Out Directory')

    args = parser.parse_args()

    # Creating the different folder
    for i in range(10,71,20):
        print(i)
        os.makedirs(args.out_dir + "%s_sec" %i, exist_ok=True)

    i = 0
    for file in os.listdir(args.in_dir):
        if file.endswith(".mid") or file.endswith(".midi"):

            file_path = args.in_dir + file
            midi = MidiFile(file_path)
            time = midi.length

            if (time <= 10) :
                sh.copy2(file_path, args.out_dir + '10_sec')
            elif (time <= 30) :
                sh.copy2(file_path, args.out_dir + '30_sec')

            elif (time <= 50) :
                sh.copy2(file_path, args.out_dir + '50_sec')

            else:
                sh.copy2(file_path, args.out_dir + '70_sec')

            # if ( i < 10):
            #     print(i)
            #     i += 1
            #     print(file)
            #     print(time)
