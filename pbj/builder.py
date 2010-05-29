#!/usr/bin/env python

from targets import reg

from optparse import OptionParser

class Builder:
    def __init__(self, name):
        self.name = name
        self.targets = []

    def __getattr__(self, name):
        if name in reg.target_reg:
            cls, required = reg.target_reg[name]
            def meta(*pos, **kwd):
                if len(pos) < required:
                    raise TypeError('%s takes at least %s arguments' % (name, required))
                if required == 0 and len(pos) == 1:
                    target = cls(**kwd)
                    self.targets.append(target)
                    return target(pos[0])
                target = cls(*pos, **kwd)
                self.targets.append(target)
                return target
        raise AttributeError

    '''
    def target(self, function=None, name=None, depends=[]):
        actual = Target(name, depends)
        self.targets.append(actual)
        if function is not None:
            return actual(function)
        return actual

    def file(self, filename,
        actual = File(name, output)
        self.targets.append(actual)
        return actual
    
    def clean(self, *files):
        self.cmd('clean', ('rm', '-rf') + tuple(files))

    def cmd(self, name, command):
        actual = CmdTarget(name, command)
    '''
    
    def add(self, target):
        self.targets.append(target)
        return target
    
    def _resolve(self, dep):
        changed = False
        for target in self.targets:
            if target.appies_to(dep):
                ## TODO: kill circular deps
                if target.check_depends(self):
                    target.run()
                    changed = True
        return changed

# vim: et sw=4 sts=4
