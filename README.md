# caffe-platform-build
A platform independent build environment for the caffe framework.

In case you want to use the CUDA interface, get the CUDA toolkit
[here](https://developer.nvidia.com/cuda-downloads).

You can set the path to `protoc` by using the environment variable
`PROTOC`.

Ubuntu/Debian package requirements:

    sudo apt-get install scons libprotobuf-dev libgoogle-glog-dev \
      libhdf5-dev libopenblas-dev libopencv-dev libboost-all-dev


Windows package requirements:

* Boost
* google protobuf (protoc must be available on the command line)
* HDF5
* OpenBLAS
* OpenCV

__How to get these quickly:__

* Download OpenBLAS binary from [here](http://www.openblas.net/). Set the
`OPENBLAS_ROOT` environment variable. Rename `lib\openblas.dll.a` to
`lib\openblas.dll.a.lib` and add the `bin` folder to your path.

To build, you will need `cl.exe` on your path (e.g., by using the
Visual Studio command line) and the shell must have elevated
privileges. This is, because apparently the msvc linker is using
a default temp path in C:\, where the user nowadays does not
have write permissions.

### Specify GPU architectures

### Choose a temp folder
