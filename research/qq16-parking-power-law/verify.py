#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact certificate for the stated parked-volume recurrence.

Produced by Nick Petalas. The histogram and source-tree premises are Brian's
PR4753, with the physical/QQ16 predecessor attribution retained in README.md.
"""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DENOMINATOR = 14336
DIMENSION = 73
THRESHOLD = 356
SHIFT = Q(3456, 25)
EXPONENT_LO = Q(9983245373, 10**10)
EXPONENT_HI = Q(9983245374, 10**10)
DP_LIMIT = 8192
TREE_LIMIT = 2**20


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "bounded file input: " + str(path))
    return raw


def load_premises():
    manifest = json.loads(read_bounded(HERE / "SOURCES.json", 2**16))
    need(len(manifest["files"]) <= 16, "source row bound")
    authenticated = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = read_bounded(ROOT / row["path"], 2**20)
            need(sha256(raw).hexdigest() == row["sha256"], "premise digest")
            authenticated[row["path"]] = raw
    published = json.loads(authenticated["research/qq16-nonterminal-c8-tree/RESULT.json"])
    counts = {int(r): n for r, n in published["rank_histogram"].items()}
    need(len(counts) == 8, "eight inherited rank classes")
    need(all(1 <= r <= 48 and type(n) is int and n > 0
             for r, n in counts.items()), "positive inherited multiplicities")
    need(published["first_nonterminal_width"] == THRESHOLD, "inherited cutoff")
    return tuple(sorted(counts.items()))


def log_interval(value):
    """Enclose log(value), value >= 1, by 48 atanh terms and their tail."""
    need(1 <= value <= 2**24, "log argument bound")
    reduced, shifts = Q(value), 0
    for _ in range(25):
        if reduced < 2:
            break
        reduced /= 2
        shifts += 1
    need(1 <= reduced < 2, "bounded log range reduction")
    intervals = []
    for argument in (reduced, Q(2)):
        z = (argument - 1) / (argument + 1)
        partial = sum((2 * z**(2*j+1) / (2*j+1) for j in range(48)), Q(0))
        tail = 2 * z**97 / (97 * (1 - z*z))
        intervals.append((partial, partial + tail))
    lower = intervals[0][0] + shifts * intervals[1][0]
    upper = intervals[0][1] + shifts * intervals[1][1]
    scale = 10**40
    # Round outward to keep subsequent rational powers small.
    return Q(lower * scale // 1, scale), Q(-(-upper * scale // 1), scale)


def exp_interval(value):
    """Positive Taylor series through degree 12, with geometric tail."""
    need(0 <= value < 1, "exp argument bound")
    term, partial = Q(1), Q(1)
    for j in range(1, 13):
        term *= value / j
        partial += term
    first_omitted = term * value / 13
    return partial, partial + first_omitted / (1 - value / 14)


def power_interval(base, exponent):
    """Enclose base**exponent near exponent one using rational arithmetic."""
    need(Q(1, 73) <= base <= 2**24, "power argument bound")
    need(Q(99, 100) <= exponent <= 1, "power exponent bound")
    inverse = base < 1
    argument = 1 / base if inverse else base
    log_lo, log_hi = log_interval(argument)
    lower = exp_interval((1 - exponent) * log_lo)[0]
    upper = exp_interval((1 - exponent) * log_hi)[1]
    return (base * lower, base * upper) if inverse else (base / upper, base / lower)


def moment_interval(counts, exponent):
    intervals = [(Q(n, DENOMINATOR), power_interval(Q(r, DIMENSION), exponent))
                 for r, n in counts]
    return tuple(sum((c * bounds[i] for c, bounds in intervals), Q(0))
                 for i in range(2))


def exponent_certificate(counts, lower, upper):
    need(0 < lower < upper < 1, "ordered interior exponent bracket")
    left, right = moment_interval(counts, lower), moment_interval(counts, upper)
    need(left[0] > 1 and right[1] < 1, "opposite strict moment signs")
    return left, right


def bottom_up(counts):
    """Two independent recurrences: internal node mass and leaf mass."""
    tolls = [Q(0)] * (DP_LIMIT + 1)
    leaves = [Q(1)] * (DP_LIMIT + 1)
    for width in range(THRESHOLD, DP_LIMIT + 1):
        q = width // DIMENSION
        need(max(r*q for r, _ in counts) < width, "strict child descent")
        tolls[width] = 1 + sum((Q(n, DENOMINATOR) * tolls[r*q]
                               for r, n in counts), Q(0))
        leaves[width] = sum((Q(n, DENOMINATOR) * leaves[r*q]
                             for r, n in counts), Q(0))
    return tolls, leaves


def level_census(counts, width):
    """Count paths by depth with integer n_r, leaving Gamma symbolic."""
    need(type(width) is int and 0 <= width <= TREE_LIMIT, "tree width bound")
    frontier, rows = Counter({width: 1}), []
    for depth in range(64):
        if not frontier:
            return rows
        need(len(frontier) <= 4096, "frontier capacity")
        active = {w: n for w, n in frontier.items() if w >= THRESHOLD}
        rows.append((depth, sum(active.values()),
                     sum(n for w, n in frontier.items() if w < THRESHOLD)))
        children = Counter()
        for w, paths in active.items():
            for rank, multiplicity in counts:
                child = rank * (w // DIMENSION)
                need(child < w, "census child descent")
                if child not in children:
                    need(len(children) < 4096, "successor frontier capacity")
                children[child] += paths * multiplicity
        frontier = children
    raise ValueError("64-level capacity exhausted")


def census_masses(rows):
    internal = sum((Q(active, DENOMINATOR**depth)
                    for depth, active, _ in rows), Q(0))
    leaf = sum((Q(terminal, DENOMINATOR**depth)
                for depth, _, terminal in rows), Q(0))
    return internal, leaf


def check_envelope(width, mass, a):
    lower_base = (Q(width) + SHIFT) / (THRESHOLD - 1 + SHIFT)
    upper_base = Q(width, THRESHOLD // DIMENSION)
    # Use the harder endpoints: these imply the claimed bounds for the root s.
    lower_power = power_interval(lower_base, EXPONENT_HI)[1]
    upper_power = power_interval(upper_base, EXPONENT_LO)[0]
    need(a * (lower_power - 1) <= mass <= a * (upper_power - 1),
         "two-sided finite envelope")


def rejection_controls(counts, tolls):
    rejected = []
    for name, lo, hi in (
        ("root bracket above the root", Q(999, 1000), Q(9991, 10000)),
        ("root bracket below the root", Q(997, 1000), Q(998, 1000)),
        ("reversed bracket", EXPONENT_HI, EXPONENT_LO),
    ):
        try:
            exponent_certificate(counts, lo, hi)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("mutant bracket accepted")
    # Each alternative makes a mathematically different, incorrect prediction.
    alternatives = {
        "cutoff repeated after remainder": tolls[DIMENSION * (356 // DIMENSION)],
        "threshold equality called terminal": Q(0),
        "fresh-row divisor omitted after cover cancellation": Q(1 + dict(counts)[48]),
        "round width upward": tolls[584],
    }
    expected = {name: tolls[356] for name in alternatives}
    expected["fresh-row divisor omitted after cover cancellation"] = tolls[584]
    expected["round width upward"] = tolls[583]
    for name, result in alternatives.items():
        need(result != expected[name], "incorrect recurrence not distinguished")
        rejected.append(name)
    too_small = SHIFT - Q(1, 25)
    need(48 * 72 > too_small * 25, "smaller uniform shift is invalid")
    rejected.append("shift below sharp residue allowance")
    return rejected


def main():
    counts = load_premises()
    total = sum(n for _, n in counts)
    c = Q(total, DENOMINATOR)
    a = 1 / (c - 1)
    need(c > 1 and sum(Q(n*r, DENOMINATOR*DIMENSION) for r, n in counts) < 1,
         "unique critical root between zero and one")
    signs = exponent_certificate(counts, EXPONENT_LO, EXPONENT_HI)
    shifts = [Q(r*delta, DIMENSION-r) for r, _ in counts for delta in range(73)]
    need(max(shifts) == SHIFT, "sharp affine floor allowance")
    tolls, leaves = bottom_up(counts)
    for width in range(DP_LIMIT + 1):
        need(leaves[width] == 1 + (c-1) * tolls[width], "weighted leaf identity")
    need(tolls[355] == 0 and tolls[356] == tolls[583] == 1, "strict cutoff")
    need(tolls[584] == Q(9601, 7168), "first extra generation value")
    samples = (356, 360, 583, 584, 948, 949, 3284, 3285, 8192, 65536, TREE_LIMIT)
    rows = []
    for width in samples:
        census = level_census(counts, width)
        mass, leaf = census_masses(census)
        need(leaf == 1 + (c-1)*mass, "independent census leaf identity")
        if width <= DP_LIMIT:
            need(mass == tolls[width], "integer path census matches rational DP")
        check_envelope(width, mass, a)
        rows.append({"width": width, "mass": str(mass), "depth_rows": census})
    controls = rejection_controls(counts, tolls)
    receipt = {
        "status": "PASS_QQ16_PARKING_POWER_LAW",
        "claim_type": "scoped proof with exact finite corroboration",
        "exponent_open_interval": [str(EXPONENT_LO), str(EXPONENT_HI)],
        "moment_sign_intervals": [[str(x) for x in pair] for pair in signs],
        "C": str(c), "a": str(a), "shift": str(SHIFT),
        "DP_widths": DP_LIMIT + 1, "path_censuses": rows, "controls": controls,
        "source_sha256": {name: sha256(read_bounded(HERE / name, 2**20)).hexdigest()
                          for name in ("README.md", "SOURCES.json", "TASK.json",
                                       "VERIFY.json", "verify.py")},
        "full_cost_sign": "unresolved", "new_kappa": False,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
