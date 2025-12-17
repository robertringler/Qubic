cmake_minimum_required(VERSION 3.16)
project(QuASIM LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Check for CUDA support (optional for CPU fallback)
include(CheckLanguage)
check_language(CUDA)
if(CMAKE_CUDA_COMPILER)
    enable_language(CUDA)
    set(CMAKE_CUDA_STANDARD 17)
    set(QUASIM_HAS_CUDA ON)
    message(STATUS "CUDA support enabled")
else()
    set(QUASIM_HAS_CUDA OFF)
    message(STATUS "CUDA not found - building CPU-only version")
endif()

# QuASIM core library
add_library(quasim_core src/quasim_tensor_solve.cpp)
target_include_directories(quasim_core PUBLIC include)

# QuASIM demo executable
add_executable(quasim_demo demo.cpp)
target_link_libraries(quasim_demo PRIVATE quasim_core)

# Optional: CUDA kernels if available
if(QUASIM_HAS_CUDA)
    # CUDA kernels would be compiled here
    message(STATUS "CUDA kernels available in src/cuda/")
endif()
