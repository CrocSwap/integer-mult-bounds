#!/usr/bin/env python3
"""Check completed-error majorants for the pinned zero-retention QQ16 word.

Nick Petalas. Apache-2.0. This does not execute native child internals.
"""

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
# Authenticates the exact dependency inventory, not a moving PR or local Git ref.
PREDECESSOR_SHA256 = "e044ecb06d90d138cd580d3f9444f7208ace5adf74963574a6946ca1da90dd22"
MAX_EVENTS = 3823
PORTS = 112
SHAPES = {
    "begin": 3,
    "end": 3,
    "checkpoint": 2,
    "clear": 3,
    "add": 4,
    "line": 4,
    "map": 5,
}
INPUTS = tuple(f"{kind}{port}" for kind in "XY" for port in range(PORTS))
OWNED = tuple(f"{kind}{port}" for kind in "ZW" for port in range(PORTS))
SCRATCH = tuple(f"{kind}{port}" for kind in "FG" for port in range(8))
METRICS = ("P", "J", "K", "add", "line", "map")
ZERO = (Fraction(0),) * len(METRICS)


def require(condition, message):
    """Keep all checks enabled under Python optimization."""
    if not condition:
        raise ValueError(message)


def bounded_read(path, maximum):
    """Reject oversized or external inputs before reading them."""
    require(path.is_file() and not path.is_symlink(), f"missing plain file: {path}")
    require(path.stat().st_size <= maximum, f"oversized input: {path}")
    with path.open("rb") as source:
        payload = source.read(maximum + 1)
    require(len(payload) <= maximum, f"input grew past capacity: {path}")
    return payload


def unique_object(pairs):
    """Reject ambiguous or oversized JSON objects at the receipt boundary."""
    require(
        len(pairs) <= len(INPUTS) + len(OWNED) + len(SCRATCH), "JSON object capacity"
    )
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_word(package):
    """Authenticate retained bytes without importing predecessor code."""
    raw = bounded_read(package / "PREDECESSOR.json", 4096)
    require(hashlib.sha256(raw).hexdigest() == PREDECESSOR_SHA256, "inventory drift")
    inventory = json.loads(raw)
    word = None
    for row in inventory["files"]:  # Three entries, bound by the inventory digest.
        payload = bounded_read(package / row["path"], 1_000_000)
        require(len(payload) == row["size"], "source size drift")
        require(hashlib.sha256(payload).hexdigest() == row["sha256"], "source drift")
        header = f"blob {len(payload)}\0".encode()
        blob = hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()
        require(blob == row["git_blob"], "source Git blob drift")
        if row["path"] == "source/WORD.json":
            word = json.loads(payload)
    require(isinstance(word, list) and len(word) == MAX_EVENTS, "wrong source word")
    return word


def validate_event(event, known, active):
    """Validate one boundary, including dirty state and private lifetime."""
    require(isinstance(event, list) and bool(event), "invalid event")
    op = event[0]
    require(isinstance(op, str) and op in SHAPES, "unknown instruction")
    require(len(event) == SHAPES[op], "invalid instruction shape")
    require(isinstance(event[1], str), "invalid field or scope name")
    if op == "begin":
        require(active is None, "overlapping private scope")
        require(type(event[2]) is int and event[2] in (8, 16), "scratch capacity")
        return (event[1], event[2])
    if op == "end":
        require(
            type(event[2]) is int and (event[1], event[2]) == active,
            "private scope mismatch",
        )
        return None
    if op == "checkpoint":
        require(active is None, "invalid checkpoint")
        return active
    dest = event[1]
    require(dest in OWNED or (dest in SCRATCH and active), "borrowed or illegal write")
    if op == "clear":
        require(isinstance(event[2], str), "invalid CLEAR")
        known.add(dest)
        if dest in SCRATCH:
            require(len(known.intersection(SCRATCH)) <= active[1], "scratch capacity")
    else:
        require(dest in known, "dirty destination before initialization")
    if op == "add":
        require(
            isinstance(event[2], str) and event[2] in known, "uninitialized ADD source"
        )
        require(event[2] != dest, "aliased ADD outside the word contract")
        require(event[3] in ("1", "-1", "1/4", "-1/4"), "ADD alphabet")
    if op == "line":
        require(type(event[2]) is int, "invalid line")
        require(0 <= event[2] < PORTS and type(event[3]) is int, "invalid line port")
        require(event[3] in (-1, 1), "invalid line sign")
    if op == "map":
        require(type(event[2]) is int, "invalid map")
        require(event[2] in (1, 2) and type(event[3]) is int, "invalid map stage")
        require(0 <= event[3] < PORTS and type(event[4]) is bool, "invalid map route")
    return active


