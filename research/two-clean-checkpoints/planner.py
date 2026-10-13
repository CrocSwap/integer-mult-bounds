"""Exact ordered binary checkpoint planning; Python standard library only."""
from functools import lru_cache


def natural(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer')


def solve(prices, scratch, clean):
    """Return (minimum complete signed-leaf price, literal tree), or None.

    Nodes are ('C' or 'D', left, right); leaves are ordered factor indices.
    Ties minimize completed leaf calls, then follow split/connector order.
    """
    prices = tuple(prices)
    if not prices or any(type(p) is not int or p <= 0 for p in prices):
        raise ValueError('prices must be nonempty positive integers')
    natural(scratch, 'scratch')
    natural(clean, 'clean')
    if clean > scratch:
        raise ValueError('clean cannot exceed scratch')
    dirty = min(scratch - clean, len(prices) - 1)
    clean = min(clean, len(prices) - 1)

    @lru_cache(None)
    def visit(lo, hi, d, c):
        n = hi - lo
        if n == 1:
            return prices[lo], 1, lo
        if n > 1 << (d + c):
            return None
        best = None
        for cut in range(lo + 1, hi):
            for kind, dd, cc, right_mult in (
                ('D', d - 1, c, 2), ('C', d, c - 1, 1)):
                if dd < 0 or cc < 0:
                    continue
                left = visit(lo, cut, dd, cc)
                right = visit(cut, hi, dd, cc)
                if left is None or right is None:
                    continue
                candidate = (2 * left[0] + right_mult * right[0],
                             2 * left[1] + right_mult * right[1],
                             (kind, left[2], right[2]))
                if best is None or candidate[:2] < best[:2]:
                    best = candidate
        return best

    result = visit(0, len(prices), dirty, clean)
    return None if result is None else (result[0], result[2])


def profile(tree):
    """Count complete leaf/internal invocations and simultaneous connectors."""
    if type(tree) is int and tree >= 0:
        return {'leaves': {tree: 1}, 'C': 0, 'D': 0, 'clean': 0, 'dirty': 0}
    if not isinstance(tree, (tuple, list)) or len(tree) != 3 or tree[0] not in ('C', 'D'):
        raise ValueError('invalid tree')
    kind, left, right = tree
    a, b = profile(left), profile(right)
    if set(a['leaves']) & set(b['leaves']):
        raise ValueError('duplicate factor')
    if max(a['leaves']) >= min(b['leaves']):
        raise ValueError('factors must remain ordered')
    m = 1 if kind == 'C' else 2
    leaves = {i: 2 * v for i, v in a['leaves'].items()}
    leaves.update({i: m * v for i, v in b['leaves'].items()})
    return {'leaves': leaves,
            'C': 2 * a['C'] + m * b['C'] + int(kind == 'C'),
            'D': 2 * a['D'] + m * b['D'] + int(kind == 'D'),
            'clean': max(a['clean'], b['clean']) + int(kind == 'C'),
            'dirty': max(a['dirty'], b['dirty']) + int(kind == 'D')}


def emit(tree, source, target, dirty, clean, sign=1):
    """Validate roles and return a streaming literal instruction iterator.

    Caller must supply zero clean arrays and deterministic zero-preserving,
    target-independent leaf increments. Negative leaves must be exact inverses.
    """
    # JSON trees use lists: snapshot them before validating a lazy program.
    def freeze(node):
        if type(node) is int and node >= 0:
            return node
        if not isinstance(node, (tuple, list)) or len(node) != 3 or node[0] not in ('C', 'D'):
            raise ValueError('invalid tree')
        return node[0], freeze(node[1]), freeze(node[2])

    tree = freeze(tree)
    dirty, clean = tuple(dirty), tuple(clean)
    roles = (source, target) + dirty + clean
    if any(type(x) is not int or x < 0 for x in roles) or len(set(roles)) != len(roles):
        raise ValueError('array roles must be distinct nonnegative integers')
    if type(sign) is not int or sign not in (-1, 1):
        raise ValueError('sign must be +1 or -1')
    p = profile(tree)
    if p['dirty'] > len(dirty) or p['clean'] > len(clean):
        raise ValueError('insufficient scratch by type')

    def walk(node, src, dst, ds, cs, direction):
        if type(node) is int:
            yield node, src, dst, direction
            return
        kind, left, right = node
        z = cs[0] if kind == 'C' else ds[0]
        dd, cc = (ds, cs[1:]) if kind == 'C' else (ds[1:], cs)
        ops = [(left, src, z, 1), (right, z, dst, 1), (left, src, z, -1)]
        if kind == 'D':
            ops.append((right, z, dst, -1))
        if direction == -1:
            ops = [(child, x, y, -s) for child, x, y, s in reversed(ops)]
        for child, x, y, s in ops:
            yield from walk(child, x, y, dd, cc, s)

    return walk(tree, source, target, dirty, clean, sign)
