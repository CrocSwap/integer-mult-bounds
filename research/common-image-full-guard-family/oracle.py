#!/usr/bin/env python3
"""Independent binary column-span and literal full-guard oracle.

Credit unpaidmoon6515 and Nick Petalas4807/4275/6694, the retained
rank-one/header lineage and classical orbit-stabilizer counting.
Substantial OpenAI Codex assistance. Apache-2.0. No primary or
predecessor implementation is imported or executed.
"""

import argparse
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
PIN_SHA = "680b0d75e9419b4577dd0710a8c430c512f12f9ae70ba9d0ce6c91acc3fbefc9"
CASE_SHA = "3da07e088ca190dc480ce52aab01c44816d334fe32b82ba88a9787f380e99273"
SCHEMA_SHA = "c01cd12853adcce258701b3d8e56bfff7ba9d370223dcecccc62200ef8bd087a"
COMMON = {"schema_version", "source_manifest_sha256", "case_manifest_sha256", "family", "small_gl", "example"}
FAMILY_KEYS = {"m", "k", "support_histogram", "orbit_numerator", "orbit_denominator", "probability", "header_fiber"}
SMALL_KEYS = {"m", "gl_count", "mask_histogram", "joint_first_k", "record_sha256"}
EXAMPLE_KEYS = {"m", "k", "u", "v_rows", "header_rows", "proper_minors", "joint_probability",
                "single_probability", "product_probability", "ratio", "ratio_gt_one"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha((canonical(value) + "\n").encode())


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def bad_number(value):
    raise ValueError("noninteger JSON number: " + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_float=bad_number, parse_constant=bad_number)


def pair(value):
    return [value.numerator, value.denominator]


def domain(m, k):
    require(type(m) is int and type(k) is int, "dimension/arity must be integers, not bool")
    require(2 <= m <= 16 and 1 <= k <= m, "finite oracle domain is2<=m<=16,1<=k<=m")


def authenticate():
    for name, expected in (("SOURCE-PINS.json", PIN_SHA), ("CASES.json", CASE_SHA), ("SCHEMA.json", SCHEMA_SHA)):
        require(sha((ROOT / name).read_bytes()) == expected, "source/cases/schema digest changed")
    source = parse((ROOT / "SOURCE-PINS.json").read_bytes())
    require(len(source["files"]) == 8, "eight inert source objects required")
    for row in source["files"]:
        raw = (ROOT / row["local_path"]).read_bytes()
        require(len(raw) == row["bytes"] and sha(raw) == row["sha256"], "pinned source bytes changed")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "pinned Git blob changed")
    cases = parse((ROOT / "CASES.json").read_bytes())
    parse((ROOT / "SCHEMA.json").read_bytes())
    return cases


def rank_support_count(m, k):
    """Count actual column-pair options by quotient rank and zero-u support."""
    domain(m, k)
    states = {(0, 0): 1}
    for unused in range(m - 1):
        next_states = defaultdict(int)
        for (rank, zeros), count in states.items():
            next_states[rank, zeros] += count
            next_states[rank, zeros + 1] += count * (1 << (rank + 1))
            outside = (1 << k) - (1 << (rank + 1))
            if outside:
                next_states[rank + 1, zeros + 1] += count * outside
        states = next_states
    histogram = [[zeros, states.get((k - 1, zeros), 0)] for zeros in range(m)]
    unrestricted = {0: 1}
    for unused in range(m - 1):
        after = defaultdict(int)
        for rank, count in unrestricted.items():
            after[rank] += count * (1 << (rank + 1))
            outside = (1 << k) - (1 << (rank + 1))
            if outside:
                after[rank + 1] += count * outside
        unrestricted = after
    denominator = ((1 << m) - 1) * unrestricted.get(k - 1, 0)
    return sum(count for unused, count in histogram), denominator, histogram


def insert(basis, value):
    """Canonical reduced binary row basis, with descending pivot positions."""
    for row in basis:
        value = min(value, value ^ row)
    if not value:
        return basis
    pivot = value.bit_length() - 1
    result = [row ^ value if row & (1 << pivot) else row for row in basis]
    return tuple(sorted(result + [value], reverse=True))


