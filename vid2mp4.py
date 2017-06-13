#!/usr/local/bin/python

import optparse
import os, sys
import shutil
import subprocess
import stat
import toolbox.ansi as ansi

# control globals
EXT_TO_CHECK = ["mp4", "avi", "mkv", "mpg", "mpeg"]
ALLOWED_EXT = ["mp4"]
ALLOWED_VCODECS = ["h264"]
ALLOWED_ACODECS = ["aac"]
HOPELESS_VCODECS = []
HOPELESS_ACODECS = ["adpcm_dtk"]
TARGET_EXT = "mp4"
TARGET_VCODEC = "libx264"
TARGET_ACODEC = "aac -strict -2 -ar 48000 -ac 2 -ab 400000"

CONFORM_EXT = ["mkv", "avi"] # all lower case

#internal globals
DEBUG = False
DRYRUN = False
PROCESSED_FILES = False

class ProbeException(Exception):
    pass

def codecStat(f):
    if DEBUG:
        print "codecStat", f

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

    if DEBUG:
        print "debug:", rval
    return rval

def isChromecastPlayable(file, codecs=None):
    if DEBUG:
        print "isChromecastPlayable", file, codecs

    if codecs is None:
        codecs = codecStat(file)

    try:
        if codecs["ext"] in ALLOWED_EXT and codecs["vcodec"] in ALLOWED_VCODECS and codecs["acodec"] in ALLOWED_ACODECS:
            return True
    except KeyError:
        return False
    return False

def isConformable(file, codecs=None):
    if DEBUG:
        print "isConformable", file, codecs

    if codecs is None:
        codecs = codecStat(file)

    try:
        if codecs["vcodec"] in HOPELESS_VCODECS or codecs["acodec"] in HOPELESS_ACODECS:
            return False
    except KeyError:
        return False
    return True

def conformFile(source):
    if DEBUG:
        print "conformFile", source

    c = codecStat(source)
    # print c
    if isChromecastPlayable(source, c):
        # print "file OK"
        return
    if not isConformable(source, c):
        print "Warning:"
        printFileStats(source)
        return

    dest =  os.path.splitext(source)[0] + "." + TARGET_EXT
    inline_conform = False
    if dest == source:
        dest =  os.path.splitext(source)[0] + "_tmp." + TARGET_EXT
        inline_conform = True

    # build the conform command
    cmd = "ffmpeg -loglevel error -y -i \"%s\" " % (source)

    try:
        if c["vcodec"] in ALLOWED_VCODECS:
            cmd += "-vcodec copy "
        else:
            raise KeyError
    except KeyError:
        cmd += "-vcodec %s " % (TARGET_VCODEC)

    try:
        if c["acodec"] in ALLOWED_ACODECS:
            cmd += "-acodec copy "
        else:
            raise KeyError
    except KeyError:
        cmd += "-acodec %s " % (TARGET_ACODEC)

    cmd += "\"%s\"" % (dest)
    # print cmd

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
    if DEBUG:
        print "printFileStats", source

    c = "ERROR"
    try:
        c = codecStat(source)
    except ProbeException:
        return

    codec = str(c)
    if not isChromecastPlayable(source, c):
        codec = ansi.red(str(c))
    if not isConformable(source, c):
        codec = "*!* " + codec
    print codec, source

def spiderFolders(f):
    if DEBUG:
        print "spiderFolders", f

    if os.path.isdir(f):
        for s in sorted(os.listdir(f)):
            spiderFolders(os.path.join(f, s))

    elif os.path.isfile(f):
        # short circuit if we don't care about this file
        (root, ext) = os.path.splitext(os.path.basename(f))
        ext = ext.lstrip(".").lower()
        if ext not in EXT_TO_CHECK or root.startswith(".") or root.endswith("jpg"):
            return

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
    desc = "conforms files to mp4 format to work with a chromecast or a fire tv stick"
    ver = "%prog v0.3"
    p = optparse.OptionParser(usage=usage, description=desc, version=ver)
    p.add_option("--debug", dest="debug", action="store_true", default=False, help=optparse.SUPPRESS_HELP)
    p.add_option("--dryrun", dest="dryrun", action="store_true", default=False, help="print what will be done instead of doing it")
    p.add_option("--codecs", dest="codecs", action="store_true", default=False, help="list the codec of all files")
    p.add_option("--queue", dest="queue", action="store_true", default=False, help="allow for the queueing and later processing of files")
    (opts, args) = p.parse_args()

    global DRYRUN
    DRYRUN = opts.dryrun
    global CODECS
    CODECS = opts.codecs
    global DEBUG
    DEBUG = opts.debug

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
