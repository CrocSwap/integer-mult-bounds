"""Strict syntax and byte-independent binding, not an algebraic compiler.

Prepared for Krzysztof Wójt with OpenAI Codex assistance. Apache-2.0.
"""

import hashlib
import json

from fields import Field


def exact_keys(obj, keys):
    if not isinstance(obj, dict) or set(obj) != set(keys):
        raise ValueError(f"expected exactly these keys: {sorted(keys)}")


def names(values, nonempty=False):
    if not isinstance(values, list) or (nonempty and not values):
        raise ValueError("expected a list of names")
    if any(not isinstance(x, str) or not x for x in values):
        raise ValueError("names must be nonempty strings")
    if len(set(values)) != len(values):
        raise ValueError("duplicate name")


def validate(program):
    exact_keys(program, {"schema", "field", "roles", "operators", "left", "right"})
    if program["schema"] != "inverse-dirty-program/v1":
        raise ValueError("unknown program schema")
    field = Field(program["field"])
    names(program["roles"], nonempty=True)
    names(program["operators"])
    roles, operators = set(program["roles"]), set(program["operators"])
    for side in ("left", "right"):
        if not isinstance(program[side], list):
            raise ValueError("instruction sequence must be a list")
        for ins in program[side]:
            if not isinstance(ins, dict):
                raise ValueError("instruction must be an object")
            op = ins.get("op")
            if op == "linear":
                exact_keys(ins, {"op", "dst", "terms"})
                if not isinstance(ins["terms"], list):
                    raise ValueError("linear terms must be a list")
                for term in ins["terms"]:
                    if not isinstance(term, list) or len(term) != 2 or term[0] not in roles:
                        raise ValueError("invalid linear term or undeclared source")
                    field.parse(term[1])
            elif op in ("apply", "query"):
                keys = {"op", "dst", "operator", "direction"}
                if op == "query":
                    keys |= {"src", "coefficient"}
                exact_keys(ins, keys)
                if ins["operator"] not in operators:
                    raise ValueError("undeclared operator")
                if type(ins["direction"]) is not int or ins["direction"] not in (-1, 1):
                    raise ValueError("direction must be exactly +1 or -1")
                if op == "query":
                    if ins["src"] not in roles:
                        raise ValueError("undeclared query source")
                    field.parse(ins["coefficient"])
            else:
                raise ValueError("unknown instruction")
            if ins["dst"] not in roles:
                raise ValueError("undeclared destination")
    return field


def fingerprint(program):
    payload = json.dumps(program, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()
