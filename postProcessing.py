#!/usr/local/bin/python

"""
launcher to trigger custom scripts on episode post processing
also allows for argument passing
"""

import optparse
import subprocess

p = optparse.OptionParser()
(opts, args) = p.parse_args()

(newPath, oldPath, tvdbid, season, episode, airDate) = args

print "SOURCEFILE:", newPath
subprocess.call("python /mnt/animal/extensions/maintenance/vid2mp4.py '%s'" % (newPath), shell=True)
# print "UPDATEDB"
# subprocess.call("/mnt/animal/fuppes/updatedb.sh", shell=True)
