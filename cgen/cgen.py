import argparse
import glob
import logging
import os
import shutil
import yaml

from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, TemplateError
from pathlib import Path
from typing import List, Dict, Optional

from .doc import create_render_data
from .jinja_filters import j2_base, j2_camel_case, j2_pascal_case, j2_snake_case, j2_title_case, j2_is_type
from .spec_types import ArrayType, DictionaryType, ObjectType, ObjectField, Type
from .spec_types import Constraint
from .spec_types import load_type, load_constraints


#
#
#


class Loader:
    def __init__(self):
        self.data = dict()
        self.search_paths = []

    def load(self, path):
        self._load_yaml(path)

    def _load_yaml(self, filepath):
        paths = [filepath]
        [paths.append(os.path.join(sp, filepath)) for sp in self.search_paths]
        for path in paths:
            try:
                with open(path, 'r') as stream:
                    data = yaml.safe_load(stream)
            except FileNotFoundError:
                continue
            self._load_references(data)
            Loader.merge(data, self.data)
            return
        raise FileNotFoundError(filepath)

    def _load_references(self, data):
        for key, value in data.items():
            if key == '$ref':
                file, path = value.split('#', 1)
                if not file == '':
                    self._load_yaml(file)
                    data[key] = f'#{path}'
            if isinstance(value, dict):
                self._load_references(value)

    @staticmethod
    def merge(source, destination):
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


def sort_type(types: List[Type], current: Type) -> List[Type]:
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
        if t.name == current.name:
            types.remove(t)
            sorted_.append(current)
    return sorted_


# def sort_type2(current: Type, types: List[Type]) -> List[Type]:
#     sorted = []
#     if isinstance(current, ArrayType):
#         sorted.extend(sort_type2(current.item_type, types))
#     elif isinstance(current, ObjectType):
#         for field in current.fields:
#             sorted.extend(sort_type2(field.type, types))
#     sorted.append(current)
#     return sorted


def sort_types(types: List[Type]) -> List[Type]:
    unsorted = types[:]
    sorted_ = []
    while len(unsorted) > 0:
        sorted_.extend(sort_type(unsorted, unsorted[0]))
    return sorted_


def load_types(types_dict: Dict, elem: str) -> List[Type]:
    types = []
    for key, value in types_dict[elem].items():
        t = load_type(types_dict, key, value)
        if t:
            types.append(t)
    return types


def assign_constraints(types: List[Type], elements: List[Type], constraints: List[Constraint]):
    def find_elem(data: List[Type], path: str) -> Optional[Type]:
        name = path.split('/')[-1]
        for x in data:
            if x.name == name or x.alias == name:
                return x
        return None

    def find_type(data: List[Type], path: str) -> Optional[Type]:
        name = path.split('/')[-1]
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
            print(f'constraint scope "{cst.scope}" not found')
            continue
        # find path in data ... TODO
        # assign to scope object
        elem.constraints.append(cst)


#
#
#


TEMPLATE_DEFAULT_CONFIG = {
    'template': {
        'publish': []
    }
}


def load_template_config(path: str):
    try:
        with open(Path(path) / 'template.yml', 'r') as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        return TEMPLATE_DEFAULT_CONFIG


#
#
#


def create_path(path: str):
    os.makedirs(path, exist_ok = True)


def render(env: Environment, template_file: str, output_path: str, data):
    template = env.get_template(template_file + '.j2')
    try:
        output = template.render(data)
    except TemplateSyntaxError as e:
        logging.error(f'Template syntax error ({e.filename}, {e.lineno}): {e.message}')
        raise
    except TemplateError as e:
        logging.error(f'Template error: {e.message}')
        raise

    try:
        prefix = data['options']['output_prefix']
    except KeyError:
        prefix = ''

    output_file = os.path.join(output_path, prefix + os.path.basename(template_file))

    with open(output_file, 'w') as stream:
        stream.write(output)


#
#
#


