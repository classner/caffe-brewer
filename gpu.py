# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["env"])

# Create a temporary environment to be able to modify it locally.
gpu_lib_env = env.Clone()
gpu_lib_env['CPPDEFINES'] = []
gpu_lib_env['CCFLAGS'] = [flag for flag in gpu_lib_env['CCFLAGS'] if flag != '-std=c++11' and flag != '-fPIC']
gpu_lib_env['CFLAGS'] = [flag for flag in gpu_lib_env['CFLAGS'] if flag != '-std=c++11' and flag != '-fPIC']
gpu_lib_env['SHCFLAGS'] = [flag for flag in gpu_lib_env['SHCFLAGS'] if flag != '-std=c++11' and flag != '-fPIC']
gpu_lib_env['SHCCFLAGS'] = [flag for flag in gpu_lib_env['SHCCFLAGS'] if flag != '-std=c++11' and flag != '-fPIC']
gpu_lib_env['CCFLAGS'] = ''

if gpu_lib_env.GetOption('debug_build'):
	gpu_lib_env.AppendUnique(SHCCFLAGS=["-D_CUDACC_", "-D_DEBUG", "-g", "-O0", "-G"]) 

if GetOption("cpu_only"):
    file_list = []
else:
    file_list = Glob('caffe-framework/src/caffe/layers/*.cu') +\
                Glob('caffe-framework/src/caffe/util/*.cu')
# Boost 1.54 workaround.
#gpu_lib_env.AppendUnique(CPPFLAGS=['-DBOOST_NOINLINE=__attribute__((noinline))'])
for archi in GetOption('cuda_architectures').split(';'):
    gpu_lib_env.Append(SHCCFLAGS=['-gencode', 'arch=compute_%s,code=compute_%s' % (archi, archi)])
cufiles = []
for fil in file_list:
    cufiles.append(gpu_lib_env.SharedObject(fil))
culib = gpu_lib_env.StaticLibrary(target='caffe-gpu', source=cufiles)
if not GetOption('cpu_only'):
    installed_culib = gpu_lib_env.InstallAs(os.path.join(str(Dir('lib').srcnode()),
                                                         os.path.basename(str(culib[0]))), culib)
# The library.
Return("cufiles", "culib")
