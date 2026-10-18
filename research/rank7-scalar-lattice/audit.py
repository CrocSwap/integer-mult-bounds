# SPDX-License-Identifier: Apache-2.0
"""Separate fixed-integer free-word interpreter. No Fraction propagation."""

import gzip
import json
import sys
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


def exact_divide(value, denominator, event):
    check(
        denominator != 0 and value % denominator == 0,
        f"nonintegral encoded coefficient at event {event}",
    )
    return value // denominator


def integer_scalar(state, op, index):
    key = tuple(op[1])
    if op[0] == "clear":
        state[key] = {}
    elif op[0] == "copy":
        state[key] = state[tuple(op[2])].copy()
    elif op[0] == "scale":
        state[key] = {
            k: exact_divide(v * op[2], op[3], index) for k, v in state[key].items()
        }
    else:
        check(op[0] == "add", "audit scalar kind")
        target = state.setdefault(key, {})
        for k, value in state[tuple(op[2])].items():
            delta = exact_divide(value * op[3], op[4], index)
            total = target.get(k, 0) + delta
            if total:
                target[k] = total
            else:
                target.pop(k, None)
    return key


def execute(events, fraction_bits, backward, inputs=632):
    check(0 <= fraction_bits <= 16 and len(events) <= 30_000, "audit bounds")
    check(1 <= inputs <= 632, "audit input count")
    unit = 1 << fraction_bits
    state = {("L", i): {(i, ()): unit} for i in range(inputs)}
    largest = unit
    for index, event in enumerate(events):
        kind = event[0]
        if kind == "zero_buffer":
            key = "Z", event[2]
            if event[1] == "alloc":
                check(key not in state, "audit unique allocation")
                state[key] = {}
            else:
                check(state[key] == {}, "audit clean free")
                del state[key]
            continue
        if kind == "warp":
            key, op = tuple(event[1]), event[2]
            new = {}
            for (variable, word), value in state[key].items():
                tail = word[:-1] if word and word[-1] == -op else (*word, op)
                new[variable, tail] = value
            state[key] = new
        elif kind == "scalar":
            key = integer_scalar(state, event[1], index)
        else:
            check(
                kind in ("phase", "climb", "center", "adapter", "residual_adapter"),
                "audit event kind",
            )
            continue
        check(len(state[key]) <= 4096, "audit row bound")
        largest = max(largest, sum(map(abs, state[key].values())))
    endpoints(state, inputs, unit, backward)
    return largest // unit if largest % unit == 0 else f"{largest}/{unit}"


def endpoints(state, inputs, unit, backward):
    for i in range(inputs):
        expected = {(i, ()): unit}
        if inputs == 632 and backward and i < 112:
            expected[i + 112, ()] = -unit
        elif inputs == 632 and not backward and 112 <= i < 224:
            expected[i - 112, ()] = unit
        check(state["L", i] == expected, "audit full endpoint")
    check(
        all(not row for key, row in state.items() if key[0] != "L"),
        "audit private endpoints",
    )


def run(directory):
    result = {}
    for provider in ("base", "extra"):
        path = directory / provider / "LOCAL-PROGRAMS.json.gz"
        check(path.stat().st_size <= 8_000_000, "audit compressed bound")
        with gzip.open(path) as stream:
            raw = stream.read(8_000_001)
        check(len(raw) <= 8_000_000, "audit decoded bound")
        programs = json.loads(raw)
        result[provider] = {}
        for name, bits, mass in (("forward", 4, 302), ("backward", 5, 169)):
            events = programs[name]
            measured = execute(events, bits, name == "backward")
            check(measured == mass, "independent coefficient norm")
            try:
                execute(events, bits - 1, name == "backward")
            except ValueError as error:
                check(
                    str(error).startswith("nonintegral encoded coefficient"),
                    "precision rejection reason",
                )
                rejection = str(error)
            else:
                raise ValueError("one fewer fractional bit was accepted")
            result[provider][name] = {
                "fraction_bits": bits,
                "max_l1": measured,
                "one_fewer_bit": rejection,
            }
    return result


if __name__ == "__main__":
    print(json.dumps(run(Path(sys.argv[1])), sort_keys=True, indent=2))
