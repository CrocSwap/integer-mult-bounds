"""A paid clean root checkpoint over unchanged balanced dirty subtrees.

Research adapter, not a supplier or tape compiler. Apache-2.0.
Prepared for FanPUYen with substantial OpenAI Codex assistance.
"""


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dirty_count(n):
    need(type(n) is int and n >= 1, 'positive integer factor count')
    q = 1 << (n.bit_length() - 1)
    return 3 * q * n - 2 * q * q


def optimal_interval(n):
    """All optimal root splits, with balanced dirty subtrees on each side."""
    need(type(n) is int and n >= 2, 'at least two factors')
    if n == 2:
        return 1, 1
    q = 1 << ((n // 3).bit_length() - 1)
    return max(q, n - 4 * q), min(2 * q, n - 2 * q)


def plan(n, split=None):
    lo, hi = optimal_interval(n)
    k = hi if split is None else split
    need(type(k) is int and 0 < k < n, 'interior split')
    return dict(factors=n, split=k, optimal_splits=[lo, hi],
                leaf_calls=2 * dirty_count(k) + dirty_count(n - k),
                balanced_dirty_leaf_calls=dirty_count(n),
                clean_arrays=1,
                dirty_arrays=(max(k, n - k) - 1).bit_length(),
                balanced_dirty_arrays=(n - 1).bit_length())


def compose_clean(compose, c, x, y, factors, clean, scratch, phases,
                  beta, bits, d, split=None, sign=1, stats=None):
    """Apply a three-call root with the supplied target-additive dispatcher.

    Preconditions inherited from that dispatcher include immutable parameters,
    exact inverse signs, source/scratch restoration and zero-preserving leaves.
    Initial clean storage is an additional caller obligation, never an erasure
    of borrowed data. The adapter checks all root array exclusions before work.
    """
    p = plan(len(factors), split)
    need(sign in (-1, 1) and d in (-1, 1), 'orientation and sign')
    arrays = [x, y, clean] + list(scratch)
    need(len({id(a) for a in arrays}) == len(arrays), 'distinct root arrays')
    # Credit PR673's concurrent admission finding: phases cannot alias an
    # array mutated by the leaf, even if its initial entries are unit phases.
    need(all(phases is not a for a in arrays), 'phase array must be distinct')
    need(len(x) > 0 and all(len(a) == len(x) for a in arrays), 'array lengths')
    need(len(phases) == len(x) and all(c.norm2(t) == 1 for t in phases),
         'unit phase array')
    need(len(scratch) >= p['dirty_arrays'], 'dirty depth')
    need(all(v == c.ZERO for v in clean), 'checkpoint must initially be zero')
    k = p['split']
    operations = [(x, clean, factors[:k], 1),
                  (clean, y, factors[k:], 1),
                  (x, clean, factors[:k], -1)]
    if sign == -1:
        operations = [(a, b, fs, -s) for a, b, fs, s in reversed(operations)]
    for a, b, fs, s in operations:
        compose(a, b, fs, scratch, phases, beta, bits, d, s, stats)
