audiosort
=========

Sorts audio files into a folder structure according to ID3 Tags.
This might be interesting for everyone who just ripped his CD library
to disk and wants the resulting audiofiles to be sorted according to
artist and album names.

Installation
=============

Just download and execute.

Dependencies
============

python >= 2.6, mutagen >= 1.20


Usage Example
=============
```
$ audiosort.py -h
Usage: audiosort.py [options] source_directory

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d DEST, --destination=DEST
                        Destination directory
  -c, --copy            Copy files to destination (default).
  -m, --move            Move files to destination (possibly dangerous).
  -v, --verbose         Write lots of information on the console while
                        processing.
  -a, --all             Traverse hidden directories.
  
  
$ cd
$ mkdir music
$ cd music
$ audiosort.py ~/dumpdir
```
