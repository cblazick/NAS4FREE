#!/usr/local/bin/python

import optparse
import os
import subprocess
import stat

# control globals
CONFORM_EXT = ["mkv"] # all lower case

usage = "%prog <files or directories to operate on>"
desc = "conforms files to mp4 format to work with a chromecast"
ver = "%prog v0.1"
p = optparse.OptionParser(usage=usage, description=desc, version=ver)
p.add_option("--debug", dest="debug", action="store_true", default=False, help=optparse.SUPPRESS_HELP)
(opts, args) = p.parse_args()

PROCESSED_FILES = False

def generateMp4(source):
    dest = os.path.splitext(source)[0] + ".mp4"
    cmd = "ffmpeg -i '%s' -codec copy '%s'" % (source, dest)
    print repr(cmd)
    #ratio = float(os.stat(source).st_mode[stat.ST_SIZE])/float(os.stat(dest).st_mode[stat.ST_SIZE])
    print os.stat(source).st_mode
    #print ratio
    #if ratio > 0.95:
    #    return
    try:
        s = subprocess.Popen(cmd, shell=True)
        s.communicate()
    except: # catch all errors ESPECIALLY ctrl-c
        #os.unlink(dest)
        raise

    PROCESSED_FILES = True

def conformFile(source):
    generateMp4(source)
    #os.unlink(source)

def process(f):
    if os.path.isdir(f):
        for s in os.listdir(f):
            process(os.path.join(f, s))
    elif os.path.isfile(f):
        if os.path.splitext(f)[1].lstrip(".").lower() in CONFORM_EXT:
            conformFile(f)
    else:
        raise("unhandled file type found: " + str(e))

for e in args:
    process(e)

if PROCESSED_FILES:
    cmd = "/mnt/animal/fuppes/updatedb.sh"
    s = subprocess.call(cmd, shell=True)
