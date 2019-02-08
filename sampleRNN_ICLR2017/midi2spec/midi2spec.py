import midi

def pitch_to_fonda (pitch):
    return pitch

def open_midi (file_name):
    return midi.read_midifile(file_name)

#main
print open_midi("mary.mid")
