#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Deferred target basis on fixed R439 bit words (H5-tw): exact finite verification.

Every PR915-lineage word runs, in D, a 306-gate target-basis preparation E, the helper reads, and the
literal undo E^-1.  The deferred word deletes the undo from D, lists the scatter in the target basis
(rows of E S) and runs the same undo gates, at the zero frame, as the first gates of B.  This replaces
H5 (V = I) together with the H2 target clause (R = I) by V R = I, with V N = K' T and J = I.

Checks, from SHA-256 and git-blob pinned repository inputs only:
* census on every committed lineage word (as of base c6765481): D layout, literal undo = reversed
  preparation at the zero frame, ADD saving, literal COPY/ERASE boundary (x,y,h) -> (x,y+x,h) on all 661
  dirty columns forward and reverse, identical ordered per-register frame paths, paid profile from frames
  and from the pinned exporter, exporter bill and MOVE records, both precision guards from the exporter's
  F/B, the unchanged owner checker (exactly H5_V_identity newly false), the H5-tw identities (V R = I,
  V N = K' T, J = I, R = E, V = E^-1), the per-cut bridge (the deferred word's own D, A and B prefix are
  replayed; its targets differ only by the tracked twist, at the zero frame, unread, until the undo) and
  the maximality census (fixed frame paths; B means the base word's B, which is the deferred word's B
  after the deferred undo);
* the order-ideal refinement: an exhaustive search over order ideals (commutation-closed down-sets) of the
  undo's dependency poset up to a fixed size, a greedy descent, and the best split found, fully checked on
  four words (found by search, not optimal);
* the PR1062 and PR1188 instances rebuilt and compared with the committed payloads;
* the PR589 selected-word heuristic (minimum-spanning-tree scatter basis G), with the same checks;
* controls that must fail or be rejected (each check-level control must fail for its intended reason),
  and an honest reorder census.
Standard library only.  Every check raises ValueError (never assert), so -O cannot weaken it.  The
pinned exporter uses assert, so it runs from its verified bytes in a child interpreter without -O.
`--census-scan` (optional, needs git) lists every committed R439 word under research/ and reports any word
missing from LINEAGE/OUTSIDE.
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

# Every distinct committed PR915-lineage R439 word at base c6765481 (duplicate vendor copies omitted).
LINEAGE = [
    ('PR915', 'research/r439-target-compensation/candidate.json.gz'),
    ('PR926', 'research/r439-two-sided-compensation/candidate.json.gz'),
    ('PR941', 'research/r439-helper-matching/candidate.json.gz'),
    ('PR941-floor', 'research/r439-helper-matching/floor-word.json.gz'),
    ('PR965', 'research/r439-helper-triples/candidate.json.gz'),
    ('PR967', 'research/r439-helper-stars-seed19/candidate.json.gz'),
    ('PR1040', 'research/r439-target-retune-seed14/candidate.json.gz'),
    ('PR1047', 'research/r439-post-helper-shear-seed03/candidate.json.gz'),
    ('PR1062', 'research/r439-bsection-stars-seed01/candidate.json.gz'),
    ('PR1062-composition', 'research/r439-bsection-stars-seed01/composition.json.gz'),
    ('PR1062-pair-control', 'research/r439-bsection-stars-seed01/pair_control.json.gz'),
    ('PR1122', 'research/r439-abc-star-composition/candidate.json.gz'),
    ('PR1188', 'research/r439-gl5-shortest/candidate.json.gz'),
    ('PR1208', 'research/r439-abc-zrewrite-seed16/CANDIDATE-WORD.json'),
    ('PR1449', 'research/r439-neutral-mixed-shears-seed13/candidate.json.gz'),
    ('PR1543', 'research/r439-neutral-helper-chain-seed17/CANDIDATE.json.gz'),
    ('PR1709', 'research/r439-five-cycle-seed9f01/CANDIDATE.json.gz'),
    ('PR1868-1062', 'research/r439-twisted-star-absorption-seed02/absorbed-pr1062.json.gz'),
    ('PR1868-1188', 'research/r439-twisted-star-absorption-seed02/absorbed-pr1188.json.gz'),
]
PR589 = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
# Committed R439 words outside the lineage: D is the 111 helper reads only (no target basis, R = I).
OUTSIDE = [
    ('PR555', 'research/e8-bit-p111/data/bitE8mut-p111.json.gz'),
    ('PR589', PR589),
    ('PR904', 'research/r439-four-wire-prefix/candidate.json.gz'),
    ('PR936', 'research/r439-five-wire-prefix/candidate.json.gz'),
    ('PR952', 'research/r439-six-wire-boolean/candidate.json.gz'),
    ('PR980', 'research/r439-global-prefix-admission/candidate.json.gz'),
    ('PR1127', 'research/r439-z3to2-seed13/CANDIDATE-WORD.json'),
    ('PR1221', 'research/r439-b509-boolean-seed05/candidate.json.gz'),
]
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
EXPORTER = 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
INPUTS = sorted({p for _, p in LINEAGE + OUTSIDE} | {CHECKER, EXPORTER})

INSTANCES = {'PR1062': 'candidate-1062.json.gz', 'PR1188': 'candidate-1188.json.gz'}
# Probe table: complete local ADDs (base, deferred) and B/guard bits from the unpublished exploratory probe,
# required to reproduce; every other number is pinned in EXPECTED.json.
PROBE = {'PR915': (13208, 12778), 'PR967': (11783, 11353), 'PR1062': (11500, 11070), 'PR1122': (10652, 10222),
         'PR1188': (10492, 10062), 'PR1208': (10542, 10112), 'PR1543': (11489, 11059),
         'PR1868-1188': (10489, 10059)}
PROBE_B = {'PR1062': (5911840, 5024524, (95, 182), (95, 181)), 'PR1188': (3758418, 2825146, (91, 175), (91, 173))}
# Order-ideal refinement: exhaustive search bound, and the words on which the best split found is fully checked,
# with the complete local ADDs reported by the pre-PR proof review (required to reproduce).
IDEAL_MAX = 4
IDEAL_REVIEW = {'PR1062': 11067, 'PR1188': 10059, 'PR1040': 11345, 'PR1868-1188': 10056}
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
RANK_MASS = 5129
LOCAL_CAP, NINE_CAP = 104, 192
OWNER_KEYS = ['H1_no_target_feeds_z', 'H2_D_frame0_targets_from_helpers', 'H3_A_z_only_scatter_targets_B_split',
              'H4_C_literal_reverse_at_full', 'H5_V_identity', 'U_block_form', 'J_identity', 'K_equals_D',
              'C_is_U_inverse']


def need(cond, msg):
    if not cond:
        raise ValueError(msg)


def canonical(w):
    return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git_blob(b):
    return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()


# ------------------------------------------------------------------ pinned inputs

def check_pin(path, data, pin):
    need(sha(data) == pin['sha256'], 'source pin mismatch (sha256): ' + path)
    need(git_blob(data) == pin['git_blob'], 'source pin mismatch (git blob): ' + path)


def load_inputs():
    src = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    pins = {r['path']: r for r in src['files'] if r['usage'] == 'input'}
    need(sorted(pins) == INPUTS, 'SOURCES.json input set differs from the verifier inputs')
    man = json.loads((HERE / 'VERIFY.json').read_text(encoding='utf-8'))
    need(sorted(man['inputs']) == INPUTS, 'VERIFY.json input set differs from the verifier inputs')
    data = {}
    for p in INPUTS:
        b = (ROOT / p).read_bytes()
        check_pin(p, b, pins[p])
        data[p] = b
    return data, pins


def parse_word(path, b):
    return json.loads(gzip.decompress(b) if path.endswith('.gz') else b)


def owner_module(code):
    mod = types.ModuleType('r439_owner_xcheck_p')
    mod.__file__ = CHECKER
    exec(compile(code, CHECKER, 'exec'), mod.__dict__)
    return mod


# ------------------------------------------------------------------ geometry (adapted from PR1868's verify.py)

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
        self.I = [1 << a for a in range(self.v)]

    def is_y(self, r):
        return self.v <= r < 2 * self.v


def same_geometry(a, b):
    return all(a[k] == b[k] for k in ('v', 'R', 'h', 'lines', 'frames', 'start', 'final', 'ret'))


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


