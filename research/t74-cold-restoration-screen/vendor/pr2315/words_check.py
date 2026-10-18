#!/usr/bin/env python3
"""Independent check (task A) of the two borrowed T74 local words of PR #2269.

Object: CrocSwap/integer-mult-bounds PR #2269 (jeremykothe2), head
b479fc5567bc09ab9185bffe89b62594f36d74e5, package research/gmx-t74-borrow43/:
new/borrow/words/BORROW-WORD-43{base,extra}.json.gz and their inputs
new/borrow/inputs/* (canonical unborrowed words, block certificate, witnesses).

Credit: PR2269 (jeremykothe2) for the borrow43 package and words; PR2226
(Cinna Davis / 1337isnot1337, with OpenAI Codex) for anticipatory dirty
borrowing, the alias rule, the K_G reference changes and the free-operator
replay idea; PR2260 (Dugongue) for concurrent application of PR2226; the T74
lineage PR1319/PR1297 (Rohan Arun), PR1625 (mdumitrean) and the pivot-554
kernel; icekylinx (Zhihao Chen) for the Clifford-frame normal forms
(notes/general-clifford-frames.tex) and the local-word checker lineage.

This file shares no code with those packages.  It was written from their
written specification (PR2226 README/PROOF, notes/general-clifford-frames.tex,
the PR2269 README and the JSON field layout); no package code is imported or
executed.  Inputs are read as git blobs at the pinned commit (or from
--blob-dir) and are pinned by sha256 and git blob id.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B words_check.py [--repo PATH | --blob-dir DIR] [--out RECEIPT.json]
The receipt (if requested) must be written next to this script.  The final
stdout line is PASS_T74_BORROW43_WORDS_INDEPENDENT or FAIL_T74_BORROW43_WORDS_INDEPENDENT.

MODEL (stated precisely; see also the receipt field "model").
 * Registers 0..v-1 are X (sources), v..2v-1 are Y (targets), 2v..2v+R-1
   helpers; n = 2v+R.  Removed helpers do not exist.  A buffer register b = r+n
   exists only for r in helper_final (restored cold helpers) and only in cleanup.
 * Frame = GF(2)-subspace of F_2^h (h = 9), given by a list of bit-mask
   vectors; compared as spans (reduced echelon form).  Start: X_i = span(port_i),
   Y = 0, helper = start_extra[r] or 0.  End: X = FULL, Y_i = port_i^perp,
   helper = helper_final[r] or FULL.
 * Every framed gate (add t s c F | scale t c F) climbs each incident register
   from its current frame S to F; legal only if S <= F; a strict climb pays one
   child of rank dim F - dim S.  precondition/compensation are at frame 0.
 * After A every target sits at its level (target_levels, here all 0) and
   every centre at its centre frame.  cut gates (frame null) add c*centre into
   a target at its level; each centre pays one COPY child of rank
   dim(centre frame) - dim(level) per distinct served level (nested chain).
 * warp [pos, L, G, U, E] is inserted before B[pos] (list order inside a
   position): requires cur[L] == span U exactly, sets cur[L] = span E, pays
   nothing (rank-zero reference change K_G); logically L <- K_G L.
 * After B and restore every live register climbs to its end frame (paid).
 * cleanup items must all be at FULL, may touch only live registers whose
   current frame is FULL, or buffers; they pay nothing.
 * Logic: exact replay over Q<F_43> (rationals x free group on K_1..K_43):
   every live register starts as an independent symbol (arbitrary dirty
   content), buffers start at 0; add t+=c*s, scale t*=c, warp left-multiplies
   by K_k^{+-1} with free-group cancellation.  Accept iff after cleanup
   Y_i = Y_i + X_i, every other live register is its own input, and every
   buffer is 0.  The dual orientation replays g^{-T} for every item
   (add -> s -= c t, scale -> 1/c, K -> K^{-T} as new free letters) and expects
   X_i = X_i - Y_i.
 * Warp algebra over GF(2): G (columns = images of unit vectors) invertible,
   dim U = dim E, G span U = span E, M = [[G,0],[G+G^-T,G^-T]] symplectic for
   w((x,z),(x',z')) = x.z' + z.x', M L_0 = L_0, M L_FULL = L_FULL,
   M L_U = L_E where L_W = {(u, u+p): u in W, p in W^perp}, and the Fourier
   rank h - dim(L_E cap M L_U) of R_in = T_E K_G T_U^-1 is 0; G^-T U^perp = E^perp.
   Exact Clifford phases / Gaussian monomial lifts are NOT checked here.
"""

import argparse
import copy
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from fractions import Fraction

PASS_LINE = 'PASS_T74_BORROW43_WORDS_INDEPENDENT'
FAIL_LINE = 'FAIL_T74_BORROW43_WORDS_INDEPENDENT'
COMMIT = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'
PKG = 'research/gmx-t74-borrow43/'
DEFAULT_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repository root

# path (relative to PKG) -> (git blob id, sha256 of blob bytes)
PINS = {
    'word_base': ('new/borrow/words/BORROW-WORD-43base.json.gz',
                  '448dd795adba29392a90b34aa3f1b1b796c7e0bd',
                  '9492a5537fb87d9ca98dffcd0230f7625b3789744fa94e2f18acf23d91d998b5'),
    'word_extra': ('new/borrow/words/BORROW-WORD-43extra.json.gz',
                   '2b51ba96256283bbc5578f99b694c50edd8a0e35',
                   '87d51f5298101d5947f45c43ee02f0ec45d6acbddabb808d0d02db1eaf063734'),
    'canon_base': ('new/borrow/inputs/gauge44.canonical.json.gz',
                   '4abb6e28f02c95b41ed345d4e4401d16d58ae791',
                   '65c6d17ffee2eacf27bff438f37fc549c9ed0c909cbc7a52976cc75cf2d15b91'),
    'canon_extra': ('new/borrow/inputs/extra.canonical.json.gz',
                    'e0d670d4351229ce6921ecfbecf180070b17616b',
                    'd7e48dcbafa236a2e1e41f7958244211506f7c7630fe6a2d43d2bdf17b7ae015'),
    'blocks': ('new/borrow/inputs/blocks.json',
               'c683574b3861678081fd5c5944dbd7a47309f6fd',
               'ddfac1dae1fe7cc0a91e7c7205c6d9d0c07c682880aa34eed83bf4ad7384da9f'),
    'witness_base': ('new/borrow/inputs/witness_43_base.json',
                     '9f4b93f3bc52d4f4ffaa128cfd7ae574fd36c462',
                     '67ffb66d94067f6e53aee9118fe90e14a57f497fc8b3f708b6dac3de2e58ff28'),
    'witness_extra': ('new/borrow/inputs/witness_43_extra.json',
                      '864ba533f50c2f1f639a6a3559b185bd321b923a',
                      'd46449c6dbf4477f260cf5baea9bbb570a66ee0b6db81f4a220b9e3086ae9e46'),
    'providers': ('new/BORROW-PROVIDERS.json',
                  '42563d218a5c7321f686c1cf9b98e75883d85abc',
                  '8324fcf5fd652af9793c1acbc5f5099ee0d2f1eefa0adfbb8335f3d31d891da2'),
    'word566_base': ('new/gauge44-word-566.json.gz',
                     '76c01583a0286cddb0f71e0cb13077e4317104f6',
                     'eeb6a236ed0ea8873b8800947d0cd19c36a6fcfdf857fc42913cb45cd984f219'),
    'word566_extra': ('new/extra-word-566.json.gz',
                      'e86142b352466f54a3da38c96a6e1484145c3b5c',
                      'cd417b904408c221d9840d08faff8af040cc4207f9804284f2f5375d21298a62'),
}

# Claims under test (PR2269 README / scout notes), written here independently of the files.
CLAIMS = {
    'base': dict(profile={1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8},
                 old_profile={1: 2348, 2: 500, 3: 416, 4: 130, 5: 82, 8: 8},
                 providers_key='gauge44', base_tag='eeb6a236'),
    'extra': dict(profile={1: 2339, 2: 509, 3: 418, 4: 125, 5: 42, 8: 8},
                  old_profile={1: 2340, 2: 508, 3: 420, 4: 126, 5: 82, 8: 8},
                  providers_key='extra', base_tag='cd417b90'),
    'width_inventory': {4: 36, 5: 9, 7: 36, 8: 116, 9: 240},
    'helpers_before': 480, 'helpers_after': 437, 'warps': 43, 'mass': 5385,
    # README: "43 high helpers (8 width-4, 35 width-5)". This holds for the base (gauge44) word; the
    # extra word's 43 removed helpers have canonical widths 4 x 4 + 39 x 5 (recorded, see receipt).
    'removed_old_widths': {'base': {4: 8, 5: 35}, 'extra': {4: 4, 5: 39}},
}


