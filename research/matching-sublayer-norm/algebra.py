"""Independent small exact matrix/cut oracle; retained C is a scalar only."""
from fractions import Fraction as Q


def need(ok, why):
    if not ok:
        raise ValueError(why)


def eye(n, C):
    return [[C(int(i == j)) for j in range(n)] for i in range(n)]


def mul(a, b):
    return [[sum((x * b[k][j] for k, x in enumerate(row)), row[0] * 0)
             for j in range(len(b[0]))] for row in a]


def inv(a, C):
    n = len(a)
    rows = [list(x) + y for x, y in zip(a, eye(n, C))]
    for j in range(n):
        k = next((i for i in range(j, n) if rows[i][j] != 0), None)
        need(k is not None, 'invertible oracle matrix')
        rows[j], rows[k] = rows[k], rows[j]
        q = rows[j][j]
        rows[j] = [x / q for x in rows[j]]
        for i in range(n):
            if i != j:
                q = rows[i][j]
                rows[i] = [x - q * y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def embed(ids, gate, n, C):
    need(len(ids) == len(gate) and len(set(ids)) == len(ids), 'gate shape')
    out = eye(n, C)
    for i, a in enumerate(ids):
        for j, b in enumerate(ids):
            out[a][b] = gate[i][j]
    return out


def op(layer, n, C):
    used = set()
    out = eye(n, C)
    for ids, gate in layer:
        need(not used.intersection(ids), 'matching disjoint supports')
        used.update(ids)
        out = mul(embed(ids, gate, n, C), out)
    return out


def psd(a):
    n = len(a)
    need(all(a[i][j] == a[j][i].conjugate() for i in range(n) for j in range(n)),
         'Hermitian PSD input')
    rows = [list(row) for row in a]
    for k in range(n):
        pivot = rows[k][k]
        if pivot.im or pivot.re < 0:
            return False
        if pivot == 0:
            if any(rows[k][j] != 0 for j in range(k + 1, n)):
                return False
        else:
            for i in range(k + 1, n):
                for j in range(k + 1, n):
                    rows[i][j] -= rows[i][k] * rows[k][j] / pivot
    return True


def gram(a):
    return mul([[x.conjugate() for x in col] for col in zip(*a)], a)


def norm_cert(a, bound2, C):
    g = gram(a)
    return psd([[C(bound2 * int(i == j)) - x for j, x in enumerate(row)]
                for i, row in enumerate(g)])


def frob2(a):
    return sum((x.norm2() for row in a for x in row), Q(0))


def certified2(a, C):
    bound = frob2(a)
    while bound and norm_cert(a, bound / 2, C):
        bound /= 2
    return bound


def mix_rows(a, b, selected):
    return [list((a if i in selected else b)[i]) for i in range(len(a))]


def mix_cols(a, b, selected):
    return [[(a if j in selected else b)[i][j] for j in range(len(a))]
            for i in range(len(a))]


def cuts(plan, n, C):
    prefixes = [eye(n, C)]
    for layer in plan:
        prefixes.append(mul(op(layer, n, C), prefixes[-1]))
    suffixes = [None] * (len(plan) + 1)
    suffixes[-1] = eye(n, C)
    for k in reversed(range(len(plan))):
        suffixes[k] = mul(suffixes[k + 1], op(plan[k], n, C))
    count = proper = projections = 0
    for k, layer in enumerate(plan):
        p0, p1 = prefixes[k:k + 2]
        s0, s1 = suffixes[k:k + 2]
        pi0, pi1, si0, si1 = (inv(x, C) for x in (p0, p1, s0, s1))
        adjacent = [(left, right) for left, right in
                    zip((p0, pi0, s0, si0), (p1, pi1, s1, si1))]
        budgets = [certified2(left, C) + certified2(right, C) for left, right in adjacent]
        for mask in range(1 << len(layer)):
            chosen = [g for j, g in enumerate(layer) if mask >> j & 1]
            rest = [g for j, g in enumerate(layer) if not (mask >> j & 1)]
            selected = {i for ids, _ in chosen for i in ids}
            p = mul(op(chosen, n, C), p0)
            s = mul(s1, op(rest, n, C))
            matrices = (p, inv(p, C), s, inv(s, C))
            mixed = (mix_rows(p1, p0, selected), mix_cols(pi1, pi0, selected),
                     mix_cols(s1, s0, selected), mix_rows(si1, si0, selected))
            need(matrices == mixed, 'four adjacent-cut interpolation identities')
            for actual, budget in zip(matrices, budgets):
                need(norm_cert(actual, budget, C), 'certified adjacent-bound interpolation')
            count += 1
            proper += int(0 < mask < (1 << len(layer)) - 1)
            projections += len(selected)
    return dict(cuts=count, proper_cuts=proper, coordinate_projection_entries=projections,
                identities=4 * count, spectral_certificates=4 * count)
