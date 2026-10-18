"""Exact, injective row packing for the historical dyadic central factor.

Adapted validation/receipt from Douglas R. Colkitt's complex_centers.py.
Apache-2.0. See README.md for the radix argument and NOTICE.md for credit.
"""
from itertools import combinations


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _radix_bits(scatter):
    # Every gather coordinate is -1, 0 or 1 and appears at most once.
    # Thus |actual - expected| <= ||scatter_row||_1 + 2 < 2**bits.
    bound = max((sum(abs(x) for x in u) for u in scatter), default=0) + 2
    return bound.bit_length()


def verify_factor(f):
    """Return the original receipt, checking all entries by exact row packing.

    The supplied factors, not the generator's closed formula, determine the
    actual product. Python integers are unbounded; no modular fingerprint,
    floating-point tolerance, sample, or cached acceptance is used.
    """
    h = f['h']
    triples = list(combinations(range(h), 3))
    n = len(triples)
    require(f['triples'] == triples and len(f['gather']) == len(f['scatter']) == n,
            'Wrong triple or factor dimensions')
    require(all(len(u) == h and all(type(x) is int for x in u) for u in f['scatter']),
            'Scatter must be integral')
    for v in f['gather']:
        require(len({i for i, x in v}) == len(v) and
                all(type(i) is int and type(x) is int and 0 <= i < h and x in (-1, 1)
                    for i, x in v), 'Invalid sparse gather')

    bits = _radix_bits(f['scatter'])
    gather_columns = [0] * h
    incidence_columns = [0] * h
    ones = 0
    for j, (T, v) in enumerate(zip(triples, f['gather'])):
        place = 1 << (bits * j)
        ones += place
        for i, x in v:
            gather_columns[i] += x * place
        for i in T:
            incidence_columns[i] += place
    for S, u in zip(triples, f['scatter']):
        actual = sum(x * column for x, column in zip(u, gather_columns))
        expected = sum(incidence_columns[i] for i in S) - ones
        require(actual == expected, 'Central factor coefficient mismatch')

    require(all(x in (-1, 0, 1, 2) for u in f['scatter'] for x in u),
            'Scalar charge requires these dyadic weights')
    G = sum(len(v) for v in f['gather'])
    R = sum(1 if abs(x) == 2 else 2 for u in f['scatter'] for x in u if x)
    return dict(h=h, triples=n, central_roles=h, coefficients_checked=n*n,
                integer_product_verified=True, gather_steps=G, scatter_steps=R,
                all_scalar_weights_dyadic=True)
