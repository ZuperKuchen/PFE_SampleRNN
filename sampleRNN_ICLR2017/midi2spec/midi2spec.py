import midi

def pitch_to_fonda (pitch):
    return pitch

def open_midi (file_name):
    notes_pattern = []
    pattern = midi.read_midifile(file_name)
    for track in pattern:
        for event in track:
            if type(event) == midi.events.NoteOnEvent or type(event) == midi.events.NoteOffEvent:
                notes_pattern.append(event)
    return notes_pattern

#main
pattern = open_midi("mary.mid")
print pattern
