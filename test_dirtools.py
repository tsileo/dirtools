# -*- coding: utf-8 -*-

""" test_dirtools.py - Test the dirtools module with pyfakefs. """

import unittest

try:
    import fake_filesystem
except ImportError:
    print "You must install pyfakefs in order to run the test suite."

import dirtools

fk = fake_filesystem.FakeFilesystem()
fk.CreateDirectory('/test_dirtools')
fk.CreateFile('/test_dirtools/file1', contents='contents1')
fk.CreateFile('/test_dirtools/file2', contents='contents2')

fk.CreateDirectory('/test_dirtools/excluded_dir')
fk.CreateFile('/test_dirtools/excluded_dir/excluded_file',
              contents='excluded')

fk.CreateDirectory('/test_dirtools/dir1')
fk.CreateDirectory('/test_dirtools/dir1/subdir1')
fk.CreateFile('/test_dirtools/dir1/subdir1/file_subdir1',
              contents='inside subdir1')

fk.CreateDirectory('/test_dirtools/dir2')
fk.CreateFile('/test_dirtools/dir2/file_dir2', contents='inside dir2')

dirtools.os = fake_filesystem.FakeOsModule(fk)
dirtools.open = fake_filesystem.FakeFileOpen(fk)


class TestDirtools(unittest.TestCase):
    def setUp(self):
        self.dir = dirtools.Dir('/test_dirtools')

    def testFiles(self):
        self.assertEqual(sorted(self.dir.files),
                         sorted(["file1",
                                 "file2",
                                 "excluded_dir/excluded_file",
                                 "dir1/subdir1/file_subdir1",
                                 "dir2/file_dir2"]))

    def testSubdirs(self):
        self.assertEqual(sorted(self.dir.subdirs),
                         sorted(["excluded_dir",
                                 "dir1",
                                 "dir1/subdir1",
                                 "dir2"]))

    def testHashdir(self):
        pass

    def testExclude(self):
        pass

    def testProjects(self):
        pass

if __name__ == '__main__':
    unittest.main()
