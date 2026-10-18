"""Exact stabilizer orbits and zero-multiplicity budgets for E8 simplices."""

from collections import Counter
from itertools import combinations, combinations_with_replacement, product

from vendor.geometry import dot, require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
EXPECTED = {
    6: [{0: 1, 1: 21, 2: 63, 3: 35}],
    7: [{1: 8, 2: 56, 3: 56}, {0: 1, 2: 84, 4: 35}],
}


def signed_roots(roots):
    require(len(roots) == len(set(roots)) == 120, "incomplete E8 root inventory")
    require(all(len(r) == 8 and dot(r, r) == 8 for r in roots), "root normalization")
    signed = tuple(v for r in roots for v in (r, tuple(-x for x in r)))
    require(len(set(signed)) == 240, "duplicate signed roots")
    return signed


def extension_orbits(prefix, roots):
    """A subgroup of the pointwise stabilizer suffices; no full-group claim."""
    require(len(prefix) <= 7, "prefix exceeds seven roots")
    signed = signed_roots(roots)
    require(all(r in signed for r in prefix), "prefix contains a non-root")
    require(all(dot(a, b) == 4 for a, b in combinations(prefix, 2)), "not a root star")
    candidates = {r for r in signed if all(dot(r, a) == 4 for a in prefix)}
    normals = tuple(r for r in roots if all(dot(r, a) == 0 for a in prefix))
    unseen = set(candidates)
    classes = []
    for _ in range(240):
        if not unseen:
            break
        representative = min(unseen)
        queue, seen = [representative], {representative}
        for index in range(240):
            if index >= len(queue):
                break
            for normal in normals:
                pairing = dot(queue[index], normal)
                require(pairing % 4 == 0, "nonintegral reflection")
                reflected = tuple(x - (pairing // 4) * y
                                  for x, y in zip(queue[index], normal, strict=True))
                require(reflected in candidates, "reflection leaves extension inventory")
                if reflected not in seen:
                    seen.add(reflected)
                    queue.append(reflected)
            require(len(queue) <= 240, "reflection orbit capacity")
        require(seen <= unseen, "overlapping stabilizer orbits")
        unseen.difference_update(seen)
        classes.append((representative, len(seen)))
    require(not unseen and sum(size for _, size in classes) == len(candidates),
            "incomplete extension partition")
    return classes, len(normals), len(candidates)


def cost_spectrum(prefix, roots):
    """Minimum nonzeros after an arbitrary common coordinate shift."""
    require(len(prefix) in (6, 7), "only seven/eight vertices are supported")
    require(all(r in signed_roots(roots) for r in prefix), "non-root vertex")
    require(all(dot(a, b) == 4 for a, b in combinations(prefix, 2)), "not a root simplex")
    costs = []
    for root in roots:
        values = [0] + [dot(root, vertex) for vertex in prefix]
        costs.append(len(values) - max(Counter(values).values()))
    require(len(costs) == 120, "incomplete coordinate spectrum")
    return dict(sorted(Counter(costs).items()))


def support_lower(spectrum, removed):
    require(type(removed) is int and 0 <= removed <= 120, "invalid deletion budget")
    require(1 <= len(spectrum) <= 8 and all(type(k) is int and 0 <= k <= 7
            and type(v) is int and 0 < v <= 120 for k, v in spectrum.items()),
            "invalid support spectrum")
    require(sum(spectrum.values()) == 120, "incomplete support spectrum")
    costs = sorted(k for k, count in spectrum.items() for _ in range(count))
    return sum(costs[:120 - removed])


def simplex_receipt(roots):
    """Inductive coverage of all ordered root stars, through rank seven."""
    level, steps, spectra = [()], [], {}
    for rank in range(8):
        require(len(level) == (2 if rank == 7 else 1), "unexpected prefix inventory")
        following = []
        for prefix in level:
            if rank in (6, 7):
                spectrum = cost_spectrum(prefix, roots)
                spectra.setdefault(rank, []).append(spectrum)
            if rank < 7:
                classes, normal_count, candidate_count = extension_orbits(prefix, roots)
                steps.append({"rank": rank, "normal_lines": normal_count,
                              "candidates": candidate_count,
                              "orbit_sizes": [size for _, size in classes]})
                following.extend(prefix + (representative,) for representative, _ in classes)
        level = following
    require(spectra == EXPECTED, "root-simplex spectra changed")
    return {"steps": steps, "spectra": spectra,
            "lower_after_36_deletions": {
                rank: [support_lower(s, 36) for s in rows] for rank, rows in spectra.items()}}


def profiles(b):
    require(type(b) is int and b in (6, 7), "unsupported beta cell")
    return ((3, 5, 5) + (6,) * (b + 1), (4, 4, 5) + (6,) * (b + 1))


def cover_audit(weights):
    """All weight-certified four-piece quotient bases and two-six-flat packings."""
    require(weights in profiles(6) + profiles(7), "unsupported profile")
    rows = []
    for basis in sorted(set(combinations(weights, 4))):
        if sum(CAP[w] for w in basis) >= 53:
            continue
        remaining = list(weights)
        for weight in basis:
            remaining.remove(weight)
        costs = []
        for assignment in product(range(3), repeat=4):
            loads = [sum(w for w, g in zip(basis, assignment, strict=True) if g == group)
                     for group in (0, 1)]
            if max(loads) <= 6:
                costs.append(sum(CAP[w] for w, g in zip(basis, assignment, strict=True)
                                 if g == 2))
        require(bool(costs), "no packing with paid cuts")
        rows.append({"basis": basis, "minimum_cuts": min(costs),
                     "rank_four_anchor": min(remaining) <= 4})
    require(len(rows) == 1 and rows[0]["minimum_cuts"] == 16
            and not rows[0]["rank_four_anchor"], "prior weight-cover overlap changed")
    return rows


def original_survivors(b):
    """Independent transcription of the original TWOSIDE t=4 weight filters."""
    require(b in (6, 7), "unsupported original cell")
    distance = (0, 53, 78, 92, 100, 106, 109, 111, 112)
    rows = []
    for size in range(b, b + 5):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 6 * b:
                continue
            feasible = True
            for level in range(1, b + 1):
                prefix = weights[:size - b + level]
                total = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if ((level == 1 and target < 53 and total < 73)
                        or (level == 2 and target < 78 and total < 82)
                        or (level >= 3 and total < distance[level])):
                    feasible = False
                    break
            if not feasible:
                continue
            basis = weights[:size - b]
            killed = False
            if sum(CAP[w] for w in basis) < 53:
                killed = sum(basis) <= 7 or any(
                    all(sum(w for w, g in zip(basis, assignment, strict=True) if g == group)
                        <= 6 for group in (0, 1))
                    for assignment in product(range(2), repeat=len(basis)))
            if not killed:
                rows.append(weights)
    require(len(rows) == {6: 69, 7: 154}[b], "original survivor count changed")
    return rows


def application_rows(spectra):
    rows = []
    for b in (6, 7):
        original = original_survivors(b)
        lower = min(support_lower(s, 36) for s in spectra[b])
        for weights in profiles(b):
            require(weights in original, "target absent from original residue")
            small = sum(CAP[w] for w in weights[:3])
            large = [CAP[w] for w in weights[3:]]
            require(small == 28 and len(large) == b + 1 and set(large) == {20},
                    "profile support caps changed")
            require(small + max(large) < 53, "quotient independence fails")
            require(small + sum(sorted(large)[-2:]) < 70, "root-edge classification fails")
            old_margin = 53 * b * (b + 1) // 2 - (
                112 + (max((b + 1)**2 // 4, 2*b - 1) - 1) * small
                + (b - 1) * sum(large))
            require(old_margin < 0 and lower > sum(large), "no new strict contradiction")
            rows.append({"b": b, "t": 4, "weights": weights, "small_cap": small,
                         "basis_cap": small + max(large), "edge_cap": small + 40,
                         "endpoint_cap": sum(large), "endpoint_lower": lower,
                         "margin": lower - sum(large), "old_margin": old_margin,
                         "weight_cover_audit": cover_audit(weights)})
    return rows
