# Config Generator

## Definition

### Elements

#### info

```yaml
info:
  version: 1.0.0
  title: my_fancy_config
  description: This is a fancy configuration.
```

The _info_ block contains model specific information,
which can be used in templates.

#### options

```yaml
options:
  output_prefix: my_fancy_
  cpp:
    namespaces:
      - my
      - fancy
      - config
    use_optional: True
```

The _options_ block contains generic options.

The generated files are named after their template files.
With the _output_prefix_ a custom prefix can be added to the generated filenames.

The _cpp_ options allow to specify custom _namespaces_ and controls the use
of std::optional for non-required fields that do not have a default value.

#### elements

```yaml
elements:
  foo:
    type: integer

  opt:
    type: string
    use: required
```

The _elements_ block contains the main elements of the configuration.
Elements can either be defined locally or they can reference types.
By default an element is optional. Use the _use_ property to mark
it as either _optional_ or _required_.

#### types

```yaml
types:
  bar:
    type: object
    properties:
      bar:
        type: integer
```

The _types_ block contains type definitions.

### References

The _$ref_ keyword can be used to reference types.

Reference format:
```
$REF = [<FILEPATH>] <ANCHOR> <REFERENCE-PATH>

ANCHOR = '#'
REFERENCE-PATH = 1..*('/' <PATH-SEGMENT>)
```

Example, reference to type in same file:
```yaml
# ./foobar.yml
types:
  foo:
    type: object
    properties:
      bar:
        $ref: '#/types/bar'
  bar:
    type: string
```
Example, reference to type in another file:
```yaml
# ./foo.yml
types:
  foo:
    type: object
    properties:
      bar:
        $ref: 'more/bar.yml#/types/bar'

# ./more/bar.yml
types:
  bar:
    type: string
```

### Data Types

#### Integers

type names:
* int
* integer
* number
* uint
* unsigned

properties:
* base      ... number base             (default: 10)
* default   ... default value           (default: none)
* min       ... min value (inclusive)   (default: none)
* max       ... max value (inclusive)   (default: none)
* enum      ... enumeration values      (default: none)

```yaml
foohex:
  type: integer
  description: foo number
  base: 16
  default: 0xaa
  min: 0x00
  max: 0xff

barfixed:
  type: integer
  enum: [0, 8, 16]
  default: 8
```

#### Strings

type names:
* string

properties:
* default   ... default value       (default: none)
* pattern   ... regex pattern       (default: none)
* enum      ... enumeration values  (default: none)
* min       ... minimum length      (default: none)
* max       ... maximum length      (default: none)

```yaml
version:
  type: string
  pattern: '(\d+)\.(\d+)'

foobar:
  type: string
  enum: [foo, bar]
```

#### Floating Point

type names:
* float
* double

properties:
* default   ... default value               (default: none)
* min       ... minimum value (inclusive)   (default: none)
* max       ... maximum value (inclusive)   (default: none)

```yaml
floaty:
  type: double
  min: 0.07
  max: 3.14
```

#### Boolean

type names:
* bool
* boolean

properties:
* default   ... default value   (default: none)

```yaml
either:
  type: boolean
  default: 'false'  # WARNING: currently this needs to be a string (quotes!)
```

#### Arrays

type names:
* array
* list

properties:
* items         ... type declaration of contained items (can contain $ref)
* default       ... default value           (default: none)
* min/minItems  ... minimum size            (default: none)
* max/maxItems  ... maximum size            (default: none)
* itemName      ... name of contained items (default: none)

Either _items_ or _$ref_ must be present.

```yaml
manythings:
  type: array
  items:
    type: integer

manymorethings:
  type: array
  items:
    $ref: '#/types/asinglething'
  minItems: 1
  maxItems: 10
```

#### Dictionaries

type names:
* dict
* dictionary
* map

properties:
* keys    ... type declaration of keys (can contain $ref)
* values  ... type declaration of values (can contain $ref)

Either _items_ or _$ref_ must be present.

```yaml
mappings:
  type: dictionary
  keys:
    type: string
  values:
    $ref: '#/types/something'
```

### Objects

type names:
* object

properties:
* properties    ... list of properties
* required      ... list of names of the required properties    (default: none)
* xml           ... xml specific options                        (default: empty dict)
  * type        ... xml compositor type (all/choice/sequence)
  * min         ... minOccurs property for choice type
  * max         ... maxOccurs property for choice type

A property can either be a type definition or a
reference (_$ref_) to another type.

```yaml
myobject:
  type: object
  properties:
    name:
      type: string
    value:
      $ref: '#/types/myobjectvalue'
  required:
    - name
```


## TODO

* [x] includes
* [x] integer enumerations
* [x] restrictions on attributes
  * [x] min/max for integer types
  * [x] min/max length for strings
  * [x] pattern for strings
  * [x] everything else should be done via types
* [ ] nested types
* [ ] proper handling of boolean defaults
* [ ] inheritance / extending objects
* [ ] cut back on (integer) types
* [ ] validation and error reporting


## Internals

### Build

This project uses hatchling for packaging - edit ```pyproject.toml``` for changes.

```shell
# (optional) check for updates / install build deps
python3 -m pip install --upgrade pip --upgrade build

# build the package - execute in project root dir where .toml file exists
python3 -m build

# (optional) install package from file
python3 -m pip install cgen-<version>.whl

# (optional) use the installed package with
python3 -m cgen some.yml
```