def config_generator(definition: str, template_path: str, output_path: str, input_path: str) -> int:
    try:
        logging.info(f'processing template "{template_path}"')

        template_path = find_template_path(template_path)
        if not template_path:
            raise FileNotFoundError('template path not found')

        loader = Loader()
        loader.search_paths = ["definition", input_path]  # TODO: config
        loader.load(definition)

        types = load_types(loader.data, 'types')
        types = sort_types(types)
        elements = load_types(loader.data, 'elements')

        constraints = load_constraints(loader.data)
        assign_constraints(types, elements, constraints)

        template_config = load_template_config(template_path)

        render_data = dict()

        try:
            render_data['info'] = loader.data['info']
        except KeyError:
            render_data['info'] = dict()
        try:
            render_data['options'] = loader.data['options']
        except KeyError:
            render_data['options'] = dict()

        render_data['definition'] = definition
        render_data['types'] = types
        render_data['elements'] = elements

        render_data['config'] = ObjectType(
            name='config',
            type_='object',
            description='Configuration',
            fields=[ObjectField(e.alias, e, e.description, e.required if hasattr(e, 'required') else False) for e in
                    elements]
        )

        type_names = set([t.name for t in types])
        elem_names = set([e.name for e in elements])

        render_data['unique_elements'] = list(elem_names.difference(type_names))
        render_data['unique_types'] = list(type_names.union(elem_names))

        render_data['docs'] = create_render_data(render_data['config'].doc('config'))

        template_paths = [template_path]
        try:
            for dependency in template_config.get('template', {}).get('depends', []):
                source = dependency.get('source', '')
                if source:
                    source_path = Path(source)
                    if source_path.is_absolute():
                        template_paths.append(source_path)
                    else:
                        template_paths.append(Path(template_path) / source_path)
        except Exception:
            pass

        file_loader = FileSystemLoader(template_paths)  # [template_path, Path(template_path).parent])
        env = Environment(loader=file_loader)

        env.filters['camel_case'] = j2_camel_case
        env.filters['pascal_case'] = j2_pascal_case
        env.filters['snake_case'] = j2_snake_case
        env.filters['title_case'] = j2_title_case
        env.filters['base'] = j2_base
        env.tests['Type'] = j2_is_type

        create_path(output_path)

        for file_path in glob.glob(os.path.join(os.getcwd(), template_path, '*.j2')):
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            if not file_name.startswith('_'):
                render(env, file_name, output_path, render_data)

        for publish_path in template_config['template']['publish']:
            if isinstance(publish_path, str):
                source_path = Path(template_path) / Path(publish_path)
                target_path = Path(output_path) / Path(publish_path)
            else:
                source_path = Path(template_path) / Path(publish_path['from'])
                target_path = Path(output_path) / Path(publish_path['to'])
            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, target_path)

        return 0

    except TemplateSyntaxError as e:
        logging.error(f'Template syntax error at {e.filename}:{e.lineno}:\n{e}')
    except Exception as e:
        logging.error(f'Error: {e}')
    return 1


def find_template_path(path: str):
    if os.path.isabs(path):
        return path
    base_paths = [
        Path.cwd(),
        Path.cwd() / 'templates',
        Path.home() / '.config/cgen/templates',
        Path(__file__).parent.absolute() / 'templates'
    ]
    for bp in base_paths:
        tp = bp / path
        if os.path.isdir(tp):
            return tp
    return None


def cgen() -> int:
    parser = argparse.ArgumentParser(description='Config generator')
    parser.add_argument('definition', type=str, help='.yml definition file')
    parser.add_argument('--template', type=str, nargs='+', help='template path - default: xsd, cpp-xmlwrp',
                        default=['xsd', 'cpp-xmlwrp'])
    parser.add_argument('--output', type=str, default='out', help='output path - default: out')
    parser.add_argument('--input', type=str, default='', help='input path')
    args = parser.parse_args()
    rv = [config_generator(args.definition, t, args.output, args.input) for t in args.template]
    return max(rv) if rv else 1