def paid_profile(w, geo, ps=None):
    ps = frame_paths(w, geo) if ps is None else ps
    prof = Counter(geo.fdim[b] - geo.fdim[a] for p in ps for a, b in zip(p, p[1:]))
    prof.update(copy_ranks(w, geo))
    return {k: prof[k] for k in sorted(prof)}


# ------------------------------------------------------------------ literal F2 stream (adapted from PR1868)

def stream(w):
    v, tmp = w['v'], 2 * w['v'] + w['R']
    out = [(0, d, s) for sec in 'DA' for _, d, ss in w[sec] for s in ss]
    for j, centre in enumerate(w['ret']):
        out.append((1, tmp, centre))
        out += [(0, v + i, tmp) for i, row in enumerate(w['scatter']) if j in row]
        out.append((2, tmp, centre))
    out += [(0, d, s) for sec in 'BC' for _, d, ss in w[sec] for s in ss]
    return out


def literal(w, reverse=False):
    """Set-valued (bitmask) replay of the literal ADD/COPY/ERASE stream on all formal columns."""
    n = 2 * w['v'] + w['R']
    rows = [1 << r for r in range(n)] + [0]
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


def wanted(w):
    v, n = w['v'], 2 * w['v'] + w['R']
    return [(1 << r) | (1 << (r - v)) if v <= r < 2 * v else 1 << r for r in range(n)]


def boundary_bad(w, reverse=False):
    """Registers whose literal endpoint differs from (x, y + x, h); None if the stream itself is rejected."""
    try:
        rows = literal(w, reverse)
    except ValueError:
        return None
    return [r for r, (a, b) in enumerate(zip(rows, wanted(w))) if a != b]


def boundary_ok(w):
    return all(boundary_bad(w, rev) == [] for rev in (False, True))


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
    return dict(ADDs=sum(k == 0 for k, _, _ in ins), D_ADDs=sum(len(g[2]) for g in w['D']),
                A_ADDs=sum(len(g[2]) for g in w['A']), scatter_ADDs=sum(len(r) for r in w['scatter']),
                B_ADDs=sum(len(g[2]) for g in w['B']), C_ADDs=sum(len(g[2]) for g in w['C']), F=F, B=B)


def guard_bits(F, B):
    local, nine = 64 * F**3 * B**2, (1 << 18) * F**5 * B**4
    return dict(local_bits=local.bit_length(), nine_stage_bits=nine.bit_length(),
                local_ok=local < 1 << LOCAL_CAP, nine_ok=nine < 1 << NINE_CAP)


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
        rk += 1
        low = p & -p
        rows = [r ^ p if r & low else r for r in rows]
        rows = [r for r in rows if r]
    return rk


# ------------------------------------------------------------------ target-basis algebra

def tmat(gates, v, start=None):
    """Rows over target indices: after the target-only gates, target a holds the sum of targets in row a."""
    M = list(start) if start is not None else [1 << a for a in range(v)]
    for _, d, ss in gates:
        acc = 0
        for s in ss:
            acc ^= M[s - v]
        M[d - v] ^= acc
    return M


def mul(A, B):
    out = []
    for row in A:
        acc = 0
        for b in bits(row):
            acc ^= B[b]
        out.append(acc)
    return out


def scatter_rows(w):
    return [sum(1 << j for j in row) for row in w['scatter']]


def listing(rows, nret):
    return [[j for j in range(nret) if r >> j & 1] for r in rows]


def gate_kind(geo, g):
    _, d, ss = g
    H0 = 2 * geo.v
    if geo.is_y(d):
        if all(geo.is_y(s) for s in ss):
            return 'yy'
        if all(s >= H0 for s in ss):
            return 'yh'
        return 'y-mixed'
    if d >= H0 and all(s >= H0 for s in ss):
        return 'hh'
    return 'z-other'


def d_runs(geo, D):
    out = []
    for g in D:
        k = gate_kind(geo, g)
        if out and out[-1][0] == k:
            out[-1][1] += 1
        else:
            out.append([k, 1])
    return out


def split_d(w, geo):
    """Partition D into target-basis preparation, helper reads and literal undo (target gates only)."""
    D = w['D']
    ks = [gate_kind(geo, g) for g in D]
    need(all(k in ('yy', 'yh', 'hh') for k in ks), 'D has a gate outside target<-target, target<-helper, helper<-helper')
    need(all(g[0] == geo.ZERO for g in D), 'D gate off the zero frame')
    reads = [i for i, k in enumerate(ks) if k == 'yh']
    need(reads, 'D has no helper reads')
    lo, hi = reads[0], reads[-1]
    need(all(ks[i] != 'yy' for i in range(lo, hi + 1)), 'a target<-target gate sits among the reads')
    prep = [i for i in range(lo) if ks[i] == 'yy']
    undo = [i for i in range(hi + 1, len(D)) if ks[i] == 'yy']
    return dict(prep=prep, reads=reads, undo=undo,
                helper_gates=sum(1 for k in ks if k == 'hh'), runs=d_runs(geo, D))


def defer(w, geo, sp):
    """Delete the undo from D, list the scatter as rows of E S, and run the undo first in B."""
    v, D = geo.v, w['D']
    E = tmat([D[i] for i in sp['prep']], v)
    ES = mul(E, scatter_rows(w))
    und = set(sp['undo'])
    w2 = dict(w)
    w2['D'] = [list(g) for i, g in enumerate(D) if i not in und]
    w2['scatter'] = listing(ES, len(w['ret']))
    w2['B'] = [list(D[i]) for i in sp['undo']] + [list(g) for g in w['B']]
    return w2, E, ES


# ------------------------------------------------------------------ H5-tw identities

def h5tw(w, geo):
    """Block form of D and of the raw word W0' = (A, scatter, B), and the H5-tw equations."""
    v, n, H0 = geo.v, geo.n, 2 * geo.v
    z = [r for r in range(n) if not geo.is_y(r)]
    Dm = run_values(w, ['D'])
    R = [(Dm[v + a] & geo.Y) >> v for a in range(v)]
    N = [Dm[v + a] & geo.H for a in range(v)]
    T = [Dm[h] & geo.H for h in range(H0, n)]
    raw = run_values(w, ['A', 'scatter', 'B'])
    V = [(raw[v + a] & geo.Y) >> v for a in range(v)]
    Kp = [raw[v + a] & geo.H for a in range(v)]
    VN = mul(V, N)
    KpT = []
    for a in range(v):
        acc = 0
        for j in bits(Kp[a]):
            acc ^= Dm[j] & geo.H
        KpT.append(acc)
    full = run_values(w, ['D', 'A', 'scatter', 'B', 'C'])
    out = dict(
        D_frame_zero=all(g[0] == geo.ZERO for g in w['D']),
        D_source_free=all(g[1] >= v and all(s >= v for s in g[2]) for g in w['D']),
        D_sources_identity=all(Dm[s] == 1 << s for s in range(v)),
        D_targets_no_source_column=all(Dm[v + a] & geo.X == 0 for a in range(v)),
        T_helper_only=all(Dm[h] & ~geo.H == 0 for h in range(H0, n)),
        T_invertible=f2_rank(T) == geo.R,
        T_is_identity=all(Dm[h] == 1 << h for h in range(H0, n)),
        R_invertible=f2_rank(R) == v,
        R_is_identity=R == geo.I,
        U_block_form=all(raw[r] & geo.Y == 0 for r in z),
        V_is_identity=V == geo.I,
        VR_identity=mul(V, R) == geo.I,
        J_identity=all(raw[v + a] & geo.X == 1 << a for a in range(v)),
        VN_equals_KprimeT=VN == KpT,
        C_full_frame_z_only=all(g[0] == geo.FULL and not geo.is_y(g[1]) and not any(geo.is_y(s) for s in g[2])
                                for g in w['C']),
        C_Uprime_T_identity=all(full[r] == 1 << r for r in z),
        final_targets_y_plus_x=all(full[v + a] == (1 << (v + a)) | (1 << a) for a in range(v)),
        R_offdiagonal_ones=sum(len(bits(R[a] & ~(1 << a))) for a in range(v)),
        V_offdiagonal_ones=sum(len(bits(V[a] & ~(1 << a))) for a in range(v)),
    )
    return out, R, V


