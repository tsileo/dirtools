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

        fk.CreateDirectory('/test_dirtools/excluded_dir')
        fk.CreateFile('/test_dirtools/excluded_dir/excluded_file',
                      contents='excluded')

        fk.CreateDirectory('/test_dirtools/dir1')
        fk.CreateDirectory('/test_dirtools/dir1/subdir1')
        fk.CreateFile('/test_dirtools/dir1/subdir1/file_subdir1',
                      contents='inside subdir1')

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
        """ Check that Dir.files return all files,
        except those excluded. """
        self.assertEqual(sorted(self.dir.files),
                         sorted(["file1",
                                 "file2",
                                 "excluded_dir/excluded_file",
                                 "dir1/subdir1/file_subdir1",
                                 "dir2/file_dir2"]))

    def testSubdirs(self):
        """ Check that Dir.subdirs return all subdirs,
        except those excluded. """
        self.assertEqual(sorted(self.dir.subdirs),
                         sorted(["excluded_dir",
                                 "dir1",
                                 "dir1/subdir1",
                                 "dir2"]))

    def testHashdir(self):
        """ Check that the hashdir changes
        when a file change in the tree. """
        hashdir = self.dir.hash
        print self.open('/test_dirtools/file2').read()
        print dirtools.filehash('/test_dirtools/file2')
        with self.open('/test_dirtools/file2', 'w') as f:
            f.write("new content")
        print self.open('/test_dirtools/file2').read()
        print dirtools.filehash('/test_dirtools/file2')
        new_hashdir = dirtools.Dir('/test_dirtools').hash

        self.assertNotEqual(hashdir, new_hashdir)

    def testExclude(self):
        """ Check that Dir.is_excluded actually exclude files. """
        pass

    def testProjects(self):
        """ Check if Dir.find_projects find all projects
        in the directory tree. """
        pass

if __name__ == '__main__':
    unittest.main()
