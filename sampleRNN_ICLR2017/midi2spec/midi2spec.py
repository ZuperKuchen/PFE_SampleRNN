import midi
import numpy as np

def pitch_to_fonda (pitch):
    return np.round(27.5 * np.power(2.0,((pitch - 21.0)/12.0)))

def open_midi (file_name):
    notes_pattern = []
    pattern = midi.read_midifile(file_name)
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

def midi_matrix (pattern):
    velocity_mat = np.zeros((128,get_max_tick(pattern)+1))
    for event in pattern:
        velocity_mat[event.pitch][event.tick] = event.velocity
    return velocity_mat

#main
pattern = open_midi("mary.mid")
for note_event in pattern:
    print (pitch_to_fonda(note_event.pitch), note_event.tick, note_event.velocity)

print midi_matrix(pattern).shape
