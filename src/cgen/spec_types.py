import logging

from .doc import DocEntry


class Type:
    def __init__(
        self,
        name: str,
        type_: str,
        description: str,
        xml: dict | None,
    ):
        self.name = name
        self.type = type_
        self.description = description
        self.alias = name
        self.constraints = []
        self.xml = xml if xml else {}
        self.is_ref = False
        self.is_nested = False
        self.required = False

    def __str__(self):
        return f"""Type{{
            name={self.name},
            type={self.type},
            alias={self.alias},
            constraints={self.constraints}}}"""


class IntegerType(Type):
    def __init__(
        self,
        name: str,
        type_: str,
        description: str = "",
        base: int | None = None,
        defv: str | None = None,
        minv: str | None = None,
        maxv: str | None = None,
        xml: dict | None = None,
    ):
        super().__init__(name, type_, description, xml)
        self.base = base if base else 10
        self.default = defv
        self.min = minv
        self.max = maxv

    def __str__(self):
        return f"""IntegerType{{
            name={self.name},
            type={self.type},
            alias={self.alias},
            default={self.default}}}"""

    @staticmethod
    def create(name: str, props: dict, ttype: str):
        return IntegerType(
            name=name,
            type_=ttype,
            description=props.get("description", ""),
            defv=props.get("default", None),
            base=props.get("base", 10),
            minv=props.get("min", None),
            maxv=props.get("max", None),
            xml=props.get("xml", None),
        )


class FloatingType(Type):
    def __init__(
        self,
        name: str,
        type_: str,
        description: str = "",
        defv: str | None = None,
        minv: str | None = None,
        maxv: str | None = None,
        xml: dict | None = None,
    ):
        super().__init__(name, type_, description, xml)
        self.default = defv
        self.min = minv
        self.max = maxv

    def __str__(self):
        return f"""FloatingType{{
            name={self.name},
            type={self.type},
            alias={self.alias}}}"""

    @staticmethod
    def create(name: str, props: dict, ttype: str):
        return FloatingType(
            name=name,
            type_=ttype,
            description=props.get("description", ""),
            defv=props.get("default", None),
            minv=props.get("min", None),
            maxv=props.get("max", None),
            xml=props.get("xml", None),
        )


class BooleanType(Type):
    def __init__(
        self,
        name: str,
        type_: str,
        description: str = "",
        defv: bool | None = None,
        xml: dict | None = None,
    ):
        super().__init__(name, type_, description, xml)
        self.default = None
        if isinstance(defv, bool):
            self.default = defv
        elif isinstance(defv, str):
            defv = defv.lower()
            if defv in ["true", "yes", "on", "1"]:
                self.default = True
            elif defv in ["false", "no", "off", "0"]:
                self.default = False
        elif isinstance(defv, int):
            self.default = defv != 0

    def __str__(self):
        return f"""BooleanType{{
            name={self.name},
            type={self.type},
            alias={self.alias}}}"""

    @staticmethod
    def create(name: str, props: dict, ttype: str):
        return BooleanType(
            name=name,
            type_=ttype,
            description=props.get("description", ""),
            defv=props.get("default", None),
            xml=props.get("xml", None),
        )


class StringType(Type):
    def __init__(
        self,
        name: str,
        type_: str,
        description: str = "",
        defv: str | None = None,
        pattern: str | None = None,
        minl: int | None = None,
        maxl: int | None = None,
        xml: dict | None = None,
    ):
        super().__init__(name, type_, description, xml)
        self.default = defv
        self.pattern = pattern
        self.min = minl
        self.max = maxl

    def __str__(self):
        return f"""StringType{{
            name={self.name},
            type={self.type},
            alias={self.alias}}}"""

    @staticmethod
    def create(name: str, props: dict, ttype: str):
        return StringType(
            name=name,
            type_=ttype,
            description=props.get("description", ""),
            defv=props.get("default", None),
            pattern=props.get("pattern", None),
            minl=props.get("min", None),
            maxl=props.get("max", None),
            xml=props.get("xml", None),
        )