H5TW_REQUIRED = ['D_frame_zero', 'D_source_free', 'D_sources_identity', 'D_targets_no_source_column', 'T_helper_only',
                 'T_invertible', 'R_invertible', 'U_block_form', 'VR_identity', 'J_identity', 'VN_equals_KprimeT',
                 'C_full_frame_z_only', 'C_Uprime_T_identity', 'final_targets_y_plus_x']
EQUATIONS = ['VR_identity', 'J_identity', 'VN_equals_KprimeT', 'C_Uprime_T_identity']


def failed_equations(w, geo):
    t, _, _ = h5tw(w, geo)
    return [k for k in EQUATIONS if not t[k]]


# ------------------------------------------------------------------ per-cut bridge

def bridge(w, w2, geo, steps_d, twist_b, twist):
    """Lockstep replay, with frames, of the original word w and the deferred word w2 up to the undo.

    steps_d: D steps ('both' | 'W' | 'W2', gate); twist_b: the gates w2 runs first in B.  Invariant at every
    cut: all non-target registers agree in value and frame, every target sits at the zero frame in both
    words, and w2's targets equal M times w's targets for the tracked basis M.  The deferred side is the
    deferred word itself: its D and A must equal the replayed steps and its B prefix the replayed twist_b."""
    v, n = geo.v, geo.n
    need(w2['D'] == [list(g) for who, g in steps_d if who in ('both', 'W2')] and w2['A'] == w['A'],
         'bridge: the deferred word D/A differ from the replayed steps')
    need(w['D'] == [list(g) for who, g in steps_d if who in ('both', 'W')],
         'bridge: the original word D differs from the replayed steps')
    need(w2['B'][:len(twist_b)] == [list(g) for g in twist_b], 'bridge: the deferred B prefix differs from the replayed undo')
    vals = [[1 << r for r in range(n)], [1 << r for r in range(n)]]
    curs = [list(w['start']), list(w['start'])]
    M = list(geo.I)
    st = dict(cuts=0, cuts_with_target_difference=0, max_targets_differing=0, z_reads_of_targets_in_window=0)
    now = [0]                   # targets differing at the current cut (only target steps change it)

    def cut():
        st['cuts'] += 1
        st['cuts_with_target_difference'] += now[0] > 0

    def gate(side, f, d, ss):
        for r in (d, *ss):
            if curs[side][r] != f:
                need(geo.fs[curs[side][r]] < geo.fs[f], 'bridge: frame descent')
                curs[side][r] = f
        acc = 0
        for s in ss:
            acc ^= vals[side][s]
        vals[side][d] ^= acc

    def check_targets():
        diff = 0
        for a in range(v):
            acc = 0
            for b in bits(M[a]):
                acc ^= vals[0][v + b]
            need(acc == vals[1][v + a], 'bridge: target %d is not the tracked twist of the original' % a)
            diff += vals[0][v + a] != vals[1][v + a]
        need(all(curs[i][v + a] == geo.ZERO for i in (0, 1) for a in range(v)), 'bridge: a target left the zero frame')
        now[0] = diff
        st['max_targets_differing'] = max(st['max_targets_differing'], diff)

    def check_z(regs):
        for r in regs:
            need(curs[0][r] == curs[1][r], 'bridge: register %d frames differ' % r)
            if not geo.is_y(r):
                need(vals[0][r] == vals[1][r], 'bridge: z register %d differs' % r)

    def twist_col(g):           # w alone runs g: M <- M G
        _, d, ss = g
        for a in range(v):
            if M[a] >> (d - v) & 1:
                for s in ss:
                    M[a] ^= 1 << (s - v)

    def twist_row(g):           # w2 alone runs g: M <- G M
        _, d, ss = g
        for s in ss:
            M[d - v] ^= M[s - v]

    for who, g in steps_d:
        if who in ('both', 'W'):
            gate(0, *g)
        if who in ('both', 'W2'):
            gate(1, *g)
        if who == 'W':
            twist_col(g)
        elif who == 'W2':
            twist_row(g)
        if who != 'both' or geo.is_y(g[1]):
            check_targets()
        else:
            check_z((g[1], *g[2]))
        cut()
    need(M == twist, 'bridge: after D the twist is not the expected target basis')
    for g in w['A']:
        need(not geo.is_y(g[1]), 'bridge: A writes a target')
        st['z_reads_of_targets_in_window'] += sum(1 for s in g[2] if geo.is_y(s))
        gate(0, *g)
        gate(1, *g)
        check_z((g[1], *g[2]))
        cut()
    need(st['z_reads_of_targets_in_window'] == 0, 'bridge: a z gate reads a twisted target')
    need(all(vals[0][r] == vals[1][r] and curs[0][r] == curs[1][r] for r in range(n) if not geo.is_y(r)),
         'bridge: z state differs after A')
    # No separate listing check here: a listing other than M S breaks the per-cut invariant at a COPY block.
    S0, S1 = scatter_rows(w), scatter_rows(w2)
    for j, q in enumerate(w['ret']):
        need(vals[0][q] == vals[1][q] and curs[0][q] == curs[1][q], 'bridge: COPY source differs')
        for side, rows in ((0, S0), (1, S1)):
            for a in range(v):
                if rows[a] >> j & 1:
                    vals[side][v + a] ^= vals[side][q]
        check_targets()
        cut()
    for g in twist_b:
        gate(1, *g)
        twist_row(g)
        check_targets()
        cut()
    need(M == geo.I, 'bridge: the twist is not undone')
    need(vals[0] == vals[1] and curs[0] == curs[1], 'bridge: states differ at the start of the common B')
    need(w['B'] == w2['B'][len(twist_b):] and w['C'] == w2['C'], 'bridge: B/C suffix differs')
    st['states_equal_after_undo'] = True
    return st


# ------------------------------------------------------------------ maximality census

