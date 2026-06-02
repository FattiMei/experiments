cmake_minimum_required(VERSION 3.12.0)
project(dirichlet-asymm LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED "ON")

find_package(deal.II 9.5.1 REQUIRED)
deal_ii_initialize_cached_variables()

add_executable(main main.cpp)
target_link_libraries(main)
deal_ii_setup_target(main)

