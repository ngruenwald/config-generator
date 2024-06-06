from typing import List, Dict, Optional

from .doc import DocEntry


class Type:
    def __init__(self, name: str, type_: str, description: str):
        self.name = name
        self.type = type_
        self.description = description
        self.alias = name
        self.constraints = []

    def __str__(self):
        return f'Type{{name={self.name},type={self.type},alias={self.alias},constraints={self.constraints}}}'


class IntegerType(Type):
    def __init__(self, name: str, type_: str, description: str = None,
                 base: int = None, defv: str = None,
                 minv: str = None, maxv: str = None):
        super().__init__(name, type_, description)
        self.base = base if base else 10
        self.default = defv
        self.min = minv
        self.max = maxv

    def __str__(self):
        return f'IntegerType{{default={self.default}}}'

    @staticmethod
    def create(name: str, props: Dict):
        return IntegerType(
            name=name,
            type_=props.get('type', 'int'),
            description=props.get('description', ''),
            defv=props.get('default', None),
            base=props.get('base', 10),
            minv=props.get('min', None),
            maxv=props.get('max', None)
        )


class FloatingType(Type):
    def __init__(self, name: str, type_: str, description: str = None,
                 defv: str = None, minv: str = None, maxv: str = None):
        super().__init__(name, type_, description)
        self.default = defv
        self.min = minv
        self.max = maxv

    def __str__(self):
        return f'FloatingType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(name: str, props: Dict):
        return FloatingType(
            name=name,
            type_=props.get('type', 'float'),
            description=props.get('description', ''),
            defv=props.get('default', None),
            minv=props.get('min', None),
            maxv=props.get('max', None)
        )


class BooleanType(Type):
    def __init__(self, name: str, type_: str, description: str = None,
                 defv: bool = None):
        super().__init__(name, type_, description)
        self.default = defv if defv is not None else False

    def __str__(self):
        return f'BooleanType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(name: str, props: Dict):
        return BooleanType(
            name=name,
            type_=props.get('type', 'bool'),
            description=props.get('description', ''),
            defv=props.get('default', None)
        )


class StringType(Type):
    def __init__(self, name: str, type_: str, description: str = None,
                 defv: str = None, pattern: str = None,
                 minl: int = None, maxl: int = None):
        super().__init__(name, type_, description)
        self.default = defv
        self.pattern = pattern
        self.min = minl
        self.max = maxl

    def __str__(self):
        return f'StringType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(name: str, props: Dict):
        return StringType(
            name=name,
            type_=props.get('type', 'string'),
            description=props.get('description', ''),
            defv=props.get('default', None),
            pattern=props.get('pattern', None),
            minl=props.get('min', None),
            maxl=props.get('max', None)
        )


class EnumType(Type):
    def __init__(self, name: str, type_: str, base_type: str, enum: List[str],
                 description: str = None, defv: str = None):
        super().__init__(name, type_, description)
        self.base_type = base_type
        self.enum = enum
        self.default = defv

    def __str__(self):
        return f'EnumType{{name={self.name},type={self.type},base_type={self.base_type},alias={self.alias}}}'

    @staticmethod
    def create(name: str, props: Dict):
        return EnumType(
            name=name,
            type_='enum',
            base_type=props.get('type', 'string'),
            enum=props.get('enum', None),
            description=props.get('description', ''),
            defv=props.get('default', None)
        )


class ArrayType(Type):
    def __init__(self, name: str, type_: str, item_type: Type,
                 item_name: str, description: str = None,
                 defv: List[str] = None,
                 mins: int = None, maxs: int = None):
        super().__init__(name, type_, description)
        self.item_type = item_type
        self.item_name = item_name
        self.default = defv
        self.minsize = mins
        self.maxsize = maxs

    def __str__(self):
        return f'ArrayType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(data: Dict, name: str, props: Dict):
        item_type = None
        if 'items' in props:
            item_type = load_type(data, 'items', props['items'])
        elif '$ref' in props:
            item_type = load_ref_type(data, 'items', props)
            # if item_type.type == 'object':          # aaaarrgghhh
            #     item_type.type = item_type.name

        return ArrayType(
            name=name,
            type_=props.get('type', 'array'),
            item_type=item_type,
            item_name=props.get('itemName', 'entry'),
            description=props.get('description', ''),
            defv=props.get('default', None),
            mins=props.get('minItems', props.get('min', None)),
            maxs=props.get('maxItems', props.get('max', None))
        )

    def doc(self, root) -> List[DocEntry]:
        doc_ = getattr(self.item_type, 'doc', None)
        if callable(doc_):
            return doc_(f"{root}")
        else:
            xpath = f"{root}/@{self.name}"
            default = self.item_type.default if hasattr(self.item_type, 'default') else ""
            return [DocEntry(xpath, self.description, True if self.minsize else False, default)]


