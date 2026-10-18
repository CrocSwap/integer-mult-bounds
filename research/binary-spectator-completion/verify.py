#!/usr/bin/env python3
"""Exact finite interface audit; ywz65 with OpenAI Codex assistance. Apache-2.0."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAX_VOLUME = 262144


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)


def binary_ceiling(n):
    need(type(n) is int and n >= 1, "positive integer cardinality required")
    return 1 << (n - 1).bit_length()


def padded_shape(shape):
    need(type(shape) is tuple and len(shape) == 5, "five complete fields required")
    result = tuple(binary_ceiling(n) for n in shape)
    need(shape[1] == shape[3] and shape[1] >= 2, "equal active fields of size at least two required")
    return result


def pad(payload, shape):
    """One forward genuine-input iterator; dummy cells are owned zeros."""
    target = padded_shape(shape)
    need(math.prod(target) <= MAX_VOLUME, "finite replay capacity exceeded")
    need(len(payload) == math.prod(shape), "incomplete genuine rectangle")
    source = iter(payload)
    output = []
    for coords in itertools.product(*(range(n) for n in target)):
        output.append(next(source) if all(x < n for x, n in zip(coords, shape)) else 0)
    need(next(source, None) is None, "unconsumed genuine input")
    return output, target


def restrict(payload, shape):
    target = padded_shape(shape)
    need(len(payload) == math.prod(target), "incomplete padded rectangle")
    result = []
    for value, coords in zip(payload, itertools.product(*(range(n) for n in target))):
        if all(x < n for x, n in zip(coords, shape)):
            result.append(value)
    return result


def exchange(payload, shape, completed_binary_callee):
    padded, target = pad(payload, shape)
    result = completed_binary_callee(padded, target)
    need(len(result) == len(padded), "callee changed complete volume")
    return restrict(result, shape)


def reference_binary_callee(payload, shape):
    """Slow finite semantic reference, not a claimed fast tape implementation."""
    need(all(n > 0 and n & (n - 1) == 0 for n in shape), "callee received nonbinary field")
    p, q, g, q2, s = shape
    need(q == q2, "unequal binary fields")
    output = [None] * len(payload)
    for index, value in enumerate(payload):
        prefix, rem = divmod(index, q * g * q * s)
        first, rem = divmod(rem, g * q * s)
        gap, rem = divmod(rem, q * s)
        second, suffix = divmod(rem, s)
        target = ((((prefix * q + second) * g + gap) * q + first) * s + suffix)
        output[target] = value
    need(all(value is not None for value in output), "callee endpoint not bijective")
    return output


def oracle(payload, shape):
    """Independent pull oracle: nested tuples, no source-to-target index formula."""
    table = dict(zip(itertools.product(*(range(n) for n in shape)), payload))
    return [table[(p, y, g, x, s)] for p, x, g, y, s in itertools.product(*(range(n) for n in shape))]


def authenticate():
    manifest = read_json(HERE / "SOURCES.json")
    for item in manifest["files"]:
        if item["usage"] == "input":
            data = (ROOT / item["path"]).read_bytes()
            need(hashlib.sha256(data).hexdigest() == item["sha256"], "live source hash mismatch")
    for source in manifest["pending_sources"]:
        for item in source["files"]:
            data = (HERE / item["path"]).read_bytes()
            need(hashlib.sha256(data).hexdigest() == item["sha256"], "pending source hash mismatch")
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            need(blob == item["git_blob"], "pending Git blob mismatch")


def mixed_rank(coords, radices):
    out = 0
    for value, radix in zip(coords, radices):
        out = out * radix + value
    return out


def calculate():
    authenticate()
    cases = 0
    rows = 0
    digest = hashlib.sha256()
    spectra = [(1, 1, 1), (3, 1, 5), (5, 3, 2), (3, 5, 7), (7, 7, 3), (15, 6, 6)]
    for p, g, s in spectra:
        for q in (2, 3, 5, 8, 9):
            shape = (p, q, g, q, s)
            payload = list(range(1, math.prod(shape) + 1))
            actual = exchange(payload, shape, reference_binary_callee)
            expected = oracle(payload, shape)
            need(actual == expected, "completed endpoint mismatch")
            need(exchange(actual, shape, reference_binary_callee) == payload, "row restoration mismatch")
            binary = padded_shape(shape)
            need(math.prod(binary) < 32 * len(payload), "combined constant bound")
            need(binary[0] * binary[2] * binary[4] < 8 * p * g * s, "spectator constant bound")
            digest.update(json.dumps(actual, separators=(",", ":")).encode())
            cases += 1
            rows += len(payload)
    shape = (1, 2, 3, 2, 1)
    for bits in itertools.product((0, 1), repeat=12):
        data = list(bits)
        need(exchange(data, shape, reference_binary_callee) == oracle(data, shape), "Boolean endpoint")
    radices = (3, 2, 5, 3)
    ranked = [mixed_rank(c, radices) for c in itertools.product(*(range(n) for n in radices))]
    need(ranked == list(range(math.prod(radices))), "mixed-radix aggregate order")
    arithmetic_cases = 0
    for p in range(1, 41):
        for g in range(1, 41):
            for s in range(1, 41):
                need(binary_ceiling(p) * binary_ceiling(g) * binary_ceiling(s) < 8 * p * g * s,
                     "all cardinality factor")
                arithmetic_cases += 1
    depth_examples = []
    for depth in (1, 10, 100, 1000):
        genuine = 3 ** depth
        aggregate = binary_ceiling(genuine)
        per_field = 4 ** depth
        need(aggregate < 2 * genuine, "aggregate depth-independent bound")
        if depth >= 10:
            need(per_field > 8 * genuine, "per-field growth witness")
        depth_examples.append({"ternary_fields": depth, "aggregate_binary_bits": aggregate.bit_length()-1,
                               "per_field_binary_bits": 2*depth})
    controls = {}
    shape = (3, 3, 3, 3, 3)
    data = list(range(1, math.prod(shape)+1))
    controls["clean_identity_is_not_exchange"] = exchange(data, shape, lambda x, _: list(x)) != oracle(data, shape)
    padded, target = pad(data, shape)
    first_genuine, first_dummy = 0, shape[4]
    middle = list(padded)
    middle[first_genuine], middle[first_dummy] = middle[first_dummy], middle[first_genuine]
    controls["restriction_before_completed_return_loses_payload"] = sorted(restrict(middle, shape)) != sorted(data)
    middle[first_genuine], middle[first_dummy] = middle[first_dummy], middle[first_genuine]
    need(middle == padded, "internal excursion cleanup positive control")
    controls["gap_not_preserved"] = exchange(data, shape, lambda x, z: list(reversed(reference_binary_callee(x,z)))) != oracle(data, shape)
    controls["direct_nonbinary_call_rejected"] = False
    try:
        reference_binary_callee(data, shape)
    except ValueError:
        controls["direct_nonbinary_call_rejected"] = True
    for name, bad in [("zero_range", (0,3,1,3,1)), ("boolean_range", (True,3,1,3,1)),
                      ("unequal_targets", (1,3,1,4,1)), ("zero_width_target", (1,1,1,1,1))]:
        try:
            padded_shape(bad)
        except ValueError:
            controls[name] = True
        else:
            controls[name] = False
    need(all(controls.values()), "semantic failure control did not reject")
    return {"schema_version":1, "scope":"conditional binary-only spectator completion; no selected admission",
            "symbolic_cases":cases, "symbolic_rows":rows, "symbolic_sha256":digest.hexdigest(),
            "boolean_payload_cases":4096, "mixed_radix_rows":len(ranked),
            "exact_volume_comparisons":arithmetic_cases, "depth_examples":depth_examples,
            "controls":controls, "spectator_volume_factor_strict":8, "combined_volume_factor_strict":32}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = calculate()
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    else:
        expected = read_json(HERE / "RESULT.json")
        need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), "required receipt mismatch")
    print("PASS_BINARY_SPECTATOR_COMPLETION symbolic_cases=" + str(result["symbolic_cases"]) +
          " boolean_payloads=4096 factor_lt_32 no_selected_admission")


if __name__ == "__main__":
    main()
