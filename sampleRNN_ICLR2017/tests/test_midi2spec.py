import midi2spec
import unittest

# Exemple class for testing midi2spec functions 

class Midi2specTest(unittest.TestCase):
  
  #test for a fixed value
  #test for a negative value or a null value (for a bad use of the function)
  #for a calcul function, always test positiv, negativ and null value.
  def test_pitch_to_funda(self):
    theorical_result = 440.0 #frequency for A4 note
    pitch = 69 #midi number for A4 note
    function_resultat = midi2spec.pitch_to_funda(pitch)
    self.assertEqual(theorical_result, function_resultat)
    pitch = 0
    function_resultat = midi2spec.pitch_to_funda(pitch)
    self.assertEqual(0, function_resultat)

  #search max tick on a known midi file, assertEqual between result function and theorical max tick
  #def test_get_max_tick(self):

  #turns the spectrum into a listenable wav file
  #def test_midi_to_spec(self):

  #define a known spectrum from a wav file, and use it for spec_to_wav function. Compare the two wav files. Not an unit test in this case.
  #def test_spec_to_wav(self):

if __name__ == '_main_':
  unittest.main()