class DictionaryType(Type):
    def __init__(self, name: str, type_: str, key_type: Type, value_type: Type, description: str = None, defv: Dict = None):
        super().__init__(name, type_, description)
        self.key_type = key_type
        self.value_type = value_type
        self.default = defv

    def __str__(self):
        return f'DictionaryType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(data: Dict, name: str, props: Dict):
        key_type = None
        if 'type' in props['keys']:
            key_type = load_type(data, 'type', props['keys'])
        elif '$ref' in props['keys']:
            key_type = load_ref_type(data, 'keys', props['keys'])

        # if 'keys' in props:
        #     key_type = load_type(data, 'keys', props['keys'])
        # elif '$ref' in props:
        #     key_type = load_ref_type(data, 'keys', props)

        value_type = None
        if 'values' in props:
            value_type = load_type(data, 'values', props['values'])
        elif '$ref' in props:
            value_type = load_ref_type(data, 'values', props)

        return DictionaryType(
            name=name,
            type_=props.get('type', 'dict'),
            key_type=key_type,
            value_type=value_type,
            description=props.get('description', ''),
            defv=props.get('default', None)
        )

    def doc(self, root) -> List[DocEntry]:
        # TODO: what is this, and how can we make this work for dictionaries?
        doc_ = getattr(self.value_type, 'doc', None)
        if callable(doc_):
            return doc_(f"{root}")
        else:
            xpath = f"{root}/@{self.name}"
            default = self.value_type.default if hasattr(self.value_type, 'default') else ""
            return [DocEntry(xpath, self.description, False, default)]


class ObjectField:
    def __init__(self, name: str, type_: Type, description: str = None,
                 required: bool = False):
        self.name = name
        self.type = type_
        self.description = description
        self.required = required

    def __str__(self):
        return f'Field{{name={self.name},type={self.type},required={self.required}}}'

    def __repr__(self):
        return self.__str__()

    def doc(self, root) -> List[DocEntry]:
        doc_ = getattr(self.type, 'doc', None)
        if callable(doc_):
            return doc_(f"{root}/{self.name}")
        else:
            xpath = f"{root}/@{self.name}"
            default = self.type.default if hasattr(self.type, 'default') else ""
            return [DocEntry(xpath, self.description, self.required, default)]


class ObjectType(Type):
    def __init__(self, name: str, type_: str, description: str = None,
                 fields: List[ObjectField] = None, xml: dict = None):
        super().__init__(name, type_, description)
        self.fields = fields
        self.xml = xml if xml else dict()

    def __str__(self):
        return f'ObjectType{{name={self.name},type={self.type},alias={self.alias},fields={self.fields},xml={self.xml}}}'

    @staticmethod
    def create(data: Dict, name: str, props: Dict):
        fields = []
        required_fields = props.get('required', [])
        xml = props.get('xml', {})
        if 'properties' in props:
            for pkey, pval in props['properties'].items():
                pt = load_type(data, pkey, pval)
                if pt:
                    fields.append(
                        ObjectField(
                            name=pkey,
                            type_=pt,
                            description=pt.description,
                            required=True if pkey in required_fields else False
                        )
                    )
        return ObjectType(
            name=name,
            type_=props.get('type', 'object'),
            description=props.get('description', ''),
            fields=fields,
            xml=xml
        )

    def doc(self, root) -> List[DocEntry]:
        r = []
        for field in self.fields:
            r.extend(field.doc(root))
        return r


def data_from_path(data: Dict, path: List[str]):
    key = path[0]
    if len(path) == 1:
        return key, data[key]
    return data_from_path(data[key], path[1:])