class Reject(Exception):
    """A failed check; .check names the check family that rejected."""

    def __init__(self, check, msg):
        Exception.__init__(self, '[%s] %s' % (check, msg))
        self.check = check
        self.msg = msg


def need(cond, check, msg):
    if not cond:
        raise Reject(check, msg)


# ----------------------------------------------------------------------------
# Input loading and pinning
# ----------------------------------------------------------------------------

def git_blob_id(data):
    h = hashlib.sha1()
    h.update(b'blob %d\0' % len(data))
    h.update(data)
    return h.hexdigest()


def verify_pin(key, data):
    rel, blob, sha = PINS[key]
    need(git_blob_id(data) == blob, 'pin', 'git blob id mismatch for %s' % rel)
    need(hashlib.sha256(data).hexdigest() == sha, 'pin', 'sha256 mismatch for %s' % rel)


def load_inputs(repo, blob_dir):
    raw = {}
    pins = {}
    for key in sorted(PINS):
        rel, blob, sha = PINS[key]
        path = PKG + rel
        if blob_dir is None:
            got = subprocess.run(['git', '-C', repo, 'rev-parse', COMMIT + ':' + path],
                                 capture_output=True, text=True)
            need(got.returncode == 0, 'pin', 'cannot resolve %s at %s' % (path, COMMIT))
            need(got.stdout.strip() == blob, 'pin', 'path %s does not resolve to pinned blob' % path)
            got = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', blob], capture_output=True)
            need(got.returncode == 0, 'pin', 'cannot read blob %s' % blob)
            data = got.stdout
        else:
            # Layouts: DIR/<package-relative path> (a `git archive` export of the package, as
            # check_all.py uses) or DIR/<basename>.  Either way the bytes must match both pins.
            cands = [os.path.join(blob_dir, rel), os.path.join(blob_dir, os.path.basename(rel))]
            src = next((c for c in cands if os.path.isfile(c)), None)
            need(src is not None, 'pin', 'blob for %s not found in --blob-dir (tried %s)' % (rel, ', '.join(cands)))
            with open(src, 'rb') as fh:
                data = fh.read()
        verify_pin(key, data)
        raw[key] = data
        pins[key] = dict(path=path, git_blob=blob, sha256=sha, bytes=len(data))
    js = {}
    for key, data in raw.items():
        if PINS[key][0].endswith('.gz'):
            data = gzip.decompress(data)
        js[key] = json.loads(data.decode('utf-8'))
    return js, pins, raw


# ----------------------------------------------------------------------------
# GF(2) linear algebra on integer bit vectors
# ----------------------------------------------------------------------------

def parity(x):
    return bin(x).count('1') & 1


def echelon(vectors):
    """Fully reduced echelon basis {pivot bit: vector} of the span of the vectors."""
    piv = {}
    for x in vectors:
        x = int(x)
        for b in list(piv):
            if (x >> b) & 1:
                x ^= piv[b]
        if x:
            lead = x.bit_length() - 1
            for b in list(piv):
                if (piv[b] >> lead) & 1:
                    piv[b] ^= x
            piv[lead] = x
    return piv


def span(vectors):
    """Canonical key of a subspace: its reduced echelon basis, sorted decreasingly."""
    return tuple(sorted(echelon(vectors).values(), reverse=True))


def reduce_by(x, piv):
    for b, vec in piv.items():
        if (x >> b) & 1:
            x ^= vec
    return x


def contains(small, big):
    piv = echelon(big)
    return all(reduce_by(x, piv) == 0 for x in small)


def dim_sum(a, b):
    return len(span(list(a) + list(b)))


def perp(sub, h):
    return span([x for x in range(1, 1 << h) if all(parity(x & u) == 0 for u in sub)])


def mat_apply(cols, x):
    y = 0
    i = 0
    while x:
        if x & 1:
            y ^= cols[i]
        x >>= 1
        i += 1
    return y


def mat_inverse(cols, h):
    """Columns of G^{-1}, or None if G is singular over GF(2)."""
    piv = {}
    for i in range(h):
        a, b = cols[i], 1 << i  # invariant: G(b) = a
        for p in list(piv):
            pa, pb = piv[p]
            if (a >> p) & 1:
                a ^= pa
                b ^= pb
        if a == 0:
            return None
        lead = a.bit_length() - 1
        for p in list(piv):
            pa, pb = piv[p]
            if (pa >> lead) & 1:
                piv[p] = (pa ^ a, pb ^ b)
        piv[lead] = (a, b)
    inv = [0] * h
    for p, (a, b) in piv.items():
        if a != (1 << p):
            return None
        inv[p] = b
    return inv


def mat_transpose(cols, h):
    return [sum(((cols[r] >> j) & 1) << r for r in range(h)) for j in range(h)]


def lagrangian(sub, h):
    """L_W = {(u, u+p): u in W, p in W^perp} encoded as x | z << h."""
    return span([u | (u << h) for u in sub] + [p << h for p in perp(sub, h)])


def symp(a, b, h):
    mask = (1 << h) - 1
    return parity((a & mask) & (b >> h)) ^ parity((a >> h) & (b & mask))


# ----------------------------------------------------------------------------
# Parsing (borrow word and canonical word) into one internal program shape
# ----------------------------------------------------------------------------

def is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def dyadic(q):
    return q.denominator & (q.denominator - 1) == 0


def unit(q):
    a = abs(q.numerator)
    return a > 0 and a & (a - 1) == 0 and dyadic(q)


def regs_of(item):
    if item[0] == 'add':
        return (item[1], item[2])
    return (item[1],)


def conv_gate(g, frame_of, where, allow_warp=False):
    need(isinstance(g, list) and g, 'format', 'gate is not a list at %s' % where)
    op = g[0]
    if op == 'add':
        need(len(g) == 6 and all(is_int(x) for x in g[1:5]), 'format', 'bad add at %s' % where)
        need(g[4] > 0 and g[3] != 0, 'format', 'bad add coefficient at %s' % where)
        q = Fraction(g[3], g[4])
        need(dyadic(q), 'format', 'non-dyadic coefficient at %s' % where)
        need(g[1] != g[2], 'format', 'self add at %s' % where)
        return ('add', g[1], g[2], q, frame_of(g[5]))
    if op == 'scale':
        need(len(g) == 5 and all(is_int(x) for x in g[1:4]), 'format', 'bad scale at %s' % where)
        need(g[3] != 0 and g[2] != 0, 'format', 'zero scale at %s' % where)
        q = Fraction(g[2], g[3])
        need(unit(q), 'format', 'scale is not a dyadic unit at %s' % where)
        return ('scale', g[1], q, frame_of(g[4]))
    if op == 'warp' and allow_warp:
        need(len(g) == 4 and is_int(g[1]) and is_int(g[2]) and g[2] != 0, 'format', 'bad warp item at %s' % where)
        return ('warp', g[1], g[2], frame_of(g[3]))
    raise Reject('format', 'unknown primitive %r at %s' % (op, where))


