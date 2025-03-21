import argparse
import glob
import logging
import os
import shutil
import sys
import yaml

from copy import deepcopy
from jinja2 import (
    Environment,
    FileSystemLoader,
    TemplateSyntaxError,
    TemplateError,
    ChainableUndefined,
)
from jsonschema import validate
from pathlib import Path

from .doc import create_render_data
from .jinja_filters import (
    j2_base,
    j2_camel_case,
    j2_debug_print,
    j2_pascal_case,
    j2_snake_case,
    j2_str_to_dict,
    j2_title_case,
    j2_is_type,
)
from .spec_types import (
    ArrayType,
    DictionaryType,
    EnumType,
    ObjectType,
    ObjectField,
    Type,
    is_equal_type
)
from .spec_types import Constraint
from .spec_types import load_type, load_constraints


from .__version__ import __version__

#
#
#


class Loader:
    def __init__(self):
        self.data = dict()
        self.search_paths = []

    def load(self, path: str, schema_path: str | None = None):
        self._load_yaml(path)
        if schema_path:
            self._validate(schema_path)

    def _load_yaml(self, filepath: str):
        paths = [filepath]
        [paths.append(os.path.join(sp, filepath)) for sp in self.search_paths]
        for path in paths:
            try:
                with open(path, "r") as stream:
                    data = yaml.safe_load(stream)
            except FileNotFoundError:
                continue
            self._load_references(data)
            Loader.merge(data, self.data)
            return
        raise FileNotFoundError(filepath)

    def _load_references(self, data: dict):
        for key, value in data.items():
            if key == "$ref":
                file, path = value.split("#", 1)
                if not file == "":
                    self._load_yaml(file)
                    data[key] = f"#{path}"
            if isinstance(value, dict):
                self._load_references(value)

    def _validate(self, schema_path: str):
        with open(schema_path, "r") as stream:
            schema = yaml.safe_load(stream)
            validate(self.data, schema)

    @staticmethod
    def merge(source: dict, destination: dict):
        for key, value in source.items():
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                Loader.merge(value, node)
            else:
                destination[key] = value
        return destination


#
#
#


def create_name_with_counter(
    name: str,
    types: list[Type],
    counter: int = 0,
) -> str:
    while True:
        cname: str = f"{name}-{counter}"
        if not any(x.name == cname for x in types):
            return cname
        counter += 1


def create_name_with_opt_counter(
    name: str,
    types: list[Type],
) -> str:
    if not any(x.name == name for x in types):
        return name
    return create_name_with_counter(name, types, counter=1)


def create_name(
    outer_name: list[str],
    types: list[Type],
    suffix: str | None = None,
) -> str:
    full_name: bool = False
    append_suffix: bool = False
    if full_name:
        name: str = "-".join(outer_name)
    else:
        name = outer_name[-1]
    if append_suffix and suffix:
        name = name + suffix
    return create_name_with_opt_counter(name, types)


def create_name2(
    type: Type,
    types: list[Type],
    merge_collection_types: bool,
) -> str:
    if isinstance(type, ArrayType):
        at: ArrayType = type
        iname: str = (
            at.item_type.name
            if isinstance(at.item_type, ObjectType)
            else at.item_type.type
        )
        name: str = f"{iname}_array"
        if merge_collection_types:
            return name
        return create_name_with_opt_counter(name, types)
    if isinstance(type, DictionaryType):
        dt: DictionaryType = type
        kname: str = (
            dt.key_type.name
            if isinstance(dt.key_type, ObjectType)
            else dt.key_type.type
        )
        vname: str = (
            dt.value_type.name
            if isinstance(dt.value_type, ObjectType)
            else dt.value_type.type
        )
        name: str = f"{kname}_{vname}_dict"
        if merge_collection_types:
            return name
        return create_name_with_opt_counter(name, types)
    return create_name([type.name], types, get_type_suffix(type))


def clone_type(type: Type, type_name: str) -> Type:
    clone = deepcopy(type)
    clone.name = type_name
    clone.alias = type_name
    clone.is_nested = True
    return clone


def create_nested_type(
    outer_name: list[str],
    type: Type,
    types: list[Type],
    suffix: str,
) -> None:
    if any(is_equal_type(type, x) for x in types):
        return
    merge_collection_types: bool = False  # this might be a problem if properties differ
    type_name: str = create_name2(type, types, merge_collection_types)
    if not any(x.name == type_name for x in types):
        types.append(clone_type(type, type_name))
    type.name = type_name


def get_type_suffix(type: Type) -> str:
    if isinstance(type, ArrayType):
        return "-array"
    if isinstance(type, DictionaryType):
        return "-dict"
    if isinstance(type, EnumType):
        return "-enum"
    if isinstance(type, ObjectType):
        return "-object"
    return "-type"


def extract_nested_types_from_type(
    outer_name: list[str],
    type: Type,
    types: list[Type],
) -> None:
    if type.is_ref:
        return

    if isinstance(type, ObjectType):
        objtype: ObjectType = type
        for field in objtype.fields:
            extract_nested_types_from_type(outer_name + [field.name], field.type, types)

    create_nested_type(outer_name, type, types, get_type_suffix(type))


