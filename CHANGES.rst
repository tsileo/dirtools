====================
 Dirtools Changelog
====================

0.2.0 (2013-12-12)
==================

- New ``compress_to`` methods for easy gzip compression with tarfile.
- Added patterns support to ``Dir.files`` and ``Dir.subdirs`` methods.
- Now ``Dir.files`` and ``Dir.subdirs`` methods return sorted list.
 allowing custom sort options and abspath args that allow to choose between relative/absolute path.
- Added Dir.size method to recursively compute directory size.
- New ``DirState`` and ``compute_diff`` method.
- Now skipping symlinks.


0.1.0 (2013-07-01)
==================

- v0.1.0 on pypi.


0.0.0 (2013-06-17)
==================

- First version.