class EnumType(Type):
    def __init__(
        self,
        name: str,
        type_: str,
        base_type: str,
        enum: list[str],
        description: str = "",
        defv: str | None = None,
        xml: dict | None = None,
    ):
        super().__init__(name, type_, description, xml)
        self.base_type = base_type
        self.enum = enum
        self.default = defv

    def __str__(self):
        return f"""EnumType{{
            name={self.name},
            type={self.type},
            base_type={self.base_type},
            alias={self.alias}}}"""

    @staticmethod
    def create(name: str, props: dict, ttype: str):
        return EnumType(
            name=name,
            type_="enum",
            base_type=ttype,
            enum=props.get("enum", None),
            description=props.get("description", ""),
            defv=props.get("default", None),
            xml=props.get("xml", None),
        )


class ArrayType(Type):
    def __init__(
        self,
        name: str,
        type_: str,
        item_type: Type,
        item_name: str,
        description: str = "",
        defv: list[str] | None = None,
        mins: int | None = None,
        maxs: int | None = None,
        xml: dict | None = None,
    ):
        super().__init__(name, type_, description, xml)
        self.item_type = item_type
        self.item_name = item_name
        self.default = defv
        self.minsize = mins
        self.maxsize = maxs

    def __str__(self):
        return f"""ArrayType{{
            name={self.name},
            type={self.type},
            alias={self.alias}}}"""

    @staticmethod
    def create(data: dict, name: str, props: dict, ttype: str):
        item_type: Type | None = None
        if "items" in props:
            item_type = load_type(data, "items", props["items"])
        elif "$ref" in props:
            item_type = load_ref_type(data, "items", props)
            # if item_type.type == 'object':          # aaaarrgghhh
            #     item_type.type = item_type.name

        if item_type is None:
            raise Exception(f"could not resolve item type of '{name}'")

        return ArrayType(
            name=name,
            type_=ttype,
            item_type=item_type,
            item_name=props.get("itemName", "entry"),
            description=props.get("description", ""),
            defv=props.get("default", None),
            mins=props.get("minItems", props.get("min", None)),
            maxs=props.get("maxItems", props.get("max", None)),
            xml=props.get("xml", None),
        )

    def doc(self, root) -> list[DocEntry]:
        doc_ = getattr(self.item_type, "doc", None)
        if callable(doc_):
            return doc_(f"{root}")
        else:
            xpath = f"{root}/@{self.name}"
            default = getattr(self.item_type, "default", "")
            return [
                DocEntry(
                    xpath, self.description, True if self.minsize else False, default
                )
            ]


class DictionaryType(Type):
    def __init__(
        self,
        name: str,
        type_: str,
        key_type: Type,
        value_type: Type,
        description: str = "",
        defv: dict | None = None,
        xml: dict | None = None,
    ):
        super().__init__(name, type_, description, xml)
        self.key_type = key_type
        self.value_type = value_type
        self.default = defv

    def __str__(self):
        return f"""DictionaryType{{
            name={self.name},
            type={self.type},
            alias={self.alias}}}"""

    @staticmethod
    def create(data: dict, name: str, props: dict, ttype: str):
        key_type = None
        if "type" in props["keys"]:
            key_type = load_type(data, "type", props["keys"])
        elif "$ref" in props["keys"]:
            key_type = load_ref_type(data, "keys", props["keys"])

        if key_type is None:
            raise Exception(f"could not retrieve key type of '{name}'")

        value_type = None
        if "values" in props:
            value_type = load_type(data, "values", props["values"])
        elif "$ref" in props:
            value_type = load_ref_type(data, "values", props)

        if value_type is None:
            raise Exception(f"could not retrieve value type of '{name}'")

        return DictionaryType(
            name=name,
            type_=ttype,
            key_type=key_type,
            value_type=value_type,
            description=props.get("description", ""),
            defv=props.get("default", None),
            xml=props.get("xml", None),
        )

    def doc(self, root) -> list[DocEntry]:
        # TODO: what is this, and how can we make this work for dictionaries?
        doc_ = getattr(self.value_type, "doc", None)
        if callable(doc_):
            return doc_(f"{root}")
        else:
            xpath = f"{root}/@{self.name}"
            default = getattr(self.value_type, "default", "")
            return [DocEntry(xpath, self.description, False, default)]


