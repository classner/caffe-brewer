# -*- python -*-
# Author: Christoph Lassner.

import os
import sys
import platform
import sysconfig
import subprocess
from SConsChecks import AddLibOptions, GetLibChecks

_libs = ['boost.datetime',      # leveldb
         'boost.filesystem',
         'boost.interprocess',
         'boost.thread',
         'swig']

_checks = GetLibChecks(_libs)

def getRequiredLibs():
  return _libs

####################################
# Command line length fix for compilers other than MSVC on Windows.
# http://scons.org/wiki/LongCmdLinesOnWin32
if os.name == 'nt':
    import win32file
    import win32event
    import win32process    
    import win32security
    def my_spawn(sh, escape, cmd, args, spawnenv):
        for var in spawnenv:
            spawnenv[var] = spawnenv[var].encode('ascii', 'replace')
        sAttrs = win32security.SECURITY_ATTRIBUTES()
        StartupInfo = win32process.STARTUPINFO()
        newargs = ' '.join(map(escape, args[1:]))
        cmdline = cmd + " " + newargs
        # check for any special operating system commands
        if cmd == 'del':
            for arg in args[1:]:
                win32file.DeleteFile(arg)
            exit_code = 0
        else:
            # otherwise execute the command.
            hProcess, hThread, dwPid, dwTid = win32process.CreateProcess(None, cmdline, None, None, 1, 0, spawnenv, None, StartupInfo)
            win32event.WaitForSingleObject(hProcess, win32event.INFINITE)
            exit_code = win32process.GetExitCodeProcess(hProcess)
            win32file.CloseHandle(hProcess);
            win32file.CloseHandle(hThread);
        return exit_code

def SetupSpawn( env ):
    if env['CC'] == 'g++' and sys.platform == 'win32':
        # Enable workaround for handling of extralong
        # command lines. This is not handled by the
        # default toolchain spawner of SCons in this
        # case.
        env['SPAWN'] = my_spawn
#####################################

# Setup command-line options
def setupOptions():
    default_toolchain = 'default'
    if platform.system() == 'Windows':
        default_prefix = r'C:\Libraries'
    else:
        default_prefix = "/usr/local"
    AddOption("--prefix-dir", dest="prefix", type="string", nargs=1, action="store",
              metavar="DIR", default=default_prefix, help="installation prefix")
    AddOption("--install-headers-dir", dest="install_headers", type="string", nargs=1, action="store",
              metavar="DIR", help="location to install header files (overrides --prefix for headers)")
    AddOption("--install-lib-dir", dest="install_lib", type="string", nargs=1, action="store",
              metavar="DIR", help="location to install libraries (overrides --prefix for libraries)")
    AddOption("--rpath", dest="custom_rpath", type="string", action="store",
              help="runtime link paths to add to libraries and executables (unix); may be passed more than once")
    AddOption("--cpu-only", help="build only CPU support without GPU", action="store_true",
              dest="cpu_only", default=False)
    # Add library configuration options.
    AddLibOptions(AddOption, _libs)
    # Default variables.
    variables = Variables()
    # Enable optimization, building of debug symbols.
    flags_default =  "-O2"
    if os.name == 'nt':
      flags_default = "/O2"
    variables.Add("CCFLAGS", default=os.environ.get("CCFLAGS", flags_default), help="compiler flags")
    return variables

