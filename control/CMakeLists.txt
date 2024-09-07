cmake_minimum_required(VERSION 3.10)
project(control)

set(CMAKE_CXX_FLAGS "-march=native -mcpu=native -mtune=native")

# Find LCM
find_package(lcm REQUIRED)
include(${LCM_USE_FILE})

FILE(GLOB example_message_definitions "${CMAKE_CURRENT_LIST_DIR}/../types/*.lcm")

lcm_wrap_types(CPP_HEADERS cpp_headers
  ${example_message_definitions})

lcm_add_library(example_messages-cpp CPP ${cpp_headers})
target_include_directories(example_messages-cpp INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>)

# Set C++ flags for threading
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

# Use local clones instead of fetching from repositories
include(FetchContent)
FetchContent_Declare(
  moteus
  SOURCE_DIR /home/easternspork/moteus_libs/moteus
)

FetchContent_MakeAvailable(moteus)

include(FetchContent)
FetchContent_Declare(
  pi3hat
  SOURCE_DIR /home/easternspork/moteus_libs/pi3hat
)

FetchContent_MakeAvailable(pi3hat)

add_executable(lcm-client test-lcm-client.cpp)
target_link_libraries(lcm-client example_messages-cpp ${LCM_NAMESPACE}lcm)

add_executable(lcm-server test-lcm-server.cpp)
target_link_libraries(lcm-server example_messages-cpp ${LCM_NAMESPACE}lcm)

add_executable(control control.cpp)
target_link_libraries(control example_messages-cpp ${LCM_NAMESPACE}lcm)

target_link_libraries(control pi3hat::pi3hat)
target_link_libraries(control moteus::cpp)

find_package(Eigen3 REQUIRED NO_MODULE)
target_link_libraries(control Eigen3::Eigen)

add_executable(test test.cpp)
target_link_libraries(test pi3hat::pi3hat)
target_link_libraries(test moteus::cpp)
