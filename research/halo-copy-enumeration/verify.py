#!/usr/bin/env python3
"""Exact finite enumeration audit; no matrix payloads or theorem acceptance.

Prepared with substantial OpenAI Astra assistance. Apache-2.0.
All rejecting checks are explicit and remain active under python -O.
"""

import json
from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


@dataclass(frozen=True)
class Grid:
    cores: tuple
    side: int
    margin: int
    bandwidth: int

    def validate(self):
        require(2 <= len(self.cores) <= 3, "fixture dimension must be 2 or 3")
        require(
            all(type(n) is int and n >= 2 for n in self.cores),
            "at least two cores per periodic axis required",
        )
        require(
            type(self.side) is int
            and type(self.margin) is int
            and self.margin > 0
            and self.side > 4 * self.margin,
            "require integer L > 4A > 0",
        )
        require(
            type(self.bandwidth) is int and 0 <= self.bandwidth < self.margin,
            "require 0 <= b < A",
        )

    def sources(self):
        return product(*(range(n * self.side) for n in self.cores))


def same_multiset(actual, expected):
    require(actual == expected, "full emitted key multiset mismatch")
    require(all(n == 1 for n in actual.values()), "duplicate input-copy key")


def expect_rejection(label, operation):
    try:
        operation()
    except Rejected:
        return label
    raise Rejected("failure control did not reject: " + label)


def source_enumeration(grid, *, _mutation=None):
    """One coordinate scan, prefix AND, then pruned DFS face forests.

    The explicit stack (depth,next-choice) is the depth-first odometer.
    Roots exist only for permitted faces; all their suffix factors are nonempty.
    Keys include destination core, face axis/side, lifted local coordinate,
    and canonical global source. No payload arrays are allocated.
    _mutation changes one algorithm seam only for negative controls; the
    destination oracle is unchanged and compares the complete returned keys.
    """
    grid.validate()
    g, L, A, b = len(grid.cores), grid.side, grid.margin, grid.bandwidth
    keys = Counter()
    stats = Counter()
    per_source = Counter()
    for x in grid.sources():
        stats["sources"] += 1
        later, interior, faces = [], [], []
        for i, (xi, n) in enumerate(zip(x, grid.cores)):
            stats["coordinate_scans"] += 1
            q, r = divmod(xi, L)
            choices = [q]
            if r < b and _mutation != "omit-neighbor-core":
                choices.append((q - 1) % n)
            if r >= L - b:
                choices.append((q + 1) % n)
            require(len(set(choices)) == len(choices) <= 2, "bad later choices")
            later.append(tuple(choices))
            interior_margin = A if _mutation == "strict-earlier-interior" else A - b
            interior.append(q if interior_margin <= r < L - interior_margin else None)
            axis_faces = [[], []]
            S = n * L
            for c in choices:
                stats["candidate_tests"] += 1
                t = (xi - c * L) % S
                if t < A + b or (b > 0 and t >= S - b):
                    axis_faces[0].append(c)
                lower = L - A - b + (_mutation == "open-upper-face-lower-endpoint")
                if lower <= t < L + b:
                    axis_faces[1].append(c)
            faces.append(axis_faces)
        prefix = [True]
        for c in interior:
            stats["prefix_steps"] += 1
            prefix.append(prefix[-1] and c is not None)
        for f in range(g):
            for side in range(2):
                stats["face_tests"] += 1
                if not prefix[f] or not faces[f][side]:
                    continue
                factors = [tuple(faces[f][side])] + later[f + 1 :]
                selected = [0] * len(factors)
                # Each stack entry denotes an actual non-leaf node.
                stack = [[0, 0]]
                stats["forests"] += 1
                stats["internal_nodes"] += 1
                forest_nodes, forest_leaves = 1, 0
                while stack:
                    depth, choice = stack[-1]
                    if choice == len(factors[depth]):
                        stack.pop()
                        continue
                    stack[-1][1] += 1
                    selected[depth] = factors[depth][choice]
                    if depth + 1 < len(factors):
                        stack.append([depth + 1, 0])
                        stats["internal_nodes"] += 1
                        forest_nodes += 1
                        continue
                    core = tuple(interior[:f]) + tuple(selected)
                    local = []
                    for xi, c, n in zip(x, core, grid.cores):
                        t = (xi - c * L) % (n * L)
                        local.append(t - n * L if b > 0 and t >= n * L - b else t)
                    key = (core, f, side, tuple(local), x)
                    keys[key] += 1
                    per_source[x] += 1
                    stats["copies"] += 1
                    forest_leaves += 1
                require(forest_leaves > 0, "empty admitted forest")
                require(
                    forest_nodes <= (g - f) * forest_leaves,
                    "internal-node versus leaf bound",
                )
    stats["empty_sources"] = stats["sources"] - len(per_source)
    stats["max_copies_per_source"] = max(per_source.values(), default=0)
    return keys, stats, per_source


