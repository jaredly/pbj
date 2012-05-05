#!/usr/bin/env python
#!/usr/bin/env python

from distutils.core import setup
import os

from disttest import test

setup(
    name='pbj',
    author='Jared Forsyth',
    author_email='jared@jaredforsyth.com',
    version='0.1',
    url='http://jaredforsyth.com/projects/pbj',
    download_url='http://github.com/jabapyth/pbj',
    packages=['pbj'],
    description='python build jelly - a simple, extensible pythonic build framework',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
    ],
    cmdclass={'test': test},
    options={
        'test': {
            'test_dir': ['tests'],
        },
    },
)

# vim: et sw=4 sts=4
