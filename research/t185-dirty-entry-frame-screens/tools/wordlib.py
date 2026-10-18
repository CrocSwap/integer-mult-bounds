# SPDX-License-Identifier: Apache-2.0
"""Exact helpers for BORROW-WORD supplier words (PR2833 / PR2857 format).

Climb ledger: same rules as PR2833 new/borrow/audit_local.py (run_borrow) and
PR2857 shared_kernel.apply(); reimplemented independently, nothing imported.
Adjoint responses: exact rational target-dirt response of every register at
every program position (warp-crossing responses are marked tainted).

Prepared for digitalis-p with Claude (Anthropic) assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction as F

V, H_DIM, NREG = 112, 9, 704


def load(path):
    raw = open(path, 'rb').read()
    return json.loads(gzip.decompress(raw)), hashlib.sha256(raw).hexdigest()


def basis(vs):
    piv = {}
    for a in vs:
        while a:
            bit = a.bit_length() - 1
            if bit in piv:
                a ^= piv[bit]
            else:
                piv[bit] = a
                break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1:
                piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))


def contained(a, b):
    return basis(list(a) + list(b)) == b


def span(u):
    s = {0}
    for x in u:
        s |= {a ^ x for a in s}
    return s


def meet(u, w):
    return basis(list(span(u) & span(w)))


def join(*us):
    return basis([x for u in us for x in u])


FULL = basis([1 << i for i in range(H_DIM)])


def regs_of(g):
    return g[1:3] if g[0] == 'add' else g[1:2]


def end_frames(x):
    end = [FULL] * V + [basis([z for z in range(1, 1 << H_DIM) if (z & p).bit_count() % 2 == 0])
                        for p in x['ports']] + [FULL] * (NREG - 2 * V)
    for r, u in x['helper_final'].items():
        end[int(r)] = basis(u)
    return end


def start_frames(x):
    start = [(p,) for p in x['ports']] + [()] * (NREG - V)
    for r, u in x['start_extra'].items():
        start[int(r)] = basis(u)
    return start


class LedgerError(Exception):
    pass


def ledger(x):
    """Return (paid profile Counter, helper width Counter); raise LedgerError on any frame violation."""
    end, start = end_frames(x), start_frames(x)
    cur = list(start)
    paid = Counter()

    def climb(r, u, where):
        u = basis(u)
        if not contained(cur[r], u):
            raise LedgerError(('non-monotone frame', r, where))
        d = len(u) - len(cur[r])
        if d:
            paid[d] += 1
        cur[r] = u

    def step(g, where):
        if g[0] == 'warp':
            if cur[g[1]] != basis(g[3]):
                raise LedgerError(('A warp frame', g[1], where))
            cur[g[1]] = basis(g[4])
        else:
            for r in regs_of(g):
                climb(r, g[-1], where)

    for i, g in enumerate(x['A']):
        step(g, ('A', i))
    lev = {int(t): basis(u) for t, u in x.get('target_levels', {}).items()}
    for t in range(V):
        if cur[V + t] != lev.get(t, ()):
            raise LedgerError(('target level', t))
    for r, u in zip(x['centers'], x['center_frames']):
        u = basis(u)
        if cur[r] != u:
            raise LedgerError(('centre frame', r))
        served = {basis(x['target_levels'].get(str(g[1] - V), [])) for g in x['cut'] if g[2] == r}
        for t in sorted(served, key=lambda s: -len(s)):
            if not contained(t, u):
                raise LedgerError(('centre path not nested', r))
            if t != u:
                paid[len(u) - len(t)] += 1
            u = t
    bw = defaultdict(list)
    for rec in x['warps']:
        bw[rec[0]].append(rec)
    for p in range(len(x['B']) + 1):
        for rec in bw.get(p, []):
            if cur[rec[1]] != basis(rec[3]):
                raise LedgerError(('B warp frame', rec[1], p))
            cur[rec[1]] = basis(rec[4])
        if p < len(x['B']):
            step(x['B'][p], ('B', p))
    for i, g in enumerate(x['restore']):
        step(g, ('R', i))
    live = set(range(NREG)) - set(x['removed'])
    for r in sorted(live):
        climb(r, end[r], ('end',))
    inv = Counter(len(end[r]) - len(start[r]) for r in live if r >= 2 * V)
    return paid, inv


def program(x):
    """Chronological program: A, cut, B (with B warps interleaved by position), restore."""
    prog = [('A', i, g) for i, g in enumerate(x['A'])]
    prog += [('cut', i, g) for i, g in enumerate(x['cut'])]
    bw = defaultdict(list)
    for rec in x['warps']:
        bw[rec[0]].append(rec)
    for p in range(len(x['B']) + 1):
        for rec in bw.get(p, []):
            prog.append(('warpB', p, ['warp', rec[1], rec]))
        if p < len(x['B']):
            prog.append(('B', p, x['B'][p]))
    prog += [('R', i, g) for i, g in enumerate(x['restore'])]
    return prog


def _axpy(dst, src, c):
    for k, val in src.items():
        nv = dst.get(k, F(0)) + c * val
        if nv:
            dst[k] = nv
        else:
            dst.pop(k, None)


def adjoint(x, record=None):
    """Exact backward pass. Returns (R0, taint0, snaps, prog).

    R0[r][t] is the coefficient of register r's initial value in target t's final value (raw dirt).
    snaps[r] is a chronological list of (k, R, tainted) giving r's response just BEFORE program item k,
    for every item k that touches r. A response that crosses a warp operator is tainted (operator-valued).
    """
    prog = program(x)
    resp = [dict() for _ in range(NREG)]
    taint = [False] * NREG
    for t in range(V, 2 * V):
        resp[t] = {t: F(1)}
    snaps = defaultdict(list)
    for k in range(len(prog) - 1, -1, -1):
        _, _, e = prog[k]
        if e[0] == 'add':
            t, s = e[1], e[2]
            if t == s:
                raise ValueError('self add')
            _axpy(resp[s], resp[t], F(e[3], e[4]))
            taint[s] = taint[s] or taint[t]
        elif e[0] == 'scale':
            c = F(e[2], e[3])
            resp[e[1]] = {kk: c * val for kk, val in resp[e[1]].items()}
        elif e[0] == 'warp':
            if resp[e[1]]:
                taint[e[1]] = True
        if record is not None:
            for r in (regs_of(e) if e[0] in ('add', 'scale') else (e[1],)):
                if r in record:
                    snaps[r].append((k, dict(resp[r]), taint[r]))
    for r in snaps:
        snaps[r].reverse()
    return resp, taint, snaps, prog


def precondition_map(x, col):
    col = dict(col)
    for g in x['precondition']:
        if g[0] == 'add':
            t, s, c = g[1], g[2], F(g[3], g[4])
            if s in col:
                _axpy_one(col, t, c * col[s])
        else:
            t, c = g[1], F(g[2], g[3])
            if t in col:
                col[t] = c * col[t]
    return col


def _axpy_one(col, t, val):
    nv = col.get(t, F(0)) + val
    if nv:
        col[t] = nv
    else:
        col.pop(t, None)


def compensation_columns(x):
    cols = defaultdict(dict)
    for g in x['compensation']:
        if g[0] != 'add' or g[-1] != []:
            raise ValueError('unexpected compensation gate')
        _axpy_one(cols[g[2]], g[1], F(g[3], g[4]))
    return {h: c for h, c in cols.items() if c}


def check_responses(x, resp, taint):
    """Compare -precondition(raw dirt) with the stored compensation for every live helper."""
    comp = compensation_columns(x)
    corr = {c['source'] for c in x['initial_corrections']}
    match, mismatch = 0, []
    for h in range(2 * V, NREG):
        if h in x['removed']:
            continue
        got = precondition_map(x, resp[h])
        exp = {t: -v for t, v in comp.get(h, {}).items()}
        if got == exp:
            match += 1
        else:
            mismatch.append(dict(helper=h, tainted=taint[h], correction_source=h in corr))
    return match, mismatch


def timeline(x, prog):
    """Per-register frame requirements in program-index space: (k, kind, required_frame, frame_after)."""
    tl = defaultdict(list)
    lev = {int(t): basis(u) for t, u in x.get('target_levels', {}).items()}
    for k, (sec, i, e) in enumerate(prog):
        if sec == 'cut':
            if i == 0:
                for t in range(V):
                    tl[V + t].append((k, 'pin', lev.get(t, ()), lev.get(t, ())))
                for r, u in zip(x['centers'], x['center_frames']):
                    tl[r].append((k, 'pin', basis(u), basis(u)))
            continue
        if e[0] == 'warp':
            if sec == 'A':
                tl[e[1]].append((k, 'pin', basis(e[3]), basis(e[4])))
            else:
                rec = e[2]
                tl[e[1]].append((k, 'pin', basis(rec[3]), basis(rec[4])))
            continue
        for r in regs_of(e):
            tl[r].append((k, 'gate', basis(e[-1]), basis(e[-1])))
    end = end_frames(x)
    for r in range(NREG):
        tl[r].append((len(prog), 'end', end[r], end[r]))
    return tl
