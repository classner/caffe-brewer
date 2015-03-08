# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["env"])

if os.name == 'nt':
    # Create a temporary environment to be able to modify it locally.
    glog_lib_env = env.Clone()
    glog_lib_env['CPPPATH'] = ''
    glog_lib_env['CPPDEFINES'] = ''
    glog_lib_env['CPPFLAGS'] = ''
    # Activate symbol exporting.
    if glog_lib_env['CC'] == 'cl':
      # Set warning level to 3 (highest, before all warnings).
      glog_lib_env.AppendUnique(CPPFLAGS=['/W3'])
      glog_lib_env.AppendUnique(CPPFLAGS=['/TP'])
      glog_lib_env.AppendUnique(CPPFLAGS=['/MD'])
      glog_lib_env.AppendUnique(CPPFLAGS=['/EHsc'])
      glog_lib_env.AppendUnique(CPPFLAGS=['/nologo'])
      glog_lib_env.AppendUnique(CPPFLAGS=['/GL'])
      glog_lib_env.AppendUnique(CPPDEFINES='GOOGLE_GLOG_DLL_DECL=')
      
    subfolder = 'glog-0.3.3'
    glog_lib_env.AppendUnique(CPPPATH='%s' % subfolder)
    glog_lib_env.AppendUnique(CPPPATH=['%s/src/windows' % subfolder])
    # Create the build file list.
    file_list = Glob('%s/src/logging.cc' % subfolder) +\
                Glob('%s/src/windows/port.cc' % subfolder) +\
                Glob('%s/src/raw_logging.cc' % subfolder) +\
                Glob('%s/src/utilities.cc' % subfolder) +\
                Glob('%s/src/vlog_is_on.cc' % subfolder)
    headers = Glob('%s/src/*.h' % subfolder)
    # The library.
    libfile = glog_lib_env.StaticLibrary('glog', file_list)
    installed_libfile = glog_lib_env.InstallAs(os.path.join(str(Dir('../lib').srcnode()),
                                                            os.path.basename(str(libfile[0]))), libfile[0])
else:
    # rely on the platform provided build.
    installed_libfile = 'glog'
    headers = []
Return("installed_libfile", "headers")
