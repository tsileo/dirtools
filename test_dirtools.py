# -*- coding: utf-8 -*-

""" test_dirtools.py - Test the dirtools module with pyfakefs. """
import shutil
import unittest
import os
import tarfile
import time

try:
    import fake_filesystem
    import fake_filesystem_shutil
except ImportError:
    print "You must install pyfakefs in order to run the test suite."

import dirtools


class TestDirtools(unittest.TestCase):
    def setUp(self):
        """ Initialize a fake filesystem and dirtools. """

        # First we create a fake filesystem in order to test dirtools
        fk = fake_filesystem.FakeFilesystem()
        fk.CreateDirectory('/test_dirtools')
        fk.CreateFile('/test_dirtools/file1', contents='contents1')
        fk.CreateFile('/test_dirtools/file2', contents='contents2')
        fk.CreateFile('/test_dirtools/file3.py', contents='print "ok"')
        fk.CreateFile('/test_dirtools/file3.pyc', contents='')
        fk.CreateFile('/test_dirtools/.exclude', contents='excluded_dir/\n*.pyc')

        fk.CreateDirectory('/test_dirtools/excluded_dir')
        fk.CreateFile('/test_dirtools/excluded_dir/excluded_file',
                      contents='excluded')

        fk.CreateDirectory('/test_dirtools/dir1')
        fk.CreateDirectory('/test_dirtools/dir1/subdir1')
        fk.CreateFile('/test_dirtools/dir1/subdir1/file_subdir1',
                      contents='inside subdir1')
        fk.CreateFile('/test_dirtools/dir1/subdir1/.project')

        fk.CreateDirectory('/test_dirtools/dir2')
        fk.CreateFile('/test_dirtools/dir2/file_dir2', contents='inside dir2')

        # Sort of "monkey patch" to make dirtools use the fake filesystem
        dirtools.os = fake_filesystem.FakeOsModule(fk)
        dirtools.open = fake_filesystem.FakeFileOpen(fk)

        # Dirtools initialization
        self.dir = dirtools.Dir('/test_dirtools')
        self.os = dirtools.os
        self.open = dirtools.open
        self.shutil = fake_filesystem_shutil.FakeShutilModule(fk)
        self.fk = fk

    def testFiles(self):
        """ Check that Dir.files return all files, except those excluded. """
        self.assertEqual(sorted(self.dir.files()),
                         sorted(["file1",
                                 "file2",
                                 "file3.py",
                                 ".exclude",
                                 "dir1/subdir1/file_subdir1",
                                 "dir1/subdir1/.project",
                                 "dir2/file_dir2"]))

    def testFilesWithPatterns(self):
        """ Check that Dir.files return all files matching the pattern, except those excluded. """
        self.assertEqual(sorted(self.dir.files("*.py")),
                         sorted(["file3.py"]))

        self.assertEqual(sorted(self.dir.files("*_dir2")),
                         sorted(["dir2/file_dir2"]))

    def testSubdirs(self):
        """ Check that Dir.subdirs return all subdirs, except those excluded. """
        self.assertEqual(sorted(self.dir.subdirs()),
                         sorted(["dir1",
                                 "dir1/subdir1",
                                 "dir2"]))

    def testSubdirsWithPatterns(self):
        """ Check that Dir.subdirs return all subdirs matching the pattern, except those excluded. """
        self.assertEqual(sorted(self.dir.subdirs("*1")),
                         sorted(["dir1",
                                 "dir1/subdir1"]))

    def testHashdir(self):
        """ Check that the hashdir changes when a file change in the tree. """
        hashdir = self.dir.hash(dirtools.filehash)
        with self.open('/test_dirtools/file2', 'w') as f:
            f.write("new content")
        new_hashdir = self.dir.hash(dirtools.filehash)

        self.assertNotEqual(hashdir, new_hashdir)

    def testDirState(self):
        dir_state = dirtools.DirState(self.dir, index_cmp=dirtools.filehash)
        self.shutil.copytree('/test_dirtools', 'test_dirtools2')
        with self.open('/test_dirtools2/dir1/subdir1/file_subdir1', 'w') as f:
            f.write("dir state")
        with self.open('/test_dirtools2/new_file', 'w') as f:
            f.write("dir state")
        self.os.remove('/test_dirtools2/file1')
        self.shutil.rmtree('/test_dirtools2/dir2')
        dir_state2 = dirtools.DirState(dirtools.Dir('/test_dirtools2'), index_cmp=dirtools.filehash)
        diff = dir_state2 - dir_state
        self.assertEqual(diff, {'deleted': ['file1', 'dir2/file_dir2'], 'updated': ['dir1/subdir1/file_subdir1'], 'deleted_dirs': ['dir2'], 'created': ['new_file']})
        self.assertEqual(diff, dirtools.compute_diff(dir_state2.state, dir_state.state))

    def testExclude(self):
        """ Check that Dir.is_excluded actually exclude files. """
        self.assertTrue(self.dir.is_excluded("excluded_dir"))
        # Only the dir is excluded, the exclude line is excluded_dir/ not excluded_dir/*
        self.assertFalse(self.dir.is_excluded("excluded_dir/excluded_file"))
        self.assertTrue(self.dir.is_excluded("file3.pyc"))
        self.assertFalse(self.dir.is_excluded("file3.py"))

    def testProjects(self):
        """ Check if Dir.find_projects find all projects in the directory tree. """
        self.assertEqual(self.dir.find_projects(".project"), ['dir1/subdir1'])

    def testCompression(self):
        """ Check the compression, withouth pyfakefs because it doesn't support tarfile. """
        dirtools.os = os
        dirtools.open = open

        test_dir = '/tmp/test_dirtools'

        if os.path.isdir(test_dir):
            shutil.rmtree(test_dir)
        os.mkdir(test_dir)

        with open(os.path.join(test_dir, 'file1'), 'w') as f:
            f.write(os.urandom(2 ** 10))

        with open(os.path.join(test_dir, 'file2.pyc'), 'w') as f:
            f.write('excluded')
        os.mkdir(os.path.join(test_dir, 'dir1'))
        with open(os.path.join(test_dir, 'dir1/file1'), 'w') as f:
            f.write(os.urandom(2 ** 10))

        cdir = dirtools.Dir(test_dir)

        archive_path = cdir.compress_to()

        tar = tarfile.open(archive_path)

        test_dir_extract = '/tmp/test_dirtools_extract'

        if os.path.isdir(test_dir_extract):
            shutil.rmtree(test_dir_extract)
        os.mkdir(test_dir_extract)

        tar.extractall(test_dir_extract)

        extracted_dir = dirtools.Dir(test_dir_extract)

        self.assertEqual(sorted(extracted_dir.files()),
                         sorted(cdir.files()))

        self.assertEqual(sorted(extracted_dir.subdirs()),
                         sorted(cdir.subdirs()))

        self.assertEqual(extracted_dir.hash(dirtools.filehash),
                         cdir.hash(dirtools.filehash))

        shutil.rmtree(test_dir)
        shutil.rmtree(test_dir_extract)
        os.remove(archive_path)

if __name__ == '__main__':
    unittest.main()