def forward(word):
    """Propagate ideal loads and five nonnegative error weights at every cut."""
    require(isinstance(word, list) and 1 <= len(word) <= MAX_EVENTS, "event capacity")
    state = {name: (Fraction(1), *ZERO[1:]) for name in INPUTS}
    known, active = set(INPUTS), None
    cuts, loads = [], []
    for index, event in enumerate(word):
        active = validate_event(event, known, active)
        op = event[0]
        if op in ("begin", "end", "checkpoint"):
            loads.append((Fraction(0), Fraction(0)))
            if op == "end":
                require(
                    all(state.get(name, ZERO) == ZERO for name in SCRATCH),
                    "scratch not exactly cleared at scope exit",
                )
                known.difference_update(SCRATCH)
            continue
        dest = event[1]
        alpha = beta = Fraction(0)
        if op == "clear":
            row = ZERO
        elif op == "add":
            coefficient = abs(Fraction(event[3]))
            before, source = state[dest], state[event[2]]
            alpha, beta = before[0] + coefficient * source[0], 1 + coefficient
            row = tuple(
                a + coefficient * b for a, b in zip(before, source, strict=True)
            )
        else:  # Ideal native lines and affine cover maps are isometries.
            row = state[dest]
            alpha, beta = row[0], Fraction(1)
        if op != "clear":
            values = list(row)
            values[1] += alpha
            values[2] += beta
            values[METRICS.index(op)] += 1
            row = tuple(values)
        require(all(value >= 0 for value in row), "negative triangle majorant")
        state[dest] = row
        cuts.append((index, dest, row))
        loads.append((alpha, beta))
    require(active is None, "unterminated private scope")
    return cuts, loads, state


def reverse_cut(word, loads, stop, target):
    """Independently accumulate prefix impulse weights by an adjoint traversal."""
    weights = {target: Fraction(1)}
    totals = [Fraction(0)] * 5
    for index in range(stop, -1, -1):  # At most MAX_EVENTS instructions per cut.
        event = word[index]
        op = event[0]
        if op not in ("clear", "add", "line", "map"):
            continue
        dest = event[1]
        weight = weights.get(dest, Fraction(0))
        if not weight:
            continue
        if op == "clear":
            del weights[dest]
            continue
        alpha, beta = loads[index]
        totals[0] += weight * alpha
        totals[1] += weight * beta
        totals[("add", "line", "map").index(op) + 2] += weight
        if op == "add":
            source = event[2]
            value = weight * abs(Fraction(event[3]))
            weights[source] = weights.get(source, Fraction(0)) + value
    require(set(weights) <= set(INPUTS), "uncleared initial dirt in adjoint")
    return (sum(weights.values(), Fraction(0)), *totals)


def make_receipt(word):
    """Check all cut metrics and construct a deterministic, exact receipt."""
    cuts, loads, state = forward(word)
    require(len(word) == MAX_EVENTS, "fixture length drift")
    counts = Counter(event[0] for event in word)
    require(
        counts
        == {
            "add": 2704,
            "map": 464,
            "line": 336,
            "clear": 312,
            "begin": 3,
            "end": 3,
            "checkpoint": 1,
        },
        "invoice drift",
    )
    peaks = [Fraction(1), *ZERO[1:]]
    origins = ["input", *([None] * 5)]
    records = []
    for index, field, row in cuts:  # 3816 cuts, each independently checked.
        observed = reverse_cut(word, loads, index, field)
        require(observed == row, f"adjoint disagrees at {index}:{field}")
        for metric, value in enumerate(row):
            if value > peaks[metric]:
                peaks[metric], origins[metric] = value, [index, field]
        records.append([index, field, *map(str, row)])
    require(
        all(state[name] == (Fraction(1), *ZERO[1:]) for name in INPUTS),
        "borrowed input changed",
    )
    total = peaks[1] + peaks[2]
    guard = (total.numerator - 1).bit_length()
    require(total.denominator == 1, "guard assumes an integral threshold")
    require(2 ** (guard - 1) < total <= 2**guard, "guard bracket")
    finals = {name: list(map(str, state[name])) for name in (*OWNED, *SCRATCH)}
    return {
        "schema_version": 1,
        "dependency_head": "efa51a6c7ffec6edd556a98deedfe9deeba65809",
        "events": len(word),
        "cuts": len(cuts),
        "metrics": list(METRICS),
        "counts": dict(sorted(counts.items())),
        "peaks": list(map(str, peaks)),
        "peak_origins": origins,
        "relative_guard_bits": guard,
        "guard_threshold": str(total),
        "cut_certificate": records,
        "final_fields": finals,
    }


def encode_receipt(receipt):
    """Keep each cut on one line so the certificate is practical to inspect."""
    header = dict(receipt)
    cuts = header.pop("cut_certificate")
    require(len(cuts) <= MAX_EVENTS, "receipt capacity")
    prefix = json.dumps(header, indent=2).removesuffix("\n}")
    rows = ",\n".join("    " + json.dumps(cut) for cut in cuts)
    return prefix + ',\n  "cut_certificate": [\n' + rows + "\n  ]\n}\n"


def main():
    """Compare against the committed result, or create a new absent receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", type=Path, help="create a new receipt; never overwrite"
    )
    args = parser.parse_args()
    if args.write is not None:
        require(not args.write.exists(), "refusing to overwrite receipt")
    receipt = make_receipt(load_word(PACKAGE))
    if args.write is not None:
        with args.write.open("x", encoding="utf-8") as output:
            output.write(encode_receipt(receipt))
    else:
        expected = json.loads(
            bounded_read(PACKAGE / "RESULT.json", 2_000_000),
            object_pairs_hook=unique_object,
        )
        actual_json = json.dumps(receipt, sort_keys=True)
        expected_json = json.dumps(expected, sort_keys=True)
        require(actual_json == expected_json, "result certificate drift")
    print(
        "PASS_QQ16_ZERO_RETENTION_DEFECTS cuts=3816 P=32368 J=2919388 "
        "K=199144 guard=22 borrowed_writes=0 no_new_kappa"
    )


if __name__ == "__main__":
    main()
