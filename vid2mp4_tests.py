import unittest
import shutil
import os
import glob
import subprocess

import vid2mp4

class vid2mp4_testSuite(unittest.TestCase):
    """
    testing routines for the vid2mp4 module
    """

    # def setUp(self):
    #     shutil.copy("vid2mp4_tests_dir/The.Soup.2015.05.29.Rich.Eisen.mp4", "vid2mp4_tests_dir/processing")

    # def tearDown(self):
    #     for e in glob.glob("vid2mp4_tests_dir/processing/*"):
    #         print "deleteing", e
    #         os.unlink(e)

    # def test_vid2mp4_codecs(self):
    #     s = subprocess.Popen("python  vid2mp4.py --codecs vid2mp4_tests_dir/processing/The.Soup.2015.05.29.Rich.Eisen.mp4", shell=True, stdout=subprocess.PIPE)
    #     s.wait()
    #     c = s.communicate()
    #     rval = c[0].strip()
    #     #self.assertRaises(TypeError, didYouMean.edits, ())
    #     self.assertEqual(rval, "{'ext': 'mp4', 'vcodec': 'h264', 'acodec': 'aac'} vid2mp4_tests_dir/processing/The.Soup.2015.05.29.Rich.Eisen.mp4")

    def test_ffprobe_support(selfself):
        for (dirname, dirpaths, filepaths) in os.walk("/mnt/animal/tv/unsorted_old/Good Eats/"):
            for file in filepaths:
                if not file.endswith(".mp4"):
                    continue

                f = os.path.join(dirname, file)
                print f
                try:
                    vid2mp4.codecStat(f)
                except:
                    print "ERR"
                    continue

if __name__ == "__main__":
    unittest.main()