def parse_borrow(w):
    need(w.get('kind') == 'BORROW-WORD', 'format', 'not a BORROW-WORD')
    rep = w['report']
    v, h, R = rep['v'], rep['h'], rep['R']
    need((v, h, R) == (112, 9, 480), 'format', 'unexpected geometry')
    n = 2 * v + R
    full = span([1 << i for i in range(h)])

    def frame_lit(F):
        if F is None:
            return None
        need(isinstance(F, list) and all(is_int(x) and 0 < x < (1 << h) for x in F), 'format', 'bad frame literal')
        return span(F)

    ports = w['ports']
    need(len(ports) == v and all(is_int(p) and 0 < p < (1 << h) for p in ports), 'format', 'ports')
    removed = w['removed']
    need(len(set(removed)) == len(removed) and all(2 * v <= r < n for r in removed), 'format', 'removed helpers')
    removed = set(removed)
    live = [r for r in range(n) if r not in removed]
    start, end = {}, {}
    for i in range(v):
        start[i] = span([ports[i]])
        end[i] = full
        start[v + i] = ()
        end[v + i] = perp(span([ports[i]]), h)
    for r in live:
        if r >= 2 * v:
            start[r] = ()
            end[r] = full
    for k, F in w['start_extra'].items():
        r = int(k)
        need(r in start and r >= 2 * v, 'format', 'start_extra names a non-live/non-helper register %s' % k)
        start[r] = frame_lit(F)
    restored = set()
    for k, F in w['helper_final'].items():
        r = int(k)
        need(r in end and r >= 2 * v, 'format', 'helper_final names a non-live/non-helper register %s' % k)
        end[r] = frame_lit(F)
        restored.add(r)
    need(w.get('initial_corrections') == [], 'anticipatory',
         'initial (anticipatory) corrections present; this checker covers the zero-correction case only')
    sec = {}
    for name in ('precondition', 'compensation', 'A', 'cut', 'B', 'restore'):
        sec[name] = [conv_gate(g, frame_lit, '%s[%d]' % (name, i)) for i, g in enumerate(w[name])]
    cleanup = [conv_gate(g, frame_lit, 'cleanup[%d]' % i, allow_warp=True) for i, g in enumerate(w['cleanup'])]
    warps = []
    for k, rec in enumerate(w['warps'], 1):
        need(isinstance(rec, list) and len(rec) == 5, 'format', 'warp record %d shape' % k)
        pos, L, cols, U, E = rec
        need(is_int(pos) and 0 <= pos <= len(sec['B']), 'format', 'warp %d position' % k)
        need(is_int(L), 'format', 'warp %d lender' % k)
        need(isinstance(cols, list) and len(cols) == h and all(is_int(c) and 0 <= c < (1 << h) for c in cols),
             'format', 'warp %d G columns' % k)
        need(isinstance(U, list) and isinstance(E, list) and all(is_int(x) and 0 < x < (1 << h) for x in U + E),
             'format', 'warp %d frames' % k)
        warps.append(dict(op=k, pos=pos, lender=L, G=list(cols), U_list=list(U), E_list=list(E),
                          U=span(U), E=span(E)))
    by_pos = {}
    for wr in warps:
        by_pos.setdefault(wr['pos'], []).append(wr)
    items = []
    for p in range(len(sec['B']) + 1):
        for wr in by_pos.get(p, []):
            items.append(('warp', wr['lender'], wr['op'], wr['U'], wr['E']))
        if p < len(sec['B']):
            items.append(sec['B'][p])
    return dict(kind='borrow', v=v, h=h, R=R, n=n, full=full, ports=ports, live=live, removed=removed,
                start=start, end=end, restored=restored, buffers=set(r + n for r in restored),
                centers=list(w['centers']), center_frames=[frame_lit(F) for F in w['center_frames']],
                target_levels={int(k): frame_lit(F) for k, F in w['target_levels'].items()},
                pre=sec['precondition'] + sec['compensation'], n_pre=len(sec['precondition']),
                A=sec['A'], cut=sec['cut'], B_items=items, post=sec['restore'], cleanup=cleanup,
                warps=warps, sections=sec,
                claimed_profile={int(k): c for k, c in rep['local_profile'].items()},
                claimed_inventory={int(k): c for k, c in rep['width_inventory'].items()})


def parse_canonical(c):
    v, h, R = c['v'], c['h'], c['R']
    need((v, h, R) == (112, 9, 480), 'format', 'unexpected canonical geometry')
    n = 2 * v + R
    full = span([1 << i for i in range(h)])
    frames = []
    for F in c['frames']:
        need(isinstance(F, list) and all(is_int(x) and 0 < x < (1 << h) for x in F), 'format', 'canonical frame')
        need(len(span(F)) == len(F), 'format', 'canonical frame basis is dependent')
        frames.append(span(F))

    def frame_idx(F):
        if F is None:
            return None
        need(is_int(F) and 0 <= F < len(frames), 'format', 'canonical frame index')
        return frames[F]

    ports = c['ports']
    need(len(c['start']) == n and len(c['final']) == n, 'format', 'canonical start/final length')
    start = {r: frames[c['start'][r]] for r in range(n)}
    end = {r: frames[c['final'][r]] for r in range(n)}
    for i in range(v):
        need(start[i] == span([ports[i]]), 'format', 'canonical X start is not its port line')
        need(end[i] == full, 'format', 'canonical X end is not FULL')
        need(start[v + i] == (), 'format', 'canonical Y start is not 0')
        need(end[v + i] == perp(span([ports[i]]), h), 'format', 'canonical Y end is not port-perp')
    sec = {}
    for name in ('precondition', 'compensation', 'A', 'cut', 'B', 'tail', 'cleanup'):
        sec[name] = [conv_gate(g, frame_idx, 'canon %s[%d]' % (name, i)) for i, g in enumerate(c[name])]
    return dict(kind='canonical', v=v, h=h, R=R, n=n, full=full, ports=ports, live=list(range(n)),
                removed=set(), start=start, end=end, restored=set(), buffers=set(),
                centers=list(c['centers']), center_frames=[frames[i] for i in c['center_frames']],
                target_levels={int(k): frame_idx(F) for k, F in c['target_levels'].items()},
                pre=sec['precondition'] + sec['compensation'], n_pre=len(sec['precondition']),
                A=sec['A'], cut=sec['cut'], B_items=list(sec['B']), post=sec['tail'], cleanup=sec['cleanup'],
                warps=[], sections=sec, frames=frames,
                claimed_profile={int(k): x for k, x in c['local_profile'].items()}, claimed_inventory=None)


# ----------------------------------------------------------------------------
# Check 1: warp algebra
# ----------------------------------------------------------------------------

def check_warp(wr, h, live, v):
    k = wr['op']
    cols = wr['G']
    inv = mat_inverse(cols, h)
    need(inv is not None, 'warp', 'warp %d: G is singular over GF(2)' % k)
    need(all(mat_apply(cols, inv[t]) == 1 << t and mat_apply(inv, cols[t]) == 1 << t for t in range(h)),
         'warp', 'warp %d: inverse witness' % k)
    U, E = wr['U'], wr['E']
    need(len(U) == len(wr['U_list']) and len(E) == len(wr['E_list']), 'warp',
         'warp %d: U or E list is linearly dependent' % k)
    need(len(U) == len(E), 'warp', 'warp %d: dim U != dim E' % k)
    need(span([mat_apply(cols, u) for u in U]) == E, 'warp', 'warp %d: G span U != span E' % k)
    git = mat_transpose(inv, h)  # G^{-T}
    mask = (1 << h) - 1

    def M(vec):
        x, z = vec & mask, vec >> h
        gx = mat_apply(cols, x)
        return gx | ((gx ^ mat_apply(git, x) ^ mat_apply(git, z)) << h)

    gens = [1 << i for i in range(2 * h)]
    imgs = [M(g) for g in gens]
    need(len(span(imgs)) == 2 * h, 'warp', 'warp %d: K_G singular' % k)
    for a in range(2 * h):
        for b in range(a + 1, 2 * h):
            need(symp(imgs[a], imgs[b], h) == symp(gens[a], gens[b], h), 'warp', 'warp %d: K_G not symplectic' % k)
    full = span([1 << i for i in range(h)])
    L0, LF, LU, LE = lagrangian((), h), lagrangian(full, h), lagrangian(U, h), lagrangian(E, h)
    need(len(L0) == len(LF) == len(LU) == len(LE) == h, 'warp', 'warp %d: Lagrangian dimension' % k)
    need(span([M(x) for x in L0]) == L0, 'warp', 'warp %d: K_G does not fix L_0' % k)
    need(span([M(x) for x in LF]) == LF, 'warp', 'warp %d: K_G does not fix L_FULL' % k)
    MLU = span([M(x) for x in LU])
    rank_in = h - (len(LE) + len(MLU) - dim_sum(LE, MLU))
    need(MLU == LE and rank_in == 0, 'warp', 'warp %d: K_G L_U != L_E (Fourier rank %d)' % (k, rank_in))
    need(span([mat_apply(git, p) for p in perp(U, h)]) == perp(E, h), 'warp', 'warp %d: G^-T U^perp != E^perp' % k)
    need(wr['lender'] in live and not (v <= wr['lender'] < 2 * v), 'warp',
         'warp %d: lender must be a live non-target register' % k)
    # Fourier distance of a plain frame change U -> E (what the transition would cost without K_G)
    plain = h - (2 * h - dim_sum(LU, LE))
    by_formula = len(U) + len(E) - 2 * (len(U) + len(E) - dim_sum(U, E))
    need(plain == by_formula, 'warp', 'warp %d: Lagrangian distance lemma inconsistency' % k)
    return dict(op=k, pos=wr['pos'], lender=wr['lender'], dim=len(U), plain_fourier_distance=plain,
                U_eq_E=(U == E), U_in_E=contains(U, E))


def check_all_warps(P):
    out = [check_warp(wr, P['h'], set(P['live']), P['v']) for wr in P['warps']]
    lenders = [wr['lender'] for wr in P['warps']]
    need(len(set(lenders)) == len(lenders), 'warp', 'a register lends twice')
    return out


# ----------------------------------------------------------------------------
# Check 2: frame legality and paid-profile recount
# ----------------------------------------------------------------------------

