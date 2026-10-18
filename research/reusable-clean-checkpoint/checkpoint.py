"""One reusable clean connector, ordered binary echo trees. Apache-2.0."""
from functools import lru_cache


def require(ok, message):
    if not ok:
        raise ValueError(message)


def optimize(prices, cap, clean=True):
    prices = tuple(prices)
    require(prices and all(type(p) is int and p > 0 for p in prices), 'positive integer prices')
    require(type(cap) is int and cap >= 0 and type(clean) is bool, 'scratch contract')
    require(not clean or cap >= 1, 'one clean array must be supplied')

    @lru_cache(None)
    def solve(lo, hi, space, available):
        if hi - lo == 1:
            return prices[lo], ('leaf', lo)
        if space == 0 or hi - lo > 2**space:
            return None
        best = None
        for mid in range(lo + 1, hi):
            for kind in ('dirty', 'clean'):
                if kind == 'clean' and not available:
                    continue
                # Reserving a dirty connector requires a dirty array. If the
                # pool contains the one clean array, space must exceed one.
                if kind == 'dirty' and available and space == 1:
                    continue
                child_clean = available and kind == 'dirty'
                a = solve(lo, mid, space - 1, child_clean)
                b = solve(mid, hi, space - 1, child_clean)
                if a is None or b is None:
                    continue
                cost = 2*a[0] + (1 if kind == 'clean' else 2)*b[0]
                candidate = (cost, (kind, a[1], b[1]))
                if best is None or candidate < best:
                    best = candidate
        return best
    answer = solve(0, len(prices), cap, clean)
    require(answer is not None, 'insufficient scratch')
    return answer


def emit(tree, source=0, target=1, dirty=(), clean=None, sign=1):
    """Signed leaf word. Inverses reverse the complete emitted word."""
    require(sign in (-1, 1), 'sign')
    def forward(t, src, dst, pool, zero):
        kind = t[0]
        if kind == 'leaf':
            return [(t[1], src, dst, 1)]
        if kind == 'clean':
            require(zero is not None, 'missing clean connector')
            connector, rest, child_zero = zero, pool, None
        elif kind == 'dirty':
            require(bool(pool), 'missing dirty connector')
            connector, rest, child_zero = pool[0], pool[1:], zero
        else:
            raise ValueError('unknown node')
        left = forward(t[1], src, connector, rest, child_zero)
        right = forward(t[2], connector, dst, rest, child_zero)
        inv_left = [(i, s, d, -v) for i, s, d, v in reversed(left)]
        inv_right = [(i, s, d, -v) for i, s, d, v in reversed(right)]
        # Both children restore their own scratch, so the same pool is reused.
        return left + right + inv_left + ([] if kind == 'clean' else inv_right)
    roles = [source, target] + list(dirty) + ([] if clean is None else [clean])
    require(len(set(roles)) == len(roles), 'role aliases')
    word = forward(tree, source, target, tuple(dirty), clean)
    return word if sign == 1 else [(i, s, d, -v) for i, s, d, v in reversed(word)]


def execute(word, arrays, factors, clean=None, leaf=None):
    """Reference indexed-RAM interpreter, with admission before mutation."""
    require(len({id(a) for a in arrays}) == len(arrays), 'array aliases')
    require(arrays and len(arrays[0]) > 0 and all(len(a) == len(arrays[0]) for a in arrays), 'lengths')
    if clean is not None:
        require(0 <= clean < len(arrays) and all(v == 0 for v in arrays[clean]), 'clean array must be zero')
    for i, s, d, sign in word:
        require(0 <= i < len(factors) and 0 <= s < len(arrays) and 0 <= d < len(arrays) and s != d and sign in (-1, 1), 'instruction')
    for i, s, d, sign in word:
        value = (leaf(i, arrays[s]) if leaf else
                 [sum(a*b for a, b in zip(row, arrays[s])) for row in factors[i]])
        require(len(value) == len(arrays[d]), 'leaf output')
        arrays[d][:] = [a + sign*b for a, b in zip(arrays[d], value)]