def maximality(w, w2, geo, undo, E):
    """Fixed-frame-path census: where the undo may sit and whether B can absorb it.  Here B is w's B, which is
    w2's B after the deferred undo."""
    v, fs = geo.v, geo.fs
    ps = frame_paths(w2, geo)
    tpath = [set(ps[v + a]) - {geo.ZERO} for a in range(v)]
    sharing = sum(1 for a in range(v) for b in range(a + 1, v) if tpath[a] & tpath[b])
    Bt = [(k, g) for k, g in enumerate(w['B']) if geo.is_y(g[1])]
    target_reading = sum(1 for _, g in Bt if any(geo.is_y(s) for s in g[2]))
    zero_writes = sum(1 for _, g in Bt if g[0] == geo.ZERO)
    vb = run_values(w, ['B'])
    confined = all(vb[v + a] & geo.Y == 1 << (v + a) for a in range(v))
    first = {}
    for k, (f, d, ss) in enumerate(w['B']):
        for r in (d, *ss):
            if geo.is_y(r) and r not in first:
                first[r] = (k, f)
    need(len(first) == v, 'every target is touched in B')
    first_climbs = all(f != geo.ZERO for _, f in first.values())
    operands = sorted({r - v for g in undo for r in (g[1], *g[2])})
    latest = [min(first[r][0] for r in (g[1], *g[2])) for g in undo]
    # single-edge absorption into a B target write: undo gate t ^= s against a B gate writing t at frame f;
    # compensating it there needs s at frame f, i.e. f on s's fixed path.
    pairs = legal = 0
    for g in undo:
        t = g[1]
        for _, (f, d, ss) in Bt:
            if d == t:
                pairs += 1
                legal += all(f in ps[s] for s in g[2])
    # any target sharing the frame of a B target write on its fixed path
    shared_write_frames = sum(1 for _, (f, d, _) in Bt if any(f in tpath[b] for b in range(v) if v + b != d))
    # Relaxed paths (scope limit, not a maximality claim): for each B target write at frame f, count the other
    # targets that could be co-located at f if paths may change, under three criteria of decreasing looseness:
    # loose = the target's final frame contains f (an upper bound); current = also its frame at that moment lies
    # inside f; monotone = f fits monotonically between its own earlier and later fixed touches (and its final).
    cur = list(w['start'])
    for sec in 'DA':
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                cur[r] = f
    touches = {v + b: [] for b in range(v)}
    for k, (f, d, ss) in enumerate(w['B']):
        for r in (d, *ss):
            if geo.is_y(r):
                touches[r].append((k, f))
    relaxed = {'loose': Counter(), 'current': Counter(), 'monotone': Counter()}
    for k, (f, d, ss) in enumerate(w['B']):
        if geo.is_y(d):
            cnt = Counter()
            for b in range(v):
                r = v + b
                if r == d or not fs[f] <= fs[w['final'][r]]:
                    continue
                cnt['loose'] += 1
                cnt['current'] += fs[cur[r]] <= fs[f]
                cnt['monotone'] += (all(fs[x] <= fs[f] for kk, x in touches[r] if kk < k)
                                    and all(fs[f] <= fs[x] for kk, x in touches[r] if kk > k))
            for key in relaxed:
                relaxed[key][cnt[key]] += 1
        for r in (d, *ss):
            cur[r] = f
    relaxed_report = {key: dict(writes_with_a_partner=sum(c for x, c in cnt.items() if x), max_partners=max(cnt))
                      for key, cnt in relaxed.items()}
    # prefix-split census: keep the first k undo gates (literal order) in D, defer the rest; scatter cost nnz(E_k S)
    S = scatter_rows(w)
    ES = mul(E, S)
    Ek = list(E)
    costs = [sum(len(bits(r)) for r in ES)]
    same_listing = [True]
    for g in undo:
        Ek = tmat([g], v, Ek)
        P = mul(Ek, S)
        costs.append(sum(len(bits(r)) for r in P))
        same_listing.append(P == ES)
    need(Ek == geo.I, 'the undo inverts E')
    best = min(costs)
    nret = len(w['ret'])
    listing_kept = next((k for k, x in enumerate(same_listing) if not x), len(costs)) - 1
    cost_kept = next((k for k, c in enumerate(costs) if c != costs[0]), len(costs)) - 1
    col_old = [sum(1 for a in range(v) if S[a] >> j & 1) for j in range(nret)]
    col_new = [sum(1 for a in range(v) if ES[a] >> j & 1) for j in range(nret)]
    return dict(
        target_nonzero_frame_sets_pairwise_disjoint=sharing == 0, target_pairs_sharing_a_nonzero_frame=sharing,
        B_target_writes=len(Bt), B_target_writes_reading_targets=target_reading, B_target_writes_at_zero=zero_writes,
        B_target_block_identity=confined, first_B_touch_of_every_target_climbs=first_climbs,
        first_B_target_climb_index=min(k for k, _ in first.values()),
        undo_operands=len(operands), undo_latest_B_index_min=min(latest), undo_latest_B_index_max=max(latest),
        absorption_pairs=pairs, absorption_pairs_frame_legal=legal,
        B_target_write_frames_shared_by_another_target_path=shared_write_frames,
        relaxed_paths=relaxed_report,
        prefix_split_cost_full_deferral=costs[0], prefix_split_cost_no_deferral=costs[-1], prefix_split_cost_min=best,
        prefix_split_argmin=[k for k, c in enumerate(costs) if c == best], prefix_split_points=len(costs),
        prefix_split_listing_unchanged_for_first_gates=listing_kept, prefix_split_cost_unchanged_for_first_gates=cost_kept,
        scatter_column_ones_old=col_old, scatter_column_ones_new=col_new,
        per_column_choice_total=sum(min(a, b) for a, b in zip(col_old, col_new)))


def require_maximality(mx, name):
    need(mx['target_nonzero_frame_sets_pairwise_disjoint'] and mx['B_target_writes_reading_targets'] == 0
         and mx['B_target_writes_at_zero'] == 0 and mx['B_target_block_identity']
         and mx['first_B_touch_of_every_target_climbs'] and mx['absorption_pairs_frame_legal'] == 0
         and mx['B_target_write_frames_shared_by_another_target_path'] == 0, name + ': maximality census')
    need(mx['prefix_split_argmin'][0] == 0, name + ': full deferral is not a best prefix split')


# ------------------------------------------------------------------ owner checker and exporter

def owner_flags(own, w):
    try:
        _, _, _, hyp, con, _ = own.check(w)
    except own.Reject as e:
        raise ValueError('owner checker rejects: %s' % e)
    flags = {**hyp, **con}
    need(list(flags) == OWNER_KEYS, 'owner checker flag set changed')
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
    out = dict(records=len(rec), ADD=sum(r[0] == 1 for r in rec), COPY=sum(r[0] == 2 for r in rec),
               ERASE=sum(r[0] == 3 for r in rec), MOVE=sum(r[0] == 0 for r in rec),
               COPY_ranks=[r[5] for r in rec if r[0] == 2], F=peaks[0], B=peaks[1],
               profile={k: prof[k] for k in sorted(prof)}, rank_mass=sum(k * x for k, x in prof.items()),
               record_sha256=sha(raw))
    out.update(guard_bits(out['F'], out['B']))
    return out, moves


def rejected(label, fn, out, why=None):
    """A control must be rejected; with `why`, it must be rejected by the intended check (message substring)."""
    try:
        detail = fn()
    except ValueError as e:
        msg = str(e)
        need(why is None or why in msg, 'control rejected for the wrong reason: %s (%s)' % (label, msg[:160]))
        out.append([label, msg[:160]])
        return
    raise ValueError('control accepted: %s (%s)' % (label, detail))


# ------------------------------------------------------------------ checks (each has a control that it must reject)

def require_boundary(w, tag):
    for rev in (False, True):
        need(boundary_bad(w, rev) == [], '%s boundary (%s)' % (tag, 'reverse' if rev else 'forward'))


def require_same_paths(w, w2, geo, name):
    ps0, ps1 = frame_paths(w, geo), frame_paths(w2, geo)
    need(ps0 == ps1, name + ': ordered per-register frame paths changed')
    return ps0, ps1


def require_same_profile(w, w2, geo, name):
    prof0, prof1 = paid_profile(w, geo), paid_profile(w2, geo)
    need(prof0 == prof1, name + ': paid profile changed')
    return prof0, prof1


def require_exporter(e, b, prof, nret, name):
    need(e['ADD'] == b['ADDs'] and e['COPY'] == e['ERASE'] == nret and e['F'] == b['F'] and e['B'] == b['B'],
         name + ': exporter bill')
    need(e['profile'] == prof, name + ': exporter profile differs from the frame-path profile')


def require_guards(e, name):
    need(e['local_ok'] and e['nine_ok'], name + ': precision guard (exporter F/B)')


def require_owner_delta(own, w, w2, name, expect=('H5_V_identity',)):
    f0, f1 = owner_flags(own, w), owner_flags(own, w2)
    newly_false = [k for k in OWNER_KEYS if f0[k] and not f1[k]]
    newly_true = [k for k in OWNER_KEYS if f1[k] and not f0[k]]
    need(newly_false == list(expect) and not newly_true, name + ': owner flags newly false %s, newly true %s'
         % (newly_false, newly_true))
    return f0, f1, newly_false


def legal_frame_raise(w2, geo, skip, changes_profile=False):
    """First B z-gate (from index skip) whose frame can be raised to a larger non-full frame while every operand
    still climbs monotonically; optionally the first such raise that also changes the paid profile."""
    fs, B = geo.fs, w2['B']
    seq = [g for sec in 'DA' for g in w2[sec]] + [g for g in B] + [g for g in w2['C']]
    off = len(w2['D']) + len(w2['A'])
    base_prof = paid_profile(w2, geo) if changes_profile else None
    for k in range(skip, len(B)):
        f, d, ss = B[k]
        if geo.is_y(d):
            continue
        nxt = []
        for r in (d, *ss):
            g2 = next((g for g in seq[off + k + 1:] if r == g[1] or r in g[2]), None)
            nxt.append(fs[g2[0]] if g2 is not None else fs[w2['final'][r]])
        for f2 in range(len(fs)):
            if f2 == geo.FULL or not fs[f] < fs[f2] or not all(fs[f2] <= x for x in nxt):
                continue
            trial = dict(w2, B=B[:k] + [[f2, d, list(ss)]] + B[k + 1:])
            frame_paths(trial, geo)          # confirms legality with the full replay
            if changes_profile and paid_profile(trial, geo) == base_prof:
                continue
            return trial, k, f, f2
    raise ValueError('no legal frame raise found')


# ------------------------------------------------------------------ order-ideal refinement

def commute(g, h):
    return g[1] not in h[2] and h[1] not in g[2]