def quotient(value, k):
    mask = (1 << (k - 1)) - 1
    return (value & mask) ^ (mask if value >> (k - 1) else 0)


@lru_cache(maxsize=None)
def literal_next_columns(basis, k):
    return tuple(insert(basis, quotient(column, k)) for column in range(1 << k))


def literal_span_count(m, k):
    domain(m, k)
    require((m, k) == (7, 6), "literal-span fixture is the frozen7,6 case")
    states = {((), 0): 1}
    layers = []
    for unused in range(m - 1):
        after = defaultdict(int)
        for (basis, zeros), count in states.items():
            after[basis, zeros] += count
            for target_basis in literal_next_columns(basis, k):
                after[target_basis, zeros + 1] += count
        states = after
        layers.append(len({basis for basis, unused in states}))
    full = tuple(1 << index for index in reversed(range(k - 1)))
    histogram = [[zeros, states.get((full, zeros), 0)] for zeros in range(m)]
    return {"zero_u_histogram": histogram, "quotient_span_counts_by_layer": layers,
            "full_rank_orbit_count": sum(count for unused, count in histogram)}


def identity(m):
    return tuple(1 << index for index in range(m))


def multiply(left, right):
    rows = []
    for mask in left:
        value = 0
        for index, row in enumerate(right):
            if mask & (1 << index):
                value ^= row
        rows.append(value)
    return tuple(rows)


def inverse(rows):
    m = len(rows)
    values = [row | (1 << (m + index)) for index, row in enumerate(rows)]
    for column in range(m):
        pivot = next((index for index in range(column, m) if values[index] >> column & 1), None)
        if pivot is None:
            return None
        values[column], values[pivot] = values[pivot], values[column]
        for index in range(m):
            if index != column and values[index] >> column & 1:
                values[index] ^= values[column]
    return tuple(value >> m for value in values)


def leading_determinants(rows):
    result = []
    for size in range(1, len(rows)):
        mask = (1 << size) - 1
        result.append(int(inverse(tuple(row & mask for row in rows[:size])) is not None))
    return result


def request(u, covector, m):
    return tuple((1 << index) ^ (covector if u >> index & 1 else 0) for index in range(m))


def independent_covectors(m):
    final = 1 << (m - 1)
    return [final] + [final | (1 << index) for index in range(m - 1)]


def validate_family(u, covectors, m):
    require(type(u) is int and 0 < u < (1 << m), "invalid common image vector")
    require(type(covectors) is list and 1 <= len(covectors) <= m, "invalid covector family size")
    require(all(type(value) is int and 0 < value < (1 << m) for value in covectors), "invalid covector encoding")
    require(all((u & value).bit_count() % 2 == 1 for value in covectors), "kernel is not idempotent")
    require(len(insert_all(covectors)) == len(covectors), "covectors must be independent")


def literal_headers(m):
    require(type(m) is int and m in (2, 3, 4), "literal headers require dimension2,3,4")
    requests = [request(1 << (m - 1), covector, m) for covector in independent_covectors(m)]
    headers, passed, histogram, records = 0, [0] * m, [0] * (1 << m), []
    for rows in itertools.product(range(1 << m), repeat=m):
        back = inverse(rows)
        if back is None:
            continue
        headers += 1
        require(multiply(rows, back) == identity(m) and multiply(back, rows) == identity(m), "header inverse differs")
        outcomes = []
        for original in requests:
            actual = multiply(multiply(rows, original), back)
            outcomes.append(all(leading_determinants(actual)))
        for k in range(1, m + 1):
            passed[k - 1] += int(all(outcomes[:k]))
        mask = sum(int(value) << index for index, value in enumerate(outcomes))
        histogram[mask] += 1
        code = sum(row << (m * index) for index, row in enumerate(rows))
        records.append([code, mask])
    records.sort()
    return {"m": m, "gl_count": headers, "mask_histogram": histogram,
            "joint_first_k": passed, "record_sha256": digest(records)}, records


