#!/usr/bin/env python

import sys
from targets import reg
from optparse import OptionParser
from errors import PBJFailed

from clog import LOG

GENERAL_DOCS = '''\
## general options ##
   --list [target]   list completion options
   --zsh             output zsh completion function 
                     (to get completion, try `./make.pbj --zsh >> ~/.zshrc`)
'''

# TODO: make the completion as good as django-manage.py
ZSH_OUT = '''_make_pbj() {                     
    local a
    read -l a
    reply=(`./make.pbj --list "$a"`)
}
compctl -K _make_pbj ./make.pbj '''


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
                if required == 0 and len(pos) == 1 and not kwd and callable(pos[0]):
                    target = cls()
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
                    LOG.info('building dependent target "%s" (%s)'
                                % (target.name, dep))
                    target.run()
                    changed = True
                else:
                    LOG.info('nothing to do for "%s" (%s)' % (target.name, dep))
        if not found and dep[0] == '@':
            raise PBJFailed('dependency not found "%s"' % dep)
        return changed
    
    def help(self):
        res = '## build targets ##\n'
        targets = []
        maxname = 0
        for target in self.targets:
            if len(target.name) > maxname:
                maxname = len(target.name)
            targets.append((target.name, target.short_help))
        for name, help in targets:
            line = '   ' + name.ljust(maxname) + ' --  '
            hl = help.splitlines()
            line += hl.pop(0)
            for hline in hl:
                line += '\n'.ljust(maxname + 4 + 3) + hline
            res += line+ '\n'
        res += '\n'
        res += GENERAL_DOCS
        print res

    def run(self):
        if len(sys.argv) < 2:
            self.help()
            return
        targets = {}
        for target in self.targets:
            if targets.has_key(target.name):
                raise Exception('invalid PBJ configuration; multiple rules for %s'
                                    % target.name)
            targets[target.name] = target

        force = False
        name = sys.argv.pop(1)
        if name == '--list':
            if len(sys.argv) == 1:
                print ' '.join(targets.keys())
            else:
                ## ?? why split the first argument ??
                parts = sys.argv[1].split()
                if len(parts)>1 and parts[1] in targets:
                    target = targets[parts[1]]
                    print ' '.join(target.get_completion())
                else:
                    print ' '.join(targets.keys())
            return
        elif name == '--zsh':
            print ZSH_OUT
            return 
        '''
        elif name in ('-f', '--force'):
            force = True
            name = sys.argv.pop(1)
        '''
        if name in targets:
            target = targets[name]
            if target.optparser:
                pass#parser, 
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
