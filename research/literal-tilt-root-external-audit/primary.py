#!/usr/bin/env python3
"""Exact outward atanh/Taylor certificate for the literal nine-atom tilt."""
import argparse
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PINS = {
    "CASES.json": "c0ba307f9017317c16035fa59b28ce31a10b39efba208814ccd3c648def39f5d",
    "SCHEMA.json": "c314601815cacb8a9283621b7ca0e6647691ba177e07f38073b53ece16ab1f90",
    "SOURCE-PINS.json": "7f700d0d33722a5ea018b2f712b235dc3d924785a5e5aff5bbe292ec777ef3cc",
}
SOURCE = "cd666f05c4e9006025b634687cc493911c8371c8"
COUNTS = [[1, 37305], [2, 10695], [3, 3360], [4, 1530], [5, 300],
          [8, 1464], [16, 448], [32, 448], [48, 448]]
INPUTS = {"inputs/LOCAL_LIMIT.md", "inputs/README.md", "inputs/NOTICE"}
GRID = 10 ** 60
LOG_TERMS = 96
EXP_TERMS = 128
CONTROL_IDS = {"swapped_endpoints", "wrong_multiplicity", "degenerate_support",
               "nonpositive_weight", "duplicate_key", "float_token", "boolean_integer"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def bad_number(_):
    raise ValueError("float or nonfinite JSON token")


def decode(raw):
    need(len(raw) <= 8 * 1024 * 1024, "JSON byte budget")
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_float=bad_number, parse_constant=bad_number)


def load(path):
    return decode(path.read_bytes())


def integer(value, label):
    need(type(value) is int, label + ": proof integer required")
    return value


def rat(value):
    need(type(value) is list and len(value) == 2, "rational pair")
    numerator, denominator = (integer(x, "rational") for x in value)
    need(denominator > 0 and gcd(numerator, denominator) == 1,
         "reduced rational with positive denominator")
    return Fraction(numerator, denominator)


def encode_rat(value):
    return [value.numerator, value.denominator]


def encode_interval(bounds):
    return [encode_rat(bounds[0]), encode_rat(bounds[1])]


def interval(value):
    need(type(value) is list and len(value) == 2, "interval pair")
    lower, upper = (rat(x) for x in value)
    need(lower <= upper, "nonempty rational interval")
    return lower, upper


