# SPDX-License-Identifier: Apache-2.0
"""Complete retained-hit quotient for the nine new COPY6 patterns.

The full parent/codeword traversal follows the credited PR1347 and
p112-rank6-cover-representatives patterns. New work is the mixed COPY62
family, all eight coordinate choices, and exact proper-clique separators.
"""
from collections import Counter
import hashlib
import itertools
import screen


def require(condition, message):
    if not condition:
        raise ValueError(message)


def representatives(data, pairing, supports, frames, original):
    incidence = [0] * 120
    for j, frame in enumerate(frames):
        for root in frame:
            incidence[root] |= 1 << j
    cache = {}

    def hits(mask):
        if mask not in cache:
            value = 0
            for root in screen.engine.bits(mask):
                value |= incidence[root]
            cache[mask] = value
        return cache[mask]

    patterns = [hits(left) & hits(right) for left, right in original[:9]]
    require(len(set(patterns)) == 9 and all(p.bit_count() == 1120 for p in patterns),
            "nine distinct new maximum-hit patterns")
    tagged_counts = [0] * 9
    found = [{} for _ in patterns]
    parent_counts = Counter()
    cases = 0
    digest = hashlib.sha256()
    for a, left in enumerate(supports):
        for b, right in enumerate(supports):
            rank = screen.engine.rank(pairing, left, right)
            parent_counts[rank] += 1
            if rank != 7:
                continue
            words = screen.engine.column_code(pairing, left, right)
            require(len(words) == 127 and len(set(words)) == 127, "complete nonzero rank-seven code")
            right_hits = hits(right)
            for cut in words:
                cases += 1
                digest.update(f"{a},{b},{cut:x}\n".encode())
                row = left ^ cut
                met = hits(row) & right_hits
                for k, target in enumerate(patterns):
                    if target & ~met:
                        continue
                    tagged_counts[k] += 1
                    require(screen.engine.rank(pairing, row, right) == 6, "representative rank")
                    found[k].setdefault((row, right), dict(parent=[a, b], cut=format(cut, "x"),
                                                        left=format(row, "x"), right=format(right, "x"),
                                                        diagonal=format(row & right, "x"),
                                                        hits=met.bit_count()))
    require(dict(parent_counts) == {7: 7616, 8: 37440, 9: 12544}, "complete parent-rank census")
    require(cases == 967232, "complete maximal row-cut census")
    choices = [[table[key] for key in sorted(table)] for table in found]
    require(tagged_counts == [4] * 9 and [len(c) for c in choices] == [2] * 9,
            "complete representative quotient changed")
    require(all(record["hits"] == 1120 for group in choices for record in group),
            "a strict hit-superset appeared")
    require(all(len({record["diagonal"] for record in group}) == 2 for group in choices),
            "two genuinely different diagonal choices per pattern")
    require(all(hits(supports[2*c]) == (1 << len(frames)) - 1 for c in data["punctured_frame"]),
            "each coordinate star meets every live frame")
    census = dict(parent_rank_histogram=dict(sorted(parent_counts.items())), maximal_row_cuts=cases,
                  tagged_matches=tagged_counts, distinct_support_choices=[len(c) for c in choices],
                  enumeration_sha256=digest.hexdigest(), representatives=choices)
    return choices, census


def check_rank_cut(data, terms, cut):
    roots = cut["roots"]
    require(len(roots) == 2 and len(set(roots)) == 2 and set(roots) <= set(data["live"]), "rank-cut roots")
    a, b = roots
    require(sum(x*y for x, y in zip(data["lines"][a], data["lines"][b])) == 0,
            "rank-cut roots must be orthogonal")
    mask = (1 << a) | (1 << b)
    active = [j for j, (left, right) in enumerate(terms) if left & mask and right & mask]
    require(active == cut["active_terms"], "rank-cut incidence")
    require(len(active) < 2, "rank-two target is not excluded")
    return True


def quotient(data, ip, supports, choices):
    live_mask = sum(1 << i for i in data["live"])
    pairs = [(a, b) for a, b in itertools.combinations(data["live"], 2) if ip[a][b] == 0]
    per_coordinate = {c: Counter() for c in data["punctured_frame"]}
    survivors = []
    for indices in itertools.product(range(2), repeat=9):
        selected = [choices[k][choice] for k, choice in enumerate(indices)]
        terms = [(int(record["left"], 16), int(record["right"], 16)) for record in selected]
        union = 0
        for left, right in terms:
            union |= left & right
        for coordinate in data["punctured_frame"]:
            star = supports[2 * coordinate]
            totals = per_coordinate[coordinate]
            totals["families"] += 1
            if union | star != live_mask:
                totals["diagonal_rejected"] += 1
                continue
            completed = terms + [(star, star)]
            cut = None
            for a, b in pairs:
                mask = (1 << a) | (1 << b)
                active = [j for j, (left, right) in enumerate(completed) if left & mask and right & mask]
                if len(active) < 2:
                    cut = dict(roots=[a, b], active_terms=active)
                    break
            require(cut is not None, "a diagonal survivor needs a new coefficient investigation")
            check_rank_cut(data, completed, cut)
            totals["rank2_rejected"] += 1
            survivors.append(dict(coordinate_root=coordinate, choices=list(indices),
                                  terms=[[record["parent"][0], record["parent"][1], record["cut"]]
                                         for record in selected], rank_cut=cut))
    totals = sum(per_coordinate.values(), Counter())
    require(totals == {"families": 4096, "diagonal_rejected": 4093, "rank2_rejected": 3},
            "complete quotient result changed")
    return dict(totals=dict(totals), per_coordinate={str(c): dict(v) for c, v in per_coordinate.items()},
                diagonal_survivors=survivors)
