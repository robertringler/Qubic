
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
extern "C" void saxpy_kernel(int n,const float a,const float* x,float* y);
static void saxpy(py::array_t<float> x,py::array_t<float> y,float a){
    auto bx=x.request();auto by=y.request();
    int n=(int)bx.size;const float* px=(float*)bx.ptr;float* py_=(float*)by.ptr;
    for(int i=0;i<n;++i){py_[i]=a*px[i]+py_[i];}
}
PYBIND11_MODULE(quasim_cuda,m){m.def("saxpy",&saxpy);}