def destination_oracle(grid):
    """Independent destination-first rectangle membership on integer lifts.

    Does not call source candidate, prefix, offset or odometer code. For each
    destination it directly intersects shifted absolute half-open intervals
    with each canonical periodic source. Unique lifts follow from widths < S.
    """
    g, L, A, b = len(grid.cores), grid.side, grid.margin, grid.bandwidth
    keys = Counter()
    membership_tests = 0
    for core in product(*(range(n) for n in grid.cores)):
        for face in range(g):
            for side in range(2):
                intervals = []
                for i, c in enumerate(core):
                    if i < face:
                        lo, hi = A, L - A
                    elif i == face:
                        lo, hi = (0, A) if side == 0 else (L - A, L)
                    else:
                        lo, hi = 0, L
                    intervals.append((c * L + lo - b, c * L + hi + b))
                for x in grid.sources():
                    membership_tests += 1
                    local = []
                    for i, (lo, hi) in enumerate(intervals):
                        period = grid.cores[i] * L
                        lifts = [
                            x[i] + shift * period
                            for shift in (-1, 0, 1)
                            if lo <= x[i] + shift * period < hi
                        ]
                        require(len(lifts) <= 1, "ambiguous periodic lift")
                        if not lifts:
                            break
                        local.append(lifts[0] - core[i] * L)
                    if len(local) == g:
                        keys[(core, face, side, tuple(local), x)] += 1
    return keys, membership_tests


def output_partition(grid):
    """Enumerate unexpanded outputs and independently classify each hole."""
    g, L, A = len(grid.cores), grid.side, grid.margin
    returned = Counter()
    for core in product(*(range(n) for n in grid.cores)):
        for f in range(g):
            for side in range(2):
                ranges = []
                for i in range(g):
                    if i < f:
                        ranges.append(range(A, L - A))
                    elif i == f:
                        ranges.append(range(A) if side == 0 else range(L - A, L))
                    else:
                        ranges.append(range(L))
                for local in product(*ranges):
                    returned[tuple(c * L + r for c, r in zip(core, local))] += 1
    expected = Counter()
    for x in grid.sources():
        if any(not (A <= xi % L < L - A) for xi in x):
            expected[x] = 1
    require(returned == expected, "returned hole multiset mismatch")
    require(all(n == 1 for n in returned.values()), "duplicate returned output")
    require(
        len(returned) == prod(grid.cores) * (L**g - (L - 2 * A) ** g),
        "exact discarded volume",
    )
    return returned


def bind_live_sources():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = json.loads((package / "SOURCES.json").read_text())
    manifest = json.loads((package / "VERIFY.json").read_text())
    count = 0
    for row in sources["files"]:
        if row["usage"] == "input":
            require(row["path"] in manifest["inputs"], "undeclared live input")
            require(
                sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "live source hash mismatch: " + row["path"],
            )
            count += 1
    require(count == 6, "unexpected live source count")
    return count


