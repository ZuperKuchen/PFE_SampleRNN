import midi
import numpy as np
import numpy.fft as fft
import sys
import wave

#Fixed the SAMPLE_RATE at twice the frequency of the max MIDI pitch
SAMPLE_RATE = 8372
#FRAME_SIZE has to be the same as SAMPLE_RATE to accurately transcribe the frequencies
FRAME_SIZE = 8372

MIDI_MIN_PITCH = 21
MIDI_MAX_PITCH = 108

#returns the fundamental frequency linked to the given MIDI pitch
def pitch_to_funda (pitch):
    return 27.5 * np.power(2.0,((pitch - 21.0)/12.0))

#returns the index of the given frequency in a spectral frame
def freq_to_index (freq):
    return int(np.round(float(FRAME_SIZE) * freq / float(SAMPLE_RATE)))

#opens a midi file and returns an array of its note on/offsets
def open_midi (file_name):
    notes_pattern = []

    #open the MIDI file
    pattern = midi.read_midifile(file_name)
    #it is easier to compute a piano roll if the ticks are already in absolute form
    pattern.make_ticks_abs()

    #browse the tracks, in case there is several
    for track in pattern:
        #browse the events of each track and keep the on/offsets
        for event in track:
            if type(event) == midi.events.NoteOnEvent or type(event) == midi.events.NoteOffEvent:
                notes_pattern.append(event)
    return notes_pattern

#returns the number of the last tick in the track (in absolute)
def get_max_tick(pattern):
    t = 0
    for event in pattern:
        if(event.tick > t):
            t = event.tick
    return t

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
            #an onset event
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
def midi_to_spec (piano_roll):
    nb_ticks = (piano_roll.shape)[1]
    frames_per_tick = get_frames_per_tick()
    spectrum = np.zeros((frames_per_tick * nb_ticks, FRAME_SIZE), dtype=np.float)

    #transform each tick of the track into a spectral slice (frame)
    #that represents the fundamental frequencies of the pitches
    for tick in range(0, nb_ticks):
        for pitch in range(MIDI_MIN_PITCH, MIDI_MAX_PITCH):
            if piano_roll[pitch][tick] > 0 :
                freq_index = freq_to_index(pitch_to_funda(pitch))
                for i in range (0, frames_per_tick):
                    #amplitude computed from the velocity of the note
                    amp = float(piano_roll[pitch][tick])/128.0
                    #keep the symmetry of the spectrum
                    spectrum[tick * frames_per_tick + i][freq_index] = amp
                    spectrum[tick * frames_per_tick + i][FRAME_SIZE-freq_index] = amp
    return spectrum

#For testing purposes : turns the spectrum into a listenable wav file
#NOTE : the wav file will be very long, as each frame is one second in length
def spec_to_wav (spectrum):
    #open a new wav file and set its parameter
    wav_file = wave.open("out.wav", 'wb')
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.setnframes(spectrum.shape[0])

    for frame in spectrum:
        #reverse fourier transform of the frame
        data_frame = fft.ifft(frame, norm='ortho')
        #write the data as short integers
        wav_file.writeframes(np.int16(data_frame*32767))
    wav_file.close()

#main
if __name__ == '__main__':
    path = sys.argv[1]

    #open the MIDI file in the given path
    pattern = open_midi(path)

    #create the piano roll of the track
    piano_roll = get_piano_roll(pattern)
    #create the amplitude spectrum for that piano roll
    spectrum = midi_to_spec(piano_roll)

    #create the listenable wav file, to check that the melody can be recognized
    #from the spectrum
    spec_to_wav(spectrum)

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