def extract_nested_types(types: list[Type], elements: list[Type]) -> None:
    for type in types:
        extract_nested_types_from_type([type.name], type, types)
    for type in elements:
        extract_nested_types_from_type([type.name], type, types)


def sort_type(types: list[Type], current: Type) -> list[Type]:
    sorted_ = []
    if isinstance(current, ArrayType):
        sorted_.extend(sort_type(types, current.item_type))
        # sorted.append(current)
    elif isinstance(current, DictionaryType):
        sorted_.extend(sort_type(types, current.key_type))
        sorted_.extend(sort_type(types, current.value_type))
    elif isinstance(current, ObjectType):
        for field in current.fields:
            sorted_.extend(sort_type(types, field.type))

    for t in types:
        if t.name != current.name:
            continue
        types.remove(t)
        sorted_.append(t if current.is_ref else current)  # prefer non ref types

    return sorted_


def sort_types(types: list[Type]) -> list[Type]:
    unsorted = types[:]
    sorted_ = []
    while len(unsorted) > 0:
        sorted_.extend(sort_type(unsorted, unsorted[0]))
    return sorted_


def filter_types(types: list[Type]) -> list[Type]:
    names = {}
    filtered = []
    for type in types:
        if type.name in names:
            continue
        names.update({type.name: 1})
        filtered.append(type)
    return filtered


def reorder_types(types: list[Type]) -> list[Type]:
    def reorder_type(types: list[Type], typeA: Type, typeB: Type) -> bool:
        def indexOf(types: list[Type], type: Type) -> int:
            index = -1
            for t in types:
                index += 1
                if type.name == t.name:
                    return index
            return -1

        idxA = indexOf(types, typeA)
        if idxA == -1:
            # tbd: error
            return False
        idxB = indexOf(types, typeB)
        if idxB == -1:
            # tbd: error
            return False
        if idxB <= idxA:
            # ok
            return False
        logging.debug(f"moving {typeB.name} from {idxB} to {idxA+1}")
        types.pop(idxB)
        types.insert(idxA, typeB)
        return True

    result = types[:]
    iteration = 0
    while True:
        iteration += 1
        moves = 0
        for type in types:
            # check all composite types
            if isinstance(type, ArrayType):
                if reorder_type(result, type, type.item_type):
                    moves += 1
            if isinstance(type, DictionaryType):
                if reorder_type(result, type, type.key_type):
                    moves += 1
                if reorder_type(result, type, type.value_type):
                    moves += 1
            if isinstance(type, ObjectType):
                for field in type.fields:
                    if reorder_type(result, type, field.type):
                        moves += 1
        logging.debug(f"iteration {iteration}, {moves} moves")
        if moves == 0:
            break
    return result


def load_types(types_dict: dict, elem: str) -> list[Type]:
    types = []
    for key, value in types_dict[elem].items():
        t = load_type(types_dict, key, value)
        if t:
            types.append(t)
    return types


def assign_constraints(
    types: list[Type],
    elements: list[Type],
    constraints: list[Constraint],
):
    def find_elem(data: list[Type], path: str) -> Type | None:
        name = path.split("/")[-1]
        for x in data:
            if x.name == name or x.alias == name:
                return x
        return None

    def find_type(data: list[Type], path: str) -> Type | None:
        name = path.split("/")[-1]
        for x in data:
            if not isinstance(x, ObjectType):
                continue
            for f in x.fields:
                if f.name == name:
                    return x
        return None

    for cst in constraints:
        # find scope in data
        elem = find_elem(elements, cst.scope)
        if elem is None:
            elem = find_type(types, cst.scope)
        if elem is None:
            logging.warning(f'constraint scope "{cst.scope}" not found')
            continue
        # find path in data ... TODO
        # assign to scope object
        elem.constraints.append(cst)


#
#
#


TEMPLATE_DEFAULT_CONFIG = {"template": {"publish": []}}


def load_template_config(path: str):
    try:
        with open(Path(path) / "template.yml", "r") as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        return TEMPLATE_DEFAULT_CONFIG


#
#
#


def create_path(path: str):
    os.makedirs(path, exist_ok=True)


def render(env: Environment, template_file: str, output_path: str, data):
    template = env.get_template(template_file + ".j2")
    try:
        output = template.render(data)
    except TemplateSyntaxError as e:
        logging.error(f"Template syntax error ({e.filename}, {e.lineno}): {e.message}")
        raise
    except TemplateError as e:
        logging.error(f"Template error: {e.message}")
        raise

    try:
        prefix = data["options"]["output_prefix"]
    except KeyError:
        prefix = ""

    output_file = os.path.join(output_path, prefix + os.path.basename(template_file))

    with open(output_file, "w") as stream:
        stream.write(output)


#
#
#