def makeEnvironment(variables):
    shellEnv = {}
    # Some of these don't make sense on Windows, but don't hurt.
    for key in ("PATH",
                "LD_LIBRARY_PATH",
                "DYLD_LIBRARY_PATH",
                "PYTHONPATH",
                "CUDA_TOOLKIT_PATH",
                "CUDA_SDK_PATH"):
        if key in os.environ.keys():
            shellEnv[key] = os.environ[key]
    # Create build enviromnent.
    env = Environment(variables=variables, ENV=shellEnv)
    env["CUDA_TOOLKIT_PATH"] = os.environ["CUDA_TOOLKIT_PATH"]
    env["CUDA_SDK_PATH"] = os.environ["CUDA_TOOLKIT_PATH"]
    if not GetOption("cpu_only"):
        env.Tool('nvcc')
        # cudart is automatically added by the cuda build tool.
        env.AppendUnique(LIBS=['cublas', 'cublas_device',
                               'cufft', 'curand'])
    # Append environment compiler flags.
    if env.Dictionary().has_key("CCFLAGS"):
        if isinstance(env['CCFLAGS'], basestring):
            env['CCFLAGS'] = env['CCFLAGS'].split()
    if os.environ.has_key("CCFLAGS"):
        env.AppendUnique(CCFLAGS=os.environ.get("CCFLAGS").split())
    # Specifics for MSVC.
    if env['CC'] == 'cl' or env['CC'] == 'icl' and os.name == 'nt':
        # Enable C++ exception handling.
        env.Append(CCFLAGS=['/EHsc'])
        # Enable .dll and .exe builds without GUI.
        env.AppendUnique(LINKFLAGS=['/SUBSYSTEM:CONSOLE'])
        # Linker debug symbol generation, link time code generation.
        env.AppendUnique(LINKFLAGS=["/DEBUG", "/LTCG"])
        # Enable whole program optimization.
        env.AppendUnique(CCFLAGS=['/GL'])
        # Suppress Microsoft disclaimer display on console.
        env.AppendUnique(CPPFLAGS=['/nologo'])
        # Allow up to 10 elements for variadic template spec.
        env.AppendUnique(CPPDEFINES=['_VARIADIC_MAX=10'])
        # Each object has its own pdb, so -jN works
        env.AppendUnique(CCFLAGS=["/Zi", "/Fd${TARGET}.pdb"])
    # Specifics for icl.
    if env['CC'] == 'icl':
        # 3199: triggered in boost serialization
        # 2586: decorated name length exceeded
        # 11081: Python on Windows tries to link via a pragma comment, but 
        #        the library is linked explicitely.
        env.AppendUnique(CCFLAGS=['-wd3199,2586,11081'])
        # Replace /GL with /Qipo-jobs4, which is a speeded up version.
        #env.Replace(CCFLAGS=[flag for flag in env['CCFLAGS'] if flag not in ['/GL']])
        #env.AppendUnique(CCFLAGS=['/Qipo-jobs4'])
    # Specifics for gcc.
    if env['CC'] == 'g++' or env['CC'] == 'gcc':
        # Replace default /O2 on Windows if MinGW is used.
        if '/O2' in env['CCFLAGS']:
          env.Replace(CCFLAGS=[flag for flag in env['CCFLAGS'] \
            if flag not in ['/O2']] + ['-O2'])
        # Enable C++ 11 support, OpenMP, and generation of debug symbols.
        env.AppendUnique(CCFLAGS=['-std=c++11', '-g'])
        env.AppendUnique(LINKFLAGS=['-g'])
    # RPATH.
    custom_rpath = GetOption("custom_rpath")
    if custom_rpath is not None:
        env.AppendUnique(RPATH=custom_rpath)
    # Set the 'no debug' symbol.
    env.AppendUnique(CPPDEFINES=['NDEBUG'])
    if os.name == 'nt':
        env.AppendUnique(CPPDEFINES=['LEVELDB_PLATFORM_WINDOWS', 'OS_WIN', 'WIN32'])
    if env['CC'] == 'cl' or env['CC'] == 'icl' and os.name == 'nt':
      # Link against non-debug system libraries.
      env.AppendUnique(CPPFLAGS=['/MD'])
    # Main library include folder.
    env.PrependUnique(CPPPATH=[Dir('#caffe-framework/include').abspath])
    # contains the gtest includes.
    env.PrependUnique(CPPPATH=[Dir('#caffe-framework/src').abspath])
    # Add dependency include folders.
    print env['CPPPATH']
    env.PrependUnique(CPPPATH=[Dir('#dependencies/glog-0.3.3/src/windows').abspath])
    env.PrependUnique(CPPPATH=[Dir('#dependencies/gflags-2.1.1/include').abspath])
    env.PrependUnique(CPPPATH=[Dir(r'C:\Users\lassnech\Desktop\git\protobuf\src').abspath])
    env.PrependUnique(CPPPATH=[Dir(r'C:\Libraries\OpenBLAS-v0.2.13-Win64-int64\include').abspath])
    env.PrependUnique(CPPPATH=[Dir(r'P:\temp\opencv\opencv\build\include').abspath])
    env.PrependUnique(CPPPATH=[Dir(r'C:\Libraries\HDF5\1.8.14\include').abspath])
    env.PrependUnique(CPPPATH=[Dir(r'C:\Users\lassnech\Desktop\git\leveldb\include').abspath])
    env.PrependUnique(CPPPATH=[Dir(r'C:\Users\lassnech\Desktop\git\mdb\libraries\liblmdb').abspath])
    env.PrependUnique(CPPPATH=[Dir('#proto_include').abspath])
    #for ipth in env['CPPPATH']:
    #    env.PrependUnique(NVCCFLAGS=['-I"%s"' % ipth])
    return env

def setupTargets(env, root="."):
    file_list = Glob('caffe-framework/src/caffe/*.cpp') #+ \
    cu_file_list = Glob('caffe-framework/src/caffe/layers/*.cu')# + \
                #Glob('caffe-framework/src/caffe/util/*.cpp') #+ \
                #Glob('caffe-framework/src/caffe/layers/*.cu') + \
    # Excludes
    file_list = [fn for fn in file_list \
                 if not str(fn).endswith("123data_transformer.cpp") and \
                    not str(fn).endswith("env_posix.cc") and \
                    not str(fn).endswith("env_chromium.cc")]
    headers = Glob('caffe-framework/include/caffe/*.hpp') + \
              Glob('caffe-framework/include/caffe/util/*.hpp')
    lib = env.SharedLibrary('caffe', file_list)
    #env['CPPDEFINES'] = []
    culib = env.StaticLibrary('caffegpu', cu_file_list)
    if os.name == 'nt':
        #project_lib = env.InstallAs(os.path.join(Dir('#lib').abspath, os.path.basename(lib[1].abspath)), lib[1])
        project_bin = env.InstallAs(os.path.join(Dir('#bin').abspath, os.path.basename(lib[0].abspath)), lib[0])
    else:
        #project_lib = env.InstallAs(os.path.join(Dir('#lib').abspath, os.path.basename(lib[0].abspath)), lib[0])
        project_bin = env.InstallAs(os.path.join(Dir('#bin').abspath, os.path.basename(lib[0].abspath)), lib[0])
    # Install in installation folders.
    prefix = Dir(GetOption("prefix")).abspath
    install_headers = GetOption('install_headers')
    install_lib = GetOption('install_lib')
    if not install_headers:
      install_headers = os.path.join(prefix, "include")
    if not install_lib:
      install_lib = os.path.join(prefix, "lib")
    env.Alias("install", env.Install(install_lib, lib))
    for header in Flatten(headers):
        relative = os.path.relpath(header.abspath, Dir('#include').abspath)
        env.Alias("install", env.InstallAs(os.path.join(install_headers,
                                                        'leveldb',
                                                        relative), header))

Return("setupOptions",
       "makeEnvironment",
       "setupTargets",
       "_checks",
       "getRequiredLibs")
