from target import Target
from reg import register

@register('file', required=1)
class FileTarget(Target):
    def __init__(self, fname, **kwargs):
        Target.__init__(self, **kwargs)
        self.filename = fname

    def applies_to(self, target):
        return target in ['@' + self.name, self.filename]

    def check_depends(self, builder):
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

# vim: et sw=4 sts=4
