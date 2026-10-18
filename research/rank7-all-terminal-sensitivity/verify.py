#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify sharp occurrence-level sensitivity of the 22 terminal widenings."""

import argparse
import gzip
import hashlib
import io
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from frames import require, terminal_changes

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = "research/rank7-joint-endframes/"
WIDTHS = (4, 5, 6, 7, 8, 9)
CAPS = (8, 16, 32, 48)
IDLE = (1, 3, 5, 48)
NORMALIZER = 73 * 896


def pairs(entries):
    result = {}
    for key, value in entries:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    raw = path.read_bytes()
    require(len(raw) <= 2_000_000, "compressed/source size limit")
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(32_000_001)
        require(len(raw) <= 32_000_000, "decompressed size limit")
    return json.loads(raw, object_pairs_hook=pairs)


def authenticate():
    sources = read_json(PACKAGE / "SOURCES.json")
    live = [entry for entry in sources["files"] if entry["usage"] == "input"]
    require(len(live) == 7, "complete live source closure")
    for entry in live:
        path = ROOT / entry["path"]
        require(not path.is_symlink() and path.is_file(), "regular live source")
        require(path.stat().st_size <= 2_000_000, "live source byte limit")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"],
                "source SHA256: " + entry["path"])
    return {entry["path"]: entry["sha256"] for entry in live}


def load_tariffs():
    # This one authenticated canonical-main module imports only the standard library.
    sys.path.insert(0, str(ROOT / "research/coupled-cap-independent"))
    import arithmetic
    require(Path(arithmetic.__file__).resolve()
            == ROOT / "research/coupled-cap-independent/arithmetic.py",
            "exact tariff module")
    return arithmetic


