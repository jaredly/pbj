#!/usr/bin/env python

import sys
import inspect
from targets import reg, Target, GroupTarget
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

## TODO: show a list of the targets for help message
base_parser = argparse.ArgumentParser()
base_parser.add_argument('--list', '-l',
        help='list completion options', action='store_true')
base_parser.add_argument('--zsh', help='''output zsh completion function
(to get completion, try `./make.pbj --zsh >> ~/.zshrc`)''', action='store_true')
base_parser.add_argument('target', help='the build target',
        type=str, default=None, nargs='?')
base_parser.add_argument('rest', help='target arguments',
        nargs=argparse.REMAINDER)

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

    def group(self, name=None, depends=[], default=None, help=''):
        def meta(cls):
            if inspect.isclass(cls):
                if not help and cls.__doc__:
                    _help = pydoc.getdoc(cls)
                else:
                    _help = help

                children = []

                for i in dir(cls):
                    value = getattr(cls, i)

                    if isinstance(value, Target):
                        children.append(value)
            elif type(cls) in (list, tuple):
                _help = help
                children = cls

            for value in children:
                assert value in self.targets
                self.targets.remove(value)

            newgroup = GroupTarget(name=name, depends=depends,
                    help=_help, children=children)
            self.targets.append(newgroup)

            return newgroup

        if callable(name) and not (depends or default or help):
            return meta(name)

        return meta
    
    def add(self, target):
        self.targets.append(target)
        return target
    
    def _resolve(self, dep):
        applicable = self.get_targets_for(dep)
        if not applicable and dep.startswith('@'):
            raise PBJFailed('dependency not found "%s"' % dep)

        changed = False
        for target in applicable:
            if target.check_depends(self):
                LOG.info('building dependent target "%s" (%s)'
                            % (target.name, dep))
                target.run()
                changed = True
            else:
                LOG.info('nothing to do for "%s" (%s)' % (target.name, dep))
        return changed

    def get_targets_for(self, dep):
        if isinstance(dep, Target):
            return [dep]
        targets = []
        for target in self.targets:
            res = target.applies_to(dep)
            targets += res
        return targets
    
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
        if args.target is None:
            base_parser.print_help()
            return
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
                target = targets[args.target]
                print target.get_completion(args.rest)
            return

        elif args.zsh:
            print ZSH_OUT
            return 

        if args.target in targets:
            target = targets[args.target]
            target.build(self, args.rest)
        else:
            LOG.error('Unknown target %s' % args.target)

# vim: et sw=4 sts=4
