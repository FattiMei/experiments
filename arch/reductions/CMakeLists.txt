cmake_minimum_required(VERSION 3.20)
project(reductions LANGUAGES CXX)

set(CMAKE_BUILD_TYPE "Release")

add_executable(repr reduction.cpp)
target_compile_definitions(repr PUBLIC NPOINTS=1000)
target_compile_definitions(repr PUBLIC MIN_EXPONENT=10)
target_compile_definitions(repr PUBLIC MAX_EXPONENT=26)
target_compile_definitions(repr PUBLIC DISABLE_VECTORIZATION=false)
target_compile_definitions(repr PUBLIC SHUFFLE_ITERATIONS=false)

