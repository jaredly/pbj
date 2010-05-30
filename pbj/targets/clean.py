import glob
import os
from reg import register
from target import Target

@register('clean', required=1)
class CleanTarget(Target):
    def __init__(self, *files, **kwargs):
        Target.__init__(self, 'clean', **kwargs)
        self.files = files

    def __call__(self, fn):
        raise Exception('CmdTarget is not a function wrapper')

    def run(self):
        for fname in self.files:
            for item in glob.glob(fname):
                remove(item)

def remove(item):
    if os.path.isdir(item):
        for child in os.listdir(item):
            remove(os.path.join(item, child))
    elif os.path.exists(item):
        os.remove(item)


def clean(*files, **kwargs):
    return CmdTarget('clean', ('rm', '-rf') + tuple(files), **kwargs)

# vim: et sw=4 sts=4
