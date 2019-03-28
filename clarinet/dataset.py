import midi
import numpy as np
import librosa

#this file permit to cut midi and wav track of a dataset to shorter tracks, the two output files are synchronized.

#Tempo = microseconds per quarter note
DEFAULT_TEMPO = 500000.0
#Resolution = ticks per quarter note
DEFAULT_RESOLUTION = 480.0

#Duration threshold for the subfiles
DURATION_THRESH = 4.0

#Get the duration of a MIDI tick, as it is defined in the object "pattern"
def get_mus_per_tick (pattern):
    tempo = DEFAULT_TEMPO
    resolution = DEFAULT_RESOLUTION

    resolution = pattern.resolution

    for track in pattern:
        for event in track:
            if type(event) == midi.events.SetTempoEvent :
                tempo = event.get_mpqn ()

    return tempo / resolution

#Return a track that contains the metadata of src_mid
#as well as the track that contains every note in the song
#We assume there is always only one notes track
def copy_metadata (src_mid):
    md_track = midi.Track ()
    src_notes_track = -1

    for track in src_mid:
        for event in track :
            if type (event) == midi.events.TimeSignatureEvent \
              or type (event) == midi.events.KeySignatureEvent \
              or type (event) == midi.events.SetTempoEvent :
              md_track.append (event)
            if type (event) == midi.events.NoteOnEvent \
              or type (event) == midi.events.NoteOffEvent :
                if src_notes_track == -1 :
                    src_notes_track = track

    md_track.append (midi.EndOfTrackEvent (tick=1))
    return md_track, src_notes_track

#Copy a given amount of data from wav_data_src into wav_data_dst
#The amount of data to copy is given in seconds (can be a float number)
#cur_pos gives the starting point of the copy
#returns : src_eof a boolean for if the end of the src file was reached
#new_cur_pos the point reached in the data array after copying
def copy_x_seconds (wav_data_src, wav_data_dst, nb_seconds, sample_rate, cur_pos):
    src_eof = False

    nb_samples_offset = int (np.round (nb_seconds * sample_rate))

    data_read = wav_data_src[cur_pos : cur_pos + nb_samples_offset]

    #if couldn't read as much as requested, return eof
    if len (data_read) < nb_samples_offset :
        return True, 0, cur_pos + nb_samples_offset

    wav_data_dst.extend (data_read)

    new_cur_pos = cur_pos + nb_samples_offset

    return src_eof, new_cur_pos

#returns true if the event is a midi note onset (and its velocity is non-null)
def is_noteon (event):
    if type(event) == midi.events.NoteOnEvent and event.velocity != 0 :
        return True
    else :
        return False

#returns true if the event is a midi note offset (includes the possibility
#of an onset with null velocity)
def is_noteoff (event):
    if(type (event) == midi.events.NoteOffEvent) :
        return True
    if(type (event) == midi.events.NoteOnEvent and event.velocity == 0):
        return True
    else:
        return False

#browse the midi data and cut it into smaller midi files each time
#a silence is reached while also cutting the corresponding wav
#at the same time mark
def cut_midi_at_silence (mid_path, wav_path):
    cumul_duration = 0.0
    ongoing_notes = 0

    #open src MIDI file
    try:
        mid_data = midi.read_midifile (mid_path)
    except:
        print(mid_path + " INVALID")
        command = "rm " + wav_path + " " + mid_path
        os.system(command)
        return

    metadata_track, src_notes_track = copy_metadata (mid_data)
    nb_note_events = len (src_notes_track)
    mus_per_tick = get_mus_per_tick (mid_data)

    nb_subfiles = 0

    #initialize the first subfile
    tmp_pattern = midi.Pattern ()
    tmp_pattern.resolution = mid_data.resolution
    tmp_mid_path = os.path.splitext (mid_path)[0] \
                    + "_" + str(nb_subfiles) + ".mid"
    notes_track = midi.Track ()
    tmp_pattern.append (metadata_track)

    mus_per_tick = get_mus_per_tick (mid_data)

    #open src wav file
    try:
        [wav_data, sample_rate] = librosa.load (wav_path)
    except:
        print(wav_path + " INVALID")

    cur_pos = 0

    #in the main loop : compute the cumulative duration of the midi
    #and keep track of the ongoing notes, in order to cut when no notes
    #are playing and a certain time threshold has been reached
    for event in src_notes_track :
        cumul_duration = cumul_duration + event.tick * mus_per_tick / 1000000.0

        notes_track.append (event)

        if is_noteon(event) :
            ongoing_notes = ongoing_notes + 1
        if is_noteoff(event) :
            ongoing_notes = ongoing_notes - 1

        if cumul_duration > DURATION_THRESH and ongoing_notes == 0 :
            #finalize latest midi file
            notes_track.append (midi.EndOfTrackEvent (tick=1))
            tmp_pattern.append (notes_track)
            midi.write_midifile (tmp_mid_path, tmp_pattern)

            #cut the same amount of time in the wav
            tmp_wav_path = os.path.splitext (wav_path)[0]\
                            + "_" + str(nb_subfiles) + ".wav"
            tmp_wav = []
            [wav_eof, cur_pos] = copy_x_seconds (wav_data, tmp_wav,\
                                    cumul_duration, sample_rate, cur_pos)
            librosa.output.write_wav (tmp_wav_path, \
                                        np.asarray (tmp_wav), sample_rate)

            #start a new midi to fill up
            nb_subfiles = nb_subfiles + 1
            tmp_pattern = midi.Pattern ()
            tmp_pattern.resolution = mid_data.resolution
            tmp_mid_path = os.path.splitext (mid_path)[0]\
                            + "_" + str(nb_subfiles) + ".mid"
            notes_track = midi.Track ()
            tmp_pattern.append (metadata_track)

            #reinitialize cumulative duration
            cumul_duration = 0.0

    #finalize latest midi file
    notes_track.append (midi.EndOfTrackEvent (tick=1))
    tmp_pattern.append (notes_track)
    midi.write_midifile (tmp_mid_path, tmp_pattern)
    #cut the same amount of time in the wav
    tmp_wav_path = os.path.splitext (wav_path)[0]\
                    + "_" + str(nb_subfiles) + ".wav"
    tmp_wav = []
    [wav_eof, cur_pos] = copy_x_seconds (wav_data, tmp_wav, \
                            cumul_duration, sample_rate, cur_pos)
    librosa.output.write_wav (tmp_wav_path, np.asarray (tmp_wav), sample_rate)

    command = "rm " + wav_path + " " + mid_path
    os.system(command)

#how to use the program
def usage ():
    print("dataset.py <wav dir> <midi dir>")

#main
if __name__ == '__main__' :
    import sys
    import os

    i = 0
    if len(sys.argv) == 3 :
        wav_dir = sys.argv[1]
        mid_dir = sys.argv[2]


        #for all midi_file
        dir = os.listdir(mid_dir)
        for mid in dir:
            (filename, ext) = os.path.splitext(mid)

            wav_path = wav_dir + filename + '.wav'
            mid_path = mid_dir + mid
            cut_midi_at_silence (mid_path, wav_path)

            i += 1
            print(i)

    else:
        usage ()

    print(i)
    print("%d cut midi & wav files" % i)
