"""Hub normal form: classes, event decomposition, conditions and the explicit dyadic gauge.

DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
Notation (PROOF.md section 1): K = registers with initial frame {0}, R = registers with final frame full,
J = K minus R, H = K and R, I = R minus K, Hnn = neither.  A = I + E with E supported on J x I.
"""
from fractions import Fraction as Q
from hubmodel import need, regs, event_frame, mul, identity, is_dyadic, is_dyadic_unit


# -------------------------------------------------------------------------------------- classes
def classes(word, F):
    pub = word['public']
    K = [r for r in range(pub) if word['initial'][r] == F.zero]
    R = [r for r in range(pub) if word['final'][r] == F.full]
    sK, sR = set(K), set(R)
    X = sorted(word['live'])
    Y = sorted(r + 112 for r in word['live'])
    main = set(X) | set(Y)
    H = [r for r in range(pub) if r not in main]
    cl = dict(K=K, R=R, X=X, Y=Y,
              H09=[h for h in H if h in sK and h in sR], H0n=[h for h in H if h in sK and h not in sR],
              Hn9=[h for h in H if h not in sK and h in sR], Hnn=[h for h in H if h not in sK and h not in sR])
    need(set(Y) <= sK - sR and set(X) <= sR - sK, 'main registers are not Y in K\\R, X in R\\K')
    return cl


# ------------------------------------------------------------------------------- decomposition
def decompose(word, F, program):
    """Label each event 'pre' (public events at the zero frame that no earlier unlabelled event touches), 'post'
    (events at the full frame on public registers or never-moving full-frame private lifetimes that no later
    unlabelled event touches) or None.  Moving a labelled event past an unlabelled one never crosses a shared
    register, so pre + mid + post has the same per-register event sequences as the word."""
    pub = word['public']
    life, cur = [], {}
    for i, e in enumerate(program):
        if e[0] == 'INIT':
            cur[e[1]] = len(life)
            life.append(dict(reg=e[1], a=i, f=e[2], mv=0, b=None))
        elif e[0] == 'CLEAR':
            life[cur[e[1]]]['b'] = i
        elif e[0] == 'MOVE' and e[1] >= pub:
            life[cur[e[1]]]['mv'] += 1
    pure = [l for l in life if l['mv'] == 0 and l['f'] == F.full]
    spans = {}
    for l in pure:
        spans.setdefault(l['reg'], []).append((l['a'], l['b']))

    def inpure(r, i):
        return any(a <= i <= b for a, b in spans.get(r, ()))

    lab = [None] * len(program)
    blocked = set()
    for i in range(len(program) - 1, -1, -1):
        e = program[i]
        rs = regs(e)
        if e[0] in ('ADD', 'COPY', 'SCALE') and e[-1] == F.full and all(r < pub or inpure(r, i) for r in rs) \
                and not (set(rs) & blocked):
            lab[i] = 'post'
            continue
        if e[0] in ('INIT', 'CLEAR') and inpure(e[1], i) and e[1] not in blocked:
            lab[i] = 'post'
            continue
        blocked |= set(rs)
    blocked = set()
    for i, e in enumerate(program):
        if lab[i]:
            continue
        rs = regs(e)
        if e[0] in ('ADD', 'COPY', 'SCALE') and e[-1] == F.zero and all(r < pub for r in rs) \
                and not (set(rs) & blocked):
            lab[i] = 'pre'
            continue
        blocked |= set(rs)
    for l in pure:                                    # every pure lifetime is entirely in the post part
        ev = [i for i in range(l['a'], l['b'] + 1) if l['reg'] in regs(program[i])]
        need(all(lab[i] == 'post' for i in ev), ('pure lifetime split between post and mid', l))
    return lab, pure


# ------------------------------------------------------------------------------------ conditions
def block(M, rows, cols):
    cs = set(cols)
    return [{c: v for c, v in M[r].items() if c in cs} for r in rows]


def conditions(T, Tinv, A, Ainv, K, R, pub):
    sK, sR = set(K), set(R)
    Kb = [r for r in range(pub) if r not in sK]
    Rb = [r for r in range(pub) if r not in sR]
    Hnn = [r for r in Kb if r in set(Rb)]
    return {
        'C1': block(T, Rb, Kb) == block(A, Rb, Kb),
        'C2': all(not v for v in block(T, R, Hnn)),
        'C2p': all(not v for v in block(T, Hnn, K)),
        'C3': block(Tinv, Kb, Rb) == block(Ainv, Kb, Rb),
    }


# ----------------------------------------------------------------------------------------- gauge
def inverse(T):
    """Exact inverse of a small sparse matrix by Gauss-Jordan over Q (used for the small instances only)."""
    n = len(T)
    L = [dict(r) for r in T]
    Rm = [{i: Q(1)} for i in range(n)]
    for c in range(n):
        p = next((i for i in range(c, n) if L[i].get(c)), None)
        need(p is not None, 'singular matrix')
        L[c], L[p] = L[p], L[c]
        Rm[c], Rm[p] = Rm[p], Rm[c]
        x = L[c][c]
        L[c] = {k: v / x for k, v in L[c].items()}
        Rm[c] = {k: v / x for k, v in Rm[c].items()}
        for i in range(n):
            if i != c and L[i].get(c):
                f = L[i][c]
                for M in (L, Rm):
                    for k, v in M[c].items():
                        y = M[i].get(k, 0) - f * v
                        if y:
                            M[i][k] = y
                        else:
                            M[i].pop(k, None)
    return Rm


