cmake_minimum_required(VERSION 3.10)
project(test)

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
include_directories(thirdparty/moteus/lib/cpp/mjbots/moteus)

add_executable(moteus-test moteus-test.cpp)
target_link_libraries(moteus-test example_messages-cpp ${LCM_NAMESPACE}lcm)

add_executable(lcm-client test-lcm-client.cpp)
target_link_libraries(lcm-client example_messages-cpp ${LCM_NAMESPACE}lcm)

add_executable(lcm-server test-lcm-server.cpp)
target_link_libraries(lcm-server example_messages-cpp ${LCM_NAMESPACE}lcm)
