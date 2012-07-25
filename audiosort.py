#!/usr/bin/env python
'''
Created on 23.07.2012

@author: roman
'''
from __future__ import print_function

__version__ = "1.0"

import os
import shutil
import re

from optparse import OptionParser
from mutagen import File

vprint = None

re_fcnt = re.compile("\([0-9]*\)$")

class UnsupportedFileType(Exception):
    pass

def parse_options():
    
    usage = "usage: %prog [options] arg1 arg2"

    parser = OptionParser(usage=usage, version=__version__)

    parser.add_option("-d", "--destination", dest="dest", default=".",
                      help="destination directory")
        
    parser.add_option("-c", "--copy", dest="copy", default=True,
                      action="store_true",
                      help="copy files to destination (default)")
    parser.add_option("-m", "--move", dest="copy",
                      action="store_false",
                      help="move files to destination")                  
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False ,
                  help="be silent while processing")
    parser.add_option("-a", "--all",
                  action="store_true", dest="hidden", default=False ,
                  help="traverse hidden directories")
    return parser.parse_args()

def _copy(source,target):
    new_path = get_new_path(source,target)
    vprint("copying to %s" % new_path)
    shutil.copy2(source, new_path)

def _move(source, target):
    vprint("moving %s to %s" % (source,target))
    new_path = get_new_path(source,target)
    vprint("moving to %s" % new_path)
    shutil.move(source, new_path)
    
def get_new_path(source,target):

    filename = os.path.basename(source).decode("utf-8")
    
    f = File(source, easy=True)
    if f is None:
        raise UnsupportedFileType(source) 
    
    try:
        artist = f["artist"][0]
    except KeyError:
        artist = u"Unknown Artist"
        
    try: 
        album = f["album"][0]
    except KeyError:
        album = u"Unknown Album"
    base = os.path.join(target, artist, album)
    
    try:
        os.makedirs(base)
    except OSError:
        pass

    
    new_file_name = _get_file_name(base,filename)
    new_path = os.path.join(base,new_file_name)
    vprint("new file path: %s" % new_path )
    
    return os.path.normpath(new_path)

def _get_file_name(base,filename,i=0):
    filename = filename
    name, ext  = filename.rsplit(os.extsep,1)
    if i == 0:
        pass
    else:
        name = re_fcnt.sub("", name)
        filename = u''.join([name, "(", str(i), ")", os.extsep, ext])

    path = os.path.join(base,filename)
    
    try:
        os.stat(path)
        vprint("path %s allready exists" % path)
        i += 1
        return _get_file_name(base, filename, i) 
    except OSError:
        return filename

        
def main():

    (options,args) = parse_options()
    
    global vprint    
    vprint = print if options.verbose else lambda *a, **k: None
    process = _copy if options.copy else _move
        
    for arg in args:
        for root, dirs, files in os.walk(arg):
            for d in dirs:
                if not options.hidden and str(d).startswith("."):
                    vprint("skipping directory %s" % d)
                    dirs.remove(d)
            for f in files:
                path = "%s/%s" % (root,f)
                vprint("processing file %s" %  (path))
                
                try:
                    process(path, options.dest)
                except UnsupportedFileType, e:
                    vprint("Skipping unsuported file: %s" % e)
                    continue
                                  
if __name__ == '__main__':
    main()
                