def special_witness():
    m, u = 7, 1 << 6
    covectors = [u | (1 << index) for index in range(6)]
    validate_family(u, covectors, m)
    idempotents = [tuple(covector if u >> row & 1 else 0 for row in range(m)) for covector in covectors]
    require(len(set(idempotents)) == 6 and len(insert_all(covectors)) == 6, "six distinct independent kernels required")
    for value in idempotents:
        require(multiply(value, value) == value, "kernel is not idempotent")
    require(all(multiply(a, b) != multiply(b, a) for a, b in itertools.combinations(idempotents, 2)),
            "common-image kernels unexpectedly commute")
    minors = [leading_determinants(request(u, value, m)) for value in covectors]
    require(all(all(row) for row in minors), "identity witness full guards fail")
    return {"m": m, "k": 6, "u": u, "v_rows": covectors,
            "header_rows": list(identity(m)), "proper_minors": minors}


def insert_all(values):
    result = ()
    for value in values:
        result = insert(result, value)
    return result


def rejected(function, value):
    try:
        function(value)
    except ValueError:
        return True
    return False


def controls():
    bad = request(2, 2, 3)
    require(leading_determinants(bad) == [1, 0], "first-pivot-only control failed")
    result = {"boolean_dimension_rejected": rejected(lambda m: domain(m, 1), True),
              "unsupported_dimension_rejected": rejected(lambda m: domain(m, 1), 17),
              "zero_arity_rejected": rejected(lambda k: domain(7, k), 0),
              "boolean_arity_rejected": rejected(lambda k: domain(7, k), True),
              "too_many_requests_rejected": rejected(lambda k: domain(7, k), 8),
              "duplicate_json_rejected": rejected(parse, '{"x":1,"x":2}'),
              "nonfinite_json_rejected": rejected(parse, '{"x":NaN}'),
              "float_json_rejected": rejected(parse, '{"x":1.0}'),
              "singular_header_rejected": inverse((1, 1)) is None,
              "first_pivot_only_detected": not all(leading_determinants(bad)),
              "dependent_covectors_rejected": rejected(lambda rows: validate_family(1, rows, 3), [1, 1]),
              "nonidempotent_kernel_rejected": rejected(lambda rows: validate_family(1, rows, 3), [2]),
              "boolean_covector_rejected": rejected(lambda rows: validate_family(1, rows, 3), [True])}
    require(all(type(value) is bool and value for value in result.values()), "oracle control failed")
    return result


def general_linear_count(m):
    states = {0: 1}
    for unused in range(m):
        after = defaultdict(int)
        for rank, count in states.items():
            after[rank] += count * (1 << rank)
            if rank < m:
                after[rank + 1] += count * ((1 << m) - (1 << rank))
        states = after
    return states[m]