def config_generator(
    definition: str,
    template_path: str,
    output_path: str,
    input_path: str,
    validate_input: bool = True,
) -> int:
    try:
        logging.info(f'processing template "{template_path}"')

        full_template_path: str | None = find_template_path(template_path)
        if not full_template_path:
            raise FileNotFoundError("template path not found")
        template_path = full_template_path

        schema_path: str | None = None
        if validate_input:
            schema_path = find_schema_path("definition.schema.json")
            if not schema_path:
                raise FileNotFoundError("schema path not found")

        loader = Loader()
        loader.search_paths = ["definition", input_path]  # TODO: config
        loader.load(definition, schema_path)

        types = load_types(loader.data, "types")
        elements = load_types(loader.data, "elements")

        extract_nested_types(types, elements)

        types = sort_types(types)
        types = filter_types(types)
        types = reorder_types(types)

        constraints = load_constraints(loader.data)
        assign_constraints(types, elements, constraints)

        template_config = load_template_config(template_path)

        render_data = dict()

        try:
            render_data["info"] = loader.data["info"]
        except KeyError:
            render_data["info"] = dict()
        try:
            render_data["options"] = loader.data["options"]
        except KeyError:
            render_data["options"] = dict()

        render_data["definition"] = definition
        render_data["types"] = types
        render_data["elements"] = elements

        render_data["config"] = ObjectType(
            name="config",
            type_="object",
            description="Configuration",
            fields=[
                ObjectField(
                    e.alias,
                    e,
                    e.description,
                    getattr(e, "required", False),
                    getattr(e, "default", False),
                )
                for e in elements
            ],
        )

        type_names = set([t.name for t in types])
        elem_names = set([e.name for e in elements])

        render_data["unique_elements"] = list(elem_names.difference(type_names))
        render_data["unique_types"] = list(type_names.union(elem_names))

        render_data["docs"] = create_render_data(render_data["config"].doc("config"))

        template_paths: list[str] = [template_path]
        try:
            for dependency in template_config.get("template", {}).get("depends", []):
                source = dependency.get("source", "")
                if source:
                    source_path = Path(source)
                    if source_path.is_absolute():
                        template_paths.append(str(source_path))
                    else:
                        template_paths.append(str(Path(template_path) / source_path))
        except Exception:
            pass

        logging.debug(f"Template paths: {template_paths}")

        file_loader = FileSystemLoader(
            template_paths
        )  # [template_path, Path(template_path).parent])
        env = Environment(loader=file_loader, undefined=ChainableUndefined)

        env.filters["camel_case"] = j2_camel_case
        env.filters["pascal_case"] = j2_pascal_case
        env.filters["snake_case"] = j2_snake_case
        env.filters["title_case"] = j2_title_case
        env.filters["base"] = j2_base
        env.filters["to_dict"] = j2_str_to_dict
        env.filters["debug"] = j2_debug_print
        env.tests["Type"] = j2_is_type

        create_path(output_path)

        for file_path in glob.glob(os.path.join(os.getcwd(), template_path, "*.j2")):
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            if not file_name.startswith("_"):
                render(env, file_name, output_path, render_data)

        for publish_path in template_config["template"]["publish"]:
            if isinstance(publish_path, str):
                source_path = Path(template_path) / Path(publish_path)
                target_path = Path(output_path) / Path(publish_path)
            else:
                source_path = Path(template_path) / Path(publish_path["from"])
                target_path = Path(output_path) / Path(publish_path["to"])
            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, target_path)

        return 0

    except TemplateSyntaxError as e:
        logging.error(f"Template syntax error at {e.filename}:{e.lineno}:\n{e}")
    except Exception as e:
        logging.error(f"Error: {e}")
    return 1


def find_template_path(path: str) -> str | None:
    if os.path.isabs(path):
        return path
    base_paths = [
        Path.cwd(),
        Path.cwd() / "templates",
        Path.home() / ".config/cgen/templates",
        Path(sys.prefix) / "share/cgen/templates",
        Path(__file__).parent.parent.absolute() / "templates",
    ]
    for bp in base_paths:
        tp = bp / path
        if os.path.isdir(tp):
            return str(tp)
    return None


def find_schema_path(path: str) -> str | None:
    if os.path.isabs(path):
        return path
    base_paths = [
        Path.cwd(),
        Path.cwd() / "schema",
        Path.home() / ".config/cgen/schema",
        Path(sys.prefix) / "share/cgen/schema",
        Path(__file__).parent.parent.absolute() / "schema",
    ]
    for bp in base_paths:
        tp = bp / path
        if os.path.isfile(tp):
            return str(tp)
    return None


def cgen() -> int:
    parser = argparse.ArgumentParser(prog="cgen", description="Config generator")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("definition", type=str, help=".yml definition file")
    parser.add_argument(
        "--template",
        type=str,
        nargs="+",
        help="template path - default: xsd, cpp-xmlwrp",
        default=["xsd", "cpp-xmlwrp"],
    )
    parser.add_argument(
        "--output", type=str, default="out", help="output path - default: out"
    )
    parser.add_argument("--input", type=str, default="", help="input path")
    parser.add_argument("--no-validate", action="store_true", help="skip validation")
    args = parser.parse_args()
    rv = [
        config_generator(
            args.definition, t, args.output, args.input, not args.no_validate
        )
        for t in args.template
    ]
    return max(rv) if rv else 1
