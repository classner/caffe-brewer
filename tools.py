# -*- python -*-
# Author: Christoph Lassner.
import os
Import(["core_objects", "link_libs", "env"])

# Create a temporary environment to be able to modify it locally.
tools_env = env.Clone()

file_list = Glob('caffe-framework/tools/*.cpp')

tools_env.PrependUnique(LIBS=link_libs)

tool_executables = []
for tfile in file_list:
    tool_object = tools_env.SharedObject(tfile)
    tool_executable = tools_env.Program(target=os.path.splitext(str(tfile))[0],
                                        source=core_objects+[tool_object])
    tool_executables.append(tools_env.Install(Dir('./bin').srcnode(), tool_executable))

Return("tool_executables")
