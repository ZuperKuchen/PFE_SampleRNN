import os
import argparse

#This script transforms a MIDI file to a wav file using the timidity library.
#To use if only dataset is only MIDI.
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Preprocessing', \
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--in_dir', '-i', type=str, default='./essen30/',\
            help='In Directory')

    args = parser.parse_args()

    midi_path = args.in_dir + 'midi/'
    wav_path = args.in_dir + 'wav/'
    os.makedirs(wav_path, exist_ok=True)

    start = time.time()


    i = 0
    for midi in os.listdir(midi_path):

        #Remove the .mid or .midi extension
        (filename, ext) = os.path.splitext(midi)

        wav_name = filename + '.wav'

        #Use timidity to convert the MIDI to a wav equivalent
        command = "timidity " + midi_path + midi + " -Ow -o" + wav_path + wav_name
        os.system(command)
        i +=1

    print('%d wav files created' % i)


    end = time.time()
    print("--- %s seconds ---" % (end - start))
