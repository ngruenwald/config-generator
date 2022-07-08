from argparse import ArgumentError
from typing import List


class Type():
    def __init__(self, name: str, type: str, description: str):
        self.name = name
        self.type = type
        self.description = description
        self.alias = name
        self.constraints = []

    def __str__(self):
        return f'Type{{name={self.name},type={self.type},alias={self.alias},constraints={self.constraints}}}'


class IntegerType(Type):
    def __init__(self, name: str, type: str, description: str = None,
                 base: int = None, defv: str = None,
                 minv: str = None, maxv: str = None):
        super().__init__(name, type, description)
        self.base = base if base else 10
        self.default = defv
        self.min = minv
        self.max = maxv

    def __str__(self):
        return f'IntegerType{{default={self.default}}}'

    @staticmethod
    def create(name: str, props: dict()):
        return IntegerType(
            name=name,
            type=v_or_d(props, 'type', 'int'),
            description=v_or_d(props, 'description', ''),
            defv=v_or_d(props, 'default', None),
            base=v_or_d(props, 'base', 10),
            minv=v_or_d(props, 'min', None),
            maxv=v_or_d(props, 'max', None)
        )


class FloatingType(Type):
    def __init__(self, name: str, type: str, description: str = None,
                 defv: str = None, minv: str = None, maxv: str = None):
        super().__init__(name, type, description)
        self.default = defv
        self.min = minv
        self.max = maxv

    def __str__(self):
        return f'FloatingType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(name: str, props: dict()):
        return FloatingType(
            name=name,
            type=v_or_d(props, 'type', 'float'),
            description=v_or_d(props, 'description', ''),
            defv=v_or_d(props, 'default', None),
            minv=v_or_d(props, 'min', None),
            maxv=v_or_d(props, 'max', None)
        )


class BooleanType(Type):
    def __init__(self, name: str, type: str, description: str = None,
                 defv: bool = None):
        super().__init__(name, type, description)
        self.default = defv if defv is not None else False

    def __str__(self):
        return f'BooleanType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(name: str, props: dict()):
        return BooleanType(
            name=name,
            type=v_or_d(props, 'type', 'bool'),
            description=v_or_d(props, 'description', ''),
            defv=v_or_d(props, 'default', None)
        )


class StringType(Type):
    def __init__(self, name: str, type: str, description: str = None,
                 defv: str = None, pattern: str = None,
                 minl: int = None, maxl: int = None):
        super().__init__(name, type, description)
        self.default = defv
        self.pattern = pattern
        self.min = minl
        self.max = maxl

    def __str__(self):
        return f'StringType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(name: str, props: dict()):
        return StringType(
            name=name,
            type=v_or_d(props, 'type', 'string'),
            description=v_or_d(props, 'description', ''),
            defv=v_or_d(props, 'default', None),
            pattern=v_or_d(props, 'pattern', None),
            minl=v_or_d(props, 'min', None),
            maxl=v_or_d(props, 'max', None)
        )


class EnumType(Type):
    def __init__(self, name: str, type: str, base_type: str, enum: List[str],
                 description: str = None, defv: str = None):
        super().__init__(name, type, description)
        self.base_type = base_type
        self.enum = enum
        self.default = defv

    def __str__(self):
        return f'EnumType{{name={self.name},type={self.type},base_type={self.base_type},alias={self.alias}}}'

    @staticmethod
    def create(name: str, props: dict()):
        return EnumType(
            name=name,
            type='enum',
            base_type=v_or_d(props, 'type', 'string'),
            enum=v_or_d(props, 'enum', None),
            description=v_or_d(props, 'description', ''),
            defv=v_or_d(props, 'default', None)
        )


class ArrayType(Type):
    def __init__(self, name: str, type: str, item_type: Type,
                 item_name: str, description: str = None,
                 defv: List[str] = None,
                 mins: int = None, maxs: int = None):
        super().__init__(name, type, description)
        self.item_type = item_type
        self.item_name = item_name
        self.default = defv
        self.minsize = mins
        self.maxsize = maxs

    def __str__(self):
        return f'ArrayType{{name={self.name},type={self.type},alias={self.alias}}}'

    @staticmethod
    def create(data: dict(), name: str, props: dict()):
        item_type = None
        if 'items' in props:
            item_type = load_type(data, 'items', props['items'])
        elif '$ref' in props:
            item_type = load_ref_type(data, 'items', props)
            # if item_type.type == 'object':          # aaaarrgghhh
            #     item_type.type = item_type.name

        return ArrayType(
            name=name,
            type=v_or_d(props, 'type', 'array'),
            item_type=item_type,
            item_name=v_or_d(props, 'itemName', 'entry'),
            description=v_or_d(props, 'description', ''),
            defv=v_or_d(props, 'default', None),
            mins=v_or_d(props, 'minItems', v_or_d(props, 'min', None)),
            maxs=v_or_d(props, 'maxItems', v_or_d(props, 'max', None))
        )


