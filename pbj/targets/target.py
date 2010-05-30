#!/usr/bin/env python

from reg import register

@register('target')
class Target:
    def __init__(self, name=None, depends=[], always=False):
        self.name = name
        self.depends = depends
        self.always = always
        self.fn = None

    def __call__(self, fn):
        if self.name is None:
            self.name = fn.__name__
        self.fn = fn

    def applies_to(self, target):
        return '@' + self.name == target

    def check_depends(self, builder):
        if type(self.depends) not in (tuple, list):
            self.depends = [self.depends]
        if not self.depends:
            return True
        changed = False
        for dep in self.depends:
            # TODO: could dependencies be something other than strings?
            if builder._resolve(dep):
                changed = True
        if self.always:
            return True
        return changed

    def get_arguments(self):
        return []

    def run(self, *args):
        self.fn(*args)

# vim: et sw=4 sts=4
