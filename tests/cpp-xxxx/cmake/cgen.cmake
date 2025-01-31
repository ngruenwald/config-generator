function(get_dir dir)
  set(path "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/..")
  cmake_path(ABSOLUTE_PATH path NORMALIZE)
  set(${dir} "${path}" PARENT_SCOPE)
endfunction()

function(cgen target template inputfile outputdir workdir)
  find_package(Python3 COMPONENTS Interpreter REQUIRED QUIET)

  message(STATUS "running cgen for ${target}")

  add_custom_target(
    ${target}
    ALL
    COMMAND "${Python3_EXECUTABLE}" -m src.cgen --template "${template}" --output "${outputdir}" "${inputfile}"
    DEPENDS "${inputfile}"
    BYPRODUCTS "${outputdir}/config.cpp" "${outputdir}/config.hpp"  # enums.hpp, from_string.hpp
    WORKING_DIRECTORY "${workdir}"
    COMMENT "Generating '${template}' ..."
    SOURCES "${inputfile}"
  )
endfunction()

function(main target dep_cgen dep_library examplefile code_dir)
  get_dir(base_dir)
  add_executable(${target} "${base_dir}/main.cpp" "${code_dir}/config.cpp")
  target_link_libraries(${target} ${dep_library})
  target_include_directories(${target} PRIVATE "${code_dir}")
  add_dependencies(${target} ${dep_cgen})
  add_test(NAME ${target} COMMAND ${target} "${examplefile}")
endfunction()

function(magic)
  set(oneValueArgs TEMPLATE DEPENDENCY TESTFILE)
  cmake_parse_arguments(ARG "" "${oneValueArgs}" "" ${ARGN})

  get_dir(base_dir)
  set(data_dir "${base_dir}/data")
  set(code_dir "${CMAKE_CURRENT_BINARY_DIR}/cgen-${ARG_TEMPLATE}")
  set(work_dir "${base_dir}/../..")

  cgen(codegen-${ARG_TEMPLATE} "${ARG_TEMPLATE}" "${data_dir}/definition.yml" "${code_dir}" "${work_dir}")
  main(${ARG_TEMPLATE} codegen-${ARG_TEMPLATE} "${ARG_DEPENDENCY}" "${data_dir}/${ARG_TESTFILE}" "${code_dir}")
endfunction()
