"""Emit and restore an ordered native directory with child-before-parent references."""

import struct
import sys
from array import array
from collections import Counter
from fractions import Fraction


def types():
    import grades
    from clock_ports import Ports
    from powered import Port, PoweredWord
    from raw_binary_stage import BinaryWord
    from transport import Recipe

    base = (
        type(None),
        bool,
        int,
        str,
        Fraction,
        tuple,
        list,
        dict,
        Counter,
        set,
        Port,
        Ports,
        PoweredWord,
        BinaryWord,
    )
    if hasattr(grades, "WeightedGrades"):
        return base + (
            grades.WeightedGrades,
            Recipe,
            grades.GradeVariant,
            grades.WeightedRecipe,
        )
    return base + (grades.Grades, Recipe)


def ref_bytes(ids):
    words = array("I", ids)
    assert words.itemsize == 4
    if sys.byteorder != "little":
        words.byteswap()
    return words.tobytes()


def dump(out, roots):
    cls = types()
    codes = {t: i for i, t in enumerate(cls)}
    ids = {}
    w = out.write
    w(b"IMBDAG1\x00")

    def visit(obj):
        k = id(obj)
        if k in ids:
            return ids[k]
        tag = codes[type(obj)]
        if tag == 0:
            body = b""
        elif tag == 1:
            body = bytes([obj])
        elif tag == 2:
            body = int(obj).to_bytes(
                max(1, (obj.bit_length() + 8) // 8), "little", signed=True
            )
        elif tag == 3:
            body = obj.encode("utf8")
        elif tag == 4:
            body = ref_bytes((visit(obj.numerator), visit(obj.denominator)))
        elif tag in (5, 6, 9):
            body = ref_bytes(visit(v) for v in (sorted(obj) if tag == 9 else obj))
        elif tag in (7, 8):
            body = ref_bytes(visit(v) for pair in obj.items() for v in pair)
        else:
            body = ref_bytes((visit(vars(obj)),))
        rid = len(ids)
        ids[k] = rid
        w(struct.pack("<BI", tag, len(body)))
        w(body)
        return rid

    root = visit(roots)
    assert root == len(ids) - 1
    return len(ids)


def load(src):
    cls = types()
    records = []
    if src.read(8) != b"IMBDAG1\x00":
        raise ValueError("wrong directory magic")
    while True:
        head = src.read(5)
        if not head:
            break
        tag, n = struct.unpack("<BI", head)
        body = src.read(n)
        if len(body) != n:
            raise ValueError("truncated directory record")
        if tag == 0:
            obj = None
        elif tag == 1:
            obj = bool(body[0])
        elif tag == 2:
            obj = int.from_bytes(body, "little", signed=True)
        elif tag == 3:
            obj = body.decode("utf8")
        else:
            refs = array("I")
            refs.frombytes(body)
            if sys.byteorder != "little":
                refs.byteswap()
            values = (records[i] for i in refs)
            if tag == 4:
                obj = Fraction(*values)
            elif tag == 5:
                obj = tuple(values)
            elif tag == 6:
                obj = list(values)
            elif tag == 9:
                obj = set(values)
            elif tag in (7, 8):
                obj = cls[tag]()
                for k, v in zip(values, values, strict=True):
                    obj[k] = v
            else:
                obj = object.__new__(cls[tag])
                (attrs,) = values
                vars(obj).update(attrs)
        records.append(obj)
    return records[-1]
