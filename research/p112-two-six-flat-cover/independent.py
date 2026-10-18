"""Separate direct affine-five-space enumeration on the eight label coordinates."""

from itertools import combinations, product

from vendor.geometry import require


def affine_masks(labels):
    require(
        len(set(labels)) == 112 and all(0 < x < 512 and x & 1 for x in labels),
        "affine label domain",
    )
    lookup = [0] * 256
    for i, label in enumerate(labels):
        lookup[label >> 1] = 1 << i
    masks, spaces, cosets = {0}, 0, 0
    for pivots in combinations(range(8), 5):
        other = tuple(c for c in range(8) if c not in pivots)
        offsets = tuple(
            sum((code >> j & 1) << c for j, c in enumerate(other)) for code in range(8)
        )
        choices = []
        for pivot in pivots:
            free = tuple(c for c in other if c > pivot)
            choices.append(
                tuple(
                    (1 << pivot) | sum((code >> j & 1) << c for j, c in enumerate(free))
                    for code in range(1 << len(free))
                )
            )
        for rows in product(*choices):
            span = [0]
            for row in rows:
                span += [x ^ row for x in span]
            require(len(span) == len(set(span)) == 32, "affine basis rank")
            for offset in offsets:
                masks.add(sum(lookup[x ^ offset] for x in span))
                cosets += 1
            spaces += 1
    require(
        (spaces, cosets, len(masks)) == (97155, 777240, 776806),
        "incomplete affine census",
    )
    return tuple(sorted(masks)), {
        "linear_five_spaces": spaces,
        "affine_cosets": cosets,
        "distinct_masks": len(masks),
    }


def check_witness(points, labels, row):
    """Use explicit sets and exhaustive XOR closure, separate from cover.rank."""
    normal = row["normal"]
    off = {
        i
        for i, root in enumerate(points)
        if sum(a * b for a, b in zip(normal, root, strict=True)) != 0
    }
    flats = [set(x) for x in row["flat_lines"]]
    require(len(flats) == 2 and all(len(x) <= 20 for x in flats), "witness flats")
    for flat in flats:
        require(all(type(i) is int and 0 <= i < 112 for i in flat), "witness indices")
        closure = {0}
        for i in sorted(flat):
            closure |= {x ^ labels[i] for x in closure}
            require(len(closure) <= 64, "witness exceeds binary rank six")
        require(len(closure) == 64, "witness binary rank is not six")
        require(
            flat == {i for i, label in enumerate(labels) if label in closure},
            "witness does not contain its full live flat",
        )
    extra = off - flats[0] - flats[1]
    require(
        len(off & (flats[0] | flats[1])) == 38
        and extra == set(row["extra_lines"])
        and len(extra) == row["minimum_extra"],
        "witness cover differs",
    )
    return True
