"""Independent reviewer circuit primitives, snapshotted from round1 checker.
No retained evaluator is imported. Exact Gaussian integers / 2^den.
"""
def need(b, s):
    if not b:
        raise ValueError(s)

def rank(xs):
    piv = {}
    for x in xs:
        while x:
            j = x.bit_length() - 1
            if j not in piv:
                piv[j] = x
                break
            x ^= piv[j]
    return len(piv)

def transpose(a):
    return [sum(((a[j] >> i & 1) << j for j in range(9))) for i in range(9)]

def mv(a, x):
    return sum(((r & x).bit_count() % 2 << i for i, r in enumerate(a)))

def inverse(a):
    w = [x | 1 << 9 + i for i, x in enumerate(a)]
    for j in range(9):
        k = next((i for i in range(j, 9) if w[i] >> j & 1))
        w[j], w[k] = (w[k], w[j])
        for i in range(9):
            if i != j and w[i] >> j & 1:
                w[i] ^= w[j]
    return [x >> 9 for x in w]

def adj(c):
    return [('P', inverse(g[1])) if g[0] == 'P' else ('D', g[1], [-x % 4 for x in g[2]]) if g[0] == 'D' else ('C', g[1], -g[2]) if g[0] == 'C' else ('phase', -g[1]) if g[0] == 'phase' else g for g in reversed(c)]

def conjugate(c):
    return [('D', g[1], [-x % 4 for x in g[2]]) if g[0] == 'D' else ('C', g[1], -g[2]) if g[0] == 'C' else ('phase', -g[1]) if g[0] == 'phase' else g for g in c]

def frame(b):
    if len(b) == 0:
        return []
    if len(b) == 9:
        return [('C', 1 << i, 1) for i in range(9)]
    ext = []
    for x in b + [1 << i for i in range(9)]:
        if rank(ext + [x]) > len(ext):
            ext.append(x)
    G = transpose(ext)
    it = transpose(inverse(G))
    qm = [1 << i ^ sum(((a & bb).bit_count() % 2 << j for j, bb in enumerate(it))) for i, a in enumerate(it)]
    K = [('P', G), ('D', qm, [qm[i] >> i & 1 for i in range(9)])]
    return adj(K) + [('C', 1 << i, 1) for i in range(len(b))] + K

def recipe(r):
    return [('D', r['quadratic_rows'], r['linear_Z4']), ('P', r['matrix_rows']), ('X', r['offset']), ('phase', r['phase'])]

def qvalue(rows, lin, x):
    return (sum((lin[i] for i in range(9) if x >> i & 1)) + 2 * sum(((rows[i] & x & ~((1 << i + 1) - 1)).bit_count() for i in range(9) if x >> i & 1))) % 4

def tableau(c):
    out = []
    for j in range(18):
        x, z, p = (1 << j, 0, 0) if j < 9 else (0, 1 << j - 9, 0)
        for g in c:
            if g[0] == 'P':
                x = mv(g[1], x)
                z = mv(transpose(inverse(g[1])), z)
            elif g[0] == 'D':
                p = (p + qvalue(g[1], g[2], x)) % 4
                z ^= mv(g[1], x)
            elif g[0] == 'C':
                if (z & g[1]).bit_count() % 2:
                    x ^= g[1]
                    p = (p + 3 * g[2]) % 4
            elif g[0] == 'X':
                p = (p + 2 * ((z & g[1]).bit_count() % 2)) % 4
            elif g[0] != 'phase':
                raise ValueError(g)
        out.append((x, z, p))
    return out

def rot(a, p):
    x, y = a
    return [(x, y), (-y, x), (-x, -y), (y, -x)][p % 4]

def state(c, basis=0):
    a = [(0, 0)] * 512
    a[basis] = (1, 0)
    den = 0
    for g in c:
        if g[0] == 'P':
            b = [(0, 0)] * 512
            for x, v in enumerate(a):
                b[mv(g[1], x)] = v
            a = b
        elif g[0] == 'X':
            a = [a[x ^ g[1]] for x in range(512)]
        elif g[0] == 'D':
            a = [rot(v, qvalue(g[1], g[2], x)) for x, v in enumerate(a)]
        elif g[0] == 'phase':
            a = [rot(v, g[1]) for v in a]
        elif g[0] == 'C':
            b = []
            s = g[2]
            for x, (u, v) in enumerate(a):
                w, t = a[x ^ g[1]]
                b.append((u - s * v + w + s * t, v + s * u + t - s * w))
            a = b
            den += 1
        else:
            raise ValueError(g)
        while den and all((not (u | v) & 1 for u, v in a)):
            a = [(u // 2, v // 2) for u, v in a]
            den -= 1
    return (a, den)
