#!/usr/bin/env python3
"""Outward integer Simpson/binomial certificate for the declared tilt root."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
D = 10 ** 100
N = 32768
M = 2 ** 128
CASE_SHA = "c0ba307f9017317c16035fa59b28ce31a10b39efba208814ccd3c648def39f5d"
SCHEMA_SHA = "c314601815cacb8a9283621b7ca0e6647691ba177e07f38073b53ece16ab1f90"
SOURCE_SHA = "7f700d0d33722a5ea018b2f712b235dc3d924785a5e5aff5bbe292ec777ef3cc"
PATHS = {"primary.py", "oracle.py", "CASES.json", "SCHEMA.json", "SOURCE-PINS.json",
         "inputs/LOCAL_LIMIT.md", "inputs/README.md", "inputs/NOTICE"}
LAW = [[1,37305],[2,10695],[3,3360],[4,1530],[5,300],[8,1464],
       [16,448],[32,448],[48,448]]
CONTROLS = {"swapped_endpoints", "wrong_multiplicity", "degenerate_support",
            "nonpositive_weight", "duplicate_key", "float_token", "boolean_integer"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    need(type(value) is int, "proof integer excludes Boolean")
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ceil_div(numerator, denominator):
    need(denominator > 0, "positive division denominator")
    return -(-numerator // denominator)


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def forbidden_number(_):
    raise ValueError("float or nonfinite JSON token")


def decode(data):
    need(len(data) <= 4 * 1024 * 1024, "JSON exceeds4MiB")
    return json.loads(data, object_pairs_hook=unique_pairs,
                      parse_float=forbidden_number, parse_constant=forbidden_number)


def load(path):
    return decode(path.read_bytes())


def authenticate():
    for name, sha in (("CASES.json", CASE_SHA), ("SCHEMA.json", SCHEMA_SHA),
                      ("SOURCE-PINS.json", SOURCE_SHA)):
        need(digest((HERE/name).read_bytes()) == sha, "frozen metadata drift: " + name)
    files = load(HERE/"FILES.json")
    need(type(files) is dict and set(files) == {"schema_version", "files"}, "FILES exact keys")
    need(integer(files["schema_version"]) == 1, "FILES version")
    seen = set()
    for row in files["files"]:
        need(type(row) is dict and set(row) == {"path", "sha256"}, "FILES row")
        name = row["path"]
        need(type(name) is str and name in PATHS and name not in seen, "FILES exact path set")
        need(digest((HERE/name).read_bytes()) == row["sha256"], "FILES byte drift: " + name)
        seen.add(name)
    need(seen == PATHS, "FILES missing input")
    pins = load(HERE/"SOURCE-PINS.json")
    need(len(pins["sources"]) == 3, "three inert sources")
    for row in pins["sources"]:
        need(digest((HERE/row["local_path"]).read_bytes()) == row["sha256"], "source byte drift")
    text = (HERE/"inputs/LOCAL_LIMIT.md").read_text()
    need("P = {1:37305, 2:10695, 3:3360, 4:1530, 5:300," in text
         and "8:1464, 16:448, 32:448, 48:448}" in text
         and "A = sum_r P_r r^alpha" in text and "E X = a = log 5" in text,
         "literal source law binding")


def pair(value):
    return [value.numerator, value.denominator]


def fixed_interval(bounds):
    return [pair(Fraction(bounds[0], D)), pair(Fraction(bounds[1], D))]


def simpson_log_unit(numerator, denominator):
    need(denominator > 0 and denominator <= numerator <= 2*denominator, "Simpson range")
    delta = numerator - denominator
    if delta == 0:
        return (0, 0)
    low_sum, high_sum = 0, 0
    for index in range(N+1):
        divisor = N*denominator + index*delta
        scaled = D*N*denominator
        weight = 1 if index in (0, N) else (4 if index % 2 else 2)
        low_sum += weight*(scaled // divisor)
        high_sum += weight*ceil_div(scaled, divisor)
    lower = delta*low_sum // (denominator*3*N)
    upper = ceil_div(delta*high_sum, denominator*3*N)
    error = ceil_div(2*D*delta**5, 15*denominator**5*N**4)
    return (lower-error, upper+error)


def logarithms(ranks):
    log_two = simpson_log_unit(2, 1)
    cache = {(1, 1): (0, 0)}
    result = {}
    for rank in ranks:
        need(type(rank) is int and rank > 0, "positive integer rank")
        exponent = rank.bit_length()-1
        unit = Fraction(rank, 2**exponent)
        key = (unit.numerator, unit.denominator)
        if key not in cache:
            cache[key] = simpson_log_unit(*key)
        lo, hi = cache[key]
        result[rank] = (lo+exponent*log_two[0], hi+exponent*log_two[1])
    return result


def positive_exp(bounds):
    lower, upper = bounds
    need(0 <= lower <= upper < 16*D and upper < D*M, "positive binomial exp range")
    lo = D + lower // M
    hi = ceil_div(D*D*M, D*M-upper)
    for _ in range(128):
        lo = lo*lo // D
        hi = ceil_div(hi*hi, D)
    return (lo, hi)


def validate_law(law):
    need(type(law) is list and len(law) >= 2, "nondegenerate support")
    ranks = []
    for row in law:
        need(type(row) is list and len(row) == 2, "law row")
        rank, weight = map(integer, row)
        need(rank > 0 and weight > 0, "positive weight and rank")
        ranks.append(rank)
    need(len(set(ranks)) == len(ranks), "distinct support ranks")
    return ranks


def evaluate(alpha, law, logs):
    need(type(alpha) is list and len(alpha) == 2, "alpha pair")
    a, b = map(integer, alpha)
    need(a > 0 and b > 0 and Fraction(a, b) < 2, "positive bounded alpha")
    zlo = zhi = nlo = nhi = 0
    for rank, weight in law:
        loglo, loghi = logs[rank]
        x = (a*loglo // b, ceil_div(a*loghi, b))
        wlo, whi = positive_exp(x)
        zlo += weight*wlo
        zhi += weight*whi
        nlo += weight*(wlo*loglo // D)
        nhi += weight*ceil_div(whi*loghi, D)
    need(zlo > 0 and zhi >= zlo, "positive normalizer")
    mean = (D*nlo // zhi, ceil_div(D*nhi, zlo))
    residual = (mean[0]-logs[5][1], mean[1]-logs[5][0])
    return {"alpha": pair(Fraction(a, b)), "normalizer": fixed_interval((zlo, zhi)),
            "numerator": fixed_interval((nlo, nhi)), "mean": fixed_interval(mean),
            "residual": fixed_interval(residual)}


def parse_rational(value):
    need(type(value) is list and len(value) == 2, "rational pair")
    numerator, denominator = map(integer, value)
    need(denominator > 0, "positive rational denominator")
    result = Fraction(numerator, denominator)
    need(pair(result) == value, "reduced rational")
    return result


def parse_interval(value):
    need(type(value) is list and len(value) == 2, "interval pair")
    lo, hi = map(parse_rational, value)
    need(lo <= hi, "ordered interval")
    return lo, hi


def bracket(endpoints, law, logs):
    validate_law(law)
    need(len(endpoints) == 2 and parse_rational(endpoints[0]) < parse_rational(endpoints[1]),
         "ordered alpha endpoints")
    rows = [evaluate(alpha, law, logs) for alpha in endpoints]
    need(parse_interval(rows[0]["residual"])[1] < 0
         and parse_interval(rows[1]["residual"])[0] > 0, "strict endpoint signs")
    return rows


def expected_failure(function, diagnostic):
    try:
        function()
    except ValueError as error:
        need(diagnostic in str(error), "wrong control failure: " + str(error))
        return True
    raise ValueError("control unexpectedly accepted: " + diagnostic)


def controls(cases, logs):
    endpoints = cases["alpha_endpoints"]
    wrong = [row[:] for row in LAW]
    wrong[1][1] += 1
    result = {
        "swapped_endpoints": expected_failure(lambda: bracket(endpoints[::-1], LAW, logs), "ordered alpha"),
        "wrong_multiplicity": expected_failure(lambda: bracket(endpoints, wrong, logs), "strict endpoint signs"),
        "degenerate_support": expected_failure(lambda: validate_law([[1,1]]), "nondegenerate support"),
        "nonpositive_weight": expected_failure(lambda: validate_law([[1,1],[2,0]]), "positive weight"),
        "duplicate_key": expected_failure(lambda: decode(b'{"x":1,"x":2}'), "duplicate JSON"),
        "float_token": expected_failure(lambda: decode(b'{"x":0.5}'), "float or nonfinite"),
        "boolean_integer": expected_failure(lambda: integer(True), "excludes Boolean")}
    need(set(result) == CONTROLS and all(result.values()), "seven actual controls")
    return result


def certificate(cases):
    need(cases["counts"] == LAW and integer(cases["target_log_rank"]) == 5, "literal case law")
    ranks = validate_law(cases["counts"])
    logs = logarithms(ranks)
    rows = bracket(cases["alpha_endpoints"], LAW, logs)
    return {"schema_version": 1, "method": "simpson-binomial",
            "source_head": cases["source_head"], "cases_sha256": CASE_SHA,
            "source_pins_sha256": SOURCE_SHA,
            "logs": {str(rank): fixed_interval(logs[rank]) for rank in ranks},
            "endpoints": rows, "controls": controls(cases, logs),
            "conclusion": {"left_negative": True, "right_positive": True,
                           "root_bracket": cases["alpha_endpoints"],
                           "strict_variance_all_real": len(ranks) > 1}}


def validate_certificate(value, cases):
    schema = load(HERE/"SCHEMA.json")
    need(type(value) is dict and set(value) == set(schema["certificate_keys"]), "certificate exact keys")
    need(integer(value["schema_version"]) == 1, "certificate version")
    need(type(value["logs"]) is dict and set(value["logs"]) == {str(r) for r,w in LAW}, "all log keys")
    for bounds in value["logs"].values():
        parse_interval(bounds)
    need(type(value["endpoints"]) is list and len(value["endpoints"]) == 2, "two endpoint rows")
    for row in value["endpoints"]:
        need(type(row) is dict and set(row) == set(schema["endpoint_keys"]), "endpoint exact keys")
        parse_rational(row["alpha"])
        for name in ("normalizer", "numerator", "mean", "residual"):
            parse_interval(row[name])
    need(type(value["controls"]) is dict and set(value["controls"]) == CONTROLS, "control exact keys")
    need(all(type(flag) is bool and flag for flag in value["controls"].values()), "true Boolean controls")
    conclusion = value["conclusion"]
    need(type(conclusion) is dict and set(conclusion) == set(schema["conclusion_keys"]), "conclusion exact keys")
    for name in ("left_negative", "right_positive", "strict_variance_all_real"):
        need(type(conclusion[name]) is bool and conclusion[name], "true Boolean conclusion")
    need(type(conclusion["root_bracket"]) is list and len(conclusion["root_bracket"]) == 2, "root bracket shape")
    for alpha in conclusion["root_bracket"]:
        parse_rational(alpha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    need(not (args.emit and args.certificate), "choose emit or retained certificate")
    authenticate()
    cases = load(HERE/"CASES.json")
    result = certificate(cases)
    validate_certificate(result, cases)
    if args.emit:
        args.emit.write_bytes(canonical(result)+b"\n")
    else:
        actual = load(args.certificate or HERE/"ORACLE.json")
        validate_certificate(actual, cases)
        need(canonical(actual) == canonical(result), "whole actual oracle certificate differs")
    print("PASS_TILTROOT_SIMPSON_BINOMIAL endpoints2 controls7 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL_TILTROOT_SIMPSON_BINOMIAL: " + str(error), file=sys.stderr)
        raise SystemExit(1)
