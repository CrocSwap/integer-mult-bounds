#!/usr/bin/env python3
"""Exact rectangle-log/power-sandwich oracle for six coarse finite-law H's.

No source or peer program is imported. Every retained certificate field is
regenerated; actual expectation, not an assumed log5, centers the moments.
"""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
N = M = 4096
Q = 10 ** 12
PINS = {
    "CASES.json": "7ce6661535811eb4e0b21960e20e910daef13b25df7d63eb9d0cd1683c8cd7cb",
    "SCHEMA.json": "e6d9a613e13d74aca027a40e110fbe70a3c32c89d3b9e009366f246f4f10d889",
    "SOURCE-PINS.json": "03ba0a7c3d0df9641e683ee1d8830862f0fe3efd2305d59a4a600ea058001b6c",
}
NAMES = ("atom_0", "atom_log2", "atom_log3", "variance_2_3", "third_abs_le5", "support_le3")
COUNTS = ((1, 37305), (2, 10695), (3, 3360), (4, 1530), (5, 300),
          (8, 1464), (16, 448), (32, 448), (48, 448))


def need(ok, why):
    if not ok:
        raise ValueError(why)


class NormalizationError(ValueError):
    pass


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def unique_pairs(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def decode_json(raw):
    need(len(raw) <= 4 * 1024 * 1024, "JSON byte budget")
    def bad_float(value):
        raise ValueError("JSON float forbidden: " + value)
    def bad_constant(value):
        raise ValueError("JSON nonfinite value forbidden: " + value)
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_float=bad_float, parse_constant=bad_constant)


def read_json(path):
    return decode_json(path.read_bytes())


def fraction(value):
    need(type(value) is str and 0 < len(value) <= 8192, "fraction must be a bounded string")
    result = F(value)
    need(str(result) == value, "canonical Fraction string required")
    return result


def authenticate():
    for name, digest in PINS.items():
        need(sha256((HERE / name).read_bytes()).hexdigest() == digest, "immutable input: " + name)
    source = read_json(HERE / "SOURCE-PINS.json")
    files = read_json(HERE / "FILES.json")
    need(type(files) is dict and set(files) == {"schema_version", "files"} and
         type(files["schema_version"]) is int and files["schema_version"] == 1,
         "FILES manifest shape")
    need(type(files["files"]) is list, "FILES list")
    expected = {"primary.py", "oracle.py", "CASES.json", "SCHEMA.json", "SOURCE-PINS.json"}
    source_paths = {}
    need(len(source["sources"]) == 6, "six inert sources")
    for entry in source["sources"]:
        local = "inputs/" + PurePosixPath(entry["local_path"]).name
        need(local not in source_paths, "unique inert source names")
        source_paths[local] = entry["sha256"]
    expected.update(source_paths)
    observed = set()
    for entry in files["files"]:
        need(type(entry) is dict and set(entry) == {"path", "sha256"}, "FILES entry keys")
        path, digest = entry["path"], entry["sha256"]
        need(type(path) is str and path in expected and path not in observed, "FILES exact unique path set")
        need(type(digest) is str and len(digest) == 64 and
             all(c in "0123456789abcdef" for c in digest), "FILES lowercase SHA256")
        raw = (HERE / path).read_bytes()
        need(len(raw) <= 4 * 1024 * 1024 and sha256(raw).hexdigest() == digest, "FILES byte binding: " + path)
        if path in source_paths:
            need(digest == source_paths[path], "inert source manifest agreement")
        observed.add(path)
    need(observed == expected, "FILES covers code2,metadata3,sources6 and no certificates")
    cases, schema = read_json(HERE / "CASES.json"), read_json(HERE / "SCHEMA.json")
    need(cases["law_counts"] == [list(x) for x in COUNTS] and cases["hypotheses"] == list(NAMES),
         "literal nine-atom law and six H predicates")
    need(cases["source_head"] == source["git_commit"] == "cd666f05c4e9006025b634687cc493911c8371c8",
         "source head agreement")
    return cases, schema


