from reg import register
from cmd import CmdTarget

@register('clean', required=1)
def clean(*files):
    return CmdTarget('clean', ('rm', '-rf') + tuple(files))

# vim: et sw=4 sts=4