def frame_check(P, charge_warps=False, warp_as_climb=()):
    v, full = P['v'], P['full']
    cur = {r: P['start'][r] for r in P['live']}
    paid, climbs, copies, warp_charge = Counter(), Counter(), Counter(), Counter()
    per_reg = Counter()
    istarget = lambda r: v <= r < 2 * v

    def climb(r, F, where):
        need(r in cur, 'frame', 'register %d is not live (%s)' % (r, where))
        old = cur[r]
        need(contains(old, F), 'frame', 'non-nested climb of %d at %s: %r -> %r' % (r, where, old, F))
        d = len(F) - len(old)
        if d:
            paid[d] += 1
            climbs[d] += 1
            per_reg[r] += d
        cur[r] = F

    for i, g in enumerate(P['pre']):
        need(g[-1] == (), 'frame', 'precondition/compensation gate %d not at frame 0' % i)
        need(istarget(g[1]), 'frame', 'precondition/compensation gate %d writes a non-target' % i)
        for r in regs_of(g):
            climb(r, (), 'pre[%d]' % i)
    for i, g in enumerate(list(P['A']) + [it for it in P['B_items'] if it[0] != 'warp'] + list(P['post'])):
        need(not (g[0] == 'add' and not istarget(g[1]) and istarget(g[2])), 'frame',
             'a non-target register reads a target (item %d of A+B+post)' % i)
    for i, g in enumerate(P['A']):
        need(g[-1] is not None, 'frame', 'unframed gate in A')
        for r in regs_of(g):
            climb(r, g[-1], 'A[%d]' % i)
    for t in range(v):
        need(cur[v + t] == P['target_levels'].get(t, ()), 'frame', 'target %d not at its level after A' % t)
    need(len(set(P['centers'])) == len(P['centers']) == len(P['center_frames']), 'frame', 'centres')
    for q, U in zip(P['centers'], P['center_frames']):
        need(q in cur and cur[q] == U, 'frame', 'centre %d not at its centre frame after A' % q)
    served = dict((q, set()) for q in P['centers'])
    for i, g in enumerate(P['cut']):
        need(g[0] == 'add' and g[-1] is None, 'frame', 'cut[%d] is not an unframed add' % i)
        t, s = g[1], g[2]
        need(istarget(t) and s in served, 'frame', 'cut[%d] must add a centre into a target' % i)
        need(cur[t] == P['target_levels'].get(t - v, ()), 'frame', 'cut[%d] target off its level' % i)
        served[s].add(cur[t])
    for q, U in zip(P['centers'], P['center_frames']):
        prev = U
        for T in sorted(served[q], key=lambda S: (-len(S), S)):
            need(contains(T, prev), 'frame', 'centre %d copy levels not nested' % q)
            if T != prev:
                paid[len(prev) - len(T)] += 1
                copies[len(prev) - len(T)] += 1
            prev = T
    for i, it in enumerate(P['B_items']):
        if it[0] == 'warp':
            _, L, k, U, E = it
            need(L in cur and not istarget(L), 'frame', 'warp %d lender %d not a live non-target' % (k, L))
            if k in warp_as_climb:
                climb(L, E, 'warp %d treated as an ordinary climb' % k)
                continue
            need(cur[L] == U, 'frame', 'warp %d: lender %d frame %r != U %r' % (k, L, cur[L], U))
            if charge_warps:
                d = len(U) + len(E) - 2 * (len(U) + len(E) - dim_sum(U, E))
                if d:
                    paid[d] += 1
                    warp_charge[d] += 1
            cur[L] = E
        else:
            need(it[-1] is not None, 'frame', 'unframed gate in B')
            for r in regs_of(it):
                climb(r, it[-1], 'B item %d' % i)
    for i, g in enumerate(P['post']):
        need(g[-1] is not None, 'frame', 'unframed gate after B')
        for r in regs_of(g):
            climb(r, g[-1], 'post-B[%d]' % i)
    for r in P['live']:
        climb(r, P['end'][r], 'end frame')
    for i, it in enumerate(P['cleanup']):
        need(it[-1] == full, 'frame', 'cleanup item %d not at FULL' % i)
        rr = (it[1],) if it[0] == 'warp' else regs_of(it)
        for r in rr:
            if r in P['buffers']:
                continue
            need(r in cur and cur[r] == full, 'frame',
                 'cleanup item %d touches register %d whose frame is not FULL' % (i, r))
    for r in P['live']:
        need(per_reg[r] == len(P['end'][r]) - len(P['start'][r]), 'frame', 'per-register charge != width for %d' % r)
    helpers = [r for r in P['live'] if r >= 2 * v]
    inventory = Counter(len(P['end'][r]) - len(P['start'][r]) for r in helpers)
    return dict(paid=paid, climbs=climbs, copies=copies, warp_charge=warp_charge, inventory=inventory,
                helpers=len(helpers), widths=[len(P['end'][r]) - len(P['start'][r]) for r in sorted(helpers)],
                mass=sum(k * c for k, c in paid.items()))


# ----------------------------------------------------------------------------
# Check 3: exact replay over the free-group algebra Q<F_43>
# ----------------------------------------------------------------------------

ONE = Fraction(1)


def replay(P, dual=False):
    v, n = P['v'], P['n']
    rows = {}
    for r in P['live']:
        rows[r] = {(r, ()): ONE}
    for b in P['buffers']:
        rows[b] = {}
    istarget = lambda r: v <= r < 2 * v

    def row(r):
        need(r in rows, 'replay', 'unknown register %d' % r)
        return rows[r]

    def do(it):
        kind = it[0]
        if kind == 'add':
            t, s, c = it[1], it[2], it[3]
            if dual:
                t, s, c = s, t, -c
            src, dst = row(s), row(t)
            for key, val in src.items():
                nv = dst.get(key, 0) + c * val
                if nv:
                    dst[key] = nv
                else:
                    del dst[key]
        elif kind == 'scale':
            t, c = it[1], it[2]
            if dual:
                c = 1 / c
            rr = row(t)
            for key in rr:
                rr[key] = rr[key] * c
        elif kind == 'warp':
            reg, k = it[1], it[2]
            letter = (abs(k), 1 if dual else 0, 1 if k > 0 else -1)
            inverse = (letter[0], letter[1], -letter[2])
            old = row(reg)
            new = {}
            for (var, word), val in old.items():
                nw = word[1:] if (word and word[0] == inverse) else (letter,) + word
                new[(var, nw)] = val
            rows[reg] = new
        else:
            raise Reject('replay', 'unknown item')

    before = list(P['pre']) + list(P['A']) + list(P['cut'])
    for it in before:
        do(it)
    for it in P['B_items']:
        if it[0] == 'warp':
            do(('warp', it[1], it[2]))
        else:
            do(it)
    for it in P['post']:
        do(it)
    diag = {}
    need(all(not rows[b] for b in P['buffers']), 'replay', 'a buffer is non-zero before cleanup')
    if not dual:
        for t in range(v):
            need(rows[v + t] == {(v + t, ()): ONE, (t, ()): ONE}, 'replay', 'target %d not final before cleanup' % t)
        for r in P['restored']:
            need(rows[r] == {(r, ()): ONE}, 'replay', 'restored cold register %d is not its own input' % r)
        readers = [r for r in P['live'] if r not in P['restored'] and not istarget(r)
                   and any(var in P['restored'] for var, _ in rows[r])]
        need(not readers, 'replay', 'restored inputs still read by %r' % readers[:5])
        diag['rows_with_operator_words_before_cleanup'] = sum(
            1 for r in P['live'] if any(word for _, word in rows[r]))
    peak = 0
    first_live = last_live = None
    span_of = {}
    noop_buffer_reads = 0
    for i, it in enumerate(P['cleanup']):
        if it[0] == 'add':
            src = it[2] if not dual else it[1]
            if src in P['buffers'] and not rows[src]:
                noop_buffer_reads += 1
        do(it)
        live_buffers = 0
        for b in P['buffers']:
            if rows[b]:
                live_buffers += 1
                lo, hi = span_of.get(b, (i, i))
                span_of[b] = (min(lo, i), i)
        if live_buffers:
            first_live = i if first_live is None else first_live
            last_live = i
        peak = max(peak, live_buffers)
    events = sorted([(lo, 1) for lo, hi in span_of.values()] + [(hi + 1, -1) for lo, hi in span_of.values()])
    overlap = best = 0
    for _, d in events:
        overlap += d
        best = max(best, overlap)
    diag['buffers_ever_nonzero'] = len(span_of)
    diag['max_overlap_of_buffer_lifetimes'] = best
    diag['cleanup_adds_reading_a_zero_buffer'] = noop_buffer_reads
    for r in P['live']:
        if dual:
            exp = {(r, ()): ONE, (r + v, ()): -ONE} if r < v else {(r, ()): ONE}
        else:
            exp = {(r, ()): ONE, (r - v, ()): ONE} if istarget(r) else {(r, ()): ONE}
        need(rows[r] == exp, 'replay', 'final map wrong on register %d (%s)' % (r, 'dual' if dual else 'forward'))
    need(all(not rows[b] for b in P['buffers']), 'replay', 'a zero buffer is not returned to zero')
    diag.update(peak_nonzero_buffers=peak, buffer_nonzero_window=[first_live, last_live],
                buffers=len(P['buffers']), independent_inputs=len(P['live']))
    return diag


