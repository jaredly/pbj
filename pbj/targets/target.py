#!/usr/bin/env python

import pydoc
from reg import register

@register('target')
class Target:
    '''Base class for build targets

    Arguments:
        name(str)     : target name, defaults to the function name
        depends(list) : list of dependancies. (in the form of @target-name)
        always(bool)  : build even if all dependancies are satisfied
        completion[]  : completion options
        help(str)     : help text -- defaults to the functions docstring

    '''
    def __init__(self, name=None, depends=[], always=False, completion=[], help=''):
        self.name = name
        self.depends = depends
        self.always = always
        self.completion = completion
        self.fn = None
        self.set_help(help)

    def __call__(self, fn):
        if self.name is None:
            self.name = fn.__name__
        if self.help == '' and fn.__doc__:
            self.set_help(pydoc.getdoc(fn))
        self.fn = fn

    def set_help(self, help):
        short = []
        for line in help.splitlines():
            if not line.strip():
                break
            short.append(line)
        short = '\n'.join(short)
        self.short_help = short
        self.help = help

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

    def get_completion(self):
        return self.completion

    def run(self, *args):
        if not self.fn:
            raise Exception('Invalid Configuration: target %s has no associated function' % self.name)
        self.fn(*args)

# vim: et sw=4 sts=4
