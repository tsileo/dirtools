# -*- coding: utf-8 -*-

""" test_dirtools.py - Test the dirtools module with pyfakefs. """

import unittest

try:
    import fake_filesystem
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

    def testSubdirs(self):
        """ Check that Dir.subdirs return all subdirs, except those excluded. """
        self.assertEqual(sorted(self.dir.subdirs()),
                         sorted(["dir1",
                                 "dir1/subdir1",
                                 "dir2"]))

    def testHashdir(self):
        """ Check that the hashdir changes when a file change in the tree. """
        hashdir = self.dir.hash()
        with self.open('/test_dirtools/file2', 'w') as f:
            f.write("new content")
        new_hashdir = self.dir.hash()

        self.assertNotEqual(hashdir, new_hashdir)

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

if __name__ == '__main__':
    unittest.main()
