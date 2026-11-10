#!/usr/bin/env python3
"""Independent raw quotient-algebra oracle for the unequal(2,3) handoff.

Credits: Nick Petalas6682/6578; Ali Romman5316/5459; the retained5252
and tensor-atlas lineage. No predecessor implementation is imported.
Substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from collections import Counter
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
PIN_SHA = "e9e770f3a98ed8366e254ad33c3970e95a77e255c95d6128ff6897e14b13cc41"
CASE_SHA = "0449dbb927e385e63a14d5c5366f65bd91a99a341c05e2a6373ea0de1e05bd0c"
BASIS = ((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2))
ZERO = (0,) * 6
ONE = (1, 0, 0, 0, 0, 0)
COMMON = ("schema_version", "source_manifest_sha256", "case_manifest_sha256", "census", "witnesses")
FIELDS = ((2, 2, None), (3, 3, None), (4, 2, 7), (5, 5, None))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_value(value):
    return sha((canonical(value) + "\n").encode())


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_number(token):
    raise ValueError("JSON noninteger number forbidden: " + token)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=reject_number, parse_float=reject_number)


def integer(value, label):
    require(type(value) is int, label + " must be integer, not bool")
    return value


def digest_text(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def check_hash(raw, expected):
    require(sha(raw) == expected, "authenticated source/case digest changed")


def authenticate():
    raw = (ROOT / "SOURCE-PINS.json").read_bytes()
    check_hash(raw, PIN_SHA)
    manifest = parse(raw)
    require(len(manifest["files"]) == 6, "six inert source objects required")
    for entry in manifest["files"]:
        data = (ROOT / entry["local_path"]).read_bytes()
        require(len(data) == entry["bytes"], "source byte count changed")
        check_hash(data, entry["sha256"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == entry["git_blob"], "source Git blob changed")
    raw = (ROOT / "CASES.json").read_bytes()
    check_hash(raw, CASE_SHA)
    cases = parse(raw)
    require(cases["basis_exponents"] == [list(item) for item in BASIS], "basis changed")
    expected = [{"q": q, "p": p, "modulus": modulus} for q, p, modulus in FIELDS]
    require(cases["full_census_fields"] == expected, "field domain changed")
    require(cases["witness_prime_fields"] == [7, 13], "witness fields changed")


def extension_product(a, b):
    value = 0
    for index in range(2):
        if b & (1 << index):
            value ^= a << index
    if value & 4:
        value ^= 7
    return value


def field(q, modulus=None):
    integer(q, "field size")
    require(q in (2, 3, 4, 5, 7, 13), "unsupported oracle field")
    require((q == 4 and modulus == 7) or (q != 4 and modulus is None),
            "wrong field polynomial")
    addition = [[a ^ b if q == 4 else (a + b) % q for b in range(q)] for a in range(q)]
    multiply = [[extension_product(a, b) if q == 4 else a * b % q for b in range(q)] for a in range(q)]
    negative = [next(b for b in range(q) if addition[a][b] == 0) for a in range(q)]
    inverse = [0] + [next(b for b in range(1, q) if multiply[a][b] == 1) for a in range(1, q)]
    return {"q": q, "p": 2 if q == 4 else q, "add": addition,
            "mul": multiply, "neg": negative, "inv": inverse}


def quotient(x_cutoff=2, y_cutoff=3):
    require(type(x_cutoff) is int and type(y_cutoff) is int and (x_cutoff, y_cutoff) == (2, 3),
            "only fixed unequal cutoffs(2,3) supported")
    index = {exponents: position for position, exponents in enumerate(BASIS)}
    return [[index.get((a[0] + b[0], a[1] + b[1]), -1) for b in BASIS] for a in BASIS]


TABLE = quotient()


def multiply(left, right, f):
    result = [0] * 6
    add, mul = f["add"], f["mul"]
    for i, a in enumerate(left):
        if a:
            for j, b in enumerate(right):
                position = TABLE[i][j]
                if b and position >= 0:
                    result[position] = add[result[position]][mul[a][b]]
    return tuple(result)


def image_columns(x, y, y_squared, f):
    return (ONE, x, y, multiply(x, y, f), y_squared, multiply(x, y_squared, f))


def determinant(columns, f):
    matrix = [list(row) for row in zip(*columns)]
    add, mul, neg, inv = f["add"], f["mul"], f["neg"], f["inv"]
    result = 1
    for column in range(6):
        pivot = next((row for row in range(column, 6) if matrix[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            matrix[pivot], matrix[column] = matrix[column], matrix[pivot]
            result = neg[result]
        value = matrix[column][column]
        result = mul[result][value]
        for row in range(column + 1, 6):
            ratio = mul[matrix[row][column]][inv[value]]
            if ratio:
                for j in range(column + 1, 6):
                    matrix[row][j] = add[matrix[row][j]][neg[mul[ratio][matrix[column][j]]]]
                matrix[row][column] = 0
    return result


def power(value, exponent, f):
    result = 1
    for _ in range(exponent):
        result = f["mul"][result][value]
    return result


def vector(value, f):
    require(type(value) in (list, tuple) and len(value) == 6, "six coefficients required")
    require(all(type(item) is int and 0 <= item < f["q"] for item in value),
            "coefficients must be canonical field integers")
    require(value[0] == 0, "generator images must have zero constant")
    return tuple(value)


def checked_map(x, y, f):
    x, y = vector(x, f), vector(y, f)
    y2 = multiply(y, y, f)
    require(multiply(x, x, f) == ZERO, "X squared relation fails")
    require(multiply(y, y2, f) == ZERO, "Y cubed relation fails")
    columns = image_columns(x, y, y2, f)
    value = determinant(columns, f)
    require(value != 0, "substitution matrix is singular")
    return columns, value


def product_check(columns, f):
    require(columns[0] == ONE, "substitution must preserve one")
    for i in range(6):
        for j in range(6):
            expected = ZERO if TABLE[i][j] < 0 else columns[TABLE[i][j]]
            require(multiply(columns[i], columns[j], f) == expected,
                    "literal basis product not preserved")


def relation_candidates(f):
    square_zero, cube_zero = [], []
    for coefficients in product(range(f["q"]), repeat=5):
        value = (0, *coefficients)
        squared = multiply(value, value, f)
        if squared == ZERO:
            square_zero.append(value)
        if multiply(value, squared, f) == ZERO:
            cube_zero.append((value, squared))
    return square_zero, cube_zero


def census(f):
    xs, ys = relation_candidates(f)
    accepted, counts = [], Counter()
    actual_matrices, literal_checks = 0, 0
    for x in xs:
        for y, y2 in ys:
            columns = image_columns(x, y, y2, f)
            actual = determinant(columns, f)
            actual_matrices += 1
            if actual:
                accepted.append(list(x[1:] + y[1:]))
                counts[actual] += 1
                predicted = f["mul"][power(x[1], 3, f)][power(y[2], 6, f)]
                require(actual == predicted, "full determinant disagrees with filtration character")
                if literal_checks < 16:
                    product_check(columns, f)
                    literal_checks += 1
    require(accepted == sorted(accepted), "accepted coefficient rows not lexicographic")
    require(len(accepted) == len({tuple(row) for row in accepted}), "duplicate accepted map")
    row = {"q": f["q"], "p": f["p"], "accepted_count": len(accepted),
           "accepted_map_sha256": digest_value(accepted),
           "determinant_counts": {str(key): counts[key] for key in sorted(counts)}}
    diagnostic = {"radical_vectors_per_generator": f["q"] ** 5, "square_zero_candidates": len(xs),
                  "cube_zero_candidates": len(ys), "relation_pairs_with_actual_matrix_determinant": actual_matrices,
                  "full_basis_product_maps": literal_checks}
    return row, accepted, diagnostic


def witnesses():
    result = []
    for q in (7, 13):
        f = field(q)
        for a in range(1, q):
            for d in range(1, q):
                x, y = (0, a, 0, 1, 0, 2), (0, 0, d, 1, 1, 1)
                columns, actual = checked_map(x, y, f)
                product_check(columns, f)
                result.append([q, a, d, actual])
    return result


def validate_receipt(value):
    require(type(value) is dict, "receipt must be object")
    require(set(value) == set(COMMON), "receipt keys must match schema v1")
    require(type(value["schema_version"]) is int and value["schema_version"] == 1,
            "receipt schema_version must be integer1")
    require(digest_text(value["source_manifest_sha256"]) and digest_text(value["case_manifest_sha256"]),
            "receipt source/case digest malformed")
    rows = value["census"]
    require(type(rows) is list and len(rows) == 4, "four census fields required")
    for row, (q, p, _) in zip(rows, FIELDS):
        keys = {"q", "p", "accepted_count", "accepted_map_sha256", "determinant_counts"}
        require(type(row) is dict and set(row) == keys, "census row keys invalid")
        require(integer(row["q"], "q") == q and integer(row["p"], "p") == p, "census field order invalid")
        require(integer(row["accepted_count"], "count") > 0, "accepted count must be positive")
        require(digest_text(row["accepted_map_sha256"]), "map digest malformed")
        counts = row["determinant_counts"]
        require(type(counts) is dict and bool(counts), "determinant counts must be nonempty object")
        for key, count in counts.items():
            require(type(key) is str and key in [str(i) for i in range(1, q)], "determinant key invalid")
            require(integer(count, "determinant count") > 0, "determinant count must be positive")
        require(sum(counts.values()) == row["accepted_count"], "determinant total differs")
    expected_pairs = [(q, a, d) for q in (7, 13) for a in range(1, q) for d in range(1, q)]
    require(type(value["witnesses"]) is list and len(value["witnesses"]) == len(expected_pairs),
            "witness domain differs")
    for row, expected_pair in zip(value["witnesses"], expected_pairs):
        require(type(row) is list and len(row) == 4 and all(type(item) is int for item in row),
                "witness must be four integers")
        require(tuple(row[:3]) == expected_pair and 1 <= row[3] < row[0], "witness field/order invalid")


def rejected(function, argument):
    try:
        function(argument)
    except ValueError:
        return True
    return False


def controls(receipt):
    f2, f3, f4, f5 = field(2), field(3), field(4, 7), field(5)
    x, y = (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0)
    shear = (0, 1, 1, 0, 0, 0)
    nonlinear_x = (0, 1, 0, 0, 1, 0)
    constant = (1, 1, 0, 0, 0, 0)
    scale4 = (0, 2, 0, 0, 0, 0)
    columns4, det4 = checked_map(scale4, y, f4)
    result = {"unsupported_field_rejected": rejected(field, 6),
              "boolean_field_rejected": rejected(field, True),
              "wrong_cutoff_rejected": rejected(lambda n: quotient(2, n), 4),
              "nonrelation_rejected": rejected(lambda v: checked_map(v, y, f5), y),
              "constant_rejected": rejected(lambda v: checked_map(v, y, f3), constant),
              "singular_substitution_rejected": rejected(lambda v: checked_map(v, y, f2), ZERO),
              "char3_triangular_shear_accepted": checked_map(x, shear, f3)[1] != 0,
              "same_shear_rejected_char2": rejected(lambda v: checked_map(x, v, f2), shear),
              "same_shear_rejected_char5": rejected(lambda v: checked_map(x, v, f5), shear),
              "char2_nonlinear_exception_accepted": checked_map(nonlinear_x, y, f2)[1] != 0,
              "same_nonlinear_term_rejected_char3": rejected(lambda v: checked_map(v, y, f3), nonlinear_x),
              "same_nonlinear_term_rejected_char5": rejected(lambda v: checked_map(v, y, f5), nonlinear_x),
              "tangent_determinant_is_not_full_determinant": det4 != f4["mul"][scale4[1]][y[2]],
              "variable_swap_rejected": rejected(lambda v: checked_map(v, x, f5), y),
              "duplicate_json_rejected": rejected(parse, '{"v":1,"v":2}'),
              "nonfinite_json_rejected": rejected(parse, '{"v":NaN}'),
              "float_json_rejected": rejected(parse, '{"v":1.0}')}
    bad_version = dict(receipt)
    bad_version["schema_version"] = True
    bad_missing = dict(receipt)
    del bad_missing["census"]
    bad_count = parse(canonical(receipt))
    bad_count["census"][0]["accepted_count"] = True
    result["boolean_schema_rejected"] = rejected(validate_receipt, bad_version)
    result["missing_profile_rejected"] = rejected(validate_receipt, bad_missing)
    result["boolean_count_rejected"] = rejected(validate_receipt, bad_count)
    result["source_digest_guard_rejects_drift"] = rejected(lambda raw: check_hash(raw, sha(b"source")), b"drift")
    require(all(type(item) is bool and item for item in result.values()), "semantic control failed")
    product_check(columns4, f4)
    return result


def generate():
    authenticate()
    rows, accepted_maps, diagnostics = [], {}, {}
    for q, _, modulus in FIELDS:
        row, accepted, diagnostic = census(field(q, modulus))
        rows.append(row)
        accepted_maps[str(q)] = accepted
        diagnostics[str(q)] = diagnostic
    receipt = {"schema_version": 1, "source_manifest_sha256": PIN_SHA, "case_manifest_sha256": CASE_SHA,
               "census": rows, "witnesses": witnesses()}
    validate_receipt(receipt)
    report = {"code_sha256": sha(Path(__file__).read_bytes()), "domains": diagnostics,
              "controls": controls(receipt)}
    return receipt, accepted_maps, report


def load_maps(path):
    with gzip.open(path, "rb") as stream:
        raw = stream.read(16777217)
    require(len(raw) <= 16777216, "accepted-map certificate exceeds16MiB")
    data = parse(raw)
    require(type(data) is dict and set(data) == {str(q) for q, _, _ in FIELDS}, "map certificate field keys invalid")
    for key, rows in data.items():
        q = int(key)
        require(type(rows) is list, "map certificate rows must be list")
        for row in rows:
            require(type(row) is list and len(row) == 10 and all(type(item) is int and 0 <= item < q for item in row),
                    "map certificate row must be ten canonical integers")
        require(rows == sorted(rows) and len(rows) == len({tuple(row) for row in rows}),
                "map certificate must be unique and lexicographic")
    return data


def compare_primary(receipt, maps, primary, actual_maps):
    validate_receipt(primary)
    for key in COMMON:
        require(canonical(receipt[key]) == canonical(primary[key]), "independent primary mismatch: " + key)
    require(canonical(maps) == canonical(actual_maps), "actual primary accepted-map certificate mismatch")
    return sum(len(rows) for rows in maps.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-first", "--emit", dest="write_first", type=Path)
    parser.add_argument("--check-primary", type=Path)
    args = parser.parse_args()
    require(not (args.write_first and args.check_primary), "first receipt must remain blind")
    frozen, primary, actual_maps = None, None, None
    if not args.write_first:
        frozen = parse((ROOT / "ORACLE.json").read_bytes())
        validate_receipt(frozen)
    if args.check_primary:
        primary = parse(args.check_primary.read_bytes())
        validate_receipt(primary)
        actual_maps = load_maps(args.check_primary.parent / "ACCEPTED-MAPS.json.gz")
    receipt, maps, diagnostics = generate()
    if args.write_first:
        with args.write_first.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(canonical(receipt) == canonical(frozen), "frozen oracle receipt mismatch")
    if args.check_primary:
        count = compare_primary(receipt, maps, primary, actual_maps)
        print("PASS_ACTUAL_PRIMARY_ACCEPTED_MAPS count=" + str(count))
    print("ORACLE_DIAGNOSTICS " + canonical(diagnostics))
    print("PASS_UNEQUAL_QUADRATIC_CUBIC_ORACLE fields=4 witnesses=180")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as error:
        print("FAIL_UNEQUAL_QUADRATIC_CUBIC_ORACLE: " + str(error), file=sys.stderr)
        sys.exit(1)
