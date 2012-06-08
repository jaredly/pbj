from .reg import register
from .target import Target

import pydoc

## not registering, because it's handled specially by the builder
class GroupTarget(Target):
    '''A Target Group'''

    def __init__(self, name=None, depends=[], children=[], default=None, help=''):
        Target.__init__(self, name=name, depends=depends,
                always=True, help=help)
        # self.children = children

        self.targets = {}
        self.default = default

        for target in children:
            self.targets[target.name] = target

        self.completion = self.targets.keys()

    def __call__(self, cls):
        raise TypeError('GroupTarget not callable')
    
    def print_help(self):
        print 'Group Target'
        for name in sorted(self.targets.keys()):
            print '   ', name

    def build(self, builder, arglist):
        target = None
        if not arglist or arglist[0] not in self.targets:
            if not self.default:
                self.print_help()
                return
            else:
                target = self.default
        else:
            target = self.targets[arglist.pop(0)]
        ## For now, we'll have no "group arguments". We might add those later.
        return target.build(builder, arglist)

    def applies_to(self, target):
        if '@' + self.name == target:
            return [self]
        prefix = '@' + self.name + '.'
        applies = []
        if target.startswith(prefix):
            rest = target[len(prefix):]
            for child in self.targets.values():
                res = child.applies_to('@' + rest)
                applies += res

        return applies

# vim: et sw=4 sts=4
