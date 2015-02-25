import random
import unittest

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        self.assertRaises(ValueError, random.sample, self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

    def test_gottamakerealtests(self):
        self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()

"""
Still to test:
def loadData(resultsfile):
def blend(imagestouse, ad_keywords):
def addImageToLibrary(keyword, startIndex):
class NewCreation:
"""
