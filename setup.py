#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Frank Xu",
    author_email='franky.xhl@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Port to Python 3 and released at PyPi by Frank Xu.
dbfpy is a python-only module for reading and writing DBF-files.
It was created by Jeff Kunce and then modified by Hans Fiby
and Yaroslav Samchuk.  Dbfpy was ported to Python 3.x by James
Douglass.
dbfpy can read and write simple DBF-files.  The `DBF-format
<http://www.clicketyclick.dk/databases/xbase/format/>`_
was developed about 30 years ago and was used by a number
of simple database applications (dBase, Foxpro, Clipper, ...).
The basic datatypes numbers, short text, and dates are available.
Many different extensions have been used; dbfpy can read and write
only simple DBF-files.
    ",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='dbfpy3',
    name='dbfpy3',
    packages=find_packages(include=['dbfpy3', 'dbfpy3.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/frankyxhl/dbfpy3',
    version='3.0.0',
    zip_safe=False,
)
