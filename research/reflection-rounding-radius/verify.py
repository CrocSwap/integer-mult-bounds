#!/usr/bin/env python3
"""Exact finite corroboration of PROOF.md, not a universal proof kernel.

Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor verifier is imported. Default execution writes no files.
"""

from __future__ import annotations

import argparse
from fractions import Fraction as F
import hashlib
import json
from math import ceil, floor
from pathlib import Path
import runpy
import sys


class VerificationError(RuntimeError):
    """A mathematical claim or rejection control did not verify."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def parameters(k, m=None):
    if type(k) is not int:
        raise TypeError("k must be an integer")
    if m is not None and (type(m) is not int or m < 2):
        raise ValueError("m must be an integer at least two")


def grid_radius(k, m):
    parameters(k, m)
    K = abs(k)
    if K == 0:
        numerator = m // 2
    elif K == 1:
        numerator = 2 * m // 3
    elif K % 2 == 0:
        numerator = (K // 2 + 1) * (m // 2)
    else:
        correction = max(K - m, 0) if m % 2 else 0
        numerator = ((K + 1) * m - correction) // 4
    return F(numerator, m)


def real_radius(k):
    parameters(k)
    K = abs(k)
    if K == 0:
        return F(1, 2)
    if K == 1:
        return F(2, 3)
    return F(K + 2 if K % 2 == 0 else K + 1, 4)


def reflection(k, point):
    x, y = point
    return x + k * y, -y


def literal_orbit_error(k, point, output):
    """Compute both actual coordinate errors, without the reduced norm."""
    reflected_point = reflection(k, point)
    reflected_output = reflection(k, output)
    return max(*(abs(a - b) for a, b in zip(point, output)),
               *(abs(a - b) for a, b in zip(reflected_point, reflected_output)))


def nearest_integer(value):
    lo = floor(value)
    return lo if value - lo <= F(1, 2) else lo + 1


def local_output(k, point):
    """Minimize the derived norm among at most four candidates."""
    x, y = point
    candidates = set()
    for b in {floor(y), ceil(y)}:
        horizontal = x + F(k, 2) * (y - b)
        for a in {floor(horizontal), ceil(horizontal)}:
            candidates.add((a, b))

    def key(output):
        u, v = output[0] - x, output[1] - y
        return max(abs(u), abs(v), abs(u + k * v)), output

    return min(candidates, key=key)


def round_equivariant(k, point):
    parameters(k)
    if len(point) != 2 or any(type(x) not in (int, F) for x in point):
        raise TypeError("use exactly two integer or Fraction coordinates")
    x, y = (F(t) for t in point)
    if y == 0:
        return nearest_integer(x), 0
    if y < 0:
        return reflection(k, local_output(k, reflection(k, (x, y))))
    return local_output(k, (x, y))


def grid_witness(k, m):
    parameters(k, m)
    K = abs(k)
    if K == 0:
        p, q = m // 2, 0
    elif K == 1:
        p, q = (m + 1) // 3, m // 3
    elif K % 2 == 0:
        q = m // 2
        p = (m // 2 - (K // 2) * q) % m
    elif m % 2 == 0:
        q = j = m // 2
        p = ((j - K * q) // 2) % m
    else:
        q = (m - 1) // 2
        s = min((K + 1) * m // 4, (K * (m - 1) + 2 * m) // 4)
        j = 2 * s - K * q
        require(0 <= j <= m and (j - q) % 2 == 0, "invalid odd-grid witness")
        p = ((j - K * q) // 2) % m
    if k < 0:
        p = (-p) % m
    return F(p, m), F(q, m)


def real_witness(k):
    K = abs(k)
    if K == 0:
        point = (F(1, 2), F(0))
    elif K == 1:
        point = (F(1, 3), F(1, 3))
    else:
        point = (F(1, 2) - F(K, 4) if K % 2 == 0 else F(1 - K, 4), F(1, 2))
    return (-point[0], point[1]) if k < 0 else point


def check_rounder(k, point, radius, routine=round_equivariant):
    output = routine(k, point)
    require(all(type(z) is int for z in output), "noninteger output")
    require(routine(k, reflection(k, point)) == reflection(k, output),
            f"equivariance failure: k={k}, point={point}")
    error = literal_orbit_error(k, point, output)
    require(error <= radius, f"radius failure: k={k}, point={point}, error={error}")
    if all(F(z).denominator == 1 for z in point):
        require(output == point, "integer point not fixed")
    return error


def rejection_controls():
    """Reject wrong mathematical variants using literal errors and orbits."""
    rejected = []

    def reject(name, operation):
        try:
            operation()
        except VerificationError:
            rejected.append(name)
        else:
            raise VerificationError("control accepted: " + name)

    # Canonical transport alone cannot repair a cost that omits the other point.
    def coordinate_round(k, point):
        if point[1] < 0:
            return reflection(k, coordinate_round(k, reflection(k, point)))
        return tuple(nearest_integer(z) for z in point)

    reject("omit_reflected_error", lambda: check_rounder(
        1, (F(2, 5), F(2, 5)), grid_radius(1, 5), coordinate_round))

    def no_inverse_transport(k, point):
        if point[1] < 0:
            return local_output(k, reflection(k, point))
        return round_equivariant(k, point)

    reject("omit_output_transport", lambda: check_rounder(
        1, (F(0), F(1)), real_radius(1), no_inverse_transport))
    reject("independent_nearest_even_ties", lambda: check_rounder(
        1, (F(1, 2), F(1, 2)), grid_radius(1, 2),
        lambda k, p: tuple(round(z) for z in p)))

    # A local lexicographic minimizer has the right cost but can break ties
    # inconsistently on the two members of an orbit.
    tie_witness = (F(0), F(1, 2))
    reject("omit_canonical_orbit_ties", lambda: check_rounder(
        2, tie_witness, real_radius(2), local_output))
    reject("understate_sharp_radius", lambda: check_rounder(
        1, grid_witness(1, 5), grid_radius(1, 5) - F(1, 5)))
    reject("omit_odd_grid_gap", lambda: require(
        grid_radius(7, 3) == F((7 + 1) * 3 // 4, 3), "incorrect sharp grid radius"))
    reject("ignore_grid_parity", lambda: require(
        grid_radius(5, 5) == real_radius(5), "incorrect sharp grid radius"))

    # Dropping |v| is legal only at K>=2. The resulting two-horizontal-error
    # score at this output is 1/3, but its actual error is 2/3.
    point, output = (F(1, 3), F(1, 3)), (0, 1)
    u, v = output[0] - point[0], output[1] - point[1]
    reject("drop_vertical_error_at_K1", lambda: require(
        max(abs(u), abs(u + v)) == literal_orbit_error(1, point, output),
        "incorrect two-point error"))
    return {"names": rejected, "raw_tie_k": 2,
            "raw_tie_witness": [str(x) for x in tie_witness]}


def verify():
    package = Path(__file__).resolve().parent
    # run_path compiles the oracle source directly; no package import or cached
    # predecessor module supplies this independent enumeration.
    oracle = runpy.run_path(str(package / "lattice_oracle.py"))
    cases = points = candidates = equivariance = 0
    rows = []
    for k in range(-10, 11):
        for m in range(2, 19):
            result = oracle["grid"](k, m)
            expected = grid_radius(k, m)
            require(F(result["radius_numerator"], m) == expected,
                    f"independent grid mismatch: k={k}, m={m}")
            witness = grid_witness(k, m)
            p, q = (int(t * m) for t in witness)
            minimum, _, _ = oracle["minimum"](k, m, p, q)
            require(F(minimum, m) == expected, "analytic witness not a grid maximizer")
            for p in range(m):
                for q in range(m):
                    point = (F(p, m), F(q, m))
                    check_rounder(k, point, expected)
                    equivariance += 1
            # These translations include noncanonical signs and integer y away
            # from the fixed axis. No translation equivariance is assumed.
            for dx, dy in ((-2, -3), (2, 1)):
                shifted = (witness[0] + dx, witness[1] + dy)
                check_rounder(k, shifted, expected)
                equivariance += 1
            cases += 1
            points += result["points"]
            candidates += result["candidates"]
            rows.append([k, m, str(expected), list(result["witness"])])

    larger = real_cases = fixed_integers = 0
    for k in range(-102, 103):
        for m in range(2, 38):
            witness = grid_witness(k, m)
            require(check_rounder(k, witness, grid_radius(k, m)) == grid_radius(k, m),
                    "larger witness not attained")
            larger += 1
        witness = real_witness(k)
        require(check_rounder(k, witness, real_radius(k)) == real_radius(k),
                "real witness not attained")
        real_cases += 1
        for point in ((-2, 0), (0, 0), (3, 1), (-3, -2)):
            require(round_equivariant(k, point) == point, "integer not fixed")
            fixed_integers += 1

    controls = rejection_controls()
    table_bytes = json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode()
    source_names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                    "verify.py", "lattice_oracle.py", "VALIDATION.md")
    return {
        "schema": "reflection-rounding-radius/v1",
        "claim_type": "scoped-written-proof-with-finite-corroboration",
        "no_new_kappa": True,
        "grid_cases": cases, "oracle_residues": points, "oracle_candidates": candidates,
        "small_rounder_equivariance_cases": equivariance,
        "larger_grid_attainment_cases": larger, "real_attainment_cases": real_cases,
        "integer_fixed_cases": fixed_integers, "rejection_controls": controls,
        "grid_table_sha256": hashlib.sha256(table_bytes).hexdigest(),
        "package_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                           for name in source_names},
        "python": sys.version.split()[0],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.receipt:
        package = Path(__file__).resolve().parent
        if not args.receipt.is_absolute() or args.receipt.resolve().is_relative_to(package):
            parser.error("receipt must be an absolute path outside the package")
    result = verify()
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as stream:
            stream.write(serialized)
    print(serialized, end="")
    print("PASS_REFLECTION_ROUNDING_RADIUS no_new_kappa")


if __name__ == "__main__":
    main()
