#!/usr/bin/env python

import sys
from StringIO import StringIO

def get_builder():
    try:
        import pbj
    except ImportError:
        import sys,os
        dn = os.path.dirname(os.path.dirname(__file__))
        sys.path.append(dn)
        import pbj

    return pbj.Builder('TestBuilder')

def pytest_funcarg__build(request):
    return get_builder()

class Capture:
    def __init__(self):
        self.out = None
        self.err = None

    def on(self):
        self.out = StringIO()
        self.err = StringIO()
        self._out = sys.stdout
        self._err = sys.stderr
        sys.stdout = self.out
        sys.stderr = self.err

    def off(self):
        sys.stdout = self._out
        sys.stderr = self._err
        self.out = self.out.getvalue()
        self.err = self.err.getvalue()

    def __del__(self):
        self.off()

def pytest_funcarg__capture(request):
    return Capture() 

# vim: et sw=4 sts=4
