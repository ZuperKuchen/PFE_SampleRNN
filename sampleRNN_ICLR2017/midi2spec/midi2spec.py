import midi
import numpy as np
import sys

sample_rate = 44100

def pitch_to_funda (pitch):
    return 27.5 * np.power(2.0,((pitch - 21.0)/12.0))

def open_midi (file_name):
    notes_pattern = []
    
    pattern = midi.read_midifile(file_name)
    pattern.make_ticks_abs()
    
    for track in pattern:
        for event in track:
            if type(event) == midi.events.NoteOnEvent or type(event) == midi.events.NoteOffEvent:
                notes_pattern.append(event)
    return notes_pattern

def get_max_tick(pattern):
    t = 0
    for event in pattern:
        if(event.tick > t):
            t = event.tick
    return t

def get_midi_matrix (pattern):
    end_tick = get_max_tick(pattern)
    midi_matrix = np.zeros((128,end_tick+1))
    for event in pattern:
        for i in range(event.tick, end_tick):
            midi_matrix[event.pitch][i] = event.velocity
    return midi_matrix

def midi_to_spec (midi_matrix):
    nb_ticks = (midi_matrix.shape)[1]
    for tick in range(0, nb_ticks):
        for pitch in range(0,127):
            if midi_matrix[pitch][tick] != 0:
                print 'TODO'
        

#main
if __name__ == '__main__':
    path = sys.argv[1]
    pattern = open_midi(path)
    for note_event in pattern:
        print (note_event.tick, note_event.pitch, note_event.velocity, pitch_to_funda(note_event.pitch))
    midi_matrix = get_midi_matrix(pattern)
    midi_to_spec(midi_matrix)


