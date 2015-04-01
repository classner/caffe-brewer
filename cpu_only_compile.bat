@echo off
echo Ensure that you adjusted "setup_paths.bat"!
echo You can speed up the build process by editing
echo "cpu_only_compile.bat" and increasing the --jobs=1
echo value.

echo Setting up paths...
call setup_paths

echo Compiling...
scons --with-tests --with-tools --cpu-only --jobs=1
