# caffe-platform-build
A platform independent build environment for the caffe framework.

In case you want to use the CUDA interface, get the CUDA toolkit
[here](https://developer.nvidia.com/cuda-downloads).

Ubuntu/Debian package requirements:

    sudo apt-get install scons libprotobuf-dev libgoogle-glog-dev \
      libhdf5-dev libopenblas-dev libopencv-all-dev


Windows package requirements:

* google protobuf (protoc must be available on the command line)
* HDF5
* OpenBLAS
* OpenCV
