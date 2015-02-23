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
# It is necessary to circumvent the automatic symbol removal from the
# static library.
if os.name != 'nt':
  py_env.PrependUnique(LIBS=link_libs[1:])
  py_env['LINKFLAGS']='-Wl,--whole-archive %s -Wl,--no-whole-archive' % (str(link_libs[0][0]))
else:
  py_env.PrependUnique(LIBS=link_libs)
py_module = py_env.SharedLibrary(file_list)
if os.name != 'nt':
  py_env.Depends(py_module, link_libs[0])
# The module.
Return("py_module")