# ----------------------------------------------------------------------------
# Links between the borrowed word, its canonical base, witness, providers, 566 word
# ----------------------------------------------------------------------------

def coef(g):
    return g[3] if g[0] == 'add' else g[2]


def norm(g):
    return (g[0],) + tuple(regs_of(g)) + (coef(g), g[-1])


def link_checks(tag, P, C, wit, blocks, providers, fr):
    out = {}
    need(P['ports'] == C['ports'] and P['centers'] == C['centers'], 'link', 'ports/centres differ from canonical')
    need(P['center_frames'] == C['center_frames'], 'link', 'centre frames differ from canonical')
    removed = P['removed']
    touches = lambda g: any(r in removed for r in regs_of(g))
    need(not any(touches(g) for g in C['sections']['compensation']), 'link',
         'canonical compensation reads a removed helper (a removed helper has non-zero response)')
    for name in ('precondition', 'compensation', 'A', 'cut'):
        kept = [norm(g) for g in C['sections'][name] if not touches(g)]
        need([norm(g) for g in P['sections'][name]] == kept, 'link', 'section %s != canonical minus removed' % name)
        out['canonical_%s_gates_dropped' % name] = len(C['sections'][name]) - len(kept)
    v, n, h = P['v'], P['n'], P['h']
    for r in P['live']:
        if r >= 2 * v:
            need(P['start'][r] == C['start'][r], 'link', 'start frame of %d differs from canonical' % r)
    for r in P['restored']:
        need(P['end'][r] == C['end'][r], 'link', 'cold end frame of %d differs from canonical' % r)
    canon_cold = [r for r in range(2 * v, n) if len(C['end'][r]) < h]
    out['canonical_cold_helpers'] = len(canon_cold)
    out['canonical_cold_helpers_ending_FULL_after_borrowing'] = sorted(
        r for r in canon_cold if r not in removed and r not in P['restored'])
    # exact mass bookkeeping: local mass = sum of all register widths + COPY mass, so the saving must equal
    # (canonical widths of removed helpers) - (width added to canonical cold helpers that now end at FULL)
    grown = sum(len(P['end'][r]) - len(C['end'][r]) for r in out['canonical_cold_helpers_ending_FULL_after_borrowing'])
    removed_widths = sum(len(C['end'][r]) - len(C['start'][r]) for r in removed)
    others_same = all(P['start'][r] == C['start'][r] and P['end'][r] == C['end'][r] for r in P['live']
                      if r not in out['canonical_cold_helpers_ending_FULL_after_borrowing'])
    need(others_same, 'link', 'some other register changed its start/end frame')
    out['mass_identity'] = dict(removed_widths=removed_widths, width_added_to_cold_now_FULL=grown,
                                predicted_saving=removed_widths - grown)
    high = set()
    low = set()
    for bl in blocks['sources'][0]['blocks']:
        high |= set(bl['high'])
        low |= set(bl['low'])
    need(removed <= high and not (removed & low), 'link', 'removed helpers are not all high helpers')
    out['high_helpers_in_blocks'] = len(high)
    old_w = Counter(len(C['end'][r]) - len(C['start'][r]) for r in removed)
    out['removed_old_widths'] = dict(sorted(old_w.items()))
    need(dict(old_w) == CLAIMS['removed_old_widths'][tag], 'link', 'removed helper canonical widths %r' % dict(old_w))
    # witness: pairs <-> warp records
    need(wit['initial_corrections'] == [], 'link', 'witness has initial corrections')
    pairs = wit['pairs']
    need(len(pairs) == len(P['warps']), 'link', 'witness pair count')
    gauss = dict((g['operator'], g['G_columns']) for g in wit['gaussian']['records'])
    for wr, pr in zip(P['warps'], pairs):
        k = wr['op']
        need(pr['borrow_from'] == wr['lender'], 'link', 'warp %d lender != witness borrow_from' % k)
        need(gauss.get(k) == wr['G'], 'link', 'warp %d G != witness Gaussian record' % k)
        need(span(pr['retirement_basis']) == wr['U'], 'link', 'warp %d U != witness retirement basis' % k)
        need(span(pr['handoff_basis']) == wr['E'], 'link', 'warp %d E != witness handoff basis' % k)
        need(pr['anticipate'] is False and pr['low'] is False and pr['handoff_paid_rank'] == 0, 'link',
             'warp %d witness flags' % k)
    need(set(p['register'] for p in pairs) == removed, 'link', 'witness registers != removed set')
    # B multiset: canonical B plus the 48 moved tail gates, with each removed helper renamed to its lender
    rename = dict((p['register'], p['borrow_from']) for p in pairs)
    def ren(g):
        if g[0] == 'add':
            return ('add', rename.get(g[1], g[1]), rename.get(g[2], g[2]), g[3], g[4])
        return ('scale', rename.get(g[1], g[1]), g[2], g[3])
    moved = [C['sections']['tail'][e['old_tail_index']] for e in wit['early_tail_events']]
    lhs = Counter(norm(ren(g)) for g in list(C['sections']['B']) + moved)
    rhs = Counter(norm(it) for it in P['B_items'] if it[0] != 'warp')
    out['B_multiset_equals_canonical_B_plus_moved_tail_renamed'] = (lhs == rhs)
    need(lhs == rhs, 'link', 'B multiset != canonical B + moved tail (renamed)')
    out['moved_tail_gates'] = len(moved)
    # providers (interface to the owner fill)
    need(providers['widths'] == fr['widths'], 'link', 'BORROW-PROVIDERS widths != recount')
    need(dict((int(k), c) for k, c in providers['actual_paid_profile'].items()) == dict(fr['paid']), 'link',
         'BORROW-PROVIDERS paid profile != recount')
    out['providers_widths_match'] = True
    return out


def link_566(C, o):
    """Canonical word == predecessor 566 word up to a register permutation and a linear frame map."""
    h = C['h']
    pi = {}
    pairs = {}

    def lit(F):
        return None if F is None else span(F)

    def add_pair(a, b, where):
        need((a is None) == (b is None), 'link566', 'frame presence differs at %s' % where)
        if a is not None:
            need(pairs.setdefault(a, b) == b, 'link566', 'inconsistent frame pair at %s' % where)

    def align(cg, og, where):
        need(cg[0] == og[0], 'link566', 'op differs at %s' % where)
        oc = conv_gate(og, lit, where)
        need(coef(cg) == coef(oc), 'link566', 'coefficient differs at %s' % where)
        for x, y in zip(regs_of(cg), regs_of(oc)):
            need(pi.setdefault(x, y) == y, 'link566', 'register map conflict at %s' % where)
        add_pair(cg[-1], oc[-1], where)

    for name in ('precondition', 'A', 'cut', 'B'):
        need(len(C['sections'][name]) == len(o[name]), 'link566', 'length of %s' % name)
        for i, (cg, og) in enumerate(zip(C['sections'][name], o[name])):
            align(cg, og, '%s[%d]' % (name, i))
    early = o['early_cleanup']
    eidx = [e[0] for e in early]
    need(len(set(eidx)) == len(eidx) == len(C['sections']['tail']), 'link566', 'early cleanup count')
    rest = [g for i, g in enumerate(o['cleanup']) if i not in set(eidx)]
    need(len(rest) == len(C['sections']['cleanup']), 'link566', 'cleanup length')
    for i, (cg, og) in enumerate(zip(C['sections']['cleanup'], rest)):
        align(cg, og, 'cleanup[%d]' % i)
    for i, (cg, (j, F)) in enumerate(zip(C['sections']['tail'], early)):
        og = list(o['cleanup'][j][:-1]) + [F]
        align(cg, og, 'tail[%d]' % i)
    need(len(pi) == C['n'] and len(set(pi.values())) == C['n'], 'link566', 'register map is not a bijection')
    v = C['v']
    need(all((x < v) == (y < v) and (x < 2 * v) == (y < 2 * v) for x, y in pi.items()), 'link566', 'roles not preserved')
    need(all(x == y for x, y in pi.items() if x >= 2 * v), 'link566', 'helpers renumbered')
    # linear frame map tau from 1-dim pairs, then verified on every frame
    ones = [(a[0], b[0]) for a, b in pairs.items() if len(a) == 1 and b is not None and len(b) == 1]
    piv = {}
    for a, b in ones:
        x, y = a, b
        for p in list(piv):
            pa, pb = piv[p]
            if (x >> p) & 1:
                x ^= pa
                y ^= pb
        if x:
            lead = x.bit_length() - 1
            for p in list(piv):
                pa, pb = piv[p]
                if (pa >> lead) & 1:
                    piv[p] = (pa ^ x, pb ^ y)
            piv[lead] = (x, y)
    need(len(piv) == h, 'link566', 'one-dimensional frame pairs do not span F_2^h')
    tau = [0] * h
    for p, (a, b) in piv.items():
        need(a == 1 << p, 'link566', 'tau construction')
        tau[p] = b
    need(mat_inverse(tau, h) is not None, 'link566', 'tau singular')
    tmap = lambda S: span([mat_apply(tau, x) for x in S])
    for a, b in pairs.items():
        need(tmap(a) == b, 'link566', 'frame pair not induced by the linear map tau')
    for i in range(v):
        need(mat_apply(tau, C['ports'][i]) == o['ports'][pi[i]], 'link566', 'port %d' % i)
    need([pi[q] for q in C['centers']] == o['centers'], 'link566', 'centres')
    need([tmap(F) for F in C['center_frames']] == [span(F) for F in o['center_frames']], 'link566', 'centre frames')
    full = C['full']
    for r in range(2 * v, C['n']):
        os_ = span(o['start_extra'][str(r)]) if str(r) in o['start_extra'] else ()
        oe = span(o['helper_final'][str(r)]) if str(r) in o['helper_final'] else full
        need(tmap(C['start'][r]) == os_, 'link566', 'helper start %d' % r)
        need(tmap(C['end'][r]) == oe, 'link566', 'helper end %d' % r)
    need(dict((int(k), c) for k, c in o['report']['local_profile'].items()) == C['claimed_profile'], 'link566',
         'canonical local_profile != 566 report local_profile')
    return dict(register_permutation_nonidentity=sum(1 for x, y in pi.items() if x != y),
                frame_map_tau_columns=tau, aligned_frame_pairs=len(pairs))


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------

