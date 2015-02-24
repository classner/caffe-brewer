# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["core_objects", "link_libs", "env"])

# Create a temporary environment to be able to modify it locally.
tests_env = env.Clone()

file_list = Glob('caffe-framework/src/gtest/gtest_main.cpp') + \
            Glob('caffe-framework/src/gtest/gtest-all.cpp') + \
            Glob('caffe-framework/src/caffe/test/*.cpp')

tests_env.PrependUnique(LIBS=link_libs)

test_objects = []
for tfile in file_list:
    test_objects.append(tests_env.SharedObject(tfile))

test_program = tests_env.Program(target='gtest-all', source=core_objects+test_objects)

tests_executable = tests_env.Install(Dir('./caffe-framework').srcnode(), test_program)
# The library.
Return("test_program")
