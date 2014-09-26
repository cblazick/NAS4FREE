#!/usr/local/bin/python

import optparse
import os, sys
import shutil
import subprocess
import stat
import toolbox.ansi as ansi

# control globals
EXT_TO_CHECK = ["mp4", "avi", "mkv"]
ALLOWED_EXT = ["avi", "mp4"]
ALLOWED_VCODECS = ["h264"]
ALLOWED_ACODECS = ["aac", "mp3"]
TARGET_EXT = "mp4"
TARGET_VCODEC = "h264"
TARGET_ACODEC = "aac -strict -2 -ar 48000 -ac 2 -b:a 400k"

CONFORM_EXT = ["mkv", "avi"] # all lower case
CHROMECAST_ACODECS = ["aac", "mp3"]
CHROMECAST_VCODECS = ["h264"]

#internal globals
DRYRUN = False
PROCESSED_FILES = False

class ProbeException(Exception):
    pass

def codecStat(f):
    rval = {}

    rval["ext"] = os.path.splitext(f)[1].lstrip(".").lower()

    cmd = "ffprobe \"%s\"" % (f)
    # print cmd
    s = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    (stdout, stderr) = s.communicate()
    if s.returncode:
        print "ERR:", repr(cmd)
        # print stderr
        raise ProbeException

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

def conformFile(source):
    # print "conformFile", source, cstat

    # short circuit if we don't need to scan the codec
    ext = os.path.splitext(source)[1].lstrip(".").lower()
    if ext not in EXT_TO_CHECK or os.path.split(source)[1].startswith(".") or os.path.split(source)[1].endswith("jpg"):
        return

    c = codecStat(source)
    # print c
    if c["ext"] in ALLOWED_EXT and c["vcodec"] in ALLOWED_VCODECS and c["acodec"] in ALLOWED_ACODECS:
        # print "file OK"
        return

    dest =  os.path.splitext(source)[0] + "." + TARGET_EXT
    inline_conform = False
    if dest == source:
        dest =  os.path.splitext(source)[0] + "_tmp." + TARGET_EXT
        inline_conform = True

    # build the conform command
    cmd = "ffmpeg -loglevel error -y -i \"%s\" " % (source)

    if c["vcodec"] in ALLOWED_VCODECS:
        cmd += "-vcodec copy "
    else:
        cmd += "-vcodec %s " % (TARGET_VCODEC)

    if c["acodec"] in CHROMECAST_ACODECS:
        cmd += "-acodec copy "
    else:
        cmd += "-acodec %s " % (TARGET_ACODEC)

    cmd += "\"%s\"" % (dest)

    # run the command as necessary
    if DRYRUN:
        print "run", repr(cmd)
    else:
        try:
            print cmd, ":"
            subprocess.call(cmd, shell=True)
            PROCESSED_FILES = True
        except: # catch all errors ESPECIALLY ctrl-c
            os.unlink(dest)
            raise

    if inline_conform:
        if DRYRUN:
            print "delete", source
            print "move", dest, "->", source
        else:
            os.unlink(source)
            shutil.move(dest, source)
    else:
        if DRYRUN:
            print "delete", source
        else:
            os.unlink(source)

def printFileStats(source):
    c = "ERROR"
    try:
        c = codecStat(source)
    except ProbeException:
        return

    if c["ext"] not in ALLOWED_EXT or c["vcodec"] not in ALLOWED_VCODECS or c["acodec"] not in ALLOWED_ACODECS:
        codec = ansi.red(str(c))
    else:
        codec = str(c)
    print codec, source

def spiderFolders(f):
    # print "spiderFolders", f

    if os.path.isdir(f):
        for s in sorted(os.listdir(f)):
            spiderFolders(os.path.join(f, s))

    elif os.path.isfile(f):
        if CODECS:
            printFileStats(f)
            return
        try:
            conformFile(f)
        except ProbeException:
            return

    elif not os.path.exists(f):
        print "ERR: file doesn't exist:", f
    else:
        raise("unhandled file type found: " + str(e))

def main():
    usage = "%prog <files or directories to operate on>"
    desc = "conforms files to mp4 format to work with a chromecast"
    ver = "%prog v0.3"
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
        for e in sorted(args):
            spiderFolders(e)

    if PROCESSED_FILES:
        cmd = "/mnt/animal/fuppes/updatedb.sh"
        print "running:", cmd
        s = subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    main()