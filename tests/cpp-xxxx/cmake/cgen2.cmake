include(embedded_resources)

find_package(Python3 COMPONENTS Interpreter REQUIRED QUIET)


function(create_xsd_resource_for_target target definition)
  # get_target_property(target_dir ${target} BINARY_DIR)
  set(target_dir ${CMAKE_BINARY_DIR}/cgen-${target}/xsd)
  set(work_dir ${CMAKE_SOURCE_DIR}/../..)
  set(res_script ${CMAKE_SOURCE_DIR}/cmake/embedded_resources.cmake)

  #
  # generate schema from definition
  #

  add_custom_command(
    OUTPUT
      config.xsd
    COMMAND
      ${Python3_EXECUTABLE}
      -m cgen
      --template "xsd"
      --output="${target_dir}"
      "${definition}"
    WORKING_DIRECTORY
      "${work_dir}"
    COMMENT
      "Generating schema file"
    DEPENDS
      "${definition}"
  )

  add_custom_target(
    ${target}-xsd-res-gen
    DEPENDS config.xsd
  )

  #
  # create embedded resource code from schema
  #

  add_custom_command(
    OUTPUT
      embedded_resources.h
    COMMAND
      "${CMAKE_COMMAND}"
      -D EXEC=generate_resources_header
      -D RESOURCES="${target_dir}/config.xsd"
      -D PATH="${target_dir}/embedded_resources.h"
      -P "${res_script}"
    COMMENT
      "Generating resource header"
  )

  add_custom_command(
    OUTPUT
      config.xsd.cpp
    COMMAND
      "${CMAKE_COMMAND}"
      -D EXEC=generate_resource_file
      -D INFILE="${target_dir}/config.xsd"
      -D OUTFILE="${target_dir}/config.xsd.cpp"
      -P "${res_script}"
    COMMENT
      "Generating resource source"
  )

  add_custom_target(
    ${target}-xsd-code-gen
    DEPENDS config.xsd.cpp embedded_resources.h
  )

  add_dependencies(
    ${target}-xsd-code-gen
    ${target}-xsd-res-gen
  )

  #
  # set dependencies
  #

  add_dependencies(
    ${target}
    ${target}-xsd-code-gen
    ${target}-xsd-res-gen
  )

  target_include_directories(
    ${target}
    PRIVATE
    ${target_dir}
  )

  #
  # dummy files for the target, the real ones are generated during build
  #

  file(
    MAKE_DIRECTORY
    ${target_dir}
  )

  file(
    TOUCH
    ${target_dir}/config.xsd.cpp
    ${target_dir}/embedded_resources.h
  )

  #
  # add generated files to target
  #

  target_sources(
    ${target}
    PRIVATE
    ${target_dir}/config.xsd.cpp
    ${target_dir}/embedded_resources.h
  )

endfunction()

# target_sources(
#   "${TEMPLATE_NAME}"
#   PRIVATE
#   "${CMAKE_BINARY_DIR}/cgen-${TEMPLATE_NAME}/config.xsd.cpp"
#   "${CMAKE_BINARY_DIR}/cgen-${TEMPLATE_NAME}/embedded_resources.h"
# )