class ObjectField:
    def __init__(
        self,
        name: str,
        type_: Type,
        description: str = "",
        required: bool = False,
        default: bool = False,  # only used for objects
    ):
        self.name = name
        self.type = type_
        self.description = description
        self.required = required
        self.default = default

    def __str__(self):
        return f"Field{{name={self.name},type={self.type},required={self.required}}}"

    def __repr__(self):
        return self.__str__()

    def doc(self, root) -> list[DocEntry]:
        doc_ = getattr(self.type, "doc", None)
        if callable(doc_):
            return doc_(f"{root}/{self.name}")
        else:
            xpath = f"{root}/@{self.name}"
            default = getattr(self.type, "default", "")
            return [DocEntry(xpath, self.description, self.required, default)]


class ObjectType(Type):
    def __init__(
        self,
        name: str,
        type_: str,
        description: str = "",
        defv: bool = False,
        fields: list[ObjectField] | None = None,
        xml: dict | None = None,
    ):
        super().__init__(name, type_, description, xml)
        self.default = defv
        self.fields = fields if fields else []

    def __str__(self):
        return f"""ObjectType{{
            name={self.name},
            type={self.type},
            alias={self.alias},
            fields={self.fields},
            xml={self.xml}}}"""

    @staticmethod
    def create(data: dict, name: str, props: dict, ttype: str):
        fields = []
        required_fields = props.get("required", [])
        xml = props.get("xml", None)
        if "properties" in props:
            for pkey, pval in props["properties"].items():
                pt = load_type(data, pkey, pval)
                if pt:
                    fields.append(
                        ObjectField(
                            name=pkey,
                            type_=pt,
                            description=pt.description,
                            required=True if pkey in required_fields else False,
                        )
                    )
        return ObjectType(
            name=name,
            type_=ttype,
            description=props.get("description", ""),
            defv=props.get("default", False),
            fields=fields,
            xml=xml,
        )

    def doc(self, root) -> list[DocEntry]:
        r = []
        for field in self.fields:
            r.extend(field.doc(root))
        return r


def data_from_path(data: dict, path: list[str]):
    key = path[0]
    if len(path) == 1:
        return key, data[key]
    return data_from_path(data[key], path[1:])


def load_type(data: dict, name: str, props: dict) -> Type | None:
    try:
        res = load_type_(data, name, props)
        if not res:
            return None
        # res.required = props.get("required", False)  # deprecated
        # res.required = props.get("use", "optional") == "required"
        required_old: bool | None = props.get("required", None)
        required_new: bool | None = props.get("use", None)
        if required_old is not None:
            res.required = required_old
        elif required_new is not None:
            res.required = required_new == "required"
        else:
            res.required = False
        return res
    except Exception:
        logging.error(f'failed to load type "{name}"')
        raise


def load_type_(data: dict, name: str, props: dict) -> Type | None:
    if "type" in props:
        if props["type"] in ["int", "integer", "number"]:
            if "enum" in props.keys():
                return EnumType.create(name, props, ttype="int")
            else:
                return IntegerType.create(name, props, ttype="int")

        if props["type"] in ["uint", "unsigned"]:
            if "enum" in props.keys():
                return EnumType.create(name, props, ttype="uint")
            else:
                return IntegerType.create(name, props, ttype="uint")

        if props["type"] in ["float", "double"]:
            return FloatingType.create(name, props, ttype=props["type"])

        if props["type"] in ["bool", "boolean"]:
            return BooleanType.create(name, props, ttype="bool")

        if props["type"] in ["string"]:
            if "enum" in props.keys():
                return EnumType.create(name, props, ttype="string")
            else:
                return StringType.create(name, props, ttype="string")

        if props["type"] in ["array", "list"]:
            return ArrayType.create(data, name, props, ttype="array")

        if props["type"] in ["dict", "dictionary", "map"]:
            return DictionaryType.create(data, name, props, ttype="dict")

        if props["type"] in ["object"]:
            return ObjectType.create(data, name, props, ttype="object")

    elif "$ref" in props:
        return load_ref_type(data, name, props)

    return None


