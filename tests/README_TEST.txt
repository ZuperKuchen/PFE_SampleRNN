ENTETE :

import unittest
import [le script à tester]

STRUCTURE DE LA CLASSE : 

créer la classe : NomdeclasseTest(unittest.TestCase)

	def [test_nom_méthode

	...

ASSERTION : 

assertEqual(a, b) -> a == b

assertNotEqual(a, b) -> a != b

assertTrue(x) -> x is True

assertFalse(x) -> x is False

assertIs(a, b) -> a is b

assertIsNot(a, b) -> a is not b

assertIsNone(x) -> x is None

assertIsNotNone(x) -> x is not None

assertIn(a, b) -> a in b

assertNotIn(a, b) -> a not in b

assertIsInstance(a, b)
	
isinstance(a, b)

assertNotIsInstance(a, b)
	
not isinstance(a, b)

assertRaises(exception, fonction, *args, **kwargs) -> Vérifie que la fonction lève l'exception attendue.

EXECUTION : 

pyton -m unittest [nom du script de test]

