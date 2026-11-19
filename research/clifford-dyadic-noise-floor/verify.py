"""Exact four-qubit character data and arithmetic tests for optimal decoding.

apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from fractions import Fraction as Q
from math import lcm
from pathlib import Path


ROOT = Path(__file__).resolve().parent
QUOTIENT_ORDER = 47377612800
PROJECTIVE_ORDER = 256 * QUOTIENT_ORDER
BELL_ENDPOINT = (1, 136, 8619, 271320, 4205460, 31541664,
                 110396096, 165593600, 82796544)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_pinned_inputs():
    inputs = {}
    for pin in json.loads((ROOT / "SOURCE-PINS.json").read_text())["files"]:
        if "local_path" in pin:
            data = (ROOT / pin["local_path"]).read_bytes()
            require(len(data) == pin["bytes"], "source length")
            require(hashlib.sha256(data).hexdigest() == pin["sha256"], "source hash")
            require(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                    == pin["git_blob"], "original Git blob")
            inputs[pin["pr"]] = json.loads(data)
    require(set(inputs) == {7747, 7772}, "which machine-readable sources are used")
    return inputs


def projection_rows(projection):
    complete = []
    for index, (degree, *middle) in enumerate(projection["rows"]):
        require(len(middle) == 7, "expected fixed-space dimensions 1 through 7")
        fixed_zero = (QUOTIENT_ORDER if index == 0 else 0) - sum(middle) - degree
        complete.append((degree, [fixed_zero, *middle, degree]))
    require(len(complete) == 81, "quotient character count")
    require(complete[0][1] == projection["element_counts"], "trivial character row")
    require(sum(d*d for d, _ in complete) == QUOTIENT_ORDER, "quotient order")
    return complete


def odd_levels(rows, width):
    p = (width - 1) // 2
    sign = (-1)**((width + 1) // 4)
    levels = []
    for degree, character in rows:
        scalar_product = sum(entry * (sign * 2**p)**d for d, entry in enumerate(character))
        multiplicity, remainder = divmod(scalar_product, QUOTIENT_ORDER)
        require(remainder == 0 and multiplicity >= 0, "odd-sector integral multiplicity")
        levels.append(Q(PROJECTIVE_ORDER * multiplicity, 16**width * 16 * degree))
    return levels


def neutral_levels(rows, width, include_trace_phase=True):
    # Sum the real character directly over the projective Pauli lifts.
    # At fixed-space dimension d, 2^(8-d) of the 256 lifts have nonzero trace.
    powers = [2**(8-d) * 2**(d*width//2)
              * ((-1)**(d*(width//4)) if include_trace_phase else 1)
              for d in range(9)]
    return [Q(sum(c*p for c, p in zip(character, powers, strict=True)), 16**width * degree)
            for degree, character in rows]


def bell_minimum(width):
    x = -Q(1, 2**((width-2)//2))
    return sum(c*x**i for i, c in enumerate(BELL_ENDPOINT))


def check_four_qubit():
    data = read_pinned_inputs()
    rows = projection_rows(data[7747])
    receipt = data[7772]
    levels = odd_levels(rows, 13)
    require(levels == [Q(*r["eigenvalue"]) for r in receipt["rows"]], "all width-13 levels")
    require(sum(r["regular_dimension"] for r in receipt["rows"]) == PROJECTIVE_ORDER,
            "four-qubit spectral dimension")
    require(min(levels) == levels[0] == Q(470624175, 2**32), "width-13 minimum")
    require(len(set(levels)) == 52 and sum(x == min(levels) for x in levels) == 1,
            "width-13 distinct levels and minimum row")
    require(bell_minimum(14) == Q(5741614935, 2**35), "width-14 minimum")
    require(min(odd_levels(rows, 15)) == Q(75707742285, 2**38), "width-15 minimum")
    width17 = min(odd_levels(rows, 17))
    require(width17 == Q(37674563331825, 2**46) and width17 > Q(1, 2),
            "monotone lower bound beyond width 16")
    for width in range(16, 97, 4):
        inflated = neutral_levels(rows, width)
        preceding = odd_levels(rows, width-1)
        require(inflated == preceding, "neutral sector duplication")
        if width % 8 == 4:
            require(neutral_levels(rows, width, False) != preceding, "trace phase control")
        require(min(inflated).numerator > 1 and max(inflated) > 1 > min(inflated),
                "strict endpoints and odd numerator")
    return 21*len(rows)


def odd_denominator(rows):
    common = lcm(*(Q(a).denominator for row in rows for a in row))
    while common % 2 == 0:
        common //= 2
    return common


def check_exact_odd_budget():
    # A has two disjoint columns (1,2) and (2,3); L begins with rows
    # (1,0) and (-1,1). Section 1 predicts odd denominator exactly five,
    # whereas J has denominator 65.
    blocks = [(1, 2), (2, 3)]
    canonical = [[Q(x, a*a+b*b) for x in (a, b)] for a, b in blocks]
    rows = [[Q(1), Q(0)], [Q(-1), Q(1)]]
    require(odd_denominator(canonical) == 65, "canonical denominator")
    for step, h in enumerate([Q(1, 5)] + [Q(1, 8)] * 12):
        rows = [[(1-h*(a*a+b*b))*x + h*y for x, y in zip(row, (a,b), strict=True)]
                for row, (a,b) in zip(rows, blocks, strict=True)]
        require(all(a*x+b*y == 1 for (x,y),(a,b) in zip(rows, blocks, strict=True)),
                "split lost during exact repair")
        require(rows[0] == canonical[0] and odd_denominator(rows) == 5, "minimum mode repair")
        if max(sum(q*q for q in row) for row in rows) == Q(1, 5):
            break
    else:
        raise ValueError("no exact optimum at the advertised odd denominator")
    require(rows != canonical and step > 0, "measured noncanonical minimizer")
    # An odd obstruction away from the bottom eigenspace need not affect the optimum.
    require(Q(1, 5) < 1 and odd_denominator([[1, 0], [Q(1, 5), Q(2, 5)]]) == 5,
            "nonminimum denominator control")
    # A = e1, e2 + 2e3. Picking coordinates 1 and 2 decodes exactly with norm one.
    column_matrix = [[1, 0], [0, 1], [0, 2]]
    integer_decoder = [[1, 0, 0], [0, 1, 0]]
    identity = [[sum(x*y for x, y in zip(r, c, strict=True))
                 for c in zip(*column_matrix)] for r in integer_decoder]
    require(identity == [[1, 0], [0, 1]], "nonminimum counterexample")
    return step


def check_precision_lattice():
    # For the column (1,2) an exact row on the grid is ((2^s-2z), z)/2^s,
    # with z Gaussian integral. Im(z) contributes 5 Im(z)^2 to the numerator.
    # Enumerate complete sublevel balls: the feasible row (1,0) bounds the optimum by 1.
    for s in range(8):
        den = 2**s
        best = den*den
        for y in range(-den, den+1):
            for x in range(-den, den+1):
                value = (den-2*x)**2 + x*x + 5*y*y
                best = min(best, value)
        excess = Q(best, den*den) - Q(1, 5)
        nearest_residue = min((2*den) % 5, (-2*den) % 5)
        require(excess == Q(nearest_residue**2, 5*den**2), "exact grid optimum")
        require(excess*den**2 in (Q(1, 5), Q(4, 5)), "nonzero quadratic rate")
    return 8


def check_round_and_repair():
    # A=[I; 1/2,2], with L selecting the first two coordinates. The only
    # nonzero row of I-AL is (-1/2,-2,1), so t=1 in the precision bound.
    a = [(1, 0), (0, 1), (Q(1, 2), 2)]
    l = [(1, 0, 0), (0, 1, 0)]
    last = [-Q(1, 2), -2, 1]
    j = [[Q(v, 21) for v in row] for row in ((20,-4,2), (-4,5,8))]
    for s in range(1, 17):
        grid = 2**(s-1)
        h = [[Q(round(v*grid), grid) for v in row] for row in j]
        d = [[u + row[2]*v for u, v in zip(identity_row, last, strict=True)]
             for row, identity_row in zip(h, l, strict=True)]
        require(all((v * 2**s).denominator == 1 for row in d for v in row), "grid accounting")
        require([[sum(r[i]*a[i][c] for i in range(3)) for c in range(2)] for r in d]
                == [[1, 0], [0, 1]], "round-and-repair lost BA=I")
        # This error has rank at most one. The squared Frobenius norm is exact.
        difference = sum((x-y)**2 for r, t in zip(d, j, strict=True)
                         for x, y in zip(r, t, strict=True))
        require(0 < difference <= Q(21, 8*grid**2), "round-and-repair error bound")
    return 16


if __name__ == "__main__":
    comparisons = check_four_qubit()
    corrections = check_exact_odd_budget()
    grids = check_precision_lattice()
    repairs = check_round_and_repair()
    print(f"PASS_NOISE_FLOOR width13_rows=81 neutral_row_equalities={comparisons} "
          f"width13_odd_budget=470624175 toy_dyadic_corrections={corrections} "
          f"exhaustive_complex_grids={grids} rounding_grids={repairs}")
