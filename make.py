#!/usr/bin/env python

from optparse import OptionParser

from pymake import Builder, cmd

build = Builder('PJs')

@build.file('build/pjslib.js', depends='jslib/*.js')
def jslib(name):
    cmd('cat', 'jslib/*.js', '>', 'build/pjslib.js')

build.cmd('jstest', ('js', 'test/runtests.js'))

build.clean('build', 'test/py/*.js')

if __name__ == '__main__':
    build.run()


# vim: et sw=4 sts=4