def main():
    live = bind_live_sources()
    controls = []
    fixtures = (
        ("two_dimensional_wrap", Grid((2, 3), 12, 2, 1)),
        ("three_dimensional_corner", Grid((2, 2, 2), 10, 2, 1)),
        ("zero_bandwidth", Grid((2, 2), 10, 2, 0)),
    )
    for name, grid in fixtures:
        actual, stats, per_source = source_enumeration(grid)
        expected, tests = destination_oracle(grid)
        same_multiset(actual, expected)
        if grid.bandwidth:
            for mutation in (
                "omit-neighbor-core",
                "strict-earlier-interior",
                "open-upper-face-lower-endpoint",
            ):
                # Run the real source algorithm with one test-only seam changed.
                # An internal exception is a failure, not an oracle rejection.
                mutated, _, _ = source_enumeration(grid, _mutation=mutation)
                controls.append(
                    expect_rejection(
                        name + ":algorithm:" + mutation,
                        lambda mutated=mutated, expected=expected: same_multiset(
                            mutated, expected
                        ),
                    )
                )
        returned = output_partition(grid)
        g, L, A, b = len(grid.cores), grid.side, grid.margin, grid.bandwidth
        volume = prod(grid.cores) * sum(
            2 * (L - 2 * A + 2 * b) ** f * (A + 2 * b) * (L + 2 * b) ** (g - f - 1)
            for f in range(g)
        )
        require(stats["copies"] == volume, "exact copied-volume identity")
        # Diagnostic loop-accounting consistency, not physical-cost evidence.
        require(stats["coordinate_scans"] == g * stats["sources"], "dense scan count")
        require(stats["prefix_steps"] == g * stats["sources"], "prefix setup count")
        require(stats["face_tests"] == 2 * g * stats["sources"], "face setup count")
        require(
            stats["candidate_tests"] <= 2 * g * stats["sources"], "candidate scan bound"
        )
        require(stats["internal_nodes"] <= g * stats["copies"], "forest total bound")
        center = (L // 2,) * g
        require(
            per_source[center] == 0 and stats["empty_sources"] > 0,
            "missing empty-output source",
        )
        corner = (0,) * g
        require(per_source[corner] == (2**g if b else 1), "rare corner copy count")
        if b:
            require(
                any(any(t < 0 for t in key[3]) for key in actual),
                "missing wrap fixture",
            )
            require(stats["max_copies_per_source"] >= 2**g, "missing many-copy fixture")
            omitted = Counter(
                {k: v for k, v in actual.items() if not (k[1] == 0 and k[2] == 0)}
            )
            controls.append(
                expect_rejection(
                    name + ":omitted-face",
                    lambda omitted=omitted, expected=expected: same_multiset(
                        omitted, expected
                    ),
                )
            )
            duplicate = actual.copy()
            duplicate[next(iter(duplicate))] += 1
            controls.append(
                expect_rejection(
                    name + ":duplicate",
                    lambda duplicate=duplicate, expected=expected: same_multiset(
                        duplicate, expected
                    ),
                )
            )
            no_wrap = Counter(
                {k: v for k, v in actual.items() if all(t >= 0 for t in k[3])}
            )
            controls.append(
                expect_rejection(
                    name + ":lost-wrap",
                    lambda no_wrap=no_wrap, expected=expected: same_multiset(
                        no_wrap, expected
                    ),
                )
            )
            boundary = actual.copy()
            boundary_key = next(k for k in boundary if k[3][k[1]] == -b and k[2] == 0)
            del boundary[boundary_key]
            controls.append(
                expect_rejection(
                    name + ":open-lower-endpoint",
                    lambda boundary=boundary, expected=expected: same_multiset(
                        boundary, expected
                    ),
                )
            )
        duplicate_return = returned.copy()
        duplicate_return[next(iter(duplicate_return))] += 1
        controls.append(
            expect_rejection(
                name + ":duplicate-return",
                lambda duplicate_return=duplicate_return: require(
                    all(n == 1 for n in duplicate_return.values()),
                    "duplicate returned output",
                ),
            )
        )
        print(
            json.dumps(
                {
                    "fixture": name,
                    **stats,
                    "oracle_membership_tests": tests,
                    "returned_outputs": len(returned),
                },
                sort_keys=True,
            )
        )
    for b in (-1, 2, 3):
        controls.append(
            expect_rejection(
                "invalid-bandwidth:" + str(b),
                lambda b=b: Grid((2, 2), 10, 2, b).validate(),
            )
        )
    print(
        "PASS_HALO_COPY_ENUMERATION "
        + json.dumps(
            {
                "fixtures": len(fixtures),
                "controls": controls,
                "live_sources": live,
                "scope": "finite_exact_keys_and_counts; written_combinatorial_proof_separate; physical_tape_cost_open",
                "no_new_kappa": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
