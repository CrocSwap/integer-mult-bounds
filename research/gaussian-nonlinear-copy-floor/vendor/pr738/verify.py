#!/usr/bin/env python3
"""Replay the Gaussian clique copy bound. Python 3.10+, standard library."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from geometry import (J, bits, canonical_basis, clique_hits, doubled_roots,
                      gaussian_flats, gaussian_lines, maximal_cliques,
                      nonorthogonality, pairing_rank, remainder, self_check)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_sources():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, expected in sources["sha256"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        require(actual == expected, f"source hash mismatch: {path}")
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text())
    require(selected["kappa"] == sources["selected_kappa"], "selected kappa changed")


def check_cliques(cliques, graph):
    require(len(cliques) == len(set(cliques)), "duplicate clique")
    for clique in cliques:
        require(clique > 0 and clique >> len(graph) == 0, "invalid clique vertices")
        for vertex in bits(clique):
            require((clique ^ (1 << vertex)) & ~graph[vertex] == 0,
                    "clique contains orthogonal lines")


def check_charge(hits, rank, coefficient=192):
    require(hits <= coefficient * rank, "clique charge exceeds pairing rank")


def check_fitting(rows, graph):
    require(len(rows) == len(graph), "wrong decoder dimension")
    for i, row in enumerate(rows):
        require(row >> len(rows) == 0 and row >= 0, "invalid decoder bits")
        require((row >> i) & 1, "decoder diagonal is zero")
        require(row & graph[i] == 0, "decoder violates nonorthogonal zero")


def rejected(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError(f"negative control was accepted: {function.__name__}")


def calculate():
    self_check()
    lines = gaussian_lines()
    graph = nonorthogonality(lines)
    require(all(mask.bit_count() == 44 for mask in graph), "wrong Gaussian graph")
    all_cliques = maximal_cliques(graph)
    check_cliques(all_cliques, graph)
    maximum = max(c.bit_count() for c in all_cliques)
    cliques = tuple(c for c in all_cliques if c.bit_count() == maximum)
    require(maximum == 12 and len(cliques) == 640, "wrong maximum-clique census")
    flats = gaussian_flats(lines)
    rows = []
    flat_census = {}
    for rank, level in flats.items():
        census = Counter()
        for mask, basis in level:
            require(len(basis) == 2 * rank, "wrong flat rank")
            generated = canonical_basis(v for i in bits(mask)
                                        for v in (lines[i], J(lines[i])))
            require(generated == basis, "flat basis does not match its lines")
            require(all(not any(remainder(J(v), basis)) for v in basis),
                    "flat is not Gaussian")
            closure = sum(1 << i for i, line in enumerate(lines)
                          if not any(remainder(line, basis)))
            require(closure == mask, "flat is not closed")
            hits = clique_hits(mask, cliques)
            census[(mask.bit_count(), hits.bit_count())] += 1
            if rank:
                rows.append((rank, mask, basis, hits))
        flat_census[str(rank)] = [
            {"lines": size, "cliques_hit": hits, "count": count}
            for (size, hits), count in sorted(census.items())]

    exact = pruned = zero = pairs = 0
    for i, (rank_f, _, basis_f, hits_f) in enumerate(rows):
        for rank_g, _, basis_g, hits_g in rows[i:]:
            pairs += 1
            hits = (hits_f & hits_g).bit_count()
            if not hits:
                zero += 1
                continue
            # A joint-hit clique gives a nonzero pairing; Sylvester gives r+s-4.
            lower_rank = max(1, rank_f + rank_g - 4)
            if hits <= 192 * lower_rank:
                pruned += 1
                continue
            rank = pairing_rank(basis_f, basis_g)
            exact += 1
            check_charge(hits, rank)

    witness_f = [0, 1, 2, 11, 12, 45]
    witness_g = [0, 3, 4, 5, 6, 7, 8, 9, 10, 54, 55, 56, 57, 58, 59]
    masks = [sum(1 << i for i in indices) for indices in (witness_f, witness_g)]
    by_mask = {mask: (rank, basis, hits) for rank, mask, basis, hits in rows}
    rf, bf, hf = by_mask[masks[0]]
    rg, bg, hg = by_mask[masks[1]]
    beta, hits = pairing_rank(bf, bg), (hf & hg).bit_count()
    require((rf, rg, beta, hits) == (2, 3, 1, 192), "sharp witness changed")
    require(pairing_rank(bg, bf) == beta, "pairing symmetry failed")
    require(pairs == len(rows) * (len(rows) + 1) // 2, "incomplete pair coverage")
    require(pairs == exact + pruned + zero, "pair accounting mismatch")
    weighted_clique_size = len(cliques) * maximum
    require(weighted_clique_size % 192 == 0, "nonintegral bound")
    gaussian_floor = weighted_clique_size // 192
    rational_floor = 2 * gaussian_floor
    deficit_slope = 2 * len(lines) - rational_floor
    require(3 * deficit_slope - 2 * len(lines) == 0, "three-stage budget changed")

    # Positive controls: row totals realize I and an asymmetric free-entry edit.
    identity = [1 << i for i in range(60)]
    check_fitting(identity, graph)
    free = next(j for j in range(1, 60) if not (graph[0] >> j) & 1)
    asymmetric = identity.copy()
    asymmetric[0] |= 1 << free
    check_fitting(asymmetric, graph)
    row_cost = sum(pairing_rank(canonical_basis((lines[i], J(lines[i]))),
                               canonical_basis(v for j in bits(row)
                                               for v in (lines[j], J(lines[j]))))
                   for i, row in enumerate(asymmetric))
    require(row_cost == 60, "row-decomposition upper bound failed")

    # Each control changes a proof-relevant condition.
    rejected(check_charge, hits, beta, 191)
    rejected(check_charge, hits, beta, 96)  # confusing rational and Gaussian units
    rejected(check_cliques, (1 | (1 << free),), graph)
    rejected(check_cliques, (cliques[0], cliques[0]), graph)
    rejected(check_fitting, [0] * 60, graph)
    corrupted = identity.copy()
    corrupted[0] |= 1 << next(bits(graph[0]))
    rejected(check_fitting, corrupted, graph)

    return {
        "roots": len(doubled_roots()), "lines": len(lines),
        "maximal_clique_sizes": {str(k): v for k, v in
                                 sorted(Counter(c.bit_count() for c in all_cliques).items())},
        "maximum_clique_size": maximum, "maximum_cliques": len(cliques),
        "flat_census": flat_census,
        "nonempty_flats": len(rows), "unordered_nonempty_flat_pairs": pairs,
        "zero_joint_hit_pairs": zero, "rank_bound_pairs": pruned,
        "exact_pairing_rank_pairs": exact,
        "uniform_coefficient": 192, "gaussian_copy_floor": gaussian_floor,
        "rational_copy_floor": rational_floor, "abstract_row_upper_bound": row_cost,
        "deficit_upper_bound": {"slope": deficit_slope, "intercept": -2 * len(lines)},
        "sharp_witness": {"F": witness_f, "G": witness_g,
                          "ranks": [rf, rg], "pairing_rank": beta, "joint_hits": hits},
        "negative_controls": 6,
    }


def main():
    require(__debug__, "optimized Python disables geometry assertions; run without -O")
    check_sources()
    result = calculate()
    expected = json.loads((HERE / "certificate.json").read_text())
    require(result == expected, "certificate mismatch")
    print("PASS_GAUSSIAN_CLIQUE_COPY_BOUND: cost >= 40 Gaussian / 80 rational; "
          "2579856 flat pairs; 6 negative controls; kappa unchanged")


if __name__ == "__main__":
    main()