def load_type(data: Dict, name: str, props: Dict) -> Optional[Type]:
    try:
        res = load_type_(data, name, props)
        if not res:
            return None
        try:
            res.required = props['required']
        except KeyError:
            res.required = False
        return res
    except Exception:
        print(f'failed to load type "{name}"')
        raise


def load_type_(data: Dict, name: str, props: Dict) -> Optional[Type]:
    if 'type' in props:
        if props['type'] in ['int', 'integer', 'number', 'uint', 'unsigned']:
            if 'enum' in props.keys():
                return EnumType.create(name, props)
            else:
                return IntegerType.create(name, props)

        if props['type'] in ['float', 'double']:
            return FloatingType.create(name, props)

        if props['type'] in ['bool', 'boolean']:
            return BooleanType.create(name, props)

        if props['type'] in ['string']:
            if 'enum' in props.keys():
                return EnumType.create(name, props)
            else:
                return StringType.create(name, props)

        if props['type'] in ['array', 'list']:
            return ArrayType.create(data, name, props)

        if props['type'] in ['dict', 'dictionary', 'map']:
            return DictionaryType.create(data, name, props)

        if props['type'] in ['object']:
            return ObjectType.create(data, name, props)

    elif '$ref' in props:
        return load_ref_type(data, name, props)

    return None


def load_ref_type(data: Dict, name: str, props: Dict) -> Type:
    # 1. find and load type from data
    path = props['$ref'].split('/')
    if path[0] != '#':
        raise NotImplementedError('external references not supported')
    key, value = data_from_path(data, path[1:])
    t = load_type(data, key, value)
    t.alias = name

    # 2. overwrite properties if present
    if isinstance(t, IntegerType):
        t.description = props.get('description', t.description)
        t.base = props.get('base', t.base)
        t.default = props.get('default', t.default)
        t.min = props.get('min', t.min)
        t.max = props.get('max', t.max)

    if isinstance(t, FloatingType):
        t.description = props.get('description', t.description)
        t.default = props.get('default', t.default)
        t.min = props.get('min', t.min)
        t.max = props.get('max', t.max)

    if isinstance(t, BooleanType):
        t.description = props.get('description', t.description)
        t.default = props.get('default', t.default)

    if isinstance(t, StringType):
        t.description = props.get('description', t.description)
        t.default = props.get('default', t.default)
        t.pattern = props.get('pattern', t.pattern)
        t.min = props.get('min', t.min)
        t.max = props.get('max', t.max)

    if isinstance(t, EnumType):
        t.description = props.get('description', t.description)
        t.default = props.get('default', t.default)

    if isinstance(t, ArrayType):
        t.description = props.get('description', t.description)
        t.default = props.get('default', t.default)
        t.minsize = props.get('min', t.minsize)
        t.maxsize = props.get('max', t.maxsize)

    if isinstance(t, DictionaryType):
        t.description = props.get('description', t.description)
        t.default = props.get('default', t.default)

    if isinstance(t, ObjectType):
        t.description = props.get('description', t.description)

    return t


class Constraint:
    def __init__(self, typename: str, id_: str, scope: str):
        self.type = typename
        self.id = id_
        self.scope = scope


class UniqueConstraint(Constraint):
    def __init__(self, id_: str, scope: str, field: str):
        super().__init__('unique', id_, scope)
        self.field = field


class KeyRefConstraint(Constraint):
    def __init__(self, id_: str, scope: str, refer: str, field: str):
        super().__init__('keyref', id_, scope)
        self.refer = refer
        self.field = field


def load_constraints(data: Dict) -> List[Constraint]:
    result = []
    if 'constraints' in data:
        try:
            for cst in data['constraints']:
                obj = load_constraint(cst)
                if obj is None:
                    continue
                result.append(obj)
        except Exception:
            print('failed to load constraints')
            raise
    return result


def load_constraint(data: Dict) -> Optional[Constraint]:
    ctype = 'unknown'
    cid = 'unknown'
    try:
        if 'unique' in data:
            ctype = 'unique'
            cid = data['id']
            return UniqueConstraint(data['id'], data['scope'], data['field'])
        if 'keyref' in data:
            ctype = 'keyref'
            cid = data['id']
            return KeyRefConstraint(data['id'], data['scope'], data['refer'], data['field'])
        raise ValueError('unknown constraint type')
    except Exception:
        print(f'failed to load constraint "{ctype}" "{cid}"')
    return None
