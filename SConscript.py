# -*- python -*-
# Author: Christoph Lassner.

import os
import sys
import platform
import sysconfig
import subprocess
from SConsChecks import AddLibOptions, GetLibChecks

_libs = ['boost.datetime',
         'boost.system',
         'boost.filesystem',
         'boost.interprocess',
         'boost.thread',
         'hdf5',
		 'numpy',
         'openblas',
         'opencv',
		 'python',
         'boost.python',
         'protobuf',
         'cuda']

_checks = GetLibChecks(_libs)

def getRequiredLibs():
  req_libs = _libs[:]
  if not GetOption("with_python"):
    req_libs = [lib for lib in req_libs if lib != 'boost.python' and \
	                                       lib != 'python' and \
										   lib != 'numpy']
  if GetOption("cpu_only"):
    req_libs = [lib for lib in req_libs if not lib == 'cuda']
  return req_libs

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
def setupOptions(rpath=True, python=True, tools=True, libs=True):
    default_toolchain = 'default'
    if platform.system() == 'Windows':
        default_prefix = r'C:\Libraries'
        default_caffe_temp = r'C:\temp'
    else:
        default_prefix = "/usr/local"
        default_caffe_temp = r'/tmp'
    if rpath:
        AddOption("--rpath", dest="custom_rpath", type="string", action="store",
                  help="runtime link paths to add to libraries and executables (unix); may be passed more than once")
    if python:
        AddOption("--with-python", help="build the Python interface", action="store_true",
                  dest="with_python", default=False)
    if tools:
        AddOption("--with-tools", help="build the tools", action="store_true",
                  dest="with_tools", default=False)
    AddOption("--temp-folder", dest="caffe_temp", type="string", action="store",
              help=r"temp path for the caffe framework. Default: C:\temp for Win, /tmp for Lin.",
              default=default_caffe_temp)
    AddOption("--cuda-architectures", dest="cuda_architectures", type="string", action="store",
              help="the CUDA architectures ;-separated. Default: 20;30;35;50",
              default='20;30;35;50')
    AddOption("--cpu-only", help="build only CPU support without GPU", action="store_true",
              dest="cpu_only", default=False)
    # Add library configuration options.
    if libs:
        AddLibOptions(AddOption, _libs)
    # Default variables.
    variables = Variables()
    # Enable optimization, building of debug symbols.
    flags_default =  "-O2"
    if os.name == 'nt':
      flags_default = "/O2"
    variables.Add("CCFLAGS", default=os.environ.get("CCFLAGS", flags_default), help="compiler flags")
    return variables

def makeEnvironment(variables, root='.'):
    shellEnv = {}
    # Some of these don't make sense on Windows, but don't hurt.
    for key in ("PATH",
                "LD_LIBRARY_PATH",
                "DYLD_LIBRARY_PATH",
                "PYTHONPATH",
                "CUDA_TOOLKIT_PATH",
                "CUDA_SDK_PATH",
                "PROTOC"):
        if key in os.environ.keys():
            shellEnv[key] = os.environ[key]
    # Create build enviromnent.
    env = Environment(variables=variables, ENV=shellEnv)
    if os.name == 'nt':
        try:
            env["PROTOC"] = os.environ["PROTOC"]
        except:
            print "It is necessary to define the environment variable "+\
                  "PROTOC with the executable of the protocol buffers "+\
                  "compiler!"
            sys.exit(1)
    else:
        try:
            env["PROTOC"] = os.environ["PROTOC"]
        except:
            print "Environment variable PROTOC not defined. Using the "+\
                  "result of `which protoc` as fallback."
            # Try determining the path by searching for the executable.
            env["PROTOC"] = os.popen("which protoc").read().strip()
    print "Using protoc at %s." % (env["PROTOC"])
    if not GetOption("cpu_only"):
        env.Tool('nvcc')
    env.Tool('protoc')
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
        env.AppendUnique(LINKFLAGS=["/OPT:NOREF"])
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
    env.PrependUnique(CPPPATH=[Dir('%s/caffe-framework/include'%(root)).abspath])
    # Contains the gtest includes.
    env.PrependUnique(CPPPATH=[Dir('%s/caffe-framework/src'%(root)).abspath])
    # Configuration options.
    if GetOption('cpu_only'):
        env.AppendUnique(CPPDEFINES=['CPU_ONLY'])
    # Add dependency include folders.
    if os.name == 'nt':
        env.PrependUnique(CPPPATH=[Dir('%s/dependencies/glog-0.3.3/src/windows'%(root)).abspath])
        env.PrependUnique(CPPPATH=[Dir('%s/dependencies/gflags-2.1.1/include'%(root)).abspath])
        env.PrependUnique(CPPDEFINES=['GOOGLE_GLOG_DLL_DECL='])
    else:
        env.PrependUnique(CPPPATH=[Dir('%s/dependencies/gflags-2.1.1-linux/include'%(root)).abspath])
    env.PrependUnique(CPPPATH=[Dir(r'%s/dependencies/leveldb/include'%(root)).abspath])
    env.PrependUnique(CPPPATH=[Dir(r'%s/dependencies/mdb/libraries/liblmdb'%(root)).abspath])
    if os.name != 'nt':
        env.AppendUnique(LIBS=['pthread', 'glog'])
        env.AppendUnique(CPPFLAGS=['-fPIC'])
    return env

