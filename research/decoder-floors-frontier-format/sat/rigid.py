"""CNF generator for Theorem R (rigidity of the minimal-rank label table).  Standard library only.
Unit U (v lines), h = label dimension.  General model: B = U V^T, U, V in F2^{v x h}; symmetric model (the physical one, B = P P^T): V = U.
Fitting: B_tt = 1, B_ts = 0 for every non-orthogonal pair t != s; entries on orthogonal pairs are free.  Dense B: 1 on every orthogonal pair.
mode 'alt': add the clause "some orthogonal ordered pair (unordered if symmetric) has B_ts = 0".  UNSAT  <=>  every fitting B of F2-rank <= h is dense.
mode 'ctl': no extra clause (must be SAT, and every model must decode to a fitting matrix; for h = rank of the dense B the model is the dense B).
Gauge: S = a pairwise non-orthogonal clique (|S| = 8 for E8/P112/P104, 7 for E7, 5 for E6, pinned in data/gauge.json): B[S,S] = I, so U[S] has rank |S|,
GL(h) is transitive on such tuples, hence U[S] = (e_1..e_|S|) WLOG (symmetric model: P[S] orthonormal, the isometry argument of STRAYS Thm R requires
|S| >= h - 1).  This is the encoding of the author's working card STRAYS/rigid2.py; the clique choice here is deterministic and pinned."""
import sys, os, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from units import *

def gauge_clique(name, L_idx, kc):
    """lexicographically least (by bitmask) maximum clique of the non-orthogonality graph on the unit, truncated to kc lines (deterministic)"""
    from satgen import clique_in, nonorth_graph
    L = sub(L_idx); adj = nonorth_graph(L)
    S = clique_in(adj, (1 << len(L)) - 1)
    assert len(S) >= kc
    return [L_idx[i] for i in S[:kc]]

def build(name, h, sym, mode, S, V=None, orthf=None):
    """returns (nv, clauses, info); line labels are positions in the unit's index list"""
    orthf = orthf or orth
    V = V if V is not None else unit_idx(name); pos = {t: i for i, t in enumerate(V)}; v = len(V)
    kc = len(S); assert all(t in pos for t in S)
    nv = 0; cls = []
    def new():
        nonlocal nv; nv += 1; return nv
    Sset = {t: k for k, t in enumerate(S)}
    Uv = {t: [new() for _ in range(h)] for t in V if t not in Sset}
    Vv = Uv if sym else {t: [new() for _ in range(h)] for t in V}
    def ub(t, k): return ('c', int(Sset[t] == k)) if t in Sset else ('v', Uv[t][k])
    def vb(t, k): return ub(t, k) if sym else ('v', Vv[t][k])
    def AND(a, b):
        if a[0] == 'c' and b[0] == 'c': return ('c', a[1] & b[1])
        if a[0] == 'c': return b if a[1] else ('c', 0)
        if b[0] == 'c': return a if b[1] else ('c', 0)
        if a[1] == b[1]: return a
        z = new(); x, y = a[1], b[1]; cls.extend([[-z, x], [-z, y], [z, -x, -y]]); return ('v', z)
    def XOR(a, b):
        if a[0] == 'c' and b[0] == 'c': return ('c', a[1] ^ b[1])
        if a[0] == 'c': return ('v', -b[1]) if a[1] else b
        if b[0] == 'c': return ('v', -a[1]) if b[1] else a
        z = new(); x, y = a[1], b[1]; cls.extend([[-z, x, y], [-z, -x, -y], [z, -x, y], [z, x, -y]]); return ('v', z)
    def Bent(t, s):
        acc = ('c', 0)
        for k in range(h): acc = XOR(acc, AND(ub(t, k), vb(s, k)))
        return acc
    def force(l, val):
        if l[0] == 'c':
            if l[1] != val: cls.append([])
            return
        cls.append([l[1] if val else -l[1]])
    orthp = []
    for t in V:
        force(Bent(t, t), 1)
        for s in V:
            if s == t: continue
            if not orthf(t, s): force(Bent(t, s), 0)
            elif not sym or t < s: orthp.append((t, s))
    if mode == 'alt':
        lits = []
        for (t, s) in orthp:
            d = Bent(t, s)
            if d[0] == 'c':
                assert d[1] == 1, 'trivially SAT'
                continue
            lits.append(-d[1])
        cls.append(lits)
    info = dict(v=v, h=h, sym=sym, mode=mode, nv=nv, ncls=len(cls), orth=len(orthp), gauge=S)
    return nv, cls, info, Uv, Vv, orthp

def dimacs(nv, cls):
    return "p cnf %d %d\n" % (nv, len(cls)) + "".join(" ".join(map(str, c)) + " 0\n" for c in cls)

