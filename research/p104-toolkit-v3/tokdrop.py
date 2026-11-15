#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Token-settled drop engine for P104 native words (our TOKDEBT / SEEDBUILD / OWNRETIME lanes, consolidated).

A *stay* is one interior stop of a public register: (r, F, t_arr, t_dep) = register r sits at frame F from the MOVE at
program index t_arr to the MOVE at t_dep.  Dropping a stay deletes the two MOVEs around it (the register climbs
straight to its next frame) and every event that touched r at F.  The engine then asks whether the damage can be
repaired for free:

 1. clean-mode repair (Engine.solve).  Unknown corrections a += k*b are inserted wherever a and b sit at a common
    frame after a became dirty (b clean there, so final rows stay LINEAR in k).  Constraints: every main and every
    helper not ending at V has its base final row, compared on the main (pi) columns only ("clean mode": helper token
    columns are deleted); helpers ending at V land in the row span of the V group (free V post-ops); owned rows at
    every owned->public write and CLEAR equal the base.  Solved mod 2^31-1 by random rank-1 tensor projections
    (Schwartz-Zippel), rank test, canonical rref solution.
 2. settlement rank (settle).  The helper-token columns the clean repair ignored are settled by a premix at t = 0: an
    invertible block-diagonal map on registers sharing a birth frame.  rank = sum_f rank[Xnew_f | Xbase_f] - rank Xnew_f.
    Tier B keeps every row exact; tier A relaxes helpers ending at V.  rank 0 <=> a premix exists.
 3. exact build (build_exact).  Rational reconstruction of the corrections, exact Fraction solve of the premix
    (ADDs at the birth frame at t = 0), exact V post-ops, exact replay against the base.

Results from this engine (see README): the two drops of our #7601 (main 134 at chart 595, main 100 at chart 783),
rebuilt here byte-for-byte; and, run on the frame-perp dual (dualword.py), the main-902 drop at chart 595.

API
  ctx = Context(word)                       base word (dict); ctx.census() -> interior stays with stop price m
  ctx.stay(r, F) -> (r, F, t_arr, t_dep)    locate a stay
  ctx.test(stays, owned=True, frames_mode='down'|'all'|'none', want=True) -> dict(ok, K, nviol, r1, r2, x, ...)
  ctx.settle_rank(res, tier) -> (rank, per_frame, pi_ok, nobs)
  ctx.build_exact(stays, owned=False) -> (word, report)       raises BuildError if any step is not exact
CLI
  python3 tokdrop.py WORD scan  r:F [r:F ...]      repair + settlement rank of single-stay drops
  python3 tokdrop.py WORD build r:F [r:F ...] OUT  exact word with all listed stays dropped