def family_rows(cases):
    require(cases["family_cases"] == [[m, k] for m in range(2, 17) for k in range(1, m + 1)],
            "frozen family domain differs")
    rows = []
    for m, k in cases["family_cases"]:
        numerator, denominator, histogram = rank_support_count(m, k)
        gl = general_linear_count(m)
        require(gl % denominator == 0, "header orbit does not have integer fiber")
        probability = Fraction(numerator, denominator)
        if k == 1:
            require(probability == Fraction(3 ** (m - 1), ((1 << m) - 1) * (1 << (m - 1))), "prior marginal mismatch")
        if k == 2:
            prior = Fraction(5 ** (m - 1) - 3 ** (m - 1), ((1 << m) - 1) * ((1 << m) - 2) * (1 << (m - 2)))
            require(probability == prior, "prior4807 binary pair mismatch")
        rows.append({"m": m, "k": k, "support_histogram": [count for unused, count in histogram],
                     "orbit_numerator": numerator, "orbit_denominator": denominator,
                     "probability": pair(probability), "header_fiber": gl // denominator})
    return rows


def make_example(cases, rows):
    example = special_witness()
    for key, expected in cases["example"].items():
        require(example[key] == expected, "explicit example differs from frozen tuple/header")
    row = next(row for row in rows if (row["m"], row["k"]) == (7, 6))
    probability = Fraction(*row["probability"])
    marginal = Fraction(3 ** 6, ((1 << 7) - 1) * (1 << 6))
    product = marginal ** 6
    example.update({"joint_probability": pair(probability), "single_probability": pair(marginal),
                    "product_probability": pair(product), "ratio": pair(probability / product),
                    "ratio_gt_one": probability > product})
    require(example["ratio_gt_one"], "explicit six-event product comparison not positive")
    return example


def generate(cases):
    family = family_rows(cases)
    small, actual_records = [], []
    require(cases["small_gl_dimensions"] == [2, 3, 4], "literal GL domain changed")
    for m in cases["small_gl_dimensions"]:
        profile, records = literal_headers(m)
        small.append(profile)
        actual_records.append({"m": m, "records": records})
        for k, count in enumerate(profile["joint_first_k"], 1):
            row = next(row for row in family if (row["m"], row["k"]) == (m, k))
            require(Fraction(count, profile["gl_count"]) == Fraction(*row["probability"]), "literal GL orbit fraction differs")
    span = literal_span_count(7, 6)
    row = next(row for row in family if (row["m"], row["k"]) == (7, 6))
    require([count for unused, count in span["zero_u_histogram"]] == row["support_histogram"], "actual quotient-span support histogram differs")
    value = {"schema_version": 1, "source_manifest_sha256": PIN_SHA, "case_manifest_sha256": CASE_SHA,
             "family": family, "small_gl": small, "example": make_example(cases, family)}
    diagnostic = {"family_cases": len(family), "complete_headers": sum(row["gl_count"] for row in small),
                  "literal_span": span, "controls": controls(), "receipt_controls": receipt_controls(value),
                  "code_sha256": sha(Path(__file__).read_bytes())}
    return value, diagnostic, {"schema_version": 1, "domains": actual_records}


def nonnegative(value, name):
    require(type(value) is int and value >= 0, name + " must be nonnegative integer, not bool")


def rational(value):
    require(type(value) is list and len(value) == 2 and all(type(item) is int for item in value), "rational needs two integer entries")
    require(value[1] > 0 and pair(Fraction(*value)) == value, "rational must be reduced with positive denominator")


def check_family(rows):
    order = [(m, k) for m in range(2, 17) for k in range(1, m + 1)]
    require(type(rows) is list and len(rows) == len(order), "family length invalid")
    for row, (m, k) in zip(rows, order):
        require(type(row) is dict and set(row) == FAMILY_KEYS, "family record keys invalid")
        for name in FAMILY_KEYS - {"support_histogram", "probability"}:
            nonnegative(row[name], "family " + name)
        require((row["m"], row["k"]) == (m, k), "family order invalid")
        hist = row["support_histogram"]
        require(type(hist) is list and len(hist) == m, "support histogram length invalid")
        for item in hist:
            nonnegative(item, "support histogram count")
        require(sum(hist) == row["orbit_numerator"] and row["orbit_denominator"] > 0 and row["header_fiber"] > 0,
                "orbit count/fiber invalid")
        rational(row["probability"])
        require(Fraction(*row["probability"]) == Fraction(row["orbit_numerator"], row["orbit_denominator"]), "orbit fraction differs")


def check_small(rows):
    require(type(rows) is list and len(rows) == 3, "small GL profile count invalid")
    for row, m in zip(rows, (2, 3, 4)):
        require(type(row) is dict and set(row) == SMALL_KEYS, "small GL keys invalid")
        require(type(row["m"]) is int and row["m"] == m, "small GL dimension invalid")
        nonnegative(row["gl_count"], "GL count")
        for key, size in (("mask_histogram", 1 << m), ("joint_first_k", m)):
            require(type(row[key]) is list and len(row[key]) == size, "small GL histogram length invalid")
            for item in row[key]:
                nonnegative(item, "small GL count")
                require(item <= row["gl_count"], "small GL count exceeds headers")
        require(sum(row["mask_histogram"]) == row["gl_count"], "mask histogram count differs")
        require(type(row["record_sha256"]) is str and len(row["record_sha256"]) == 64
                and all(char in "0123456789abcdef" for char in row["record_sha256"]), "GL record digest invalid")


def check_example(value):
    require(type(value) is dict and set(value) == EXAMPLE_KEYS, "example keys invalid")
    require(type(value["m"]) is int and value["m"] == 7 and type(value["k"]) is int and value["k"] == 6, "example dimension/arity invalid")
    validate_family(value["u"], value["v_rows"], 7)
    require(len(value["v_rows"]) == 6, "example must have six requests")
    require(type(value["header_rows"]) is list and len(value["header_rows"]) == 7
            and all(type(row) is int and 0 <= row < 128 for row in value["header_rows"]), "example header invalid")
    minors = value["proper_minors"]
    require(type(minors) is list and len(minors) == 6, "example minor count invalid")
    require(all(type(row) is list and len(row) == 6 and all(type(v) is int and v in (0, 1) for v in row) for row in minors), "example minors must be binary integers")
    for key in ("joint_probability", "single_probability", "product_probability", "ratio"):
        rational(value[key])
    require(type(value["ratio_gt_one"]) is bool, "example comparison must be bool")


def validate_receipt(value):
    require(type(value) is dict and set(value) == COMMON, "receipt schema keys invalid")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1, "receipt schema_version must be integer1")
    require(value["source_manifest_sha256"] == PIN_SHA and value["case_manifest_sha256"] == CASE_SHA, "receipt source/case binding differs")
    check_family(value["family"])
    check_small(value["small_gl"])
    check_example(value["example"])


def receipt_controls(value):
    mutants = {}
    bad = parse(canonical(value))
    bad["schema_version"] = True
    mutants["boolean_version_rejected"] = bad
    bad = parse(canonical(value))
    del bad["example"]
    mutants["missing_profile_key_rejected"] = bad
    bad = parse(canonical(value))
    bad["extra"] = 1
    mutants["extra_profile_key_rejected"] = bad
    bad = parse(canonical(value))
    bad["family"][0]["support_histogram"][0] = False
    mutants["boolean_histogram_rejected"] = bad
    bad = parse(canonical(value))
    bad["example"]["ratio"][1] = True
    mutants["boolean_rational_rejected"] = bad
    result = {name: rejected(validate_receipt, bad) for name, bad in mutants.items()}
    require(all(result.values()), "strict receipt control failed")
    return result


def check_actual_records(path, expected):
    with gzip.open(path, "rb") as stream:
        raw = stream.read(8388609)
    require(len(raw) <= 8388608, "actual GL record artifact exceeds8MiB")
    value = parse(raw)
    require(type(value) is dict and set(value) == {"schema_version", "domains"}, "actual GL artifact keys invalid")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1, "actual GL artifact version invalid")
    require(type(value["domains"]) is list and len(value["domains"]) == 3, "actual GL artifact domains invalid")
    for row, target in zip(value["domains"], expected["domains"]):
        require(type(row) is dict and set(row) == {"m", "records"}, "actual GL domain keys invalid")
        require(type(row["m"]) is int and row["m"] == target["m"], "actual GL domain order invalid")
        require(type(row["records"]) is list and len(row["records"]) == len(target["records"]), "actual GL record count invalid")
        for record in row["records"]:
            require(type(record) is list and len(record) == 2 and all(type(v) is int for v in record), "actual GL record needs two integers")
            require(0 <= record[0] < (1 << (row["m"] ** 2)) and 0 <= record[1] < (1 << row["m"]), "actual GL record out of range")
    require(canonical(value) == canonical(expected), "actual complete primary GL records differ")
    return {"actual_gl_records_compared": sum(len(row["records"]) for row in value["domains"]),
            "actual_gl_canonical_sha256": digest(value), "decompressed_bytes": len(raw)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--check-primary", type=Path)
    args = parser.parse_args()
    require(not (args.emit and args.check_primary), "blind first emission cannot read primary data")
    cases = authenticate()
    retained = None if args.emit else parse((ROOT / "ORACLE.json").read_bytes())
    if retained is not None:
        validate_receipt(retained)
    value, diagnostics, actual_records = generate(cases)
    validate_receipt(value)
    if args.emit:
        with args.emit.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(canonical(value) == canonical(retained), "retained oracle receipt differs")
    if args.check_primary:
        primary = parse(args.check_primary.read_bytes())
        validate_receipt(primary)
        require(canonical(primary) == canonical(value), "actual complete primary receipt differs")
        diagnostics["primary_data_comparison"] = check_actual_records(args.check_primary.parent / "SMALL-GL.json.gz", actual_records)
    print("PASS_COMMON_IMAGE_FULL_GUARD_ORACLE " + canonical(diagnostics))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL_COMMON_IMAGE_FULL_GUARD_ORACLE: " + str(error), file=sys.stderr)
        sys.exit(1)