def load_ref_type(data: dict, name: str, props: dict) -> Type | None:
    # 1. find and load type from data
    path = props["$ref"].split("/")
    if path[0] != "#":
        raise NotImplementedError("external references not supported")
    key, value = data_from_path(data, path[1:])
    t = load_type(data, key, value)
    if t is not None:
        t.alias = name
        t.is_ref = True

    # 2. overwrite properties if present
    if isinstance(t, IntegerType):
        t.description = props.get("description", t.description)
        t.base = props.get("base", t.base)
        t.default = props.get("default", t.default)
        t.min = props.get("min", t.min)
        t.max = props.get("max", t.max)
        t.xml = props.get("xml", t.xml)

    if isinstance(t, FloatingType):
        t.description = props.get("description", t.description)
        t.default = props.get("default", t.default)
        t.min = props.get("min", t.min)
        t.max = props.get("max", t.max)
        t.xml = props.get("xml", t.xml)

    if isinstance(t, BooleanType):
        t.description = props.get("description", t.description)
        t.default = props.get("default", t.default)
        t.xml = props.get("xml", t.xml)

    if isinstance(t, StringType):
        t.description = props.get("description", t.description)
        t.default = props.get("default", t.default)
        t.pattern = props.get("pattern", t.pattern)
        t.min = props.get("min", t.min)
        t.max = props.get("max", t.max)
        t.xml = props.get("xml", t.xml)

    if isinstance(t, EnumType):
        t.description = props.get("description", t.description)
        t.default = props.get("default", t.default)
        t.xml = props.get("xml", t.xml)

    if isinstance(t, ArrayType):
        t.description = props.get("description", t.description)
        t.default = props.get("default", t.default)
        t.minsize = props.get("min", t.minsize)
        t.maxsize = props.get("max", t.maxsize)
        t.xml = props.get("xml", t.xml)

    if isinstance(t, DictionaryType):
        t.description = props.get("description", t.description)
        t.default = props.get("default", t.default)
        t.xml = props.get("xml", t.xml)

    if isinstance(t, ObjectType):
        t.description = props.get("description", t.description)
        t.default = props.get("default", t.default)
        t.xml = props.get("xml", t.xml)

    return t


class Constraint:
    def __init__(self, typename: str, id_: str, scope: str):
        self.type = typename
        self.id = id_
        self.scope = scope


class UniqueConstraint(Constraint):
    def __init__(self, id_: str, scope: str, field: str):
        super().__init__("unique", id_, scope)
        self.field = field


class KeyRefConstraint(Constraint):
    def __init__(self, id_: str, scope: str, refer: str, field: str):
        super().__init__("keyref", id_, scope)
        self.refer = refer
        self.field = field


def load_constraints(data: dict) -> list[Constraint]:
    result = []
    if "constraints" in data:
        try:
            for cst in data["constraints"]:
                obj = load_constraint(cst)
                if obj is None:
                    continue
                result.append(obj)
        except Exception:
            logging.error("failed to load constraints")
            raise
    return result


def load_constraint(data: dict) -> Constraint | None:
    ctype = "unknown"
    cid = "unknown"
    try:
        if "unique" in data:
            ctype = "unique"
            cid = data["id"]
            return UniqueConstraint(data["id"], data["scope"], data["field"])
        if "keyref" in data:
            ctype = "keyref"
            cid = data["id"]
            return KeyRefConstraint(
                data["id"], data["scope"], data["refer"], data["field"]
            )
        raise ValueError("unknown constraint type")
    except Exception:
        logging.error(f'failed to load constraint "{ctype}" "{cid}"')
    return None

#
# A couple of comparison functions used for detecting and filtering out
# duplicate types, but to keep those that have relevant changes.
# These functions do not compare for complete equality of the the given
# types, as this would lead to a lot of unnecessary type duplication.
# Due to this "incompleteness" these functions are placed here and not
# implemented on the types themselves.
# I'll keep the omitted checks in here, but commented out, just to make clear
# that they were considered but cannot be used for our purpose.
# TODO:
# implement a more generic approach with white/blacklists
# of properties that need to match
#

