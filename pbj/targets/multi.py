#!/usr/bin/env python

from reg import register
from target import Target

## TODO: make specialized multi targets that all point to permutations of the same build fucntion, just with different arguments. Then the unspecified default arguments could be passed into argparse and would work for all the build targets

@register('multi')
class Multi(Target):
    def __init__(self, name, depends, help=''):
        Target.__init__(self, name, depends=depends, help=help)

    def __call__(self, fn):
        raise Exception('MultiTarget is not a function wrapper')

    def run(self):
        pass

# vim: et sw=4 sts=4
