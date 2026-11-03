#!/usr/bin/env python3
"""Exact source-bound audit of coarse rounding in the P104 shared prefix.

Interpret only the authenticated old eighteen ADDs and our local replacement.
The suffix and all predecessor checkers remain unexecuted. Tables for the new
program end before CLEAR; its zero precondition is recorded, never assumed.
"""

import argparse
from collections import Counter
import gzip
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_HASH = "1b680642e59f1c72fb6cbdf05de48a335bc25f7895ca53fe35f0c51719a7e1ee"
CASES_HASH = "a11f84b9e0e8eea4f0dd9f96b37327a04ef6eb9f84f02594b5a7b8c0ab462695"
DESTINATIONS = [119, 169, 191, 193, 204, 206]
SOURCES = [471, 525, 704]
OWNED = 770
COEFFICIENTS = {"1": (1, 1), "1/2": (1, 2), "2": (2, 1),
                "-1": (-1, 1), "-1/2": (-1, 2), "-2": (-2, 1)}


class CheckFailure(Exception):
    """An explicit check failed, including in optimized Python."""


def require(condition, message):
    if not condition:
        raise CheckFailure(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise CheckFailure("nonfinite JSON number: " + value)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def same_typed(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (left.keys() == right.keys()
                and all(same_typed(left[k], right[k]) for k in left))
    if isinstance(left, list):
        return len(left) == len(right) and all(same_typed(a, b) for a, b in zip(left, right))
    return left == right


def authenticate_sources():
    path = ROOT / "SOURCE-PINS.json"
    require(digest(path.read_bytes()) == SOURCE_HASH, "source manifest hash")
    manifest = load_json(path)
    files = manifest.get("files")
    require(type(files) is list and len(files) == 5, "five inert source objects")
    for item in files:
        rel = item.get("local_path")
        require(type(rel) is str and rel.startswith("inputs/"), "source path")
        source = (ROOT / rel).resolve()
        require(source.parent == (ROOT / "inputs").resolve(), "source containment")
        data = source.read_bytes()
        require(type(item.get("bytes")) is int and len(data) == item["bytes"],
                "source length: " + rel)
        require(digest(data) == item.get("sha256"), "source SHA256: " + rel)
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == item.get("git_blob"), "source Git blob")
    case_path = ROOT / "CASES.json"
    require(digest(case_path.read_bytes()) == CASES_HASH, "case manifest hash")
    return manifest


def inspect_word():
    data = (ROOT / "inputs" / "WORD.json.gz").read_bytes()
    require(len(data) == 91086 and digest(data)
            == "25b350a56ce11436fccf4c987da466cb002fa28dfc9b7e9d88e8b1b748b79df3",
            "actual source compressed word")
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
        raw = stream.read(4000001)
    require(len(raw) <= 4000000, "bounded inert JSON decompression")
    word = json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)
    expected = [["ADD", d, s, c, 3] for d in DESTINATIONS
                for s, c in zip(SOURCES, ["1", "1/2", "2"])]
    require(same_typed(word["program"][:18], expected), "literal eighteen ADD prefix")
    require(all(word["initial"][r] == 3 for r in DESTINATIONS + SOURCES), "entry frames")
    require(word["frames"][3] == [], "empty native-label frame")
    require(word["public"] == 770 and word["owned_fields"] == 29, "source role metadata")
    first = next((i, event) for i, event in enumerate(word["program"])
                 if OWNED in event[1:-1])
    require(first == (8448, ["INIT", OWNED, 737]), "owned slot first source use")
    binding = {"prefix": word["program"][:18], "public_entry_frames":
               [[r, word["initial"][r]] for r in DESTINATIONS + SOURCES],
               "frame_3": word["frames"][3], "public_count": word["public"],
               "owned_fields": word["owned_fields"], "program_events": len(word["program"]),
               "first_owned_occurrence_zero_based": first[0], "first_owned_event": first[1],
               "suffix_executed": False, "decompressed_sha256": digest(raw)}
    return word["program"][:18], binding


