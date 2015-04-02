@echo off
echo Ensure that you adjusted "setup_paths.bat"!
echo You can speed up the build process by editing
echo "full_compile.bat" and increasing the --jobs=1
echo value.

echo Setting up paths...
call setup_paths

echo Compiling...
REM Add --with-python to build the python interface.
scons --with-tests --with-tools --jobs=1
