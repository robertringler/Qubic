cmake_minimum_required(VERSION 3.14)
project(QuASIMClient VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Options
option(QUASIM_BUILD_TESTS "Build tests" OFF)
option(QUASIM_BUILD_EXAMPLES "Build examples" OFF)

# Find dependencies
find_package(Threads REQUIRED)

# Optional gRPC support
find_package(gRPC CONFIG)
if(gRPC_FOUND)
    message(STATUS "gRPC found - enabling gRPC support")
    set(QUASIM_HAS_GRPC ON)
else()
    message(STATUS "gRPC not found - gRPC support disabled")
    set(QUASIM_HAS_GRPC OFF)
endif()

# QuASIM client library
add_library(quasim_client INTERFACE)
target_include_directories(quasim_client INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(quasim_client INTERFACE Threads::Threads)

if(QUASIM_HAS_GRPC)
    target_link_libraries(quasim_client INTERFACE gRPC::grpc++)
    target_compile_definitions(quasim_client INTERFACE QUASIM_HAS_GRPC)
endif()

# Install rules
install(TARGETS quasim_client
    EXPORT QuASIMClientTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(FILES quasim_client.hpp
    DESTINATION include/quasim
)

# CMake package configuration
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/QuASIMClientConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(EXPORT QuASIMClientTargets
    FILE QuASIMClientTargets.cmake
    NAMESPACE QuASIM::
    DESTINATION lib/cmake/QuASIMClient
)

configure_file(QuASIMClientConfig.cmake.in
    "${CMAKE_CURRENT_BINARY_DIR}/QuASIMClientConfig.cmake"
    @ONLY
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/QuASIMClientConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/QuASIMClientConfigVersion.cmake"
    DESTINATION lib/cmake/QuASIMClient
)

# Examples
if(QUASIM_BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Tests
if(QUASIM_BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
