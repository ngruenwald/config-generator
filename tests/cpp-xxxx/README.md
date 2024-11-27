# Test Project

## Build

The TEMPLATE variable specifies which variants to build,
you must specify one of the following:

* cpp-json
* cpp-pugixml
* cpp-toml11
* cpp-xmlwrp
* cpp-yaml
* all

cmake -S . -B build -D TEMPLATE=all
cmake --build build

## Execute

cmake --build build --target test

