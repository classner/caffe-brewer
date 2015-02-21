# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["env"])

# Create a temporary environment to be able to modify it locally.
gpu_lib_env = env.Clone()
gpu_lib_env['CPPDEFINES'] = []
if GetOption("cpu_only"):
    file_list = []
else:
    file_list = Glob('caffe-framework/src/caffe/layers/*.cu')

cufiles = []
for fil in file_list:
    cufiles.append(gpu_lib_env.SharedObject(fil))

# The library.
Return("cufiles")
