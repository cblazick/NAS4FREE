import unittest
import shutil
import os
import glob
import subprocess

class vid2mp4_testSuite(unittest.TestCase):
    """
    testing routines for the vid2mp4 module
    """

    def setUp(self):
        shutil.copy("test_files/The.Soup.2015.05.29.Rich.Eisen.mp4", "test_files/processing")

    def tearDown(self):
        for e in glob.glob("test_files/processing/*"):
            print "deleteing", e
            os.unlink(e)

    def test_vid2mp4_codecs(self):
        s = subprocess.Popen("python  vid2mp4.py --codecs test_files/processing/The.Soup.2015.05.29.Rich.Eisen.mp4", shell=True, stdout=subprocess.PIPE)
        s.wait()
        c = s.communicate()
        rval = c[0].strip()
        #self.assertRaises(TypeError, didYouMean.edits, ())
        self.assertEqual(rval, "{'ext': 'mp4', 'vcodec': 'h264', 'acodec': 'aac'} test_files/processing/The.Soup.2015.05.29.Rich.Eisen.mp4")

if __name__ == "__main__":
    unittest.main()