# -*- encoding: utf-8 -*-
import re
import fnmatch
import logging
import os
import hashlib
import functools

from globster import Globster
# TODO se decider entre `path' et `filename', `filepath' and `directory'
# TODO une option pour exclude ['.hg', '.svn', 'git']
# TODO gerer les ecludes dans Dir.subdirs =>  topdown=True, pareils que Dir.files
#      => http://stackoverflow.com/questions/5141437/filtering-os-walk-dirs-and-files
log = logging.getLogger("dirtools")


def load_patterns(exclude_file=".exclude"):
    """ Load patterns to exclude file from `exclude_file',
    and return a list of pattern.

    :type exclude_file: str
    :param exclude_file: File containing exclude patterns

    :rtype: list
    :return: List a patterns

    """
    return filter(None, open(exclude_file).read().split("\n"))


def is_excluded(patterns, path):
    """ Return True `filename' match a fnmatch pattern.

    :type patterns: list
    :param patterns: List of fnmatch pattern that trigger exclusion

    :type path: str
    :param path: Relative path to check

    :rtype: bool
    :return: True if path should be excluded

    """
    g = Globster(patterns)
    match = g.match(path)
    if match:
        log.debug("{0} matched {1} for exclusion".format(path, match))
        return True
    return False


def get_exclude(exclude_file):
    """ Load a .gitignore like file to exclude files/dir from backups.

    :type exclude_file: str
    :param exclude_file: Path to the exclude file

    :rtype: function
    :return: A function ready to inject in tar.add(exclude=_exclude)

    """
    return functools.partial(is_excluded, load_patterns(exclude_file))


def filehash(filepath, blocksize=4096):
    """ Return the hash for the file `filepath', processing the file
    by chunk of `blocksize'. """
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
    for dirname, dirnames, filenames in os.walk(path, topdown=True):
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
    def __init__(self, directory=".", exclude_file=".exclude", excludes=['.git/', '.hg/', '.svn/']):
        self.directory = directory
        self.path = os.path.abspath(directory)
        self.exclude_file = os.path.join(self.path, exclude_file)
        self.patterns = excludes
        if os.path.isfile(self.exclude_file):
            self.patterns.extend(load_patterns(self.exclude_file))

    def is_excluded(self, path):
        """ Return True if `path' should be excluded
        given patterns in the `exclude_file'. """
        return is_excluded(self.patterns, self.relpath(path))

    @property
    def files(self):
        """ Generator for all the files not excluded recursively. """
        for root, dirs, files in os.walk(self.path, topdown=True):
            for d in list(dirs):
                if self.is_excluded(os.path.join(root, d)):
                    dirs.remove(d)
            for fpath in [os.path.join(root, f) for f in files]:
                if not self.is_excluded(fpath):
                    yield self.relpath(fpath)

    @property
    def hash(self):
        """ Hash for the entire directory recursively. """
        shadir = hashlib.sha256()
        for f in self.files:
            try:
                shadir.update(filehash(f))
            except (IOError, OSError):
                pass
        return shadir.hexdigest()

    @property
    def subdirs(self):
        """ List of all subdirs. """
        for p in listsubdir(self.path):
            if not self.is_excluded(p):
                yield self.relpath(p)

    def find_project(self, file_identifier=".project"):
        """ Search all directory recursively for subidirs
        with `file_identifier' in it.

        :type file_identifier: str
        :param file_identifier: File identier, .project by default.

        :rtype: list
        :return: The list of subdirs with a `file_identifier' in it.

        """
        return listproject(file_identifier, path=self.path)

    def relpath(self, path):
        """ Return a relative filepath to path from Dir path. """
        return os.path.relpath(path, start=self.path)