def replacement():
    return ([["INIT", OWNED, 3]]
            + [["ADD", OWNED, s, c, 3] for s, c in zip(SOURCES, ["1", "1/2", "2"])]
            + [["ADD", d, OWNED, "1", 3] for d in DESTINATIONS]
            + [["ADD", OWNED, s, c, 3] for s, c in zip(reversed(SOURCES), ["-2", "-1/2", "-1"])]
            + [["CLEAR", OWNED, 3]])


def nearest_even(numerator, denominator):
    require(type(numerator) is int and type(denominator) is int and denominator > 0,
            "integer rational rounding arguments")
    lower, remainder = divmod(numerator, denominator)
    return lower + int(2 * remainder > denominator
                       or (2 * remainder == denominator and lower % 2 == 1))


def clear_owned(registers):
    require(OWNED in registers and type(registers[OWNED]) is int and registers[OWNED] == 0, "CLEAR requires owned zero")
    del registers[OWNED]


def add(registers, event, mode, tape):
    _, destination, source, coefficient, frame = event
    require(destination != source and frame == 3, "local ADD roles/frame")
    numerator, denominator = COEFFICIENTS[coefficient]
    updated = denominator * registers[destination] + numerator * registers[source]
    if mode == "nearest_even":
        value = nearest_even(updated, denominator)
    elif mode == "fine_exact":
        require(updated % denominator == 0, "h/2 grid exactness")
        value = updated // denominator
    elif mode == "stochastic":
        lower, remainder = divmod(updated, denominator)
        require(remainder == 0 or 2 * remainder == denominator, "only half ties")
        value = lower if remainder == 0 else lower + next(tape)
    else:
        raise CheckFailure("unknown rounding mode")
    registers[destination] = value


def execute(events, x, y, z, destinations, mode="nearest_even", coins=()):
    values = [x, y, z] + list(destinations)
    require(len(destinations) == 6 and all(type(v) is int for v in values), "integer grid inputs")
    scale = 2 if mode == "fine_exact" else 1
    registers = dict(zip(SOURCES + DESTINATIONS, [scale * v for v in values]))
    initial_sources = [registers[r] for r in SOURCES]
    tape = iter(coins)
    for event in events:
        if event[0] == "ADD":
            add(registers, event, mode, tape)
        elif event[0] == "INIT":
            require(event == ["INIT", OWNED, 3] and OWNED not in registers, "zero-owned INIT")
            registers[OWNED] = 0
        elif event[0] == "CLEAR":
            require(event == ["CLEAR", OWNED, 3], "local CLEAR frame")
            clear_owned(registers)
        else:
            raise CheckFailure("unexpected prefix instruction")
    require([registers[r] for r in SOURCES] == initial_sources, "source preservation")
    require(next(tape, None) is None, "all and only declared rounding coins consumed")
    return [registers[r] for r in DESTINATIONS], registers.get(OWNED)


def parity_cases():
    return [(x, y, list(d)) for x in range(2) for y in range(4)
            for d in itertools.product(range(2), repeat=6)]


