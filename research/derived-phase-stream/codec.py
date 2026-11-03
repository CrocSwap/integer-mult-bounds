#!/usr/bin/env python3
"""Derived idle-translation records, produced by Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

SCHEMA = "derived-idle-translations/v1"
MAX_BYTES = 2**21
MAX_WIDTH = 256
MAX_RECIPES = 256
MAX_CHILDREN = 64
MAX_AXES = 128
PORT_MASK = (1 << 9) - 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")
    require(len(data) <= MAX_BYTES, "document capacity exceeded")
    return data


def no_duplicate_keys(pairs):
    require(len(pairs) <= MAX_BYTES, "object capacity exceeded")
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def parse(data):
    require(isinstance(data, bytes) and len(data) <= MAX_BYTES,
            "input byte capacity exceeded")
    return json.loads(data, object_pairs_hook=no_duplicate_keys)


def integer(value, low, high, name):
    require(type(value) is int and low <= value <= high, "invalid " + name)
    return value


def column_tag(rows, width):
    """Return bit one of each column count, using three bit operations per row."""
    integer(width, 1, MAX_WIDTH, "width")
    require(type(rows) is list and len(rows) <= MAX_AXES + 1, "invalid rows")
    low = high = 0
    for row in rows:
        integer(row, 0, (1 << width) - 1, "row")
        high ^= low & row
        low ^= row
    return low, high


def translation(axes, q, width):
    """Synthesize the inherited mod-four column formula with two bit planes."""
    integer(width, 9, MAX_WIDTH, "width")
    integer(q, 1, PORT_MASK, "port normal")
    require(type(axes) is list and len(axes) <= MAX_AXES, "invalid axes")
    rows = [integer(a, 1, (1 << width) - 1, "axis") for a in axes]
    if any(a & PORT_MASK for a in rows):
        rows.append(q)
    support = 0
    for row in rows:
        support |= row
    require(support.bit_count() == len(rows), "frame is incomplete on support")
    for i, row in enumerate(rows):
        for j in range(i + 1):
            require((row & rows[j]).bit_count() % 2 == int(i == j),
                    "frame is not orthonormal")
    low, high = column_tag(rows, width)
    require(low == support, "column parity invariant failed")
    return high


def transform(document, expand):
    """Copy metadata, then derive or remove each declared idle translation."""
    result = parse(canonical(document))
    require(type(result) is dict, "document must be an object")
    width = integer(result.get("m"), 9, MAX_WIDTH, "width")
    recipes = result.get("recipes")
    require(type(recipes) is list and len(recipes) <= MAX_RECIPES,
            "invalid recipes")
    seen = set()
    for rec in recipes:
        require(type(rec) is dict, "invalid recipe")
        port = integer(rec.get("port"), 0, MAX_RECIPES - 1, "port")
        require(port not in seen, "duplicate port")
        seen.add(port)
        q = integer(rec.get("q"), 1, PORT_MASK, "port normal")
        children = rec.get("idle_children")
        require(type(children) is list and len(children) <= MAX_CHILDREN,
                "invalid idle children")
        for child in children:
            require(type(child) is dict, "invalid child")
            axes = child.get("orthogonal_axes")
            value = translation(axes, q, width)
            require(integer(child.get("rank"), 0, MAX_AXES, "rank") == len(axes),
                    "rank differs from axis count")
            if expand:
                require("translation_after" not in child, "stored translation in compact record")
                child["translation_after"] = value
            else:
                require(type(child.get("translation_after")) is int
                        and child["translation_after"] == value,
                        "stored translation differs from frame")
                del child["translation_after"]
    require(integer(result.get("ports"), 0, MAX_RECIPES, "port count") == len(recipes),
            "port count differs")
    return result


def encode(document):
    payload = transform(document, False)
    return {"schema": SCHEMA, "original_sha256": hashlib.sha256(canonical(document)).hexdigest(),
            "payload": payload}


def decode(compact):
    require(type(compact) is dict
            and set(compact) == {"schema", "original_sha256", "payload"},
            "invalid compact envelope")
    require(compact["schema"] == SCHEMA, "unsupported encoding")
    result = transform(compact["payload"], True)
    require(hashlib.sha256(canonical(result)).hexdigest() == compact["original_sha256"],
            "reconstructed document digest differs")
    return result


def events(compact):
    """Yield legacy consumer records after complete envelope validation."""
    document = decode(compact)
    for rec in document["recipes"]:
        for index, child in enumerate(rec["idle_children"]):
            yield rec["port"], index, child


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("encode", "decode", "events"))
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    with args.input.open("rb") as handle:
        value = parse(handle.read(MAX_BYTES + 1))
    if args.operation == "encode":
        output = canonical(encode(value)) + b"\n"
    elif args.operation == "decode":
        output = canonical(decode(value)) + b"\n"
    else:
        output = b"".join(canonical(event) + b"\n" for event in events(value))
    written = sys.stdout.buffer.write(output)
    require(written == len(output), "incomplete output write")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, OSError, RecursionError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2) from error
