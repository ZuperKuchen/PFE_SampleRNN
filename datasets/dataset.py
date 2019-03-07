import midi
import numpy as np
import librosa

#Tempo = microseconds per quarter note
DEFAULT_TEMPO = 6000000.0/120.0
#Resolution = ticks per quarter note
DEFAULT_RESOLUTION = 480.0

def get_mus_per_tick (pattern):
    tempo = DEFAULT_TEMPO
    resolution = DEFAULT_RESOLUTION

    resolution = pattern.resolution

    #browse the tracks, in case there is several
    for track in pattern:
        #browse the events of each track and keep the on/offsets
        for event in track:
            if type(event) == midi.events.SetTempoEvent:
                tempo = event.get_mpqn()

    return tempo/resolution

def energy (frame):
    amp_sum = 0.0
    for i in range(0, len(frame)):
        amp_sum = amp_sum + frame[i] * frame[i]
    return float(amp_sum) / float(len(frame))

def copy_x_seconds (wav_data_src, wav_data_dst, nb_seconds, sample_rate, cur_pos):
    src_eof = False
    nb_beats = 0

    try :
        data_read = wav_data_src[cur_pos : cur_pos + nb_seconds * sample_rate]
    except IndexError:
        return True, 0, cur_pos + nb_seconds  * sample_rate

    wav_data_dst.extend(data_read)

    beats = librosa.onset.onset_detect(data_read, sample_rate)

    nb_beats = len(beats)
    
    new_cur_pos = cur_pos + nb_seconds  * sample_rate
    return src_eof, nb_beats, new_cur_pos

def usage ():
    print "dataset.py <wav path> <number of seconds> <frame size>"

#main
if __name__ == '__main__':
    import sys
    import os

    if(len(sys.argv) < 3):
        usage()

    else:
        wav_path = sys.argv[1]
        mid_path = os.path.splitext(wav_path)[0] + ".mid"

        nb_seconds = int(sys.argv[2])
        frame_size = int(sys.argv[3])

        [wav_data, sample_rate] = librosa.load(wav_path)
        
        mid_data = midi.read_midifile(mid_path)
        mid_data.make_ticks_abs()
        #print mid_data
        print get_mus_per_tick (mid_data)

        wav_eof = False

        nb_subfiles = 0
        list_nb_beats = []
        cur_pos = 0

        while (not wav_eof):
            tmp_wav_path = os.path.splitext(wav_path)[0] + "_" + str(nb_subfiles) + ".wav"

            tmp_wav = []
            
            [wav_eof, nb_beats, cur_pos] = copy_x_seconds (wav_data, tmp_wav, nb_seconds, sample_rate, cur_pos)

            list_nb_beats.append (nb_beats)
            
            keep_reading = not wav_eof
            
            prev_frame = wav_data[cur_pos - frame_size : cur_pos]
            cur_frame = wav_data[cur_pos : cur_pos + frame_size]
            next_frame = wav_data[cur_pos + frame_size : cur_pos + 2 * frame_size]
                
            while keep_reading:
                if(len(next_frame) < frame_size):
                    keep_reading = False
                    wav_eof = True
                
                if keep_reading:
                    if (energy(cur_frame) > energy(prev_frame) and energy(cur_frame) > energy(next_frame)):
                        keep_reading = False
                        print 'AAA'
                    else:
                        tmp_wav.extend(cur_frame)
                        print 'BBB'

                prev_frame = cur_frame
                cur_frame = next_frame
                next_frame = wav_data[cur_pos + frame_size : cur_pos + 2 * frame_size]
                cur_pos = cur_pos + frame_size

            librosa.output.write_wav(tmp_wav_path, np.asarray(tmp_wav), sample_rate)

            # Instantiate a MIDI Pattern (contains a list of tracks)
            tmp_mid = midi.Pattern()
            # Instantiate a MIDI Track (contains a list of MIDI events)
            track = midi.Track()
            # Append the track to the pattern
            tmp_mid.append(track)

            #print "TODO : copy as many midi onsets from mid_data to tmp_mid as the nb of beats counted in the wav (don't count as a beat if the tick has already been encountered)"
            
            #print "TODO : probably going to need to keep a list of the note onsets that weren't off'ed"

            #print "TODO : finalize tmp_mid (add the missing note offsets and track end)"

            nb_subfiles = nb_subfiles + 1

        print list_nb_beats
