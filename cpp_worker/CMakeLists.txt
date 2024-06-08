cmake_minimum_required(VERSION 3.10)

project(cpp_worker)
set(CMAKE_CXX_STANDARD 11)

include_directories(/SimpleAmqpClient)
include_directories(/usr/local/lib)

add_executable(cpp_worker main.cpp)

target_link_libraries(cpp_worker SimpleAmqpClient boost_system pthread jsoncpp)
