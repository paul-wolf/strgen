#!python
import io
import codecs
import os.path
from distutils.core import setup

current_dir = os.path.abspath(os.path.dirname(__file__))


def read(rel_path):
    with codecs.open(os.path.join(current_dir, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


DESCRIPTION = "Generate randomized strings of characters using a template"
VERSION = get_version("strgen/__init__.py")

with io.open("README.rst", encoding="utf-8") as file:
    long_description = file.read()

setup(
    name="StringGenerator",
    long_description=long_description,
    description=DESCRIPTION,
    version=VERSION + ".post1",
    url="https://github.com/paul-wolf/strgen",
    author="Paul Wolf",
    author_email="paul.wolf@yewleaf.com",
    packages=[
        "strgen",
    ],
    license="BSD",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
