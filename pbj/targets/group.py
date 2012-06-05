from .reg import register
from .target import Target

import pydoc

## not registering, because it's handled specially by the builder
class GroupTarget(Target):
    '''A Target Group'''

    def __init__(self, name=None, depends=[], children=[], default=None, help=''):
        Target.__init__(self, name=name, depends=depends,
                always=True, help=help)
        self.children = children

        self.targets = {}

        for target in self.children:
            self.targets[target.name] = target

        self.completion = self.targets.keys()

    def __call__(self, cls):
        raise TypeError('GroupTarget not callable')

    def run(self, *pargs, **dargs):
        if not pargs:
            if self.default:
                self.default.run(**dargs)
            else:
                self._argparser.print_help()
                return
        elif pargs[0] in self.targets:
            return self.targets[pargs[0]]



# vim: et sw=4 sts=4
