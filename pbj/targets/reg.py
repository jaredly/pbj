
target_reg = {}

def register(name, required=0):
    if name in ('_resolve', 'add', 'run'):
        raise ValueError('"%s" is reserved' % name)
    def meta(cls):
        target_reg[name] = cls, required
        return cls
    return meta

# vim: et sw=4 sts=4
