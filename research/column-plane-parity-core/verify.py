"""Exact ordered parity-core census. Produced by Nick Petalas. Apache-2.0."""

from array import array
from collections import Counter
from hashlib import sha1, sha256
from itertools import product
import json
from pathlib import Path


TYPE_COUNT = 15
MASK_COUNT = 1 << TYPE_COUNT
STATE_COUNT = MASK_COUNT * 16
EXPECTED_LABELED = {6: 5289, 7: 30528, 8: 70336, 9: 100032,
                    10: 102576, 11: 80080, 12: 48048, 13: 21840,
                    14: 7280, 15: 1680, 16: 240, 17: 16}
EXPECTED_ORBITS = {6: 188, 7: 1032, 8: 2312, 9: 3254, 10: 3355,
                   11: 2667, 12: 1663, 13: 813, 14: 310, 15: 91,
                   16: 21, 17: 4}
EXPECTED_DIGEST = "c8f462928008a6e39d5c3fecf3cf418ef1a77c380bde67bbf36a77d456254fef"


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def dot(a, b):
    return (a & b).bit_count() % 2


def evaluation_masks():
    return tuple(sum(dot(v, t) << (t - 1) for t in range(1, 16))
                 for v in range(16))


def admissible(mask, p, q, evaluations):
    """Projected joint rank four and six individual distance constraints."""
    if any(mask & evaluations[v] == 0 for v in range(1, 16)):
        return False
    for a in range(1, 4):
        if (mask & evaluations[a]).bit_count() + dot(a, p) < 2:
            return False
        if (mask & evaluations[a << 2]).bit_count() + dot(a, q) < 2:
            return False
    return True


def binary_rank(rows):
    require(all(0 <= row < 1 << 77 for row in rows), "rank input width at most 77")
    pivots = {}
    for row in rows:
        for bit in range(76, -1, -1):
            if row & (1 << bit):
                if bit in pivots:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return len(pivots)


def dense_rows(mask, p, q):
    """Literal four generator rows, followed by the two column units."""
    types = [t for t in range(1, 16) if mask & (1 << (t - 1))]
    rows = [0, 0, 0, 0]
    for coordinate, t in enumerate(types, start=2):
        for i in range(4):
            rows[i] |= ((t >> i) & 1) << coordinate
    for i in range(2):
        rows[i] |= ((p >> i) & 1) << 1
        rows[i + 2] |= (q >> i) & 1
    return rows + [1, 2]


def dense_admissible(rows):
    require(len(rows) == 6, "six literal rows required")
    words = [rows[0], rows[1], rows[0] ^ rows[1],
             rows[2], rows[3], rows[2] ^ rows[3]]
    return binary_rank(rows) == 6 and all(w.bit_count() >= 2 for w in words)


def basis_actions():
    # An ordered independent pair is exactly a GL(2,2) matrix's columns.
    actions = tuple((0, a, b, a ^ b)
                    for a in range(1, 4) for b in range(1, 4) if a != b)
    require(len(set(actions)) == 6, "GL(2,2) action has six elements")
    return actions


def mask_permutation(left, right):
    """All 32768 subsets under this change of the two plane bases."""
    images = [0] + [1 << (left[t & 3] + (right[t >> 2] << 2) - 1)
                    for t in range(1, 16)]
    table = array("H", [0]) * MASK_COUNT
    for mask in range(1, MASK_COUNT):
        low = mask & -mask
        table[mask] = table[mask ^ low] | images[low.bit_length()]
    return table


def actions_with_tables():
    actions = basis_actions()
    return [(left, right, mask_permutation(left, right))
            for left, right in product(actions, repeat=2)]


def fixed_supports(left, right):
    """Fixed subsets are unions of permutation cycles, without lookup tables."""
    seen = set()
    cycles = []
    for start in range(1, 16):
        if start in seen:
            continue
        current = start
        cycle = 0
        for _ in range(15):
            require(current not in seen, "disjoint permutation cycles")
            seen.add(current)
            cycle |= 1 << (current - 1)
            current = left[current & 3] + (right[current >> 2] << 2)
            if current == start:
                break
        require(current == start, "cycle closes within fifteen steps")
        cycles.append(cycle)
    require(len(seen) == 15, "every nonzero joint type in one cycle")
    supports = [0]
    for cycle in cycles:
        supports += [mask | cycle for mask in supports]
    require(len(supports) <= MASK_COUNT, "fixed support bound")
    return supports