def dsort(c):
    return dict((str(k), c[k]) for k in sorted(c))


def expect_reject(name, target, fn, results, also=None):
    """Run fn (which must raise Reject from check family `target`)."""
    entry = dict(control=name, target_check=target)
    try:
        fn()
        entry.update(rejected=False)
    except Reject as e:
        entry.update(rejected=True, by=e.check, reason=e.msg[:200])
    entry['ok'] = bool(entry['rejected'] and entry.get('by') == target)
    if also is not None:
        info = {}
        for label, g in also:
            try:
                g()
                info[label] = 'accepted'
            except Reject as e:
                info[label] = 'rejected[%s]' % e.check
        entry['other_checks'] = info
    results.append(entry)
    print('  control %-58s target=%-8s %s' % (name, target, 'REJECTED-OK' if entry['ok'] else 'NOT-OK ' + str(entry)), flush=True)
    return entry['ok']


def mutate_P(P):
    Q = dict(P)
    for key in ('pre', 'A', 'cut', 'B_items', 'post', 'cleanup'):
        Q[key] = list(P[key])
    Q['warps'] = [dict(w) for w in P['warps']]
    return Q


def profile_check(P, fr, claim):
    need(dict(fr['paid']) == P['claimed_profile'], 'profile', 'recount %r != word report %r' % (dsort(fr['paid']), P['claimed_profile']))
    need(dict(fr['paid']) == claim, 'profile', 'recount != claimed profile')


def controls_for(tag, P, claim, results):
    ok = True
    v = P['v']
    warps = P['warps']
    # pick a warp with U != E and its B-item index
    k0 = next(w['op'] for w in warps if w['U'] != w['E'])
    # 1. drop one warp from the forward word (cleanup keeps its inverse)
    Q = mutate_P(P)
    Q['B_items'] = [it for it in P['B_items'] if not (it[0] == 'warp' and it[2] == k0)]
    ok &= expect_reject('drop forward warp %d' % k0, 'replay', lambda: replay(Q), results,
                        also=[('frame', lambda: frame_check(Q))])
    # 2. drop one inverse warp in cleanup
    Q2 = mutate_P(P)
    j = next(i for i, it in enumerate(P['cleanup']) if it[0] == 'warp' and it[2] == -k0)
    del Q2['cleanup'][j]
    ok &= expect_reject('drop inverse warp %d in cleanup' % k0, 'replay', lambda: replay(Q2), results,
                        also=[('frame', lambda: frame_check(Q2))])
    # 3. perturb one coefficient (one dyadic step: c -> 2c) in B after the first warp, in compensation, in cleanup
    lender = next(w['lender'] for w in warps if w['op'] == k0)
    wi = next(i for i, it in enumerate(P['B_items']) if it[0] == 'warp' and it[2] == k0)
    bi = next(i for i in range(wi + 1, len(P['B_items'])) if P['B_items'][i][0] == 'add' and lender in regs_of(P['B_items'][i]))
    for label, key, idx in (('B item %d (lender %d after its warp)' % (bi, lender), 'B_items', bi),
                            ('compensation gate 0', 'pre', P['n_pre']),
                            ('first cleanup add between live registers', 'cleanup',
                             next(i for i, it in enumerate(P['cleanup'])
                                  if it[0] == 'add' and it[1] not in P['buffers'] and it[2] not in P['buffers']))):
        Q3 = mutate_P(P)
        g = list(Q3[key][idx])
        g[3] = g[3] * 2
        Q3[key][idx] = tuple(g)
        ok &= expect_reject('perturb coefficient x2: %s' % label, 'replay', lambda: replay(Q3), results,
                            also=[('frame', lambda: frame_check(Q3))])
    # 4a. treat the warp frame change as an ordinary climb (no K_G)
    ok &= expect_reject('warp %d as an ordinary climb U->E' % k0, 'frame',
                        lambda: frame_check(P, warp_as_climb=(k0,)), results)
    # 4b. charge every warp its plain Fourier distance d(L_U, L_E)
    def charged():
        fr = frame_check(P, charge_warps=True)
        profile_check(P, fr, claim)
    ok &= expect_reject('charge every warp as a climb of rank d(L_U,L_E)', 'profile', charged, results)
    # 5. swap two warp lenders (warps at one position with different U)
    pair = None
    for a in warps:
        for b in warps:
            if a['op'] < b['op'] and a['pos'] == b['pos'] and a['U'] != b['U']:
                pair = (a['op'], b['op'])
                break
        if pair:
            break
    need(pair is not None, 'control', 'no swappable warp pair')
    la = next(w['lender'] for w in warps if w['op'] == pair[0])
    lb = next(w['lender'] for w in warps if w['op'] == pair[1])
    Q5 = mutate_P(P)
    Q5['B_items'] = [(it[0], lb if it[1] == la else la, it[2], it[3], it[4])
                     if it[0] == 'warp' and it[2] in pair else it for it in P['B_items']]
    ok &= expect_reject('swap lenders of warps %d,%d' % pair, 'frame', lambda: frame_check(Q5), results,
                        also=[('replay', lambda: replay(Q5))])
    # 6. warp algebra: singular G, invertible G with G U != E, dimension mismatch
    def warp_mut(fn):
        wr = dict(warps[0])
        fn(wr)
        return lambda: check_warp(wr, P['h'], set(P['live']), v)

    def singular(wr):
        wr['G'] = list(wr['G'])
        wr['G'][1] = wr['G'][0]
    ok &= expect_reject('warp 1: singular G', 'warp', warp_mut(singular), results)

    def wrong_image(wr):
        h = P['h']
        for j in range(h):
            for i in range(h):
                if i == j:
                    continue
                G = list(wr['G'])
                G[j] ^= G[i]
                if mat_inverse(G, h) is not None and span([mat_apply(G, u) for u in wr['U']]) != wr['E']:
                    wr['G'] = G
                    return
        raise Reject('control', 'no wrong-image G found')
    ok &= expect_reject('warp 1: invertible G with G span U != span E', 'warp', warp_mut(wrong_image), results)

    def dim_drop(wr):
        wr['E_list'] = wr['E_list'][:-1]
        wr['E'] = span(wr['E_list'])
    ok &= expect_reject('warp 1: dim E != dim U', 'warp', warp_mut(dim_drop), results)
    # 7. cleanup reads a restored register directly instead of its zero buffer
    Q7 = mutate_P(P)
    j = next(i for i, it in enumerate(P['cleanup']) if it[0] == 'add' and (it[1] in P['buffers'] or it[2] in P['buffers']))
    it = list(P['cleanup'][j])
    if it[1] in P['buffers']:
        it[1] -= P['n']
    else:
        it[2] -= P['n']
    Q7['cleanup'][j] = tuple(it)
    ok &= expect_reject('cleanup item %d uses the restored register, not its buffer' % j, 'frame',
                        lambda: frame_check(Q7), results)
    # 8. delete one restore gate
    Q8 = mutate_P(P)
    del Q8['post'][0]
    ok &= expect_reject('delete restore gate 0', 'replay', lambda: replay(Q8), results)
    # 9. delete one T74 compensation gate (dirty helper inputs are live symbols)
    Q9 = mutate_P(P)
    del Q9['pre'][P['n_pre']]
    ok &= expect_reject('delete compensation gate 0', 'replay', lambda: replay(Q9), results)
    # 10. drop the cleanup adds that read a never-yet-written buffer: no-ops in the forward replay, but in the
    #     dual (s -= c t) they write the buffer, so only the dual replay can reject this
    Q10 = mutate_P(P)
    written, keep = set(), []
    for it in P['cleanup']:
        if it[0] == 'add' and it[2] in P['buffers'] and it[2] not in written:
            continue
        if it[0] == 'add' and it[1] in P['buffers']:
            written.add(it[1])
        keep.append(it)
    Q10['cleanup'] = keep
    ok &= expect_reject('drop %d forward-no-op cleanup adds (dual replay)' % (len(P['cleanup']) - len(keep)), 'replay',
                        lambda: replay(Q10, dual=True), results, also=[('forward replay', lambda: replay(Q10))])
    ok &= results[-1]['other_checks']['forward replay'] == 'accepted'   # they really are forward no-ops
    # positive mutation: re-express U and E of every warp in another basis of the same span
    Qp = mutate_P(P)
    rebased = []
    for wr in warps:
        w2 = dict(wr)
        if len(w2['U_list']) > 1:
            w2['U_list'] = [w2['U_list'][0] ^ w2['U_list'][1]] + w2['U_list'][1:]
            w2['E_list'] = w2['E_list'][1:] + [w2['E_list'][0] ^ w2['E_list'][-1]]
        w2['U'], w2['E'] = span(w2['U_list']), span(w2['E_list'])
        rebased.append(w2)
    entry = dict(control='positive: rebased warp U/E lists (same spans) accepted', target_check='warp+frame')
    try:
        for w2 in rebased:
            check_warp(w2, P['h'], set(P['live']), v)
        Qp['warps'] = rebased
        frp = frame_check(Qp)
        profile_check(Qp, frp, claim)
        entry.update(accepted=True, ok=True)
    except Reject as e:
        entry.update(accepted=False, ok=False, reason=str(e))
    print('  control %-58s %s' % (entry['control'], 'ACCEPTED-OK' if entry['ok'] else 'NOT-OK'), flush=True)
    results.append(entry)
    ok &= entry['ok']
    return ok


