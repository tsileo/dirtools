# -*- coding: utf-8 -*-
import logging
import os
import hashlib
from contextlib import closing  # for Python2.6 compatibility
import tarfile
import tempfile

from globster import Globster

log = logging.getLogger("dirtools")

# TODO abs=True args for .files(), .subdirs() ?


def load_patterns(exclude_file=".exclude"):
    """ Load patterns to exclude file from `exclude_file',
    and return a list of pattern.

    :type exclude_file: str
    :param exclude_file: File containing exclude patterns

    :rtype: list
    :return: List a patterns

    """
    return filter(None, open(exclude_file).read().split("\n"))


def _filehash(filepath, blocksize=4096):
    """ Return the hash object for the file `filepath', processing the file
    by chunk of `blocksize'.

    :type filepath: str
    :param filepath: Path to file

    :type blocksize: int
    :param blocksize: Size of the chunk when processing the file

    """
    sha = hashlib.sha512()
    with open(filepath, 'rb') as fp:
        while 1:
            data = fp.read(blocksize)
            if data:
                sha.update(data)
            else:
                break
    return sha


def filehash(filepath, blocksize=4096):
    """ Return the hash hexdigest() for the file `filepath', processing the file
    by chunk of `blocksize'.

    :type filepath: str
    :param filepath: Path to file

    :type blocksize: int
    :param blocksize: Size of the chunk when processing the file

    """
    sha = _filehash(filepath, blocksize)
    return sha.hexdigest()


class File(object):
    def __init__(self, path):
        self.file = os.path.basename(path)
        self.path = os.path.abspath(path)

    def _hash(self):
        """ Return the hash object. """
        return _filehash(self.path)

    def hash(self):
        """ Return the hash hexdigest. """
        return filehash(self.path)

    def compress_to(self, archive_path=None):
        """ Compress the directory with gzip using tarlib.

        :type archive_path: str
        :param archive_path: Path to the archive, if None, a tempfile is created

        """
        if archive_path is None:
            archive = tempfile.NamedTemporaryFile(delete=False)
            tar_args = ()
            tar_kwargs = {'fileobj': archive}
            _return = archive.name
        else:
            tar_args = (archive_path)
            tar_kwargs = {}
            _return = archive_path
        tar_kwargs.update({'mode': 'w:gz'})
        with closing(tarfile.open(*tar_args, **tar_kwargs)) as tar:
            tar.add(self.path, arcname=self.file)

        return _return


class Dir(object):
    """ Wrapper for dirtools arround a path.

    Try to load a .exclude file, ready to compute hashdir,


    :type directory: str
    :param directory: Root directory for initialization

    :type exclude_file: str
    :param exclude_file: File containing exclusion pattern,
        .exclude by default, you can also load .gitignore files.

    :type excludes: list
    :param excludes: List of additionals patterns for exclusion,
        by default: ['.git/', '.hg/', '.svn/']

    """
    def __init__(self, directory=".", exclude_file=".exclude",
                 excludes=['.git/', '.hg/', '.svn/']):
        self.directory = os.path.basename(directory)
        self.path = os.path.abspath(directory)
        self.exclude_file = os.path.join(self.path, exclude_file)
        self.patterns = excludes
        if os.path.isfile(self.exclude_file):
            self.patterns.extend(load_patterns(self.exclude_file))
        self.globster = Globster(self.patterns)

    def hash(self):
        """ Hash for the entire directory (except excluded files) recursively. """
        shadir = hashlib.sha512()
        for f in self.files():
            try:
                shadir.update(filehash(os.path.join(self.directory, f)))
            except (IOError, OSError):
                pass
        return shadir.hexdigest()

    def files(self, pattern=None):
        """ Generator for all the files not excluded recursively.

        :type pattern: str
        :param pattern: Unix style (glob like/gitignore like) pattern

        """
        if pattern is not None:
            globster = Globster([pattern])
        for root, dirs, files in self.walk():
            for f in files:
                if pattern is None or (pattern is not None and globster.match(f)):
                    yield self.relpath(os.path.join(root, f))

    def subdirs(self, pattern=None):
        """ List of all subdirs (except excluded).

        :type pattern: str
        :param pattern: Unix style (glob like/gitignore like) pattern

        """
        if pattern is not None:
            globster = Globster([pattern])
        for root, dirs, files in self.walk():
            for d in dirs:
                if pattern is None or (pattern is not None and globster.match(d)):
                    yield self.relpath(os.path.join(root, d))

    def is_excluded(self, path):
        """ Return True if `path' should be excluded
        given patterns in the `exclude_file'. """
        match = self.globster.match(self.relpath(path))
        if match:
            log.debug("{0} matched {1} for exclusion".format(path, match))
            return True
        return False

    def walk(self):
        """ Walk the directory like os.path
        (yields a 3-tuple (dirpath, dirnames, filenames)
        except it exclude all files/directories on the fly. """
        for root, dirs, files in os.walk(self.path, topdown=True):
            ndirs = []
            # First we exclude directories
            for d in list(dirs):
                if self.is_excluded(os.path.join(root, d)):
                    dirs.remove(d)
                else:
                    ndirs.append(d)

            nfiles = []
            for fpath in (os.path.join(root, f) for f in files):
                if not self.is_excluded(fpath):
                    nfiles.append(os.path.relpath(fpath, root))

            yield root, ndirs, nfiles

    def find_projects(self, file_identifier=".project"):
        """ Search all directory recursively for subdirs
        with `file_identifier' in it.

        :type file_identifier: str
        :param file_identifier: File identier, .project by default.

        :rtype: list
        :return: The list of subdirs with a `file_identifier' in it.

        """
        projects = []
        for d in self.subdirs():
            project_file = os.path.join(self.directory, d, file_identifier)
            if os.path.isfile(project_file):
                projects.append(d)
        return projects

    def relpath(self, path):
        """ Return a relative filepath to path from Dir path. """
        return os.path.relpath(path, start=self.path)

    def compress_to(self, archive_path=None):
        """ Compress the directory with gzip using tarlib.

        :type archive_path: str
        :param archive_path: Path to the archive, if None, a tempfile is created

        """
        if archive_path is None:
            archive = tempfile.NamedTemporaryFile(delete=False)
            tar_args = ()
            tar_kwargs = {'fileobj': archive}
            _return = archive.name
        else:
            tar_args = (archive_path)
            tar_kwargs = {}
            _return = archive_path
        tar_kwargs.update({'mode': 'w:gz'})
        with closing(tarfile.open(*tar_args, **tar_kwargs)) as tar:
            tar.add(self.path, arcname=self.directory, exclude=self.is_excluded)

        return _return
