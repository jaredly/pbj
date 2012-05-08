#!/usr/bin/env python

import sys
from targets import reg
from optparse import OptionParser
from errors import PBJFailed

from clog import LOG

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
                if required == 0 and len(pos) == 1 and callable(pos[0]):
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
        found = False
        for target in self.targets:
            if target.applies_to(dep):
                found = True
                ## TODO: kill circular deps
                if target.check_depends(self):
                    LOG.info('building dependent target "%s" (%s)' % (target.name, dep))
                    target.run()
                    changed = True
                else:
                    LOG.info('nothing to do for "%s" (%s)' % (target.name, dep))
        if not found and dep[0] == '@':
            raise PBJFailed('dependency not found "%s"' % dep)
        return changed

    def run(self):
        if len(sys.argv) < 2:
            print '## build targets ##'
            print '\t' + ' '.join(target.name for target in self.targets)
            print
            print '## options ##'
            print '\t--list [target]\t\tlist completion options'
            print '\t--zsh\t\t\toutput zsh completion function (to get completion, try `./make.pbj --zsh >> ~/.zshrc`)'
            return
        targets = {}
        for target in self.targets:
            if targets.has_key(target.name):
                raise Exception('invalid PBJ configuration; multiple rules for %s' % target.name)
            targets[target.name] = target

        force = False
        name = sys.argv.pop(1)
        if name == '--list':
            if len(sys.argv) == 1:
                print ' '.join(targets.keys())
            else:
                parts = sys.argv[1].split()
                if len(parts)>1 and parts[1] in targets:
                    target = targets[parts[1]]
                    print ' '.join(target.get_completion())
                else:
                    print ' '.join(targets.keys())
            return
        elif name == '--zsh':
            print '''_make_pbj() {                     
    local a
    read -l a
    reply=(`./make.pbj --list "$a"`)
}
compctl -K _make_pbj ./make.pbj '''
            return 
        elif name in ('-f', '--force'):
            force = True
            name = sys.argv.pop(1)
        if name in targets:
            target = targets[name]
            if target.check_depends(self) or force:
                try:
                    LOG.info('building target "%s"' % name)
                    target.run(*sys.argv[1:])
                except PBJFailed:
                    LOG.info('failed to build %s' % name)
            else:
                LOG.info('nothing to do for %s' % name)
        else:
            LOG.error('Unknown target %s' % name)

# vim: et sw=4 sts=4
