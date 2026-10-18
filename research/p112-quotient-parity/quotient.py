"""Finite controls for the quotient-parity proof. Apache-2.0.

The universal linear-algebra proof is in PROOF.md. Matchings encode its
rank-four-flat restriction; they do not enumerate every quotient matroid.
"""

from itertools import combinations

from geometry import require


def partial_matchings(size):
    """Enumerate all matchings on at most eight vertices without recursion."""
    require(type(size) is int and 0 <= size <= 8, "matching size outside 0..8")
    edges = tuple(combinations(range(size), 2))
    result = []
    for count in range(size // 2 + 1):
        for chosen in combinations(edges, count):
            used = [v for edge in chosen for v in edge]
            if len(set(used)) == len(used):
                result.append(chosen)
    return result


def good_extension(partners):
    """Return an unmatched vertex; reject a malformed or perfect matching."""
    require(isinstance(partners, tuple) and len(partners) <= 8, "partner shape")
    for i, j in enumerate(partners):
        require(j is None or (type(j) is int and 0 <= j < len(partners)
                             and j != i and partners[j] == i),
                "partners must form an involution without fixed points")
    free = [i for i, j in enumerate(partners) if j is None]
    require(bool(free), "perfect matching has no good extension")
    return free[0]


def matching_receipt():
    histogram = [0] * 8
    matchings = partial_matchings(7)
    for edges in matchings:
        partners = [None] * 7
        for i, j in edges:
            partners[i], partners[j] = j, i
        chosen = good_extension(tuple(partners))
        require(partners[chosen] is None, "selected extension is matched")
        histogram[sum(x is None for x in partners)] += 1
    require(len(matchings) == 232, "incomplete seven-vertex matching census")
    require(histogram == [0, 105, 0, 105, 0, 21, 0, 1], "matching counts")
    return {"matchings": len(matchings), "unmatched_histogram": histogram}


def application():
    """The named weight profile and strict thresholds, not a feasibility search."""
    small = 8 + 3 * 12
    remaining = 6 * 12
    edge_cap = small + 2 * 12
    lower = 15 * 53
    upper = 9 * small + 5 * remaining
    require(4 * 12 < 53 and 5 * 12 < 70, "four-independence/circuit cutoffs")
    require(edge_cap < 70 and lower > upper, "root-edge/incidence cutoffs")
    return {"weights": [4] + [5] * 9, "four_piece_support_cap": 48,
            "five_circuit_support_cap": 60, "small_union_cap": small,
            "remaining_support_sum_cap": remaining, "edge_support_cap": edge_cap,
            "edge_incidence_lower": lower, "edge_incidence_upper": upper,
            "contradiction_margin": lower - upper,
            "failed_old_quotient_support_cap": small + 12}


def original_filter_control():
    """Bind this literal profile to the pinned TWOSIDE necessary filters."""
    weights = (4,) + (5,) * 9
    caps = {4: 8, 5: 12}
    prefixes = [sum(caps[w] for w in weights[:10 - (5 - level)])
                for level in range(1, 6)]
    require(prefixes == [68, 80, 92, 104, 116], "TWOSIDE prefix caps")
    require(prefixes[0] >= 53 and prefixes[1] >= 78
            and all(x >= y for x, y in zip(prefixes[2:], (92, 100, 106), strict=True)),
            "profile fails original feasibility filters")
    excess = sum(w - 2 for w in weights)
    basis_cap = sum(caps[w] for w in weights[:5])
    require(excess == 29 and excess < 30 and basis_cap == 56,
            "profile fails original budget or is support-basis certified")
    return {"b": 5, "t": 5, "prefix_caps": prefixes,
            "sum_weight_minus_two": excess, "smallest_five_support_cap": basis_cap,
            "original_BK_BK7_survivor": True}