def ceiling_ratio(numerator, denominator):
    need(denominator > 0, "positive integer divisor")
    return -((-numerator) // denominator)


def floor_scaled(value):
    return (value.numerator * Q) // value.denominator


def ceil_scaled(value):
    return ceiling_ratio(value.numerator * Q, value.denominator)


def logarithm(rank):
    """Decreasing-integral right/left rectangles, termwise outward rounding."""
    need(type(rank) is int and 1 <= rank <= 48, "bounded positive rank")
    width = rank - 1
    if width == 0:
        return F(0), F(0)
    lower, upper = 0, 0
    for k in range(1, N + 1):
        lower += (Q * width) // (N + k * width)
    for k in range(N):
        upper += ceiling_ratio(Q * width, N + k * width)
    return F(lower, Q), F(upper, Q)


def exponential(interval):
    """Power sandwich with twelve monotone outward fixed-point squarings."""
    lo, hi = interval
    need(0 <= lo <= hi < 4 and hi < M, "nonnegative exp argument below4")
    lower = floor_scaled(1 + lo / M)
    upper = ceil_scaled(1 / (1 - hi / M))
    for unused in range(12):
        lower = (lower * lower) // Q
        upper = ceiling_ratio(upper * upper, Q)
    return F(lower, Q), F(upper, Q)


def centered_distance(log_interval, mean):
    lo, hi = log_interval[0] - mean[1], log_interval[1] - mean[0]
    lower = F(0) if lo <= 0 <= hi else min(abs(lo), abs(hi))
    return lower, max(abs(lo), abs(hi))


def engine(counts, alpha, logs):
    need(set(counts) == set(logs) and all(type(n) is int and n >= 0 for n in counts.values()),
         "nonnegative literal atom counts")
    need(F(0) <= alpha[0] <= alpha[1] < 1, "alpha bracket in[0,1)")
    weights = {}
    for rank, count in counts.items():
        bounds = exponential((alpha[0] * logs[rank][0], alpha[1] * logs[rank][1]))
        weights[rank] = (count * bounds[0], count * bounds[1])
    normalizer = (sum(x[0] for x in weights.values()), sum(x[1] for x in weights.values()))
    if normalizer[0] <= 0:
        raise NormalizationError("zero lower normalizer")
    probabilities = {rank: (lo / normalizer[1], min(F(1), hi / normalizer[0]))
                     for rank, (lo, hi) in weights.items()}
    mean = (sum(probabilities[r][0] * logs[r][0] for r in counts),
            sum(probabilities[r][1] * logs[r][1] for r in counts))
    distances = {rank: centered_distance(logs[rank], mean) for rank in counts}
    variance = (sum(probabilities[r][0] * distances[r][0] ** 2 for r in counts),
                sum(probabilities[r][1] * distances[r][1] ** 2 for r in counts))
    third = sum(probabilities[r][1] * distances[r][1] ** 3 for r in counts)
    support = max(distances[r][1] for r in counts if counts[r] > 0)
    hypotheses = {"atom_0": probabilities[1][0] >= F(1, 4),
                  "atom_log2": probabilities[2][0] >= F(1, 8),
                  "atom_log3": probabilities[3][0] >= F(1, 16),
                  "variance_2_3": variance[0] >= 2 and variance[1] <= 3,
                  "third_abs_le5": third <= 5, "support_le3": support <= 3}
    return {"probabilities": probabilities, "mean": mean, "variance": variance,
            "third": third, "support": support, "hypotheses": hypotheses}


def interval_strings(interval):
    return [str(x) for x in interval]


def controls(counts, alpha, logs):
    results = {}
    changed = counts.copy()
    changed[3] = 0
    outcome = engine(changed, alpha, logs)
    need(outcome["hypotheses"]["atom_log3"] is False and outcome["probabilities"][3] == (0, 0),
         "drop_atom3 must fail in real engine")
    results["drop_atom3"] = {"hypothesis_false": "atom_log3", "probability": interval_strings(outcome["probabilities"][3])}
    outcome = engine(counts, (F(0), F(0)), logs)
    need(outcome["hypotheses"]["variance_2_3"] is False and outcome["variance"][1] < 2,
         "alpha_zero must have certified variance below2")
    results["alpha_zero"] = {"hypothesis_false": "variance_2_3", "variance": interval_strings(outcome["variance"])}
    changed = counts.copy()
    changed[1] = 0
    outcome = engine(changed, alpha, logs)
    need(outcome["hypotheses"]["atom_0"] is False and outcome["probabilities"][1] == (0, 0),
         "drop_atom0 must fail in real engine")
    results["drop_atom0"] = {"hypothesis_false": "atom_0", "probability": interval_strings(outcome["probabilities"][1])}
    try:
        engine({rank: 0 for rank in counts}, alpha, logs)
    except NormalizationError:
        results["zero_normalizer"] = {"rejected": True}
    else:
        raise ValueError("zero normalizer accepted")
    malformed = {"duplicate": b'{"x":1,"x":1}', "float": b'{"x":1.5}',
                 "nonfinite": b'{"x":NaN}'}
    for name, raw in malformed.items():
        try:
            decode_json(raw)
        except ValueError:
            results[name] = {"rejected": True}
        else:
            raise ValueError("parser control accepted: " + name)
    try:
        fraction(True)
    except ValueError:
        results["bool_fraction"] = {"rejected": True}
    else:
        raise ValueError("Boolean fraction accepted")
    need(set(results) == {"drop_atom3", "alpha_zero", "drop_atom0", "zero_normalizer",
                          "duplicate", "float", "nonfinite", "bool_fraction"}, "eight controls")
    return results


def certificate(cases, schema):
    alpha = tuple(fraction(x) for x in cases["alpha_bracket"])
    need(len(alpha) == 2, "two alpha endpoints")
    counts = dict(COUNTS)
    logs = {rank: logarithm(rank) for rank in counts}
    positive = engine(counts, alpha, logs)
    need(all(positive["hypotheses"].values()), "positive law did not certify all six H predicates")
    checked_controls = controls(counts, alpha, logs)
    out = {"schema_version": 1,
           "method": "direct_log_rectangles_N4096_Q1e12_exp_power_sandwich_M4096_centered_squares",
           "source_head": cases["source_head"], "source_pins_sha256": PINS["SOURCE-PINS.json"],
           "case_sha256": PINS["CASES.json"], "alpha_bracket": cases["alpha_bracket"],
           "probabilities": {str(r): interval_strings(positive["probabilities"][r]) for r in counts},
           "mean": interval_strings(positive["mean"]), "variance": interval_strings(positive["variance"]),
           "third_absolute_moment": {"upper": str(positive["third"])},
           "max_centered_support": {"upper": str(positive["support"])},
           "hypotheses": positive["hypotheses"], "controls": checked_controls}
    need(set(out) == set(schema["certificate_keys"]), "exact certificate fields")
    return out


def validate_certificate_encoding(obj):
    need(type(obj) is dict, "certificate object")
    for key in ("source_pins_sha256", "case_sha256"):
        need(type(obj.get(key)) is str, "certificate digest string")
    for key in ("alpha_bracket", "mean", "variance"):
        value = obj.get(key)
        need(type(value) is list and len(value) == 2, "fraction interval pair")
        need(fraction(value[0]) <= fraction(value[1]), "ordered interval")
    probs = obj.get("probabilities")
    need(type(probs) is dict and set(probs) == {str(r) for r, unused in COUNTS}, "nine probability entries")
    for value in probs.values():
        need(type(value) is list and len(value) == 2, "probability interval")
        need(0 <= fraction(value[0]) <= fraction(value[1]) <= 1, "probability bounds")
    for key in ("third_absolute_moment", "max_centered_support"):
        value = obj.get(key)
        need(type(value) is dict and set(value) == {"upper"} and fraction(value["upper"]) >= 0,
             "nonnegative rational upper bound")
    need(type(obj.get("hypotheses")) is dict and set(obj["hypotheses"]) == set(NAMES) and
         all(type(x) is bool for x in obj["hypotheses"].values()), "six Boolean H values")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--certificate", type=Path)
    args = parser.parse_args()
    need(not (args.emit and args.certificate), "choose emit or certificate verification")
    cases, schema = authenticate()
    regenerated = certificate(cases, schema)
    if args.emit:
        args.emit.write_bytes(canonical(regenerated) + b"\n")
    else:
        actual = read_json(args.certificate or HERE / "ORACLE.json")
        validate_certificate_encoding(actual)
        need(canonical(actual) == canonical(regenerated), "complete retained certificate differs from regeneration")
    print("PASS rectangle-log centered-square oracle")
    print(json.dumps({"hypotheses": regenerated["hypotheses"], "controls": sorted(regenerated["controls"]),
                      "certificate_canonical_sha256": sha256(canonical(regenerated)).hexdigest()}, sort_keys=True))


if __name__ == "__main__":
    main()
