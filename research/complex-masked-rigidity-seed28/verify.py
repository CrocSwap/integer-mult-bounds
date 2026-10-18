#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact covariance evidence and semantic controls for one-sided mask rigidity.

Python 3.10+, standard library; no floating point or disabled-assertion checks.
The separately written tensor_oracle.py checks every concrete local span.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, indent=2) + "\n"


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def roots():
    """One first-nonzero-positive representative per line, doubled coordinates."""
    result = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            result.add(tuple(row))
    for tail in itertools.product((-1, 1), repeat=7):
        row = (1,) + tail
        if sum(x < 0 for x in row) % 2 == 0:
            result.add(row)
    return sorted(result)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def covariance(rows):
    return [[sum(r[a] * r[b] for r in rows) for b in range(8)]
            for a in range(8)]


def rank_q(rows):
    pivots = {}
    for row in rows:
        v = [Fraction(x) for x in row]
        for col, basis in sorted(pivots.items()):
            if v[col]:
                scalar = v[col]
                v = [x - scalar * y for x, y in zip(v, basis)]
        pivot = next((i for i, x in enumerate(v) if x), None)
        if pivot is not None:
            scalar = v[pivot]
            pivots[pivot] = [x / scalar for x in v]
    return len(pivots)


def check_geometry(lines, perpendicular_constant=72):
    require(len(lines) == 120 and len(set(lines)) == 120, "120 distinct root lines required")
    require(all(len(r) == 8 and dot(r, r) == 8 for r in lines), "wrong root norm")
    require(covariance(lines) == [[120 * (a == b) for b in range(8)] for a in range(8)],
            "whole-root covariance mismatch")
    counts = []
    for r in lines:
        perpendicular = [s for s in lines if dot(r, s) == 0]
        require(len(perpendicular) == 63, "orthogonal-neighbour count mismatch")
        expected = [[perpendicular_constant * (a == b) - 9 * r[a] * r[b]
                     for b in range(8)] for a in range(8)]
        require(covariance(perpendicular) == expected, "perpendicular covariance mismatch")
        counts.append(len(perpendicular))
    require(all(dot(r, s) % 4 == 0 for r in lines for s in lines), "nonintegral true Gram")
    return {"root_lines": 120, "coordinate_convention": "doubled; first nonzero positive; lexicographic",
            "roots_sha256": digest(lines), "whole_covariance": "120 I_8",
            "perpendicular_covariance": "72 I_8 - 9 q q^T", "orthogonal_counts": sorted(set(counts)),
            "covariance_entries_checked": 64 * 121,
            "geometric_cover_limit": 8,
            "two_set_lower_margins_doubled": {"perpendicular": 56, "whole": 104}}


def reject(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("control failed to reject: " + message)


def semantic_controls(lines):
    frame = set()
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[i + 1] = 2, 2 * sign
            frame.add(tuple(row))
    live = [q for q in lines if q not in frame]
    require(len(live) == 112, "P112 size")
    pairs = [(i, j) for i, r in enumerate(live) for j, s in enumerate(live)]
    mask = lambda i, j: (dot(live[i], live[j]) // 4) % 2 == 0
    gram2 = lambda i, j: Fraction(dot(live[i], live[j]), 2)
    require(all(mask(i, i) for i in range(112)), "diagonals must be masked")

    # Omitting diagonals admits X=G, whose remaining even entries vanish.
    require(all(dot(live[i], live[j]) == 0 for i, j in pairs if i != j and mask(i, j)),
            "off-diagonal control premise")
    require(dot(live[0], live[0]) != 0, "diagonal deletion must leave a nonzero error")

    # A singleton error at an odd pair passes the mask but fails full equality.
    odd_i, odd_j = next((i, j) for i, j in pairs if not mask(i, j))
    require(all((i, j) != (odd_i, odd_j) for i, j in pairs if mask(i, j)),
            "unrestricted singleton must be invisible on the mask")
    require(rank_q(live) == 8 and rank_q(live[:odd_i] + live[odd_i + 1:]) == 8,
            "singleton's column lies outside the root column space")
    # X=2G+E can be realized as D=I, T=X^T; no supplier cost is asserted.

    # Positive nine-term case: D is root-linear, T has cancelling non-root-linear columns.
    D = [list(r) + [r[0]] for r in live]
    T = []
    for j, r in enumerate(live):
        z = int(j == odd_i)
        T.append([Fraction(r[k], 2) - (z if k == 0 else 0) for k in range(8)] + [Fraction(z)])
    require(all(sum(x * y for x, y in zip(D[i], T[j])) == gram2(i, j) for i, j in pairs),
            "one-sided nine-term positive identity failed")
    # The final column of T is e_odd_i, proven outside col(R) by the rank check above.

    # Wrong scaling is detected on the mask, including its diagonals.
    wrong = [row[:] for row in T]
    wrong[0][0] += 1
    require(any(sum(x * y for x, y in zip(D[i], wrong[j])) != gram2(i, j)
                for i, j in pairs if mask(i, j)), "coefficient mutation went undetected")

    # Ordinary transpose is material: i * (-i)=1; i * conjugate(-i)=-1.
    # Integer Gaussian pairs avoid floating-point complex arithmetic entirely.
    mul = lambda z, w: (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])
    require(mul((0, 1), (0, -1)) == (1, 0) and mul((0, 1), (0, 1)) == (-1, 0),
            "ordinary-versus-conjugate transpose control")
    require(gram2(0, 0) != -gram2(0, 0), "conjugate model must fail on diagonal")

    damaged = lines.copy()
    damaged[0] = tuple(x + (i == 0) for i, x in enumerate(damaged[0]))
    reject(lambda: check_geometry(damaged), "corrupt root")
    reject(lambda: check_geometry(lines, 71), "wrong covariance normalization")
    return {"positive_one_sided_terms": 9, "positive_all_pair_entries": len(pairs),
            "controls": ["missing diagonal admits nonzero Gram error",
                         "unrestricted factors admit odd singleton error",
                         "singleton is outside the root column space",
                         "masked coefficient corruption rejected",
                         "conjugate transpose changes the identity",
                         "corrupt root rejected", "wrong covariance constant rejected"],
            "odd_singleton": [odd_i, odd_j]}


def check_sources():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for rel, expected in sources["proof_sources"].items():
        require(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == expected,
                "source pin mismatch: " + rel)
    return {"base_commit": sources["base_commit"], "proof_source_count": len(sources["proof_sources"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate this package's certificate only")
    args = parser.parse_args()
    result = {"status": "PASS_ONE_SIDED_MASK_RIGIDITY_S28", "sources": check_sources(),
              "geometry": check_geometry(roots()), "semantic_evidence": semantic_controls(roots())}
    oracle_path = HERE / "tensor_oracle.py"
    spec = importlib.util.spec_from_file_location("independent_mask_oracle", oracle_path)
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    independent = oracle.run()
    require(independent == json.loads((HERE / "TENSOR-CERTIFICATE.json").read_text()),
            "independent certificate mismatch")
    result["independent_certificate_sha256"] = digest(independent)
    path = HERE / "CERTIFICATE.json"
    if args.write:
        path.write_text(canonical(result))
    else:
        require(result == json.loads(path.read_text()), "certificate mismatch; inspect before regenerating")
    print("PASS_ONE_SIDED_MASK_RIGIDITY_S28 sets=1373 local_spans=143584 controls=7")


if __name__ == "__main__":
    main()
