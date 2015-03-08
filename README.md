# caffe-brewer

A platform independent build environment for the caffe framework using
the SCons build system.

__The aim of this environment is to build the caffe framework on Windows
and Linux with minimal dependencies.__ The github project pulls in as many
dependencies as possible automatically. It is completely non-intrusive,
so that the most recent version of caffe can be used. It builds the
core library objects for CPU and GPU computing, as well as the tests,
the Python interface and all the tools.

It is also meant to be used to build the caffe object files in a 
fast and convenient manner to be used as a subproject for larger 
projects.

## Build instructions

In case you want to use the CUDA interface, get the CUDA toolkit
[here](https://developer.nvidia.com/cuda-downloads). In case you want to use the python interface, install the protobuf python library, e.g., by doing `pip install protobuf`.

### Ubuntu/Debian package requirements:

    sudo apt-get install scons libprotobuf-dev libgoogle-glog-dev \
      libhdf5-dev libopenblas-dev libopencv-dev libboost-all-dev

### Windows package requirements:

* Boost
* google protobuf (protoc must be available on the command line)
* HDF5
* OpenBLAS
* OpenCV

__How to get these quickly:__

* Download Boost from [here](http://www.boost.org/users/download/). Set
the `BOOST_ROOT` environment variable.

* Download google protobuf from [here](https://developers.google.com/protocol-buffers/docs/downloads).
Get the 'win32' binary version and the source as well. Set the `PROTOC`
environment variable, pointing to protoc.exe, and the `PROTOBUF_ROOT`
environment variable, pointing to the protobuf source root. Enter the 'vsprojects' directory and open the solution file. If necessary, create a new architecture 'x64' by copying the preferences from 'x86' and build the release configuration.

* Download HDF5 from [here](http://www.hdfgroup.org/HDF5/release/obtain5.html)
and set the `HDF5_ROOT` environment variable.

* Download OpenBLAS binary from [here](http://www.openblas.net/). Set the
`OPENBLAS_ROOT` environment variable. Rename `lib\openblas.dll.a` to
`lib\openblas.dll.a.lib` and add the `bin` folder to your path.

* Download OpenCV from [here](http://opencv.org/downloads.html). Set
the `OPENCV_ROOT` environment variable.

To build, you will need `cl.exe` on your path (e.g., by using the
Visual Studio command line) and the shell must have elevated
privileges. This is, because apparently the msvc linker is using
a default temp path in C:\, where the user nowadays does not
have write permissions.

### Build

Clone the repository:

`git clone https://github.com/ChrislS/caffe-brewer.git`

Pull in the submodules:

`git submodule update --init --recursive`

Now simply run the magic command `scons` to get the library objects
built into the folder `objects`, the headers to the folder `includes`,
and current versions of many dependencies to `lib`. The test executable
is built into the folder `bin` as `caffe-gtest-all`.

Additional options are `--with-python`, to build the python library
to the folder `python`, and `--with-tools`, to build the tools also
into the folder `bin`.

### Specify GPU architectures

By default, GPU code is generated for the architectures with IDs
20, 30, 35 and 50. If you want to modify this behaviour, you can do
so by specifying `--cuda-architectures` as semicolon separated list
of architectures.

### Choose a temp folder

caffe uses a specific folder to create its temporary files in. This
is hard-coded in caffe usually to be `/temp`, but since I had to make
this modular anyway to be able to build in Windows, I decided to make
it parameterizable. Use the flag `--temp-folder=C:\mytemp` to specify
your favorite location.

### Using the caffe object files

Due to the way the registration of layers is performed, it is impossible
(to my knowledge, but based on quite solid research) on Windows to
statically link against the current versions of caffe.

To go more into
detail, the registration of caffe layers is performed by instantiating
an object in global scope. Since the linking process only pulls in
_referenced_ symbols, these global objects are not pulled into the
target library. On Linux, one can work around this by using the
`-Wl,--whole-archive` flag. However, on Windows, the only option that
comes close to the desired behaviour is `/OPT:NOREF`, which, however,
does not work for me with Visual Studio 2012.

This is, why I came to the conclusion that the only portable way to 
use caffe as a 'library' is, to directly add its object files to the
compilation of the referencing project. To do so, include all object
files in the `objects` folder in the linking process of your library,
as well as linking against all libs in the `lib` folder as well as

* boost.datetime,
* boost.system,
* boost.filesystem,
* boost.thread,
* hdf5,
* openblas,
* opencv,
* cuda.

This is still quite a hassle, but there is unfortunately no other
portable way to my knowledge. If you know another good way, please
send me a pull request to have others also benefit of your findings!

## Running the tests

All enabled tests pass on Windows and Linux. Just a remark: the default database size is set to 1TB for the tests! At least on Windows, some LMDB tests do not pass if you do not have at least 1TB space available on the harddrive with the temp folder.

__Have fun brewing!__
