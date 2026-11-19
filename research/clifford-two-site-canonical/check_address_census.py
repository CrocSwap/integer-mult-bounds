"""Independent finite-relation enumeration and global norm/normalization checks."""
from collections import Counter
from itertools import product
from math import prod

from address_census import (
    adjoint_norm_squared, compatible_relations, nonzero_labels, shell_profile,
    support_histogram, type_multiplicities,
)


def require(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: {actual} != {expected}")


def binary_rank(values):
    pivots = {}
    for value in values:
        while value and value.bit_length() in pivots:
            value ^= pivots[value.bit_length()]
        if value:
            pivots[value.bit_length()] = value
    return len(pivots)


def all_planes(n):
    # Insert one independent generator at a time; the frozenset is canonical.
    found = {frozenset([0])}
    for vector in range(1, 1 << n):
        found.update(space.union(x ^ vector for x in space)
                     for space in list(found) if vector not in space)
    return found


def independent_relation_census(n):
    # Describe each actual support as r+H=T(c). Enumerate H and every
    # surjection T on the n explicit coordinate generators.
    types = list(dict(type_multiplicities(n, 2 * n)))
    counts = {kind: Counter() for kind in types}
    total = 0
    for plane in all_planes(n):
        h = binary_rank(plane)
        quot = [min(x ^ u for u in plane) for x in range(1 << n)]
        classes = sorted(set(quot))
        # Minimum representatives form the linear complement to RREF pivots.
        if any(quot[x ^ y] != quot[x] ^ quot[y]
               for x in range(1 << n) for y in range(1 << n)):
            raise ValueError("Nonlinear quotient coordinates")
        # Canonical displacement spaces have a-c pure row generators,
        # b-c pure column generators and c tied coordinate generators.
        constraints = []
        for a, b, c in types:
            if any(quot[1 << i] for i in range(a - c)):
                continue
            required = (0,) * (b - c) + tuple(quot[1 << i] for i in range(a - c, a))
            constraints.append((required, (a, b, c)))
        for columns in product(classes, repeat=n):
            if binary_rank(columns) != n - h:
                continue
            total += 1
            for required, kind in constraints:
                if columns[:len(required)] == required:
                    counts[kind][h] += 1
    require(total, 1 << (n*n), "number of distinct support relations")
    for (a, b, c), shells in counts.items():
        for h in range(n + 1):
            require(shells[h], compatible_relations(n, a, b, c, h),
                    (n, a, b, c, h))


def check_spectrum_counts():
    from two_site_spectrum import pair_types, support_counts

    pairs = pair_types(4)
    for h in range(5):
        _, tally = support_counts(4, h)
        for (row, col), expected in tally.items():
            (i, j), _ = pairs[row]
            (k, l), _ = pairs[col]
            direct = [(i, k), (j, l)]
            crossed = [(i, l), (j, k)]
            counts = []
            for seq in (direct, crossed, direct + crossed):
                a = binary_rank(x for x, _ in seq)
                b = binary_rank(y for _, y in seq)
                d = binary_rank(x << 4 | y for x, y in seq)
                counts.append(compatible_relations(4, a, b, a+b-d, h))
            require(counts, expected, (row, col, h, "normal block support counts"))


def check():
    check_spectrum_counts()
    for n in range(1, 5):
        independent_relation_census(n)

    types = Counter()
    for first, second in product(range(256), repeat=2):
        a = binary_rank((first >> 4, second >> 4))
        b = binary_rank((first & 15, second & 15))
        d = binary_rank((first, second))
        types[a, b, a+b-d] += 1
    require(types, dict(type_multiplicities(4, 2)), "all 65536 two-site observations")

    two = support_histogram(4, 2)
    require(list(two.items()), [
        (5929571450880, 420), (5978984546304, 1350), (6028397641728, 18900),
        (6078693113856, 44100), (6670767882240, 90), (6781947346944, 675),
        (8338459852800, 1),
    ], "two-site census")
    all_addresses = support_histogram(4, 12)
    require(len(all_addresses), 30, "full support-size count")
    require(all_addresses[min(all_addresses)], 74959609988606102773113260160,
            "multiplicity of the minimum at a fixed base address")
    require(sum(all_addresses.values()), 1 << 96, "all addresses at a fixed base")
    require([len(support_histogram(4, k)) for k in range(7)],
            [1, 3, 7, 13, 22, 27, 30], "support growth with free positions")

    for n in range(1, 5):
        group = (1 << (n*n)) * prod((1 << (2*i)) - 1 for i in range(1, n+1))
        require(sum(shell_profile(n, 0, 0, 0)), group, "all symplectic fibres")
        for w in (1, 2, 6, 13):
            mass = 0
            for kind, count in type_multiplicities(n, w - 1):
                profile = shell_profile(n, *kind)
                mass += count * adjoint_norm_squared(n, w, profile)
            # Full basis sum is |Sp|*4^n because every column has unit norm;
            # dividing by the 4^n equivalent base addresses leaves |Sp|.
            require(mass, group, (n, w, "trace"))
    print("PASS exact coordinate histograms, exhaustive support relations n=1..4 and trace identities and all spectrum block tallies")


if __name__ == "__main__":
    check()
