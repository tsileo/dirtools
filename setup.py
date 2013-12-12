import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="dirtools",
    version="0.2.0",
    author="Thomas Sileo",
    author_email="thomas.sileo@gmail.com",
    description="Exclude/ignore files in a directory (using .gitignore like syntax), compute hash, search projects for an entire directory tree and gzip compression.",
    license="MIT",
    keywords="exclude exclusion directory hash compression gzip",
    url="https://github.com/tsileo/dirtools",
    py_modules=["dirtools"],
    long_description=read("README.rst"),
    install_requires=["globster"],
    tests_require=["pyfakefs"],
    test_suite="test_dirtools",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    scripts=["dirtools.py"],
)
