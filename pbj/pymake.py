#!/usr/bin/env python
from subprocess import Popen, PIPE

def cmd(command):
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    out = p.stdout.read()
    err = p.stderr.read()
    return out, err

class Builder:
    def __init__(self, name):
        self.name = name
        self.targets = []
        self.files = []

    def target(self, function=None, name=None, depends=[]):
        actual = Target(name, depends)
        self.targets.append(actual)
        if function is not None:
            return actual(function)
        return actual

    def file(self, name, output=None):
        actual = File(name, output)
        self.files.append(actual)
        return actual
    
    def clean(self, *files):
        self.cmd('clean', ('rm', '-rf') + tuple(files))

class Target:
    def __init__(self, name, depends):
        self.name = name
        self.depends = depends

    def __call__(self, fn):
        if self.name is None:
            self.name = fn.__name__

class FileTarget(Target):
    def __init__(self, name, output):
        pass

class CmdTarget(Target):
    def __init__(self, name, command):
        self.name = name

    def run(self):
        o, e = cmd(self.command)
        print o
        if e:
            raise Exception(e)
        print e

# vim: et sw=4 sts=4