def ideal_search(undo, E, S, v, kmax):
    """Order ideals of the undo's dependency poset (gate i depends on every earlier gate it does not commute
    with).  Keeping an ideal I before the scatter (in D) and the rest first in B lists the scatter as G_I E S.
    Exhaustive over |I| <= kmax (each ideal generated once, elements in increasing index), then a greedy strict
    descent from the empty ideal (smallest cost, then smallest index)."""
    n = len(undo)
    pred = [frozenset(j for j in range(i) if not commute(undo[i], undo[j])) for i in range(n)]
    P0 = mul(E, S)
    c0 = sum(r.bit_count() for r in P0)
    count = [0] * (kmax + 1)
    best = [None] * (kmax + 1)

    def step(P, g):
        _, t, ss = g
        new = P[t - v]
        for s in ss:
            new ^= P[s - v]
        return t - v, new

    def rec(I, last, P, cost):
        k = len(I)
        count[k] += 1
        if best[k] is None or cost < best[k][0]:
            best[k] = (cost, list(I))
        if k == kmax:
            return
        Iset = set(I)
        for i in range(last + 1, n):
            if pred[i] <= Iset:
                a, new = step(P, undo[i])
                old = P[a]
                P[a] = new
                I.append(i)
                rec(I, i, P, cost + new.bit_count() - old.bit_count())
                I.pop()
                P[a] = old
    rec([], -1, list(P0), c0)
    I, P, cost = [], list(P0), c0
    while True:
        Iset = set(I)
        cands = []
        for i in range(n):
            if i not in Iset and pred[i] <= Iset:
                a, new = step(P, undo[i])
                cands.append((cost + new.bit_count() - P[a].bit_count(), i, a, new))
        if not cands or min(cands)[0] >= cost:
            break
        c, i, a, new = min(cands)
        P[a] = new
        I.append(i)
        cost = c
    overall = min([b for b in best] + [(cost, sorted(I))], key=lambda x: (x[0], len(x[1]), x[1]))
    return dict(undo_gates=n, minimal_gates=sum(1 for p in pred if not p), size_bound=kmax, ideals_by_size=count,
                best_by_size=[[c, I] for c, I in best], greedy=[cost, sorted(I)], best=[overall[0], overall[1]],
                full_deferral_cost=c0)


def ideal_word(w, geo, sp, I):
    """Keep the undo gates of the order ideal I (original order) at the end of D, list the scatter as G E S with
    G their product, and run the remaining undo gates (original order) first in B."""
    v, D = geo.v, w['D']
    undo = [D[i] for i in sp['undo']]
    keep = set(I)
    kept = [undo[i] for i in sorted(I)]
    rest = [undo[i] for i in range(len(undo)) if i not in keep]
    E = tmat([D[i] for i in sp['prep']], v)
    G = tmat(kept, v, E)
    und = set(sp['undo'])
    w3 = dict(w)
    w3['D'] = [list(g) for i, g in enumerate(D) if i not in und] + [list(g) for g in kept]
    w3['scatter'] = listing(mul(G, scatter_rows(w)), len(w['ret']))
    w3['B'] = [list(g) for g in rest] + [list(g) for g in w['B']]
    return w3, G, kept, rest


def ideal_instance(name, w, w2, geo, sp, I, own, code, work):
    """The best order-ideal split found, with the same checks as the deferred word."""
    v = geo.v
    w3, G, kept, rest = ideal_word(w, geo, sp, I)
    require_boundary(w3, name + ' ideal split')
    require_same_paths(w, w3, geo, name + ' ideal split')
    _, prof3 = require_same_profile(w, w3, geo, name + ' ideal split')
    b0, b2, b3 = bounds(w), bounds(w2), bounds(w3)
    need(b3['ADDs'] == b2['ADDs'] - (b2['scatter_ADDs'] - b3['scatter_ADDs']), name + ': ideal split ADD accounting')
    need(b3['F'] == b2['F'] and b3['B'] == b2['B'], name + ': ideal split F/B differ from full deferral')
    need(b3['ADDs'] == IDEAL_REVIEW[name], name + ': ideal split ADDs %d, review reported %d' % (b3['ADDs'], IDEAL_REVIEW[name]))
    e0, mv0 = exporter(code, w, work, name + '-ideal-base')
    e3, mv3 = exporter(code, w3, work, name + '-ideal')
    require_exporter(e3, b3, prof3, len(w['ret']), name + ' ideal split')
    require_guards(e3, name + ' ideal split')
    need(mv0 == mv3, name + ': ideal split MOVE records differ')
    _, _, newly = require_owner_delta(own, w, w3, name + ' ideal split')
    t3, R3, V3 = h5tw(w3, geo)
    need(all(t3[k] for k in H5TW_REQUIRED) and R3 == G and V3 == tmat(rest, v) and tmat(rest, v, G) == geo.I
         and not t3['R_is_identity'] and not t3['V_is_identity'], name + ': ideal split H5-tw identities')
    und = set(sp['undo'])
    steps = [('W' if i in und else 'both', g) for i, g in enumerate(w['D'])] + [('W2', g) for g in kept]
    br = bridge(w, w3, geo, steps, w3['B'][:len(rest)], G)
    return dict(kept_undo_gates=sorted(I), kept_before_scatter=len(kept), deferred_to_B=len(rest),
                scatter_ADDs=[b0['scatter_ADDs'], b2['scatter_ADDs'], b3['scatter_ADDs']],
                ADDs=[b0['ADDs'], b2['ADDs'], b3['ADDs']], F=e3['F'], B=e3['B'],
                local_bits=e3['local_bits'], nine_stage_bits=e3['nine_stage_bits'], paid_profile=prof3,
                owner_newly_false=newly, word_sha256=sha(canonical(w3)), bridge=br,
                label='found by search (exhaustive over ideals of size <= %d plus greedy descent), not optimal' % IDEAL_MAX)


# ------------------------------------------------------------------ one lineage word

