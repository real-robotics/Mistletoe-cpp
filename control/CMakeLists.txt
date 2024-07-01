cmake_minimum_required(VERSION 3.10)
project(control)

# Find LCM
find_package(lcm REQUIRED)
include(${LCM_USE_FILE})

FILE(GLOB example_message_definitions "${CMAKE_CURRENT_LIST_DIR}/../types/*.lcm")

lcm_wrap_types(CPP_HEADERS cpp_headers
  ${example_message_definitions})

lcm_add_library(example_messages-cpp CPP ${cpp_headers})
target_include_directories(example_messages-cpp INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>)

# Include moteus
# include_directories(thirdparty/moteus/lib/cpp/mjbots/moteus)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

include(FetchContent)
FetchContent_Declare(
  moteus
  GIT_REPOSITORY https://github.com/mjbots/moteus.git
  # This git hash can (and likely should) be overriden by the higher
  # level project.
  GIT_TAG        25c847a7b7b739aa00d4f9a1a30fb041f2ce7a7b
)

FetchContent_MakeAvailable(moteus)

include(FetchContent)
FetchContent_Declare(
  pi3hat
  GIT_REPOSITORY https://github.com/mjbots/pi3hat.git
  GIT_TAG        c8b9e13
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

target_link_libraries(control utils.hpp)
