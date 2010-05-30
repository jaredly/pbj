from target import Target
from reg import register

from subprocess import Popen, PIPE
import os

def cmd(*command):
    if len(command) == 1 and type(command[0]) in (list, tuple):
        command = command[0]
    p = Popen('zsh', stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
    p.stdin.write('cd ' + os.getcwd() + '\n')
    # p.stdin.write('pwd\n')
    p.stdin.write(' '.join(command))
    p.stdin.close()
    out = p.stdout.read()
    err = p.stderr.read()
    # print out, err
    return out, err

@register('cmd', required=2)
class CmdTarget(Target):
    def __init__(self, name, command, echo=True, **kwargs):
        Target.__init__(self, name, **kwargs)
        self.command = command
        self.echo = echo

    def __call__(self, function):
        raise Exception('CmdTarget is not a function wrapper')

    def run(self):
        if self.echo:
            print self.command
        o, e = cmd(self.command)
        if o:
            print o,
        if e:
            raise Exception(e)

# vim: et sw=4 sts=4
