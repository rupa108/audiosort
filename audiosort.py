#!/usr/bin/env python
'''
The purpose of this program is to sort audio files according to the meta
information found in the file and put them in a directory structure. If no meta
information is found, the processing of the file is skipped.

The structure that is created is: artist/album. If the file is flaged as part
of a compilation it will be put in Compilations/<album>
'''
from __future__ import print_function

__version__ = "0.1 alpha"

import os
import shutil
import re

from optparse import OptionParser
from mutagen import File
import mutagen

vprint = None

re_fcnt = re.compile("\([0-9]*\)$")


class UnsupportedFileType(Exception):
    pass


class Mp4KeyMap(object):

    title = '\xa9nam'
    album = '\xa9alb'
    artist = '\xa9ART'
    description = 'desc'
    genre = '\xa9gen'
    diskcnumber = 'disk'
    tracknumber = 'trkn'
    compilation = "cpil"
    albumartist = "aART"


class Id3KeyMap(object):

    title = "TIT2"
    album = "TALB"
    artist = "TPE1"
    albumartist = "TPE2"
    discsubtitle = "TSST"
    genre = "TCON"
    disknumber = "TPOS"
    tracknumber = "TRCK"
    compilation = "TCMP"


def parse_options():

    usage = "usage: %prog [options] source_directory"

    parser = OptionParser(usage=usage, version=__version__)

    parser.add_option("-d", "--destination", dest="dest", default=".",
                      help="Destination directory")

    parser.add_option("-c", "--copy", dest="copy", default=True,
                      action="store_true",
                      help="Copy files to destination (default).")
    parser.add_option("-m", "--move", dest="copy",
                      action="store_false",
                      help="Move files to destination (possibly dangerous).")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="Write lots of information on the console while processing.")
    parser.add_option("-a", "--all",
                      action="store_true", dest="hidden", default=False,
                      help="Traverse hidden directories.")
    return parser.parse_args()


def _copy(source, target):
    new_path = get_new_path(source, target)
    vprint("copying to %s" % new_path)
    shutil.copy2(source, new_path)


def _move(source, target):
    vprint("moving %s to %s" % (source, target))
    new_path = get_new_path(source, target)
    vprint("moving to %s" % new_path)
    shutil.move(source, new_path)


def get_new_path(source, target):

    filename = os.path.basename(source).decode("utf-8")

    f = File(source)
    if f is None:
        raise UnsupportedFileType(source)

    if isinstance(f, mutagen.mp4.MP4):
        KeyMap = Mp4KeyMap
    else:
        KeyMap = Id3KeyMap

    try:
        artist = f[KeyMap.albumartist][0]
    except KeyError:
        try:
            artist = f[KeyMap.artist][0]
        except KeyError:
            artist = u"Unknown Artist"

    if f.get(KeyMap.compilation, None):
        artist = "Compilations"

    try:
        album = f[KeyMap.album][0]
    except KeyError:
        album = u"Unknown Album"

    base = os.path.join(target, artist, album)

    try:
        os.makedirs(base)
    except OSError:
        pass

    new_file_name = _get_file_name(base, filename)
    new_path = os.path.join(base, new_file_name)
    vprint("new file path: %s" % new_path)

    return os.path.normpath(new_path)


def _get_file_name(base, filename, i=0):
    filename = filename
    name, ext = filename.rsplit(os.extsep, 1)
    if i == 0:
        pass
    else:
        name = re_fcnt.sub("", name)
        filename = u''.join([name, "(", str(i), ")", os.extsep, ext])

    path = os.path.join(base, filename)

    try:
        os.stat(path)
        vprint("path %s allready exists" % path)
        i += 1
        return _get_file_name(base, filename, i)
    except OSError:
        return filename


def main():

    (options, args) = parse_options()

    global vprint
    vprint = print if options.verbose else lambda *a, **k: None
    process = _copy if options.copy else _move

    path = " ".join(args)
    vprint("Source path:", path)
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if not options.hidden and str(d).startswith("."):
                vprint("skipping directory %s" % d)
                dirs.remove(d)
        for f in files:
            path = "%s/%s" % (root, f)
            vprint("processing file %s" % (path))

            try:
                process(path, options.dest)
            except UnsupportedFileType, e:
                vprint("Skipping unsuported file: %s" % e)
                continue

if __name__ == '__main__':
    main()
