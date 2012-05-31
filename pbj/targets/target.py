#!/usr/bin/env python

import sys
import pydoc
import inspect
from optparse import OptionParser
from argparse import ArgumentParser
from reg import register

'''argparser example:

@build.target
def make(type, weeks=5, outfile=consts.OUTFILE, debug=False):
    """Generate the summary file for a given number of weeks

    Arguments:
        type(str):      the type of output
        weeks(int):     the number of weeks
        outfile(str):   the output filename
        debug(flag):    enable debug output
    """
'''

##THINK ABOUT: conditionally disabling help parsing?

TYPS = {
    'int': int,
    'float': float,
    'str': str,
    'bool': bool,
    'fflag': 'fflag',
    'tflag': 'tflag',
}
def parsedoc(text):
    helps = {}
    typs = {}
    ln = text.splitlines()
    while ln and ln[0].strip().lower().strip(':') not in ('arguments', 'args'):
        ln.pop(0)
    for line in ln[1:]:
        if ':' in line:
            name, help = line.split(':', 1)
            # use regex
            typ = str
            if '(' in name:
                typ_ = name.split('(', 1)[-1].strip('() ')
                if typ_ in TYPS:
                    typ = TYPS[typ_]
                else:
                    raise Exception('Invalid Help definition: unknown type %s for argument %s' % (typ_, name))
            name = name.split('(')[0].strip()
            helps[name] = help.strip()
            typs[name] = typ
    return helps, typs

def parse_argspec(argspec, target_args):
    positional = []
    optional = []

    if argspec.defaults:
        dl = len(argspec.defaults)
        if dl > len(argspec.args) - target_args:
            values = argspec.defaults[dl - (len(argspec.args) - target_args):]
            dl = len(argspec.args) - target_args
        else:
            values = argspec.defaults
        positional = argspec.args[target_args:-dl]
        keys = argspec.args[-dl:]
        optional = zip(keys, values)
    else:
        positional = list(argspec.args[target_args:])
    return positional, optional

def make_argparser(name, fn, target_args, always):
    '''Generate an option parser based on the function arguments
    
    Arguments:
        name(str):        the function name (used in help output)
        fn(function):     the function
        target_args(int): how many function arguments will be provided by the
                          target class, and not from the command line
        always(bool):     if false, add the --force option
    Returns:
        a meta function which takes command line arguments.
    '''

    docs = pydoc.getdoc(fn)
    syn, rest = pydoc.splitdoc(docs)
    parser = ArgumentParser(sys.argv[0] + ' ' + name, description=syn)
    helps, typs = parsedoc(rest)
    #print helps, rest

    if not always:
        parser.add_argument('--force', '-f',
                help='run even if all dependencies are satisfied', action='store_true')

    argspec = inspect.getargspec(fn)
    pos, opt = parse_argspec(argspec, target_args)

    for arg in pos:
        t = typs.get(arg, str)
        print t
        if t=='fflag':
            parser.add_argument(arg, help=helps.get(arg, None),
                                action='store_true')
        elif t=='tflag':
            parser.add_argument(arg, help=helps.get(arg, None),
                                action='store_false')
        else:
            parser.add_argument(arg, help=helps.get(arg, None),
                                type=typs.get(arg, str))

    shorts = []
    argnames = {}
    for arg, default in opt:
        if arg[0] in shorts:
            argnames[arg] = ['--' + arg]
        else:
            shorts.append(arg[0])
            argnames[arg] = ['--' + arg, '-' + arg[0]]

    for arg, default in opt:
        t = typs.get(arg, str)
        if t=='fflag':
            parser.add_argument(*argnames[arg], dest=arg,
                                help=helps.get(arg, None), action='store_true')
        elif t=='tflag':
            parser.add_argument(*argnames[arg], dest=arg,
                                help=helps.get(arg, None), action='store_false')
        else:
            parser.add_argument(*argnames[arg], dest=arg, default=default,
                    help=helps.get(arg, None), type=typs.get(arg, str))

    if argspec.varargs:
        parser.add_argument('--' + argspec.varargs, nargs='*',
                help=helps.get(argspec.varargs, None), type=typs.get(arg, str))

    def meta(args):
        '''Convert command-line arguments into *args and **kwargs for the function

        Arguments:
            args[str]: command-line arguments
        Returns:
            pargs[args]: positional arguments
            dargs(dict): optional keyword arguments
            res:         the "Namespace" object with all the arguments together
        '''
        res = parser.parse_args(args)
        dct = vars(res)
        pargs = list(dct[i] for i in pos)
        dargs = dict((i, dct[i]) for i, j in opt)
        return pargs, dargs, res

    return meta

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
    passes = []

    def __init__(self, name=None, depends=[], always=False, completion=[], help=''):
        self.name = unicode(name)
        self.depends = depends
        self.always = always
        self.completion = completion
        self.fn = None
        self.argparser = None
        self.passes = 0
        self.set_help(help)

    def __call__(self, fn):
        if self.name is None:
            self.name = fn.__name__
        if self.help == '' and fn.__doc__:
            self.set_help(pydoc.getdoc(fn))
        self.fn = fn
        self.argparser = make_argparser(self.name, fn, self.passes,
                self.always or not self.depends)

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

    def get_completion(self, stuff=None):
        return self.completion

    def run(self, *pargs, **dargs):
        if not self.fn:
            raise Exception('Invalid Configuration: '
                    'target %s has no associated function' % self.name)
        self.fn(*pargs, **dargs)

# vim: et sw=4 sts=4
