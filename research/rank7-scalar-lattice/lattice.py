# SPDX-License-Identifier: Apache-2.0
"""Exact envelopes in the emitted free-monomial scalar reference model."""

import hashlib
import json
from fractions import Fraction as Q

MAX_EVENTS = 30_000
MAX_ROLES = 768
MAX_TERMS = 4096
MAX_WORD = 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def denominator_bits(q):
    d = q.denominator
    require(d > 0 and d & (d - 1) == 0, "dyadic coefficient")
    return d.bit_length() - 1


def role(raw):
    require(type(raw) is list and len(raw) == 2, "role shape")
    tag, index = raw
    require(tag in ("L", "C", "Z") and type(index) is int, "role type")
    require(0 <= index < MAX_ROLES, "role index")
    return tag, index


def signature(row):
    return [[i, list(word), str(q)] for (i, word), q in sorted(row.items())]


def inspect_row(row, event, destination):
    require(len(row) <= MAX_TERMS, "bounded symbolic row")
    if not row:
        return 0, Q(0), None
    grid = max(denominator_bits(q) for q in row.values())
    require(grid <= 256, "bounded fractional precision")
    mass = sum(map(abs, row.values()), Q(0))
    require(mass <= 2**192, "bounded coefficient magnitude")
    key = next(key for key, q in row.items() if denominator_bits(q) == grid)
    witness = {
        "event": event,
        "role": list(destination),
        "input": key[0],
        "warp_word": list(key[1]),
        "coefficient": str(row[key]),
    }
    return grid, mass, witness


def apply_scalar(state, op):
    require(type(op) is list and 2 <= len(op) <= 5, "scalar shape")
    kind, target = op[0], role(op[1])
    require(kind in ("clear", "copy", "scale", "add"), "scalar kind")
    require(
        len(op) == {"clear": 2, "copy": 3, "scale": 4, "add": 5}[kind], "scalar arity"
    )
    if kind == "clear":
        state[target] = {}
    elif kind == "copy":
        state[target] = dict(state[role(op[2])])
    else:
        a, b = op[3:5] if kind == "add" else op[2:4]
        require(type(a) is int and type(b) is int and b != 0, "rational arguments")
        q = Q(a, b)
        denominator_bits(q)
        if kind == "scale":
            require(q != 0, "nonzero scale")
            state[target] = {key: q * value for key, value in state[target].items()}
        else:
            source = role(op[2])
            require(target != source, "distinct ADD roles")
            row = state.setdefault(target, {})
            for key, value in state[source].items():
                updated = row.get(key, Q(0)) + q * value
                if updated:
                    row[key] = updated
                else:
                    row.pop(key, None)
    return target


def apply_warp(state, event):
    require(len(event) == 5 and type(event[2]) is int and event[2] != 0, "warp shape")
    target, op = role(event[1]), event[2]
    row = {}
    for (index, word), value in state[target].items():
        tail = word[1:] if word and word[0] == -op else (op, *word)
        require(len(tail) <= MAX_WORD, "bounded free warp word")
        row[index, tail] = value
    state[target] = row
    return target


def reference_event(state, event, summary):
    require(type(event) is list and len(event) >= 2, "event shape")
    kind = event[0]
    if kind == "scalar":
        op = event[1]
        require(type(op) is list and len(op) >= 2, "scalar shape")
        if op[0] == "add":
            require(len(op) == 5, "ADD shape")
            q = Q(op[3], op[4])
            source = state[role(op[2])]
            if source:
                d = max(denominator_bits(v) for v in source.values())
                summary["source_guard_bits"] = max(
                    summary["source_guard_bits"], d + denominator_bits(q)
                )
        summary["scalar_events"] += 1
        return apply_scalar(state, op)
    if kind == "warp":
        return apply_warp(state, event)
    if kind == "zero_buffer":
        require(len(event) == 3, "buffer event")
        target = role(["Z", event[2]])
        if event[1] == "alloc":
            require(target not in state, "unique buffer allocation")
            state[target] = {}
            return target
        require(event[1] == "free" and state[target] == {}, "clean buffer return")
        del state[target]
        return None
    require(
        kind in ("phase", "climb", "center", "adapter", "residual_adapter"),
        "non-scalar kind",
    )
    return None


def check_endpoint(state, inputs, backward):
    for i in range(inputs):
        expected = {(i, ()): Q(1)}
        if inputs == 632:
            if backward and i < 112:
                expected[i + 112, ()] = Q(-1)
            elif not backward and 112 <= i < 224:
                expected[i - 112, ()] = Q(1)
        require(state["L", i] == expected, "complete ordinary endpoint")
    require(
        all(not row for key, row in state.items() if key[0] != "L"), "private endpoint"
    )


def analyze(events, inputs=632, backward=False):
    require(type(inputs) is int and 1 <= inputs <= 632, "input count")
    require(type(events) is list and len(events) <= MAX_EVENTS, "event count")
    state = {("L", i): {(i, ()): Q(1)} for i in range(inputs)}
    summary = {
        "fraction_bits": 0,
        "max_l1": "1",
        "grid_witness": None,
        "mass_witness": None,
        "source_guard_bits": 0,
        "scalar_events": 0,
    }
    masses = {key: Q(1) for key in state}
    grids = {key: 0 for key in state}
    max_mass = Q(1)
    row_hashes = []
    for index, event in enumerate(events):
        target = reference_event(state, event, summary)
        require(len(state) <= MAX_ROLES, "bounded live roles")
        if target is None:
            continue
        row = state[target]
        grid, mass, witness = inspect_row(row, index, target)
        grids[target] = max(grids.get(target, 0), grid)
        masses[target] = max(masses.get(target, Q(0)), mass)
        if grid > summary["fraction_bits"]:
            summary["fraction_bits"] = grid
            summary["grid_witness"] = witness
        if mass > max_mass:
            max_mass = mass
            summary["mass_witness"] = {
                "event": index,
                "role": list(target),
                "row_sha256": digest(signature(row)),
            }
        row_hashes.append([index, list(target), digest(signature(row))])
    check_endpoint(state, inputs, backward)
    require(
        summary["source_guard_bits"] <= summary["fraction_bits"],
        "all fractional ADD sources align",
    )
    ceiling = (max_mass.numerator + max_mass.denominator - 1) // max_mass.denominator
    summary.update(
        {
            "max_l1": str(max_mass),
            "integer_headroom_bits": (ceiling - 1).bit_length(),
            "program_sha256": digest(events),
            "row_transcript_sha256": digest(row_hashes),
            "role_fraction_bits_histogram": histogram(grids.values()),
            "role_max_l1_sha256": digest(
                [[list(k), str(v)] for k, v in sorted(masses.items())]
            ),
            "roles": len(masses),
            "complete_endpoint_checked": True,
        }
    )
    return summary


def histogram(values):
    result = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))
