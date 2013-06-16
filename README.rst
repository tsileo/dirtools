========
Dirtools
========

Dirtools is a little Python package aimed to provide the following features:

* Exclude/ignore files in a directory, using .gitignore like syntax (unix filename pattern matching).
* Generate a hash for a directory tree in order to check if a directory has been modified.
* Search recursively for all subidirs containing a given filename (all projects directory inside a dir).


Getting Started
===============

Excluding files
---------------

Dirtools let you exlude files using .gitignore like syntax (unix filename pattern matching), by default ``dirtools`` will look for a ``.exclude`` file at root.

Here is how to check if a file should be excluded:

.. code-block:: python

    from dirtools import Dir

    d = Dir('/path/to/dir', exclude_file='.gitignore')
    d.is_excluded('/path/to/dir/script.pyc')

Or using only functions:

.. code-block:: python

    import dirtools as dt

    patterns = dt.load_patterns('.gitignore')
    is_excluded(patterns, '/path/to/dir/script.pyc')


Using dirtools to exclude files with tarfile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import tarfile
    from dirtools import Dir

    d = Dir('/path/to/mydir', exclude_file='.gitignore')

    with tarfile.open(fileobj=out, mode="w:gz")) as tar:
        tar.add(filename, arcname=arcname, exclude=d.is_excluded)


Hashdir
-------

Here is how to compute the hash of a directory:

.. code-block:: python

    from dirtools import Dir

    d = Dir('/path/to/dir')
    hashdir = d.hash

Or using the ``Dir`` class:

.. code-block:: python

    import dirtools

    hash = dirtools.hashdir('/path/to/dir')

Find directories containing a file
----------------------------------


.. code-block:: python

    from dirtools import Dir

    d = Dir('/path/to/dir')
    hashdir = d.hash

Or using the ``Dir`` class:

.. code-block:: python

    import dirtools

    hash = dirtools.hashdir('/path/to/dir')


Helpers
-------

List all subdirectories of a directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import dirtools

    dirs = dirtools.listsubdir('/path/to/dir')

Or using the ``Dir`` class:

.. code-block:: python

    from dirtools import Dir

    d = Dir('/path/to/dir')

    dirs = d.subdirs


List all files recurively
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import dirtools

    dirs = dirtools.listsubdir('/path/to/dir')

Or using the ``Dir`` class:

.. code-block:: python

    from dirtools import Dir

    d = Dir('/path/to/dir')

    dirs = d.subdirs


License (MIT)
=============

Copyright (c) 2013 Thomas Sileo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
