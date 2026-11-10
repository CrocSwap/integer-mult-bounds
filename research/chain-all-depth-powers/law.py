"""All-depth balanced chain power law. SHIN09-git with OpenAI Codex. Apache-2.0."""
from math import gcd, isqrt


def first_missing_prime(repeats, block_size):
    """Least prime dividing repeats but not block_size. None means infinity."""
    if repeats < 1 or block_size < 1:
        raise ValueError("positive repeat count and block size required")
    remaining = repeats
    while (shared := gcd(remaining, block_size)) != 1:
        remaining //= shared
    if remaining == 1:
        return None
    for candidate in range(2, isqrt(remaining) + 1):
        if remaining % candidate == 0:
            return candidate
    return remaining


def shift(depth, block_size, repeats):
    """None means a proper interval obstructs every target."""
    if depth < 2:
        raise ValueError("depth must be at least two")
    prime = first_missing_prime(repeats, block_size)
    if prime is not None and prime < depth:
        return None
    if prime == depth:
        modulus = repeats * block_size
        return (repeats // depth) * pow(block_size, depth, modulus) % modulus
    return 0


def lifted_target(depth, block_size, repeats, base_target):
    offset = shift(depth, block_size, repeats)
    if base_target is None or offset is None:
        return None
    return (repeats * base_target + offset) % (block_size * repeats)


def root_target(depth, block_size, repeats, target):
    """Return the unique required residue for the shorter block, if allowed."""
    offset = shift(depth, block_size, repeats)
    if offset is None or (target - offset) % repeats:
        return None
    return ((target - offset) // repeats) % block_size


def unit_repeat_root(depth, modulus, target):
    """The only possible nonprimitive unit case, still subject to W(root)>0."""
    if depth < 2 or modulus < 2 or gcd(target, modulus) != 1:
        raise ValueError("unit target required")
    if first_missing_prime(depth, 1) != depth or modulus % depth:
        return None
    block_size = modulus // depth
    residue = pow(block_size, depth, modulus)
    if block_size % depth == 0 or (target - residue) % depth:
        return None
    return (block_size, ((target - residue) // depth) % block_size)


def order_bound(depth, modulus, target):
    """Orders that pass the arithmetic gates are exactly the divisors of D."""
    if depth < 2 or modulus < 1:
        raise ValueError("invalid depth or modulus")
    rest, radical, edge_power = modulus, 1, 1
    for prime in range(2, min(depth, modulus) + 1):
        if rest % prime:
            continue
        # Every smaller prime has already been removed in full.
        radical *= prime
        power = 1
        while rest % prime == 0:
            rest //= prime
            power *= prime
        if prime == depth:
            edge_power = power
    bound = gcd(target, modulus // radical)
    if edge_power > 1 and (target - modulus // depth) % edge_power == 0:
        bound *= depth
    return bound
