#!/usr/bin/env python

import pytest

from utils import get_builder, pytest_funcarg__build, pytest_funcarg__capture

def test_cmd(build, capture):
    one = build.cmd('moveit', ('echo', 'hello'), echo=False)
    assert one.name == 'moveit'
    assert one.command == ('echo', 'hello')
    capture.on()
    one.run()
    capture.off()
    assert capture.out == 'hello\n'
    assert one.has_run
    assert one.return_value == 'hello\n'



# vim: et sw=4 sts=4
