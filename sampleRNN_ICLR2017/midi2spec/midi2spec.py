import midi
import numpy as np
import sys

SAMPLE_RATE = 44100
FRAME_SIZE = 1024

MIDI_MIN_PITCH = 21
MIDI_MAX_PITCH = 108

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
        if event.pitch >= MIDI_MIN_PITCH and event.pitch <= MIDI_MAX_PITCH :
            for i in range(event.tick, end_tick):
                midi_matrix[event.pitch][i] = event.velocity
    return midi_matrix

def get_frames_per_tick():
    return 1

def midi_to_spec (midi_matrix):
    nb_ticks = (midi_matrix.shape)[1]
    frames_per_tick = get_frames_per_tick()
    spectrum = np.zeros((frames_per_tick * nb_ticks, FRAME_SIZE), dtype=np.int8)
    for tick in range(0, nb_ticks):
        for pitch in range(MIDI_MIN_PITCH, MIDI_MAX_PITCH):
            if midi_matrix[pitch][tick] > 0 :
                freq_index = np.round(pitch_to_funda(pitch)*(FRAME_SIZE/2)/SAMPLE_RATE)
                for i in range (0, frames_per_tick-1):
                    spectrum[tick * frames_per_tick + i][freq_index] = midi_matrix[pitch][tick]
                    spectrum[tick * frames_per_tick + i][FRAME_SIZE-freq_index] = midi_matrix[pitch][tick]
    return spectrum
    

#main
if __name__ == '__main__':
    path = sys.argv[1]
    pattern = open_midi(path)
    
    midi_matrix = get_midi_matrix(pattern)
    spectrum = midi_to_spec(midi_matrix)

    import matplotlib.pyplot as plt

    plt.matshow(midi_matrix, aspect='auto')

    plt.savefig('piano_roll.png')
    plt.show()
