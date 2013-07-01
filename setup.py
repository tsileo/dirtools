import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="dirtools",
    version="0.1.0",
    author="Thomas Sileo",
    author_email="thomas.sileo@gmail.com",
    description="Description",
    license="MIT",
    keywords="some keyword",
    url="https://github.com/tsileo/dirtools",
    py_modules=["dirtools"],
    long_description=read("README.rst"),
    install_requires=["globster"],
    tests_require=["pyfakefs"],
    test_suite="test_dirtools",
#    entry_points={'console_scripts': ["mycommand = dirtools:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    scripts=["dirtools.py"],
)
