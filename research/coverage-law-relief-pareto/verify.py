#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify the selected-word (unpaid-coordinate, centre-charge) boundary."""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MODEL_SOURCE = "research/complex-coverage-law-relief/verify.py"
QUESTION_SOURCE = "research/complex-coverage-law-relief/README.md"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def const(x):
    return Q(x), Q(x)


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def sub(x, y):
    return x[0] - y[1], x[1] - y[0]


def scale(x, q):
    q = Q(q)
    a, b = x[0] * q, x[1] * q
    return min(a, b), max(a, b)


def mul(x, y):
    values = (x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1])
    return min(values), max(values)


def div(x, y):
    require(y[0] > 0, "interval divisor must be positive")
    return mul(x, (1 / y[1], 1 / y[0]))


def floor_fraction(x):
    return x.numerator // x.denominator


def ceil_fraction(x):
    return -floor_fraction(-x)


def decimal_bracket(interval, digits):
    unit = 10**digits
    lo, hi = floor_fraction(interval[0] * unit), ceil_fraction(interval[1] * unit)

    def format_scaled(value):
        sign = "-" if value < 0 else ""
        value = abs(value)
        return f"{sign}{value // unit}.{value % unit:0{digits}d}"

    return [format_scaled(lo), format_scaled(hi)]


def decimal_interval(interval, digits):
    return {
        "lo": f"{interval[0].numerator}/{interval[0].denominator}",
        "hi": f"{interval[1].numerator}/{interval[1].denominator}",
        "decimal_bracket": decimal_bracket(interval, digits),
    }


def load_inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    bodies = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = row["path"]
        require(path in (MODEL_SOURCE, QUESTION_SOURCE), "unexpected live input")
        body = (ROOT / path).read_bytes()
        require(hashlib.sha256(body).hexdigest() == row["sha256"], "source hash: " + path)
        bodies[path] = body
    require(set(bodies) == {MODEL_SOURCE, QUESTION_SOURCE}, "complete pinned input set")
    require(b"exact combined `(u, c)`" in bodies[QUESTION_SOURCE]
            and b"Pareto surface at 1/99" in bodies[QUESTION_SOURCE], "pinned open question")
    module = types.ModuleType("pinned_coverage_law_model")
    module.__file__ = str(ROOT / MODEL_SOURCE)
    exec(compile(bodies[MODEL_SOURCE], MODEL_SOURCE, "exec"), module.__dict__)  # noqa: S102
    return module


def expected_model(module):
    require(module.M == 73, "width")
    require(module.STAGES == 9 and module.FAMILIES0 == 896, "fixed template")
    require(module.CENTRE0 == 64 and module.R == 51, "centre/rank cap")
    require(module.WORD == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "local word")
    require(module.WORD_MASS == 5586 and module.A_T1 == Q(1, 99), "mass/target")
    w = Q(module.FAMILIES0, module.STAGES)
    require(73**2 > 2 * 51**2 and 2 * 52**2 >= 73**2, "maximal halving-guard rank")
    return w


def constants(module):
    """Enclose G=sum n_r (r/73)^(98/99) and p=(51/73)^(98/99)/51."""
    G = const(0)
    for rank, count in module.WORD.items():
        G = add(G, scale(module.child_cost(rank, module.A_T1), count))
    p = scale(module.child_cost(module.R, module.A_T1), Q(1, module.R))
    require(G[0] > 0 and p[0] > 0, "positive local and idle coefficients")
    return G, p


def threshold_c(u, w, G, p):
    """Exact interval for c*(u)=5586-(73-u)w+(w-G)/p."""
    return add(
        const(Q(5586) - (Q(73) - Q(u)) * w),
        div(sub(const(w), G), p),
    )


def threshold_u_at_c(c, w, G, p):
    """Solve c*(u)=c, using u=1 as an exact affine anchor."""
    c1 = threshold_c(Q(1), w, G, p)
    return add(const(1), scale(sub(const(c), c1), Q(1, 1) / w))


def relaxation_from_constants(u, c, w, G, p):
    """Interval for rho=[G+p((73-u)w+c-5586)]/w."""
    numerator = add(
        G,
        scale(p, (Q(73) - Q(u)) * w + Q(c) - 5586),
    )
    return scale(numerator, 1 / w)


def strictly_admits_target(module, u, c):
    """Classify rho(1/99) < 1; exact equality is handled by the formula."""
    return module.target_met(module.WORD, module.A_T1, unpaid=Q(u), centre=Q(c))


