#!/usr/bin/env python3
"""Source-bound exact enumeration of a fixed coarse-output four-shear ABI.

Only the four pinned inert Markdown documents are read. No predecessor checker
is imported or executed. The all-parameter theorem is in PROOF.md; this bounded
receipt enumerates every declared phase and input, using integer arithmetic.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_HASH = "96d9bdd4983b6c0a71b86e4dae34f594988679872f29901bdf3469dcfd80b661"
CASES_HASH = "41e66cd094ae56a5148b81cdce8218651e5e04a42aa1e9caff4c4bce71c21b90"
BITS = list(range(9))
BOUNDS = [0, 1, 2, 3, 7, 16, 31]
OFFSETS = list(range(-3, 4))
PERIODS = [-3, -1, 1, 4]


class VerificationError(Exception):
    """An explicit check failed, including under Python optimization."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise VerificationError("non-finite JSON constant: " + value)


def read_json(path):
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
        return (len(left) == len(right)
                and all(same_typed(a, b) for a, b in zip(left, right)))
    return left == right


def authenticate():
    manifest_path = ROOT / "SOURCE-PINS.json"
    require(sha(manifest_path.read_bytes()) == SOURCE_HASH, "manifest SHA256")
    manifest = read_json(manifest_path)
    require(type(manifest) is dict and manifest.get("schema_version") == 1,
            "source manifest schema")
    files = manifest.get("files")
    require(type(files) is list and len(files) == 4, "four inert source files")
    for row in files:
        require(type(row) is dict, "source row type")
        rel = row.get("local_path")
        require(type(rel) is str and rel.startswith("inputs/"), "source path")
        path = (ROOT / rel).resolve()
        require(path.parent == (ROOT / "inputs").resolve(), "source containment")
        data = path.read_bytes()
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        require(type(row.get("bytes")) is int and len(data) == row["bytes"],
                "source length: " + rel)
        require(sha(data) == row.get("sha256"), "source SHA256: " + rel)
        require(hashlib.sha1(blob).hexdigest() == row.get("git_blob"),
                "source Git blob: " + rel)
    cases_path = ROOT / "CASES.json"
    require(sha(cases_path.read_bytes()) == CASES_HASH, "case manifest SHA256")
    cases = read_json(cases_path)
    require(same_typed(cases.get("helper_fractional_bits"), BITS), "bits")
    require(same_typed(cases.get("source_bounds"), BOUNDS), "bounds")
    require(same_typed(cases.get("lift_offsets"), OFFSETS), "offsets")
    require(type(cases.get("initial_destination")) is int
            and cases["initial_destination"] == -2, "initial output")
    return manifest


def reader(helper, denominator):
    require(type(helper) is int and type(denominator) is int
            and denominator > 0, "integer helper/positive denominator")
    return (6 * helper + denominator) // (2 * denominator)


