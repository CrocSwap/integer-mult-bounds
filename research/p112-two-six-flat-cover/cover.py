"""Exact two-six-flat coverage of each of the 120 P112 root codewords."""

from hashlib import sha256
from itertools import combinations, product

from vendor.geometry import dot, require


def set_bits(mask, size=112):
    require(type(mask) is int and 0 <= mask < 1 << size, "invalid support mask")
    return [i for i in range(size) if mask >> i & 1]


def rank(rows):
    require(len(rows) <= 112 and all(0 <= x < 512 for x in rows), "binary rows")
    basis = [0] * 9
    for value in rows:
        for pivot in range(8, -1, -1):
            if value >> pivot & 1:
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    return sum(bool(x) for x in basis)


def six_flat_masks(labels):
    """Enumerate kernels of every rank-three reverse-RREF annihilator."""
    require(
        len(set(labels)) == 112 and all(0 < x < 512 and x & 1 for x in labels),
        "P112 label domain",
    )
    kernels = tuple(
        sum(1 << i for i, x in enumerate(labels) if (x & row).bit_count() % 2 == 0)
        for row in range(512)
    )
    masks, count, histogram = set(), 0, [0] * 113
    for pivots in combinations(range(9), 3):
        choices = []
        for pivot in pivots:
            free = tuple(i for i in range(pivot) if i not in pivots)
            choices.append(
                tuple(
                    kernels[
                        (1 << pivot)
                        | sum((code >> i & 1) << c for i, c in enumerate(free))
                    ]
                    for code in range(1 << len(free))
                )
            )
        for a, b, c in product(*choices):
            mask = a & b & c
            histogram[mask.bit_count()] += 1
            masks.add(mask)
            count += 1
    require(count == 788035 and len(masks) == 776806, "incomplete six-flat census")
    require(max(i for i, n in enumerate(histogram) if n) == 20, "six-flat capacity")
    return tuple(sorted(masks)), {
        "subspaces": count,
        "distinct_masks": len(masks),
        "histogram": histogram,
    }


def exact_pair_cap(intersections, cap=20, target=38):
    """Certify the upper bound and return an attaining pair, with safe pruning."""
    require(0 <= target <= 2 * cap <= 224, "pair-cover bounds")
    require(1 <= len(intersections) <= 776806, "pair-cover inventory capacity")
    require(
        all(
            type(x) is int and 0 <= x < 1 << 112 and x.bit_count() <= cap
            for x in intersections
        ),
        "single-flat cap",
    )
    # A discarded set plus any set covers fewer than target coordinates.
    high = tuple(sorted({x for x in intersections if x.bit_count() >= target - cap}))
    require(len(high) <= 4096, "high-intersection capacity")
    witness, comparisons = None, 0
    for i, a in enumerate(high):
        for b in high[i:]:
            comparisons += 1
            covered = (a | b).bit_count()
            require(covered <= target, "two-flat cover exceeds bound")
            if covered == target and witness is None:
                witness = (a, b)
    require(witness is not None, "pair-cover bound is not sharp")
    return witness, high, comparisons


def all_root_covers(roots, points, labels, masks):
    require(len(roots) == 120 and len(points) == 112, "root inventory")
    rows = []
    for normal in roots:
        off = sum(1 << i for i, p in enumerate(points) if dot(normal, p))
        intersections = {mask & off for mask in masks}
        pair, high, comparisons = exact_pair_cap(intersections)
        # Recover actual six-flat masks, not just their restricted intersections.
        original = [next(mask for mask in masks if mask & off == cut) for cut in pair]
        require(
            all(rank([labels[i] for i in set_bits(mask)]) == 6 for mask in original),
            "attaining flat rank",
        )
        covered = off & (original[0] | original[1])
        require(covered.bit_count() == 38, "attaining cover changed")
        rows.append(
            {
                "normal": normal,
                "support": off.bit_count(),
                "maximum_covered": 38,
                "minimum_extra": off.bit_count() - 38,
                "high_intersections": len(high),
                "pair_comparisons": comparisons,
                "high_sha256": sha256(str(high).encode()).hexdigest(),
                "flat_lines": [set_bits(mask) for mask in original],
                "extra_lines": set_bits(off & ~covered),
            }
        )
    require(
        sorted(row["minimum_extra"] for row in rows) == [15] * 112 + [18] * 8,
        "root cover minima changed",
    )
    return rows
