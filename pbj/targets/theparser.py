#!/usr/bin/env python

from argparse import ArgumentParser
import inspect
import pydoc
import sys

def default_parser(name, args):
    parser = argparse.ArgumentParser(sys.argv[0] + ' ' + name)
    return parser.parse_args(args)

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
    lines = text.splitlines()
    while lines:
        begin = lines[0].lower().strip(' \t')
        if begin in ('arguments:', 'args:'):
            break
        lines.pop(0)
    for line in lines[1:]:
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

# vim: et sw=4 sts=4
