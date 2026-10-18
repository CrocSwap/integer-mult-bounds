# SPDX-License-Identifier: Apache-2.0
"""Exact scalar-prefix formats in a free monomial-word module, not native values."""

import hashlib
import json
from fractions import Fraction as Q

MAX_EVENTS = 30_000
MAX_ATOMS = 4096
MAX_WORD = 256
MAX_REGISTERS = 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def encoded(row):
    return [
        [v, list(w), q.numerator, q.denominator] for (v, w), q in sorted(row.items())
    ]


def depth(row):
    require(len(row) <= MAX_ATOMS, "bounded row support")
    require(all(q.denominator.bit_count() == 1 for q in row.values()), "dyadic row")
    require(
        all(abs(q.numerator).bit_length() <= 256 for q in row.values()),
        "bounded coefficient",
    )
    return max((q.denominator.bit_length() - 1 for q in row.values()), default=0)


def interval(row, precision):
    """Exact extrema when each formal atom is an independent signed P-bit integer."""
    require(type(precision) is int and 2 <= precision <= 128, "input precision")
    positive = sum((q for q in row.values() if q > 0), Q(0))
    negative = sum((-q for q in row.values() if q < 0), Q(0))
    limit = 1 << (precision - 1)
    return -limit * positive - (limit - 1) * negative, (
        limit - 1
    ) * positive + limit * negative


def signed_width(low, high):
    require(low.denominator == high.denominator == 1, "integral endpoints")
    require(low <= high, "ordered endpoints")
    extent = max(int(high) + 1, -int(low), 1)
    return 1 + (extent - 1).bit_length()


def combine(target, source, factor):
    result = target.copy()
    for atom, value in source.items():
        total = result.get(atom, Q(0)) + factor * value
        if total:
            result[atom] = total
        else:
            result.pop(atom, None)
    require(len(result) <= MAX_ATOMS, "bounded combined support")
    return result


def warp(row, operation):
    require(type(operation) is int and operation != 0, "nonzero warp symbol")
    result = {}
    for (variable, word), value in row.items():
        moved = word[1:] if word and word[0] == -operation else (operation,) + word
        require(len(moved) <= MAX_WORD, "bounded reduced word")
        result[variable, moved] = value
    require(len(result) == len(row), "warp is injective on atoms")
    return result


def scalar(state, gate):
    require(gate and gate[0] in ("clear", "copy", "scale", "add"), "scalar kind")
    tag, target = gate[0], tuple(gate[1])
    if tag == "clear":
        require(len(gate) == 2, "clear arity")
        result = {}
    elif tag == "copy":
        require(len(gate) == 3, "copy arity")
        result = state[tuple(gate[2])].copy()
    elif tag == "scale":
        require(len(gate) == 4 and gate[3] != 0 and gate[2] != 0, "scale shape")
        result = {a: q * Q(gate[2], gate[3]) for a, q in state[target].items()}
    else:
        require(len(gate) == 5 and gate[4] != 0, "ADD shape")
        source = tuple(gate[2])
        require(target != source, "distinct ADD ports")
        result = combine(state[target], state[source], Q(gate[3], gate[4]))
    state[target] = result
    require(len(state) <= MAX_REGISTERS, "bounded register inventory")
    return target, result


def prefixes(events, inputs=632):
    """Yield changed rows; transforms without scalar semantics are explicitly skipped."""
    require(type(inputs) is int and 1 <= inputs <= 704, "input inventory")
    require(len(events) <= MAX_EVENTS, "bounded emitted stream")
    state = {("L", r): {(r, ()): Q(1)} for r in range(inputs)}
    for index, event in enumerate(events):
        require(event and isinstance(event[0], str), "event shape")
        tag = event[0]
        if tag == "zero_buffer":
            target = ("Z", event[2])
            if event[1] == "alloc":
                require(target not in state, "fresh zero buffer")
                state[target] = {}
            else:
                require(
                    event[1] == "free" and target in state and not state[target],
                    "zero return",
                )
                del state[target]
            continue
        if tag == "warp":
            target = tuple(event[1])
            state[target] = warp(state[target], event[2])
            yield index, target, state[target], None, None
        elif tag == "scalar":
            gate = event[1]
            source = state[tuple(gate[2])].copy() if gate[0] == "add" else None
            before = state.get(tuple(gate[1]), {}).copy()
            target, row = scalar(state, gate)
            yield index, target, row, before, source
        else:
            require(
                tag in ("phase", "adapter", "residual_adapter", "climb", "center"),
                "known non-scalar event",
            )
    yield len(events), None, state, None, None


