#!/usr/bin/env python3
"""Build and replay the ambient-quotient words of the PR #4596 family.

Builds the pinned PR4470/PR4441/joint-patch word, then for a candidate kernel
vector v in F2^9 builds the quotient word (frames -> images under a linear
surjection with kernel span{v}), replays both orientations with the SHIPPED
evaluators, and reports the paid profile, helper profile and local deficit.

The certificate for admissibility is the shipped literal replay
(research/kappa-rebuild/complex/native_extensions.py:literal_replay) plus the
shipped endpoint table (research/kappa-causal-continuation/buffer-borrowing/
verify_buffers.py:expected) -- this script never re-implements the semantics.
The quotient, the helper re-padding and the invoice constants follow DaysSky's
PR #4596 (research/complex-quotient-511); the base word is Cinna Davis's PR4470
word with the PR4441 and joint-helper patches.

Imported by verify.py; this module writes no files.
"""
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/fresh-helper-boundary'))
sys.path.insert(0, str(ROOT/'research/joint-helper-lattice'))

import native as F  # noqa: E402

JOINT = ROOT/'research/joint-helper-lattice'
ROLES = 632
MAINS = 224
BLOCK = 8
PORTS = 112
PAIRS = 16
SPLIT = 7
CALLS = 18


# ---------------------------------------------------------------- base word
def build_base():
    """The pinned word of PR4470 + PR4441 + the joint-helper patch (as PR4596)."""
    patch = F.read(JOINT/'PATCH.json')
    c = F.read(F.BASE/'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    original = F.read(F.BASE/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    parent = F.read(F.HERE/'CHANGES.json')
    maps = {d: F.gates(p) for d, p in original.items()}
    F.need(set(maps['forward']) == set(maps['backward']), 'Same scalar contact inventory')
    for key, field in [('entrances', 'start'), ('exits', 'final')]:
        for r, old, new in parent[key]:
            F.need(c[field][r] == old, 'Parent boundary pin')
            c[field][r] = new
    for phase, ordinal, old, new in parent['gates']:
        for d, p in original.items():
            i = maps[d][phase, ordinal]
            F.need(p[i][2] == old, 'Parent scalar pin')
            p[i][2] = new
    prior = F.read(ROOT/'research/missing-join-frame/PATCH.json')
    F.need(prior['phase'] == 'B' and prior['ordinal'] == 480, 'Exact prior contact')
    prior_frame = len(c['frames'])
    c['frames'].append(prior['new_basis'])
    for d, p in original.items():
        i = maps[d]['B', 480]
        F.need(p[i][2] == prior['old_frame'], 'Missing-span parent pin')
        p[i][2] = prior_frame
    labels = {frozenset(F.span(b)): i for i, b in enumerate(c['frames'])}

    def label(b):
        s = frozenset(F.span(b))
        F.need(len(s) == 2**len(b), 'Independent binary basis')
        if s not in labels:
            labels[s] = len(c['frames'])
            c['frames'].append(b)
        return labels[s]

    for move in patch['changes']:
        phase, r = move['phase'], move['ordinal']
        a, b = F.span(move['old']), F.span(move['new'])
        F.need(a != b, 'No unchanged patch entry')
        f = label(move['new'])
        if phase in ('entrance', 'exit'):
            field = 'start' if phase == 'entrance' else 'final'
            F.need(F.span(c['frames'][c[field][r]]) == a, 'Current source pin')
            c[field][r] = f
        else:
            for d, p in original.items():
                i = maps[d][phase, r]
                F.need(F.span(c['frames'][p[i][2]]) == a, 'Current scalar source pin')
                p[i][2] = f
    return c, original


# ---------------------------------------------------------------- quotient
def span_of(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in out}
    return frozenset(out)


def dedupe(vectors):
    pivots = {}
    keep = []
    for v in vectors:
        y = v
        while y:
            bit = y.bit_length()-1
            if bit in pivots:
                y ^= pivots[bit]
            else:
                pivots[bit] = y
                keep.append(v)
                break
    return keep


def projector(v):
    """Linear map pi_v with kernel span{v}; image = {x : x_p = 0}, p = top bit."""
    p = v.bit_length()-1
    mask = 1 << p
    def pi(x):
        return (x ^ v) if (x & mask) else x
    return pi, p


def quotient(c, programs, v):
    """Return (word, programs, remap) with every frame replaced by pi_v(image)."""
    pi, _ = projector(v)
    frames = c['frames']
    span_index = {}
    new_frames = []

    def frame_index(basis):
        mapped = dedupe([pi(x) for x in basis])
        key = span_of(mapped)
        if key not in span_index:
            span_index[key] = len(new_frames)
            new_frames.append(mapped)
        return span_index[key]

    remap = {i: frame_index(basis) for i, basis in enumerate(frames)}
    word = deepcopy(c)
    for r in range(len(word['start'])):
        word['start'][r] = remap[word['start'][r]]
        word['final'][r] = remap[word['final'][r]]
    out_programs = {}
    for direction, program in programs.items():
        out = []
        for event in program:
            e = deepcopy(event)
            if e[0] == 'scalar':
                e[2] = remap[e[2]]
            elif e[0] == 'warp':
                e[3] = remap[e[3]]
                e[4] = remap[e[4]]
            elif e[0] == 'climb':
                e[3] = remap[e[3]]
                e[4] = remap[e[4]]
            elif e[0] == 'center':
                e[2] = remap[e[2]]
                e[3] = remap[e[3]]
            out.append(e)
        out_programs[direction] = out
    word['frames'] = new_frames
    return word, out_programs, remap


def pad_ambient(word, p):
    """Spend the unused axis on one helper so the word occupies nine axes."""
    axis = 1 << p
    frames = word['frames']
    for role in range(MAINS, ROLES):
        final = word['final'][role]
        if axis in span_of(frames[final]):
            continue
        new = dedupe(frames[final]+[axis])
        if len(new) != len(frames[final])+1:
            continue
        frames.append(new)
        word['final'][role] = len(frames)-1
        return role
    return None


# ---------------------------------------------------------------- pricing
def moment(profile, exponent):
    return sum(n*(r**exponent) for r, n in profile.items() if n and r > 0)


def rank_mass(profile):
    return sum(r*n for r, n in profile.items())


def invoice(helper_profile, paid_profile, block=BLOCK, p=PAIRS, split=SPLIT, calls=CALLS):
    targets = Counter({r: calls*n for r, n in helper_profile.items()})
    paid = Counter({r: calls*n for r, n in paid_profile.items()})
    thin = PORTS*(2*p+1-calls)
    paid[1] += thin
    targets[1+block*(p+2)] += 2*PORTS
    for length in (split, p-1-split):
        for j in range(1, length+1):
            targets[1+block*(j+1)] += 2*PORTS
            paid[block*(j+1)] += 2*PORTS
    surplus = rank_mass(targets)-rank_mass(paid)
    return targets, paid, surplus, thin


def dual_ok(T, P, kappa, u=0.2, c=20.0, gamma=0.97):
    t = 1.0-kappa
    return moment(P, t) < moment(T, t) and moment(P, t+u) < gamma*(c**u)*moment(T, t)


def admissible_kappa(T, P, lo=1e-7, hi=0.25, steps=2400):
    best = None
    prev = None
    for i in range(steps+1):
        k = lo+(hi-lo)*i/steps
        if dual_ok(T, P, k):
            best, prev = k, k
        elif prev is not None and best == prev:
            a, b = prev, k
            for _ in range(90):
                mid = (a+b)/2
                if dual_ok(T, P, mid):
                    a = mid
                else:
                    b = mid
            return a
    return best


# ---------------------------------------------------------------- evaluation
def evaluate(base_word, base_programs, v, V, X):
    """Return a record for the kernel span{v}; record['admissible'] says it replayed."""
    rec = {'kernel': v, 'admissible': False, 'reason': None}
    try:
        word, programs, remap = quotient(base_word, base_programs, v)
    except Exception as exc:                     # noqa: BLE001
        rec['reason'] = 'quotient:%s' % exc
        return rec
    p = v.bit_length()-1
    padded = pad_ambient(word, p)
    if padded is None:
        rec['reason'] = 'no helper absorbs the unused axis'
        return rec
    rec['padded_helper'] = padded
    frames = word['frames']
    union = set()
    for basis in frames:
        union |= span_of(basis)
    ambient = len(union).bit_length()-1
    rec['ambient_dim'] = ambient
    if ambient != BLOCK+1:
        rec['reason'] = 'ambient dim %d (block-8 charge invalid)' % ambient
        return rec
    ranks = [len(b) for b in frames]
    mains = [ranks[word['final'][r]]-ranks[word['start'][r]] for r in range(MAINS)]
    helpers = Counter(ranks[word['final'][r]]-ranks[word['start'][r]] for r in range(MAINS, ROLES))
    rec['main_widths'] = dict(sorted(Counter(mains).items()))
    rec['main_rank_mass'] = sum(mains)
    rec['helper_widths'] = dict(sorted(helpers.items()))
    rec['helper_rank_mass'] = rank_mass(helpers)
    try:
        profiles = {}
        for direction in ('forward', 'backward'):
            program = [list(e) for e in programs[direction]]
            synthesized = F.synthesize({'frames': frames, 'start': word['start'],
                                        'final': word['final'], 'precondition': [], 'A': [],
                                        'B': [], 'cut': [], 'compensation': [], 'cleanup': [],
                                        'tail': []}, program)
            rows, receipt = X.literal_replay(V, {'frames': frames, 'start': word['start'],
                                                 'final': word['final'], 'v': PORTS, 'R': 408},
                                             synthesized, direction == 'backward')
            bad = [r for r in range(ROLES)
                   if rows['L', r] != V.expected(('L', r), [], direction == 'backward', False)]
            if bad:
                rec['reason'] = '%s: %d endpoint failures (first %s)' % (direction, len(bad), bad[:5])
                return rec
            if rows[('C', 0)]:
                rec['reason'] = '%s: owned C not cleared' % direction
                return rec
            profiles[direction] = Counter({int(k): val for k, val in receipt['paid_profile'].items()})
        if profiles['forward'] != profiles['backward']:
            rec['reason'] = 'directions disagree'
            return rec
    except Exception as exc:                     # noqa: BLE001
        rec['reason'] = 'replay:%s' % exc
        return rec
    paid = profiles['forward']
    rec['paid_profile'] = dict(sorted(paid.items()))
    rec['paid_rank_mass'] = rank_mass(paid)
    rec['local_deficit'] = rec['paid_rank_mass']-rec['helper_rank_mass']
    targets, paidc, surplus, thin = invoice(dict(helpers), dict(paid))
    rec['surplus'] = surplus
    rec['thin'] = thin
    kappa = admissible_kappa(targets, paidc)
    rec['kappa'] = kappa
    rec['admissible'] = True
    return rec
