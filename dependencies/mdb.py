# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["env"])

# Create a temporary environment to be able to modify it locally.
mdb_lib_env = env.Clone()
mdb_lib_env.AppendUnique(CPPPATH=['mdb/libraries/libmdb'])
if os.name != 'nt':
    mdb_lib_env.Append(LIBS=['pthread'])
else:
    # Apply hotpatch for Windows.
    print("Applying LMDB hotpatch for Windows.")
    lines = []
    with open(os.path.join(Dir('.').srcnode().abspath,
                           'mdb',
                           'libraries',
                           'liblmdb',
                           'mdb.c'), 'r') as infile:
      for line in infile:
        if line.strip().startswith("#include <inttypes.h>"):
           lines.append("#include <stdint.h>" + os.linesep)
           lines.append("#include <stddef.h>" + os.linesep)
           lines.append("#include <sys/types.h>" + os.linesep)
           lines.append("typedef int64_t ssize_t;" + os.linesep)
           continue
        elif line.strip().startswith("#include <unistd.h>"):
           continue
        else:
            lines.append(line)
    with open(os.path.join(Dir('.').srcnode().abspath,
                           'mdb',
                           'libraries',
                           'liblmdb',
                           'mdb.c'), 'w') as outfile:
      outfile.writelines(lines)
    print("Success! You might have to restart a clean build to use the "+\
          "updated sources.")

# Create a temporary environment to be able to modify it locally.
mdb_lib_env['CPPPATH'] = ''
mdb_lib_env['CPPDEFINES'] = ''
# Activate symbol exporting.
if mdb_lib_env['CC'] == 'cl':
  # Set warning level to 3 (highest, before all warnings).
  mdb_lib_env.AppendUnique(CPPFLAGS='/W3')
  mdb_lib_env.AppendUnique(CPPFLAGS='/MD')
  mdb_lib_env.AppendUnique(CPPFLAGS='/GL')
  mdb_lib_env.AppendUnique(CPPFLAGS=['/nologo'])
  mdb_lib_env.AppendUnique(CPPDEFINES='_WIN32;_WINDOWS'.split(';'))
  mdb_lib_env.AppendUnique(CCFLAGS=["/Zi", "/Fd${TARGET}.pdb"])
  mdb_lib_env.AppendUnique(CCFLAGS=['/O2'])
else:
  mdb_lib_env.AppendUnique(CCFLAGS=['-O2','-std=c++11','-g','-fPIC'])

file_list = Glob('mdb/libraries/liblmdb/mdb.c') + \
            Glob('mdb/libraries/liblmdb/midl.c')
headers =   Glob('mdb/libraries/liblmdb/mdb.h') + \
            Glob('mdb/libraries/liblmdb/midl.h')
libfile = mdb_lib_env.StaticLibrary('mdb', file_list)
installed_libfile = mdb_lib_env.InstallAs(os.path.join(str(Dir('../lib').srcnode()),
                                                       os.path.basename(str(libfile[0]))), libfile[0])
# The library.
Return("installed_libfile", "headers")
