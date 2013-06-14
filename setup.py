import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="packagename",
    version="0.1.0",
    author="Thomas Sileo",
    author_email="thomas.sileo@gmail.com",
    description="Description",
    license="MIT",
    keywords="some keyword",
    url="https://github.com/tsileo/packagename",
    py_modules=["packagename"],
    long_description=read("README.rst"),
    install_requires=[],
#    entry_points={'console_scripts': ["mycommand = packagename:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
    scripts=["packagename.py"],
#    test_suite="test_packagename",
)