def burnside_census():
    sums = Counter()
    group = basis_actions()
    for left, right in product(group, repeat=2):
        cross_values = [(p, q) for p, q in product(range(4), repeat=2)
                        if left[p] == p and right[q] == q]
        for mask in fixed_supports(left, right):
            for p, q in cross_values:
                if dense_admissible(dense_rows(mask, p, q)):
                    sums[2 + mask.bit_count()] += 1
    require(all(count % 36 == 0 for count in sums.values()),
            "Burnside fixed-point totals divisible by group order")
    return dict(sorted((width, count // 36) for width, count in sums.items()))


def census(evaluations, actions):
    visited = bytearray(STATE_COUNT)
    labeled = Counter()
    orbits = Counter()
    sizes = Counter()
    digest = sha256()
    for state in range(STATE_COUNT):
        if visited[state]:
            continue
        mask, cross = divmod(state, 16)
        p, q = divmod(cross, 4)
        if not admissible(mask, p, q, evaluations):
            continue
        orbit = {16 * table[mask] + 4 * left[p] + right[q]
                 for left, right, table in actions}
        require(state == min(orbit), "ordered scan finds canonical representative")
        require(36 % len(orbit) == 0, "orbit-stabilizer divisibility")
        width = 2 + mask.bit_count()
        orbits[width] += 1
        sizes[len(orbit)] += 1
        labeled[width] += len(orbit)
        digest.update(state.to_bytes(4, "little"))
        for image in orbit:
            require(not visited[image], "orbits must be disjoint")
            m, c = divmod(image, 16)
            require(admissible(m, c // 4, c % 4, evaluations),
                    "basis changes preserve admissibility")
            visited[image] = 1
    require(sum(visited) == sum(labeled.values()), "state coverage total")
    return {"labeled_by_width": dict(sorted(labeled.items())),
            "orbits_by_width": dict(sorted(orbits.items())),
            "orbit_sizes": dict(sorted(sizes.items())),
            "labeled_total": sum(labeled.values()),
            "orbit_total": sum(orbits.values()),
            "canonical_sha256": digest.hexdigest()}


def check_dense_equivalence(evaluations):
    # Every support is checked; rank is independent of the cross values.
    counts = Counter()
    for mask in range(MASK_COUNT):
        base = dense_rows(mask, 0, 0)
        rank_pass = binary_rank(base) == 6
        mask_pass = all(mask & evaluations[v] for v in range(1, 16))
        require(rank_pass == mask_pass, "dense/mask projected-rank mismatch")
        weights = [base[0].bit_count(), base[1].bit_count(),
                   (base[0] ^ base[1]).bit_count(), base[2].bit_count(),
                   base[3].bit_count(), (base[2] ^ base[3]).bit_count()]
        for p, q in product(range(4), repeat=2):
            # Derive cross contributions from literal generator rows.
            cross = [((p >> 0) & 1) << 1, ((p >> 1) & 1) << 1,
                     (q >> 0) & 1, (q >> 1) & 1]
            extra = [cross[0], cross[1], cross[0] ^ cross[1],
                     cross[2], cross[3], cross[2] ^ cross[3]]
            valid = rank_pass and all(w + e.bit_count() >= 2
                                      for w, e in zip(weights, extra))
            require(valid == admissible(mask, p, q, evaluations),
                    "dense/mask distance mismatch")
            if valid:
                counts[2 + mask.bit_count()] += 1
    return dict(sorted(counts.items()))


def reduction_rows(multiplicities, p, q):
    require(len(multiplicities) == 15, "fifteen external joint types required")
    require(all(type(n) is int and 0 <= n <= 5 for n in multiplicities),
            "bounded checker permits multiplicities zero through five")
    expanded = [0, 0, 0, 0, 1, 2]
    coordinate = 2
    for t, count in enumerate(multiplicities, start=1):
        for _ in range(count):
            for i in range(4):
                expanded[i] |= ((t >> i) & 1) << coordinate
            coordinate += 1
    for i in range(2):
        expanded[i] |= ((p >> i) & 1) << 1
        expanded[i + 2] |= (q >> i) & 1
    return expanded


def literal_pair_deletion(rows):
    """Group actual external columns and project onto odd-sized groups."""
    require(len(rows) == 6 and max(rows).bit_length() <= 77,
            "bounded literal deletion matrix")
    groups = [[] for _ in range(16)]
    for coordinate in range(2, 77):
        kind = sum(((rows[i] >> coordinate) & 1) << i for i in range(4))
        if kind:
            groups[kind].append(coordinate)
    keep = [0, 1] + [positions[-1] for positions in groups[1:]
                     if len(positions) % 2]
    return [sum(((row >> old) & 1) << new for new, old in enumerate(keep))
            for row in rows]


def check_reduction(evaluations):
    checks = 0
    # Bounded literal deletion fixtures; the all-width conclusion is written.
    for mask in (0, 1, 0x1234, 0x5555, 0x7fff):
        for t, p, q in product(range(15), range(4), range(4)):
            counts = [(mask >> i) & 1 for i in range(15)]
            counts[t] += 2
            reduced = sum((n % 2) << i for i, n in enumerate(counts))
            require(reduced == mask, "pair deletion leaves parity support")
            original = reduction_rows(counts, p, q)
            rows = literal_pair_deletion(original)
            require(rows == dense_rows(mask, p, q), "literal projection matches core")
            require(dense_admissible(rows) == admissible(mask, p, q, evaluations),
                    "literal deletion disagrees with criterion")
            require(not dense_admissible(rows) or dense_admissible(original),
                    "valid core implies valid original")
            checks += 1
    # An empty parity core can come from a valid pair.
    even = [0] * 15
    for t in (1, 2, 4, 8):
        even[t - 1] = 2
    require(dense_admissible(reduction_rows(even, 0, 0)),
            "even multiplicities can define a valid original")
    require(not admissible(0, 0, 0, evaluations), "even example collapses")
    require(admissible(0x7fff, 0, 0, evaluations), "sharp width seventeen")
    # Rank can survive while a single plane's distance fails.
    axes = sum(1 << (t - 1) for t in (1, 2, 4, 8))
    require(binary_rank(dense_rows(axes, 0, 0)) == 6,
            "distance control retains independent image spaces")
    require(not admissible(axes, 0, 0, evaluations), "distance constraint needed")
    require(admissible(axes, 3, 3, evaluations), "cross bits can repair distance")
    # Both planes can have distance two yet share a projected image.
    overlap = sum(1 << (t - 1) for t in (5, 10, 15))
    rows = dense_rows(overlap, 0, 0)
    require(all(w.bit_count() == 2 for w in
                (rows[0], rows[1], rows[0] ^ rows[1],
                 rows[2], rows[3], rows[2] ^ rows[3])),
            "rank control has six weight-two nonzero words")
    require(not admissible(overlap, 0, 0, evaluations), "joint rank needed")
    return checks


def check_sources():
    package = Path(__file__).resolve().parent
    sources = json.loads((package / "SOURCES.json").read_text())
    files = sources["retained_predecessor"]["files"]
    require(len(files) == 2, "two retained source notes")
    for row in files:
        raw = (package / row["path"]).read_bytes()
        require(sha256(raw).hexdigest() == row["sha256"], "retained source hash")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(sha1(blob).hexdigest() == row["git_blob"], "retained Git blob")


def main():
    check_sources()
    evaluations = evaluation_masks()
    reduction_checks = check_reduction(evaluations)
    labeled = check_dense_equivalence(evaluations)
    result = census(evaluations, actions_with_tables())
    require(labeled == result["labeled_by_width"], "independent labeled census")
    require(labeled == EXPECTED_LABELED, "published labeled counts")
    require(result["orbits_by_width"] == EXPECTED_ORBITS, "published orbit counts")
    require(result["canonical_sha256"] == EXPECTED_DIGEST, "canonical digest")
    require(burnside_census() == result["orbits_by_width"],
            "independent literal-matrix Burnside orbit count")
    print(json.dumps({"status": "PASS_COLUMN_PLANE_PARITY_CORE",
                      "states_checked": STATE_COUNT,
                      "deletion_fixtures": reduction_checks,
                      **result}, sort_keys=True))


if __name__ == "__main__":
    main()
