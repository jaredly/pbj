#!/usr/bin/env python

from utils import get_builder, pytest_funcarg__build

def test_setup():
    build = get_builder()
    assert build.name == 'TestBuilder'

def test_target(build):
    @build.target
    def one():
        print 'doing good things'
        return 'Success'

    assert build.targets[0] == one
    assert build.targets[0].name == 'one'
    assert one.applies_to('@one')

def test_filetarget(build):
    @build.file('output/main.py')
    def two():
        return 45

'''TODO:

    test inheritance
    make a function to list the targets to be built (basically get_all_dependencies)
    make a 'has_run' flag for a target and a 'return_value' attribute to store it

    test all the target types

    test group targets and multi targets
    test tons of other stuff

    test argument parsing
    test function doc magic
    test manual naming
    test 'always' flag
    test completion lists
    '''

# vim: et sw=4 sts=4