def census_word(name, w, geo, p589, own, code, work, check_controls):
    v = geo.v
    need(same_geometry(w, p589), name + ': geometry differs from PR589')
    sp = split_d(w, geo)
    D = w['D']
    prep, undo = [D[i] for i in sp['prep']], [D[i] for i in sp['undo']]
    need(prep and len(prep) == len(undo), name + ': preparation/undo shape')
    need(undo == prep[::-1], name + ': the undo is not the literal reverse of the preparation')
    need(all(g[0] == geo.ZERO for g in prep + undo), name + ': preparation/undo off the zero frame')
    w2, E, ES = defer(w, geo, sp)
    need(tmat(undo, v, E) == geo.I, name + ': the undo is not E^-1')
    need(scatter_rows(w2) == mul(E, scatter_rows(w)), name + ': the deferred listing is not E S')
    # literal boundary, both words, both directions
    require_boundary(w, name + ' base')
    require_boundary(w2, name + ' deferred')
    # frames and paid profile
    ps0, ps1 = require_same_paths(w, w2, geo, name)
    prof0, prof1 = require_same_profile(w, w2, geo, name)
    # Census fact (reported per word): every committed lineage word carries PR589's profile.
    need(prof1 == PROFILE and sum(k * x for k, x in prof1.items()) == RANK_MASS, name + ': profile is not PR589\'s')
    # scalar bill
    b0, b1 = bounds(w), bounds(w2)
    saving = b0['scatter_ADDs'] - b1['scatter_ADDs']
    undo_adds = sum(len(g[2]) for g in undo)
    need(b0['ADDs'] - b1['ADDs'] == saving and b1['B_ADDs'] - b0['B_ADDs'] == b0['D_ADDs'] - b1['D_ADDs'] == undo_adds,
         name + ': ADD accounting')
    need(b1['F'] == b0['F'] and b1['B'] < b0['B'], name + ': F unchanged and B falls')
    if name in PROBE:
        need((b0['ADDs'], b1['ADDs']) == PROBE[name], name + ': probe ADDs %s, found %s' % (PROBE[name], (b0['ADDs'], b1['ADDs'])))
    # exporter: bill, profile, guards, MOVE records
    e0, mv0 = exporter(code, w, work, name + '-base')
    e1, mv1 = exporter(code, w2, work, name + '-deferred')
    require_exporter(e0, b0, prof0, len(w['ret']), name + ' base')
    require_exporter(e1, b1, prof1, len(w['ret']), name + ' deferred')
    # The guards are required of every deferred word.  PR941's floor-calibration word is the only base word that
    # already misses the nine-stage guard (193 bits); the guard check must reject it.
    require_guards(e1, name + ' deferred')
    if name == 'PR941-floor':
        rejected('precision guard on the PR941 floor-calibration base word (%d nine-stage bits)' % e0['nine_stage_bits'],
                 lambda: require_guards(e0, name + ' base'), check_controls, why='precision guard')
    else:
        require_guards(e0, name + ' base')
    need(e1['local_bits'] <= e0['local_bits'] and e1['nine_stage_bits'] <= e0['nine_stage_bits'], name + ': guard bits rise')
    need(mv0 == mv1, name + ': exporter MOVE records differ')
    if name in PROBE_B:
        B0, B1, bits0, bits1 = PROBE_B[name]
        need((e0['B'], e1['B']) == (B0, B1) and (e0['local_bits'], e0['nine_stage_bits']) == bits0
             and (e1['local_bits'], e1['nine_stage_bits']) == bits1, name + ': probe B and guard bits')
    # owner checker
    f0, f1, newly_false = require_owner_delta(own, w, w2, name)
    # H5-tw identities
    t0, R0, V0 = h5tw(w, geo)
    t1, R1, V1 = h5tw(w2, geo)
    for t in (t0, t1):
        need(all(t[k] for k in H5TW_REQUIRED), name + ': H5-tw contract')
    need(t0['R_is_identity'] and t0['V_is_identity'], name + ': base is the R = V = I case')
    need(not t1['R_is_identity'] and not t1['V_is_identity'] and R1 == E and V1 == tmat(undo, v), name + ': R = E, V = E^-1')
    need(t0['T_is_identity'] == t1['T_is_identity'], name + ': helper twist T unchanged')
    # Anchor of the bridge chain for T = I words: the base D has PR589's D operator, and the PR1194-style
    # proof-only splice (base A/scatter/B/C with PR589's target-only D) passes every inherited owner flag.
    # The T != I words of PR1868 are anchored by PR1868's own per-cut bridge instead.
    d_equal = run_values(w, ['D']) == run_values(p589, ['D'])
    splice_ok = all(owner_flags(own, dict(w, D=p589['D'])).values()) if t0['T_is_identity'] else None
    need(d_equal == t0['T_is_identity'] and splice_ok in (True, None), name + ': PR1194-style anchor')
    # per-cut bridge (the deferred word's own D, A and B prefix)
    und = set(sp['undo'])
    steps = [('W' if i in und else 'both', g) for i, g in enumerate(D)]
    br = bridge(w, w2, geo, steps, w2['B'][:len(undo)], E)
    # maximality (prefix splits of the literal undo order) and the order-ideal search
    mx = maximality(w, w2, geo, undo, E)
    require_maximality(mx, name)
    ideals = ideal_search(undo, E, scatter_rows(w), v, IDEAL_MAX)
    need(ideals['full_deferral_cost'] == b1['scatter_ADDs'] and ideals['best'][0] <= mx['prefix_split_cost_min'],
         name + ': order-ideal search')
    row = dict(path=dict(LINEAGE)[name], payload_sha256=sha(canonical(w)), deferred_sha256=sha(canonical(w2)),
               D_runs=sp['runs'], preparation_gates=len(prep), undo_gates=len(undo),
               preparation_contiguous=sp['prep'] == list(range(sp['prep'][0], sp['prep'][-1] + 1)),
               ES_nonzero_rows=sum(1 for r in ES if r), scatter_ADDs=[b0['scatter_ADDs'], b1['scatter_ADDs']],
               ADDs=[b0['ADDs'], b1['ADDs']], saving=saving, F=[e0['F'], e1['F']], B=[e0['B'], e1['B']],
               local_bits=[e0['local_bits'], e1['local_bits']], nine_stage_bits=[e0['nine_stage_bits'], e1['nine_stage_bits']],
               paid_profile=prof1, rank_mass=sum(k * x for k, x in prof1.items()), selected_profile=prof1 == PROFILE,
               exporter=dict(base=e0, deferred=e1), owner_false_base=[k for k in OWNER_KEYS if not f0[k]],
               owner_false_deferred=[k for k in OWNER_KEYS if not f1[k]], owner_newly_false=newly_false,
               h5tw=dict(base=t0, deferred=t1), T_is_identity=t1['T_is_identity'],
               anchor=dict(base_D_operator_equals_PR589_D=d_equal, PR589_D_splice_passes_every_owner_flag=splice_ok),
               bridge=br, maximality=mx, order_ideals=ideals)
    return w2, row


# ------------------------------------------------------------------ controls (instances)

