#!/usr/bin/env python3
"""Exact finite checks of the fractional-column resolvent envelope.

New implementation by ToikY with substantial OpenAI Codex assistance.
The all-real theorem is written separately; no predecessor code is executed.
"""

import hashlib
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
RHOS = (Q(1, 3), Q(1, 2), Q(2, 3))
BETAS = tuple(map(Q, (1,))) + (Q(5, 4), Q(4, 3), Q(3, 2),
                              Q(7, 4), Q(2), Q(5, 2), Q(3), Q(4))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encode(value):
    if isinstance(value, Q):
        return [value.numerator, value.denominator]
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def canonical(value):
    return (json.dumps(encode(value), sort_keys=True,
                       separators=(",", ":")) + "\n").encode()


def reject_constant(value):
    raise ValueError("non-finite JSON number: " + value)


def reject_float(value):
    raise ValueError("non-integer JSON number: " + value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def strict_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=reject_constant, parse_float=reject_float)


def domain(n, rho, beta):
    need(type(n) is int and n >= 1, "positive integer dimension")
    need(type(rho) is Q and 0 < rho < 1, "rho must be in (0,1)")
    need(type(beta) is Q and beta >= 1, "beta must be at least one")


def envelope(n, rho, beta):
    """Partial-sum recurrence; no transport matrix is read or constructed."""
    domain(n, rho, beta)
    if beta == 1:
        return [Q(0)] + [1 / (1 - rho)] * n
    values = [Q(0)]
    for k in range(1, n + 1):
        q = Q(k) // beta
        delta = k - beta * q
        need(0 <= q < k and 0 <= delta < beta, "recurrence index")
        numerator = 1 + rho * (beta - delta) * values[q]
        diagonal = Q(0)
        if delta and q + 1 == k:
            diagonal = rho * delta
        elif delta:
            numerator += rho * delta * values[q + 1]
        need(diagonal < 1, "positive recurrence denominator")
        values.append(numerator / (1 - diagonal))
    return values


def overlap_matrix(n, rho, beta):
    """Literal interval intersections; no recurrence coefficients are used."""
    domain(n, rho, beta)
    rows = []
    for i in range(n):
        row = []
        for j in range(n):
            left = max(Q(i), beta * j)
            right = min(Q(i + 1), beta * (j + 1))
            row.append(rho * max(Q(0), right - left))
        rows.append(row)
    return rows


def admitted(matrix, rho, beta):
    n = len(matrix)
    domain(n, rho, beta)
    need(all(len(row) == n for row in matrix), "square matrix")
    need(all(sum(map(abs, row)) <= rho for row in matrix), "row cap")
    need(all(sum(abs(matrix[i][j]) for i in range(n)) <= beta * rho
             for j in range(n)), "column cap")


