"""Distribution of nonzero adjoint coefficients over coordinate observations."""
from collections import Counter
from fractions import Fraction
from math import prod


def injections(domain, target):
    """Number of independent ordered domain-tuples in a binary target."""
    if not 0 <= domain <= target:
        return 0
    return prod((1 << target) - (1 << i) for i in range(domain))


def subspace_count(n, k):
    if not 0 <= k <= n:
        return 0
    return injections(k, n) // injections(k, k)


def choices_off_projection(n, projection_dim, kernel_dim, h):
    """Choose an h-plane with one prescribed intersection with a fixed plane."""
    free = h - kernel_dim
    if not 0 <= free <= n - projection_dim:
        return 0
    return subspace_count(n - projection_dim, free) << ((projection_dim - kernel_dim) * free)


def compatible_relations(n, a, b, c, h):
    """Quotient-isomorphism supports at rank h containing one displacement space."""
    total = 0
    for e in range(c + 1):
        constrained = c - e
        complement = n - h - constrained
        if complement < 0:
            continue
        left = choices_off_projection(n, a, a - c + e, h)
        right = choices_off_projection(n, b, b - c + e, h)
        extensions = injections(complement, complement) << (constrained * complement)
        total += subspace_count(c, e) * left * right * extensions
    return total


def shell_profile(n, a, b, c):
    """Occupied symplectic fibres by Hadamard rank. c is the common quotient rank."""
    if not (0 <= c <= min(a, b) and max(a, b) <= n):
        raise ValueError("Invalid displacement type")
    parabolic = injections(n, n) << (n * (n + 1) // 2)
    counts = []
    for h in range(n + 1):
        per_relation, remainder = divmod(
            parabolic << (h * (h + 1) // 2), injections(n - h, n))
        if remainder:
            raise ArithmeticError("Expected integral fibre multiplicity")
        counts.append(per_relation * compatible_relations(n, a, b, c, h))
    return tuple(counts)


def nonzero_labels(n, profile):
    return sum(count << (n + h) for h, count in enumerate(profile))


def adjoint_norm_squared(n, width, profile):
    return sum(Fraction(count, 1 << ((n + h) * (width - 1)))
               for h, count in enumerate(profile))


def type_multiplicities(n, free_sites):
    """For fixed base address, count ordered lists of independent input slots.

    Each of the free_sites slots may repeat any address. The displacement
    type records the two projected dimensions and their common quotient.
    """
    if n < 1 or free_sites < 0:
        raise ValueError("Expected positive qubit dimension and nonnegative slot count")
    for a in range(n + 1):
        for b in range(n + 1):
            for c in range(min(a, b) + 1):
                d = a + b - c
                if d > free_sites:
                    continue
                spaces = (subspace_count(n, a) * subspace_count(n, b)
                          * subspace_count(a, c) * subspace_count(b, c)
                          * injections(c, c))
                yield (a, b, c), spaces * injections(d, free_sites)


def support_histogram(n, free_sites):
    """Map total occupied label count to ordered address count, base fixed."""
    result = Counter()
    for kind, count in type_multiplicities(n, free_sites):
        result[nonzero_labels(n, shell_profile(n, *kind))] += count
    return dict(sorted(result.items()))


if __name__ == "__main__":
    for support, multiplicity in support_histogram(4, 2).items():
        print(support, multiplicity)
