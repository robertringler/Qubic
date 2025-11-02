
#include <cuda_runtime.h>
extern "C" __global__ void saxpy_kernel(int n,const float a,const float* x,float* y){
    int i=blockIdx.x*blockDim.x+threadIdx.x;
    if(i<n){y[i]=a*x[i]+y[i];}
}
