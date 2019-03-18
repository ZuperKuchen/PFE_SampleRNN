import midi
import numpy as np
import librosa

#Tempo = microseconds per quarter note
DEFAULT_TEMPO = 500000.0
#Resolution = ticks per quarter note
DEFAULT_RESOLUTION = 480.0

def get_mus_per_tick (pattern):
    tempo = DEFAULT_TEMPO
    resolution = DEFAULT_RESOLUTION

    resolution = pattern.resolution

    for track in pattern:
        for event in track:
            if type(event) == midi.events.SetTempoEvent:
                tempo = event.get_mpqn()

    print tempo
    return tempo/resolution

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

def wav_separation (wav_path, nb_seconds, frame_size):
    #open src wav file
    [wav_data, sample_rate] = librosa.load(wav_path)

    #info on wav separation :
    #wav_eof = end of source file,
    #nb_subfiles = number of smaller wav files that were created
    #cur_pos = position pointer in the data of wav data
    wav_eof = False
    nb_subfiles = 0
    cur_pos = 0

    #wav separation
    while (not wav_eof):
        tmp_wav_path = os.path.splitext(wav_path)[0] + "_" + str(nb_subfiles) + ".wav"
        tmp_wav = []
            
        [wav_eof, nb_beats, cur_pos] = copy_x_seconds (wav_data, tmp_wav, nb_seconds, sample_rate, cur_pos)
            
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

def is_noteon (event):
    if (type(event) == midi.events.NoteOnEvent and event.velocity != 0):
        return True
    else:
        return False

def is_noteoff (event):
    if(type(event) == midi.events.NoteOffEvent):
        return True
    if(type(event) == midi.events.NoteOnEvent and event.velocity == 0):
        return True
    else:
        return False

def midi_separation (mid_path, nb_seconds):
    #open src MIDI file
    mid_data = midi.read_midifile(mid_path)
    
    mid_data.make_ticks_abs()

    metadata_track, src_notes_track = copy_metadata (mid_data)

    nb_note_events = len(src_notes_track)

    nb_ticks_total = src_notes_track[nb_note_events - 1].tick

    mus_per_tick = get_mus_per_tick (mid_data)
    
    print mus_per_tick
    print nb_ticks_total
    print mus_per_tick * nb_ticks_total

    nb_subfiles = 0

    midi_eot = False

    last_tick = 0
    id_cur_event = 0
    next_timestep = 0
    
    while not midi_eot:
        cur_event = src_notes_track [id_cur_event]
        tmp_pattern = midi.Pattern()
        tmp_pattern.resolution = mid_data.resolution
        tmp_mid_path = os.path.splitext(mid_path)[0] + "_" + str(nb_subfiles) + ".mid"

        notes_track = midi.Track()

        tmp_pattern.append(metadata_track)

        next_timestep = next_timestep + nb_seconds
        
        while (not is_noteon(cur_event)) or cur_event.tick * mus_per_tick / 1000000 <= next_timestep:
            if cur_event.tick * mus_per_tick / 1000000 > next_timestep and not is_noteon(cur_event):
                next_timestep = cur_event.tick * mus_per_tick / 1000000
            print nb_subfiles, ' : ', cur_event.tick * mus_per_tick / 1000000, '/', next_timestep

            id_cur_event = id_cur_event + 1
            cur_tick = cur_event.tick

            cur_event.tick = cur_tick - last_tick
            
            last_tick = cur_tick

            notes_track.append(cur_event)
            
            if id_cur_event >= nb_note_events:
                midi_eot = True
                break
            else:
                cur_event = src_notes_track [id_cur_event]

        notes_track.append(midi.EndOfTrackEvent(tick=1))
        tmp_pattern.append(notes_track)

        midi.write_midifile (tmp_mid_path, tmp_pattern)
        nb_subfiles = nb_subfiles + 1

                
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

        #separate the sub-wavs
        wav_separation (wav_path, nb_seconds, frame_size)

        #separate the MIDI
        midi_separation (mid_path, nb_seconds)