def sha(s): return hashlib.sha256(s.encode()).hexdigest()

# ---------------------------------------------------------------- registry
def sub_unit(kc_S, k):
    """negative control: the gauge clique S plus the first k other lines of P112 (index order)"""
    return list(kc_S) + [t for t in P112_IDX if t not in set(kc_S)][:k]

import functools
KC = {'E8': 8, 'P112': 8, 'P104H4': 8, 'P104_759': 8, 'P104_767': 8, 'P104_801': 8, 'E7': 7, 'E6': 5}
@functools.lru_cache(maxsize=None)
def registry():
    """name -> dict(unit, h, sym, mode, expect, S, V)"""
    R = {}
    def add(unit, h, sym, mode, expect, V=None, tag=None):
        S = gauge_clique(unit if V is None else 'P112', unit_idx(unit if V is None else 'P112'), KC[unit if V is None else 'P112'])
        if expect == 'UNSAT' and sym: assert len(S) >= h - 1
        name = '%s_%s_h%d_%s' % (tag or unit, 'sym' if sym else 'gen', h, mode)
        R[name] = dict(unit=unit, h=h, sym=sym, mode=mode, expect=expect, S=S, V=V)
    for u in ('P112', 'E8', 'P104H4', 'P104_759', 'P104_767', 'P104_801'):
        for sym in (True, False): add(u, 9, sym, 'alt', 'UNSAT')
    for u in ('E7', 'E6'): add(u, 7, False, 'alt', 'UNSAT')
    for u in ('P112', 'E8', 'P104H4'):
        for sym in (True, False): add(u, 9, sym, 'ctl', 'SAT')
    for u in ('E7', 'E6'): add(u, 7, False, 'ctl', 'SAT')
    S = gauge_clique('P112', unit_idx('P112'), 8)
    for k in (20, 40): add('P112', 9, False, 'alt', 'SAT', V=sub_unit(S, k), tag='SUB%d' % k)
    for sym in (True, False): add('P112', 10, sym, 'alt', 'SAT')
    # P111 (bit unit of PR #589): own coordinates, gauge clique from its own Gram
    L, of = p111(); adjn = [sum(1 << s for s in range(111) if s != t and not of(t, s)) for t in range(111)]
    from satgen import clique_in
    S1 = clique_in(adjn, (1 << 111) - 1)[:8]
    for sym in (True, False):
        for mode, ex in (('alt', 'UNSAT'), ('ctl', 'SAT')):
            name = 'P111_%s_h9_%s' % ('sym' if sym else 'gen', mode)
            R[name] = dict(unit='P111', h=9, sym=sym, mode=mode, expect=ex, S=S1, V=None)
    return R

def p111():
    """(vectors, orthf) of the P111 bit unit (data/p111_lines.json)"""
    L = json.load(open(os.path.join(DATA, 'p111_lines.json')))['lines']
    return L, (lambda t, s: sum(a * b for a, b in zip(L[t], L[s])) == 0)

def build_named(name):
    r = registry()[name]
    if r['unit'] == 'P111':
        L, of = p111(); return build('P111', r['h'], r['sym'], r['mode'], r['S'], V=list(range(111)), orthf=of)
    return build(r['unit'], r['h'], r['sym'], r['mode'], r['S'], V=r['V'])

def decode_model(name, pos_vars):
    """returns (fitting?, #orthogonal pairs with B_ts = 0, #orthogonal pairs) for a model of an instance"""
    r = registry()[name]; nv, cls, info, Uv, Vv, orthp = build_named(name)
    V = r['V'] if r['V'] is not None else (list(range(111)) if r['unit'] == 'P111' else unit_idx(r['unit'])); h = r['h']; Sset = {t: k for k, t in enumerate(r['S'])}
    def row(t, M):
        if M is Uv and t in Sset: return [int(Sset[t] == k) for k in range(h)]
        return [int(x in pos_vars) for x in M[t]]
    # in the symmetric model V = U so the S rows are constants for both
    Ur = {t: row(t, Uv) for t in V}; Vr = Ur if r['sym'] else {t: [int(x in pos_vars) for x in Vv[t]] for t in V}
    ent = lambda t, s: sum(a & b for a, b in zip(Ur[t], Vr[s])) & 1
    of = p111()[1] if r['unit'] == 'P111' else orth
    fit = all(ent(t, t) == 1 for t in V) and all(ent(t, s) == 0 for t in V for s in V if t != s and not of(t, s))
    zeros = sum(1 for (t, s) in orthp if ent(t, s) == 0)
    return fit, zeros, len(orthp)
