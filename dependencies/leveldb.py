# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["env"])

# Create a temporary environment to be able to modify it locally.
leveldb_lib_env = env.Clone()
leveldb_lib_env.AppendUnique(CPPPATH=['leveldb'])
if os.name == 'nt':
    leveldb_lib_env.AppendUnique(CPPDEFINES=['LEVELDB_PLATFORM_WINDOWS'])
else:
    leveldb_lib_env.AppendUnique(CPPDEFINES=['LEVELDB_PLATFORM_POSIX'])
    leveldb_lib_env.AppendUnique(CPPFLAGS=['-std=c++11'])
# Activate symbol exporting.
if leveldb_lib_env['CC'] == 'cl':
  # Set warning level to 3 (highest, before all warnings).
  leveldb_lib_env.AppendUnique(CPPFLAGS='/W3')
file_list = Glob('leveldb/table/*.cc') +\
            Glob('leveldb/util/*.cc') + \
            Glob('leveldb/helpers/memenv/memenv.cc') + \
            Glob('leveldb/db/*.cc')
# Excludes
if os.name == 'nt':
    file_list = [fn for fn in file_list \
                 if not str(fn).endswith("test.cc") and \
                    not str(fn).endswith("env_posix.cc") and \
                    not str(fn).endswith("env_chromium.cc")]
    file_list += [Glob('leveldb/port/port_win.cc')]
else:
    file_list = [fn for fn in file_list \
                 if not str(fn).endswith("test.cc") and \
                    not str(fn).endswith("win_logger.cc") and \
                    not str(fn).endswith("env_chromium.cc")]
    file_list += [Glob('leveldb/port/port_posix.cc')]
headers = Glob('leveldb/include/*.h')
libfile = leveldb_lib_env.StaticLibrary('leveldb', file_list)
installed_libfile = leveldb_lib_env.InstallAs(os.path.join(str(Dir('../lib').srcnode()),
                                                           os.path.basename(str(libfile[0]))), libfile[0])
# The library.
Return("libfile", "headers")