def ceiling(numerator, denominator):
    need(denominator > 0, "positive ceiling denominator")
    return -((-numerator) // denominator)


def rounded_interval(lower, upper):
    need(lower <= upper, "outward interval order")
    lo = lower.numerator * GRID // lower.denominator
    hi = ceiling(upper.numerator * GRID, upper.denominator)
    return Fraction(lo, GRID), Fraction(hi, GRID)


def authenticate():
    for name, expected in PINS.items():
        need(digest((HERE / name).read_bytes()) == expected, "frozen metadata drift: " + name)
    sources = load(HERE / "SOURCE-PINS.json")
    need(type(sources) is dict and len(sources["sources"]) == 3, "three inert source inputs")
    seen = set()
    for entry in sources["sources"]:
        name = entry["local_path"]
        need(type(name) is str and name in INPUTS and name not in seen, "exact source paths")
        seen.add(name)
        need(digest((HERE / name).read_bytes()) == entry["sha256"], "inert source byte drift")
    need(seen == INPUTS, "complete inert source set")
    paths = {"primary.py", "oracle.py", *PINS, *INPUTS}
    files = load(HERE / "FILES.json")
    need(type(files) is dict and set(files) == {"schema_version", "files"}, "FILES keys")
    need(integer(files["schema_version"], "FILES version") == 1, "FILES version one")
    need(type(files["files"]) is list, "FILES rows")
    covered = set()
    for entry in files["files"]:
        need(type(entry) is dict and set(entry) == {"path", "sha256"}, "FILES row")
        name = entry["path"]
        need(type(name) is str and name in paths and name not in covered, "FILES exact unique path")
        covered.add(name)
        need(digest((HERE / name).read_bytes()) == entry["sha256"], "FILES byte drift: " + name)
    need(covered == paths and len(paths) == 8, "FILES eight core inputs")
    cases, schema = load(HERE / "CASES.json"), load(HERE / "SCHEMA.json")
    need(canonical(cases["counts"]) == canonical(COUNTS), "literal nine-atom counts")
    compact = "".join((HERE / "inputs/LOCAL_LIMIT.md").read_text().split())
    law = "P={" + ",".join(str(r) + ":" + str(c) for r, c in COUNTS) + "},"
    need(law in compact and "Pr(X=logr)=P_rr^alpha/A," in compact,
         "literal law and positive r^alpha binding")
    need("EX=a=log5," in compact and "[0.98981438244597,0.98981438244599]" in compact,
         "literal mean equation and bracket binding")
    return cases, schema


def law_guard(counts):
    need(type(counts) is list and len(counts) >= 2, "nondegenerate support")
    ranks = set()
    for pair in counts:
        need(type(pair) is list and len(pair) == 2, "rank/multiplicity row")
        rank, count = (integer(x, "law integer") for x in pair)
        need(rank > 0 and count > 0, "positive rank and weight")
        need(rank not in ranks, "distinct support ranks")
        ranks.add(rank)
    need(len(ranks) >= 2, "nondegenerate support")


def atanh_log(value):
    need(Fraction(1) <= value <= 2, "range-reduced log argument")
    z = (value - 1) / (value + 1)
    square, power, total = z * z, z, Fraction(0)
    for index in range(LOG_TERMS):
        total += power / (2 * index + 1)
        power *= square
    lower = 2 * total
    tail = 2 * power / ((2 * LOG_TERMS + 1) * (1 - square))
    return lower, lower + tail


def logarithms(counts):
    two = atanh_log(Fraction(2))
    result = {}
    for rank in sorted({r for r, _ in counts} | {5}):
        exponent = rank.bit_length() - 1
        base = atanh_log(Fraction(rank, 1 << exponent))
        bounds = rounded_interval(base[0] + exponent * two[0],
                                  base[1] + exponent * two[1])
        need(bounds[1] - bounds[0] < Fraction(1, 10 ** 40), "log enclosure precision")
        result[rank] = bounds
    return result


def exp_interval(alpha, log_bounds):
    need(alpha > 0 and log_bounds[0] >= 0, "positive exponential argument")
    lower, upper = rounded_interval(alpha * log_bounds[0], alpha * log_bounds[1])
    xlo, xhi = int(lower * GRID), int(upper * GRID)
    need(0 <= xlo <= xhi <= 8 * GRID, "bounded Taylor argument")
    term_lo = term_hi = sum_lo = sum_hi = GRID
    for index in range(1, EXP_TERMS):
        term_lo = term_lo * xlo // (GRID * index)
        term_hi = ceiling(term_hi * xhi, GRID * index)
        sum_lo += term_lo
        sum_hi += term_hi
    first_omitted = ceiling(term_hi * xhi, GRID * EXP_TERMS)
    denominator = GRID * (EXP_TERMS + 1) - xhi
    need(denominator > 0, "Taylor geometric tail ratio")
    tail = ceiling(first_omitted * GRID * (EXP_TERMS + 1), denominator)
    bounds = Fraction(sum_lo, GRID), Fraction(sum_hi + tail, GRID)
    need(bounds[1] - bounds[0] < Fraction(1, 10 ** 40), "exp enclosure precision")
    return bounds


def endpoint(alpha, counts, logs):
    zlo = zhi = nlo = nhi = Fraction(0)
    for rank, count in counts:
        exp_lo, exp_hi = exp_interval(alpha, logs[rank])
        weight_lo, weight_hi = count * exp_lo, count * exp_hi
        zlo += weight_lo
        zhi += weight_hi
        nlo += weight_lo * logs[rank][0]
        nhi += weight_hi * logs[rank][1]
    need(zlo > 0, "positive normalizer")
    mean = nlo / zhi, nhi / zlo
    residual = mean[0] - logs[5][1], mean[1] - logs[5][0]
    return {"alpha": encode_rat(alpha), "normalizer": encode_interval((zlo, zhi)),
            "numerator": encode_interval((nlo, nhi)), "mean": encode_interval(mean),
            "residual": encode_interval(residual)}


class BracketFailure(ValueError):
    pass


def sign_checks(endpoints):
    left, right = (interval(row["residual"]) for row in endpoints)
    if left[1] >= 0:
        raise BracketFailure("left residual upper must be negative")
    if right[0] <= 0:
        raise BracketFailure("right residual lower must be positive")


def calculate(counts, alpha_values):
    law_guard(counts)
    need(type(alpha_values) is list and len(alpha_values) == 2, "two bracket endpoints")
    alphas = [rat(value) for value in alpha_values]
    logs = logarithms(counts)
    endpoints = [endpoint(alpha, counts, logs) for alpha in alphas]
    sign_checks(endpoints)
    need(alphas[0] < alphas[1], "ordered bracket")
    return logs, endpoints


def bracket_failure(counts, alphas, expected):
    try:
        calculate(counts, alphas)
    except BracketFailure as error:
        need(expected in str(error), "unintended bracket control diagnostic")
        return True
    raise ValueError("changed law/bracket was accepted")


def expected_failure(function, expected):
    try:
        function()
    except ValueError as error:
        need(expected in str(error), "unintended guard control diagnostic")
        return True
    raise ValueError("guard mutation was accepted")


def controls(cases):
    alphas = cases["alpha_endpoints"]
    wrong = [list(pair) for pair in COUNTS]
    wrong[1][1] += 1
    result = {
        "swapped_endpoints": bracket_failure(COUNTS, list(reversed(alphas)), "left residual"),
        "wrong_multiplicity": bracket_failure(wrong, alphas, "right residual"),
        "degenerate_support": expected_failure(lambda: law_guard([[1, 1]]), "nondegenerate"),
        "nonpositive_weight": expected_failure(lambda: law_guard([[1, 1], [2, 0]]), "positive"),
        "duplicate_key": expected_failure(lambda: decode(b'{"x":1,"x":2}'), "duplicate"),
        "float_token": expected_failure(lambda: decode(b'{"x":1.0}'), "float"),
        "boolean_integer": expected_failure(lambda: rat([True, 1]), "proof integer"),
    }
    need(set(result) == CONTROL_IDS, "complete seven controls")
    return result


def certificate(cases):
    need(cases["source_head"] == SOURCE and cases["target_log_rank"] == 5,
         "source and target binding")
    logs, endpoints = calculate(cases["counts"], cases["alpha_endpoints"])
    return {"schema_version": 1, "method": "atanh-taylor", "source_head": SOURCE,
            "cases_sha256": PINS["CASES.json"], "source_pins_sha256": PINS["SOURCE-PINS.json"],
            "logs": {str(rank): encode_interval(bounds) for rank, bounds in sorted(logs.items())},
            "endpoints": endpoints, "controls": controls(cases),
            "conclusion": {"left_negative": True, "right_positive": True,
                           "root_bracket": cases["alpha_endpoints"],
                           "strict_variance_all_real": True}}


def validate_certificate(value, cases, schema):
    need(type(value) is dict and set(value) == set(schema["certificate_keys"]), "certificate exact keys")
    need(integer(value["schema_version"], "certificate version") == 1, "certificate version one")
    need(type(value["method"]) is str and value["method"] == "atanh-taylor", "method identity")
    for key in ("source_head", "cases_sha256", "source_pins_sha256"):
        need(type(value[key]) is str, "certificate provenance string")
    logs = value["logs"]
    need(type(logs) is dict and set(logs) == {str(r) for r, _ in COUNTS}, "exact log support")
    for bounds in logs.values():
        interval(bounds)
    rows = value["endpoints"]
    need(type(rows) is list and len(rows) == 2, "two endpoint rows")
    for row, alpha in zip(rows, cases["alpha_endpoints"]):
        need(type(row) is dict and set(row) == set(schema["endpoint_keys"]), "endpoint exact keys")
        need(rat(row["alpha"]) == rat(alpha), "endpoint alpha/domain")
        for key in ("normalizer", "numerator", "mean", "residual"):
            interval(row[key])
    sign_checks(rows)
    outcomes = value["controls"]
    need(type(outcomes) is dict and set(outcomes) == CONTROL_IDS, "control exact keys")
    need(all(type(x) is bool and x for x in outcomes.values()), "true Boolean control outcomes")
    conclusion = value["conclusion"]
    need(type(conclusion) is dict and set(conclusion) == set(schema["conclusion_keys"]),
         "conclusion exact keys")
    for key in ("left_negative", "right_positive", "strict_variance_all_real"):
        need(type(conclusion[key]) is bool and conclusion[key], "true Boolean conclusion")
    need(type(conclusion["root_bracket"]) is list and len(conclusion["root_bracket"]) == 2,
         "root bracket endpoints")
    for observed, expected in zip(conclusion["root_bracket"], cases["alpha_endpoints"]):
        need(rat(observed) == rat(expected), "root bracket exact values")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    need(not (args.emit and args.certificate), "choose emission or retained certificate")
    cases, schema = authenticate()
    expected = certificate(cases)
    validate_certificate(expected, cases, schema)
    if args.emit:
        args.emit.write_bytes(canonical(expected) + b"\n")
    else:
        actual = load(args.certificate or HERE / "CERTIFICATE.json")
        validate_certificate(actual, cases, schema)
        need(canonical(actual) == canonical(expected), "whole canonical certificate differs")
    print("PASS_LITERAL_TILT_ATANH_TAYLOR signs2 controls7 strict_variance_structural no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL_LITERAL_TILT_ATANH_TAYLOR: " + str(error), file=sys.stderr)
        raise SystemExit(1)
