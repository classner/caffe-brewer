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

test_exec = tests_env.Program(target='caffe-gtest-all', source=core_objects+test_objects)
installed_test_exec = tests_env.Install(Dir('./bin').srcnode(), test_exec)
# Install test-datafiles.
testfiles = Glob('caffe-framework/src/caffe/test/test_data/*') +\
            Glob('caffe-framework/examples/images/*')
for tfile in testfiles:
    relative = os.path.relpath(tfile.abspath, Dir('caffe-framework').abspath)
    tests_env.InstallAs(os.path.join(str(Dir('bin').srcnode()),
                                     relative), tfile)
Return("installed_test_exec")
