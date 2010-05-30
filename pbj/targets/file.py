from target import Target
from reg import register

import os, glob

@register('file', required=1)
class FileTarget(Target):
    def __init__(self, fname, *args, **kwargs):
        Target.__init__(self, *args, **kwargs)
        self.filename = fname

    def applies_to(self, target):
        return target in ['@' + self.name, self.filename]

    def check_depends(self, builder):
        if not os.path.exists(self.filename):
            return True
        if Target.check_depends(self, builder):
            return True
        last_mod = os.path.getctime(self.filename)
        for dep in self.depends:
            if dep.startswith('@'):continue
            files = glob.glob(dep)
            for fname in files:
                if last_mod < os.path.getctime(fname):
                    return True
        return False

    def run(self, *args):
        self.fn(self.filename, *args)

# vim: et sw=4 sts=4
