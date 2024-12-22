cmake_minimum_required(VERSION 3.18)
project(mcnerf
        VERSION 0.1
        LANGUAGES CUDA CXX)

include(CheckLanguage)
check_language(CUDA)

# C++ 표준을 C++17로 설정
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

###############################################################################
# CUDA compiler setup
###############################################################################
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_EXTENSIONS OFF)
set(CUDA_LINK_LIBRARIES_KEYWORD PUBLIC)

add_definitions(-DHALF_PRECISION)

# tiny-cuda-nn
add_definitions(-DJSON_HAS_CPP_14)
set(TCNN_BUILD_BENCHMARK OFF)
set(TCNN_BUILD_EXAMPLES OFF)
add_subdirectory(External/tiny-cuda-nn)
include_directories(${TCNN_INCLUDE_DIRECTORIES})
include_directories(External/tiny-cuda-nn/include)
include_directories(External/tiny-cuda-nn/dependencies)

set(CMAKE_CUDA_ARCHITECTURES ${TCNN_CUDA_ARCHITECTURES})
set_property(GLOBAL PROPERTY CUDA_ARCHITECTURES ${TCNN_CUDA_ARCHITECTURES})

# zlib, for compiling cnpy
find_package(ZLIB REQUIRED)
include_directories(${ZLIB_INCLUDE_DIRS})

# Libtorch
set(CMAKE_PREFIX_PATH ${CMAKE_SOURCE_DIR}/External/libtorch/)
find_package(Torch REQUIRED PATHS ${CMAKE_SOURCE_DIR}/External/libtorch NO_DEFAULT_PATH)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
link_directories(${CMAKE_SOURCE_DIR}/External/libtorch/lib/)
include_directories(${TORCH_INCLUDE_DIRS})

# YAML
add_subdirectory(External/yaml-cpp)
include_directories(External/yaml-cpp/include)

# YAML 라이브러리 경로 설정
set(YAML_CPP_LIB_PATH "${CMAKE_SOURCE_DIR}/External/yaml-cpp/build")
link_directories(${YAML_CPP_LIB_PATH})

# eigen
include_directories(External/eigen-3.4.0)

# 소스 파일 포함
include(src/Field/field.cmake)
include(src/Dataset/dataset.cmake)
include(src/PtsSampler/pts_sampler.cmake)
include(src/Renderer/renderer.cmake)
include(src/Shader/shader.cmake)
include(src/Utils/utils.cmake)

list(APPEND SRC_ALL
        ${SRC_FIELD}
        ${SRC_DATASET}
        ${SRC_GEOMETRY}
        ${SRC_PTS_SAMPLER}
        ${SRC_RENDERER}
        ${SRC_SHADER}
        ${SRC_UTILS})

list(APPEND SRC_ALL src/ExpRunner.cpp)

# 라이브러리 설정
set(ALL_LIBS ${TORCH_LIBRARIES} ${TORCH_CUDA_LIBRARIES} ${ZLIB_LIBRARIES} tiny-cuda-nn stdc++fs)

# 디버그 모드와 릴리스 모드에서 각각 yaml-cpp 라이브러리를 설정
if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    list(APPEND ALL_LIBS ${YAML_CPP_LIB_PATH}/libyaml-cppd.a)
else()
    list(APPEND ALL_LIBS ${YAML_CPP_LIB_PATH}/libyaml-cpp.a)
endif()

# ------------------------------------ Add executables ---------------------------------------
add_executable(main main.cpp ${SRC_ALL})
target_link_libraries(main ${ALL_LIBS})
target_compile_features(main PUBLIC cxx_std_17)  # 명시적으로 C++17 설정
set_property(TARGET main PROPERTY CXX_STANDARD 17)
set_property(TARGET main PROPERTY CUDA_ARCHITECTURES ${TCNN_CUDA_ARCHITECTURES})

# 경고 억제 플래그 추가
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -diag-suppress=611")

# 추가: NVCC 컴파일러에 C++17 설정 추가
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} --std=c++17")

# Install scripts
configure_file(scripts/run.py ${CMAKE_BINARY_DIR}/run.py COPYONLY)
