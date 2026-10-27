cmake_minimum_required(VERSION 3.28)
project(masqrayd-soundboard VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Match the official OBS plugin template dependencies during Windows CI.
include("${CMAKE_CURRENT_SOURCE_DIR}/cmake/common/bootstrap.cmake" NO_POLICY_SCOPE)
set(ENABLE_FRONTEND_API ON CACHE BOOL "OBS frontend required" FORCE)
set(ENABLE_QT ON CACHE BOOL "Qt required" FORCE)
include(compilerconfig)
include(defaults)
include(helpers)

find_package(libobs REQUIRED)
find_package(obs-frontend-api REQUIRED)
find_package(Qt6 REQUIRED COMPONENTS Core Widgets Multimedia)
add_library(masqrayd-soundboard MODULE src/plugin-main.cpp)
target_link_libraries(masqrayd-soundboard PRIVATE OBS::libobs OBS::obs-frontend-api Qt6::Core Qt6::Widgets Qt6::Multimedia)
set_target_properties_plugin(masqrayd-soundboard PROPERTIES OUTPUT_NAME "masqrayd-soundboard")
