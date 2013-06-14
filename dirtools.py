# -*- encoding: utf-8 -*-
import re
import fnmatch
import logging
import os
import hashlib
import functools
# TODO se decider entre `path' et `filename', `filepath' and `directory'
# TODO une option pour exclude ['.hg', '.svn', 'git']
log = logging.getLogger("dirtools")


def load_patterns(exclude_file):
    return filter(None, open(exclude_file).read().split("\n"))


def is_excluded(patterns, filename):
    for pattern in patterns:
        if re.search(fnmatch.translate(pattern), filename):
            log.debug("{0} excluded".format(filename))
            return True
    return False


def get_exclude(exclude_file):
    return functools.partial(is_excluded, load_patterns(exclude_file))


def filehash(filepath, blocksize=4096):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as fp:
        while 1:
            data = fp.read(blocksize)
            if data:
                sha.update(data)
            else:
                break
    return sha.hexdigest()


def hashdir(dirname):
    shadir = hashlib.sha256()
    for root, dirs, files in os.walk(dirname):
        for fpath in [os.path.join(root, f) for f in files]:
            try:
                #size = os.path.getsize(fpath)
                sha = filehash(fpath)
                #name = os.path.relpath(fpath, dirname)
                shadir.update(sha)
            except (IOError, OSError):
                pass
        return shadir.hexdigest()


def listsubdir(path='.'):
    """ Yield all subdirectory of path. """
    for dirname, dirnames, filenames in os.walk(path):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            yield os.path.join(dirname, subdirname)


def listproject(filename, path="."):
    """ Yield all dirs that contains `filename'
    recursively from `path' """
    for d in list(listsubdir(path)):
        if os.path.isfile(os.path.join(d, filename)):
            yield d


class Dir(object):
    def __init__(self, directory=".", exclude_file=".exclude"):
        self.directory = directory
        self.path = os.path.abspath(directory)
        self.exclude_file = os.path.join(self.path, exclude_file)
        self.patterns = []
        if os.path.isfile(self.exclude_file):
            self.patterns = load_patterns(self.exclude_file)

    @property
    def files(self):
        for root, dirs, files in os.walk(self.path):
            for d in dirs:
                reldir = os.path.relpath(os.path.join(root, d), self.path)
                if is_excluded(self.patterns, reldir):
                    dirs.remove(d)
            for fpath in [os.path.join(root, f) for f in files]:
                relpath = os.path.relpath(fpath, self.path)
                if not is_excluded(self.patterns, relpath):
                    yield relpath

    @property
    def hash(self):
        shadir = hashlib.sha256()
        for f in self.files:
            try:
                shadir.update(filehash(f))
            except (IOError, OSError):
                pass
        return shadir.hexdigest()

    @property
    def subdirs(self):
        for p in listsubdir(self.path):
            yield os.path.relpath(p, self.path)

    def find_project(self, file_identifier=".project"):
        return listproject(file_identifier, path=self.path)