def is_equal_type(a: Type, b: Type) -> bool:
    try:
        if a.name != b.name:
            return False
        if a.type != b.type:
            return False
        # if a.alias != b.alias:
        #     return False
        # if not is_equal_list(a.constraints, b.constraints):   # TODO: this one should be checked!
        #     return False
        if a.is_ref != b.is_ref:
            return False
        # if a.is_nested != b.is_nested:
        #     return False
        # if a.required != b.required:
        #     return False

        if isinstance(a, IntegerType) and isinstance(b, IntegerType):
            return is_equal_type_integer(a, b)
        if isinstance(a, FloatingType) and isinstance(b, FloatingType):
            return is_equal_type_floating(a, b)
        if isinstance(a, BooleanType) and isinstance(b, BooleanType):
            return is_equal_type_boolean(a, b)
        if isinstance(a, StringType) and isinstance(b, StringType):
            return is_equal_type_string(a, b)
        if isinstance(a, EnumType) and isinstance(b, EnumType):
            return is_equal_type_enum(a, b)
        if isinstance(a, ArrayType) and isinstance(b, ArrayType):
            return is_equal_type_array(a, b)
        if isinstance(a, DictionaryType) and isinstance(b, DictionaryType):
            return is_equal_type_dictionary(a, b)
        if isinstance(a, ObjectType) and isinstance(b, ObjectType):
            return is_equal_type_object(a, b)
        return False
    except Exception as error:
        print(error)
        return False


def is_equal_type_integer(a: IntegerType, b: IntegerType) -> bool:
    if a.base != b.base:
        return False
    if a.min != b.min:
        return False
    if a.max != b.max:
        return False
    # if a.default != b.default:
    #     return False
    return True


def is_equal_type_floating(a: FloatingType, b: FloatingType) -> bool:
    if a.min != b.min:
        return False
    if a.max != b.max:
        return False
    # if a.default != b.default:
    #     return False
    return True


def is_equal_type_boolean(a: BooleanType, b: BooleanType) -> bool:
    # if a.default != b.default:
    #     return False
    return True


def is_equal_type_string(a: StringType, b: StringType) -> bool:
    if a.pattern != b.pattern:
        return False
    if a.min != b.min:
        return False
    if a.max != b.max:
        return False
    # if a.default != b.default:
    #     return False
    return True


def is_equal_type_enum(a: EnumType, b: EnumType) -> bool:
    if a.base_type != b.base_type:
        return False
    if len(a.enum) != len(b.enum):
        return False
    for idx in range(len(a.enum)):
        if a.enum[idx] != b.enum[idx]:
            return False
    # if a.default != b.default:
    #     return False
    return True


def is_equal_type_array(a: ArrayType, b: ArrayType) -> bool:
    if not is_equal_type(a.item_type, b.item_type):
        return False
    if a.item_name != b.item_name:
        return False
    if a.minsize != b.minsize:
        return False
    if a.maxsize != b.maxsize:
        return False
    # # todo ... array compare
    # if a.default != b.default:
    #     return False
    return True


def is_equal_type_dictionary(a: DictionaryType, b: DictionaryType) -> bool:
    if not is_equal_type(a.key_type, b.key_type):
        return False
    if not is_equal_type(a.value_type, b.value_type):
        return False
    # # todo ... dict compare
    # if a.default != b.default:
    #     return False
    return True


def is_equal_type_object_field(a: ObjectField, b: ObjectField) -> bool:
    if a.name != b.name:
        return False
    if not is_equal_type(a.type, b.type):
        return False
    return True

def is_equal_type_object(a: ObjectType, b: ObjectType) -> bool:
    if len(a.fields) != len(b.fields):
        return False
    for idx in range(len(a.fields)):
        if not is_equal_type_object_field(a.fields[idx], b.fields[idx]):
            return False
    return True
