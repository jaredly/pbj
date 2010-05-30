#!/usr/bin/env python

import sys
from targets import reg
from optparse import OptionParser
from errors import PBJFailed

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
            return meta
        raise AttributeError
    
    def add(self, target):
        self.targets.append(target)
        return target
    
    def _resolve(self, dep):
        changed = False
        for target in self.targets:
            if target.applies_to(dep):
                ## TODO: kill circular deps
                if target.check_depends(self):
                    target.run()
                    changed = True
        return changed

    def run(self):
        if len(sys.argv) < 2:
            print ' '.join(target.name for target in self.targets)
            return
        name = sys.argv.pop(1)
        if name == '--list':
            print ' '.join(target.name for target in self.targets)
            return
        found = False
        for target in self.targets:
            if target.name == name:
                found = True
                if target.check_depends(self):
                    try:
                        target.run(*sys.argv[1:])
                    except PBJFailed:
                        print '[pbj] failed to build', name
                else:
                    print 'Nothing to be done for ' + name
        if not found:
            print 'Unknown target %s' % name
        '''
        parser = OptionParser('Usage [%s]' % 'ho')
        for name in args:
            less
        parser.add_option('--' + name, 
        opts, args = parse.parse_args()
        '''

# vim: et sw=4 sts=4
