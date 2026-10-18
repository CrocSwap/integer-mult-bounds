#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Twisted helper-star absorption on fixed R439 bit words: exact finite verification.

Checks, from SHA-256-pinned repository inputs only:
* the single-edge census on the PR967, PR1062, PR1122 and PR1188 words: delete one trailing D
  helper-star restoration a ^= b, and replace the source set Sg of one A gate writing the centre a
  before the first read of a by Sg xor S, where S is the unique register set whose current values
  sum to b's input column.  Every move is replayed on all 661 dirty columns forward and reverse;
  every one-register perturbation of the three admitted new source sets is rejected (iff criterion);
* the two instances (PR1062 and PR1188 words with the three frame-legal positive moves): literal
  COPY/ERASE boundary (x,y,h) -> (x,y+x,h) both directions, ordered per-register frame paths and
  exporter MOVE records identical to the base word, paid profile and rank mass, exporter bill,
  strict 104/192-bit precision guards, the unchanged owner checker's flag pattern, the twisted
  identities (T != I, C U' diag(I_x, T) = I, N = K' T, V = J = I), the chronological per-cut state difference
  and the first-climb census that isolates the newly used helper climb premise;
* seven controls that must fail or be rejected.
Standard library only.  Every check raises ValueError (never assert), so -O cannot weaken it.  The
pinned exporter uses assert, so it runs from its verified bytes in a child interpreter without -O.
"""
import argparse
import gzip
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import time
import types
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

WORDS = {
    'PR967': 'research/r439-helper-stars-seed19/candidate.json.gz',
    'PR1062': 'research/r439-bsection-stars-seed01/candidate.json.gz',
    'PR1122': 'research/r439-abc-star-composition/candidate.json.gz',
    'PR1188': 'research/r439-gl5-shortest/candidate.json.gz',
}
PR589 = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
INPUTS = sorted([*WORDS.values(), PR589, CHECKER, EXPORTER])

INSTANCES = {'PR1062': ('absorbed-pr1062.json.gz', 11500, 11497),
             'PR1188': ('absorbed-pr1188.json.gz', 10492, 10489)}
# (centre a, leaf b, absorbing A index, new source set of that A gate)
TRIPLES = [[506, 374, 288, [69]], [507, 355, 290, [72]], [514, 367, 304, [360]]]
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
OWNER_FALSE = ['H2_D_frame0_targets_from_helpers', 'H4_C_literal_reverse_at_full', 'K_equals_D', 'C_is_U_inverse']
LOCAL_CAP, NINE_CAP = 104, 192


def need(cond, msg):
    if not cond:
        raise ValueError(msg)


def canonical(w):
    return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ pinned inputs

def check_pin(path, data, pinned):
    need(sha(data) == pinned, 'source pin mismatch: ' + path)


def load_inputs():
    src = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    pins = {r['path']: r['sha256'] for r in src['files'] if r['usage'] == 'input'}
    need(sorted(pins) == INPUTS, 'SOURCES.json input set differs from the verifier inputs')
    man = json.loads((HERE / 'VERIFY.json').read_text(encoding='utf-8'))
    need(sorted(man['inputs']) == INPUTS, 'VERIFY.json input set differs from the verifier inputs')
    data = {}
    for p in INPUTS:
        b = (ROOT / p).read_bytes()
        check_pin(p, b, pins[p])
        data[p] = b
    return data, pins


def owner_module(code):
    mod = types.ModuleType('r439_owner_xcheck_p')
    mod.__file__ = CHECKER
    exec(compile(code, CHECKER, 'exec'), mod.__dict__)
    return mod


# ------------------------------------------------------------------ geometry

def rank_q(rows):
    m = [[Fraction(x) for x in r] for r in rows]
    rk = 0
    for col in range(len(m[0]) if m else 0):
        p = next((i for i in range(rk, len(m)) if m[i][col] != 0), None)
        if p is None:
            continue
        m[rk], m[p] = m[p], m[rk]
        for i in range(len(m)):
            if i != rk and m[i][col] != 0:
                f = m[i][col] / m[rk][col]
                m[i] = [a - f * b for a, b in zip(m[i], m[rk])]
        rk += 1
    return rk


class Geo:
    def __init__(self, w):
        self.v, self.R = w['v'], w['R']
        self.n = 2 * self.v + self.R
        self.fs = [frozenset(f) for f in w['frames']]
        self.fdim = [rank_q([w['lines'][i] for i in f]) if f else 0 for f in w['frames']]
        zero = [k for k, d in enumerate(self.fdim) if d == 0]
        full = [k for k, d in enumerate(self.fdim) if d == 8]
        need(len(zero) == 1 and len(full) == 1, 'one zero and one full frame')
        self.ZERO, self.FULL = zero[0], full[0]
        self.X = (1 << self.v) - 1
        self.Y = self.X << self.v
        self.H = ((1 << self.R) - 1) << (2 * self.v)

    def is_y(self, r):
        return self.v <= r < 2 * self.v


def same_geometry(a, b):
    return all(a[k] == b[k] for k in ('v', 'R', 'h', 'lines', 'frames', 'start', 'final', 'ret', 'scatter'))


def frame_paths(w, geo):
    fs = geo.fs
    ps = [[f] for f in w['start']]
    for sec in 'DABC':
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                if ps[r][-1] != f:
                    need(fs[ps[r][-1]] < fs[f], 'illegal frame move: register %d frame %d -> %d' % (r, ps[r][-1], f))
                    ps[r].append(f)
    for r, f in enumerate(w['final']):
        if ps[r][-1] != f:
            need(fs[ps[r][-1]] < fs[f], 'illegal final move: register %d' % r)
            ps[r].append(f)
    return ps


def copy_ranks(w, geo):
    cur = list(w['start'])
    for sec in 'DA':
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                cur[r] = f
    return [geo.fdim[cur[q]] for q in w['ret']]


def paid_profile(w, geo):
    prof = Counter(geo.fdim[b] - geo.fdim[a] for p in frame_paths(w, geo) for a, b in zip(p, p[1:]))
    prof.update(copy_ranks(w, geo))
    return {k: prof[k] for k in sorted(prof)}


# ------------------------------------------------------------------ literal F2 stream

def stream(w):
    v, tmp = w['v'], 2 * w['v'] + w['R']
    out = [(0, d, s) for sec in 'DA' for _, d, ss in w[sec] for s in ss]
    for j, centre in enumerate(w['ret']):
        out.append((1, tmp, centre))
        out += [(0, v + i, tmp) for i, row in enumerate(w['scatter']) if j in row]
        out.append((2, tmp, centre))
    out += [(0, d, s) for sec in 'BC' for _, d, ss in w[sec] for s in ss]
    return out


def literal(w, reverse=False, clean_helpers=False):
    """Set-valued (bitmask) replay of the literal ADD/COPY/ERASE stream on all formal columns."""
    v, n = w['v'], 2 * w['v'] + w['R']
    rows = [0 if clean_helpers and r >= 2 * v else 1 << r for r in range(n)] + [0]
    ins = stream(w)
    for kind, d, s in (reversed(ins) if reverse else ins):
        if reverse and kind:
            kind = 3 - kind
        if kind == 0:
            rows[d] ^= rows[s]
        elif kind == 1:
            need(not rows[d], 'COPY into a live temporary')
            rows[d] = rows[s]
        else:
            need(rows[d] == rows[s], 'ERASE of a changed copy')
            rows[d] = 0
    need(not rows[-1], 'temporary not erased')
    return rows[:-1]


def wanted(w, clean_helpers=False):
    v, n = w['v'], 2 * w['v'] + w['R']
    out = []
    for r in range(n):
        if v <= r < 2 * v:
            out.append((1 << r) | (1 << (r - v)))
        else:
            out.append(0 if clean_helpers and r >= 2 * v else 1 << r)
    return out


def boundary_ok(w):
    want = wanted(w)
    try:
        return all(literal(w, rev) == want for rev in (False, True))
    except ValueError:
        return False


def bounds(w):
    peaks = []
    ins = stream(w)
    for reverse in (False, True):
        val = [1] * (2 * w['v'] + w['R'] + 1)
        peak = 1
        for kind, d, s in (reversed(ins) if reverse else ins):
            if reverse and kind:
                kind = 3 - kind
            val[d] = val[d] + val[s] if kind == 0 else (val[s] if kind == 1 else 0)
            peak = max(peak, val[d])
        peaks.append(peak)
    F, B = peaks
    local, nine = 64 * F**3 * B**2, (1 << 18) * F**5 * B**4
    return dict(ADDs=sum(k == 0 for k, _, _ in ins), D_ADDs=sum(len(g[2]) for g in w['D']),
                A_ADDs=sum(len(g[2]) for g in w['A']), C_ADDs=sum(len(g[2]) for g in w['C']),
                F=F, B=B, local_bits=local.bit_length(), nine_stage_bits=nine.bit_length(),
                local_ok=local < 1 << LOCAL_CAP, nine_ok=nine < 1 << NINE_CAP)


def guards(b):
    need(b['local_ok'] and b['nine_ok'], 'precision guard')


def run_values(w, secs, start=None):
    v, n = w['v'], 2 * w['v'] + w['R']
    val = list(start) if start is not None else [1 << r for r in range(n)]
    for sec in secs:
        if sec == 'scatter':
            cp = [val[q] for q in w['ret']]
            for t, row in enumerate(w['scatter']):
                for j in row:
                    val[v + t] ^= cp[j]
        else:
            for f, d, ss in w[sec]:
                acc = 0
                for s in ss:
                    acc ^= val[s]
                val[d] ^= acc
    return val


def bits(x):
    out = []
    while x:
        low = x & -x
        out.append(low.bit_length() - 1)
        x ^= low
    return out


def f2_rank(rows):
    rows = [r for r in rows if r]
    rk = 0
    while rows:
        p = rows.pop()
        if not p:
            continue
        rk += 1
        low = p & -p
        rows = [r ^ p if r & low else r for r in rows]
        rows = [r for r in rows if r]
    return rk


# ------------------------------------------------------------------ helper-star structure and census

def stars(w, geo):
    v, H0, D = geo.v, 2 * geo.v, w['D']
    nh2 = sum(1 for g in D if g[1] >= H0)
    need(nh2 % 2 == 0, 'helper gate count')
    nh = nh2 // 2
    prep, rest, mid = D[:nh], D[len(D) - nh:], D[nh:len(D) - nh]
    need(all(g[0] == geo.ZERO and g[1] >= H0 and len(g[2]) == 1 and g[2][0] >= H0 for g in prep), 'star preparation shape')
    need(rest == prep[::-1], 'restorations are the reversed preparations')
    need(all(g[0] == geo.ZERO and geo.is_y(g[1]) and all(s >= v for s in g[2]) for g in mid), 'target block shape')
    centres = Counter(g[1] for g in prep)
    leaves = [g[2][0] for g in prep]
    need(len(set(leaves)) == nh and not set(leaves) & set(centres), 'leaves distinct and never centres')
    need(all(any(c in g[2] for g in mid) for c in centres), 'every centre is read by the target block')
    return nh, centres


def census(w, geo):
    v, n, D, A = geo.v, geo.n, w['D'], w['A']
    nh, centres = stars(w, geo)
    tail0 = len(D) - nh
    val = [1 << i for i in range(n)]
    icol = [1 << i for i in range(n)]   # columns of the inverse state matrix

    def apply(d, ss):
        for s in ss:
            val[d] ^= val[s]
            icol[s] ^= icol[d]

    def unique_set(delta):
        S = [j for j in range(n) if (icol[j] & delta).bit_count() & 1]
        acc = 0
        for j in S:
            acc ^= val[j]
        need(acc == delta, 'inverse state representation')
        return S

    for g in D[:tail0]:
        apply(g[1], g[2])
    edges, dtail = [], []
    by_centre = {}
    for i in range(tail0, len(D)):
        f, a, ss = D[i]
        by_centre.setdefault(a, []).append((i, ss[0]))
    for i in range(tail0, len(D)):
        f, a, ss = D[i]
        b = ss[0]
        need(val[b] == 1 << b, 'leaf holds its own input at its restoration')
        need(not any(a in D[j][2] for j in range(i + 1, len(D))), 'centre read later in the D tail')
        for e, b2 in by_centre[a]:
            if e != i:       # D-tail alternative writer: absorb restoration e into this restoration i
                S = unique_set(1 << b2)
                new = sorted(set(ss) ^ set(S))
                dtail.append((e, i, new, 1 + 1 - len(new)))
        edges.append((i, a, b, 1 << b))
        apply(a, ss)
    read, moves = {}, []
    for k, (f, d, ss) in enumerate(A):
        for i, a, b, delta in edges:
            if i in read:
                continue
            if a in ss:
                read[i] = 'A'
                continue
            if d == a:
                S = unique_set(delta)
                new = sorted(set(ss) ^ set(S))
                moves.append(dict(restoration=i, edge=[a, b], k=k, S=S, new=new, gain=1 + len(ss) - len(new),
                                  a_in_S=a in S))
        apply(d, ss)
    for i, a, b, _ in edges:
        if i not in read:
            need(a in w['ret'], 'centre never read before B')
            read[i] = 'scatter'
    return dict(nh=nh, centres=centres, edges=edges, read=read, moves=moves, dtail=dtail)


def edit(w, moves):
    """Delete each move's restoration and give its A gate the move's new source set."""
    dels = {m['restoration'] for m in moves}
    need(len(dels) == len(moves) and len({m['k'] for m in moves}) == len(moves), 'one move per edge and gate')
    out = dict(w)
    out['D'] = [g for i, g in enumerate(w['D']) if i not in dels]
    A = [list(g) for g in w['A']]
    for m in moves:
        f, d, ss = A[m['k']]
        need(d == m['edge'][0], 'move gate writes the centre')
        A[m['k']] = [f, d, list(m['new'])] if m['new'] else None
    out['A'] = [g for g in A if g is not None]
    return out


def classify(w2, geo, base_paths):
    try:
        ps = frame_paths(w2, geo)
    except ValueError:
        return 'frame_illegal'
    if ps != base_paths:
        return 'paths_changed'
    return 'frame_legal'


def census_report(name, w, geo, base_paths):
    c = census(w, geo)
    moves = c['moves']
    need(not any(m['a_in_S'] for m in moves), 'a centre in its own substitute set')
    boundary_pass = 0
    legal_by_gain = {}
    outcomes = Counter()
    admitted = []
    first_illegal = None
    for m in moves:
        w2 = edit(w, [m])
        need(boundary_ok(w2), '%s move %s at A[%d] breaks the boundary' % (name, m['edge'], m['k']))
        boundary_pass += 1
        cls = classify(w2, geo, base_paths)
        m['frame'] = cls
        row = legal_by_gain.setdefault(m['gain'], Counter())
        row[cls] += 1
        if m['gain'] > 0:
            if cls == 'frame_legal':
                b = bounds(w2)
                cls = 'admitted' if b['local_ok'] and b['nine_ok'] else 'guard_fail'
                if cls == 'admitted':
                    admitted.append(m)
            elif cls == 'frame_illegal' and first_illegal is None:
                first_illegal = m
            outcomes[cls] += 1
    # D-tail same-centre alternatives (the only other writers of a before its first read) never gain.
    for e, i, new, gain in c['dtail']:
        D = [list(g) for g in w['D']]
        D[i] = [D[i][0], D[i][1], new]
        need(gain == 0 and boundary_ok(dict(w, D=[g for j, g in enumerate(D) if j != e])), 'D-tail alternative')
    return c, dict(
        star_edges=len(c['edges']), centres=len(c['centres']),
        first_centre_read=dict(sorted(Counter(c['read'].values()).items())),
        A_writer_pairs=len(moves), edges_with_A_writer=len({m['restoration'] for m in moves}),
        gain_histogram={str(g): n for g, n in sorted(Counter(m['gain'] for m in moves).items())},
        substitute_size_histogram={str(s): n for s, n in sorted(Counter(len(m['S']) for m in moves).items())},
        frame_by_gain={str(g): dict(sorted(r.items())) for g, r in sorted(legal_by_gain.items())},
        dirty_boundary_preserved=boundary_pass,
        positive=sum(m['gain'] > 0 for m in moves), positive_outcomes=dict(sorted(outcomes.items())),
        admitted=[[m['edge'][0], m['edge'][1], m['k'], m['new']] for m in sorted(admitted, key=lambda m: m['edge'])],
        d_tail_same_centre_pairs=len(c['dtail']), d_tail_gains=sorted({x[3] for x in c['dtail']}),
        d_tail_dirty_boundary_preserved=len(c['dtail'])), admitted, first_illegal


# ------------------------------------------------------------------ twisted contract identities

def twisted(w, geo):
    v, n, R, H0 = geo.v, geo.n, geo.R, 2 * geo.v
    X, Y, H = geo.X, geo.Y, geo.H
    z = [r for r in range(n) if not geo.is_y(r)]
    out = {}
    out['D_frame_zero'] = all(g[0] == geo.ZERO for g in w['D'])
    out['D_source_free'] = all(g[1] >= v and all(s >= v for s in g[2]) for g in w['D'])
    out['D_no_target_feeds_helper'] = not any(g[1] >= H0 and any(geo.is_y(s) for s in g[2]) for g in w['D'])
    out['D_entry_frame_zero'] = all(w['start'][r] == geo.ZERO for r in range(v, n))
    Dm = run_values(w, ['D'])
    out['D_sources_identity'] = all(Dm[s] == 1 << s for s in range(v))
    out['T_helper_only'] = all(Dm[h] & ~H == 0 for h in range(H0, n))
    out['T_invertible'] = f2_rank([Dm[h] for h in range(H0, n)]) == R
    out['T_is_identity'] = all(Dm[h] == 1 << h for h in range(H0, n))
    out['T_offdiagonal'] = sorted([h, j] for h in range(H0, n) for j in bits(Dm[h] ^ (1 << h)))
    out['D_targets_y_plus_Nh'] = all(Dm[v + t] & ~H == 1 << (v + t) for t in range(v))
    N = [Dm[v + t] & H for t in range(v)]
    raw = run_values(w, ['A', 'scatter', 'B'])
    out['U_block_form'] = all(raw[r] & Y == 0 for r in z)
    out['V_identity'] = all(raw[v + t] & Y == 1 << (v + t) for t in range(v))
    out['J_identity'] = all(raw[v + t] & X == 1 << t for t in range(v))
    Kp = [raw[v + t] & H for t in range(v)]
    KpT = []
    for t in range(v):
        acc = 0
        for j in bits(Kp[t]):
            acc ^= Dm[j] & H
        KpT.append(acc)
    out['N_equals_KprimeT'] = N == KpT
    out['N_equals_Kprime'] = N == Kp
    out['C_full_frame_z_only'] = all(g[0] == geo.FULL and not geo.is_y(g[1]) and not any(geo.is_y(s) for s in g[2])
                                     for g in w['C'])
    after_C = run_values(w, ['C'], raw)
    out['C_Uprime_identity'] = all(after_C[r] == 1 << r for r in z)
    full = run_values(w, ['D', 'A', 'scatter', 'B', 'C'])
    out['C_Uprime_T_identity'] = all(full[r] == 1 << r for r in z)
    out['final_targets_y_plus_x'] = all(full[v + t] == (1 << (v + t)) | (1 << t) for t in range(v))
    out['N_targets_touched'] = sum(1 for t in range(v) if N[t])
    return out


TWISTED_REQUIRED = ['D_frame_zero', 'D_source_free', 'D_no_target_feeds_helper', 'D_entry_frame_zero',
                    'D_sources_identity', 'T_helper_only', 'T_invertible', 'D_targets_y_plus_Nh', 'U_block_form',
                    'V_identity', 'J_identity', 'N_equals_KprimeT', 'C_full_frame_z_only', 'C_Uprime_T_identity',
                    'final_targets_y_plus_x']


# ------------------------------------------------------------------ chronology

def per_cut(w0, w1, geo, moves):
    """Lockstep D/A replay of the base word w0 and absorbed word w1, with frames."""
    dels = {m['restoration']: m for m in moves}
    edits = {m['k']: m for m in moves}
    seq0 = [('D', i, g) for i, g in enumerate(w0['D'])] + [('A', k, g) for k, g in enumerate(w0['A'])]
    n = geo.n
    vals = [[1 << r for r in range(n)], [1 << r for r in range(n)]]
    curs = [list(w0['start']), list(w0['start'])]
    pending = {}
    cuts = diff_cuts = 0
    frames_equal = True
    maxpend = 0

    def gate(side, f, d, ss):
        for r in (d, *ss):
            if curs[side][r] != f:
                need(geo.fs[curs[side][r]] < geo.fs[f], 'per-cut frame climb')
                curs[side][r] = f
        acc = 0
        for s in ss:
            acc ^= vals[side][s]
        vals[side][d] ^= acc

    for sec, i, g in seq0:
        gate(0, *g)
        if sec == 'D' and i in dels:
            m = dels[i]
            pending[m['edge'][0]] = 1 << m['edge'][1]
        elif sec == 'A' and i in edits:
            m = edits[i]
            gate(1, g[0], g[1], m['new'])
            need(m['edge'][0] in pending, 'absorption before its restoration')
            del pending[m['edge'][0]]
        else:
            gate(1, *g)
        cuts += 1
        diff = {r: vals[0][r] ^ vals[1][r] for r in range(n) if vals[0][r] != vals[1][r]}
        need(diff == pending, 'state difference at a cut is not exactly the pending leaf columns')
        diff_cuts += bool(diff)
        maxpend = max(maxpend, len(diff))
        frames_equal &= curs[0] == curs[1]
        need(all(curs[1][c] == geo.ZERO for c in pending), 'a differing centre left the zero frame')
    need(not pending and vals[0] == vals[1], 'states equal after the last absorption')
    need(frames_equal, 'register frames identical at every cut')
    first_touch = all(min(k for k, g in enumerate(w1['A']) if m['edge'][0] in (g[1], *g[2])) == m['k'] for m in moves)
    need(first_touch, 'each absorbing gate is the first A gate touching its centre')
    return dict(cuts=cuts, cuts_with_difference=diff_cuts, max_registers_differing=maxpend,
                frames_identical_at_every_cut=frames_equal, differing_centres_stay_at_zero_frame=True,
                absorbing_gate_is_first_A_touch=first_touch)


def first_climbs(w, geo):
    """Helpers whose first climb out of the zero frame (in D/A) carries a value other than their own column."""
    n, H0 = geo.n, 2 * geo.v
    val = [1 << r for r in range(n)]
    cur = list(w['start'])
    seen = {}
    for sec in 'DA':
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                if cur[r] != f and r not in seen and cur[r] == geo.ZERO:
                    seen[r] = val[r]
                cur[r] = f
            acc = 0
            for s in ss:
                acc ^= val[s]
            val[d] ^= acc
    hel = [r for r in seen if r >= H0]
    return dict(helpers_climbing_from_zero=len(hel), non_own_value=sorted(r for r in hel if seen[r] != 1 << r),
                targets_climbing_in_D_or_A=sum(1 for r in seen if geo.is_y(r)))


# ------------------------------------------------------------------ owner checker and exporter

def owner_flags(own, w):
    try:
        _, _, _, hyp, con, _ = own.check(w)
    except own.Reject as e:
        raise ValueError('owner checker rejects: %s' % e)
    flags = {**hyp, **con}
    return flags


def exporter(code, w, work, name):
    d = work / name
    d.mkdir()
    (d / 'export_records.py').write_bytes(code)
    (d / 'word.json.gz').write_bytes(gzip.compress(canonical(w), mtime=0))
    env = {k: x for k, x in os.environ.items() if k != 'PYTHONOPTIMIZE'}
    subprocess.run([sys.executable, '-I', '-B', str(d / 'export_records.py'), str(d / 'word.json.gz'), str(d / 'rec')],
                   check=True, capture_output=True, text=True, env=env)
    raw = (d / 'rec/249-records.bin').read_bytes()
    need(len(raw) % 24 == 0, 'record alignment')
    rec = list(struct.iter_unpack('<6i', raw))
    peaks = []
    for reverse in (False, True):
        norm, peak, open_ = [1] * (2 * w['v'] + w['R'] + 1), 1, False
        for op, a, b, c, _, _ in (reversed(rec) if reverse else rec):
            if op == 0:
                continue
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                norm[a] += abs(c) * norm[b]
                peak = max(peak, norm[a])
            elif op == 2:
                need(not open_, 'nested copy')
                norm[b], open_ = norm[a], True
            elif op == 3:
                need(open_, 'erase without copy')
                norm[b], open_ = 0, False
            else:
                raise ValueError('record opcode')
        need(not open_, 'unclosed copy')
        peaks.append(peak)
    moves = {}
    for r in rec:
        if r[0] == 0:
            moves.setdefault(r[1], []).append((r[2], r[3], r[4]))
    prof = Counter(r[4] for r in rec if r[0] == 0)
    prof.update(r[5] for r in rec if r[0] == 2)
    return dict(records=len(rec), ADD=sum(r[0] == 1 for r in rec), COPY=sum(r[0] == 2 for r in rec),
                ERASE=sum(r[0] == 3 for r in rec), MOVE=sum(r[0] == 0 for r in rec),
                COPY_ranks=[r[5] for r in rec if r[0] == 2], F=peaks[0], B=peaks[1],
                payload_bits=(64 * peaks[0]**3 * peaks[1]**2).bit_length(),
                profile={k: prof[k] for k in sorted(prof)}, record_sha256=sha(raw)), moves


# ------------------------------------------------------------------ controls

def rejected(label, fn, out):
    try:
        detail = fn()
    except ValueError as e:
        out.append([label, str(e)[:120]])
        return
    raise ValueError('control accepted: %s (%s)' % (label, detail))


def controls(name, base, absorbed, moves, geo, own, p589, first_illegal, data, pins):
    out = []
    v = geo.v
    # 1. omit the restorations without the A edit: dirty endpoint fails, clean-helper endpoint passes.
    omit = dict(base, D=absorbed['D'])
    rows = literal(omit)
    bad = [r for r, (x, y) in enumerate(zip(rows, wanted(omit))) if x != y]
    need(literal(omit, clean_helpers=True) == wanted(omit, True), 'omit-only control: clean helpers must pass')
    kinds = Counter('source' if r < v else 'target' if r < 2 * v else 'helper' for r in bad)

    def omit_check():
        need(rows == wanted(omit), 'dirty endpoint wrong on %d registers %s; clean-helper endpoint passes'
             % (len(bad), dict(sorted(kinds.items()))))
    rejected('omit restorations without the A edit', omit_check, out)
    # 2. the A edit with the literal cleanup of the edited A (inherited literal H4 enforced).
    zg = [[geo.FULL, g[1], list(g[2])] for sec in 'AB' for g in absorbed[sec] if not geo.is_y(g[1])]
    lit = dict(absorbed, C=zg[::-1])
    rows2 = literal(lit)
    bad2 = [r for r, (x, y) in enumerate(zip(rows2, wanted(lit))) if x != y]
    need(bad2 == [m['edge'][0] for m in moves] and all(rows2[m['edge'][0]] == (1 << m['edge'][0]) | (1 << m['edge'][1])
                                                       for m in moves), 'literal-H4 control fails exactly on the centres')
    need(literal(lit, clean_helpers=True) == wanted(lit, True), 'literal-H4 control passes on clean helpers')

    def lit_check():
        need(rows2 == wanted(lit), 'dirty helpers %s end as centre+leaf; clean helpers pass' % bad2)
    rejected('A edit with the literal cleanup of the edited A', lit_check, out)
    rejected('A edit with literal cleanup, owner checker', lambda: owner_flags(own, lit), out)
    # 3. absorption after the first centre read.
    late = None
    for m in moves:
        a = m['edge'][0]
        first = next(k for k, g in enumerate(base['A']) if a in g[2])
        k = next((k for k, g in enumerate(base['A']) if k > first and g[1] == a), None)
        if k is not None:
            late = (m, k)
            break
    need(late is not None, 'a late writer exists')
    m, k = late
    # Same recipe at a writer after the first read: S represents the leaf column at that cut of the
    # base word, but the pending difference has already leaked through the read.
    ref = run_values(dict(base, A=base['A'][:k]), ['D', 'A'])
    S = solve_set(ref, 1 << m['edge'][1], geo.n)
    need(m['edge'][0] not in S, 'late control substitute avoids the centre')
    late_word = edit(base, [dict(m, k=k, new=sorted(set(base['A'][k][2]) ^ set(S)))])
    rejected('absorption after the first centre read (A[%d] for centre %d)' % (k, m['edge'][0]),
             lambda: need(boundary_ok(late_word), 'dirty boundary fails'), out)
    # 4. wrong substitute register.
    wrong = [dict(x) for x in moves]
    wrong[0]['new'] = sorted(moves[1]['new'])
    wrong_word = edit(base, wrong)
    rejected('wrong substitute register (%s instead of %s at A[%d])' % (wrong[0]['new'], moves[0]['new'], moves[0]['k']),
             lambda: need(boundary_ok(wrong_word), 'dirty boundary fails'), out)
    # 5. one frame-illegal substitution (its F2 boundary is exact; frames reject it).
    need(first_illegal is not None, 'a frame-illegal positive move exists')
    ill = edit(base, [first_illegal])
    need(boundary_ok(ill), 'frame-illegal control has an exact F2 boundary')
    rejected('frame-illegal substitution (centre %d, A[%d], new %s)' % (first_illegal['edge'][0], first_illegal['k'],
                                                                       first_illegal['new']),
             lambda: frame_paths(ill, geo), out)
    # 6. PR1194/PR1311-style splice: absorbed A/B/C with PR589's target-only D.
    rejected('splice absorbed A/B/C with PR589 D', lambda: owner_flags(own, dict(absorbed, D=p589['D'])), out)
    # 7. corrupted source pin.
    b = bytearray(data[WORDS[name]])
    b[len(b) // 2] ^= 1
    rejected('corrupted source pin', lambda: check_pin(WORDS[name], bytes(b), pins[WORDS[name]]), out)
    return out


def solve_set(val, target, n):
    """Unique register set whose current values sum to target (Gaussian elimination over F2)."""
    piv = {}
    for r in range(n):
        x, tag = val[r], 1 << r
        while x:
            low = x & -x
            if low not in piv:
                piv[low] = (x, tag)
                break
            px, pt = piv[low]
            x ^= px
            tag ^= pt
        need(x, 'state not invertible')
    x, tag = target, 0
    while x:
        low = x & -x
        px, pt = piv[low]
        x ^= px
        tag ^= pt
    return bits(tag)


# ------------------------------------------------------------------ instances

def perturbations(base, moves, geo):
    """Every one-register change of each admitted new source set breaks the dirty boundary."""
    tried = 0
    for idx, m in enumerate(moves):
        for r in range(geo.n):
            if r == m['edge'][0]:
                continue
            alt = [dict(x) for x in moves]
            alt[idx]['new'] = sorted(set(m['new']) ^ {r})
            need(not boundary_ok(edit(base, alt)), 'perturbed source set accepted: move %d register %d' % (idx, r))
            tried += 1
    return tried


def instance(name, base, admitted, geo, own, p589, code, work, first_illegal, data, pins):
    fname, adds0, adds1 = INSTANCES[name]
    moves = sorted(admitted, key=lambda m: m['k'])
    need([[m['edge'][0], m['edge'][1], m['k'], m['new']] for m in moves] == TRIPLES, name + ' admitted triples')
    centres = {m['edge'][0] for m in moves}
    need(not any(set(m['S']) & (centres - {m['edge'][0]}) for m in moves), 'joint substitutes avoid other centres')
    w = edit(base, moves)
    for k in base:
        if k not in ('A', 'D'):
            need(w[k] == base[k], '%s field %s changed' % (name, k))
    need(len(w['D']) == len(base['D']) - 3 and len(w['A']) == len(base['A']), name + ' edit shape')
    for rev in (False, True):
        need(literal(w, rev) == wanted(w), '%s boundary (%s)' % (name, 'reverse' if rev else 'forward'))
    ps0, ps1 = frame_paths(base, geo), frame_paths(w, geo)
    need(ps1 == ps0, name + ' ordered frame paths')
    need(same_geometry(p589, base) and frame_paths(p589, geo) == ps0, name + ' frame paths equal PR589')
    prof0, prof1 = paid_profile(base, geo), paid_profile(w, geo)
    need(prof0 == prof1 == PROFILE and sum(k * x for k, x in prof1.items()) == 5129, name + ' paid profile')
    b0, b1 = bounds(base), bounds(w)
    need(b0['ADDs'] == adds0 and b1['ADDs'] == adds1, name + ' ADD count')
    guards(b0)
    guards(b1)
    e0, mv0 = exporter(code, base, work, name + '-base')
    e1, mv1 = exporter(code, w, work, name + '-absorbed')
    for e, b in ((e0, b0), (e1, b1)):
        need(e['ADD'] == b['ADDs'] and e['COPY'] == e['ERASE'] == 9 and e['F'] == b['F'] and e['B'] == b['B'],
             name + ' exporter bill')
        need(e['profile'] == PROFILE, name + ' exporter profile')
    need(mv0 == mv1, name + ' ordered per-register MOVE records')
    f0, f1 = owner_flags(own, base), owner_flags(own, w)
    need([k for k, x in f0.items() if not x] == ['H2_D_frame0_targets_from_helpers', 'K_equals_D'], name + ' base owner')
    need([k for k, x in f1.items() if not x] == OWNER_FALSE, name + ' absorbed owner flags')
    bridge = owner_flags(own, dict(base, D=p589['D']))
    need(all(bridge.values()), name + ' PR1194-style original-D splice on the base word')
    need(run_values(base, ['D']) == run_values(p589, ['D']), name + ' base D operator equals PR589 D')
    t0, t1 = twisted(base, geo), twisted(w, geo)
    for t in (t0, t1):
        need(all(t[k] for k in TWISTED_REQUIRED), name + ' twisted contract')
    need(t0['T_is_identity'] and t0['C_Uprime_identity'] and t0['N_equals_Kprime'], name + ' base is the T = I case')
    need(not t1['T_is_identity'] and not t1['C_Uprime_identity'] and not t1['N_equals_Kprime']
         and t1['T_offdiagonal'] == sorted([m['edge'][0], m['edge'][1]] for m in moves), name + ' T != I exactly on the stars')
    chron = per_cut(base, w, geo, moves)
    fc0, fc1 = first_climbs(base, geo), first_climbs(w, geo)
    need(fc0['non_own_value'] == [] and fc1['non_own_value'] == sorted(centres), name + ' first-climb census')
    tried = perturbations(base, moves, geo)
    ctl = controls(name, base, w, moves, geo, own, p589, first_illegal, data, pins)
    return w, dict(
        payload=fname, payload_sha256=sha(canonical(w)), moves=TRIPLES,
        literal=dict(base=b0, absorbed=b1), exporter=dict(base=e0, absorbed=e1),
        profile=prof1, rank_mass=sum(k * x for k, x in prof1.items()),
        paths_registers=len(ps1), columns=geo.n, directions=2,
        owner=dict(base_false=[k for k, x in f0.items() if not x], absorbed_false=[k for k, x in f1.items() if not x],
                   absorbed_true=sum(1 for x in f1.values() if x), original_D_splice_all_true=True),
        twisted=dict(base=t0, absorbed=t1), chronology=chron, first_climbs=dict(base=fc0, absorbed=fc1),
        perturbations_rejected=tried, controls=ctl)


# ------------------------------------------------------------------ driver

def run(write=False):
    data, pins = load_inputs()
    words = {k: json.loads(gzip.decompress(data[p])) for k, p in WORDS.items()}
    p589 = json.loads(gzip.decompress(data[PR589]))
    own = owner_module(data[CHECKER])
    geo = Geo(p589)
    for k, w in words.items():
        need(same_geometry(w, p589), k + ' geometry differs from PR589')
    rep = dict(status='PASS_R439_TWISTED_STAR_ABSORPTION', inputs={p: pins[p] for p in INPUTS}, census={}, instances={})
    built = {}
    with tempfile.TemporaryDirectory(prefix='r439-twisted-') as tmp:
        work = Path(tmp)
        for name, w in words.items():
            ps = frame_paths(w, geo)
            _, summary, admitted, first_illegal = census_report(name, w, geo, ps)
            need(summary['admitted'] == TRIPLES, name + ': exactly the three frame-legal positive moves')
            need(set(summary['first_centre_read']) <= {'A', 'scatter'}, name + ': every centre is first read in A or the scatter')
            rep['census'][name] = summary
            if name in INSTANCES:
                built[name], rep['instances'][name] = instance(name, w, admitted, geo, own, p589, data[EXPORTER], work,
                                                               first_illegal, data, pins)
    rep['new_kappa_claim'] = False
    rep = json.loads(json.dumps(rep))
    if write:
        for name, w in built.items():
            (HERE / INSTANCES[name][0]).write_bytes(gzip.compress(canonical(w), mtime=0))
        (HERE / 'EXPECTED.json').write_text(json.dumps(rep, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    for name, w in built.items():
        committed = json.loads(gzip.decompress((HERE / INSTANCES[name][0]).read_bytes()))
        need(canonical(committed) == canonical(w), 'committed payload differs from the rebuilt word: ' + name)
    need(json.loads((HERE / 'EXPECTED.json').read_text(encoding='utf-8')) == rep, 'EXPECTED.json mismatch')
    return rep


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--write', action='store_true', help='regenerate EXPECTED.json and the absorbed payloads')
    a = ap.parse_args()
    t0 = time.perf_counter()
    rep = run(write=a.write)
    for name, c in rep['census'].items():
        print('census %-6s star_edges=%d A_writer_pairs=%d gains=%s positive=%d outcomes=%s admitted=%d' % (
            name, c['star_edges'], c['A_writer_pairs'], json.dumps(c['gain_histogram'], separators=(',', ':')),
            c['positive'], json.dumps(c['positive_outcomes'], separators=(',', ':')), len(c['admitted'])))
    for name, x in rep['instances'].items():
        b0, b1 = x['literal']['base'], x['literal']['absorbed']
        print('instance %-6s ADDs %d -> %d  F/B %d/%d -> %d/%d  bits %d/%d -> %d/%d  profile %s mass %d  owner_false=%s  '
              'controls=%d perturbations=%d' % (
                  name, b0['ADDs'], b1['ADDs'], b0['F'], b0['B'], b1['F'], b1['B'], b0['local_bits'],
                  b0['nine_stage_bits'], b1['local_bits'], b1['nine_stage_bits'],
                  json.dumps(x['profile'], separators=(',', ':')), x['rank_mass'], ','.join(x['owner']['absorbed_false']),
                  len(x['controls']), x['perturbations_rejected']))
        for label, why in x['controls']:
            print('  control rejected: %s -- %s' % (label, why))
    print('PASS_R439_TWISTED_STAR_ABSORPTION words=%d instances=%d ADDs 11500->11497 10492->10489 columns=661 '
          'controls=%d no_new_kappa (%.1f s)' % (len(rep['census']), len(rep['instances']),
                                                 sum(len(x['controls']) for x in rep['instances'].values()),
                                                 time.perf_counter() - t0))


if __name__ == '__main__':
    main()