def gauss_inverse(matrix):
    """Exact Gauss-Jordan inverse of I-E, independent of triangular solve."""
    n = len(matrix)
    rows = [[Q(i == j) - matrix[i][j] for j in range(n)] +
            [Q(i == j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        need(pivot is not None, "invertible I-E")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [value / scale for value in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                scale = rows[i][j]
                rows[i] = [a - scale * b for a, b in zip(rows[i], rows[j])]
    need(all(rows[i][j] == Q(i == j) for i in range(n) for j in range(n)),
         "Gauss-Jordan identity block")
    return [row[n:] for row in rows]


def check_inverse(matrix, inverse):
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            left = inverse[i][j] - sum(matrix[i][k] * inverse[k][j]
                                       for k in range(n))
            right = inverse[i][j] - sum(inverse[i][k] * matrix[k][j]
                                        for k in range(n))
            need(left == right == Q(i == j), "both inverse compositions")


def column_partials(inverse):
    output = []
    for column in zip(*inverse):
        total = Q(0)
        partials = []
        for value in sorted(map(abs, column), reverse=True):
            total += value
            partials.append(total)
        output.append(partials)
    return output


def bound_columns(partials, bounds):
    need(all(value <= bounds[k + 1] for column in partials
             for k, value in enumerate(column)), "inverse partial-sum bound")


def triangular_column(matrix):
    """Solve the literal lower-triangular equations, not their sum recurrence."""
    values = []
    for i, row in enumerate(matrix):
        need(not any(row[i + 1:]), "lower triangular transport")
        denominator = 1 - row[i]
        need(denominator > 0, "positive triangular diagonal")
        numerator = Q(i == 0) + sum(row[j] * values[j] for j in range(i))
        values.append(numerator / denominator)
    return values


def check_attainment(matrix, rho, beta):
    admitted(matrix, rho, beta)
    values = triangular_column(matrix)
    need(all(a >= b >= 0 for a, b in zip(values, values[1:])),
         "decreasing nonnegative first column")
    total = Q(0)
    partials = [total]
    for value in values:
        total += value
        partials.append(total)
    need(partials == envelope(len(matrix), rho, beta), "attainer partial sums")
    return values, partials


def half_n3(beta):
    need(Q(1) <= beta <= Q(2), "n3 fractional formula domain")
    if beta <= Q(3, 2):
        return (12 * beta * beta - 16 * beta + 6) / (beta * (2 * beta - 1))
    return 5 - 3 / beta


def integer_parent_column(n, rho, branching):
    need(type(branching) is int and branching >= 2, "integer branching")
    values = []
    for i in range(1, n + 1):
        depth, capacity = 0, 1
        while capacity < i:
            capacity *= branching
            depth += 1
        values.append(rho ** depth / (1 - rho))
    return values


def exhaustive_grid():
    digest = hashlib.sha256()
    counts = {"matrices": 0, "inversions": 0, "admitted_cap_cases": 0,
              "column_cases": 0, "partial_sum_comparisons": 0}
    for rho in RHOS:
        for n in (1, 2, 3):
            rows = [r for r in itertools.product(range(3), repeat=n) if sum(r) <= 2]
            cached = {beta: envelope(n, rho, beta) for beta in BETAS}
            for units in itertools.product(rows, repeat=n):
                matrix = [[rho * value / 2 for value in row] for row in units]
                inverse = gauss_inverse(matrix)
                check_inverse(matrix, inverse)
                partials = column_partials(inverse)
                counts["matrices"] += 1
                counts["inversions"] += 1
                accepted = grid_caps(matrix, partials, rho, cached, counts)
                digest.update(canonical([n, rho, units, inverse, accepted]))
    need(counts["matrices"] == 3117, "complete half-row-unit grid count")
    return dict(counts, profile_sha256=digest.hexdigest())


def grid_caps(matrix, partials, rho, cached, counts):
    n = len(matrix)
    ratio = max(sum(row[j] for row in matrix) for j in range(n)) / rho
    accepted = []
    for beta, bounds in cached.items():
        if ratio <= beta:
            admitted(matrix, rho, beta)
            bound_columns(partials, bounds)
            accepted.append(beta)
            counts["admitted_cap_cases"] += 1
            counts["column_cases"] += n
            counts["partial_sum_comparisons"] += n * n
    return accepted


def dense_attainer(matrix, rho, beta):
    inverse = gauss_inverse(matrix)
    check_inverse(matrix, inverse)
    bounds = envelope(len(matrix), rho, beta)
    partials = column_partials(inverse)
    bound_columns(partials, bounds)
    need(sum(row[0] for row in inverse) == bounds[-1], "dense attained column norm")
    need([row[0] for row in inverse] == triangular_column(matrix),
         "dense versus triangular first column")
    return inverse


def attainer_grid():
    digest = hashlib.sha256()
    counts = {"cases": 0, "dense_inversions": 0, "dense_columns": 0,
              "wide_cases": 0, "partial_sums": 0, "integer_parent_cases": 0,
              "half_n3_formula_cases": 0}
    fixture = None
    for n in tuple(range(1, 25)) + (32, 64, 128):
        for rho, beta in itertools.product(RHOS, BETAS):
            matrix = overlap_matrix(n, rho, beta)
            need(all(sum(row) == rho for row in matrix), "full transport row mass")
            values, partials = check_attainment(matrix, rho, beta)
            inverse = dense_attainer(matrix, rho, beta) if n <= 8 else None
            record_attainer(n, rho, beta, values, inverse, counts)
            digest.update(canonical([n, rho, beta, values, partials, inverse]))
            if (n, rho, beta) == (3, Q(1, 2), Q(3, 2)):
                fixture = (matrix, inverse)
    need(fixture is not None, "retained semantic-control fixture")
    return dict(counts, profile_sha256=digest.hexdigest()), fixture


def record_attainer(n, rho, beta, values, inverse, counts):
    counts["cases"] += 1
    counts["partial_sums"] += n
    if inverse is not None:
        counts["dense_inversions"] += 1
        counts["dense_columns"] += n
    if n > 24:
        counts["wide_cases"] += 1
    if beta.denominator == 1 and beta >= 2:
        need(values == integer_parent_column(n, rho, int(beta)),
             "credited integer ceil-log-depth formula")
        counts["integer_parent_cases"] += 1
    if n == 3 and rho == Q(1, 2) and beta <= 2:
        need(sum(values) == half_n3(beta), "n3 two-branch formula")
        counts["half_n3_formula_cases"] += 1


def signed_fixtures():
    digest = hashlib.sha256()
    cases = columns = 0
    for n in range(1, 9):
        signs = [Q((-1) ** i) for i in range(n)]
        for rho, beta in itertools.product(RHOS, (Q(5, 4), Q(3, 2), Q(2))):
            base = overlap_matrix(n, rho, beta)
            matrix = [[signs[i] * base[i][j] * signs[j] for j in range(n)]
                      for i in range(n)]
            admitted(matrix, rho, beta)
            inverse = gauss_inverse(matrix)
            check_inverse(matrix, inverse)
            partials = column_partials(inverse)
            bound_columns(partials, envelope(n, rho, beta))
            first = triangular_column(base)
            need([row[0] for row in inverse] ==
                 [signs[i] * first[i] for i in range(n)], "signed conjugate first column")
            digest.update(canonical([n, rho, beta, matrix, inverse]))
            cases += 1
            columns += n
    return {"cases": cases, "columns": columns, "phases": [1, -1],
            "profile_sha256": digest.hexdigest()}


def expect_rejection(action, expected):
    try:
        action()
    except ValueError as error:
        need(str(error) == expected, "unexpected control rejection: " + str(error))
        return
    raise ValueError("missing control rejection: " + expected)


def controls(fixture):
    matrix, inverse = fixture
    rho, beta = Q(1, 2), Q(3, 2)
    bounds = envelope(3, rho, beta)
    understated = bounds[:-1] + [bounds[-1] - Q(1, 100)]
    changed = [row[:] for row in matrix]
    changed[2][1] -= Q(1, 100)
    changed[2][2] += Q(1, 100)
    admitted(changed, rho, beta)
    bad_row = [[Q(3, 4), Q(0), Q(0)], [Q(0), rho, Q(0)],
               [Q(0), Q(0), rho]]
    tests = [
        ("bad_row_cap", lambda: admitted(bad_row, rho, beta), "row cap"),
        ("bad_column_cap", lambda: admitted(overlap_matrix(3, rho, Q(3)), rho, beta), "column cap"),
        ("understated_envelope", lambda: bound_columns(column_partials(inverse), understated), "inverse partial-sum bound"),
        ("rounded_up_integer_attainer", lambda: admitted(overlap_matrix(3, rho, Q(2)), rho, beta), "column cap"),
        ("changed_admissible_transport", lambda: check_attainment(changed, rho, beta), "attainer partial sums"),
        ("rho_zero", lambda: envelope(3, Q(0), beta), "rho must be in (0,1)"),
        ("rho_one", lambda: envelope(3, Q(1), beta), "rho must be in (0,1)"),
        ("beta_below_one", lambda: envelope(3, rho, Q(3, 4)), "beta must be at least one"),
        ("boolean_dimension", lambda: envelope(True, rho, beta), "positive integer dimension"),
        ("duplicate_json_key", lambda: strict_json('{"a":1,"a":2}'), "duplicate JSON key"),
        ("float_json", lambda: strict_json('{"a":0.5}'), "non-integer JSON number: 0.5"),
        ("nonfinite_json", lambda: strict_json('{"a":NaN}'), "non-finite JSON number: NaN"),
    ]
    for label, action, expected in tests:
        expect_rejection(action, expected)
    return {label: "rejected: " + expected for label, _, expected in tests}


def authenticate_sources():
    path = HERE / "SOURCE-PINS.json"
    need(path.is_file(), "SOURCE-PINS.json required")
    manifest = strict_json(path.read_bytes())
    need(type(manifest) is dict and type(manifest.get("schema_version")) is int
         and manifest["schema_version"] == 1,
         "source manifest schema")
    rows = manifest.get("files")
    need(type(rows) is list and len(rows) == 2, "exactly two mathematical sources")
    seen = set()
    for row in rows:
        need(type(row) is dict, "source row")
        local = row.get("local_path")
        need(type(local) is str and not Path(local).is_absolute() and
             ".." not in Path(local).parts and local not in seen, "source path")
        seen.add(local)
        raw = (HERE / local).read_bytes()
        raw.decode("utf-8")
        need(type(row.get("bytes")) is int and row["bytes"] == len(raw), "source size")
        need(hashlib.sha256(raw).hexdigest() == row.get("sha256"), "source SHA256")
        git = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(git == row.get("git_blob"), "source Git blob")
    return {"objects": len(rows), "bytes": sum(row["bytes"] for row in rows),
            "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def package_hashes():
    return {str(path.relative_to(HERE)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(HERE.rglob("*")) if path.is_file()}


def main():
    need(len(sys.argv) == 1, "no verifier arguments")
    provenance = authenticate_sources()
    grid = exhaustive_grid()
    attainers, fixture = attainer_grid()
    signed = signed_fixtures()
    rejected = controls(fixture)
    receipt = {"status": "PASS_FRACTIONAL_COLUMN_RESOLVENT", "schema_version": 1,
               "domain": {"rhos": RHOS, "betas": BETAS, "exhaustive_n": [1, 2, 3],
                          "attainer_n": list(range(1, 25)) + [32, 64, 128]},
               "grid": grid, "attainers": attainers, "signed_fixtures": signed,
               "rejection_controls": rejected, "provenance": provenance,
               "package_sha256": package_hashes(),
               "methods": ["Fraction Gauss-Jordan: both inverse compositions",
                           "literal interval overlap and direct triangular first-column solve",
                           "independent rational partial-sum recurrence",
                           "integer ceil-log depth without floating logarithms"],
               "limits": "Finite rational corroboration, not proof of all-real parameters; complex theorem uses written Neumann comparison. Only real sign-phase fixtures executed. No predecessor code imported or executed; no Gaussian caller, precision or physical tariff admission."}
    print(json.dumps(encode(receipt), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_FRACTIONAL_COLUMN_RESOLVENT: " + str(error), file=sys.stderr)
        raise SystemExit(1)