def controls(name, w, w2, geo, data, pins, own, row):
    out = []
    v = geo.v
    sp = split_d(w, geo)
    undo = [w['D'][i] for i in sp['undo']]
    nu = len(undo)
    kinds = lambda rs: dict(sorted(Counter('source' if r < v else 'target' if r < 2 * v else 'helper' for r in rs).items()))

    def endpoint(ww, label):
        bad = boundary_bad(ww)
        need(bad == [], 'dirty endpoint wrong on %d registers %s; failed equations %s'
             % (len(bad), kinds(bad), failed_equations(ww, geo)))
        return label
    # 1. deferral with the old S listing
    old = dict(w2, scatter=w['scatter'])
    rejected('deferral with the old scatter listing S', lambda: endpoint(old, 'old S'), out)
    # 2. undo moved after an operand's first B climb
    ops = {r for g in undo for r in (g[1], *g[2])}
    k0 = next(k for k, g in enumerate(w['B']) if ops & {g[1], *g[2]})
    moved = dict(w2, B=[list(g) for g in w['B'][:k0 + 1]] + [list(g) for g in undo] + [list(g) for g in w['B'][k0 + 1:]])
    rejected('undo moved after B[%d], the first B climb of an undo operand (frames)' % k0, lambda: frame_paths(moved, geo), out)
    moved_bad = boundary_bad(moved)
    need(moved_bad != [], 'moved undo: F2 endpoint unexpectedly exact')
    out.append(['undo moved after B[%d] (values, frames ignored)' % k0,
                'dirty endpoint wrong on %d registers %s' % (len(moved_bad), kinds(moved_bad))])
    # 3. one dropped undo gate
    drop = dict(w2, B=[list(g) for g in undo[1:]] + [list(g) for g in w['B']])
    rejected('first undo gate dropped', lambda: endpoint(drop, 'dropped'), out)
    # 4. reordered undo gates: preparation order instead of its reverse
    fwd = dict(w2, B=[list(g) for g in undo[::-1]] + [list(g) for g in w['B']])
    rejected('undo gates in preparation order', lambda: endpoint(fwd, 'prep order'), out)
    # 5. one wrong E S row
    a = next(i for i, row in enumerate(w2['scatter']) if row)
    rows = [list(r) for r in w2['scatter']]
    rows[a] = sorted(set(rows[a]) ^ {0})
    wrong = dict(w2, scatter=rows)
    rejected('E S row %d with bit 0 flipped' % a, lambda: endpoint(wrong, 'wrong row'), out)
    # 6. corrupted pin
    p = dict(LINEAGE)[name]
    b = bytearray(data[p])
    b[len(b) // 2] ^= 1
    rejected('corrupted source pin', lambda: check_pin(p, bytes(b), pins[p]), out)
    # reorder census: an adjacent transposition preserves the undo operator iff the two gates commute
    U = tmat(undo, v)
    comm = noncomm = agree = 0
    first_c = first_n = None
    for i in range(nu - 1):
        sw = undo[:i] + [undo[i + 1], undo[i]] + undo[i + 2:]
        same = tmat(sw, v) == U
        g, h = undo[i], undo[i + 1]
        commute = g[1] not in h[2] and h[1] not in g[2]
        agree += same == commute
        if commute:
            comm += 1
            first_c = i if first_c is None else first_c
        else:
            noncomm += 1
            first_n = i if first_n is None else first_n
    need(agree == nu - 1, 'reorder census: operator change does not match non-commutation')

    def swapped(i):
        sw = undo[:i] + [undo[i + 1], undo[i]] + undo[i + 2:]
        return dict(w2, B=[list(g) for g in sw] + [list(g) for g in w['B']])
    rejected('adjacent non-commuting undo gates %d,%d swapped' % (first_n, first_n + 1),
             lambda: endpoint(swapped(first_n), 'swap'), out)
    need(first_c is not None and boundary_ok(swapped(first_c)), 'a commuting swap keeps the boundary')
    # Check-level controls: each check must reject a word built to violate it, for the intended reason.
    E = tmat([w['D'][i] for i in sp['prep']], v)
    und = set(sp['undo'])
    steps = [('W' if i in und else 'both', g) for i, g in enumerate(w['D'])]
    short = dict(w2, D=w2['D'][:-1])
    rejected('bridge on the deferred word with its last D gate dropped',
             lambda: bridge(w, short, geo, steps, short['B'][:nu], E), out, why='differ from the replayed steps')
    rejected('bridge on the old-S word', lambda: bridge(w, old, geo, steps, old['B'][:nu], E), out, why='tracked twist')
    sw = swapped(first_n)
    rejected('bridge on the swapped-undo word', lambda: bridge(w, sw, geo, steps, sw['B'][:nu], E), out, why='not undone')
    rejected('owner delta on (base, base)', lambda: require_owner_delta(own, w, w, name), out, why='owner flags')
    fp, k, f, f2 = legal_frame_raise(w2, geo, nu)
    rejected('frame paths: legal frame raise of B[%d] %d -> %d' % (k, f, f2), lambda: require_same_paths(w, fp, geo, name),
             out, why='frame paths changed')
    fq, k2, g, g2 = legal_frame_raise(w2, geo, nu, changes_profile=True)
    rejected('paid profile: legal frame raise of B[%d] %d -> %d' % (k2, g, g2), lambda: require_same_profile(w, fq, geo, name),
             out, why='paid profile changed')
    e0, b0 = row['exporter']['base'], bounds(w)
    rejected('exporter profile against the frame-raised profile',
             lambda: require_exporter(e0, b0, paid_profile(fq, geo), len(w['ret']), name), out, why='exporter profile differs')
    rejected('maximality census with the deferred word as its own base',
             lambda: require_maximality(maximality(w2, w2, geo, undo, E), name), out, why='maximality census')
    reorder = dict(adjacent_transpositions=nu - 1, commuting=comm, non_commuting=noncomm,
                   operator_changes_iff_non_commuting=True,
                   commuting_swap_checked=[first_c, first_c + 1], commuting_swap_boundary_exact=True)
    return out, reorder


# ------------------------------------------------------------------ PR589 selected-word heuristic

def mst_basis(S, v, ZERO):
    """Prim's minimum spanning tree over the scatter rows plus a zero root; edge cost 2 + Hamming distance,
    root cost = row weight.  Returns target gates a ^= parent(a), children before parents."""
    pc = lambda x: len(bits(x))
    best = {a: (pc(S[a]), -1) for a in range(v)}
    order, parent = [], {}
    while best:
        a = min(best, key=lambda k: (best[k][0], k))
        _, p = best.pop(a)
        parent[a] = p
        order.append(a)
        for b in best:
            c = 2 + pc(S[a] ^ S[b])
            if c < best[b][0]:
                best[b] = (c, a)
    cost = sum(pc(S[a]) if parent[a] < 0 else 2 + pc(S[a] ^ S[parent[a]]) for a in range(v))
    gates = [[ZERO, v + a, [v + parent[a]]] for a in reversed(order) if parent[a] >= 0]
    return gates, cost


def selected_heuristic(p589, geo, own, code, work):
    """PR589 has no target basis; a scatter basis G (MST heuristic) after the D reads, G^-1 first in B."""
    v = geo.v
    sp = split_d(p589, geo)
    need(not sp['prep'] and not sp['undo'], 'PR589 D has no target basis')
    S = scatter_rows(p589)
    Gg, cost = mst_basis(S, v, geo.ZERO)
    Gm = tmat(Gg, v)
    GS = mul(Gm, S)
    w2 = dict(p589)
    w2['D'] = [list(g) for g in p589['D']] + [list(g) for g in Gg]
    w2['scatter'] = listing(GS, len(p589['ret']))
    w2['B'] = [list(g) for g in Gg[::-1]] + [list(g) for g in p589['B']]
    need(cost == 2 * len(Gg) + sum(len(bits(r)) for r in GS), 'MST cost accounting')
    require_boundary(w2, 'PR589 heuristic')
    require_same_paths(p589, w2, geo, 'PR589 heuristic')
    prof0, prof = require_same_profile(p589, w2, geo, 'PR589 heuristic')
    need(prof == PROFILE, 'PR589 heuristic paid profile')
    b0, b1 = bounds(p589), bounds(w2)
    e0, mv0 = exporter(code, p589, work, 'PR589-base')
    e1, mv1 = exporter(code, w2, work, 'PR589-heuristic')
    require_exporter(e0, b0, PROFILE, len(p589['ret']), 'PR589 base')
    require_exporter(e1, b1, PROFILE, len(p589['ret']), 'PR589 heuristic')
    need(e0['rank_mass'] == e1['rank_mass'] == RANK_MASS, 'PR589 heuristic rank mass')
    require_guards(e0, 'PR589 base')
    require_guards(e1, 'PR589 heuristic')
    need(mv0 == mv1, 'PR589 heuristic MOVE records')
    expect = ['H2_D_frame0_targets_from_helpers', 'H5_V_identity', 'K_equals_D']
    f0, f1, newly = require_owner_delta(own, p589, w2, 'PR589 heuristic', expect=expect)
    need(all(f0.values()), 'PR589 passes every owner flag')
    t1, R1, V1 = h5tw(w2, geo)
    need(all(t1[k] for k in H5TW_REQUIRED) and R1 == Gm and V1 == tmat(Gg[::-1], v) and not t1['V_is_identity'],
         'PR589 heuristic H5-tw identities')
    steps = [('both', g) for g in p589['D']] + [('W2', g) for g in Gg]
    br = bridge(p589, w2, geo, steps, w2['B'][:len(Gg)], Gm)
    return dict(method='Prim minimum spanning tree over the 111 scatter rows plus a zero root, edge cost 2 + Hamming '
                       'distance; scatter basis G (R = G, V = G^-1); heuristic, not optimal',
                tree_edges=len(Gg), roots=v - len(Gg), basis_gates_each_way=len(Gg),
                scatter_ADDs=[b0['scatter_ADDs'], b1['scatter_ADDs']], scatter_related_cost=cost,
                ADDs=[b0['ADDs'], b1['ADDs']], F=[e0['F'], e1['F']], B=[e0['B'], e1['B']],
                local_bits=[e0['local_bits'], e1['local_bits']], nine_stage_bits=[e0['nine_stage_bits'], e1['nine_stage_bits']],
                paid_profile=prof, rank_mass=e1['rank_mass'], owner_false=[k for k in OWNER_KEYS if not f1[k]],
                word_sha256=sha(canonical(w2)), bridge=br)


# ------------------------------------------------------------------ census scan (optional)

def census_scan():
    """Every committed R439 word under research/ (git ls-files), deduplicated by canonical hash, against the lists."""
    files = subprocess.run(['git', '-C', str(ROOT), 'ls-files', 'research'], capture_output=True, text=True,
                           check=True).stdout.split('\n')
    own_dir = 'research/' + HERE.name + '/'
    listed = {p for _, p in LINEAGE + OUTSIDE}
    seen = {}
    for f in files:
        if not f.endswith(('.json', '.json.gz')) or f.startswith(own_dir):
            continue
        try:
            b = (ROOT / f).read_bytes()
            if len(b) > 50_000_000:
                continue
            raw = gzip.decompress(b) if f.endswith('.gz') else b
            if b'"scatter"' not in raw:
                continue
            w = json.loads(raw)
        except (OSError, ValueError, EOFError):
            continue
        if not isinstance(w, dict) or not all(k in w for k in ('v', 'R', 'D', 'A', 'B', 'C', 'scatter', 'ret')):
            continue
        if (w['v'], w['R']) != (111, 439):
            continue
        seen.setdefault(sha(canonical(w)), []).append(f)
    listed_hashes = {}
    for h, fs in seen.items():
        for f in fs:
            if f in listed:
                listed_hashes[h] = f
    missing = {h: fs for h, fs in seen.items() if h not in listed_hashes}
    print('census scan: %d distinct committed R439 words (%d files); %d listed, %d unlisted'
          % (len(seen), sum(len(x) for x in seen.values()), len(listed_hashes), len(missing)))
    for h, fs in sorted(missing.items()):
        print('  UNLISTED %s %s' % (h[:12], ', '.join(fs)))
    need(len(listed_hashes) == len(listed), 'a listed word was not found by the scan')
    return not missing


# ------------------------------------------------------------------ driver

def run(write=False):
    data, pins = load_inputs()
    p589 = parse_word(PR589, data[PR589])
    own = owner_module(data[CHECKER])
    geo = Geo(p589)
    rep = dict(status='PASS_R439_DEFERRED_TARGET_BASIS', inputs={p: pins[p]['sha256'] for p in INPUTS},
               columns=geo.n, census={}, outside={}, instances={}, controls={}, check_controls=[], reorder={},
               ideal_split={})
    built = {}
    words = {}
    with tempfile.TemporaryDirectory(prefix='r439-deferred-') as tmp:
        work = Path(tmp)
        for name, path in LINEAGE:
            w = parse_word(path, data[path])
            words[name] = w
            built[name], rep['census'][name] = census_word(name, w, geo, p589, own, data[EXPORTER], work,
                                                          rep['check_controls'])
            if name in INSTANCES:
                ctl, reo = controls(name, w, built[name], geo, data, pins, own, rep['census'][name])
                rep['controls'][name] = ctl
                rep['reorder'][name] = reo
        need(len(rep['check_controls']) == 1, 'the PR941 floor guard control ran exactly once')
        for name in IDEAL_REVIEW:
            w = words[name]
            sp = split_d(w, geo)
            I = rep['census'][name]['order_ideals']['best'][1]
            rep['ideal_split'][name] = ideal_instance(name, w, built[name], geo, sp, I, own, data[EXPORTER], work)
        for name, path in OUTSIDE:
            w = parse_word(path, data[path])
            need(same_geometry(w, p589), name + ': geometry')
            sp = split_d(w, geo)
            need(not sp['prep'] and not sp['undo'] and sp['helper_gates'] == 0, name + ': not a target-basis word')
            b = bounds(w)
            rep['outside'][name] = dict(path=path, D_runs=sp['runs'], ADDs=b['ADDs'], scatter_ADDs=b['scatter_ADDs'],
                                        target_basis_gates=0, deferral='vacuous (R = I)')
        rep['selected_heuristic'] = selected_heuristic(p589, geo, own, data[EXPORTER], work)
    for name, fname in INSTANCES.items():
        rep['instances'][name] = dict(file=fname, payload_sha256=sha(canonical(built[name])))
    rep['new_kappa_claim'] = False
    rep = json.loads(json.dumps(rep))
    if write:
        for name, fname in INSTANCES.items():
            (HERE / fname).write_bytes(gzip.compress(canonical(built[name]), mtime=0))
        (HERE / 'EXPECTED.json').write_text(json.dumps(rep, indent=1, sort_keys=True) + '\n', encoding='utf-8')
    containers = {}
    for name, fname in INSTANCES.items():
        raw = (HERE / fname).read_bytes()
        need(gzip.decompress(raw) == canonical(built[name]), 'committed payload differs from the rebuilt word: ' + name)
        containers[name] = raw == gzip.compress(canonical(built[name]), mtime=0)
    need(json.loads((HERE / 'EXPECTED.json').read_text(encoding='utf-8')) == rep, 'EXPECTED.json mismatch')
    return rep, containers


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--write', action='store_true', help='regenerate EXPECTED.json and the committed payloads')
    ap.add_argument('--census-scan', action='store_true',
                    help='only list committed R439 words under research/ (needs git) and report any unlisted word')
    a = ap.parse_args()
    if a.census_scan:
        sys.exit(0 if census_scan() else 1)
    t0 = time.perf_counter()
    rep, containers = run(write=a.write)
    print('%-20s %6s %6s %5s %4s %4s %9s %7s %17s %10s %s' % ('word', 'base', 'defer', 'save', 'E', 'ES', 'scatter',
                                                            'F', 'B', 'bits', 'owner newly false'))
    for name, c in rep['census'].items():
        print('%-20s %6d %6d %5d %4d %4d %4d->%-4d %7d %8d->%-8d %d/%d->%d/%d %s%s' % (
            name, c['ADDs'][0], c['ADDs'][1], c['saving'], c['preparation_gates'], c['ES_nonzero_rows'],
            c['scatter_ADDs'][0], c['scatter_ADDs'][1], c['F'][1], c['B'][0], c['B'][1], c['local_bits'][0],
            c['nine_stage_bits'][0], c['local_bits'][1], c['nine_stage_bits'][1], ','.join(c['owner_newly_false']),
            '' if c['T_is_identity'] else ' (T != I)'))
    first = next(iter(rep['census'].values()))
    print('every lineage word: boundary %d columns both directions, frame paths and MOVE records identical, '
          'paid profile %s mass %d, bridge, maximality census' % (rep['columns'], json.dumps(first['paid_profile'],
                                                                  separators=(',', ':')), first['rank_mass']))
    for name, c in rep['census'].items():
        b, m, o = c['bridge'], c['maximality'], c['order_ideals']
        rl = m['relaxed_paths']
        print('  %-20s cuts=%d twisted=%d prefix-split min %d at %s; absorption legal %d/%d; relaxed partners '
              'loose %d/%d current %d/%d monotone %d/%d; ideals<=%d best %d %s greedy %d' % (
                  name, b['cuts'], b['cuts_with_target_difference'], m['prefix_split_cost_min'], m['prefix_split_argmin'],
                  m['absorption_pairs_frame_legal'], m['absorption_pairs'],
                  rl['loose']['writes_with_a_partner'], rl['loose']['max_partners'],
                  rl['current']['writes_with_a_partner'], rl['current']['max_partners'],
                  rl['monotone']['writes_with_a_partner'], rl['monotone']['max_partners'],
                  o['size_bound'], o['best'][0], o['best'][1], o['greedy'][0]))
    for name, x in rep['ideal_split'].items():
        print('order-ideal split %-12s keep undo gates %s before the scatter: scatter %d -> %d, ADDs %d -> %d -> %d; '
              'B %d; bits %d/%d; owner newly false %s; bridge cuts %d (%s)' % (
                  name, x['kept_undo_gates'], x['scatter_ADDs'][1], x['scatter_ADDs'][2], x['ADDs'][0], x['ADDs'][1],
                  x['ADDs'][2], x['B'], x['local_bits'], x['nine_stage_bits'], ','.join(x['owner_newly_false']),
                  x['bridge']['cuts'], x['label']))
    for name, o in rep['outside'].items():
        print('outside %-8s ADDs %d scatter %d: %s' % (name, o['ADDs'], o['scatter_ADDs'], o['deferral']))
    s = rep['selected_heuristic']
    print('PR589 heuristic (MST scatter basis G, not optimal): scatter %d -> %d with %d basis gates each way; ADDs %d -> %d; '
          'B %d -> %d; bits %d/%d -> %d/%d; owner false %s' % (
              s['scatter_ADDs'][0], s['scatter_related_cost'], s['basis_gates_each_way'], s['ADDs'][0], s['ADDs'][1],
              s['B'][0], s['B'][1], s['local_bits'][0], s['nine_stage_bits'][0], s['local_bits'][1],
              s['nine_stage_bits'][1], ','.join(s['owner_false'])))
    for label, why in rep['check_controls']:
        print('  check control rejected: %s -- %s' % (label, why))
    for name, ctl in rep['controls'].items():
        for label, why in ctl:
            print('  %s control rejected: %s -- %s' % (name, label, why))
        r = rep['reorder'][name]
        print('  %s reorder census: %d adjacent swaps, %d commuting (operator kept, boundary exact), %d not (operator '
              'changes)' % (name, r['adjacent_transpositions'], r['commuting'], r['non_commuting']))
    print('committed payloads equal the rebuilt words; gzip containers byte-identical here: %s' % containers)
    print('PASS_R439_DEFERRED_TARGET_BASIS words=%d outside=%d instances=%d ideal_splits=%d columns=%d controls=%d '
          'no_new_kappa (%.1f s)' % (len(rep['census']), len(rep['outside']), len(rep['instances']),
                                     len(rep['ideal_split']), rep['columns'],
                                     sum(len(x) for x in rep['controls'].values()) + len(rep['check_controls']),
                                     time.perf_counter() - t0))


if __name__ == '__main__':
    main()
