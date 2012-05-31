#!/usr/bin/env python

import sys
import inspect
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

import inspect

import argparse

def default_parser(name, args):
    parser = argparse.ArgumentParser(sys.argv[0] + ' ' + name)
    return parser.parse_args(args)

## TODO: show a list of the targets for help message
base_parser = argparse.ArgumentParser()
base_parser.add_argument('--list', '-l', help='list completion options', action='store_true')
base_parser.add_argument('--zsh', help='''output zsh completion function
(to get completion, try `./make.pbj --zsh >> ~/.zshrc`)''', action='store_true')
base_parser.add_argument('target', help='the build target', default=None)
base_parser.add_argument('rest', nargs=argparse.REMAINDER)

class Builder:
    def __init__(self, name):
        self.name = name
        self.targets = []

    def __getattr__(self, name):
        if name in reg.target_reg:
            cls, required = reg.target_reg[name]
            aspec = inspect.getargspec(cls.__init__)
            def meta(*pos, **kwd):
                callframe = inspect.getouterframes(inspect.currentframe())[1]
                '''
                if len(pos) < required:
                    raise TypeError('%s takes at least %s arguments' % (name, required))
                '''
                if not required and len(pos) == 1 and not kwd and callable(pos[0]):
                    target = cls()
                    self.targets.append(target)
                    return target(pos[0])
                target = cls(*pos, **kwd)
                target.init_frame = callframe
                self.targets.append(target)
                return target
            return meta
        raise AttributeError('Unknown target type: %s' % name)
    
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
            if hl:
                line += hl.pop(0)
                for hline in hl:
                    line += '\n'.ljust(maxname + 4 + 3) + hline
            res += line+ '\n'
        res += '\n'
        res += GENERAL_DOCS
        print res

    def run(self):
        args = base_parser.parse_args()
        targets = {}
        for target in self.targets:
            if targets.has_key(target.name):
                raise Exception('invalid PBJ configuration; multiple rules for %s'
                                    % target.name)
            targets[target.name] = target

        if args.list:
            if not args.target or args.target not in targets:
                print ' '.join(targets.keys())
            else:
                ## ?? why split the first argument ??
                target = targets[args.target]
                print target.get_completion(args.rest)
                '''
                parts = sys.argv[1].split()
                if len(parts)>1 and parts[1] in targets:
                    target = targets[parts[1]]
                    print ' '.join(target.get_completion())
                else:
                    print ' '.join(targets.keys())
                    '''
            return
        elif args.zsh:
            print ZSH_OUT
            return 
        if args.target in targets:
            target = targets[args.target]
            options = None
            if target.argparser:
                pargs, dargs, res = target.argparser(args.rest)
            else:
                pargs = []
                dargs = {}
                res = default_parser(args.target, args.rest)
            LOG.info('checking dependencies for "%s"' % args.target)
            if target.check_depends(self) or res.force:
                try:
                    LOG.info('building target "%s"' % args.target)
                    target.run(*pargs, **dargs)
                    LOG.info('finished building target "%s"' % args.target)
                except PBJFailed:
                    LOG.info('failed to build %s' % args.target)
            else:
                LOG.info('nothing to do for %s' % args.target)
        else:
            LOG.error('Unknown target %s' % args.target)

# vim: et sw=4 sts=4
