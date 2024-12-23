# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Common Changelog][CC].
Starting with version 1.0.0 this project will adhere to [Semantic Versioning][SV].


## [0.4.0] - xxxx-xx-xx

### Changed

- **Breaking:** Property _required_ on elements replaced by _use_

### Added

- **Breaking:** Validation of input files (can be disabled via command line)
- **Breaking:** Un-/Wrapped XML arrays (defaults to unwrapped)
- Properties as XML attributes or elements (defaults to attributes)
- SVG template
- LibXml2 templatew

### Fixed


## [0.3.5] - 2024-12-03

### Changed

- Better error messages

### Fixed

- Support for different number bases


## [0.3.4] - 2024-12-02

### Fixed

- Missing typename for enum default values


## [0.3.3] - 2024-11-29

### Added

- XSD option to disable generation of documentation elements.
  Defaults to _false_.


## [0.3.2] - 2024-11-28

### Changed

- Easier templating by using the Jinja2 _ChainableUndefined_ mode

### Added

- Explicit validation function

### Fixed

- Missing defaults in cpp-xmlwrp header
- XSD boolean format and array min/max


## [0.3.1] - 2024-11-27

### Fixed

- Re-added lost YAML features (array and dict support, default values for arrays)


## [0.3.0] - 2024-11-27

### Changed

- **Breaking:** Common base template for all C++ generators
- Redundant typenames are reduced to single name per type
  - int, integer, number -> int
  - uint, unsigned -> uint
  - bool, boolean -> bool
  - array, list -> array
  - dict, dictionary, map -> dict

### Added

- C++ templates can now generate print functions to output the
  loaded configuration to stream

### Fixed

- Boolean defaults


---
[«](README.md)


[CC]: https://common-changelog.org
[SV]: https://semver.org/spec/v2.0.0.html
