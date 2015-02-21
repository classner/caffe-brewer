# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["link_libs", "env"])

# Create a temporary environment to be able to modify it locally.
py_env = env.Clone()

# Activate symbol exporting.
if py_env['CC'] == 'cl':
  # Set warning level to 3 (highest, before all warnings).
  py_env.AppendUnique(CPPFLAGS='/W3')
file_list = Glob('caffe-framework/python/caffe/_caffe.cpp')
py_env.PrependUnique(LIBS=link_libs)
py_module = py_env.SharedLibrary(file_list)
# The module.
Return("py_module")
