#!/usr/bin/env python3
"""Rational atanh/Taylor certificate for the nine-atom finite H predicates."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SCALE = 10 ** 18
TERMS = 80
CASE_SHA = "7ce6661535811eb4e0b21960e20e910daef13b25df7d63eb9d0cd1683c8cd7cb"
SCHEMA_SHA = "e6d9a613e13d74aca027a40e110fbe70a3c32c89d3b9e009366f246f4f10d889"
SOURCE_SHA = "03ba0a7c3d0df9641e683ee1d8830862f0fe3efd2305d59a4a600ea058001b6c"
METHOD = "primary:80-term atanh prime logs;80-term positive Taylor exp;outward1e18;raw-moment variance"
INPUT_NAMES = {"LOCAL_LIMIT.md", "README.md", "REVIEW.md", "TASK.json", "SOURCES.json", "NOTICE"}
CONTROL_NAMES = {"drop_atom3", "alpha_zero", "drop_atom0", "zero_normalizer",
                 "duplicate", "float", "nonfinite", "bool_fraction"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("ascii")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique_pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def forbidden_number(_):
    raise ValueError("float or nonfinite JSON number")


def decode(data):
    need(len(data) <= 4 * 1024 * 1024, "JSON input exceeds4MiB")
    return json.loads(data, object_pairs_hook=unique_pairs,
                      parse_float=forbidden_number,
                      parse_constant=forbidden_number)


def load(path):
    return decode(path.read_bytes())


def fraction(value):
    need(type(value) is str, "fraction must be canonical string, never Boolean")
    try:
        result = F(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError("invalid rational string") from error
    need(str(result) == value, "noncanonical rational string")
    return result


def authenticate():
    for name, expected in (("CASES.json", CASE_SHA), ("SCHEMA.json", SCHEMA_SHA),
                           ("SOURCE-PINS.json", SOURCE_SHA)):
        need(digest((HERE / name).read_bytes()) == expected, "frozen input drift: " + name)
    expected_paths = {"primary.py", "oracle.py", "CASES.json", "SCHEMA.json", "SOURCE-PINS.json"}
    expected_paths |= {"inputs/" + name for name in INPUT_NAMES}
    manifest = load(HERE / "FILES.json")
    need(type(manifest) is dict and set(manifest) == {"schema_version", "files"}, "FILES schema")
    need(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1, "FILES version")
    seen = set()
    for row in manifest["files"]:
        need(type(row) is dict and set(row) == {"path", "sha256"}, "FILES row schema")
        name = row["path"]
        need(type(name) is str and name in expected_paths and name not in seen, "FILES exact path set")
        seen.add(name)
        need(digest((HERE / name).read_bytes()) == row["sha256"], "FILES byte drift: " + name)
    need(seen == expected_paths, "FILES omitted required input")
    pins = load(HERE / "SOURCE-PINS.json")
    need(len(pins["sources"]) == 6, "six frozen source objects")
    for row in pins["sources"]:
        name = Path(row["local_path"]).name
        need(name in INPUT_NAMES, "source basename outside frozen input set")
        need(digest((HERE / "inputs" / name).read_bytes()) == row["sha256"], "source byte drift: " + name)


def down(value):
    return F((value.numerator * SCALE) // value.denominator, SCALE)


def up(value):
    numerator = value.numerator * SCALE
    return F(-((-numerator) // value.denominator), SCALE)


def log_prime(prime):
    z = F(prime - 1, prime + 1)
    power, total = z, F(0)
    for k in range(TERMS):
        total += power / (2 * k + 1)
        power *= z * z
    lower = 2 * total
    tail = 2 * power / ((2 * TERMS + 1) * (1 - z * z))
    return down(lower), up(lower + tail)


def rank_logs(ranks):
    primes = {prime: log_prime(prime) for prime in (2, 3, 5)}
    result = {}
    for rank in ranks:
        need(type(rank) is int and rank >= 1, "positive integer rank")
        remaining, lower, upper = rank, F(0), F(0)
        for prime, interval in primes.items():
            while remaining % prime == 0:
                remaining //= prime
                lower += interval[0]
                upper += interval[1]
        need(remaining == 1, "rank outside declared prime support")
        result[rank] = lower, upper
    return result


def taylor_exp(value):
    need(0 <= value < 4, "exp argument outside nonnegative declared domain")
    term, total = F(1), F(1)
    for k in range(1, TERMS):
        term = term * value / k
        total += term
    first_omitted = term * value / TERMS
    tail = first_omitted / (1 - value / (TERMS + 1))
    return total, total + tail


def exp_interval(lower, upper):
    need(0 <= lower <= upper < 4, "exp interval domain")
    return down(taylor_exp(lower)[0]), up(taylor_exp(upper)[1])


def law_bounds(counts, alpha, logs):
    need(set(counts) == set(logs), "complete rank support required")
    need(all(type(n) is int and n >= 0 for n in counts.values()), "nonnegative integer counts")
    need(0 <= alpha[0] <= alpha[1], "nonnegative alpha bracket")
    weights = {}
    for rank, count in counts.items():
        low, high = logs[rank]
        a, b = exp_interval(alpha[0] * low, alpha[1] * high)
        weights[rank] = count * a, count * b
    norm_low = sum(a for a, _ in weights.values())
    norm_high = sum(b for _, b in weights.values())
    need(norm_low > 0, "positive normalizer required")
    probabilities = {r: (a / norm_high, b / norm_low) for r, (a, b) in weights.items()}
    mean_low = sum(probabilities[r][0] * logs[r][0] for r in counts)
    mean_high = sum(probabilities[r][1] * logs[r][1] for r in counts)
    second_low = sum(probabilities[r][0] * logs[r][0] ** 2 for r in counts)
    second_high = sum(probabilities[r][1] * logs[r][1] ** 2 for r in counts)
    variance = second_low - mean_high ** 2, second_high - mean_low ** 2
    distances = {r: max(abs(logs[r][0] - mean_high), abs(logs[r][1] - mean_low)) for r in counts}
    third = sum(probabilities[r][1] * distances[r] ** 3 for r in counts)
    support = max(distances[r] for r, count in counts.items() if count)
    return probabilities, (mean_low, mean_high), variance, third, support


def hypotheses(bounds):
    probabilities, _, variance, third, support = bounds
    return {"atom_0": probabilities[1][0] >= F(1, 4),
            "atom_log2": probabilities[2][0] >= F(1, 8),
            "atom_log3": probabilities[3][0] >= F(1, 16),
            "variance_2_3": variance[0] >= 2 and variance[1] <= 3,
            "third_abs_le5": third <= 5, "support_le3": support <= 3}


def rejected(function, diagnostic):
    try:
        function()
    except ValueError as error:
        need(diagnostic in str(error), "unintended control rejection: " + str(error))
        return True
    raise ValueError("control was accepted: " + diagnostic)


def controls(counts, alpha, logs):
    outcomes = {}
    for rank, key, predicate in ((3, "drop_atom3", "atom_log3"), (1, "drop_atom0", "atom_0")):
        changed = dict(counts)
        changed[rank] = 0
        need(not hypotheses(law_bounds(changed, alpha, logs))[predicate], "atom control failed")
        outcomes[key] = True
    zero_alpha = law_bounds(counts, (F(0), F(0)), logs)
    need(not hypotheses(zero_alpha)["variance_2_3"], "zero-alpha variance control failed")
    outcomes["alpha_zero"] = True
    outcomes["zero_normalizer"] = rejected(lambda: law_bounds({r: 0 for r in counts}, alpha, logs), "positive normalizer")
    outcomes["duplicate"] = rejected(lambda: decode(b'{"x":1,"x":2}'), "duplicate JSON")
    outcomes["float"] = rejected(lambda: decode(b'{"x":0.5}'), "float or nonfinite")
    outcomes["nonfinite"] = rejected(lambda: decode(b'{"x":NaN}'), "float or nonfinite")
    outcomes["bool_fraction"] = rejected(lambda: fraction(True), "fraction must be canonical string")
    need(set(outcomes) == CONTROL_NAMES, "complete control set")
    return outcomes


def interval_strings(interval):
    return [str(value) for value in interval]


def make_certificate(cases):
    counts = dict(cases["law_counts"])
    alpha = tuple(fraction(value) for value in cases["alpha_bracket"])
    logs = rank_logs(counts)
    bounds = law_bounds(counts, alpha, logs)
    flags = hypotheses(bounds)
    need(set(flags) == set(cases["hypotheses"]) and all(flags.values()), "six finite H predicates not certified")
    probabilities, mean, variance, third, support = bounds
    return {"schema_version": 1, "method": METHOD, "source_head": cases["source_head"],
            "source_pins_sha256": SOURCE_SHA, "case_sha256": CASE_SHA,
            "alpha_bracket": interval_strings(alpha),
            "probabilities": {str(rank): interval_strings(value) for rank, value in probabilities.items()},
            "mean": interval_strings(mean), "variance": interval_strings(variance),
            "third_absolute_moment": {"upper": str(third)},
            "max_centered_support": {"upper": str(support)},
            "hypotheses": flags, "controls": controls(counts, alpha, logs)}


def validate_interval(value):
    need(type(value) is list and len(value) == 2, "two endpoint interval")
    lower, upper = [fraction(x) for x in value]
    need(lower <= upper, "reversed interval")


def validate_certificate(value, cases):
    schema = load(HERE / "SCHEMA.json")
    need(type(value) is dict and set(value) == set(schema["certificate_keys"]), "certificate exact keys")
    need(type(value["schema_version"]) is int and value["schema_version"] == 1, "certificate version")
    for name in ("alpha_bracket", "mean", "variance"):
        validate_interval(value[name])
    probabilities = value["probabilities"]
    need(type(probabilities) is dict and set(probabilities) == {str(r) for r, _ in cases["law_counts"]}, "all rank probabilities")
    for interval in probabilities.values():
        validate_interval(interval)
    for name in ("third_absolute_moment", "max_centered_support"):
        need(type(value[name]) is dict and set(value[name]) == {"upper"}, "moment/support schema")
        need(fraction(value[name]["upper"]) >= 0, "nonnegative moment/support bound")
    need(type(value["hypotheses"]) is dict and set(value["hypotheses"]) == set(cases["hypotheses"]), "six hypothesis keys")
    need(all(type(x) is bool and x for x in value["hypotheses"].values()), "true Boolean hypotheses required")
    need(type(value["controls"]) is dict and set(value["controls"]) == CONTROL_NAMES, "eight control keys")
    need(all(type(x) is bool and x for x in value["controls"].values()), "executed Boolean controls required")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    need(not (args.emit and args.certificate), "choose emit or retained certificate")
    authenticate()
    cases = load(HERE / "CASES.json")
    certificate = make_certificate(cases)
    validate_certificate(certificate, cases)
    if args.emit:
        args.emit.write_bytes(canonical(certificate) + b"\n")
    else:
        actual = load(args.certificate or HERE / "CERTIFICATE.json")
        validate_certificate(actual, cases)
        need(canonical(actual) == canonical(certificate), "whole canonical certificate differs")
    print("PASS_FINITE_H_PRIMARY six_predicates controls=8 actual_mean all_alpha_bracket no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as error:
        print("FAIL_FINITE_H_PRIMARY: " + str(error), file=sys.stderr)
        raise SystemExit(1)
