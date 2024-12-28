# README

This is the common base template for C++ config generators.

## Supported Options

| Key                      | Type      | Default    | Description                                 |
|--------------------------|-----------|------------|---------------------------------------------|
| options.output_prefix    | str       | ""         | Custom name prefix for generated code files |
| options.cpp.namespaces   | list[str] | ["config"] | Encapsulate generated code in namespace(s)  |
| options.cpp.use_optional | bool      | False      | Use std::optional for non-mandatory fields  |
| options.cpp.use_printer  | bool      | True       | Generate code to print the config values    |
| options.cpp.use_validate | bool      | False      | Create code to validate the loaded config   |
