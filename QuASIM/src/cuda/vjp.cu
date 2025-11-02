
#include <cuda_runtime.h>
extern "C" __global__ void vjp_accum(int n,const float* cot,float* grad){
    int i=blockIdx.x*blockDim.x+threadIdx.x;
    if(i<n){atomicAdd(&grad[0],cot[i]);}
}