class ObjectField():
    def __init__(self, name: str, type: Type, description: str = None,
                 required: bool = False):
        self.name = name
        self.type = type
        self.description = description
        self.required = required

    def __str__(self):
        return f'Field{{name={self.name},type={self.type},required={self.required}}}'

    def __repr__(self):
        return self.__str__()


class ObjectType(Type):
    def __init__(self, name: str, type: str, description: str = None,
                 fields: List[ObjectField] = None, xmltype: str = 'sequence'):
        super().__init__(name, type, description)
        self.fields = fields
        self.xmltype = xmltype

    def __str__(self):
        return f'ObjectType{{name={self.name},type={self.type},alias={self.alias},fields={self.fields},xmltype={self.xmltype}}}'

    @staticmethod
    def create(data: dict(), name: str, props: str):
        fields = []
        required_fields = v_or_d(props, 'required', [])
        xmltype = v_or_d(props, 'xmltype', 'sequence')
        if 'properties' in props:
            for pkey, pval in props['properties'].items():
                pt = load_type(data, pkey, pval)
                if pt:
                    fields.append(
                        ObjectField(
                            name=pkey,
                            type=pt,
                            description=pt.description,
                            required=True if pkey in required_fields else False
                        )
                    )
        return ObjectType(
            name=name,
            type=v_or_d(props, 'type', 'object'),
            description=v_or_d(props, 'description', ''),
            fields=fields,
            xmltype=xmltype
        )


def v_or_d(data: dict(), key: str, defv):
    return data[key] if key in data else defv


def data_from_path(data: dict(), path: List[str]):
    key = path[0]
    if len(path) == 1:
        return key, data[key]
    return data_from_path(data[key], path[1:])


def load_type(data: dict(), name: str, props: dict()) -> Type:
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


def load_type_(data: dict(), name: str, props: dict()) -> Type:
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

        if props['type'] in ['object']:
            return ObjectType.create(data, name, props)

    elif '$ref' in props:
        return load_ref_type(data, name, props)

    return None


def load_ref_type(data: dict(), name: str, props: dict()) -> Type:
    # 1. find and load type from data
    path = props['$ref'].split('/')
    if path[0] != '#':
        raise NotImplementedError('external references not supported')
    key, value = data_from_path(data, path[1:])
    t = load_type(data, key, value)
    t.alias = name

    # 2. overwrite properties if present
    if isinstance(t, IntegerType):
        t.description = v_or_d(props, 'description', t.description)
        t.base = v_or_d(props, 'base', t.base)
        t.default = v_or_d(props, 'default', t.default)
        t.min = v_or_d(props, 'min', t.min)
        t.max = v_or_d(props, 'max', t.max)

    if isinstance(t, FloatingType):
        t.description = v_or_d(props, 'description', t.description)
        t.default = v_or_d(props, 'default', t.default)
        t.min = v_or_d(props, 'min', t.min)
        t.max = v_or_d(props, 'max', t.max)

    if isinstance(t, BooleanType):
        t.description = v_or_d(props, 'description', t.description)
        t.default = v_or_d(props, 'default', t.default)

    if isinstance(t, StringType):
        t.description = v_or_d(props, 'description', t.description)
        t.default = v_or_d(props, 'default', t.default)
        t.pattern = v_or_d(props, 'pattern', t.pattern)
        t.min = v_or_d(props, 'min', t.min)
        t.max = v_or_d(props, 'max', t.max)

    if isinstance(t, EnumType):
        t.description = v_or_d(props, 'description', t.description)
        t.default = v_or_d(props, 'default', t.default)

    if isinstance(t, ArrayType):
        t.description = v_or_d(props, 'description', t.description)
        t.default = v_or_d(props, 'default', t.default)
        t.minsize = v_or_d(props, 'min', t.minsize)
        t.maxsize = v_or_d(props, 'max', t.maxsize)

    if isinstance(t, ObjectType):
        t.description = v_or_d(props, 'description', t.description)

    return t


class Constraint():
    def __init__(self, typename: str, id: str, scope: str):
        self.type = typename
        self.id = id
        self.scope = scope


class UniqueConstraint(Constraint):
    def __init__(self, id: str, scope: str, field: str):
        super().__init__('unique', id, scope)
        self.field = field


class KeyRefConstraint(Constraint):
    def __init__(self, id: str, scope: str, refer: str, field: str):
        super().__init__('keyref', id, scope)
        self.refer = refer
        self.field = field


def load_constraints(data: dict()) -> List[Constraint]:
    result = []
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


def load_constraint(data: dict()) -> Constraint:
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
        raise ArgumentError('unknown constraint type')
    except Exception:
        print(f'failed to load constraint "{ctype}" "{cid}"')
    return None
