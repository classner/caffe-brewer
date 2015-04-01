@echo off
set BOOST_ROOT=C:\libraries\boost_1_56_0
set HDF5_ROOT=C:\libraries\HDF5\1.8.14
set OPENBLAS_ROOT=C:\libraries\OpenBLAS-v0.2.14
set OPENCV_ROOT=C:\libraries\opencv\2.4.11\build
set OPENCV_LIB_DIR=C:\libraries\opencv\2.4.11\build\x64\vc12\lib
set OPENCV_VERSION=2411
set PROTOBUF_ROOT=C:\libraries\protobuf-2.6.1
set PROTOC=C:\libraries\protobuf-2.6.1\vsprojects\x64\Release\protoc.exe

IF NOT "%CAFFE_BREWER_ADDED_PATH%"=="" goto notextending
  echo Extending path!
  set PATH=%PATH%;C:\libraries\opencv\2.4.11\build\x64\vc12\bin;C:\libraries\HDF5\1.8.14\bin;C:\libraries\OpenBLAS-v0.2.14\bin;
  set CAFFE_BREWER_ADDED_PATH=1
  goto end
:notextending
  echo Path already extended. No update.

:end
