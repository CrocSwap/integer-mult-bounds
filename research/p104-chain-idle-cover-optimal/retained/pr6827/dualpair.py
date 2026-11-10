"""Exact algebra for the pure dual-pair retirement criterion (Python 3.12, standard library).

Everything here is exact (Fraction / int).  Scalars: D = Z[1/2] (the ordinary
events ADD, SCALE, SWAP with dyadic coefficients).  Ring elements are
dict {monomial: (re, im)} with Fraction parts; monomials are hashable tuples
and combine by `rmul`.
"""
from fractions import Fraction as Q

ZERO = Q(0)


def need(ok, why):
    if not ok:
        raise ValueError(why)


# ---------------------------------------------------------------- integers
def snf(A):
    """Smith form of an integer matrix: returns (S, U, V) with U*A*V = S."""
    m = len(A)
    n = len(A[0]) if m else 0
    A = [r[:] for r in A]
    U = [[int(i == j) for j in range(m)] for i in range(m)]
    V = [[int(i == j) for j in range(n)] for i in range(n)]

    def rowop(i, j, q):
        A[i] = [x - q * y for x, y in zip(A[i], A[j])]
        U[i] = [x - q * y for x, y in zip(U[i], U[j])]

    def colop(i, j, q):
        for r in A:
            r[i] -= q * r[j]
        for r in V:
            r[i] -= q * r[j]

    def rswap(i, j):
        A[i], A[j] = A[j], A[i]
        U[i], U[j] = U[j], U[i]

    def cswap(i, j):
        for r in A:
            r[i], r[j] = r[j], r[i]
        for r in V:
            r[i], r[j] = r[j], r[i]

    t = 0
    while t < min(m, n):
        best = None
        for i in range(t, m):
            for j in range(t, n):
                if A[i][j] and (best is None or abs(A[i][j]) < abs(A[best[0]][best[1]])):
                    best = (i, j)
        if best is None:
            break
        rswap(t, best[0])
        cswap(t, best[1])
        done = False
        while not done:
            done = True
            for i in range(t + 1, m):
                if A[i][t]:
                    rowop(i, t, A[i][t] // A[t][t])
                    if A[i][t]:
                        rswap(t, i)
                        done = False
            for j in range(t + 1, n):
                if A[t][j]:
                    colop(j, t, A[t][j] // A[t][t])
                    if A[t][j]:
                        cswap(t, j)
                        done = False
            if done:
                for i in range(t + 1, m):
                    for j in range(t + 1, n):
                        if A[i][j] % A[t][t]:
                            rowop(t, i, -1)
                            done = False
                            break
                    if not done:
                        break
        t += 1
    return A, U, V


def odd_part(x):
    x = abs(int(x))
    while x and x % 2 == 0:
        x //= 2
    return x


def invariants_over_D(M):
    """Elementary divisors of an integer matrix over Z[1/2]: odd parts of the Z invariants.
    A divisor equal to 1 is a unit of D."""
    if not M or not M[0]:
        return []
    S, U, V = snf(M)
    return [odd_part(S[i][i]) for i in range(min(len(S), len(S[0]))) if S[i][i]]


def clear(vec):
    """Scale a Fraction vector by a power of two (a unit of D) and an integer to make it integral."""
    from math import lcm
    den = 1
    for x in vec:
        den = lcm(den, Q(x).denominator)
    return [int(Q(x) * den) for x in vec], den


# ------------------------------------------------- sparse exact linear algebra
def rref(forms):
    """forms: list of dict var->Fraction.  Returns (pivots dict var->row dict) in reduced form."""
    piv = {}
    for f in forms:
        r = {k: Q(v) for k, v in f.items() if v}
        for p, pr in piv.items():
            if p in r:
                c = r[p]
                for k, v in pr.items():
                    nv = r.get(k, ZERO) - c * v
                    if nv:
                        r[k] = nv
                    else:
                        r.pop(k, None)
        if not r:
            continue
        p = min(r)
        c = r[p]
        r = {k: v / c for k, v in r.items()}
        for q, qr in piv.items():
            if p in qr:
                cc = qr[p]
                for k, v in r.items():
                    nv = qr.get(k, ZERO) - cc * v
                    if nv:
                        qr[k] = nv
                    else:
                        qr.pop(k, None)
        piv[p] = r
    return piv


def int_kernel(forms, variables):
    """Z-saturated basis of {x in Z^variables : forms(x)=0}; each basis vector is a dict var->int.
    Saturation over Z is saturation over Z[1/2] up to units (powers of two)."""
    piv = rref(forms)
    free = [v for v in variables if v not in piv]
    if not free:
        return []
    pcs = sorted(piv)
    # x_p = sum_f T[p][f] x_f with T = -R[p][f]
    T = {p: {f: -piv[p][f] for f in free if f in piv[p]} for p in pcs}
    bad = [p for p in pcs if any(x.denominator != 1 for x in T[p].values())]
    fidx = {f: i for i, f in enumerate(free)}
    if not bad:
        ybasis = [[int(i == j) for j in range(len(free))] for i in range(len(free))]
    else:
        from math import lcm
        nf, nb = len(free), len(bad)
        rows = []
        for bi, p in enumerate(bad):
            N = 1
            for x in T[p].values():
                N = lcm(N, x.denominator)
            row = [0] * (nf + nb)
            for f, x in T[p].items():
                row[fidx[f]] = int(x * N)
            row[nf + bi] = -N
            rows.append(row)
        S, U, V = snf(rows)
        rk = sum(1 for i in range(min(len(S), nf + nb)) if S[i][i])
        ybasis = [[V[i][j] for i in range(nf)] for j in range(rk, nf + nb)]
        ybasis = [y for y in ybasis if any(y)]
    out = []
    for y in ybasis:
        x = {f: int(y[fidx[f]]) for f in free if y[fidx[f]]}
        for p in pcs:
            val = sum(T[p].get(f, ZERO) * y[fidx[f]] for f in free)
            need(val.denominator == 1 if isinstance(val, Q) else True, "kernel lattice point not integral")
            if val:
                x[p] = int(val)
        out.append(x)
    return out


# ------------------------------------------------------------------- ring elements
def cadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def cmulz(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def accumulate(dst, src, c=(Q(1), ZERO), shift=None):
    for key, v in src.items():
        if shift is not None:
            key = shift(key)
        nv = cadd(dst.get(key, (ZERO, ZERO)), cmulz(c, v))
        if nv != (0, 0):
            dst[key] = nv
        else:
            dst.pop(key, None)


def rmul(a, b, mulkey):
    out = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            k = mulkey(ka, kb)
            nv = cadd(out.get(k, (ZERO, ZERO)), cmulz(va, vb))
            if nv != (0, 0):
                out[k] = nv
            else:
                out.pop(k, None)
    return out


def flat(elem):
    """Real coordinates of a ring element: {(mono, 0|1): Fraction}."""
    out = {}
    for m, (re, im) in elem.items():
        if re:
            out[(m, 0)] = re
        if im:
            out[(m, 1)] = im
    return out


# ------------------------------------------------------- the pairing lattices
def proportional_forms(forms, svec):
    """Linear forms (dict var->Fraction) per real coordinate; require the coordinate vector in D*svec.
    forms: {coord: dict}; svec: {coord: Fraction}.  Returns the list of homogeneous equations."""
    eq = []
    coords = set(forms) | set(svec)
    k0 = min(svec)
    for k in coords:
        f = forms.get(k, {})
        if k not in svec:
            eq.append(f)
        elif k != k0:
            g = forms.get(k0, {})
            h = {}
            for v, x in f.items():
                h[v] = h.get(v, ZERO) + x * svec[k0]
            for v, x in g.items():
                h[v] = h.get(v, ZERO) - x * svec[k]
            eq.append(h)
    return eq


def pair_lattices(P, regs, G, RF, s):
    """P: callable i -> {j: ring element} (row i of the prefix map; sparse).
    regs: iterable of register indices (rows).  G: inputs (columns) of the class.  RF: registers
    one ordinary event can combine at the cut.  s: ring element (the job).
    Returns (Vbasis, Abasis, Gram, info):
      Vbasis: list of columns c (dict j->int) with P c in s*D^RF (zero outside RF);
      Abasis: list of rows a (dict i->int, support in RF) with a P in s*D^G (zero outside G);
      Gram[k][l] = d_k . c_l where d_k = (a_k P)/s as a row on G.
    """
    svec = flat(s)
    need(svec, "s must be nonzero")
    k0 = min(svec)
    G = list(G)
    Gs = set(G)
    RFs = set(RF)
    # ---- columns c
    eqs = []
    for i in regs:
        row = P(i)
        forms = {}
        for j in G:
            if j in row:
                for kappa, x in flat(row[j]).items():
                    forms.setdefault(kappa, {})[j] = x
        if i in RFs:
            eqs += proportional_forms(forms, svec)
        else:
            eqs += list(forms.values())
    V = int_kernel(eqs, G)
    if not V:
        return V, [], [], []
    # ---- rows a
    eqs = []
    zforms = {}
    for i in RFs:
        row = P(i)
        for j, el in row.items():
            for kappa, x in flat(el).items():
                zforms.setdefault(j, {}).setdefault(kappa, {})[i] = x
    for j, forms in zforms.items():
        if j in Gs:
            eqs += proportional_forms(forms, svec)
        else:
            eqs += list(forms.values())
    for j in G:  # a column of G untouched by RF gives z_j = 0 which is allowed (in D*s)
        pass
    A = int_kernel(eqs, sorted(RFs))
    # d_k on G: coordinate k0 of (a P)_j divided by svec[k0]
    ds = []
    for a in A:
        d = {}
        for j in G:
            tot = ZERO
            for i, ai in a.items():
                el = P(i).get(j)
                if el:
                    tot += ai * flat(el).get(k0, ZERO)
            if tot:
                d[j] = tot / svec[k0]
        ds.append(d)
    Gram = [[sum(d.get(j, ZERO) * c.get(j, 0) for j in set(d) & set(c)) for c in V] for d in ds]
    return V, A, ds, Gram


def gram_report(Gram):
    """Elementary divisors over D and their unit count."""
    if not Gram or not Gram[0]:
        return dict(rows=len(Gram), cols=len(Gram[0]) if Gram else 0, rank=0, units=0, divisors=[])
    flatv = [x for r in Gram for x in r]
    from math import lcm
    den = 1
    for x in flatv:
        den = lcm(den, Q(x).denominator)
    M = [[int(Q(x) * den) for x in r] for r in Gram]
    inv = invariants_over_D(M)
    return dict(rows=len(Gram), cols=len(Gram[0]), rank=len(inv), units=sum(1 for x in inv if x == 1), divisors=inv)


# -------------------------------------------------------- unimodular completion
def inv_event(e):
    if e[0] == 'ADD':
        return ('ADD', e[1], e[2], -e[3])
    if e[0] == 'SCALE':
        return ('SCALE', e[1], 1 / e[2])
    return e


def apply_events_vec(events, vec):
    v = dict(vec)
    for e in events:
        if e[0] == 'ADD':
            nv = v.get(e[1], ZERO) + e[3] * v.get(e[2], ZERO)
        elif e[0] == 'SCALE':
            nv = v.get(e[1], ZERO) * e[2]
        else:
            a, b = v.get(e[1], ZERO), v.get(e[2], ZERO)
            v[e[1]], v[e[2]] = b, a
            continue
        v[e[1]] = nv
    return {k: x for k, x in v.items() if x}


def unit_reduce(vec, p):
    """Events (ADD/SCALE by units/SWAP) taking the unimodular vector over Z[1/2] to e_p.
    Euclid on the odd parts: no primitive-vector gap over this PID."""
    v = {k: Q(x) for k, x in vec.items() if x}
    ev = []
    for i in sorted(v):
        x = v[i]
        num, den = x.numerator, x.denominator
        k = 0
        while num % 2 == 0:
            num //= 2
            k += 1
        # x = 2^(k - log2 den) * num; scale by unit to make it the odd integer num
        f = Q(num, 1) / x
        if f != 1:
            ev.append(('SCALE', i, f))
            v[i] = Q(num)
    need(all(x.denominator == 1 for x in v.values()), "odd scaling failed")
    while sum(1 for x in v.values() if x) > 1:
        nz = [i for i in v if v[i]]
        m = min(nz, key=lambda i: abs(v[i]))
        for j in nz:
            if j != m:
                q = v[j] // v[m]
                if q:
                    ev.append(('ADD', j, m, -q))
                    v[j] -= q * v[m]
    (t, x), = [(i, x) for i, x in v.items() if x]
    need(abs(x) == 1, "vector is not unimodular over Z[1/2]")
    if t != p:
        ev.append(('SWAP', t, p))
        v[p], v[t] = v.get(t, ZERO), v.get(p, ZERO)
    if v[p] != 1:
        ev.append(('SCALE', p, Q(int(v[p]))))
    return ev


def completion(c, d, p):
    """Given column c, row d (dict index->Fraction, dyadic) with d.c = 1 and an index p, return
    (E_events, Einv_events): events applied to the state, in order, realising E and E^{-1} with
    E e_p = c and e_p^T E^{-1} = d.  Support stays inside supp(c) | supp(d) | {p}."""
    need(sum(d.get(i, ZERO) * c.get(i, ZERO) for i in set(d) & set(c)) == 1, "dual pair needs d.c = 1")
    M1 = unit_reduce(c, p)
    # d'' = d E1, E1 = M1^{-1}: advance a row vector through the inverted events in forward order
    row = {k: Q(x) for k, x in d.items() if x}
    for e in M1:
        ie = inv_event(e)
        if ie[0] == 'ADD':        # row (I + c e_dst e_src^T): row_src += c row_dst
            row[ie[2]] = row.get(ie[2], ZERO) + ie[3] * row.get(ie[1], ZERO)
        elif ie[0] == 'SCALE':
            row[ie[1]] = row.get(ie[1], ZERO) * ie[2]
        else:
            row[ie[1]], row[ie[2]] = row.get(ie[2], ZERO), row.get(ie[1], ZERO)
    row = {k: x for k, x in row.items() if x}
    need(row.get(p) == 1, "row pivot normalisation")
    Tev = [('ADD', p, j, -x) for j, x in sorted(row.items()) if j != p]
    E_events = Tev + [inv_event(e) for e in reversed(M1)]
    Einv = list(M1) + [inv_event(e) for e in Tev]
    return E_events, Einv


def smith_pair(Gram, ds, V, A):
    """From lattice bases and Gram matrix, produce (c, d, a) with d.c a unit of D (normalised to 1)
    and a the row of A matching d, or None."""
    if not Gram or not Gram[0]:
        return None
    from math import lcm
    den = 1
    for r in Gram:
        for x in r:
            den = lcm(den, Q(x).denominator)
    M = [[int(Q(x) * den) for x in r] for r in Gram]
    S, U, Vm = snf(M)
    if not S[0][0] or odd_part(S[0][0]) != 1:
        return None
    d = {}
    a = {}
    for k, coef in enumerate(U[0]):
        if coef:
            for j, x in ds[k].items():
                d[j] = d.get(j, ZERO) + coef * x
            for i, x in A[k].items():
                a[i] = a.get(i, ZERO) + coef * x
    c = {}
    for l in range(len(V)):
        coef = Vm[l][0]
        if coef:
            for j, x in V[l].items():
                c[j] = c.get(j, ZERO) + coef * x
    val = sum(d.get(j, ZERO) * c.get(j, ZERO) for j in set(d) & set(c))
    need(val != 0 and odd_part(val.numerator) == 1 and odd_part(val.denominator) == 1, "Smith pair not a unit")
    c = {j: Q(x) / val for j, x in c.items() if x}
    return c, {j: Q(x) for j, x in d.items() if x}, {i: Q(x) for i, x in a.items() if x}
