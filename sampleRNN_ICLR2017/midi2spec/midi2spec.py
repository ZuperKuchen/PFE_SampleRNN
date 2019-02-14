import midi
import numpy as np
import numpy.fft as fft
import wave

#Fixed the DEFAULT_SAMPLE_RATE at twice the frequency of the max MIDI pitch
DEFAULT_SAMPLE_RATE = 8372
#DEFAULT_FRAME_SIZE has to be the same as DEFAULT_SAMPLE_RATE to accurately transcribe the frequencies
DEFAULT_FRAME_SIZE = 8372

#Tempo = microseconds per quarter note
DEFAULT_TEMPO = 6000000.0/120.0
#Resolution = ticks per quarter note
DEFAULT_RESOLUTION = 480.0

MIDI_MIN_PITCH = 21
MIDI_MAX_PITCH = 108

#returns the fundamental frequency linked to the given MIDI pitch
def pitch_to_funda (pitch):
    return 27.5 * np.power(2.0,((pitch - 21.0)/12.0))

#returns the index of the given frequency in a spectral frame
#fs = frame size
#sr = sample rate
def freq_to_index (freq, fs, sr):
    return int(np.round(float(fs) * freq / float(sr)))

#opens a midi file and returns an array of its note on/offsets
#also returns the duration of a tick in seconds
def open_midi (file_name):
    notes_pattern = []

    tempo = DEFAULT_TEMPO
    resolution = DEFAULT_RESOLUTION

    #open the MIDI file
    pattern = midi.read_midifile(file_name)
    #it is easier to compute a piano roll if the ticks are already in absolute form
    pattern.make_ticks_abs()

    resolution = pattern.resolution

    #browse the tracks, in case there is several
    for track in pattern:
        #browse the events of each track and keep the on/offsets
        for event in track:
            if type(event) == midi.events.NoteOnEvent or type(event) == midi.events.NoteOffEvent:
                notes_pattern.append(event)
            if type(event) == midi.events.SetTempoEvent:
                tempo = event.get_mpqn()

    microseconds_per_tick = tempo/resolution

    return notes_pattern, microseconds_per_tick

#returns the number of the last tick in the track (in absolute)
def get_max_tick(pattern):
    return pattern[len(pattern)-1].tick

#Builds the "piano roll" of the track : a matrix that contains the activation (velocity)
#of each pitch for each tick
def get_piano_roll (pattern):
    #get the last tick of the track, to know how long the piano roll should be
    end_tick = get_max_tick(pattern)
    piano_roll = np.zeros((128,end_tick+1))

    #read each event and place its velocity in the matrix at the corresponding
    #pitch and tick
    for event in pattern:
        if event.pitch >= MIDI_MIN_PITCH and event.pitch <= MIDI_MAX_PITCH :
            #to take into account the end of a note event, either use the velocity 0
            #of an onset event
            if(type(event) == midi.events.NoteOnEvent):
                for i in range(event.tick, end_tick):
                    piano_roll[event.pitch][i] = event.velocity
            #or the nature of an offset event
            if(type(event) == midi.events.NoteOffEvent):
                for i in range(event.tick, end_tick):
                    piano_roll[event.pitch][i] = 0
    return piano_roll

#TODO : returns the number of frames per tick, according to the tempo
#and resolution of the track
#NOTE : might also be useful to know how long a tick is in seconds,
#in order to know how many seconds a frame should represent
def get_frames_per_tick():
    return 1

#turns the piano roll into an amplitude spectrum of the corresponding fundamental
#frequencies
#fs = frame size
#sr = sample rate
def midi_to_spec (piano_roll, fs, sr):
    nb_ticks = (piano_roll.shape)[1]
    frames_per_tick = get_frames_per_tick()
    spectrum = np.zeros((frames_per_tick * nb_ticks, fs), dtype=np.float)

    #transform each tick of the track into a spectral slice (frame)
    #that represents the fundamental frequencies of the pitches
    for tick in range(0, nb_ticks):
        for pitch in range(MIDI_MIN_PITCH, MIDI_MAX_PITCH):
            if piano_roll[pitch][tick] > 0 :
                freq_index = freq_to_index(pitch_to_funda(pitch), fs, sr)
                for i in range (0, frames_per_tick):
                    #amplitude computed from the velocity of the note
                    amp = float(piano_roll[pitch][tick])/128.0
                    #keep the symmetry of the spectrum
                    spectrum[tick * frames_per_tick + i][freq_index] = amp
                    spectrum[tick * frames_per_tick + i][fs - freq_index] = amp
    return spectrum

#For testing purposes : turns the spectrum into a listenable wav file
#NOTE : the wav file will be very long, as each frame is one second in length
#sr = sample rate
def spec_to_wav (spectrum, sr):
    #open a new wav file and set its parameter
    wav_file = wave.open("out.wav", 'wb')
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sr)
    wav_file.setnframes(spectrum.shape[0])

    for frame in spectrum:
        #reverse fourier transform of the frame
        data_frame = fft.ifft(frame, norm='ortho')
        #write the data as short integers
        wav_file.writeframes(np.int16(np.real(data_frame)*32767))
    wav_file.close()

#main
if __name__ == '__main__':
    import sys
    path = sys.argv[1]

    #open the MIDI file in the given path
    pattern, mus_per_tick = open_midi(path)

    print 'Microseconds per tick = ', mus_per_tick

    fs = (mus_per_tick / 6000000.0) * DEFAULT_SAMPLE_RATE
    print 'Frame size for one tick = ', fs

    #create the piano roll of the track
    piano_roll = get_piano_roll(pattern)
    #create the amplitude spectrum for that piano roll
    spectrum = midi_to_spec(piano_roll, DEFAULT_FRAME_SIZE, DEFAULT_SAMPLE_RATE)

    #create the listenable wav file, to check that the melody can be recognized
    #from the spectrum
    spec_to_wav(spectrum, DEFAULT_SAMPLE_RATE)

    #plot stuff
    import matplotlib.pyplot as plt

    #plot the piano roll and save it as a png
    plt.matshow(piano_roll, aspect='auto')
    plt.savefig('piano_roll.png')
    plt.show()

    #plot the spectrum and save it as a png
    plt.close()
    plt.matshow(spectrum, aspect='auto')
    plt.savefig('spectrum.png')
    plt.show()

    plt.close()
