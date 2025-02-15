cmake_minimum_required(VERSION 3.20)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)

project(test LANGUAGES CXX)

set(CMAKE_CTEST_ARGUMENTS "--output-on-failure")
enable_testing()

if(NOT DEFINED TEMPLATE)
  set(TEMPLATE "all")
endif()

message(STATUS "TEMPLATE: ${TEMPLATE}")

include(FetchContent)
include(cgen)
include(sanitizers)

add_sanitizer_support(address leak)

if("${TEMPLATE}" STREQUAL "all")
  set(USE_JSON ON)
  set(USE_PUGIXML ON)
  set(USE_TOML11 ON)
  set(USE_XMLWRP OFF)
  set(USE_YAML ON)
  set(USE_LIBXML2 ON)
elseif("${TEMPLATE}" STREQUAL "cpp-json")
  set(USE_JSON ON)
elseif("${TEMPLATE}" STREQUAL "cpp-pugixml")
  set(USE_PUGIXML ON)
elseif("${TEMPLATE}" STREQUAL "cpp-toml11")
  set(USE_TOML11 ON)
elseif("${TEMPLATE}" STREQUAL "cpp-xmlwrp")
  set(USE_XMLWRP ON)
elseif("${TEMPLATE}" STREQUAL "cpp-yaml")
  set(USE_YAML ON)
elseif("${TEMPLATE}" STREQUAL "cpp-libxml2")
  set(USE_LIBXML2 ON)
else()
  message(FATAL_ERROR "unsupported template: ${TEMPLATE}")
endif()


if(USE_JSON)
  set(JSON_BuildTests OFF)
  set(JSON_MultipleHeaders OFF)
  FetchContent_Declare(json GIT_REPOSITORY https://github.com/nlohmann/json.git GIT_TAG v3.11.2)
  FetchContent_MakeAvailable(json)
  magic(TEMPLATE cpp-json DEPENDENCY nlohmann_json::nlohmann_json TESTFILE example.json)
endif()

if(USE_PUGIXML)
  FetchContent_Declare(pugixml GIT_REPOSITORY https://github.com/zeux/pugixml.git GIT_TAG v1.14)
  FetchContent_MakeAvailable(pugixml)
  magic(TEMPLATE cpp-pugixml DEPENDENCY pugixml::static TESTFILE example.xml)
endif()

if(USE_TOML11)
  FetchContent_Declare(toml11 GIT_REPOSITORY https://github.com/ToruNiina/toml11 GIT_TAG v4.1.0)
  FetchContent_MakeAvailable(toml11)
  magic(TEMPLATE cpp-toml11 DEPENDENCY toml11::toml11 TESTFILE example.toml)
endif()

if(USE_XMLWRP)
#  find_package(xmlwrp 3.4 QUIET)
  find_package(LibXml2 QUIET REQUIRED)
  add_library(xmlwrp STATIC IMPORTED)
  add_library(xmlwrp::xmlwrp ALIAS xmlwrp)
  set_target_properties(xmlwrp PROPERTIES INTERFACE_INCLUDE_DIRECTORIES /opt/eurofunk/include/xmlwrp/3.6.1)
  set_target_properties(xmlwrp PROPERTIES IMPORTED_LOCATION /opt/eurofunk/lib64/libxmlwrp-3.6.1.a)
  set_target_properties(xmlwrp PROPERTIES INTERFACE_LINK_LIBRARIES LibXml2::LibXml2)
  set(xmlwrp_FOUND TRUE)

  if(xmlwrp_FOUND)
    magic(TEMPLATE cpp-xmlwrp DEPENDENCY xmlwrp::xmlwrp TESTFILE example.xml)

    #
    # xml schema magic
    #

    include(cgen2)
    create_xsd_resource_for_target(cpp-xmlwrp ${CMAKE_SOURCE_DIR}/data/definition.yml)
  else()
    message(WARNING "xmlwrp not found - skipping test")
  endif()
endif()

if(USE_YAML)
  set(YAML_BUILD_SHARED_LIBS OFF)
  set(YAML_CPP_BUILD_TESTS OFF)
  FetchContent_Declare(yaml_cpp GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git GIT_TAG 0.8.0)
  FetchContent_MakeAvailable(yaml_cpp)
  magic(TEMPLATE cpp-yaml DEPENDENCY yaml-cpp::yaml-cpp TESTFILE example.yml)
endif()

if(USE_LIBXML2)
  find_package(LibXml2 QUIET REQUIRED)
  magic(TEMPLATE cpp-libxml2 DEPENDENCY LibXml2::LibXml2 TESTFILE example.xml)
  include(cgen2)
  create_xsd_resource_for_target(cpp-libxml2 ${CMAKE_SOURCE_DIR}/data/definition.yml)
endif()
