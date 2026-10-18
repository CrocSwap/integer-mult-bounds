"""Independent Euclidean/Gram replay of the finite premises. Apache-2.0.

Imports no primary geometry, retained geometry or fixture arithmetic.
New implementation by Gareth Davidson with substantial OpenAI Codex assistance.
Both implementations are from the same contributor, not independent human review.
"""
import argparse
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, digest, need, same, sources, strict_load


def basis(vectors):
    rows = {}
    for v in vectors:
        while v:
            p = v & -v
            if p in rows:
                v ^= rows[p]
            else:
                rows[p] = v
                break
    return list(rows.values())


def gram_model():
    lines = set()
    for a, b in combinations(range(8), 2):
        for sign in [-1, 1]:
            r = [0]*8
            r[a], r[b] = 2, 2*sign
            lines.add(tuple(r))
    for signs in product([-1, 1], repeat=7):
        r = (1,)+signs
        if r.count(-1) % 2 == 0:
            lines.add(r)
    frame = []
    for a in range(0, 8, 2):
        for sign in [1, -1]:
            r = [0]*8
            r[a], r[a+1] = 2, 2*sign
            frame.append(tuple(r))
    need(len(lines) == 120 and set(frame) <= lines, "independent root inventory")
    roots = sorted(lines-set(frame))
    dot = lambda a, b: sum(v*w for v, w in zip(a, b))
    x = [[dot(r, f)//4 for f in frame] for r in roots]
    gram = [[dot(r, s)//4 for s in roots] for r in roots]
    b = [sum(((v+1) % 2) << j for j, v in enumerate(row)) for row in gram]
    need(all(dot(x[i], x[j]) == 2*gram[i][j]
             for i in range(112) for j in range(112)), "independent all-pairs coordinate identity")
    need(len(roots) == 112 and len(set(b)) == 112 and 0 not in b,
         "independent distinct nonzero label evaluations")
    generators = basis(b)
    need(len(generators) == 9, "independent binary ambient dimension")
    characters = {0}
    for row in generators:
        characters |= {v ^ row for v in characters}
    need(len(characters) == 512, "independent full dual evaluation code")
    return roots, x, b, sorted(characters-{0})


def check(geometry, model=None):
    roots, x, b, characters = gram_model() if model is None else model
    dim = lambda support: len(basis(b[i] for i in support))
    cost = lambda left, right: len(basis(b[i] & sum(1 << j for j in right) for i in left))
    records, pairs = [], []
    spans, survivors, pairings = Counter(), Counter(), Counter()
    ordinary, free = Counter(), Counter()
    support_map = {}
    names = ["x", "y", "plus", "minus", "generic"]
    for a, c in combinations(range(8), 2):
        predicates = [lambda v, w: bool(v), lambda v, w: bool(w),
                      lambda v, w: v+w != 0, lambda v, w: v-w != 0,
                      lambda v, w: bool(v or w)]
        supports = []
        for name, predicate in zip(names, predicates):
            support = [i for i in range(112) if predicate(x[i][a], x[i][c])]
            support_map[(a, c, name)] = support
            sm = sum(1 << i for i in support)
            spectrum = Counter((word & sm).bit_count() for word in characters)
            free_spectrum = Counter()
            for word in characters:
                deleted = word & sm
                if deleted:
                    even_union = 0
                    for i in support:
                        if deleted >> i & 1:
                            even_union |= b[i]
                    if even_union != (1 << 112)-1:
                        free_spectrum[deleted.bit_count()] += 1
            span = dim(support)
            one_point = [dim([i for i in support if i != j]) for j in range(112)]
            even = [dim([i for i in support if b[i] >> j & 1]) for j in range(112)]
            d, f = min(w for w in spectrum if w), min(free_spectrum)
            need(d >= 12 and f >= 24, "independent erasure bounds")
            need(min(even) >= 7 and one_point == [span]*112,
                 "independent survivor and singleton bounds")
            records.append({"pair": [a, c], "stratum": name, "support": hex(sm),
                            "span": span, "ordinary_min": d,
                            "ordinary_spectrum": {str(w): n for w, n in spectrum.items()},
                            "free_min": f, "free_spectrum": {str(w): n for w, n in free_spectrum.items()},
                            "even_neighbor_spans": even, "singleton_erasure_spans": one_point})
            supports.append(support)
            spans[span] += 1
            survivors.update(even)
            ordinary[d] += 1
            free[f] += 1
        matrix = [[cost(s, t) for t in supports] for s in supports]
        need(all(v >= 8 for r in matrix for v in r), "independent pairing floor")
        pairings.update(v for r in matrix for v in r)
        pairs.append({"pair": [a, c], "costs": matrix})
    coordinate_costs = [cost([i for i in range(112) if x[i][k]],
                             [i for i in range(112) if x[i][k]]) for k in range(8)]
    need(coordinate_costs == [8]*8, "independent coordinate charges")
    boundary = geometry["free_boundary"]
    need(set(boundary) == {"pair", "stratum", "deleted", "common_odd_neighbors",
                          "span_before", "span_after", "deleted_span"}, "boundary fields")
    support = support_map[(*boundary["pair"], boundary["stratum"])]
    deleted = boundary["deleted"]
    need(len(deleted) == len(set(deleted)) == 24 and set(deleted) <= set(support),
         "boundary 24 distinct rows")
    dm, sm = sum(1 << i for i in deleted), sum(1 << i for i in support)
    need(any((word & sm) == dm for word in characters), "boundary is an actual functional cut")
    neighbors = [j for j in range(112) if all(not (b[i] >> j & 1) for i in deleted)]
    expected_boundary = {"pair": boundary["pair"], "stratum": boundary["stratum"],
                         "deleted": deleted, "common_odd_neighbors": neighbors,
                         "span_before": dim(support),
                         "span_after": dim([i for i in support if i not in deleted]),
                         "deleted_span": dim(deleted)}
    need(neighbors and expected_boundary["span_after"] < expected_boundary["span_before"],
         "free boundary has a neighbor and loses span")
    same(boundary, expected_boundary, "independent boundary receipt")
    expected = {"roots_sha256": digest([list(r) for r in roots]), "coordinates_sha256": digest(x),
                "pairing_sha256": digest([hex(row) for row in b]),
                "root_order": "lexicographic positive-first doubled Euclidean E8 roots",
                "strata": records, "pairings": pairs, "free_boundary": expected_boundary,
                "summary": {"coordinate_pairs": 28, "singleton_sites": 112, "strata": 140,
                            "functional_evaluations": 71540, "even_neighbor_slices": 15680,
                            "singleton_erasure_slices": 15680, "ordered_pairings": 700,
                            "coordinate_costs": coordinate_costs,
                            "span_counts": {str(k): v for k, v in spans.items()},
                            "survivor_counts": {str(k): v for k, v in survivors.items()},
                            "pairing_counts": {str(k): v for k, v in pairings.items()},
                            "ordinary_min_counts": {str(k): v for k, v in ordinary.items()},
                            "free_min_counts": {str(k): v for k, v in free.items()},
                            "odd_neighbor_counts": {str(k): v for k, v in Counter(
                                112-row.bit_count() for row in b).items()}}}
    same(geometry, expected, "independent complete geometry receipt")
    return {"geometry_sha256": digest(expected), "full_gram_entries": 112**2,
            "no_primary_geometry_import": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=HERE/"EXPECTED.json")
    args = parser.parse_args()
    sources()
    receipt = strict_load(args.receipt)
    result = check(receipt["geometry"])
    print("PASS_P112_COLUMN_INDEPENDENT", result["geometry_sha256"])


if __name__ == "__main__":
    main()
