# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["env"])

# Create a temporary environment to be able to modify it locally.
gflags_lib_env = env.Clone()
# Activate symbol exporting.
if gflags_lib_env['CC'] == 'cl':
  # Set warning level to 3 (highest, before all warnings).
  gflags_lib_env.AppendUnique(CPPFLAGS='/W3')
if os.name == 'nt':
    subfolder = 'gflags-2.1.1'
else:
    subfolder = 'gflags-2.1.1-linux'
gflags_lib_env.AppendUnique(CPPPATH=['%s/include/gflags' % subfolder])
# Create the build file list.
file_list = Glob('%s/*.cc' % subfolder)
headers = Glob('%s/include' % subfolder)
# The library.
lib_file = gflags_lib_env.StaticLibrary('gflags', file_list)
Return("lib_file", "headers")
