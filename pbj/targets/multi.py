#!/usr/bin/env python

from reg import register
from target import Target

@register('multi')
class Multi(Target):
    def __init__(self, name, depends):
        Target.__init__(self, name, depends=depends)

    def __call__(self, fn):
        raise Exception('MultiTarget is not a function wrapper')

    def run(self):
        pass

# vim: et sw=4 sts=4
