@echo off
set BOOST_ROOT=C:\libraries\boost_1_56_0
REM set BOOST_LIB_DIR=%BOOST_ROOT%\whereeveryoucompiledto
set HDF5_ROOT=C:\libraries\HDF5\1.8.14
set OPENBLAS_ROOT=C:\libraries\OpenBLAS-v0.2.14
set OPENCV_ROOT=C:\libraries\opencv\2.4.11\build
set OPENCV_LIB_DIR=%OPENCV_ROOT%\x64\vc12\lib
set OPENCV_VERSION=2411
set PROTOBUF_ROOT=C:\libraries\protobuf-2.6.1
set PROTOC=%PROTOBUF_ROOT%\vsprojects\x64\Release\protoc.exe

IF NOT "%CAFFE_BREWER_ADDED_PATH%"=="" goto notextending
  echo Extending path!
  set PATH=%PATH%;%OPENCV_ROOT%\x64\vc12\bin;%HDF5_ROOT%\bin;%OPENBLAS_ROOT%\bin;
  set CAFFE_BREWER_ADDED_PATH=1
  goto end
:notextending
  echo Path already extended. No update.

:end
