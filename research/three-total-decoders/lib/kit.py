"""Shared helpers of research/three-total-decoders (standard library; python-sat only where a SAT call is made).

Model (see README section 1): a configuration is a list of lines t = (p(t), q(t)) with p, q in Z^3 and p(t).q(t) != 0.
R_j = {t : p_j(t) != 0}, A_j = {t : q_j(t) != 0}.  An admissible B over F2 has unit diagonal and B_ts = 1 (t != s) only where
p(t).q(s) = 0.  Only entries that fall inside some block R_j x A_j matter for the cost, so 'free' lists exactly those incidences.
cost(B) = sum_j rank_F2 B[R_j, A_j].
"""
import json, os, subprocess, itertools
from fractions import Fraction

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(PKG, 'data')
BIN = os.environ.get('TTD_BIN') or os.path.join(PKG, 'c', 'bin')


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def load_cfg(name):
    """Return (P, Q) from data/<name>; accepts [[p,q],...] and [P,Q] (and [P,Q,B])."""
    d = json.load(open(os.path.join(DATA, name)))
    if len(d) in (2, 3) and isinstance(d[0][0], list) and isinstance(d[0][0][0], int) and len(d[0]) == len(d[1]):
        return d[0], d[1]
    return [l[0] for l in d], [l[1] for l in d]


def setup(P, Q):
    v = len(P)
    R = [[t for t in range(v) if P[t][j]] for j in range(3)]
    A = [[s for s in range(v) if Q[s][j]] for j in range(3)]
    free = [(t, s) for t in range(v) for s in range(v)
            if t != s and dot(P[t], Q[s]) == 0 and any(t in R[j] and s in A[j] for j in range(3))]
    return R, A, free


def _run(binary, text, *args):
    return subprocess.run([os.path.join(BIN, binary), *args], input=text, capture_output=True, text=True, check=True).stdout


def blocks_text(R, A):
    return "".join("%d %s\n%d %s\n" % (len(R[j]), " ".join(map(str, R[j])), len(A[j]), " ".join(map(str, A[j]))) for j in range(3))


def enum_raw(v, R, A, free, slack=0):
    """Exhaustive over all 2^f admissible B (C program enumall, f <= 30).  Returns (best, [(cost, g)]); g bit i = free[i]."""
    inp = "%d %d\n" % (v, len(free)) + "".join("%d %d\n" % e for e in free) + blocks_text(R, A)
    out = _run('enumall', inp, str(slack)).split()
    best, nm = int(out[0]), int(out[1]); xs = list(map(int, out[2:]))
    return best, [(xs[2 * i], xs[2 * i + 1]) for i in range(nm)]


def enum(P, Q, slack=0):
    """enum_raw for an integer configuration.  Returns (best, [(cost, g)], R, A, free)."""
    v = len(P); R, A, free = setup(P, Q)
    best, ms = enum_raw(v, R, A, free, slack)
    return best, ms, R, A, free


def tomat(g, free, v):
    B = [[int(t == s) for s in range(v)] for t in range(v)]
    for i, (t, s) in enumerate(free):
        if g >> i & 1:
            B[t][s] = 1
    return B


def rank2(rows):
    """F2 rank of a list of int bitmasks."""
    piv = []
    for x in rows:
        for p in piv:
            x = min(x, x ^ p)
        if x:
            piv.append(x); piv.sort(reverse=True)
    return len(piv)


def blk_rows(B, rows, cols):
    return [sum(B[t][s] << i for i, s in enumerate(cols)) for t in rows]


def blockranks(B, R, A):
    return [rank2(blk_rows(B, R[j], A[j])) for j in range(3)]