def patterns():
    result = []
    for capacity in CAPS:
        layer = [()]
        for _ in range(capacity // min(WIDTHS) + 1):
            result.extend((capacity, widths) for widths in layer)
            layer = [widths + (w,) for widths in layer for w in WIDTHS
                     if (not widths or w >= widths[-1]) and sum(widths) + w <= capacity]
    require(len(result) == len(set(result)) == 2551, "all capacity patterns")
    return result


def features(capacity, widths):
    return [Q(capacity == c) for c in CAPS] + [Q(widths.count(w)) for w in WIDTHS]


def solve(matrix, values):
    size = len(matrix)
    require(size == len(values) == 10, "ten dual equations")
    require(all(len(row) == size for row in matrix), "square matrix")
    require(all(len(row) == 4 for row in values), "four formal costs")
    rows = [list(a) + list(b) for a, b in zip(matrix, values, strict=True)]
    for column in range(size):
        pivot = next((r for r in range(column, size) if rows[r][column]), None)
        require(pivot is not None, "nonsingular dual basis")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for row in range(size):
            if row != column:
                multiplier = rows[row][column]
                rows[row] = [a - multiplier * b
                             for a, b in zip(rows[row], rows[column], strict=True)]
    return [row[size:] for row in rows]


def polynomial(terms):
    result = {}
    for coefficient, vector in terms:
        for rank, value in vector.items():
            result[rank] = result.get(rank, Q(0)) + coefficient * value
    return {r: c for r, c in result.items() if c}


def interval(coefficients, costs):
    lower = sum(c * costs[r][int(c < 0)] for r, c in coefficients.items())
    upper = sum(c * costs[r][int(c > 0)] for r, c in coefficients.items())
    return lower, upper


def dual_certificate(certificate, local, inventory, costs):
    domain = patterns()
    basis = [(entry["capacity"], tuple(sorted(entry["widths"])))
             for entry in certificate["basis_patterns"]]
    require(len(basis) == len(set(basis)) == 10, "distinct dual basis")
    require(all(p in domain for p in basis), "feasible dual basis")
    matrix = [features(*p) for p in basis]
    formal = [[Q(c - sum(ws) == rank) for rank in IDLE] for c, ws in basis]
    dual = [dict(zip(IDLE, row, strict=True)) for row in solve(matrix, formal)]
    rhs = [Q(n) for n in (672, 448, 448, 448)] + [Q(9 * inventory[w]) for w in WIDTHS]
    amounts = [Q(e["count_per_replica"]) for e in certificate["basis_patterns"]]
    require(all(n >= 0 for n in amounts), "nonnegative original primal")
    for column, target in enumerate(rhs):
        require(sum(n * row[column] for n, row in zip(amounts, matrix, strict=True))
                == target, "original primal conservation")
    strict, tight, margins = 0, 0, []
    for capacity, widths in domain:
        idle = capacity - sum(widths)
        terms = [(Q(-n), row) for n, row in zip(features(capacity, widths), dual, strict=True)]
        coefficients = polynomial(terms + [(Q(1), {idle: Q(1)})] if idle else terms)
        if coefficients:
            margin = interval(coefficients, costs)[0]
            require(margin > 0, "negative or uncertified dual pattern")
            margins.append(margin)
            strict += 1
        else:
            tight += 1
    require((tight, strict) == (12, 2539), "complete dual partition")
    base = polynomial(list(zip(rhs, dual, strict=True)) +
                      [(Q(9), {r: Q(n) for r, n in local.items()})])
    return dual, base, min(margins)


def sensitivity(dual, width):
    require(width in (6, 7), "audited width changes only")
    return polynomial([(Q(9), {1: Q(1)}),
                       (Q(-9), dual[4 + WIDTHS.index(width)]),
                       (Q(9), dual[4 + WIDTHS.index(width + 1)])])


def strings(coefficients):
    return {str(r): str(c) for r, c in sorted(coefficients.items())}


def check_providers(record, certificate):
    provider_rows = []
    for provider in ("base", "extra"):
        word = read_json(ROOT / SOURCE / f"data/WORD-{provider}.json.gz")
        rows, local, inventory = terminal_changes(word, record)
        require(dict(local) == {int(r): n for r, n in certificate["local_per_call"].items()},
                "certificate local binding")
        require(dict(inventory) == {int(r): n for r, n in certificate["inventory_per_call"].items()},
                "certificate width binding")
        require(len(word["cleanup"]) == 5207 and len(word["helper_final"]) == 91,
                "unchanged cleanup stock")
        provider_rows.append(rows)
    require(provider_rows[0] == provider_rows[1], "both providers' terminal controls agree")
    return provider_rows[0], local, inventory


def singleton_primals(certificate, local, inventory, costs, base, delta):
    matrix = [features(e["capacity"], tuple(e["widths"]))
              for e in certificate["basis_patterns"]]
    transpose = [list(row) for row in zip(*matrix, strict=True)]
    result = {}
    expected = polynomial([(Q(74), base), (Q(1, 9), delta)])
    for width in (6, 7):
        rhs = [Q(74 * n) for n in (672, 448, 448, 448)] + [Q(666 * inventory[w]) for w in WIDTHS]
        rhs[4 + WIDTHS.index(width)] -= 1
        rhs[4 + WIDTHS.index(width + 1)] += 1
        amounts = [row[0] for row in solve(transpose, [[v] * 4 for v in rhs])]
        require(all(n >= 0 for n in amounts), "nonnegative singleton primal")
        for row, target in zip(transpose, rhs, strict=True):
            require(sum(n * v for n, v in zip(amounts, row, strict=True)) == target,
                    "singleton capacity and inventory conservation")
        terms = [(Q(666), {r: Q(n) for r, n in local.items()}), (Q(1), {1: Q(1)})]
        terms.extend((n, {e["capacity"] - sum(e["widths"]): Q(1)})
                     for e, n in zip(certificate["basis_patterns"], amounts, strict=True)
                     if e["capacity"] != sum(e["widths"]))
        full = polynomial(terms)
        require(full == expected, "singleton primal equals dual lower bound")
        bounds = tuple(v / (74 * NORMALIZER) for v in interval(full, costs))
        require(bounds[1] < 1, "one-change fractional positive control")
        result[str(width)] = {"basis_amounts_at_T74": list(map(str, amounts)),
                              "moment": list(map(str, bounds))}
    return result


def compute():
    hashes = authenticate()
    tariffs = load_tariffs()
    record = read_json(ROOT / SOURCE / "data/STAGE1-FRAME-EDITS.json")
    certificate = read_json(ROOT / SOURCE / "certificates/RELAX-CAP.json")
    claim = read_json(ROOT / SOURCE / "CLAIM.json")
    require(claim["calls"] == 666 and claim["replicas"] == 74, "literal call counts")
    target = Q(claim["complex_lower"])
    costs = {r: tuple(r * x for x in tariffs.power_interval(Q(73, r), target))
             for r in range(1, 49)}
    rows, local, inventory = check_providers(record, certificate)
    dual, base, slack = dual_certificate(certificate, local, inventory, costs)
    delta = sensitivity(dual, 6)
    require(delta == sensitivity(dual, 7), "same sensitivity in both width classes")
    bounds = [interval(polynomial([(Q(1), base), (Q(k), delta)]), costs)[0] / NORMALIZER
              for k in range(23)]
    require(interval(delta, costs)[0] > 0 and all(v > 1 for v in bounds[1:]),
            "every nonempty subset fails")
    profile = {int(r): n for r, n in read_json(ROOT / SOURCE / "allocation/PROFILE.json").items()}
    require(sum(r * n for r, n in profile.items()) == 65088 * 74, "complete literal rank mass")
    require(profile == {int(r): n for r, n in claim["profile"].items()}, "literal claim profile")
    require(all(profile.get(r, 0) >= 666 * n for r, n in local.items()), "all local calls paid")
    literal = tariffs.moment(profile, target, 74)
    require(literal[1] < 1 and bounds[0] < 1, "unchanged original positive control")
    occurrence_bounds = {str(k): interval(polynomial([(Q(1), base), (Q(k, 666), delta)]), costs)[0]
                         / NORMALIZER for k in (0, 1, 2, 22 * 666)}
    require(occurrence_bounds["2"] > Q(1000000000041, 10**12), "two occurrences already fail")
    primals = singleton_primals(certificate, local, inventory, costs, base, delta)
    return {"status": "PASS_ALL_TERMINAL_SENSITIVITY", "source_sha256": hashes,
            "target_complex_saving": str(target), "endpoints": rows,
            "providers": 2, "nonempty_subsets": (1 << len(rows)) - 1,
            "potential_occurrences": 22 * 666, "sharp_fractional_failure_count": 2,
            "normalized_lower_by_occurrence_count": {k: str(v) for k, v in occurrence_bounds.items()},
            "singleton_fractional_primals": primals,
            "patterns": 2551, "tight": 12, "strict": 2539,
            "dual_formal_costs": [strings(row) for row in dual],
            "base_polynomial": strings(base), "per_widening_polynomial": strings(delta),
            "normalized_lower_by_count": {str(k): str(v) for k, v in enumerate(bounds)},
            "literal_original_moment": [str(v) for v in literal],
            "minimum_strict_reduced_cost": str(slack),
            "nominal_stock": 66304 + 408 + 8 + 91 + 2,
            "scope": "Fixed final scalar gates, partner frames, later stages, cleanup and capacity pool; no supplier admission."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit regenerated receipt to stdout")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == read_json(PACKAGE / "RESULT.json"), "complete receipt equality")
        print("PASS_ALL_TERMINAL_SENSITIVITY endpoints=22 occurrences=14652 fractional_failure_count=2 patterns=2551")


if __name__ == "__main__":
    main()