def run():
    module = load_inputs()
    w = expected_model(module)
    G, p = constants(module)

    # The selected fixed template admits every point of this rectangle: the
    # worst idle mass is at (u,c)=(3,0), where it remains positive.
    for u, c in ((1, 0), (1, 64), (3, 0), (3, 64)):
        point = module.model(module.WORD, unpaid=Q(u), centre=Q(c))
        require(point["idle"] >= 0 and point["deficit"] > 0, "admissible domain corner")
    min_idle = (Q(73 - 3) * w) - module.WORD_MASS
    require(min_idle == Q(12446, 9) and min_idle > 0, "entire-domain idle mass lower bound")

    # c*(u) is affine with slope w. At c=64 its root is u_64; at c=0 it is
    # exactly u_64 - 64/w = u_64 - 9/14.
    u64 = threshold_u_at_c(64, w, G, p)
    u0 = sub(u64, const(Q(9, 14)))
    sample_cstar = {str(u): decimal_interval(threshold_c(Q(u), w, G, p), 12)
                    for u in (1, 2, 3)}
    bracket64 = decimal_bracket(u64, 9)
    bracket0 = decimal_bracket(u0, 9)
    lo64, hi64 = map(lambda s: Q(s), bracket64)
    lo0, hi0 = map(lambda s: Q(s), bracket0)
    require(not strictly_admits_target(module, lo64, 64), "lower u64 bracket endpoint fails")
    require(strictly_admits_target(module, hi64, 64), "upper u64 bracket endpoint passes")
    require(not strictly_admits_target(module, lo0, 0), "lower u0 bracket endpoint fails")
    require(strictly_admits_target(module, hi0, 0), "upper u0 bracket endpoint passes")

    # Exact identity: rho - 1 = (p/w) * (c - c*(u)). Verify interval signs
    # against the predecessor's full relaxation on the entire requested grid.
    grid = []
    for u in range(1, 4):
        for c in range(65):
            direct = strictly_admits_target(module, u, c)
            rho = relaxation_from_constants(u, c, w, G, p)
            predicted = rho[1] < 1
            require(rho[1] < 1 or rho[0] > 1, "grid point separated from equality")
            require(direct == predicted, "formula/source sign disagreement on grid")
            grid.append({"u": u, "c": c, "strictly_below_one": direct})
    feasible = sum(point["strictly_below_one"] for point in grid)
    require(feasible == 65, "integer grid control: only u=3 points pass")

    # Named controls, including the old single-lever obstructions and optimistic
    # point. They do not turn a relaxed pass into a realization.
    require(not strictly_admits_target(module, 1, 64), "selected interface fails target")
    require(not strictly_admits_target(module, 2, 0), "u=2,c=0 fails target")
    require(strictly_admits_target(module, 3, 64), "u=3,c=64 optimistic pass")

    return {
        "status": "PASS_COVERAGE_LAW_PARETO_BOUNDARY",
        "model": {
            "width": 73,
            "stages": 9,
            "families": 896,
            "families_per_call": "896/9",
            "rank_cap": 51,
            "local_word": module.WORD,
            "local_mass": 5586,
            "target_a": "1/99",
            "parameter_domain": {"unpaid_coordinates_u": "[1,3]", "centre_charge_c": "[0,64]"},
            "minimum_idle_mass_over_domain": "12446/9",
        },
        "constants_at_target": {
            "G_definition": "sum_r n_r*(r/73)^(98/99) for the pinned local word",
            "G_local_cost_sum": decimal_interval(G, 15),
            "p_definition": "(51/73)^(98/99)/51",
            "p_idle_cost_per_rank_mass": decimal_interval(p, 18),
        },
        "exact_boundary": {
            "formula": "rho(u,c)-1 = (p/w)*(c-c_star(u))",
            "w": "896/9",
            "c_star": "5586-(73-u)*(896/9)+((896/9)-G)/p",
            "equivalent": "c_star(u)=64+(896/9)*(u-u64)",
            "u64_definition": "unique u with c_star(u)=64",
            "u64_interval": decimal_interval(u64, 9),
            "u64_certified_bracket": list(bracket64),
            "u0_definition": "unique u with c_star(u)=0 = u64-9/14",
            "u0_interval": decimal_interval(u0, 9),
            "c_star_samples_u_1_2_3": sample_cstar,
            "u0_certified_bracket": list(bracket0),
            "classification": [
                "rho<1 exactly when c<c_star(u): the relaxed ceiling exceeds 1/99",
                "rho=1 exactly when c=c_star(u): the relaxed ceiling equals 1/99",
                "rho>1 exactly when c>c_star(u): the relaxed ceiling is below 1/99",
            ],
        },
        "grid_check": {"u_values": [1, 2, 3], "c_range": "0..64 step 1", "points": len(grid),
                       "strict_pass_points": feasible,
                       "strict_pass_grid": [[p["u"], p["c"]] for p in grid if p["strictly_below_one"]]},
        "controls": ["all 4 domain corners have positive idle mass and deficit",
                     "all 195 integer grid signs match the affine boundary",
                     "selected (u=1,c=64) fails; (u=2,c=0) fails; (u=3,c=64) passes"],
        "scope": "fractional optimistic relaxation only; no physical contract, supplier, or kappa result",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write RESULT.json explicitly")
    args = parser.parse_args()
    result = run()
    if args.write:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "result differs from committed RESULT.json; use --write to regenerate")
    print(result["status"], "u64=", result["exact_boundary"]["u64_interval"]["decimal_bracket"],
          "u0=", result["exact_boundary"]["u0_interval"]["decimal_bracket"],
          "grid=65/195 strict passes; no realization claim")


if __name__ == "__main__":
    main()
