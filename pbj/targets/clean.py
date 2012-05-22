import glob
import os
from reg import register
from target import Target

class ConfigurationError(Exception):
    pass

@register('clean', required=1)
class CleanTarget(Target):
    def __init__(self, *files, **kwargs):
        if not files:
            raise ConfigurationError('You must specify at least one file to clean')
        self.keep = kwargs.pop('keep', [])
        Target.__init__(self, 'clean', **kwargs)
        self.files = files

    def __call__(self, fn):
        raise Exception('CleanTarget is not a function wrapper')

    def run(self):
        for fname in self.files:
            for item in glob.glob(fname):
                if item in self.keep:
                    continue
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
