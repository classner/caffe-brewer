# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["link_libs", "env"])

# Create a temporary environment to be able to modify it locally.
tests_env = env.Clone()

# Activate symbol exporting.
if tests_env['CC'] == 'cl':
  # Set warning level to 3 (highest, before all warnings).
  tests_env.AppendUnique(CPPFLAGS='/W3')
file_list = Glob('caffe-framework/src/gtest/gtest_main.cpp') + \
            Glob('caffe-framework/src/gtest/gtest-all.cpp') + \
            Glob('caffe-framework/src/caffe/test/*.cpp')
# It is necessary to circumvent the automatic symbol removal from the
# static library.
if os.name != 'nt':
  tests_env.PrependUnique(LIBS=link_libs[1:])
  tests_env['LINKFLAGS']='-Wl,--whole-archive %s -Wl,--no-whole-archive' % (str(link_libs[0][0]))
else:
  tests_env.PrependUnique(LIBS=link_libs)
test_program = tests_env.Program(file_list)
if os.name != 'nt':
  tests_env.Depends(test_program, link_libs[0])
# The library.
Return("test_program")
