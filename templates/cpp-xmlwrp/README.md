# README

This template creates code for reading XML configuration files.

Extends [cpp-common-base](../cpp-common-base/README.md)

NOTE: The default value for _options.cpp.use_validate_ is _True_.

## Supported Options

| Key                           | Type | Default | Description                                                        |
|-------------------------------|------|---------|--------------------------------------------------------------------|
| options.cpp.xmlwrp_camel_case | bool | True    | Use camelCase libxmlwrp API instead of legacy PascalCase.          |

## Dependencies

* libxmlwrp
* embedded_resources.h  (when using validation)
