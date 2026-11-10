#!/usr/bin/env python3
"""Independent integer/polynomial oracle for the credited pair-law sign.

Nick Petalas4807 supplies the joint law, binary sign and released odd-field
question;4227/4261 supply the marginal/header lineage. This program supports
only the new inequality corollary. No predecessor or primary implementation
is read/imported/executed. Substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
PIN_SHA = "2b8bb283881df3bcad005e11fbe3aeaddc61b563babe9dd95c2dd18ae4fdbc59"
CASE_SHA = "a8b26ebc34dbeb7f47b91f88eb0863bb4d6e914a6c26630e8cdd64dfe9ddf61b"
SCHEMA_SHA = "70db0325541f073c41886cf9fb43289723a6394d4c1e82d999dd49cda50507f5"
COMMON = {"schema_version", "source_manifest_sha256", "case_manifest_sha256", "identities", "cases"}
IDENTITIES = {"qD_minus_A2_q": 2, "A_minus_q_t": 3,
              "twoA_minus_q_qplus1_t": 3, "A2_minus_q3_t": 5}
CASE_KEYS = {"q", "n", "marginal", "joint", "ratio", "lower_bound", "positive"}
ORDER = [(q, n) for q in range(2, 17) for n in range(1, 13)]
ORDER += [(q, n) for q in (25, 27, 32, 49, 64) for n in (1, 2, 3, 8, 16)]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, "duplicate JSON key: " + key)
        value[key] = item
    return value


def reject_number(value):
    raise ValueError("noninteger JSON number forbidden: " + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_float=reject_number, parse_constant=reject_number)


def trim(coefficients):
    result = list(coefficients)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def add(left, right):
    result = [0] * max(len(left), len(right))
    for index, coefficient in enumerate(left):
        result[index] += coefficient
    for index, coefficient in enumerate(right):
        result[index] += coefficient
    return trim(result)


def scale(poly, factor):
    return trim([factor * coefficient for coefficient in poly])


def multiply(left, right):
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return trim(result)


def shift(poly, constant):
    result = [0]
    for coefficient in reversed(poly):
        result = add(multiply(result, [constant, 1]), [coefficient])
    return result


def evaluate(poly, value):
    result = 0
    for coefficient in reversed(poly):
        result = result * value + coefficient
    return result


def source_polynomials():
    q, qm1 = [0, 1], [-1, 1]
    a = add(add(multiply(q, q), scale(q, -1)), [1])
    d = add(multiply(q, q), multiply(multiply(qm1, qm1), qm1))
    return q, a, d


def polynomial_identities():
    q, a, d = source_polynomials()
    return {"qD_minus_A2_q": add(multiply(q, d), scale(multiply(a, a), -1)),
            "A_minus_q_t": shift(add(a, scale(q, -1)), 2),
            "twoA_minus_q_qplus1_t": shift(add(scale(a, 2), scale(multiply(q, add(q, [1])), -1)), 2),
            "A2_minus_q3_t": shift(add(multiply(a, a), scale(multiply(multiply(q, q), q), -1)), 2)}


def gcd(left, right):
    left, right = abs(left), abs(right)
    while right:
        left, right = right, left % right
    return left


def reduced(numerator, denominator):
    require(type(numerator) is int and type(denominator) is int, "ratio entries must be integers, not bool")
    require(denominator > 0, "ratio denominator must be positive")
    divisor = gcd(numerator, denominator)
    return [numerator // divisor, denominator // divisor]


def compare(left, right):
    difference = left[0] * right[1] - right[0] * left[1]
    return (difference > 0) - (difference < 0)


def domain(q, n):
    require(type(q) is int and type(n) is int, "q,n must be integers, not bool")
    require((q, n) in ORDER, "unsupported frozen algebra probe")


def proper_path_counts(q, n):
    unused, alpha, delta = source_polynomials()
    a, d = evaluate(alpha, q), evaluate(delta, q)
    single, distinct_pair, qpower = 1, 0, 1
    for unused in range(n):
        distinct_pair, single = d * distinct_pair + (d - a) * single, a * single
        qpower *= q
    return single, distinct_pair, qpower


def algebra_case(q, n):
    domain(q, n)
    single, distinct_pair, qpower = proper_path_counts(q, n)
    x = q * qpower
    pnum, pden = (q - 1) * single, (x - 1) * qpower
    jnum, jden = (q - 1) * distinct_pair, (x - 1) * (x - q) * (qpower // q)
    p, joint = reduced(pnum, pden), reduced(jnum, jden)
    ratio = reduced(jnum * pden * pden, jden * pnum * pnum)
    lower = reduced(q * (x - 1) * (single - qpower), (q - 1) * (x - q) * single)
    require(compare(ratio, lower) > 0 and compare(lower, [1, 1]) >= 0, "strict ratio/lower-bound chain failed")
    require(compare(ratio, [1, 1]) > 0, "positive common-covector correlation failed")
    if n >= 2:
        require(single > x and compare(lower, [1, 1]) > 0, "large-n strict lower bound failed")
    return {"q": q, "n": n, "marginal": p, "joint": joint,
            "ratio": ratio, "lower_bound": lower, "positive": True}


def authenticate():
    for name, expected in (("SOURCE-PINS.json", PIN_SHA), ("CASES.json", CASE_SHA), ("SCHEMA.json", SCHEMA_SHA)):
        require(sha((ROOT / name).read_bytes()) == expected, "source/cases/schema digest changed")
    source = parse((ROOT / "SOURCE-PINS.json").read_bytes())
    require(len(source["files"]) == 2, "two inert4807 source documents required")
    for entry in source["files"]:
        raw = (ROOT / entry["local_path"]).read_bytes()
        require(len(raw) == entry["bytes"] and sha(raw) == entry["sha256"], "pinned source bytes changed")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(blob).hexdigest() == entry["git_blob"], "pinned source Git blob changed")
    parse((ROOT / "SCHEMA.json").read_bytes())
    return parse((ROOT / "CASES.json").read_bytes())


def rational(value):
    require(type(value) is list and len(value) == 2, "rational must be a two-entry list")
    require(all(type(item) is int for item in value), "rational entries must be integers, not bool")
    require(value[1] > 0 and value == reduced(*value), "rational must be reduced with positive denominator")


def validate_receipt(value):
    require(type(value) is dict and set(value) == COMMON, "receipt schema keys invalid")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1, "receipt schema version must be integer1")
    require(value["source_manifest_sha256"] == PIN_SHA and value["case_manifest_sha256"] == CASE_SHA, "receipt source/case binding differs")
    identities = value["identities"]
    require(type(identities) is dict and set(identities) == set(IDENTITIES), "identity keys invalid")
    for name, size in IDENTITIES.items():
        poly = identities[name]
        require(type(poly) is list and len(poly) == size and all(type(c) is int for c in poly), "identity coefficient types/length invalid")
    rows = value["cases"]
    require(type(rows) is list and len(rows) == len(ORDER), "algebra case count invalid")
    for row, (q, n) in zip(rows, ORDER):
        require(type(row) is dict and set(row) == CASE_KEYS, "algebra case keys invalid")
        require(type(row["q"]) is int and type(row["n"]) is int and (row["q"], row["n"]) == (q, n), "algebra case order/domain invalid")
        for key in ("marginal", "joint", "ratio", "lower_bound"):
            rational(row[key])
        require(type(row["positive"]) is bool, "algebra positivity flag must be bool")


def rejected(function, value):
    try:
        function(value)
    except ValueError:
        return True
    return False


def controls(receipt):
    result = {"boolean_q_rejected": rejected(lambda q: domain(q, 1), True),
              "boolean_n_rejected": rejected(lambda n: domain(2, n), True),
              "unsupported_case_rejected": rejected(lambda q: domain(q, 1), 17),
              "zero_n_rejected": rejected(lambda n: domain(2, n), 0),
              "zero_denominator_rejected": rejected(lambda d: reduced(1, d), 0),
              "negative_denominator_rejected": rejected(lambda d: rational([1, d]), -2),
              "unreduced_rational_rejected": rejected(rational, [2, 4]),
              "boolean_rational_rejected": rejected(rational, [True, 1]),
              "duplicate_json_rejected": rejected(parse, '{"x":1,"x":2}'),
              "nonfinite_json_rejected": rejected(parse, '{"x":NaN}'),
              "float_json_rejected": rejected(parse, '{"x":1.0}')}
    for name in ("boolean_version", "missing_key", "extra_key", "boolean_coefficient", "boolean_positive"):
        bad = parse(canonical(receipt))
        if name == "boolean_version":
            bad["schema_version"] = True
        elif name == "missing_key":
            del bad["identities"]
        elif name == "extra_key":
            bad["extra"] = 1
        elif name == "boolean_coefficient":
            bad["identities"]["qD_minus_A2_q"][0] = False
        else:
            bad["cases"][0]["positive"] = 1
        result[name + "_rejected"] = rejected(validate_receipt, bad)
    require(all(type(v) is bool and v for v in result.values()), "oracle control failed")
    return result


def generate(cases):
    require(cases["cases"] == [{"q": q, "n": n} for q, n in ORDER], "frozen case schedule differs")
    value = {"schema_version": 1, "source_manifest_sha256": PIN_SHA, "case_manifest_sha256": CASE_SHA,
             "identities": polynomial_identities(), "cases": [algebra_case(q, n) for q, n in ORDER]}
    validate_receipt(value)
    diagnostic = {"algebra_cases": len(ORDER), "identities": len(IDENTITIES), "controls": controls(value),
                  "code_sha256": sha(Path(__file__).read_bytes()),
                  "scope": "New sign corollary only; source4807 counts and binary sign are prior; nonprimepowers are algebra probes"}
    return value, diagnostic


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--check-primary", type=Path)
    args = parser.parse_args()
    require(not (args.emit and args.check_primary), "blind first emission cannot read primary data")
    cases = authenticate()
    frozen = None if args.emit else parse((ROOT / "ORACLE.json").read_bytes())
    if frozen is not None:
        validate_receipt(frozen)
    value, diagnostic = generate(cases)
    if args.emit:
        with args.emit.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(canonical(value) == canonical(frozen), "retained oracle receipt differs")
    if args.check_primary:
        primary = parse(args.check_primary.read_bytes())
        validate_receipt(primary)
        require(canonical(value) == canonical(primary), "actual complete primary receipt differs")
        diagnostic["actual_primary_rows_compared"] = len(primary["cases"])
    print("PASS_COMMON_COVECTOR_ALL_FIELD_ORACLE " + canonical(diagnostic))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL_COMMON_COVECTOR_ALL_FIELD_ORACLE: " + str(error), file=sys.stderr)
        sys.exit(1)
