import midi
import numpy as np
import numpy.fft as fft
import sys
import wave

SAMPLE_RATE = 8372
FRAME_SIZE = 8372

MIDI_MIN_PITCH = 21
MIDI_MAX_PITCH = 108

def pitch_to_funda (pitch):
    return 27.5 * np.power(2.0,((pitch - 21.0)/12.0))

def freq_to_index (freq):
    return int(np.round(float(FRAME_SIZE) * freq / float(SAMPLE_RATE)))

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

def get_piano_roll (pattern):
    end_tick = get_max_tick(pattern)
    piano_roll = np.zeros((128,end_tick+1))
    for event in pattern:
        if event.pitch >= MIDI_MIN_PITCH and event.pitch <= MIDI_MAX_PITCH :
            for i in range(event.tick, end_tick):
                piano_roll[event.pitch][i] = event.velocity
    return piano_roll

def get_frames_per_tick():
    return 1

def midi_to_spec (piano_roll):
    nb_ticks = (piano_roll.shape)[1]
    frames_per_tick = get_frames_per_tick()
    spectrum = np.zeros((frames_per_tick * nb_ticks, FRAME_SIZE), dtype=np.float)
    for tick in range(0, nb_ticks):
        for pitch in range(MIDI_MIN_PITCH, MIDI_MAX_PITCH):
            if piano_roll[pitch][tick] > 0 :
                freq_index = freq_to_index(pitch_to_funda(pitch))
                print freq_index
                for i in range (0, frames_per_tick):
                    amp = float(piano_roll[pitch][tick])/128.0
                    spectrum[tick * frames_per_tick + i][freq_index] = amp
                    print spectrum[tick * frames_per_tick + i][freq_index]
                    spectrum[tick * frames_per_tick + i][FRAME_SIZE-freq_index] = amp
                    print spectrum[tick * frames_per_tick + i][FRAME_SIZE-freq_index]
    return spectrum

def spec_to_wav (spectrum):
    wav_file = wave.open("out.wav", 'wb')
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.setnframes(spectrum.shape[0])

    for frame in spectrum:
        data_frame = fft.ifft(frame, norm='ortho')
        wav_file.writeframes(np.int16(data_frame*32767))
    wav_file.close()

#main
if __name__ == '__main__':
    path = sys.argv[1]
    pattern = open_midi(path)

    piano_roll = get_piano_roll(pattern)
    spectrum = midi_to_spec(piano_roll)

    spec_to_wav(spectrum)

    import matplotlib.pyplot as plt

    plt.matshow(piano_roll, aspect='auto')
    plt.savefig('piano_roll.png')
    plt.show()

    plt.close()
    plt.matshow(spectrum, aspect='auto')
    plt.savefig('spectrum.png')
    plt.show()
