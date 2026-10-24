#!/usr/bin/env python3
"""Exact owner/phase utilities for terminal QQ16 decoder probes.

Apache-2.0; OpenAI assistance. Phase and owner conventions follow the pinned
QQ16 source and ywz65's qq16-current-frame-consumer/native_support.py.
No predecessor executable is imported; all source data are byte-pinned.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
AXES = tuple(1 << i for i in range(73))
PINS = {
    "certificate.json.gz": "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    "DATA-PHASES.json": "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load_sources():
    result = []
    for name, digest in PINS.items():
        raw = (HERE / "sources" / name).read_bytes()
        need(sha256(raw).hexdigest() == digest, "source pin: " + name)
        result.append(json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw))
    packet, phases = result
    need(len(phases["recipes"]) == 112 and phases["m"] == 73, "native dimensions")
    need(all(r["port"] == p for p, r in enumerate(phases["recipes"])), "port ordering")
    return packet, phases


def bits(x):
    while x:
        low = x & -x
        yield low.bit_length() - 1
        x ^= low


def act(g, x):
    out = 0
    for j in bits(x):
        out ^= g[j]
    return out


@lru_cache(None)
def product(g, h):
    return tuple(act(g, v) for v in h)


def frame(entries):
    result = Counter()
    for axis, coefficient in entries:
        if axis:
            result[axis] = (result[axis] + coefficient) % 4
    return tuple((a, c) for a, c in sorted(result.items()) if c)


@lru_cache(None)
def polynomial(entries):
    linear, quadratic = [0] * 73, [0] * 73
    for axis, c in entries:
        support = tuple(bits(axis))
        for i in support:
            linear[i] = (linear[i] + c) % 4
            if c % 2:
                for j in support:
                    if j > i:
                        quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def completed(stage):
    need(0 <= stage <= 8, "completed stage")
    return frame((a, 1) for a in AXES[:9 + 8 * stage])


def move_frame(f, g, shift=0):
    return frame([(act(g, a), c) for a, c in f] + [(shift, 2)])


def corrected_shift(g, f):
    """Return the actual affine correction, or fail when no translation works."""
    want, got = polynomial(f), polynomial(move_frame(f, g))
    need(want[1] == got[1], "a translation cannot repair a quadratic mismatch")
    delta = tuple((a - b) % 4 for a, b in zip(want[0], got[0]))
    need(all(v in (0, 2) for v in delta), "a translation cannot repair an odd phase")
    shift = sum((v // 2) << i for i, v in enumerate(delta))
    need(polynomial(move_frame(f, g, shift)) == want, "complete affine phase identity")
    return shift


def source_route(phases, stage, port):
    if stage == 0:
        return AXES
    recipe = phases["recipes"][port]
    basis = recipe["idle_children"][0]["orthogonal_axes"][:8]
    swaps = [b ^ AXES[9 + 8 * (stage - 1) + i] for i, b in enumerate(basis)]
    g = tuple(e ^ act(swaps, sum(((e & v).bit_count() % 2) << i
                               for i, v in enumerate(swaps))) for e in AXES)
    need(product(g, g) == AXES, "source route involution")
    need(act(g, recipe["q"]) == recipe["q"], "source route fixes its own port normal")
    return g


def matrix_rows(columns):
    n = len(columns)
    return [sum(((columns[j] >> i) & 1) << j for j in range(n)) for i in range(n)]


def address_action(rows, address):
    return sum(((r & address).bit_count() % 2) << j for j, r in enumerate(rows))


def line_recipe(q, sign):
    """Positive H1 and two literal monomial wrappers; inverse uses T_q C_q."""
    need(0 < q < 512 and sign in (-1, 1), "local signed line")
    pivot = (q & -q).bit_length() - 1
    columns = (q,) + tuple(1 << j for j in range(9) if j != pivot)
    inv = {act(columns, v): v for v in range(512)}
    need(len(inv) == 512, "invertible nine-axis line wrapper")
    return {"rank": 1, "left_rows": matrix_rows(columns),
            "left_offset": 0 if sign == 1 else q,
            "right_rows": matrix_rows(tuple(inv[1 << i] for i in range(9)))}


def line_column(recipe, address):
    middle = address_action(recipe["right_rows"], address)
    a = address_action(recipe["left_rows"], middle) ^ recipe["left_offset"]
    b = address_action(recipe["left_rows"], middle ^ 1) ^ recipe["left_offset"]
    return {a: (1, 1), b: (1, -1)}  # common denominator 2


def sparse_add(target, source, coefficient=Q(1)):
    for key, value in source.items():
        v = target.get(key, Q(0)) + coefficient * value
        if v:
            target[key] = v
        else:
            target.pop(key, None)


def routed(g, row):
    result = {}
    for (variable, h), c in row.items():
        key = variable, product(g, h)
        result[key] = result.get(key, Q(0)) + c
    return {key: c for key, c in result.items() if c}


def scalar_cost(kind, coefficient=Q(1)):
    if kind == "clear":
        return 2
    a, b = abs(coefficient.numerator), coefficient.denominator
    need(a > 0 and not b & (b - 1), "nonzero dyadic coefficient")
    if kind == "add":
        return 2 * (2 + a.bit_length() + a.bit_count() + b.bit_length() - 1)
    need(kind == "scale" and not a & (a - 1), "power-of-two scale")
    return 2 * (abs(a.bit_length() - b.bit_length()) + (coefficient < 0))


def write_json(value, output=None):
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if output is None:
        print(text, end="")
    else:
        Path(output).write_text(text)
