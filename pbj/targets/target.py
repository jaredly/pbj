#!/usr/bin/env python

import sys
import pydoc
import inspect
from optparse import OptionParser
from argparse import ArgumentParser
from reg import register

from .theparser import make_argparser, default_parser

from ..clog import LOG

'''argparser example:

@build.target
def make(type, weeks=5, outfile=consts.OUTFILE, debug=False):
    ""Generate the summary file for a given number of weeks

    Arguments:
        type(str):      the type of output
        weeks(int):     the number of weeks
        outfile(str):   the output filename
        debug(flag):    enable debug output
    ""
'''


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
        if name is not None:
            self.name = unicode(name)
        else:
            self.name = None
        self.depends = depends
        self.always = always
        self.completion = completion
        self.fn = None
        self.argparser = None
        self.passes = 0
        self.has_run = False
        self.return_value = None
        self.fn_args = []
        self.fn_kwargs = {}
        self.set_help(help)

    def __call__(self, fn):
        if self.fn is not None:
            raise TypeError('Target already initialized')

        if self.name is None:
            self.name = fn.__name__
        if self.help == '' and fn.__doc__:
            self.set_help(pydoc.getdoc(fn))
        self.fn = fn
        self.argparser = make_argparser(self.name, fn, self.passes,
                self.always or not self.depends)
        return self

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
        if '@' + self.name == target:
            return [self]
        return []

    def check_depends(self, builder):
        LOG.info('checking dependencies for "%s"' % self.name)
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
        self.return_value = self.fn(*pargs, **dargs)
        self.has_run = True

    def build(self, builder, arglist):
        if not self.argparser:
            res = default_parser(self.name, arglist)
            pargs = []
            dargs = {}
        else:
            pargs, dargs, res = self.argparser(arglist)

        build_needed = self.check_depends(builder)
        if build_needed or res.force:
            try:
                LOG.info('building target "%s"' % self.name)
                self.run(*pargs, **dargs)
                LOG.info('finished building target "%s"' % self.name)
            except Exception, e:
                LOG.info('failed to build %s' % self.name)
                raise
        else:
            LOG.info('nothing to do for %s' % self.name)

# vim: et sw=4 sts=4
