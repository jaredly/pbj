from target import Target
from reg import register

from subprocess import Popen, PIPE

def cmd(command):
    p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    out = p.stdout.read()
    err = p.stderr.read()
    return out, err

@register('cmd', required=2)
class CmdTarget(Target):
    def __init__(self, name, command, depends=[]):
        Target.__init__(self, name, depends)

    def __call__(self, function):
        raise Exception('CmdTarget is not a function wrapper')

    def run(self):
        o, e = cmd(self.command)
        print o
        if e:
            raise Exception(e)
        print e

# vim: et sw=4 sts=4
