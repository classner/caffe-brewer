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
# Patch the temp file location.
lines = []
with open(os.path.join(str(Dir('caffe-framework/include/caffe/util').srcnode()),
                       'io.hpp'), 'r') as patchfile:
  for line in patchfile:
    if os.name == 'nt':
      if line.startswith(r'  *temp_filename = "') and "\\" in line:
        newline = r'   *temp_filename = "%s" + string(tmpnam(nullptr));' % (GetOption("caffe_temp").replace("\\", "\\\\")) + os.linesep
      elif line.startswith(r'  *temp_dirname = "') and "\\" in line:
        newline = r'   *temp_dirname = "%s" + string(tmpnam(nullptr));' % (GetOption("caffe_temp").replace("\\", "\\\\"))  + os.linesep
      else:
        newline = line
      lines.append(newline)
    else:
      if line.startswith(r'  *temp_filename = "') and "/" in line:
        newline = r'  *temp_filename = "%s/caffe_test.XXXXXX";' % (GetOption("caffe_temp").replace("\\", "\\\\")) + os.linesep
      elif line.startswith(r'  *temp_dirname = "') and "/" in line:
        newline = r'  *temp_dirname = "%s/caffe_test.XXXXXX";' % (GetOption("caffe_temp").replace("\\", "\\\\"))  + os.linesep
      else:
        newline = line
      lines.append(newline)
with open(os.path.join(str(Dir('caffe-framework/include/caffe/util').srcnode()),
                       'io.hpp'), 'w') as patchfile:
  patchfile.writelines(lines)

shared_objects = []
for cfile in file_list:
    shared_objects.append(core_lib_env.SharedObject(cfile))

# Install.
installed_headers = []
for header in Flatten(headers):
    relative = os.path.relpath(header.abspath, Dir('caffe-framework/include').abspath)
    installed_headers.append(env.InstallAs(os.path.join(str(Dir('include').srcnode()),
                                                        relative), header))
installed_objects = []
for obj in shared_objects:
    installed_objects.append(env.InstallAs(os.path.join(str(Dir('objects').srcnode()),
                                                        os.path.basename(str(obj[0]))), obj))

# The library.
Return("installed_objects", "installed_headers")
