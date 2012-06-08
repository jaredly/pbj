#!/usr/bin/env python

import pytest

from utils import get_builder, pytest_funcarg__build, pytest_funcarg__capture

def test_one(build):
    @build.group(name='big')
    class MyMan:
        @build.target
        def one():
            return 43

    assert build.get_targets_for('@big') == [MyMan]
    assert build.get_targets_for('@big.one') == [MyMan.targets['one']]

if __name__=='__main__':
    test_one(pytest_funcarg__build(None))

# vim: et sw=4 sts=4