def endpoint_check(state, inputs, backward):
    for register, row in state.items():
        if register[0] == "L":
            r = register[1]
            expected = {(r, ()): Q(1)}
            if backward and r < 112:
                expected[r + 112, ()] = Q(-1)
            elif not backward and 112 <= r < 224:
                expected[r - 112, ()] = Q(1)
        else:
            expected = {}
        require(row == expected, "literal scalar endpoint")
    require(sum(r[0] == "L" for r in state) == inputs, "all input columns retained")


def summarize(events, backward=False, precision=64):
    digest = hashlib.sha256()
    result = {
        "fractional_bits": 0,
        "increment_depth": 0,
        "max_norm": Q(1),
        "low": Q(-(1 << (precision - 1))),
        "high": Q((1 << (precision - 1)) - 1),
        "ADDs": 0,
        "rows": 0,
        "max_support": 1,
        "ignored_events": {},
    }
    witnesses = {}
    for index, target, row, before, source in prefixes(events):
        if target is None:
            endpoint_check(row, 632, backward)
            break
        result["rows"] += 1
        d = depth(row)
        norm = sum(map(abs, row.values()), Q(0))
        low, high = interval(row, precision)
        record = {"event": index, "register": list(target), "row": encoded(row)}
        if d > result["fractional_bits"]:
            result["fractional_bits"] = d
            witnesses["depth"] = record
        if norm > result["max_norm"]:
            result["max_norm"] = norm
            witnesses["norm"] = record
        for name, value, improves in (
            ("low", low, low < result["low"]),
            ("high", high, high > result["high"]),
        ):
            if improves:
                result[name] = value
                witnesses[name] = dict(
                    record, before=encoded(before or {}), source=encoded(source or {})
                )
        increment = {}
        if source is not None:
            result["ADDs"] += 1
            gate = events[index][1]
            increment = {a: q * Q(gate[3], gate[4]) for a, q in source.items()}
            result["increment_depth"] = max(result["increment_depth"], depth(increment))
        result["max_support"] = max(result["max_support"], len(row))
        digest.update(
            canonical([index, list(target), encoded(row), encoded(increment)])
        )
        digest.update(b"\n")
    return finish_summary(result, events, witnesses, digest.hexdigest(), precision)


def finish_summary(result, events, witnesses, ledger_hash, precision):
    result["ledger_sha256"] = ledger_hash
    d = result["fractional_bits"]
    require(result["increment_depth"] <= d, "every encoded ADD source is divisible")
    result["signed_width"] = signed_width(result["low"] * 2**d, result["high"] * 2**d)
    norm_extent = result["max_norm"] * (1 << (precision - 1 + d))
    result["symmetric_norm_width"] = signed_width(-norm_extent, norm_extent)
    for event in events:
        if event[0] not in ("scalar", "warp", "zero_buffer", "phase"):
            ignored = result["ignored_events"]
            ignored[event[0]] = ignored.get(event[0], 0) + 1
    for key in ("max_norm", "low", "high"):
        result[key] = str(result[key])
    result["witnesses"] = witnesses
    return result


def triangle_bound(events, precision=64):
    """Cancellation-blind sufficient format control, with the same skipped events."""
    state = {("L", r): (Q(1), 0) for r in range(632)}
    peak, grid = Q(1), 0
    for event in events:
        tag = event[0]
        if tag == "zero_buffer":
            state["Z", event[2]] = (Q(0), 0)
        if tag != "scalar":
            continue
        gate = event[1]
        kind, target = gate[0], tuple(gate[1])
        if kind == "clear":
            value, d = Q(0), 0
        elif kind == "copy":
            value, d = state[tuple(gate[2])]
        elif kind == "scale":
            q = Q(gate[2], gate[3])
            value, old = state[target]
            value, d = abs(q) * value, old + q.denominator.bit_length() - 1
        else:
            q = Q(gate[3], gate[4])
            left, ld = state[target]
            right, rd = state[tuple(gate[2])]
            value, d = (
                left + abs(q) * right,
                max(ld, rd + q.denominator.bit_length() - 1),
            )
        state[target] = value, d
        peak, grid = max(peak, value), max(grid, d)
    extent = peak * (1 << (precision - 1 + grid))
    # A rational conservative extent is rounded outwards before sizing.
    integer_extent = -(-extent.numerator // extent.denominator)
    width = signed_width(Q(-integer_extent), Q(integer_extent))
    return {"fractional_bits": grid, "max_norm": str(peak), "signed_width": width}