def gauge(T, Tinv, A, K, R, pub):
    """The construction of PROOF.md Theorem 3.2 from T and an exact inverse alone.  Raises ValueError when a
    hypothesis fails.  Returns (G0, D, G9): G0 acts on K, G9 on R, D = G0^-1, and G9 T G0 = A."""
    sK, sR = set(K), set(R)
    J = [r for r in K if r not in sR]
    Hh = [r for r in K if r in sR]
    Ainv = [dict(r) for r in A]
    for i, row in enumerate(A):                       # A = I + E, E^2 = 0, so A^-1 = 2I - A
        Ainv[i] = {k: -v for k, v in row.items()}
        Ainv[i][i] = Ainv[i].get(i, 0) + 2
        if not Ainv[i][i]:
            del Ainv[i][i]
    need(mul(A, Ainv) == identity(pub), 'endpoint is not an involution-type matrix I+E with E^2=0')
    cond = conditions(T, Tinv, A, Ainv, K, R, pub)
    need(all(cond.values()), ('conditions fail', cond))
    need(mul(T, Tinv) == identity(pub) and mul(Tinv, T) == identity(pub), 'Tinv is not the inverse of T')
    need(all(is_dyadic(v) for row in Tinv for v in row.values()) and
         all(is_dyadic(v) for row in T for v in row.values()), 'T or its inverse is not dyadic: T not in GL(Z[1/2])')
    # N = T^-1[K, J] (T^-1[Kbar, J] = 0 by C3), D1 = T[J, K]
    N = {j: {} for j in J}
    for k in range(pub):
        for j, v in Tinv[k].items():
            if j in N:
                need(k in sK, 'T^-1[Kbar,J] is not zero')
                N[j][k] = v
    rownnz = {}
    for j in J:
        for k in N[j]:
            rownnz[k] = rownnz.get(k, 0) + 1
    cols = {j: dict(N[j]) for j in J}                 # column operations N -> N U, U in GL(Z[1/2])
    piv, used, rem = {}, set(), set(J)
    while rem:
        c = min(rem, key=lambda j: sum(1 for k in cols[j] if k not in used))
        rem.discard(c)
        cand = [k for k, v in cols[c].items() if k not in used and is_dyadic_unit(v)]
        need(cand, 'no unit pivot found (greedy rule; a unimodular completion exists by Prop. 3.1 but is not built)')
        p = min(cand, key=lambda k: rownnz.get(k, 0))
        x = cols[c][p]
        cols[c] = {k: v / x for k, v in cols[c].items()}
        for d in J:
            if d != c and p in cols[d]:
                f = cols[d][p]
                cd = cols[d]
                for k, v in cols[c].items():
                    y = cd.get(k, 0) - f * v
                    if y:
                        cd[k] = y
                    else:
                        cd.pop(k, None)
        piv[c] = p
        used.add(p)
    Pset = set(piv.values())
    C = [k for k in K if k not in Pset]
    need(len(C) == len(Hh), 'pivot count mismatch')
    Cmap = dict(zip(C, Hh))
    G0 = [{} for _ in range(pub)]
    D = [{} for _ in range(pub)]
    for r in range(pub):
        if r not in sK:
            G0[r][r] = Q(1)
            D[r][r] = Q(1)
    for j in J:
        for k, v in N[j].items():
            G0[k][j] = v
        D[j] = {k: v for k, v in T[j].items() if k in sK}
    for c, h in Cmap.items():                         # g_c = e_c - N D1 e_c ; rows of D = e_c - N'_C
        vec = {c: Q(1)}
        for j in J:
            a = T[j].get(c, 0)
            if a:
                for k, v in N[j].items():
                    y = vec.get(k, 0) - a * v
                    if y:
                        vec[k] = y
                    else:
                        vec.pop(k, None)
        for k, v in vec.items():
            G0[k][h] = v
        row = {c: Q(1)}
        for cp in J:
            v = cols[cp].get(c, 0)
            if v:
                row[piv[cp]] = row.get(piv[cp], 0) - v
        D[h] = row
    need(mul(D, G0) == identity(pub) and mul(G0, D) == identity(pub), 'D is not the inverse of G0')
    Am = mul(A, mul(D, Tinv))                         # G9 = A D T^-1
    for r in range(pub):
        if r not in sR:
            need(Am[r] == {r: Q(1)}, ('G9 does not fix a non-R register', r))
        else:
            need(all(c in sR for c in Am[r]), ('G9 leaves R', r))
    need(mul(Am, mul(T, G0)) == A, 'G9 T G0 != A')
    return G0, D, Am