numpy is required (stdlib + numpy); python-flint is used automatically if installed (faster, same verdicts).
"""
import collections
import gzip
import json
import math
import random
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pragma: no cover
    sys.exit('tokdrop.py needs numpy (pip install numpy); stdlib-only tools: pricekit.py, accx.py, dualword.py')
sys.path.insert(0, str(Path(__file__).resolve().parent))
import modp  # noqa: E402

P = modp.P


class BuildError(ValueError):
    pass


def load(path):
    op = gzip.open if str(path).endswith('.gz') else open
    with op(path, 'rt') as f:
        return json.load(f)


def save(W, path):
    with gzip.open(path, 'wt') as f:
        json.dump(W, f)


def qm(s):
    q = Q(s)
    return q.numerator % P * pow(q.denominator % P, P - 2, P) % P


def mains_of(W):
    live = set(W['live']); H = W['hosted']
    return live | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])


def spanmask(basis):
    s = {0}
    for v in basis:
        s |= {x ^ v for x in s}
    m = 0
    for x in s:
        m |= 1 << x
    return m


def xlogx(j):
    return j * math.log(j) if j > 0 else 0.0


def ratrec(a, p=P):
    a %= p; r0, r1 = p, a; s0, s1 = 0, 1; B = int((p // 2) ** 0.5)
    while r1 > B:
        q = r0 // r1; r0, r1 = r1, r0 - q * r1; s0, s1 = s1, s0 - q * s1
    if s1 == 0 or abs(s1) > B:
        return None
    v = Q(r1, s1)
    return v if (v.numerator - a * v.denominator) % p == 0 else None


# ----------------------------------------------------------------------------------------------- word structure
def stays(W):
    """per register: list of [frame, t_arr, t_dep] (t_arr = -1 initial; t_dep = len(program) final)."""
    L = collections.defaultdict(list)
    for r in range(W['public']):
        L[r].append([W['initial'][r], -1, None])
    for i, e in enumerate(W['program']):
        if e[0] == 'MOVE':
            L[e[1]][-1][2] = i; L[e[1]].append([e[3], i, None])
        elif e[0] == 'INIT':
            L[e[1]].append([e[2], i, None])
        elif e[0] == 'CLEAR':
            L[e[1]][-1][2] = i
    for r in L:
        if L[r][-1][2] is None:
            L[r][-1][2] = len(W['program'])
    return L


def replay_mod(W, snaps=None):
    """dense mod-P replay; snaps {pos: regs} records rows BEFORE event pos.  Returns (X, snapshots, owned-write rows,
    CLEAR rows)."""
    n = W['public']; N = n + W['owned_fields']
    X = np.zeros((N, n), dtype=np.int64); X[np.arange(n), np.arange(n)] = 1
    out = {}; ow = {}; cl = {}; snaps = snaps or {}
    prog = W['program']
    for i, e in enumerate(prog + [None]):
        if i in snaps:
            for r in snaps[i]:
                out[(i, r)] = X[r].copy()
        if e is None:
            break
        op = e[0]
        if op == 'MOVE':
            continue
        r = e[1]
        if op == 'INIT':
            X[r] = 0
        elif op == 'CLEAR':
            cl[i] = X[r].copy(); X[r] = 0
        elif op == 'SCALE':
            X[r] = X[r] * qm(e[2]) % P
        else:
            s_ = e[2]
            if r < n and s_ >= n:
                ow[i] = X[s_].copy()
            if op == 'COPY':
                X[r] = qm(e[3]) * X[s_] % P
            else:
                X[r] = (X[r] + qm(e[3]) * X[s_]) % P
    return X, out, ow, cl


def frac_replay(W):
    n = W['public']; N = n + W['owned_fields']
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    for e in W['program']:
        op = e[0]
        if op == 'MOVE':
            continue
        r = e[1]
        if op in ('INIT', 'CLEAR'):
            rows[r] = {}; continue
        if op == 'SCALE':
            q = Q(e[2]); rows[r] = {k: v * q for k, v in rows[r].items()}; continue
        s_, q = e[2], Q(e[3]); R = rows[r]
        if op == 'COPY':
            R.clear()
        for k, v in list(rows[s_].items()):
            nv = R.get(k, 0) + q * v
            if nv:
                R[k] = nv
            else:
                R.pop(k, None)
    return rows


def owned_observations(W, with_rows=False):
    """every owned->public write and every CLEAR, with the exact owned row at that moment (and the final rows)."""
    n = W['public']
    rows = [{r: Q(1)} if r < n else {} for r in range(n + W['owned_fields'])]
    out = []
    for e in W['program']:
        op = e[0]
        if op == 'MOVE':
            continue
        r = e[1]
        if op == 'INIT':
            rows[r] = {}; continue
        if op == 'CLEAR':
            out.append(('cl', r, dict(rows[r]))); rows[r] = {}; continue
        if op == 'SCALE':
            q = Q(e[2]); rows[r] = {k: v * q for k, v in rows[r].items()}; continue
        s_, q = e[2], Q(e[3])
        if r < n and s_ >= n:
            out.append(('ow', r, s_, dict(rows[s_])))
        R = rows[r]
        if op == 'COPY':
            R.clear()
        for k, v in list(rows[s_].items()):
            nv = R.get(k, 0) + q * v
            if nv:
                R[k] = nv
            else:
                R.pop(k, None)
    return (out, rows) if with_rows else out


def insert(W2, evs):
    """evs: list of (pos, event) inserted before W2 position pos (stable order)."""
    ins = collections.defaultdict(list)
    for pos, ev in evs:
        ins[pos].append(ev)
    prog = []
    for j, e in enumerate(W2['program'] + [None]):
        prog.extend(ins.get(j, []))
        if e is not None:
            prog.append(e)
    W3 = dict(W2); W3['program'] = prog
    return W3


def postops(W, VF, rows=None):
    """exact V post-ops (ADD/SCALE at V) so every helper ending at V is the identity row.  Returns (W', nops).
    rows: exact final rows of W if already known (they are copied, not modified)."""
    rows = frac_replay(W) if rows is None else [dict(x) for x in rows]
    n = W['public']; mains = mains_of(W)
    Vg = [r for r in range(n) if W['final'][r] == VF]
    Vh = [r for r in Vg if r not in mains]; Vm = [r for r in Vg if r in mains]; Vhs = set(Vh)
    ops = []
    bad = [h for h in Vh if rows[h] != {h: Q(1)}]

    def axpy(dst, src, c):
        for k, v in src.items():
            nv = dst.get(k, 0) + c * v
            if nv:
                dst[k] = nv
            else:
                dst.pop(k, None)
    for h in bad:
        R = dict(rows[h])
        for j in Vm:
            c = R.get(j)
            if c:
                ops.append(['ADD', h, j, str(-c), VF]); axpy(R, rows[j], -c)
        for j in list(R):
            if j not in Vhs:
                raise BuildError('helper %d keeps non-V coordinate %d' % (h, j))
        rows[h] = R
    badset = set(bad)
    for h in bad:
        R = rows[h]
        for j in [j for j in R if j not in badset]:
            c = R[j]; ops.append(['ADD', h, j, str(-c), VF]); R.pop(j)
    order = list(bad)
    for i, h in enumerate(order):
        if not rows[h].get(h):
            for g in order[i + 1:]:
                if rows[g].get(h):
                    ops.append(['ADD', h, g, '1', VF]); axpy(rows[h], rows[g], 1)
                    break
            else:
                raise BuildError('singular V block at %d' % h)
        c = rows[h][h]
        if c != 1:
            ops.append(['SCALE', h, str(1 / c), VF]); rows[h] = {k: v / c for k, v in rows[h].items()}
        for g in order:
            if g == h:
                continue
            c = rows[g].get(h)
            if c:
                ops.append(['ADD', g, h, str(-c), VF]); axpy(rows[g], rows[h], -c)
    W2 = dict(W); W2['program'] = W['program'] + ops
    return W2, len(ops)


# ----------------------------------------------------------------------------------------------- edits
class Edit:
    """build W2 from base W.  ins[i] = events inserted before base event i; dele = deleted base indices;
    mv[i] = replacement event for base index i."""

    def __init__(s, W):
        s.W = W; s.n = W['public']; s.n2 = s.n
        s.ins = collections.defaultdict(list); s.dele = set(); s.mv = {}

    def build(s):
        W = s.W; prog = []; origin = []
        for i, e in enumerate(W['program'] + [None]):
            for ev in s.ins.get(i, []):
                prog.append(list(ev)); origin.append(None)
            if e is None:
                break
            if i in s.dele:
                continue
            prog.append(s.mv[i] if i in s.mv else list(e)); origin.append(i)
        W2 = dict(W); W2['program'] = prog
        return W2, origin


# ----------------------------------------------------------------------------------------------- the engine
class Engine:
    def __init__(s, ctx, W2, origin):
        s.ctx = ctx; s.W2 = W2; s.origin = origin; s.n2 = W2['public']; s.N2 = s.n2 + W2['owned_fields']
        s.B = ctx.W; s.n = s.B['public']
        Xb, _, owb, clb = ctx.brep
        T = np.zeros((s.n2, s.n2), dtype=np.int64); T[:s.n, :s.n] = Xb[:s.n]
        s.cm = np.zeros(s.n2, dtype=np.int64)
        s.owb = owb; s.clb = clb
        s.mains = mains_of(W2)
        for r in s.mains:
            if r < s.n2:
                s.cm[r] = 1
        s.T = T * s.cm[None, :] if ctx.clean else T
        s.Vgrp = [r for r in range(s.n2) if W2['final'][r] == ctx.VF]
        s.Vh = set(r for r in s.Vgrp if r not in s.mains)
        s.L = stays(W2)

    def ext(s, row):
        o = np.zeros(s.n2, dtype=np.int64); o[:s.n] = row[:s.n]
        return o * s.cm if s.ctx.clean else o

    def dirt(s, cands):
        d = {}
        for a, b, pos, F in cands:
            if a not in d or d[a] > pos:
                d[a] = pos
        for j, e in enumerate(s.W2['program']):
            if e[0] in ('ADD', 'COPY'):
                r, s_ = e[1], e[2]
                if s_ in d and d[s_] <= j and (r not in d or d[r] > j):
                    d[r] = j + 1
        return d

    def filter_linear(s, cands):
        while True:
            d = s.dirt(cands)
            keep = [c for c in cands if not (c[1] in d and d[c[1]] <= c[2])]
            if len(keep) == len(cands):
                return keep, d
            cands = keep

    def solve(s, cands, seed=1, extra_M=8, want_solution=True):
        t0 = time.time(); clean = s.ctx.clean
        cands, d = s.filter_linear(list(cands))
        K = len(cands)
        W2 = s.W2; n2 = s.n2; N2 = s.N2
        snaps = collections.defaultdict(set)
        for a, b, pos, F in cands:
            snaps[pos].add(b)
        X2, sn, ow2, cl2 = replay_mod(W2, snaps)
        if clean:
            cm = s.cm
            X2 = X2 * cm[None, :]; sn = {k: v * cm for k, v in sn.items()}
            ow2 = {k: v * cm for k, v in ow2.items()}; cl2 = {k: v * cm for k, v in cl2.items()}
        Rb = (np.array([sn[(pos, b)] for a, b, pos, F in cands], dtype=np.int64).reshape(K, n2) if K
              else np.zeros((0, n2), dtype=np.int64))
        inj = collections.defaultdict(list)
        for i, (a, b, pos, F) in enumerate(cands):
            inj[pos].append((a, i))
        Sym = np.zeros((N2, max(K, 1)), dtype=np.int64); live = np.zeros(N2, dtype=bool)
        ownc = []
        prog = W2['program']
        for j, e in enumerate(prog + [None]):
            for a, i in inj.get(j, []):
                Sym[a, i] = (Sym[a, i] + 1) % P; live[a] = True
            if e is None:
                break
            op = e[0]
            if op == 'MOVE':
                continue
            r = e[1]
            if op == 'INIT':
                Sym[r] = 0; live[r] = False
            elif op == 'CLEAR':
                if live[r]:
                    ownc.append((Sym[r].copy(), j, 'clear'))
                Sym[r] = 0; live[r] = False
            elif op == 'SCALE':
                if live[r]:
                    Sym[r] = Sym[r] * qm(e[2]) % P
            else:
                s_ = e[2]
                if r < n2 and s_ >= n2 and live[s_]:
                    ownc.append((Sym[s_].copy(), j, 'write'))
                if op == 'COPY':
                    Sym[r] = qm(e[3]) * Sym[s_] % P if live[s_] else 0; live[r] = live[s_]
                elif live[s_]:
                    Sym[r] = (Sym[r] + qm(e[3]) * Sym[s_]) % P; live[r] = True
        Nv = s.ctx.v_null(s.T, s.Vgrp)
        E_rows = []; E_rhs = []; V_rows = []; V_rhs = []; viol = []
        Vlist = sorted(s.Vh)
        VC = modp.matmul(X2[Vlist][:, :n2], Nv) if Vlist else None
        Vpos = {R: i for i, R in enumerate(Vlist)}
        for R in range(n2):
            if R in s.Vh:
                cur = VC[Vpos[R]]
                if live[R]:
                    V_rows.append(Sym[R]); V_rhs.append((-cur) % P)
                elif cur.any():
                    viol.append(('Vspan', R))
            else:
                diff = (s.T[R] - X2[R][:n2]) % P
                if live[R]:
                    E_rows.append(Sym[R]); E_rhs.append(diff)
                elif diff.any():
                    viol.append(('exact', R))

        def borow(j, kind):
            oi = s.origin[j]
            if oi is None:
                o = W2['program'][j][2] if kind == 'write' else W2['program'][j][1]
                for jj in range(j + 1, len(W2['program'])):
                    ee = W2['program'][jj]
                    if ee[0] in ('ADD', 'COPY') and ee[1] == o:
                        return None
                    if s.origin[jj] is None:
                        continue
                    if ee[0] in ('ADD', 'COPY') and ee[2] == o and ee[1] < n2:
                        return s.owb.get(s.origin[jj])
                    if ee[0] == 'CLEAR' and ee[1] == o:
                        return s.clb.get(s.origin[jj])
                return None
            return (s.owb if kind == 'write' else s.clb).get(oi)
        livepos = {(j, kind) for _, j, kind in ownc}
        for j, kind in [(j, 'write') for j in ow2] + [(j, 'clear') for j in cl2]:
            if (j, kind) in livepos:
                continue
            b = borow(j, kind); c = (ow2 if kind == 'write' else cl2)[j]
            if b is None:
                continue
            if not np.array_equal(s.ext(b) % P, c % P):
                viol.append(('owned', j, kind))
        for sv, j, kind in ownc:
            b = borow(j, kind); c = (ow2 if kind == 'write' else cl2)[j]
            if b is None:
                raise BuildError('dirty owned register at a new event %d' % j)
            E_rows.append(sv); E_rhs.append((s.ext(b) - c) % P)
        res = dict(K=K, ndirty=len(d), nE=len(E_rows), nV=len(V_rows), viol=viol[:20], nviol=len(viol), cands=cands)
        if viol:
            res['ok'] = False; res['why'] = 'clean-violation'; return res
        if K == 0:
            res['ok'] = all(not x.any() for x in E_rhs + V_rhs); res['x'] = []; res['r1'] = res['r2'] = 0
            return res
        rng = random.Random(seed); M = K + extra_M

        def rmat(a, b):
            return np.array([rng.randrange(P) for _ in range(a * b)], dtype=np.int64).reshape(a, b)
        Atot = np.zeros((M, K), dtype=np.int64); btot = np.zeros(M, dtype=np.int64)
        blocks = []
        if E_rows:
            blocks.append((np.array(E_rows) % P, np.array(E_rhs) % P, None))
        if V_rows:
            blocks.append((np.array(V_rows) % P, np.array(V_rhs) % P, Nv))
        for S, Rhs, Nm in blocks:
            nr = S.shape[0]
            al = rmat(M, nr)
            if Nm is None:
                be = rmat(n2, M)
                Bproj = modp.matmul(Rb, be); Rp = modp.matmul(Rhs, be)
            else:
                ga = rmat(Nm.shape[1], M)
                Bproj = modp.matmul(Rb, modp.matmul(Nm, ga)); Rp = modp.matmul(Rhs, ga)
            A1 = modp.matmul(al, S); B1 = Bproj.T
            Atot = (Atot + (A1 * B1) % P) % P
            btot = (btot + ((al * Rp.T) % P).sum(axis=1) % P) % P
        Ab = np.hstack([Atot, btot.reshape(M, 1)])
        r1 = modp.rank(Atot); r2 = modp.rank(Ab)
        res.update(r1=r1, r2=r2, ok=(r1 == r2), secs=time.time() - t0)
        if r1 == r2 and want_solution:
            R_, rk = modp.rref(Ab); x = [0] * K
            for i in range(rk):
                nz = np.nonzero(R_[i])[0]
                piv = int(nz[0]) if len(nz) else None
                if piv is None or piv == K:
                    res['ok'] = False; break
                x[piv] = int(R_[i, K])
            res['x'] = x
        return res


def closure(E, seeds):
    d = dict(seeds)
    for j, e in enumerate(E.W2['program']):
        if e[0] in ('ADD', 'COPY'):
            r, s_ = e[1], e[2]
            if s_ in d and d[s_] <= j and (r not in d or d[r] > j + 1):
                d[r] = j + 1
    return d


def byframe(E):
    if not hasattr(E, '_bf'):
        bf = collections.defaultdict(list)
        for r, L in E.L.items():
            for F, s, e in L:
                bf[F].append((s, e, r))
        E._bf = bf
    return E._bf


# ----------------------------------------------------------------------------------------------- context
class Context:
    def __init__(s, W, clean=True):
        s.W = W; s.clean = clean; s.n = W['public']; s.NO = W['owned_fields']
        s.dim = [len(b) for b in W['frames']]
        s.mask = [spanmask(b) for b in W['frames']]
        zs = [i for i, d in enumerate(s.dim) if d == 0]; vs = [i for i, d in enumerate(s.dim) if d == 9]
        if len(zs) != 1 or len(vs) != 1:
            raise BuildError('need exactly one {0} frame and one V frame')
        s.Z, s.VF = zs[0], vs[0]
        s.stays = stays(W)
        s.brep = replay_mod(W)
        s._vnull = {}
        s._census = None
        s._rows = None
        s._obs = None

    def base_rows(s):
        if s._rows is None:
            s._obs, s._rows = owned_observations(s.W, with_rows=True)
        return s._rows

    def base_obs(s):
        if s._obs is None:
            s._obs, s._rows = owned_observations(s.W, with_rows=True)
        return s._obs

    def v_null(s, T, Vgrp):
        key = (tuple(Vgrp), T.shape[0])
        if key not in s._vnull:
            s._vnull[key] = modp.nullspace(T[Vgrp])
        return s._vnull[key]

    def sub(s, a, b):
        return (s.mask[a] & ~s.mask[b]) == 0

    def downset(s, G):
        return {F for F in range(len(s.W['frames'])) if F != s.Z and s.sub(F, G)}

    def census(s):
        """interior public stays with their stop price m (D0/call saved by dropping the stop) and event kinds."""
        if s._census is None:
            W = s.W; n = s.n
            st = [[dict(f=W['initial'][r], t=-1, ev=[])] for r in range(n)]
            for i, e in enumerate(W['program']):
                op = e[0]; r = e[1]
                if op == 'MOVE':
                    if r < n:
                        st[r].append(dict(f=e[3], t=i, ev=[]))
                    continue
                if op in ('ADD', 'COPY'):
                    s_ = e[2]
                    if r < n:
                        st[r][-1]['ev'].append(('OW' if s_ >= n else 'PI', i, s_))
                    if s_ < n:
                        st[s_][-1]['ev'].append(('OR' if r >= n else 'PO', i, r))
            recs = []
            for r in range(n):
                S = st[r]; d = [s.dim[x['f']] for x in S]
                for k in range(1, len(S) - 1):
                    m = xlogx(d[k + 1] - d[k - 1]) - xlogx(d[k] - d[k - 1]) - xlogx(d[k + 1] - d[k])
                    kinds = frozenset(x[0] for x in S[k]['ev'])
                    t_dep = S[k + 1]['t']
                    recs.append(dict(r=r, k=k, f=S[k]['f'], dim=d[k], m=m, kinds=kinds,
                                     stay=(r, S[k]['f'], S[k]['t'], t_dep)))
            s._census = recs
        return s._census

    def stay(s, r, F):
        hits = [x for x in s.stays[r] if x[0] == F and x[1] >= 0 and x[2] < len(s.W['program'])]
        if len(hits) != 1:
            raise BuildError('register %d has %d interior stays at frame %d' % (r, len(hits), F))
        return (r, F, hits[0][1], hits[0][2])

    def route_cost(s, fr):
        return sum(xlogx(abs(s.dim[b] - s.dim[a])) for a, b in zip(fr, fr[1:]))

    def make(s, drops):
        B0 = s.W; ed = Edit(B0); prog = B0['program']; seeds_base = {}; saved = 0.0
        byreg = collections.defaultdict(list)
        for x in drops:
            byreg[x[0]].append(x)
        for h, L in byreg.items():
            full = s.stays[h]; fr0 = [x[0] for x in full]
            dset = {(F, a) for _, F, a, _ in L}
            keep = [x for x in full if (x[0], x[1]) not in dset]
            saved += s.route_cost([x[0] for x in keep]) - s.route_cost(fr0)
            for _, F, a, d in L:
                for i in range(a + 1, d):
                    e = prog[i]
                    if e[0] == 'MOVE':
                        continue
                    regs = [e[1]] if e[0] in ('SCALE', 'INIT', 'CLEAR') else [e[1], e[2]]
                    if h in regs:
                        ed.dele.add(i); seeds_base.setdefault(e[1], i)
                        if seeds_base[e[1]] > i:
                            seeds_base[e[1]] = i
                        if e[0] in ('ADD', 'COPY'):
                            if h not in seeds_base or seeds_base[h] > i:
                                seeds_base[h] = i
                ed.dele.add(a)
            for j in range(1, len(full)):
                if (full[j][0], full[j][1]) in dset:
                    continue
                if (full[j - 1][0], full[j - 1][1]) in dset:
                    k = j - 1
                    while (full[k][0], full[k][1]) in dset:
                        k -= 1
                    a = full[j][1]; e = list(prog[a]); e[2] = full[k][0]; ed.mv[a] = e
            if (full[-1][0], full[-1][1]) in dset:
                raise BuildError('cannot drop the final stay of %d' % h)
        W2, org = ed.build()
        pos_of = {o: j for j, o in enumerate(org) if o is not None}

        def wpos(i):
            while i not in pos_of:
                i += 1
            return pos_of[i]
        seeds = {r: wpos(i) for r, i in seeds_base.items()}
        return ed, W2, org, seeds, saved

    def cands_all(s, E, d, frames=None, owned_src=True, owned_tgt=True):
        bf = byframe(E); out = set()
        for a, da in d.items():
            if a >= E.n2 and not owned_tgt:
                continue
            for F, sa, ea in E.L[a]:
                if ea is None or ea < da:
                    continue
                if frames is not None and F not in frames:
                    continue
                if F == s.VF and a < E.n2:
                    continue
                for sb, eb, b in bf[F]:
                    if b == a:
                        continue
                    if b >= E.n2 and not owned_src:
                        continue
                    lo = max(sa, sb) + 1; hi = min(ea, eb); lo = max(lo, da)
                    if lo > hi:
                        continue
                    if b in d and d[b] <= lo:
                        continue
                    out.add((a, b, lo, F))
                    hb = min(hi, d[b]) if b in d else hi
                    if hb > lo:
                        out.add((a, b, hb, F))
        return sorted(out, key=lambda c: c[2])

    def test(s, drops, frames_mode='down', K=4000, owned=True, seed=1, want=False):
        ed, W2, org, seeds, sv = s.make(drops)
        E = Engine(s, W2, org)
        dd = closure(E, seeds)
        S = set()
        for h, F, a, d_ in drops:
            L = s.stays[h]; i = [x[1] for x in L].index(a); nf = L[i + 1][0]
            S |= s.downset(nf) | {F}
        if frames_mode == 'all':
            S = None
        elif frames_mode == 'none':      # no correction candidates at all (control: is the drop damaging?)
            S = set()
        cc = s.cands_all(E, dd, frames=S, owned_src=owned, owned_tgt=owned)
        if len(cc) > K:
            t0 = min(x[2] for x in cc)
            cc = [c for c in cc if c[2] <= t0 + 3000][:K]
        r = E.solve(cc, seed=seed, want_solution=want)
        r['saved'] = sv; r['W2'] = W2; r['org'] = org
        return r

    def test_best(s, drops, owned=True):
        """frames 'down' first, then 'all' if it does better (the scan rule of TOKDEBT/DUALSCAN)."""
        r = s.test(drops, owned=owned, want=True, frames_mode='down')
        if r['nviol'] or r['K'] < 30 or not r.get('ok'):
            r2 = s.test(drops, owned=owned, want=True, frames_mode='all')
            if r2['nviol'] < r['nviol'] or r2.get('ok'):
                r = r2
        return r

    # ------------------------------------------------------------------------------------------- settlement
    def corrected(s, r):
        W2 = r['W2']; evs = collections.defaultdict(list)
        for (a, b, pos, F), v in zip(r.get('cands', []), r.get('x', [])):
            if v:
                evs[pos].append(['ADD', a, b, str(int(v)), F])
        prog = []; org = list(r['org']); org2 = []
        for j, e in enumerate(W2['program'] + [None]):
            for ev in evs.get(j, []):
                prog.append(ev); org2.append(None)
            if e is None:
                break
            prog.append(e); org2.append(org[j])
        W3 = dict(W2); W3['program'] = prog
        return W3, org2

    def settle_rank(s, r, tier='A'):
        """premix settlement rank of a repaired schedule: (rank, {birth frame: rank}, pi_ok, #observations)."""
        B0 = s.W; n = s.n
        W3, org2 = s.corrected(r)
        n2 = W3['public']; X, _, ow, cl = replay_mod(W3)
        Xb, _, owb, clb = s.brep
        new = [X[q][:n2] for q in range(n2)]; base = [Xb[q][:n] for q in range(n)]; kind = [('pub', q) for q in range(n2)]
        for j, row in ow.items():
            oi = org2[j]
            if oi is not None and oi in owb:
                new.append(row); base.append(owb[oi]); kind.append(('ow', j))
        for j, row in cl.items():
            oi = org2[j]
            if oi is not None and oi in clb:
                new.append(row); base.append(clb[oi]); kind.append(('cl', j))
        Xn = np.array(new) % P; Xbb = np.array(base) % P
        mains = mains_of(B0); pc = sorted(mains)
        Vh = {q for q in range(n) if B0['final'][q] == s.VF and q not in mains}
        keep = [i for i, k in enumerate(kind) if not (tier == 'A' and k[0] == 'pub' and k[1] in Vh)]
        Xn = Xn[keep]; Xbb = Xbb[keep]
        pi_ok = not ((Xn[:, pc] - Xbb[:, pc]) % P).any() if tier == 'A' else None
        fr = collections.defaultdict(list)
        for q in range(n):
            fr[B0['initial'][q]].append(q)
        tot = 0; per = {}
        for f_, R in fr.items():
            An = Xn[:, R]; Ab = Xbb[:, R]
            if not (An != Ab).any():
                continue
            rn = modp.rank(An); rj = modp.rank(np.hstack([An, Ab]))
            if rj > rn:
                per[f_] = rj - rn; tot += rj - rn
        return tot, per, pi_ok, len(keep)

    # ------------------------------------------------------------------------------------------- exact build
    def build_exact(s, drops, owned=False, log=print):
        """exact word with every stay in `drops` removed; raises BuildError unless every step is exact."""
        B0 = s.W; n = s.n
        r = s.test(drops, owned=owned, want=True)
        if not r.get('ok'):
            r = s.test(drops, owned=owned, want=True, frames_mode='all')
        if not r.get('ok'):
            raise BuildError('engine found no clean repair (K=%d, violations %d)' % (r['K'], r['nviol']))
        W2 = r['W2']
        evs = []
        for (a, b, pos, F), v in zip(r['cands'], r['x']):
            if v:
                q = ratrec(v)
                if q is None:
                    raise BuildError('rational reconstruction failed')
                evs.append((pos, ['ADD', a, b, str(q), F]))
        W3 = insert(W2, evs)
        obs3, rows = owned_observations(W3, with_rows=True); rows_b = s.base_rows()
        mains = mains_of(B0)
        Vh = {R for R in range(n) if B0['final'][R] == s.VF and R not in mains}
        bad = [R for R in range(n) if rows[R] != rows_b[R] and R not in Vh]
        cols = sorted({c for R in bad for c in set(rows[R]) | set(rows_b[R]) if rows[R].get(c, 0) != rows_b[R].get(c, 0)})
        fr = collections.defaultdict(list)
        for c in range(n):
            fr[B0['initial'][c]].append(c)
        pre = []
        for j in cols:
            R = [x for x in fr[B0['initial'][j]] if x != j]
            idx = sorted(i for i in ({i for i in range(n) for x in R if x in rows[i]}
                                     | {i for i in range(n) if j in rows[i] or j in rows_b[i]}) if i not in Vh)
            A = [[rows[i].get(x, Q(0)) for x in R] + [rows_b[i].get(j, Q(0)) - rows[i].get(j, Q(0))] for i in idx]
            m = len(R); piv = []; rr = 0
            for c in range(m):
                p = next((i for i in range(rr, len(A)) if A[i][c] != 0), None)
                if p is None:
                    continue
                A[rr], A[p] = A[p], A[rr]; inv = 1 / A[rr][c]; A[rr] = [x * inv for x in A[rr]]
                for i in range(len(A)):
                    if i != rr and A[i][c] != 0:
                        f_ = A[i][c]; A[i] = [x - f_ * y for x, y in zip(A[i], A[rr])]
                piv.append(c); rr += 1
            if any(all(x == 0 for x in row[:m]) and row[m] != 0 for row in A):
                raise BuildError('premix for column %d is not solvable exactly' % j)
            pre.append((j, {R[piv[i]]: A[i][m] for i in range(len(piv)) if A[i][m] != 0}))
        ops = [['ADD', x, j, str(c), B0['initial'][j]] for j, y in pre for x, c in y.items()]
        W4 = insert(W3, [(0, e) for e in ops])
        obs4, rows4 = owned_observations(W4, with_rows=True) if ops else (obs3, rows)
        W4, npo = postops(W4, s.VF, rows4)
        if npo:
            obs4, rows4 = owned_observations(W4, with_rows=True)
        bad4 = [R for R in range(n) if rows4[R] != rows_b[R]]
        if bad4:
            raise BuildError('%d public rows differ from the base after premix' % len(bad4))
        key = lambda o: (o[0], o[1], o[2] if o[0] == 'ow' else None, tuple(sorted(o[-1].items())))
        cb = collections.Counter(key(o) for o in s.base_obs())
        c4 = collections.Counter(key(o) for o in obs4)
        rep = dict(K=r['K'], corrections=len(evs), premix=len(ops), postops=npo, saved_D0_per_call=r['saved'],
                   owned_obs_base=sum(cb.values()), owned_obs_new=sum(c4.values()),
                   owned_obs_lost=sum((cb - c4).values()), owned_obs_new_only=sum((c4 - cb).values()))
        if rep['owned_obs_new_only']:
            raise BuildError('new owned observations appeared: %d' % rep['owned_obs_new_only'])
        return W4, rep


def parse_stays(ctx, args):
    out = []
    for a in args:
        r, F = a.split(':')
        out.append(ctx.stay(int(r), int(F)))
    return out


def main(argv):
    if len(argv) < 3 or argv[1] not in ('scan', 'build'):
        print(__doc__); return 2
    W = load(argv[0]); ctx = Context(W)
    print('backend', modp.BACKEND, flush=True)
    if argv[1] == 'scan':
        for st in parse_stays(ctx, argv[2:]):
            r = ctx.test_best([st])
            line = dict(stay=st, ok=bool(r.get('ok')), K=r['K'], nviol=r['nviol'], saved=round(r['saved'], 4))
            if r.get('ok'):
                line['rankA'] = ctx.settle_rank(r, 'A')[0]; line['rankB'] = ctx.settle_rank(r, 'B')[0]
            print(json.dumps(line), flush=True)
        return 0
    *sts, out = argv[2:]
    W4, rep = ctx.build_exact(parse_stays(ctx, sts))
    save(W4, out); print(json.dumps(rep)); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
