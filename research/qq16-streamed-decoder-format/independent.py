#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate explicit-depth integer/dyadic capacity recurrence. No primary imports."""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, msg):
    if not ok:
        raise ValueError(msg)


def reduce(n, e):
    if not n:
        return 0, 0
    while e > 0 and n % 2 == 0:
        n //= 2
        e -= 1
    return n, e


def add(a, b):
    e = max(a[1], b[1])
    return reduce((a[0] << (e-a[1])) + (b[0] << (e-b[1])), e)


def times(a, n, e=0):
    return reduce(a[0]*n, a[1]+e)


def text(a):
    return str(a[0]) if a[1] == 0 else str(a[0]) + "/" + str(1 << a[1])


def greater(a, b):
    return (a[0] << b[1]) > (b[0] << a[1])


def read_word():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for row in pins["files"]:
        if row["usage"] == "input":
            check(hashlib.sha256((ROOT/row["path"]).read_bytes()).hexdigest() == row["sha256"],
                  "input authentication")
    raw = (ROOT / "research/qq16-streaming-recovery/WORD.json").read_bytes()
    return json.loads(raw)


def run(word, depth):
    check(type(depth) is int and depth >= 1, "positive depth")
    fields = {s+str(i): ((1, 0), 0) for s in ("X", "Y") for i in range(112)}
    owned = {s+str(i) for s in ("Z", "W") for i in range(112)}
    active = set()
    highest, guard, trace = (1, 0), 0, []

    def see(i, label, pair):
        nonlocal highest, guard
        value, g = pair
        if greater(value, highest):
            highest = value
        guard = max(guard, g if value[0] else 0)
        trace.append([i, label, text(value), g if value[0] else 0])

    for i, event in enumerate(word):
        kind = event[0]
        if kind == "begin":
            check(not active, "private overlap")
            active = {s+str(j) for s in ("F", "G")[:event[2]//8] for j in range(8)}
        elif kind == "end":
            check(all(fields.get(n) == ((0, 0), 0) for n in active), "private return")
            for n in active:
                del fields[n]
            active = set()
        elif kind == "checkpoint":
            check(not active, "private checkpoint")
        else:
            target = event[1]
            check(target in owned | active, "borrowed write")
            if kind == "clear":
                fields[target] = ((0, 0), 0)
                see(i, "clear", fields[target])
            elif kind == "add":
                source = event[2]
                check(source != target and source in fields and target in fields, "ADD input")
                c = event[3]
                check(c in ("1", "-1", "1/4", "-1/4"), "scalar")
                quarter = 2 if "/" in c else 0
                magnitude, g = fields[source]
                see(i, "product-copy", fields[source])
                term = (times(magnitude, 1, quarter), g+quarter) if magnitude[0] else ((0, 0), 0)
                see(i, "product-result", term)
                old, go = fields[target]
                grid = max(go, term[1]) if old[0] and term[0][0] else go if old[0] else term[1]
                fields[target] = add(old, term[0]), grid
                see(i, "add", fields[target])
            elif kind == "map":
                check(not active and target in fields, "map input")
                see(i, "cover-map", fields[target])
            elif kind == "line":
                check(not active and target in fields, "line input")
                see(i, "right-monomial", fields[target])
                for _ in range(depth):
                    value, g = fields[target]
                    see(i, "native-pair", (times(value, 2), g))
                    see(i, "native-cross", (times(value, 4), g))
                    fields[target] = (times(value, 2), g+1) if value[0] else ((0, 0), 0)
                    see(i, "native-output", fields[target])
                see(i, "left-monomial", fields[target])
            else:
                raise ValueError("unknown operation")
    check(not active and all(n in fields for n in owned), "complete outputs")
    digest = hashlib.sha256(json.dumps(trace, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return highest, guard, len(trace), digest


def main():
    word = read_word()
    receipt = json.loads((HERE / "RESULT.json").read_text())
    expected_counts = Counter(e[0] for e in word)
    check(all(receipt["counts"][k] == v for k, v in expected_counts.items()), "event inventory")
    for depth in (1, 2, 3, 8, 32):
        peak, guard, count, digest = run(word, depth)
        check(guard == 9+3*(depth-1), "depth grid")
        check(not greater(peak, (171043 << (3*(depth-1)), 0)), "polynomial range")
        if depth == 1:
            check(text(peak) == receipt["peak_polynomial_at_one"] and count == receipt["observations"],
                  "one-layer capacity")
            check(digest == receipt["one_layer_capacity_sha256"], "every one-layer observation")
        print("depth", depth, "guard", guard, "range", text(peak), "observations", count)
    # Independent inventory of the declared direct numeric protocol.
    adds = sum(e[0] == "add" for e in word)
    neg = sum(e[0] == "add" and e[3].startswith("-") for e in word)
    quarter = sum(e[0] == "add" and "/" in e[3] for e in word)
    fixed = 2*adds + 2*adds + 2*neg + 2*quarter + 2*expected_counts["clear"]
    fixed += 2*expected_counts["line"]*4 + 2
    check([fixed, 10*expected_counts["line"]] == receipt["decoder_wordops_per_N"], "numeric bill")
    fused = 2*adds + 2*quarter + 2*expected_counts["clear"]
    fused += 12*expected_counts["line"] + 4*expected_counts["map"]
    check(fused == receipt["pr4109_fused_reference_fixed_with_covers_per_N"] == 12352,
          "published fused protocol")
    check(fixed+4*expected_counts["map"]-fused == receipt["protocol_difference_fixed_per_N"] == 7082,
          "explicit protocol difference")
    p = json.loads((ROOT/"research/qq16-all-depth-producer-grid/RESULT.json").read_text())
    check(p["grid_intercept_at_one"] + 9 == receipt["composed_grid_intercept"], "composed grid")
    check(p["range_bits_at_one"] + p["grid_intercept_at_one"] + 9 + 18 + 1
          == receipt["composed_width_offset"], "composed signed width")
    check(p["range_slope"] + p["grid_slope"] + 3 + 3 == receipt["composed_width_slope"],
          "composed width slope")
    print("PASS_QQ16_DECODER_EXPLICIT_DEPTHS_AND_NUMERIC_BILL")


if __name__ == "__main__":
    main()