def ceil_div(numerator, denominator):
    require(type(numerator) is int and type(denominator) is int
            and denominator > 0, "integer ceiling arguments")
    return -((-numerator) // denominator)


def execute(x, helper, a, denominator, output=-2):
    """Execute the four specified calls, retaining their literal order."""
    require(all(type(v) is int for v in (x, helper, a, denominator, output)),
            "ABI registers and lift are integers")
    source = x
    dirty_helper = helper
    dirty_output = output
    helper += a * source
    output += reader(helper, denominator)
    helper -= a * source
    output -= reader(helper, denominator)
    require(source == x, "source preservation")
    require(helper == dirty_helper, "helper restoration")
    return output - dirty_output - source


def enumerate_row(b, bound, coefficient):
    denominator = 1 << b
    histogram = Counter()
    min_error = None
    max_error = None
    min_witness = None
    max_witness = None
    for helper in range(denominator):
        for x in range(-bound, bound + 1):
            error = execute(x, helper, coefficient, denominator)
            histogram[error] += 1
            if min_error is None or error < min_error:
                min_error, min_witness = error, [helper, x]
            if max_error is None or error > max_error:
                max_error, max_witness = error, [helper, x]
    predicted = ceil_div(abs(3 * coefficient - denominator) * bound, denominator)
    maximum = max(abs(min_error), abs(max_error))
    require(maximum == predicted, "fixed-lift minimax formula")
    require(min_error == -predicted and max_error == predicted,
            "both signed endpoint errors are attained")
    visits = denominator * (2 * bound + 1)
    require(sum(histogram.values()) == visits, "row visit count")
    return {"b": b, "M": denominator, "B": bound, "a": coefficient,
            "cases": visits, "error_histogram": sorted(map(list, histogram.items())),
            "min_error": min_error, "max_error": max_error,
            "max_abs_error": maximum, "min_witness": min_witness,
            "max_witness": max_witness, "bound": predicted}


def minimum_row(b, bound, rows):
    denominator = 1 << b
    minimum = min(row["max_abs_error"] for row in rows)
    nearest = (denominator + 1) // 3
    nearest_rows = [row for row in rows if row["a"] == nearest]
    require(len(nearest_rows) == 1, "nearest lift belongs to declared window")
    nearest_error = nearest_rows[0]["max_abs_error"]
    theorem = ceil_div(bound, denominator)
    require(minimum == nearest_error == theorem, "integer-lift minimax formula")
    return {"b": b, "M": denominator, "B": bound,
            "window_min_error": minimum, "theorem_min_error": theorem,
            "nearest_a": nearest, "nearest_error": nearest_error,
            "minimizing_a_list_in_window":
                [row["a"] for row in rows if row["max_abs_error"] == minimum]}


def period_checks():
    count = 0
    for b in BITS:
        denominator = 1 << b
        coefficients = [denominator // 3 - 3, (denominator + 1) // 3,
                        denominator // 3 + 3]
        for helper in range(denominator):
            for period in PERIODS:
                shifted = helper + period * denominator
                require(reader(shifted, denominator)
                        == reader(helper, denominator) + 3 * period,
                        "signed reader period")
                for coefficient in coefficients:
                    for x in [-31, -1, 0, 1, 31]:
                        require(execute(x, shifted, coefficient, denominator)
                                == execute(x, helper, coefficient, denominator),
                                "negative/positive dirty-period error invariance")
                        count += 1
    return {"period_multipliers": PERIODS, "source_inputs": [-31, -1, 0, 1, 31],
            "coefficients": "floor(M/3)-3, nearest, floor(M/3)+3",
            "error_comparisons": count, "passed": True}


def expect_rejection(callback, name):
    try:
        callback()
    except (VerificationError, json.JSONDecodeError):
        return name
    raise VerificationError("control did not reject: " + name)


def controls():
    # Independently rounding the negative read is not the specified inverse.
    wrong_inverse_gain = reader(1, 2) + reader(-1, 2)
    require(wrong_inverse_gain == 1 and execute(0, 1, 1, 2) == 0,
            "half-tie wrong-inverse control")
    numerator, divisor = -6 + 4, 8
    truncated = -(abs(numerator) // divisor)
    require(reader(-1, 4) == -1 and truncated == 0,
            "negative truncation control")
    helper, x, coefficient = 1, 1, 1
    helper += coefficient * x
    missing_restore_gain = reader(helper, 4) - reader(helper, 4)
    require(helper != 1 and missing_restore_gain == 0,
            "omitted restoration control")
    wrong_lift_error = execute(1, 0, 4, 4)
    require(wrong_lift_error == 2, "coarse-scale lift is not a fine-helper lift")
    require(abs(3 * 1 - 4) == 1 and execute(-1, 3, 1, 4) == 1,
            "fine-output quarter-error versus coarse-output unit-error")
    rejected = [expect_rejection(lambda: execute(1, 0, 1.0, 4), "noninteger lift"),
                expect_rejection(lambda: reader(True, 4), "boolean helper"),
                expect_rejection(lambda: reader(1, 0), "zero denominator")]
    rejected += [expect_rejection(lambda: json.loads('{"x":1,"x":2}',
                         object_pairs_hook=unique_object), "duplicate receipt key"),
                 expect_rejection(lambda: json.loads('NaN', parse_constant=reject_constant),
                                  "nonfinite receipt number")]
    require(not same_typed({"x": 1}, {"x": True}), "bool/int receipt mutation")
    require(not same_typed({"x": 1}, {"x": 1.0}), "float/int receipt mutation")
    require(not same_typed({"x": 1}, {"x": 1, "extra": 0}), "extra receipt key")
    require(ceil_div(-3, 2) == -1 and reader(-1, 1) == -3, "signed ceiling and b0")
    return {"wrong_negative_reader_half_tie_gain": wrong_inverse_gain,
            "negative_truncation": {"correct": -1, "wrong": truncated},
            "omitted_restoration": {"initial_helper": 1, "final_helper": helper,
                                    "wrong_gain": missing_restore_gain},
            "wrong_lift_error": wrong_lift_error,
            "fine_output_example": {"M": 4, "a": 1, "B": 1,
                                    "fine_physical_max_error": [1, 4],
                                    "coarse_max_error": 1},
            "rejected_inputs": rejected, "typed_receipt_mutations_rejected": 3}


def compute():
    manifest = authenticate()
    rows = []
    minima = []
    for b in BITS:
        denominator = 1 << b
        for bound in BOUNDS:
            group = [enumerate_row(b, bound, denominator // 3 + offset)
                     for offset in OFFSETS]
            rows.extend(group)
            minima.append(minimum_row(b, bound, group))
    visits = sum(row["cases"] for row in rows)
    require(len(rows) == 441 and len(minima) == 63 and visits == 454279,
            "declared complete finite domain")
    return {"schema_version": 1, "source_manifest_sha256": SOURCE_HASH,
            "case_manifest_sha256": CASES_HASH, "code_sha256": sha(Path(__file__).read_bytes()),
            "counts": {"rows": len(rows), "minima": len(minima), "visits": visits,
                       "source_documents": len(manifest["files"]),
                       "literal_calls_per_visit": 4},
            "rows": rows, "minima": minima,
            "negative_period_checks": period_checks(), "controls": controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write a newly computed receipt")
    parser.add_argument("--artifact", type=Path, default=ROOT / "RESULT.json",
                        help="strictly compare retained receipt (default RESULT.json)")
    arguments = parser.parse_args()
    result = compute()
    if arguments.emit is not None:
        arguments.emit.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                  encoding="utf-8")
        require(same_typed(read_json(arguments.emit), result), "emitted receipt round trip")
        mode = "emitted"
    else:
        retained = read_json(arguments.artifact)
        require(same_typed(retained, result), "retained receipt mismatch (strict types/keys)")
        mode = "verified"
    print(json.dumps({"status": "pass", "mode": mode, "rows": len(result["rows"]),
                      "visits": result["counts"]["visits"],
                      "source_manifest_sha256": SOURCE_HASH}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (VerificationError, ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