def main():
    ap = argparse.ArgumentParser(description='Independent check of PR2269 BORROW-WORD-43{base,extra}')
    ap.add_argument('--repo', default=DEFAULT_REPO, help='git checkout containing commit %s' % COMMIT)
    ap.add_argument('--blob-dir', default=None, help='directory with exported blobs (basename of each path)')
    ap.add_argument('--out', default=None, help='JSON receipt path (must be next to this script)')
    ap.add_argument('--skip-controls', action='store_true', help='skip negative controls (not a PASS run)')
    args = ap.parse_args()
    if sys.flags.optimize:
        print('refusing to run under -O')
        print(FAIL_LINE)
        return 2
    here = os.path.dirname(os.path.abspath(__file__))
    if args.out is not None:
        if os.path.dirname(os.path.abspath(args.out)) != here:
            print('--out must name a file next to this script (%s)' % here)
            print(FAIL_LINE)
            return 2
    t0 = time.time()
    receipt = dict(checker='words_check.py', object=dict(pr=2269, commit=COMMIT, package=PKG),
                   python=sys.version.split()[0], scope='task A: BORROW-WORD-43{base,extra} and new/borrow/inputs')
    ok = True
    try:
        js, pins, raw = load_inputs(args.repo, args.blob_dir)
        receipt['pins'] = pins
        print('pins: %d input blobs verified (sha256 + git blob id)' % len(pins), flush=True)
        words = {}
        for tag in ('base', 'extra'):
            claim = CLAIMS[tag]
            print('== word 43%s' % tag, flush=True)
            w = js['word_' + tag]
            res = dict(base_tag=w.get('base'))
            need(w.get('base') == claim['base_tag'], 'link', 'base tag')
            need(PINS['word566_' + tag][2].startswith(w['base']), 'link', 'base tag is not the 566 word sha256 prefix')
            P = parse_borrow(w)
            C = parse_canonical(js['canon_' + tag])
            # 1. warps
            wres = check_all_warps(P)
            res['warps'] = dict(count=len(wres), dims=dsort(Counter(x['dim'] for x in wres)),
                                positions=[x['pos'] for x in wres], lenders=[x['lender'] for x in wres],
                                lenders_that_are_X=[x['lender'] for x in wres if x['lender'] < P['v']],
                                lenders_that_are_restored_cold=[x['lender'] for x in wres if x['lender'] in P['restored']],
                                U_equal_E=sum(1 for x in wres if x['U_eq_E']),
                                U_inside_E=sum(1 for x in wres if x['U_in_E']),
                                plain_fourier_distance=dsort(Counter(x['plain_fourier_distance'] for x in wres)),
                                anticipatory_terms=len(w['initial_corrections']))
            need(len(wres) == CLAIMS['warps'], 'warp', 'warp count')
            print('  warps: %d PASS (dims %s); anticipatory terms %d' % (len(wres), res['warps']['dims'], len(w['initial_corrections'])), flush=True)
            # 2. frames + profile
            fr = frame_check(P)
            profile_check(P, fr, claim['profile'])
            need(dict(fr['inventory']) == CLAIMS['width_inventory'] == P['claimed_inventory'], 'profile', 'width inventory')
            need(fr['helpers'] == CLAIMS['helpers_after'] == P['R'] - len(P['removed']), 'profile', 'helper count')
            need(fr['mass'] == CLAIMS['mass'], 'profile', 'local mass')
            frc = frame_check(P, charge_warps=True)
            res['frames'] = dict(model_ok=True, paid_profile=dsort(fr['paid']), climbs=dsort(fr['climbs']),
                                 copy_charges=dsort(fr['copies']), local_mass=fr['mass'],
                                 width_inventory=dsort(fr['inventory']), helpers=fr['helpers'],
                                 if_warps_charged_profile=dsort(frc['paid']), if_warps_charged_mass=frc['mass'])
            print('  frames: PASS; paid %s (climbs %s + COPY %s), mass %d, helpers %d, inventory %s' % (
                res['frames']['paid_profile'], res['frames']['climbs'], res['frames']['copy_charges'], fr['mass'],
                fr['helpers'], res['frames']['width_inventory']), flush=True)
            # 3. replay
            rf = replay(P)
            rd = replay(P, dual=True)
            res['replay'] = dict(forward=rf, dual=rd)
            print('  replay: forward PASS %s; dual PASS' % rf, flush=True)
            # links
            res['links'] = link_checks(tag, P, C, js['witness_' + tag], js['blocks'],
                                       js['providers'][claim['providers_key']], fr)
            print('  links: PASS %s' % {k: v for k, v in res['links'].items() if k != 'canonical_cold_helpers_ending_FULL_after_borrowing'}, flush=True)
            # 5. positive control: canonical words
            frC = frame_check(C)
            need(dict(frC['paid']) == C['claimed_profile'] == claim['old_profile'], 'canonical',
                 'canonical profile not reproduced: %r' % dsort(frC['paid']))
            rC = replay(C)
            l566 = link_566(C, js['word566_' + tag])
            res['canonical'] = dict(paid_profile=dsort(frC['paid']), climbs=dsort(frC['climbs']),
                                    copy_charges=dsort(frC['copies']), local_mass=frC['mass'],
                                    width_inventory=dsort(frC['inventory']), helpers=frC['helpers'], replay=rC,
                                    link_566=l566)
            print('  canonical positive control: profile %s mass %d reproduced, replay PASS, 566-link PASS' % (
                res['canonical']['paid_profile'], frC['mass']), flush=True)
            res['saving'] = dict(mass_before=frC['mass'], mass_after=fr['mass'], helpers_before=frC['helpers'],
                                 helpers_after=fr['helpers'])
            need(frC['mass'] - fr['mass'] == res['links']['mass_identity']['predicted_saving'] and
                 frC['copies'] == fr['copies'], 'profile', 'saving does not match the width bookkeeping')
            if not args.skip_controls:
                results = []
                cok = controls_for(tag, P, claim['profile'], results)
                # canonical negative controls
                CQ = mutate_P(C)
                del CQ['pre'][C['n_pre']]
                cok &= expect_reject('canonical: delete compensation gate 0', 'replay', lambda: replay(CQ), results)
                CF = mutate_P(C)
                CF['post'] = list(C['post'])
                j = next(i for i, g in enumerate(C['post']) if g[-1] != C['full'])
                g = list(C['post'][j])
                g[-1] = C['full']
                CF['post'][j] = tuple(g)
                cok &= expect_reject('canonical: tail gate %d lifted to FULL (cold end violated)' % j, 'frame',
                                     lambda: frame_check(CF), results)
                o_mut = copy.deepcopy(js['word566_' + tag])
                o_mut['B'][0][-1] = o_mut['B'][1][-1] if span(o_mut['B'][1][-1]) != span(o_mut['B'][0][-1]) else [1]
                cok &= expect_reject('566 link: one 566 B-gate frame changed', 'link566',
                                     lambda: link_566(C, o_mut), results)
                bad = bytearray(raw['word_' + tag])
                bad[len(bad) // 2] ^= 1
                cok &= expect_reject('pin: one flipped bit in the word blob', 'pin',
                                     lambda: verify_pin('word_' + tag, bytes(bad)), results)
                res['controls'] = results
                res['controls_ok'] = bool(cok)
                ok &= bool(cok)
            words[tag] = res
        receipt['words'] = words
        fb, fe = words['base'], words['extra']
        bf = fb['replay']['forward']
        # the summary below speaks for both words: assert that the shared facts really are shared
        for key in ('dims', 'lenders', 'lenders_that_are_X', 'plain_fourier_distance', 'anticipatory_terms'):
            need(fb['warps'][key] == fe['warps'][key], 'summary', 'warp fact %s differs between words' % key)
        need(fb['replay']['forward'] == fe['replay']['forward'] and fb['replay']['dual'] == fe['replay']['dual'],
             'summary', 'buffer diagnostics differ between words')
        bd = fb['replay']['dual']
        need(fb['frames']['local_mass'] == fe['frames']['local_mass'] and
             fb['frames']['if_warps_charged_mass'] == fe['frames']['if_warps_charged_mass'], 'summary', 'mass differs')
        need(fb['links']['canonical_cold_helpers_ending_FULL_after_borrowing'] ==
             fe['links']['canonical_cold_helpers_ending_FULL_after_borrowing'], 'summary', 'cold-to-FULL list differs')
        need(fb['canonical']['helpers'] == fe['canonical']['helpers'] == CLAIMS['helpers_before'], 'summary',
             'unborrowed helper count')
        cold_full = fb['links']['canonical_cold_helpers_ending_FULL_after_borrowing']
        cold_lenders = sorted(set(cold_full) & set(fb['warps']['lenders']))
        ncomp = len(js['canon_base']['compensation'])
        receipt['findings'] = [
            'Both words: 43 warps pass the GF(2) checks (G invertible, dim U = dim E, G span U = span E, '
            'K_G symplectic, fixes L_0 and L_FULL, K_G L_U = L_E, Fourier rank 0); handoff dims %s; '
            '%d anticipatory/initial correction terms; the %d-gate T74 compensation is the canonical one '
            'unchanged (%d + %d gates dropped, i.e. none reads a removed helper).' % (
                fb['warps']['dims'], fb['warps']['anticipatory_terms'], ncomp,
                fb['links']['canonical_compensation_gates_dropped'], fe['links']['canonical_compensation_gates_dropped']),
            'Paid profiles recounted exactly: base %s, extra %s (climbs + COPY %s); mass %d both; '
            '%d helpers (from %d); width inventory %s.' % (
                fb['frames']['paid_profile'], fe['frames']['paid_profile'], fb['frames']['copy_charges'],
                fb['frames']['local_mass'], fb['frames']['helpers'], fb['canonical']['helpers'],
                fb['frames']['width_inventory']),
            'Exact replay over Q<F_43> in both orientations: Y_i <- Y_i + X_i, all other %d non-target registers (X and live helpers) restored, '
            '%d zero buffers returned to zero.' % (bf['independent_inputs'] - 112, bf['buffers']),
            'Canonical inputs reproduce the old profiles (base %s mass %d; extra %s mass %d), replay exactly, '
            'and equal the pinned 566 predecessor words up to a role-preserving register permutation and a '
            'linear frame map.' % (fb['canonical']['paid_profile'], fb['canonical']['local_mass'],
                                    fe['canonical']['paid_profile'], fe['canonical']['local_mass']),
            'README imprecision: "8 width-4, 35 width-5" holds for the base word; the extra word removes '
            'helpers of canonical widths %s.' % fe['links']['removed_old_widths'],
            'Canonical cold helpers %s end at FULL after borrowing (of these, %s also lend); with the removed '
            'widths this gives the exact mass savings %d (base) and %d (extra).' % (
                cold_full, cold_lenders,
                fb['canonical']['local_mass'] - fb['frames']['local_mass'],
                fe['canonical']['local_mass'] - fe['frames']['local_mass']),
            'Lenders that are source registers X: %s; lenders that are restored cold helpers: %s.' % (
                fb['warps']['lenders_that_are_X'], fb['warps']['lenders_that_are_restored_cold']),
            'Cleanup uses %d private zero buffers outside the helper inventory. Forward orientation: at most %d are '
            'non-zero simultaneously (max overlap of lifetimes %d); %d cleanup adds read a still-zero buffer (no-ops '
            'in the forward replay only: in the dual such an add writes the buffer, and dropping those that read a '
            'never-written buffer is rejected by the dual replay, see the controls). Dual orientation: at most %d '
            'non-zero simultaneously (%d ever non-zero). No paid child runs in '
            'cleanup. Peak helper-like fields during cleanup are %d+%d = %d (lazy, forward), %d+%d = %d (lazy, dual) '
            'or %d+%d = %d (eager); the unborrowed word uses %d. Whether the global accounting must host them is a '
            'global-model question that is not decided here.' % (
                bf['buffers'], bf['peak_nonzero_buffers'], bf['max_overlap_of_buffer_lifetimes'],
                bf['cleanup_adds_reading_a_zero_buffer'], bd['peak_nonzero_buffers'], bd['buffers_ever_nonzero'],
                fb['frames']['helpers'], bf['peak_nonzero_buffers'],
                fb['frames']['helpers'] + bf['peak_nonzero_buffers'], fb['frames']['helpers'],
                bd['peak_nonzero_buffers'], fb['frames']['helpers'] + bd['peak_nonzero_buffers'],
                fb['frames']['helpers'], bf['buffers'], fb['frames']['helpers'] + bf['buffers'],
                fb['canonical']['helpers']),
            'Charging each warp as a plain frame change (rank d(L_U,L_E), distances %s) would raise the local mass '
            'from %d to %d; the saving depends on rank-zero K_G handoffs, checked here only at the binary '
            'symplectic level.' % (fb['warps']['plain_fourier_distance'], fb['frames']['local_mass'],
                                   fb['frames']['if_warps_charged_mass']),
        ]
        receipt['not_checked'] = [
            'Exact Clifford (Gaussian-dyadic, unit quadratic phase) lifts of K_G and their native lowering; only the '
            'binary symplectic image is checked (it determines the Fourier rank by notes/general-clifford-frames.tex).',
            'Native word lowering, both hosted orientations at the native level, owner/window hosting of the 437 '
            'helpers and the 76 buffers, precision/tape, global profile, kappa and outer assembly.',
            'Provenance of the 566 predecessor words beyond their pinned blobs (they are taken as the old record inputs).',
        ]
        receipt['buffers_note'] = (
            'Each borrowed word uses %d private zero buffers (one per restored cold helper) only inside the '
            'FULL-frame cleanup; they are not among the 437 helpers of the width inventory. No paid child occurs '
            'in cleanup (all items at FULL).' % words['base']['replay']['forward']['buffers'])
        for line in receipt['findings']:
            print('FINDING: ' + line)
    except Reject as e:
        ok = False
        receipt['failure'] = str(e)
        print('FAILED: %s' % e, flush=True)
    receipt['skip_controls'] = bool(args.skip_controls)
    receipt['result'] = PASS_LINE if (ok and not args.skip_controls) else FAIL_LINE
    receipt['model'] = __doc__.split('MODEL (stated precisely; see also the receipt field "model").')[1].strip()
    print('elapsed %.1f s' % (time.time() - t0))
    if args.out is not None:
        with open(args.out, 'w') as fh:
            json.dump(receipt, fh, indent=1, sort_keys=True)
            fh.write('\n')
        print('receipt written: %s' % args.out)
    print(receipt['result'])
    return 0 if receipt['result'] == PASS_LINE else 1


if __name__ == '__main__':
    sys.exit(main())
