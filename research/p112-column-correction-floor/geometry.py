"""All-pairs finite premises for the column-correction proof. Apache-2.0.

Uses Mihir Srivastava's pinned PR845 geometry, following PR717.
The five support strata and small-erasure facts credit commdata2338/PR1375.
New code by Gareth Davidson with substantial OpenAI Codex assistance.
"""
from collections import Counter
import importlib.util
from itertools import combinations

from common import ROOT, digest, need

STRATA = (("x", 1, 0), ("y", 0, 1), ("plus", 1, 1),
          ("minus", 1, -1), ("generic", 1, 2))


def rank(values):
    pivots = {}
    for value in values:
        while value:
            k = value.bit_length() - 1
            if k in pivots:
                value ^= pivots[k]
            else:
                pivots[k] = value
                break
    return len(pivots)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask(indices):
    return sum(1 << i for i in indices)


def cost(pairing, left, right):
    return rank(pairing[i] & right for i in bits(left))


def load_model():
    spec = importlib.util.spec_from_file_location("retained_p112_geometry", ROOT /
                                               "research/p112-single-lift/geometry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raw = module.build()
    module.check_geometry(raw)
    order = sorted(range(112), key=lambda i: max(tuple(raw["roots"][i]),
                                              tuple(-v for v in raw["roots"][i])))
    roots, x, labels, duals = [], [], [], []
    for i in order:
        r = raw["roots"][i]
        s = 1 if tuple(r) > tuple(-v for v in r) else -1
        roots.append([s*v for v in r])
        x.append([s*v for v in raw["X"][i]])
        labels.append(raw["labels"][i])
        duals.append(raw["duals"][i])
    pairing = [mask(j for j, label in enumerate(labels)
                    if (dual & label).bit_count() % 2) for dual in duals]
    need(len(set(labels)) == 112 and 0 not in labels, "distinct nonzero labels")
    need(rank(labels) == rank(pairing) == 9, "nondegenerate nine-dimensional pairing")
    need(all(((pairing[i] >> j) & 1) == ((pairing[j] >> i) & 1)
             for i in range(112) for j in range(112)), "symmetric pairing")
    return {"roots": roots, "x": x, "labels": labels, "pairing": pairing}


def census(model):
    x, labels, b = (model[k] for k in ("x", "labels", "pairing"))
    characters = [mask(i for i, label in enumerate(labels)
                       if (f & label).bit_count() % 2) for f in range(1, 512)]
    need(len(set(characters)) == 511 and 0 not in characters, "complete character space")
    rows, pairing_counts, survivor_counts = [], Counter(), Counter()
    span_counts, free_counts, ordinary_counts = Counter(), Counter(), Counter()
    pair_records, free_boundary = [], None
    for a, c in combinations(range(8), 2):
        supports = []
        for name, aa, cc in STRATA:
            support = mask(i for i in range(112) if aa*x[i][a] + cc*x[i][c])
            dim = rank(labels[i] for i in bits(support))
            spectrum = Counter((support & ch).bit_count() for ch in characters)
            ordinary_min = min(w for w in spectrum if w)
            free_spectrum, candidates = Counter(), []
            for f, ch in enumerate(characters, 1):
                deleted = support & ch
                if not deleted:
                    continue
                neighbors = [j for j in range(112) if not b[j] & deleted]
                if neighbors:
                    free_spectrum[deleted.bit_count()] += 1
                    candidates.append((deleted.bit_count(), f, deleted, neighbors))
            free_min = min(free_spectrum)
            need(ordinary_min >= 12 and free_min >= 24, "credited erasure premises")
            need(spectrum.get(0, 0) == 2**(9-dim)-1, "annihilator count")
            # B=1 means even pairing, including the diagonal: these survive
            # every correction supported on the odd neighbors of the site.
            survivors = [rank(labels[i] for i in bits(support & b[j]))
                         for j in range(112)]
            singleton = [rank(labels[i] for i in bits(support & ~(1 << j)))
                         for j in range(112)]
            need(min(survivors) >= 7, "all-odd-neighbor erasure leaves rank seven")
            need(singleton == [dim]*112, "singleton erasure preserves the full span")
            if free_boundary is None and free_min == 24:
                _, _, erased, neighbors = min(candidates)
                free_boundary = {"pair": [a, c], "stratum": name,
                                 "deleted": list(bits(erased)),
                                 "common_odd_neighbors": neighbors,
                                 "span_before": dim,
                                 "span_after": rank(labels[i] for i in bits(support & ~erased)),
                                 "deleted_span": rank(labels[i] for i in bits(erased))}
            rows.append({"pair": [a, c], "stratum": name, "support": hex(support),
                         "span": dim, "ordinary_min": ordinary_min,
                         "ordinary_spectrum": {str(w): n for w, n in sorted(spectrum.items())},
                         "free_min": free_min,
                         "free_spectrum": {str(w): n for w, n in sorted(free_spectrum.items())},
                         "even_neighbor_spans": survivors,
                         "singleton_erasure_spans": singleton})
            supports.append(support)
            survivor_counts.update(survivors)
            span_counts[dim] += 1
            ordinary_counts[ordinary_min] += 1
            free_counts[free_min] += 1
        matrix = [[cost(b, s, t) for t in supports] for s in supports]
        need(all(v >= 8 for row in matrix for v in row), "original stratum pairing floor")
        pairing_counts.update(v for row in matrix for v in row)
        pair_records.append({"pair": [a, c], "costs": matrix})
    coordinate_costs = [cost(b, mask(i for i in range(112) if x[i][k]),
                            mask(i for i in range(112) if x[i][k])) for k in range(8)]
    need(coordinate_costs == [8]*8, "eight original COPY charges")
    odd_counts = Counter(112-row.bit_count() for row in b)
    need(odd_counts == {52: 112}, "all singleton odd neighborhoods have 52 rows")
    return {"roots_sha256": digest(model["roots"]), "coordinates_sha256": digest(x),
            "pairing_sha256": digest([hex(row) for row in b]),
            "root_order": "lexicographic positive-first doubled Euclidean E8 roots",
            "strata": rows, "pairings": pair_records, "free_boundary": free_boundary,
            "summary": {"coordinate_pairs": 28, "singleton_sites": 112, "strata": len(rows),
                        "functional_evaluations": len(rows)*511,
                        "even_neighbor_slices": len(rows)*112,
                        "singleton_erasure_slices": len(rows)*112,
                        "ordered_pairings": 700, "coordinate_costs": coordinate_costs,
                        "span_counts": {str(k): v for k, v in sorted(span_counts.items())},
                        "survivor_counts": {str(k): v for k, v in sorted(survivor_counts.items())},
                        "pairing_counts": {str(k): v for k, v in sorted(pairing_counts.items())},
                        "ordinary_min_counts": {str(k): v for k, v in sorted(ordinary_counts.items())},
                        "free_min_counts": {str(k): v for k, v in sorted(free_counts.items())},
                        "odd_neighbor_counts": {str(k): v for k, v in sorted(odd_counts.items())}}}
