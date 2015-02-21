# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["env"])

# Create a temporary environment to be able to modify it locally.
mdb_lib_env = env.Clone()
mdb_lib_env.AppendUnique(CPPPATH=['mdb/libraries/libmdb'])
if os.name != 'nt':
    mdb_lib_env.Append(LIBS=['pthread'])

# Activate symbol exporting.
if mdb_lib_env['CC'] == 'cl':
  # Set warning level to 3 (highest, before all warnings).
  mdb_lib_env.AppendUnique(CPPFLAGS='/W3')
file_list = Glob('mdb/libraries/liblmdb/mdb.c') + \
            Glob('mdb/libraries/liblmdb/midl.c')
headers =   Glob('mdb/libraries/liblmdb/mdb.h') + \
            Glob('mdb/libraries/liblmdb/midl.h')
lib = mdb_lib_env.StaticLibrary('mdb', file_list)
# The library.
Return("lib", "headers")
