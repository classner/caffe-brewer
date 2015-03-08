# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["core_objects", "link_libs", "env"])

# Create a temporary environment to be able to modify it locally.
py_env = env.Clone()

# Activate symbol exporting.
if py_env['CC'] == 'cl':
  # Set warning level to 3 (highest, before all warnings).
  py_env.AppendUnique(CPPFLAGS='/W3')

# SCons thinks that the core objects are static objects, which they are
# not. Workaround this.
# See http://stackoverflow.com/questions/2246399/scons-to-make-a-shared-library-so-with-a-static-libarary-a
py_env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME']=1
sourcefile = Glob('caffe-framework/python/caffe/_caffe.cpp')
# py_env['LINKFLAGS']='-Wl,--whole-archive %s -Wl,--no-whole-archive' % (str(link_libs[0][0]))
py_env.PrependUnique(LIBS=link_libs)
py_object = py_env.SharedObject(sourcefile)
py_module = py_env.SharedLibrary([py_object] + core_objects)

# Install.
collected_files = Glob('caffe-framework/python/*.py') +\
                  Glob('caffe-framework/python/requirements.txt') +\
                  Glob('caffe-framework/python/caffe/*.py') +\
                  Glob('caffe-framework/python/caffe/*/*')
for fobj in collected_files:
    relative = os.path.relpath(fobj.abspath, Dir('caffe-framework/python').abspath)
    py_env.InstallAs(os.path.join(str(Dir('python').srcnode()),
                                      relative), fobj)
    if os.name == 'nt':
      installed_py_module = py_env.InstallAs(os.path.join(str(Dir('python').srcnode()),
                                                          'caffe',
                                                          '_caffe.pyd'), py_module)
    else:
      installed_py_module = py_env.InstallAs(os.path.join(str(Dir('python').srcnode()),
                                                          'caffe',
                                                          '_caffe.so'), py_module)

# The module.
Return("py_module")
