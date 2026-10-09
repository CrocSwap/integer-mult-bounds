"""Deterministic maximal nondegenerate extensions over F2, retaining E.

The construction changes no scalar values, matching links, or role gates.
All proof-critical checks are explicit and also run under optimized Python.
"""
from collections import Counter


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() & 1


def basis(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    for p in sorted(pivots):
        for q in pivots:
            if q > p and (pivots[q] >> p) & 1:
                pivots[q] ^= pivots[p]
    return [pivots[p] for p in sorted(pivots, reverse=True)]


def contains(small, large):
    return len(basis(list(small) + list(large))) == len(basis(large))


def gram_rank(rows):
    rows = basis(rows)
    return len(basis(sum(dot(x, y) << j for j, y in enumerate(rows)) for x in rows))


def kernel(functionals, h):
    rows = basis(functionals)
    pivots = {x.bit_length() - 1 for x in rows}
    return basis((1 << c) | sum(((x >> c) & 1) << (x.bit_length() - 1) for x in rows)
                 for c in range(h) if c not in pivots)


def restrict(rows, functionals):
    rows = basis(rows)
    for f in functionals:
        indices = [i for i, x in enumerate(rows) if dot(x, f)]
        if indices:
            i = indices[0]
            pivot = rows[i]
            rows = basis(x ^ (pivot if dot(x, f) else 0)
                         for j, x in enumerate(rows) if j != i)
    return rows


def extend(E, B):
    """Return nondegenerate U with E⊆U⊆B and dim U=rank Gram(B)."""
    E, B = basis(E), basis(B)
    require(contains(E, B), 'baseline frame outside feasible intersection')
    require(gram_rank(E) == len(E), 'baseline frame degenerate')
    rest = restrict(B, E)
    chosen = list(E)
    while rest:
        i = next((i for i, x in enumerate(rest) if dot(x, x)), None)
        if i is not None:
            p = rest[i]
            chosen.append(p)
            rest = basis(x ^ (p if dot(x, p) else 0)
                         for j, x in enumerate(rest) if j != i)
            continue
        pair = next(((i, j) for i in range(len(rest)) for j in range(i + 1, len(rest))
                     if dot(rest[i], rest[j])), None)
        if pair is None:
            break  # precisely the remaining radical
        i, j = pair
        p, q = rest[i], rest[j]
        chosen.extend((p, q))
        rest = basis(x ^ (p if dot(x, q) else 0) ^ (q if dot(x, p) else 0)
                     for k, x in enumerate(rest) if k not in (i, j))
    U = basis(chosen)
    require(contains(E, U) and contains(U, B), 'extension containment')
    require(gram_rank(U) == len(U), 'extension degeneracy')
    require(len(U) == gram_rank(B), 'extension not maximal dimension')
    return U


def enlarge_frames(h, old, order_desc, args, K, successors):
    """One reverse-topological pass; leaves remain their original lines."""
    U = {x: list(rows) for x, rows in old.items()}
    inverse_cache = {}
    def perpendicular(rows):
        key = tuple(basis(rows))
        if key not in inverse_cache:
            inverse_cache[key] = kernel(key, h)
        return inverse_cache[key]
    visited = set()
    changes = Counter()
    witness = {}
    for x in order_desc:
        require(all(t in visited for t in successors[x]), 'not reverse successor order')
        visited.add(x)
        if not args[x][0]:
            continue
        # Intersect ker K with every updated successor frame by adding
        # their annihilators. Baseline E is retained, never reselected.
        constraints = list(K[x])
        for t in sorted(successors[x]):
            constraints.extend(perpendicular(U[t]))
        B = kernel(constraints, h)
        E = U[x]
        U[x] = extend(E, B)
        changes[len(E), len(U[x])] += 1
        if len(U[x]) != len(E):
            witness[x] = dict(old=basis(E), feasible=B, enlarged=U[x])
    for x in U:
        require(contains(old[x], U[x]), 'old frame lost')
        require(gram_rank(U[x]) == len(U[x]), 'nondegeneracy final')
        require(all(not dot(u, f) for u in U[x] for f in K[x]), 'root annihilator final')
        require(all(contains(U[x], U[t]) for t in successors[x]), 'nesting final')
        if not args[x][0]:
            require(basis(old[x]) == basis(U[x]), 'leaf frame changed')
    receipt = dict(policy='reverse-successor maximal nondegenerate completion retaining baseline',
                   changed_nodes=len(witness),
                   dimension_counts={f'{a}->{b}': c for (a, b), c in sorted(changes.items())},
                   changed_frames=witness)
    return U, receipt
