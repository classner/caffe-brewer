# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["proto_files", "env"])

# Create a temporary environment to be able to modify it locally.
core_lib_env = env.Clone()

# Activate symbol exporting.
if core_lib_env['CC'] == 'cl':
  # Set warning level to 3 (highest, before all warnings).
  core_lib_env.AppendUnique(CPPFLAGS='/W3')
file_list = proto_files[:1] + \
            Glob('caffe-framework/src/caffe/*.cpp') + \
            Glob('caffe-framework/src/caffe/layers/*.cpp') + \
            Glob('caffe-framework/src/caffe/util/*.cpp')
headers = proto_files[1:] + \
          Glob('caffe-framework/include/caffe/*.hpp') + \
          Glob('caffe-framework/include/caffe/util/*.hpp')
shared_objects = []
for cfile in file_list:
    shared_objects.append(core_lib_env.SharedObject(cfile))

# The library.
Return("shared_objects", "headers")