def setupTargets(env, root="."):
    # Create the protobuffer files.
    proto_files = env.Protoc('%s/caffe-framework/src/caffe/proto/caffe.proto'%(root),
                             PROTOC_PATH='%s/caffe-framework/src/caffe/proto'%(root),
                             PROTOC_CCOUT='%s/caffe-framework/src/caffe/proto'%(root),
                             PROTOC_PYOUT='%s/python/caffe/proto'%(root))
    proto_header_list = [protof for protof in proto_files if str(protof).endswith('.pb.h')]
    assert len(proto_header_list) == 1
    proto_header = env.InstallAs(os.path.join(str(Dir('include').srcnode()),
                                              'caffe',
                                              'proto',
                                              'caffe.pb.h'), proto_header_list[0])
    # Build gflags.
    gflags_lib, gflags_headers = SConscript(os.path.join(root, "dependencies", "gflags.py"),
                                    exports=['env'],
                                    variant_dir='build/gflags')
    # Build glog on Windows.
    glog_lib, glog_headers = SConscript(os.path.join(root, "dependencies", "glog.py"),
                                    exports=['env'],
                                    variant_dir='build/glog')
    # Build leveldb.
    leveldb_lib, leveldb_headers = SConscript(os.path.join(root, "dependencies", "leveldb.py"),
                                    exports=['env'],
                                    variant_dir='build/leveldb')
    # Build lmdb.
    mdb_lib, mdb_headers = SConscript(os.path.join(root, "dependencies", "mdb.py"),
                                      exports=['env'],
                                      variant_dir='build/mdb')
    # Build the CUDA parts.
    cu_objects, cu_lib = SConscript(os.path.join(root, "gpu.py"),
                                    exports=['env'],
                                    variant_dir='build/CUDA')
    # Build the library core.
    core_objects, headers = SConscript(os.path.join(root, "core.py"),
                                       exports=['proto_files', 'env'],
                                       variant_dir='build/core')
    headers += proto_header
    link_libs = [mdb_lib, leveldb_lib, gflags_lib, glog_lib]
    if not GetOption("cpu_only"):
        link_libs.insert(0, cu_lib)
    if os.name == 'nt':
          link_libs.extend(['shlwapi.lib'])
    # Build the tests.
    test_program = SConscript(os.path.join(root, "tests.py"),
                              exports=['core_objects', 'link_libs', 'env'],
                              variant_dir='build/tests')
    if GetOption("with_python"):
        # Build the python interface.
        pycaffe = SConscript(os.path.join(root, "python.py"),
                             exports=['core_objects', 'link_libs', 'env'],
                             variant_dir='build/python')
    if GetOption("with_tools"):
        caffetools = SConscript(os.path.join(root, "tools.py"),
                                exports=['core_objects', 'link_libs', 'env'],
                                variant_dir='build/tools')
    return headers, core_objects, link_libs

Return("setupOptions",
       "makeEnvironment",
       "setupTargets",
       "_checks",
       "getRequiredLibs")