def qrank(M):
    M = [[Fraction(x) for x in r] for r in M]
    if not M or not M[0]:
        return 0
    rk = 0
    for c in range(len(M[0])):
        p = next((i for i in range(rk, len(M)) if M[i][c] != 0), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        for i in range(len(M)):
            if i != rk and M[i][c] != 0:
                f = M[i][c] / M[rk][c]; M[i] = [a - f * b for a, b in zip(M[i], M[rk])]
        rk += 1
    return rk


def tus(B, rows, cols):
    """Camion test (C program tusign): is the submatrix B[rows, cols] TU-signable?"""
    rows = list(rows); cols = list(cols)
    inp = "%d %d\n" % (len(rows), len(cols)) + "\n".join(str(x) for x in blk_rows(B, rows, cols))
    r = _run('tusign', inp).strip()
    assert r in ('0', '1'), r
    return r == '1'


def jsign_batch(Bs, R, A, want_sign=False):
    """C program jsign: per B the tuple (J, b0, b1, b2); with want_sign also the joint signing (list of +-1 per one, row-major) or None."""
    inp = []
    for B in Bs:
        v = len(B); inp.append(str(v)); inp += [str(sum(B[t][s] << s for s in range(v))) for t in range(v)]
        inp.append(blocks_text(R, A).strip())
    out = _run('jsign', "\n".join(inp) + "\n", *(['s'] if want_sign else [])).split('\n')
    res = []; i = 0; out = [l for l in out if l.strip()]
    while i < len(out):
        fl = tuple(x == '1' for x in out[i].split()); i += 1
        sgn = None
        if want_sign and fl[0]:
            bits = out[i].split()[1]; i += 1
            sgn = [-1 if b == '1' else 1 for b in bits]
        res.append((fl, sgn) if want_sign else fl)
    assert len(res) == len(Bs), (len(res), len(Bs))
    return res


def brute_batch(Bs, R, A):
    """C program brutetu: exhaustive signings + exhaustive minors; per B (J, b0, b1, b2) or None if out of range."""
    inp = []
    for B in Bs:
        v = len(B); inp.append(str(v)); inp += [str(sum(B[t][s] << s for s in range(v))) for t in range(v)]
        inp.append(blocks_text(R, A).strip())
    out = [l for l in _run('brutetu', "\n".join(inp) + "\n").split('\n') if l.strip()]
    return [None if l.strip() == '-1' else tuple(x == '1' for x in l.split()) for l in out]


def signed_matrix(B, sgn):
    v = len(B); S = [[0] * v for _ in range(v)]; k = 0
    for t in range(v):
        for s in range(v):
            if B[t][s]:
                S[t][s] = sgn[k]; k += 1
    return S


def block_q(S, R, A):
    return [qrank([[S[t][s] for s in A[j]] for t in R[j]]) for j in range(3)]


# ---- independent pure-Python Camion solver (same linear system as jsign.c, different code) -------------------------------
def camion_eqs(B, rows, cols, vid):
    eqs = []
    for k in range(1, len(rows) + 1):
        for S in itertools.combinations(rows, k):
            par = [sum(B[t][s] for t in S) % 2 for s in cols]
            Z = [s for s, p in zip(cols, par) if p == 0]
            for T in itertools.combinations(Z, k):
                if all(sum(B[t][s] for s in T) % 2 == 0 for t in S):
                    e = 0; cnt = 0
                    for t in S:
                        for s in T:
                            if B[t][s]:
                                e |= 1 << vid[(t, s)]; cnt += 1
                    if cnt:
                        eqs.append((e, (cnt // 2) & 1))
    return eqs


def solve_f2(eqs):
    piv = {}
    for e, r in eqs:
        while e:
            b = e.bit_length() - 1
            if b in piv:
                pe, pr = piv[b]; e ^= pe; r ^= pr
            else:
                piv[b] = (e, r); break
        if not e and r:
            return None
    x = 0
    for b in sorted(piv):
        e, r = piv[b]
        if r ^ (bin(e & x & ~(1 << b)).count('1') & 1):
            x |= 1 << b
    return x


def py_flags(B, R, A, which=(0, 1, 2)):
    """(J, b0, b1, b2) by the Python Camion system."""
    v = len(B); ents = [(t, s) for t in range(v) for s in range(v) if B[t][s]]; vid = {e: i for i, e in enumerate(ents)}
    eq = [camion_eqs(B, R[j], A[j], vid) for j in range(3)]
    bo = [solve_f2(eq[j]) is not None for j in range(3)]
    J = solve_f2(eq[0] + eq[1] + eq[2]) is not None
    return (J, *bo)


def pretty_flags(f):
    return "J=%d b=%d%d%d" % (f[0], f[1], f[2], f[3])