def deterministic_row(old, new, x, y, destinations, z=0):
    before, _ = execute(old, x, y, z, destinations)
    after, residual = execute(new[:-1], x, y, z, destinations)
    targets_twice = [2 * d + 2 * x + y + 4 * z for d in destinations]
    delta = [a - b for a, b in zip(after, before)]
    xi = (x + y // 2) % 2
    expected_delta = [0 if y % 2 == 0 or d % 2 == 0 else 2 * xi - 1 for d in destinations]
    expected_residual = 0 if y % 2 == 0 or x % 2 == 0 else (1 if (y // 2) % 2 == 0 else -1)
    require(delta == expected_delta and residual == expected_residual, "parity laws")
    clear_ok = residual == 0
    return {"case": [x, y] + destinations, "old_public": before, "shared_public": after,
            "old_error_twice": [2 * v - t for v, t in zip(before, targets_twice)],
            "shared_error_twice": [2 * v - t for v, t in zip(after, targets_twice)],
            "public_delta": delta, "cleanup_residue": residual,
            "public_equal": before == after, "clear_ok": clear_ok,
            "legal_equivalent": before == after and clear_ok}


def deterministic_tables(old, new):
    rows = []
    for x, y, destinations in parity_cases():
        rows.append(deterministic_row(old, new, x, y, destinations))
        exact_old, _ = execute(old, x, y, 0, destinations, mode="fine_exact")
        exact_new, residual = execute(new, x, y, 0, destinations, mode="fine_exact")
        target = [2 * d + 2 * x + y for d in destinations]
        require(exact_old == exact_new == target and residual is None, "h/2 positive control")
    counts = {"classes": len(rows), "public_different": sum(not r["public_equal"] for r in rows),
              "nonzero_owned": sum(not r["clear_ok"] for r in rows),
              "both_failures": sum(not r["public_equal"] and not r["clear_ok"] for r in rows),
              "legal_equivalent": sum(r["legal_equivalent"] for r in rows)}
    require(counts == {"classes": 512, "public_different": 252, "nonzero_owned": 128,
                       "both_failures": 126, "legal_equivalent": 258}, "complete parity classification")
    return rows, counts


def stochastic_tables(old, new):
    rows = []
    for bits in itertools.product(range(2), repeat=8):
        before, _ = execute(old, 1, 1, 0, [0] * 6, "stochastic", bits[:6])
        after, residual = execute(new[:-1], 1, 1, 0, [0] * 6, "stochastic", bits[6:])
        old_error = [2 * v - 3 for v in before]
        shared_error = [2 * v - 3 for v in after]
        require(old_error == [2 * c - 1 for c in bits[:6]], "old independent coin law")
        require(shared_error == [2 * bits[6] - 1] * 6, "shared preparation coin law")
        require(residual == bits[6] + bits[7] - 1, "fresh inverse residual law")
        rows.append({"coins": list(bits), "old_public": before, "shared_public": after,
                     "old_error_twice": old_error, "shared_error_twice": shared_error,
                     "cleanup_residue": residual, "clear_ok": residual == 0})
    return rows


def rational(numerator, denominator):
    divisor = math.gcd(numerator, denominator)
    return [numerator // divisor, denominator // divisor]


def covariance(rows, left, right, left_index, right_index):
    n = len(rows)
    xs = [r[left][left_index] for r in rows]
    ys = [r[right][right_index] for r in rows]
    return rational(n * sum(x * y for x, y in zip(xs, ys)) - sum(xs) * sum(ys), 4 * n * n)


def stochastic_moments(rows):
    n = len(rows)
    old = [[covariance(rows, "old_error_twice", "old_error_twice", i, j)
            for j in range(6)] for i in range(6)]
    shared = [[covariance(rows, "shared_error_twice", "shared_error_twice", i, j)
               for j in range(6)] for i in range(6)]
    residue = [r["cleanup_residue"] for r in rows]
    cross = [rational(n * sum(r["shared_error_twice"][i] * r["cleanup_residue"] for r in rows)
                      - sum(r["shared_error_twice"][i] for r in rows) * sum(residue), 2 * n * n)
             for i in range(6)]
    variance = rational(n * sum(v * v for v in residue) - sum(residue) ** 2, n * n)
    require(old == [[[1, 4] if i == j else [0, 1] for j in range(6)] for i in range(6)], "old covariance")
    require(shared == [[[1, 4] for _ in range(6)] for _ in range(6)], "shared covariance")
    require(cross == [[1, 4]] * 6 and variance == [1, 2], "cleanup joint moments")
    return {"coin_cases": n, "old_covariance": old, "shared_covariance": shared,
            "shared_cleanup_covariance": cross, "cleanup_variance": variance,
            "cleanup_histogram": sorted(map(list, Counter(residue).items()))}


def expect_reject(callback, name):
    try:
        callback()
    except (CheckFailure, json.JSONDecodeError):
        return name
    raise CheckFailure("control failed to reject: " + name)


def extra_controls(old, new):
    probes = []
    matched = 0
    for x, y, destinations in parity_cases():
        for shift in [0, 1]:
            xx = x - 8 if shift == 0 else x + 2 ** 20
            yy = y - 12 if shift == 0 else y - 4 * 2 ** 20
            zz = -7 if shift == 0 else 2 ** 20
            dd = [d + (2 * (j - 3) if shift == 0 else 2 ** 20 + 2 * j)
                  for j, d in enumerate(destinations)]
            probes.append(deterministic_row(old, new, xx, yy, dd, zz))
        prepared_increment = nearest_even(2 * x + y, 2) - x
        temp = x + prepared_increment
        temp -= prepared_increment
        temp -= x
        require(temp == 0, "recorded/recomputed actual increment restores")
        matched += 1
    rejected = [expect_reject(lambda: clear_owned({OWNED: 1}), "nonzero CLEAR"),
                expect_reject(lambda: clear_owned({}), "inactive CLEAR"),
                expect_reject(lambda: execute(new, 1, 1, 0, [0] * 6), "actual nonzero-CLEAR trace")]
    require(nearest_even(3, 2) == 2 and 1 + nearest_even(1, 2) == 1, "whole-sum versus rounded increment")
    require(nearest_even(-3, 2) == -2 and -(3 // 2) == -1, "signed tie versus truncation")
    require(nearest_even(1, 2) == 0 and (1 + 1) // 2 == 1, "nearest-even versus ties upward")
    for forward in range(2):
        require(forward + (1 - forward) - 1 == 0, "complemented inverse restores")
        require(abs(forward + forward - 1) == 1, "reused-same-up-bit fails")
    require(not same_typed({"x": 1}, {"x": True}) and not same_typed({"x": 1}, {"x": 1.0}), "strict number types")
    rejected += [expect_reject(lambda: json.loads('{"x":1,"x":2}', object_pairs_hook=unique_object), "duplicate JSON"),
                 expect_reject(lambda: json.loads('NaN', parse_constant=reject_constant), "nonfinite JSON")]
    return {"signed_large_probes": len(probes), "signed_large_rows_sha256": digest(json.dumps(probes, sort_keys=True).encode()),
            "recorded_or_recomputed_increment_restorations": matched, "rejection_controls": rejected,
            "same_up_bit_nonzero_cases": 2, "complemented_inverse_zero_cases": 2}


def compute():
    authenticate_sources()
    old, binding = inspect_word()
    new = replacement()
    clear_witness = deterministic_row(old, new, 1, 1, [0] * 6)
    public_witness = deterministic_row(old, new, 0, 1, [1] * 6)
    require(clear_witness["public_equal"] and not clear_witness["clear_ok"], "first cleanup falsification")
    require(public_witness["public_delta"] == [-1] * 6 and public_witness["clear_ok"], "first public falsification")
    deterministic, counts = deterministic_tables(old, new)
    stochastic = stochastic_tables(old, new)
    return {"schema_version": 1, "source_manifest_sha256": SOURCE_HASH,
            "case_manifest_sha256": CASES_HASH, "code_sha256": digest(Path(__file__).read_bytes()),
            "source_binding": binding, "replacement": new,
            "first_falsification": {"cleanup": clear_witness, "public": public_witness},
            "deterministic_rows": deterministic, "deterministic_counts": counts,
            "stochastic_rows": stochastic, "stochastic_moments": stochastic_moments(stochastic),
            "positive_control": {"exact_half_grid_classes": 512, "all_public_equal": True,
                                 "all_owned_clear_legal": True},
            "controls": extra_controls(old, new)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--artifact", type=Path, default=ROOT / "RESULT.json")
    arguments = parser.parse_args()
    result = compute()
    if arguments.emit is not None:
        arguments.emit.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        require(same_typed(load_json(arguments.emit), result), "emitted typed receipt")
    else:
        require(same_typed(load_json(arguments.artifact), result), "retained receipt exact types/keys/values")
    print(json.dumps({"status": "pass", "deterministic_classes": 512, "coin_vectors": 256,
                      "signed_large_probes": 1024, "pre_clear_tables": True}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (CheckFailure, ValueError, OSError, KeyError, TypeError, StopIteration) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
