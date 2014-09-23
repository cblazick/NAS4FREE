#!/usr/local/bin/python

import optparse
import os, sys
import subprocess
import stat

# control globals
CONFORM_EXT = ["mkv", "avi"] # all lower case
CHROMECAST_ACODECS = ["aac", "mp3"]
CHROMECAST_VCODECS = ["h264"]

#internal globals
DRYRUN = False
PROCESSED_FILES = False

def codecStat(f):
    rval = {}

    cmd = "ffprobe \"%s\"" % (f)
    # print cmd
    s = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    (stdout, stderr) = s.communicate()

    for l in stderr.splitlines():
        # print "++", l, "++"
        if "Video:" in l:
            tokens = l.split()
            i = tokens.index("Video:")
            rval["vcodec"] = tokens[i+1]
        if "Audio:" in l:
            tokens = l.split()
            i = tokens.index("Audio:")
            rval["acodec"] = tokens[i+1].rstrip(",")

    return rval

def generateMp4(source):
    dest =  os.path.splitext(source)[0] + ".mp4"

    cmd = "ffmpeg -y -i \"%s\" " % (source)
    c = codecStat(source)
    # print repr(c), source

    if c["vcodec"] in CHROMECAST_VCODECS:
        cmd += "-vcodec copy "
    else:
        cmd += "-vcodec h264 "

    if c["acodec"] in CHROMECAST_ACODECS:
        cmd += "-acodec copy "
    else:
        return False

    cmd += "\"%s\"" % (dest)
    if os.path.exists(dest):
        ratio = float(os.stat(dest).st_size)/float(os.stat(source).st_size)
        if ratio > 0.95:
            return
        # print ratio, cmd
    if DRYRUN:
        print "run", repr(cmd)
        return True
    else:
        try:
            subprocess.call(cmd, shell=True)
            PROCESSED_FILES = True
            return True
        except: # catch all errors ESPECIALLY ctrl-c
            os.unlink(dest)
            raise

def conformFile(source):
    if os.path.splitext(source)[1].lower().lstrip(".") not in CONFORM_EXT:
        return
    r = generateMp4(source)
    if r is False:
        print "ERR:", source
    elif r is True:
        print "deleting", source
        if not DRYRUN:
            os.unlink(source)

def printFileStats(source):
    print source, codecStat(source)

def processFile(f):
    # print ":::", f, ":::"
    if os.path.isdir(f):
        for s in os.listdir(f):
            processFile(os.path.join(f, s))
    elif os.path.isfile(f):
        if CODECS:
            printFileStats(f)
            return

        if os.path.splitext(f)[1].lstrip(".").lower() in CONFORM_EXT:
            conformFile(f)
    elif not os.path.exists(f):
        print "ERR: file doesn't exist:", f
    else:
        raise("unhandled file type found: " + str(e))

def main():
    usage = "%prog <files or directories to operate on>"
    desc = "conforms files to mp4 format to work with a chromecast"
    ver = "%prog v0.1"
    p = optparse.OptionParser(usage=usage, description=desc, version=ver)
    p.add_option("--debug", dest="debug", action="store_true", default=False, help=optparse.SUPPRESS_HELP)
    p.add_option("--dryrun", dest="dryrun", action="store_true", default=False, help="print what will be done instead of doing it")
    p.add_option("--codecs", dest="codecs", action="store_true", default=False, help="list the codec of all files")
    (opts, args) = p.parse_args()

    global DRYRUN
    DRYRUN = opts.dryrun
    global CODECS
    CODECS = opts.codecs

    # print DRYRUN

    if args == []:
        processFile(os.absath("."))
    else:
        for e in args:
            processFile(e)

    if PROCESSED_FILES:
        cmd = "/mnt/animal/fuppes/updatedb.sh"
        print "running:", cmd
        s = subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    main()