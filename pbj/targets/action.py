
from .target import Target
from .reg import register

import os, glob

@register('action')
class ActionTarget(Target):
    '''A build target that always runs.'''
    
    def __init__(self, name=None, depends=[], completion=[], help=''):
        Target.__init__(self, name=name,
                depends=depends, completion=completion, help=help,
                always=True)


# vim: et sw=4 sts=4
