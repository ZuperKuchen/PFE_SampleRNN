import midi
import numpy as np
import librosa

#Tempo = microseconds per quarter note
DEFAULT_TEMPO = 6000000.0/120.0
#Resolution = ticks per quarter note
DEFAULT_RESOLUTION = 480.0

silence_threshold = 0.0001

def get_mus_per_tick (pattern):
    tempo = DEFAULT_TEMPO
    resolution = DEFAULT_RESOLUTION

    resolution = pattern.resolution

    for track in pattern:
        for event in track:
            if type(event) == midi.events.SetTempoEvent:
                tempo = event.get_mpqn()

    return tempo/resolution

def energy (frame):
    amp_sum = 0.0
    for i in range(0, len(frame)):
        amp_sum = amp_sum + np.power(frame[i], 2.0)
    return float(amp_sum) / float(len(frame))

def copy_metadata (src_mid):
    md_track = midi.Track()
    src_notes_track = -1
    
    for track in src_mid:
        for event in track:
            if type(event) == midi.events.TimeSignatureEvent \
              or type(event) == midi.events.KeySignatureEvent \
              or type(event) == midi.events.SetTempoEvent :
              md_track.append(event)
            if type(event) == midi.events.NoteOnEvent \
              or type(event) == midi.events.NoteOffEvent :
                if(src_notes_track == -1):
                    src_notes_track = track

    md_track.append(midi.EndOfTrackEvent(tick=1))
    return md_track, src_notes_track

def copy_x_seconds (wav_data_src, wav_data_dst, nb_seconds, sample_rate, cur_pos):
    src_eof = False
    nb_beats = 0

    data_read = wav_data_src[cur_pos : cur_pos + nb_seconds * sample_rate]

    if (len(data_read) < nb_seconds  * sample_rate) :
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

        #open src wav file
        [wav_data, sample_rate] = librosa.load(wav_path)

        #info on wav separation :
        #wav_eof = end of source file,
        #nb_subfiles = number of smaller wav files that were created
        #list_nb_beats = list that keeps track of the number of beats played in each subfile
        #cur_pos = position pointer in the data of wav data
        wav_eof = False
        nb_subfiles = 0
        list_nb_beats = []
        cur_pos = 0

        #wav separation
        while (not wav_eof):
            tmp_wav_path = os.path.splitext(wav_path)[0] + "_" + str(nb_subfiles) + ".wav"

            tmp_wav = []
            
            [wav_eof, nb_beats, cur_pos] = copy_x_seconds (wav_data, tmp_wav, nb_seconds, sample_rate, cur_pos)

            list_nb_beats.append (nb_beats)
            
            #keep_reading = not wav_eof
            if not wav_eof:
                next_onsets = librosa.onset.onset_detect(wav_data[cur_pos:], sr=sample_rate, hop_length=frame_size)
                if len(next_onsets) != 0 :
                    end_of_copy_pos = cur_pos + (next_onsets[0] - 3) * frame_size
                    tmp_wav.extend(wav_data[cur_pos : end_of_copy_pos])
                    cur_pos = end_of_copy_pos
                    if (cur_pos >= len(wav_data)) :
                        wav_eof = True
                else :
                    wav_eof = True
                librosa.output.write_wav(tmp_wav_path, np.asarray(tmp_wav), sample_rate)

            nb_subfiles = nb_subfiles + 1

        print list_nb_beats

        #MIDI separation, according to what was done for the wavs
        nb_subfiles = 0
        last_tick = 0
        cur_tick = 0
        id_cur_event = 0
        midi_eot = False

        #open src MIDI file
        mid_data = midi.read_midifile(mid_path)
        mid_data.make_ticks_abs()
        
        metadata_track, src_notes_track = copy_metadata (mid_data)

        nb_note_events = len(src_notes_track)
                
        for nb_beats in list_nb_beats :
            tmp_pattern = midi.Pattern()
            tmp_pattern.resolution = mid_data.resolution
            tmp_mid_path = os.path.splitext(wav_path)[0] + "_" + str(nb_subfiles) + ".mid"
            nb_subfiles = nb_subfiles + 1

            tmp_pattern.append(metadata_track)

            notes_track = midi.Track()

            nb_beats_copied = 0

            saw_first_onset = False

            print "New subMIDI : ", nb_subfiles - 1

            #main loop
            while (nb_beats_copied != nb_beats):
                appended = False
                cur_event = src_notes_track[id_cur_event]
                cur_tick = cur_event.tick

                if type(cur_event) == midi.events.NoteOnEvent\
                  or type(cur_event) == midi.events.NoteOffEvent:

                  if (not saw_first_onset)\
                    and type(cur_event) == midi.events.NoteOnEvent \
                    and cur_event.velocity != 0:
                    saw_first_onset = True

                  if saw_first_onset:
                    cur_event.tick = cur_tick - last_tick
                    notes_track.append(cur_event)
                    print "Appended event : ", cur_event
                    appended = True
                    if cur_tick != last_tick\
                      and type(cur_event) == midi.events.NoteOnEvent\
                      and cur_event.velocity != 0:
                      nb_beats_copied = nb_beats_copied + 1
                  last_tick = cur_tick

                  if not appended:
                      print "Ignored event : ", cur_event
                                      
                id_cur_event = id_cur_event + 1
                if id_cur_event >= nb_note_events:
                    print "Reached end of track"
                    midi_eot = True
                    break

            notes_track.append(midi.EndOfTrackEvent(tick=1))
            tmp_pattern.append(notes_track)

            midi.write_midifile (tmp_mid_path, tmp_pattern)

            if midi_eot :
                break
