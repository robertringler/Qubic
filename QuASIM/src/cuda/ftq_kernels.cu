
#include <cuda_runtime.h>
extern "C" __global__ void parity_check(int n,const unsigned char* bits,int* parity){
    __shared__ int s; if(threadIdx.x==0)s=0;__syncthreads();
    int i=blockIdx.x*blockDim.x+threadIdx.x;
    if(i<n){atomicXor(&s,bits[i]&1);}__syncthreads();
    if(threadIdx.x==0)parity[blockIdx.x]=s;
}
