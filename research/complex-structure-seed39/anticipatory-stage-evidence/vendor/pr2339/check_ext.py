#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent check of the extended T74 borrow words BORROW-WORD-80{base,extra} (48 high + 32 LOW aliases,
64 anticipatory initial corrections) produced by build_ext.py in this package.

Objects under test (local files of this package, pinned below by sha256 and git blob id):
  words/BORROW-WORD-80base.json.gz, words/BORROW-WORD-80extra.json.gz,
  witness/witness_80_base.json, witness/witness_80_extra.json.
Reference inputs, read as git blobs at pinned commits (no copies are trusted):
  PR #2269 head b479fc55 (research/gmx-t74-borrow43/): canonical unborrowed T74 words, block certificate,
  43-alias witnesses and the BORROW-WORD-43 words (positive control), the pivot-566 predecessor words;
  PR #2226 head dacaf3d8 (research/anticipatory-dirty-borrowing/WITNESS.json): the 64 T8 correction terms.

Adapted from our own iteration-3 independent checker (fork commit 4a2f20ea339e30348448096ca789d0efe55df9bb,
research/t74-borrow43-independent-check/words_check.py, Apache-2.0, same authors).  The extension to LOW pairs
with anticipatory initial corrections is implemented from the WRITTEN semantics of PR2226 (PROOF.md sections
1-4 and README.md) only.  This file imports and runs no PR code and no code of build_ext.py / replay_core.py /
the vendored files; it shares no code with them.

Credit: PR2226 (Cinna Davis / @1337isnot1337, with OpenAI Codex) for anticipatory dirty borrowing, the alias
rule, initial monomial compensation and the free-operator replay idea; PR2269 (Jeremy Kothe / jeremykothe2) for
the T74 borrow43 package, canonical words, witnesses and the BORROW-WORD format; PR2260 (Dugongue) for the
concurrent high-alias application on the T8 parent; the T74 lineage PR1319/PR1297 (Rohan Arun), PR1625
(mdumitrean) and the pivot-554 kernel; Ali Romman's block certificate; icekylinx (Zhihao Chen) for the
Clifford-frame normal forms (notes/general-clifford-frames.tex) and the local-word checker lineage.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B check_ext.py [--repo PATH] [--out] [--skip-controls] [--skip-predecessor]
The final stdout line is PASS_T74_LOW_ALIAS_WORDS_INDEPENDENT or FAIL_T74_LOW_ALIAS_WORDS_INDEPENDENT.
--out writes check_ext.receipt.json next to this script.

MODEL (stated precisely; see also the receipt field "model").
 * Registers 0..v-1 are X (sources), v..2v-1 are Y (targets), 2v..2v+R-1 helpers; n = 2v+R.  Removed helpers
   do not exist.  A buffer register b = r+n exists only for r in helper_final (restored cold helpers) and only
   in cleanup.
 * Frame = GF(2)-subspace of F_2^h (h = 9), compared as spans.  Start: X_i = span(port_i), Y = 0, helper =
   start_extra[r] or 0.  End: X = FULL, Y_i = port_i^perp, helper = helper_final[r] or FULL.
 * Initial (anticipatory) corrections {target t, source s, operator_word [k], coefficient c} run FIRST, before
   the preconditioner (PR2226 PROOF section 3): t += c K_k s.  Structure: t is a Y register, s a live
   non-target register, c a non-zero dyadic rational, k an existing forward warp whose lender is s (each term is
   c K_G z for the pair lent by s), operator words have length one.  Frames: t and s must both be at frame 0
   when the term runs (s's entrance frame is 0); K_k fixes L_0 (checked for every warp), so applying K_k to s,
   reading it into t and inverting it is rank zero and pays nothing.
 * Every framed gate (add t s c F | scale t c F) climbs each incident register from its current frame S to F;
   legal only if S <= F; a strict climb pays one child of rank dim F - dim S.  precondition/compensation are at
   frame 0 and write targets only.
 * After A every target sits at its level and every centre at its centre frame; cut gates add c*centre into a
   target at its level; each centre pays one COPY child of rank dim(centre frame) - dim(level) per distinct
   served level (nested chain).
 * warp [pos, L, G, U, E] is inserted before B[pos] (list order inside a position): requires cur[L] == span U,
   sets cur[L] = span E, pays nothing (rank-zero reference change K_G); logically L <- K_G L.
 * After B and restore every live register climbs to its end frame (paid).  cleanup items must all be at FULL,
   may touch only live registers at FULL or buffers; they pay nothing.
 * Logic: exact replay over Q<F_80> (rationals x free group on K_1..K_80).  Every live register starts as an
   independent symbol (arbitrary dirty content); buffers start at 0.  add t += c s, scale t *= c, warp
   left-multiplies by K_k^{+-1} with free-group cancellation, a correction adds c K_k (row of s) to t.  LOW-lender
   exactness (PR2226 PROOF section 3): immediately before every warp whose operator occurs in a correction, the
   lender's row must be exactly its own input symbol.  Accept iff after cleanup Y_i = Y_i + X_i, every other
   live register is its own input and every buffer is 0.  The dual orientation replays g^{-T} for every item
   (add -> s -= c t, scale -> 1/c, K -> K^{-T} as new free letters, correction -> s -= c K_k^T t with
   K_k^T = (K_k^{-T})^{-1}) and expects X_i = X_i - Y_i.
 * Warp algebra over GF(2): G invertible, dim U = dim E, G span U = span E, M = [[G,0],[G+G^-T,G^-T]]
   symplectic, M L_0 = L_0, M L_FULL = L_FULL, M L_U = L_E (Fourier rank 0), G^-T U^perp = E^perp.  Exact
   Clifford phases / Gaussian lifts are NOT checked here.
 * Links (witness/canonical/block certificate): the B section is the canonical B plus the 48 moved tail gates,
   each removed helper renamed to its lender, minus the low helpers' pre-handoff echo/temporary gates, plus
   the direct-read rewrites that this checker DERIVES from those deleted gates (temporaries must be net zero;
   an echo t += c h reading a temporary part a*ext becomes t += c*a ext at the echo's frame).  Every other
   pre-handoff event of an aliased helper must be a helper-only correction inside its block.
"""

import sys

if sys.flags.optimize:
    sys.stdout.write('refusing to run under python -O\nFAIL_T74_LOW_ALIAS_WORDS_INDEPENDENT\n')
    sys.exit(2)

import argparse
import copy
import gzip
import hashlib
import json
import os
import subprocess
import time
from collections import Counter
from fractions import Fraction

PASS_LINE = 'PASS_T74_LOW_ALIAS_WORDS_INDEPENDENT'
FAIL_LINE = 'FAIL_T74_LOW_ALIAS_WORDS_INDEPENDENT'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(os.path.dirname(HERE))
RECEIPT = 'check_ext.receipt.json'

PR2269 = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'
PR2269_PKG = 'research/gmx-t74-borrow43/'
PR2226 = 'dacaf3d81f1936bb55b8454b1244e5d014272754'
PR2226_PKG = 'research/anticipatory-dirty-borrowing/'

# key -> (commit, repo path, git blob id, sha256)
GIT_PINS = {
    'word43_base': (PR2269, PR2269_PKG + 'new/borrow/words/BORROW-WORD-43base.json.gz',
                    '448dd795adba29392a90b34aa3f1b1b796c7e0bd',
                    '9492a5537fb87d9ca98dffcd0230f7625b3789744fa94e2f18acf23d91d998b5'),
    'word43_extra': (PR2269, PR2269_PKG + 'new/borrow/words/BORROW-WORD-43extra.json.gz',
                     '2b51ba96256283bbc5578f99b694c50edd8a0e35',
                     '87d51f5298101d5947f45c43ee02f0ec45d6acbddabb808d0d02db1eaf063734'),
    'canon_base': (PR2269, PR2269_PKG + 'new/borrow/inputs/gauge44.canonical.json.gz',
                   '4abb6e28f02c95b41ed345d4e4401d16d58ae791',
                   '65c6d17ffee2eacf27bff438f37fc549c9ed0c909cbc7a52976cc75cf2d15b91'),
    'canon_extra': (PR2269, PR2269_PKG + 'new/borrow/inputs/extra.canonical.json.gz',
                    'e0d670d4351229ce6921ecfbecf180070b17616b',
                    'd7e48dcbafa236a2e1e41f7958244211506f7c7630fe6a2d43d2bdf17b7ae015'),
    'blocks': (PR2269, PR2269_PKG + 'new/borrow/inputs/blocks.json',
               'c683574b3861678081fd5c5944dbd7a47309f6fd',
               'ddfac1dae1fe7cc0a91e7c7205c6d9d0c07c682880aa34eed83bf4ad7384da9f'),
    'witness43_base': (PR2269, PR2269_PKG + 'new/borrow/inputs/witness_43_base.json',
                       '9f4b93f3bc52d4f4ffaa128cfd7ae574fd36c462',
                       '67ffb66d94067f6e53aee9118fe90e14a57f497fc8b3f708b6dac3de2e58ff28'),
    'witness43_extra': (PR2269, PR2269_PKG + 'new/borrow/inputs/witness_43_extra.json',
                        '864ba533f50c2f1f639a6a3559b185bd321b923a',
                        'd46449c6dbf4477f260cf5baea9bbb570a66ee0b6db81f4a220b9e3086ae9e46'),
    'word566_base': (PR2269, PR2269_PKG + 'new/gauge44-word-566.json.gz',
                     '76c01583a0286cddb0f71e0cb13077e4317104f6',
                     'eeb6a236ed0ea8873b8800947d0cd19c36a6fcfdf857fc42913cb45cd984f219'),
    'word566_extra': (PR2269, PR2269_PKG + 'new/extra-word-566.json.gz',
                      'e86142b352466f54a3da38c96a6e1484145c3b5c',
                      'cd417b904408c221d9840d08faff8af040cc4207f9804284f2f5375d21298a62'),
    'pr2226_witness': (PR2226, PR2226_PKG + 'WITNESS.json',
                       '62edbcce166f7cf388231078c2cd7f75939b97e2',
                       '86392adde6992a08ae90f7a69c58cace1b52d942f4d2c96e82ca79e5d1e15235'),
}

# key -> (path relative to this package, git blob id, sha256): the constructed objects under test
LOCAL_PINS = {
    'word80_base': ('words/BORROW-WORD-80base.json.gz', 'c5953dfdb0ee9ac0c2c73eb29e320582b4569d2b',
                    '61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493'),
    'word80_extra': ('words/BORROW-WORD-80extra.json.gz', '852868543ed36efa799b3ed6dd76a0442b0d6ff1',
                     '1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5'),
    'witness80_base': ('witness/witness_80_base.json', 'cdcd39ff1beb577b975e48633d05ee629caa1362',
                       '9380f74c032b0616d5b13e8ef94b6d9f80cac36239e329357e7d5fcab5283ad0'),
    'witness80_extra': ('witness/witness_80_extra.json', '6b87d35600c44d053bf5ce03e34fc315d5a2af4a',
                        '6737072dcca47c6e6526bd62a41585dd09026549550c9e62eb53e64b265a6709'),
}

# Claims under test, written here from the construction report (not read from the files).
CLAIMS = {
    'ext80': {
        'base': dict(profile={1: 2303, 2: 527, 3: 386, 4: 125, 5: 37, 8: 8}, base_tag='eeb6a236'),
        'extra': dict(profile={1: 2287, 2: 535, 3: 386, 4: 125, 5: 37, 8: 8}, base_tag='cd417b90'),
        'width_inventory': {4: 4, 5: 4, 7: 36, 8: 84, 9: 272}, 'helpers': 400, 'warps': 80, 'low': 32,
        'high': 48, 'corrections': 64, 'mass': 5264, 'buffers': 44, 'inputs': 624, 'rewrites': 5,
        'new_high_X_lenders': [1, 4, 6, 12, 31]},
    'b43': {   # PR2269 predecessor (positive control of this checker on zero-correction words)
        'base': dict(profile={1: 2351, 2: 501, 3: 414, 4: 129, 5: 42, 8: 8}, base_tag='eeb6a236'),
        'extra': dict(profile={1: 2339, 2: 509, 3: 418, 4: 125, 5: 42, 8: 8}, base_tag='cd417b90'),
        'width_inventory': {4: 36, 5: 9, 7: 36, 8: 116, 9: 240}, 'helpers': 437, 'warps': 43, 'low': 0,
        'high': 43, 'corrections': 0, 'mass': 5385, 'buffers': 76, 'inputs': 661, 'rewrites': 0},
    'canonical': {'base': {1: 2348, 2: 500, 3: 416, 4: 130, 5: 82, 8: 8},
                  'extra': {1: 2340, 2: 508, 3: 420, 4: 126, 5: 82, 8: 8}},
    'helpers_before': 480,
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


def verify_bytes(what, data, blob, sha):
    need(git_blob_id(data) == blob, 'pin', 'git blob id mismatch for %s' % what)
    need(hashlib.sha256(data).hexdigest() == sha, 'pin', 'sha256 mismatch for %s' % what)


def load_inputs(repo):
    raw, pins = {}, {}
    for key in sorted(GIT_PINS):
        commit, path, blob, sha = GIT_PINS[key]
        got = subprocess.run(['git', '-C', repo, 'rev-parse', commit + ':' + path], capture_output=True, text=True)
        need(got.returncode == 0, 'pin', 'cannot resolve %s at %s (fetch the PR head first: git fetch '
             'https://github.com/CrocSwap/integer-mult-bounds pull/<N>/head)' % (path, commit[:8]))
        need(got.stdout.strip() == blob, 'pin', 'path %s does not resolve to the pinned blob' % path)
        got = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', blob], capture_output=True)
        need(got.returncode == 0, 'pin', 'cannot read blob %s' % blob)
        verify_bytes(path, got.stdout, blob, sha)
        raw[key] = got.stdout
        pins[key] = dict(commit=commit, path=path, git_blob=blob, sha256=sha, bytes=len(got.stdout))
    for key in sorted(LOCAL_PINS):
        rel, blob, sha = LOCAL_PINS[key]
        with open(os.path.join(HERE, rel), 'rb') as fh:
            data = fh.read()
        verify_bytes(rel, data, blob, sha)
        raw[key] = data
        pins[key] = dict(local=rel, git_blob=blob, sha256=sha, bytes=len(data))
    js = {}
    for key, data in raw.items():
        path = GIT_PINS[key][1] if key in GIT_PINS else LOCAL_PINS[key][0]
        if path.endswith('.gz'):
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


def parse_correction(t, j):
    need(isinstance(t, dict) and set(t) == {'target', 'source', 'operator_word', 'coefficient'}, 'format',
         'initial correction %d: fields' % j)
    need(is_int(t['target']) and is_int(t['source']), 'format', 'initial correction %d: registers' % j)
    ow = t['operator_word']
    need(isinstance(ow, list) and len(ow) == 1 and is_int(ow[0]) and ow[0] > 0, 'anticipatory',
         'initial correction %d: operator word must be a single forward warp id (scope of this checker)' % j)
    need(isinstance(t['coefficient'], str), 'format', 'initial correction %d: coefficient must be a string' % j)
    try:
        q = Fraction(t['coefficient'])
    except (ValueError, ZeroDivisionError):
        raise Reject('format', 'initial correction %d: coefficient %r' % (j, t['coefficient']))
    need(q != 0 and dyadic(q), 'anticipatory', 'initial correction %d: coefficient is not a non-zero dyadic' % j)
    return dict(target=t['target'], source=t['source'], op=ow[0], coef=q)


def check_corrections(P):
    """Structure of the anticipatory terms (PR2226 PROOF section 3): t += c K_G z for the pair lent by z."""
    v = P['v']
    by_op = dict((wr['op'], wr) for wr in P['warps'])
    live = set(P['live'])
    for j, t in enumerate(P['corr']):
        need(v <= t['target'] < 2 * v, 'anticipatory', 'correction %d writes a non-target %d' % (j, t['target']))
        need(t['source'] in live and not (v <= t['source'] < 2 * v), 'anticipatory',
             'correction %d source %d is not a live non-target register' % (j, t['source']))
        need(t['op'] in by_op, 'anticipatory', 'correction %d names a missing warp %d' % (j, t['op']))
        need(by_op[t['op']]['lender'] == t['source'], 'anticipatory',
             'correction %d: operator %d is not the reference change of the pair lent by source %d' % (
                 j, t['op'], t['source']))
    return dict(terms=len(P['corr']), operators=len(set(t['op'] for t in P['corr'])),
                sources=len(set(t['source'] for t in P['corr'])))


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
    need(isinstance(w.get('initial_corrections'), list), 'format', 'initial_corrections missing')
    corr = [parse_correction(t, j) for j, t in enumerate(w['initial_corrections'])]
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
    P = dict(kind='borrow', v=v, h=h, R=R, n=n, full=full, ports=ports, live=live, removed=removed,
             start=start, end=end, restored=restored, buffers=set(r + n for r in restored),
             centers=list(w['centers']), center_frames=[frame_lit(F) for F in w['center_frames']],
             target_levels={int(k): frame_lit(F) for k, F in w['target_levels'].items()},
             corr=corr, pre=sec['precondition'] + sec['compensation'], n_pre=len(sec['precondition']),
             A=sec['A'], cut=sec['cut'], B_items=items, post=sec['restore'], cleanup=cleanup,
             warps=warps, sections=sec,
             claimed_profile={int(k): c for k, c in rep['local_profile'].items()},
             claimed_inventory={int(k): c for k, c in rep['width_inventory'].items()})
    check_corrections(P)
    return P


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
                corr=[], pre=sec['precondition'] + sec['compensation'], n_pre=len(sec['precondition']),
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

    # anticipatory initial corrections: before the preconditioner, both ends at frame 0, K_k rank zero there
    for j, t in enumerate(P['corr']):
        for role in ('target', 'source'):
            r = t[role]
            need(r in cur, 'frame', 'initial correction %d: %s %d is not live' % (j, role, r))
            need(cur[r] == (), 'frame', 'initial correction %d: %s %d is not at frame 0 (frame %r)' % (
                j, role, r, cur[r]))
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
                helper_width_sum=sum(inventory[k] * k for k in inventory),
                mass=sum(k * c for k, c in paid.items()))


# ----------------------------------------------------------------------------
# Check 3: exact replay over the free-group algebra Q<F_k>
# ----------------------------------------------------------------------------

ONE = Fraction(1)


def left_mult(letter, word):
    inverse = (letter[0], letter[1], -letter[2])
    return word[1:] if (word and word[0] == inverse) else (letter,) + word


def replay(P, dual=False):
    v = P['v']
    rows = {}
    for r in P['live']:
        rows[r] = {(r, ()): ONE}
    for b in P['buffers']:
        rows[b] = {}
    istarget = lambda r: v <= r < 2 * v
    low_ops = set(t['op'] for t in P['corr'])

    def row(r):
        need(r in rows, 'replay', 'unknown register %d' % r)
        return rows[r]

    def axpy(dst, src, c, letter=None):
        for (var, word), val in list(src.items()):
            key = (var, word if letter is None else left_mult(letter, word))
            nv = dst.get(key, 0) + c * val
            if nv:
                dst[key] = nv
            else:
                del dst[key]

    def do(it):
        kind = it[0]
        if kind == 'add':
            t, s, c = it[1], it[2], it[3]
            if dual:
                t, s, c = s, t, -c
            need(t != s, 'replay', 'self add')
            axpy(row(t), row(s), c)
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
            rows[reg] = dict(((var, left_mult(letter, word)), val) for (var, word), val in row(reg).items())
        else:
            raise Reject('replay', 'unknown item')

    # 0. anticipatory initial corrections: t += c K_k s   (dual: s -= c K_k^T t, K_k^T = (K_k^{-T})^{-1})
    for t in P['corr']:
        if not dual:
            axpy(row(t['target']), row(t['source']), t['coef'], (t['op'], 0, 1))
        else:
            axpy(row(t['source']), row(t['target']), -t['coef'], (t['op'], 1, -1))
    for it in list(P['pre']) + list(P['A']) + list(P['cut']):
        do(it)
    exact_lenders = 0
    for it in P['B_items']:
        if it[0] == 'warp':
            if not dual and it[2] in low_ops:
                need(row(it[1]) == {(it[1], ()): ONE}, 'lender',
                     'low lender %d is not exactly its own input at the handoff of warp %d' % (it[1], it[2]))
                exact_lenders += 1
            do(('warp', it[1], it[2]))
        else:
            do(it)
    for it in P['post']:
        do(it)
    diag = {}
    need(all(not rows[b] for b in P['buffers']), 'replay', 'a buffer is non-zero before cleanup')
    if not dual:
        diag['low_lenders_exact_at_handoff'] = exact_lenders
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
    # backstop after the algebraic checks: every low operator must have had its forward warp (and exactness test)
    need(dual or exact_lenders == len(low_ops), 'lender', 'a low operator has no forward warp in B')
    diag.update(peak_nonzero_buffers=peak, buffer_nonzero_window=[first_live, last_live],
                buffers=len(P['buffers']), independent_inputs=len(P['live']), corrections=len(P['corr']))
    return diag


# ----------------------------------------------------------------------------
# Links: canonical base, block certificate, witness, PR2226 terms, PR2269 43-word, 566 predecessor
# ----------------------------------------------------------------------------

def coef(g):
    return g[3] if g[0] == 'add' else g[2]


def norm(g):
    return (g[0],) + tuple(regs_of(g)) + (coef(g), g[-1])


def block_maps(blocks):
    high, low, block_of = set(), set(), {}
    for bl in blocks['sources'][0]['blocks']:
        high |= set(bl['high'])
        low |= set(bl['low'])
        for r in bl['helpers']:
            need(r not in block_of, 'link', 'helper %d in two blocks' % r)
            block_of[r] = bl
    need(not (high & low), 'link', 'a helper is both high and low')
    return high, low, block_of


def prefix_analysis(C, pairs, block_of, low, v):
    """Derive, from the canonical B alone, what aliasing each helper requires before its handoff.

    For each aliased helper h with handoff index H (= its block's first input): every canonical B event on h
    before H is either a helper-only correction inside h's block (deferred; kept) or, for a LOW helper only,
    an echo  t += c h  (t a target; deleted) or a temporary  h += a ext  (ext outside the block, not a target;
    deleted).  Temporaries must have zero net change per source; an echo reading the current temporary part
    sum a*ext becomes direct reads  t += c*a ext  at the echo's frame (the derived rewrites)."""
    CB = C['sections']['B']
    istarget = lambda r: v <= r < 2 * v
    events = {}
    for i, g in enumerate(CB):
        for r in set(regs_of(g)):
            events.setdefault(r, []).append(i)
    deleted, rewrites, info = set(), [], {}
    for pr in pairs:
        h = pr['register']
        bl = block_of[h]
        H = pr['handoff_B']
        need(H == bl['first_input'], 'prefix', 'helper %d: handoff %r != block first input %r' % (h, H, bl['first_input']))
        helpers = set(bl['helpers'])
        pre = [i for i in events.get(h, []) if i < H]
        kept = [i for i in pre if all(r in helpers for r in regs_of(CB[i]))]
        others = [i for i in pre if i not in kept]
        if h not in low:
            need(not others, 'prefix', 'high helper %d has a pre-handoff event outside helper-only corrections' % h)
            need(not pr.get('deleted_prefix_indices') and not pr.get('deleted_echo_indices'), 'prefix',
                 'high helper %d witness deletes gates' % h)
            info[h] = dict(kind='high', deferred_helper_only=len(kept))
            continue
        need(sorted(others) == sorted(pr.get('deleted_prefix_indices', [])), 'prefix',
             'low helper %d: witness deleted prefix %r != derived %r' % (h, pr.get('deleted_prefix_indices'), others))
        temp = {}
        mine, echoes, temps = [], 0, 0
        for i in sorted(others):
            g = CB[i]
            need(g[0] == 'add', 'prefix', 'low helper %d: pre-handoff scale at B[%d]' % (h, i))
            if g[1] == h and g[2] not in helpers and not istarget(g[2]):
                temp[g[2]] = temp.get(g[2], 0) + g[3]
                temps += 1
            elif g[2] == h and istarget(g[1]):
                echoes += 1
                for ext in sorted(temp):
                    if temp[ext]:
                        mine.append(('add', g[1], ext, g[3] * temp[ext], g[-1]))
            else:
                raise Reject('prefix', 'low helper %d: B[%d] %r is neither an echo nor a temporary' % (h, i, g))
        need(all(a == 0 for a in temp.values()), 'prefix', 'low helper %d: temporaries are not net zero' % h)
        echo_idx = sorted(i for i in others if CB[i][2] == h)
        need(echo_idx == sorted(pr.get('deleted_echo_indices', [])), 'prefix', 'low helper %d: echo indices' % h)
        wit_rw = Counter()
        for idx, lst in pr.get('early_prefix_rewrites', {}).items():
            need(int(idx) in others, 'prefix', 'low helper %d: rewrite keyed by a non-deleted index' % h)
            for g in lst:
                wit_rw[(g[1], g[2], Fraction(g[3], g[4]), C['frames'][g[5]])] += 1
        need(wit_rw == Counter((g[1], g[2], g[3], g[4]) for g in mine), 'prefix',
             'low helper %d: witness rewrites != derived rewrites' % h)
        deleted |= set(others)
        rewrites += mine
        info[h] = dict(kind='low', deferred_helper_only=len(kept), echoes=echoes, temporaries=temps, rewrites=len(mine))
    return deleted, rewrites, info


def link_checks(tag, P, C, wit, blocks, w_raw):
    out = {}
    v, n, h = P['v'], P['n'], P['h']
    need(P['ports'] == C['ports'] and P['centers'] == C['centers'], 'link', 'ports/centres differ from canonical')
    need(P['center_frames'] == C['center_frames'], 'link', 'centre frames differ from canonical')
    removed = P['removed']
    high, low, block_of = block_maps(blocks)
    need(removed <= (high | low), 'link', 'a removed helper is neither high nor low')
    rh, rl = removed & high, removed & low
    out['removed_high'], out['removed_low'] = len(rh), len(rl)
    touches = lambda g: any(r in removed for r in regs_of(g))
    need(not any(touches(g) for g in C['sections']['compensation'] if any(r in rh for r in regs_of(g))), 'link',
         'canonical compensation reads a removed HIGH helper (a high helper must have zero response)')
    for name in ('precondition', 'compensation', 'A', 'cut'):
        kept = [norm(g) for g in C['sections'][name] if not touches(g)]
        need([norm(g) for g in P['sections'][name]] == kept, 'link', 'section %s != canonical minus removed' % name)
        out['canonical_%s_gates_dropped' % name] = len(C['sections'][name]) - len(kept)
    for r in P['live']:
        if r >= 2 * v:
            need(P['start'][r] == C['start'][r], 'link', 'start frame of %d differs from canonical' % r)
    for r in P['restored']:
        need(P['end'][r] == C['end'][r], 'link', 'cold end frame of %d differs from canonical' % r)
    canon_cold = [r for r in range(2 * v, n) if len(C['end'][r]) < h]
    out['canonical_cold_helpers'] = len(canon_cold)
    cold_full = sorted(r for r in canon_cold if r not in removed and r not in P['restored'])
    out['canonical_cold_helpers_ending_FULL_after_borrowing'] = cold_full
    grown = sum(len(P['end'][r]) - len(C['end'][r]) for r in cold_full)
    removed_widths = sum(len(C['end'][r]) - len(C['start'][r]) for r in removed)
    need(all(P['start'][r] == C['start'][r] and P['end'][r] == C['end'][r] for r in P['live'] if r not in cold_full),
         'link', 'some other register changed its start/end frame')
    out['mass_identity'] = dict(removed_widths=removed_widths, width_added_to_cold_now_FULL=grown,
                                predicted_saving=removed_widths - grown)
    out['removed_old_widths'] = dict(sorted(Counter(len(C['end'][r]) - len(C['start'][r]) for r in removed).items()))
    # witness <-> word
    pairs = wit['pairs']
    need(len(pairs) == len(P['warps']), 'link', 'witness pair count')
    need(wit['initial_corrections'] == w_raw['initial_corrections'], 'link', 'witness corrections != word corrections')
    gauss = dict((g['operator'], g['G_columns']) for g in wit['gaussian']['records'])
    low_ops, low_lenders = set(), set()
    for wr, pr in zip(P['warps'], pairs):
        k = wr['op']
        need(pr['borrow_from'] == wr['lender'], 'link', 'warp %d lender != witness borrow_from' % k)
        need(gauss.get(k) == wr['G'], 'link', 'warp %d G != witness Gaussian record' % k)
        need(span(pr['retirement_basis']) == wr['U'], 'link', 'warp %d U != witness retirement basis' % k)
        need(span(pr['handoff_basis']) == wr['E'], 'link', 'warp %d E != witness handoff basis' % k)
        is_low = pr['register'] in low
        need(pr['low'] is is_low and pr['anticipate'] is is_low and pr['handoff_paid_rank'] == 0, 'link',
             'warp %d witness flags (low/anticipate/handoff_paid_rank)' % k)
        if is_low:
            low_ops.add(k)
            low_lenders.add(wr['lender'])
    need(set(p['register'] for p in pairs) == removed, 'link', 'witness registers != removed set')
    need(set(t['op'] for t in P['corr']) == low_ops, 'link', 'correction operators != the low pairs\' warps')
    need(set(t['source'] for t in P['corr']) == low_lenders, 'link', 'correction sources != low lenders')
    out['low_ops'] = sorted(low_ops)
    out['low_lenders'] = sorted(low_lenders)
    out['low_lenders_entrance_frame_dims'] = sorted(set(len(P['start'][L]) for L in low_lenders))
    out['low_lenders_canonical_final_dims'] = dict(sorted(Counter(len(C['end'][L]) for L in low_lenders).items()))
    # B: canonical B + moved tail, renamed, minus derived deleted prefix, plus derived rewrites
    deleted, rewrites, pinfo = prefix_analysis(C, pairs, block_of, low, v)
    rename = dict((p['register'], p['borrow_from']) for p in pairs)

    def ren(g):
        if g[0] == 'add':
            return ('add', rename.get(g[1], g[1]), rename.get(g[2], g[2]), g[3], g[4])
        return ('scale', rename.get(g[1], g[1]), g[2], g[3])
    CB = C['sections']['B']
    moved = [C['sections']['tail'][e['old_tail_index']] for e in wit['early_tail_events']]
    lhs = Counter(norm(ren(g)) for i, g in enumerate(CB) if i not in deleted)
    lhs.update(norm(ren(g)) for g in moved)
    lhs.update(norm(ren(g)) for g in rewrites)
    rhs = Counter(norm(it) for it in P['B_items'] if it[0] != 'warp')
    need(lhs == rhs, 'link', 'B multiset != canonical B - deleted prefix + moved tail + derived rewrites (renamed)')
    out['B_multiset_ok'] = True
    out['moved_tail_gates'] = len(moved)
    out['deleted_prefix_gates'] = len(deleted)
    out['derived_rewrites'] = sorted([[g[1], g[2], str(g[3]), list(g[4])] for g in rewrites])
    out['low_prefix'] = dict(
        echoes=sum(x.get('echoes', 0) for x in pinfo.values()),
        temporaries=sum(x.get('temporaries', 0) for x in pinfo.values()),
        deferred_helper_only_low=sum(x['deferred_helper_only'] for x in pinfo.values() if x['kind'] == 'low'),
        deferred_helper_only_high=sum(x['deferred_helper_only'] for x in pinfo.values() if x['kind'] == 'high'))
    return out


def link_pr2226(P, wit, w2226, wit43):
    """The 64 terms are PR2226's 64 T8 terms up to operator ids; low pairs are PR2226's; 43 highs are PR2269's."""
    out = {}
    reg_of_op = dict((k, p['register']) for k, p in enumerate(wit['pairs'], 1))
    reg_of_op_2226 = dict((k, p['register']) for k, p in enumerate(w2226['pairs'], 1))
    ours = Counter((t['target'], t['source'], t['coef'], reg_of_op[t['op']]) for t in P['corr'])
    theirs = Counter()
    for j, t in enumerate(w2226['initial_corrections']):
        q = parse_correction(t, j)
        theirs[(q['target'], q['source'], q['coef'], reg_of_op_2226[q['op']])] += 1
    need(ours == theirs, 'link2226', '(target, source, coefficient, aliased register) multiset != PR2226 T8 terms')
    out['terms_equal_pr2226'] = sum(ours.values())
    lp = lambda pp: set((p['register'], p['borrow_from']) for p in pp if p.get('low'))
    need(lp(wit['pairs']) == lp(w2226['pairs']), 'link2226', 'low (register, lender) pairs != PR2226 low pairs')
    out['low_pairs_equal_pr2226'] = len(lp(w2226['pairs']))
    hp = lambda pp: set((p['register'], p['borrow_from']) for p in pp if not p.get('low'))
    ours_h, w43_h, t_h = hp(wit['pairs']), hp(wit43['pairs']), hp(w2226['pairs'])
    need(w43_h <= ours_h, 'link2226', 'a PR2269 high pair is missing or changed')
    new = sorted(ours_h - w43_h)
    out['high_pairs_from_pr2269'] = len(w43_h)
    out['new_high_pairs'] = [list(x) for x in new]
    out['new_high_pr2226_lenders'] = sorted([list(x) for x in t_h if x[0] in set(r for r, _ in new)])
    out['high_pairs_equal_pr2226'] = len(ours_h & t_h)
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
                aligned_frame_pairs=len(pairs))


# ----------------------------------------------------------------------------
# Controls
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
    print('  control %-66s target=%-12s %s' % (name, target, 'REJECTED-OK' if entry['ok'] else 'NOT-OK ' + str(entry)),
          flush=True)
    return entry['ok']


def mutate_P(P):
    Q = dict(P)
    for key in ('pre', 'A', 'cut', 'B_items', 'post', 'cleanup'):
        Q[key] = list(P[key])
    Q['warps'] = [dict(w) for w in P['warps']]
    Q['corr'] = [dict(t) for t in P['corr']]
    return Q


def profile_check(P, fr, claim):
    need(dict(fr['paid']) == P['claimed_profile'], 'profile',
         'recount %r != word report %r' % (dsort(fr['paid']), P['claimed_profile']))
    need(dict(fr['paid']) == claim, 'profile', 'recount != claimed profile')


def controls_low(P, results):
    """Controls specific to LOW pairs and anticipatory initial corrections."""
    ok = True
    corr = P['corr']
    low_ops = sorted(set(t['op'] for t in corr))
    by_op = dict((w['op'], w) for w in P['warps'])
    t0 = corr[0]
    # 1. drop one anticipatory term
    Q = mutate_P(P)
    del Q['corr'][0]
    ok &= expect_reject('anticipatory: drop term 0 (%d += %s K_%d %d)' % (t0['target'], t0['coef'], t0['op'],
                                                                          t0['source']), 'replay',
                        lambda: replay(Q), results, also=[('frame', lambda: frame_check(Q))])
    # 2. perturb one term (x2), 3. flip its sign
    for label, f in (('x2', lambda c: 2 * c), ('sign flip', lambda c: -c)):
        Q = mutate_P(P)
        Q['corr'][0]['coef'] = f(t0['coef'])
        ok &= expect_reject('anticipatory: term 0 coefficient %s' % label, 'replay', lambda: replay(Q), results,
                            also=[('dual replay', lambda: replay(Q, dual=True))])
    # 4. drop all terms
    Q = mutate_P(P)
    Q['corr'] = []
    ok &= expect_reject('anticipatory: drop all %d terms' % len(corr), 'replay', lambda: replay(Q), results)
    # 5. retarget one term to another target
    Q = mutate_P(P)
    Q['corr'][0]['target'] = P['v'] + ((t0['target'] - P['v'] + 1) % P['v'])
    ok &= expect_reject('anticipatory: term 0 written into target %d' % Q['corr'][0]['target'], 'replay',
                        lambda: replay(Q), results)
    # 6. structurally valid redirection to another low pair (source and operator consistent)
    other = next(k for k in low_ops if by_op[k]['lender'] != t0['source'])
    Q = mutate_P(P)
    Q['corr'][0]['op'], Q['corr'][0]['source'] = other, by_op[other]['lender']
    ok &= expect_reject('anticipatory: term 0 redirected to pair K_%d / lender %d' % (other, by_op[other]['lender']),
                        'replay', lambda: replay(Q), results, also=[('structure', lambda: check_corrections(Q))])
    # 7. operator not owned by the source
    Q = mutate_P(P)
    Q['corr'][0]['op'] = other
    ok &= expect_reject('anticipatory: term 0 uses K_%d of another lender' % other, 'anticipatory',
                        lambda: check_corrections(Q), results)
    # 8. a term reading an X register (structurally consistent: X lender with its own warp)
    xw = next(w for w in P['warps'] if w['lender'] < P['v'])
    Q = mutate_P(P)
    Q['corr'][0]['op'], Q['corr'][0]['source'] = xw['op'], xw['lender']
    ok &= expect_reject('anticipatory: term 0 reads X register %d through K_%d' % (xw['lender'], xw['op']), 'frame',
                        lambda: frame_check(Q), results, also=[('structure', lambda: check_corrections(Q))])
    # 9. drop one low warp entirely (forward in B and inverse in cleanup), corrections kept
    k = low_ops[0]
    Q = mutate_P(P)
    Q['B_items'] = [it for it in P['B_items'] if not (it[0] == 'warp' and it[2] == k)]
    Q['cleanup'] = [it for it in P['cleanup'] if not (it[0] == 'warp' and it[2] == -k)]
    ok &= expect_reject('low warp %d (lender %d) dropped from B and cleanup' % (k, by_op[k]['lender']), 'replay',
                        lambda: replay(Q), results, also=[('frame', lambda: frame_check(Q))])
    # 10. drop only the forward low warp
    Q = mutate_P(P)
    Q['B_items'] = [it for it in P['B_items'] if not (it[0] == 'warp' and it[2] == k)]
    ok &= expect_reject('low warp %d dropped from B only' % k, 'replay', lambda: replay(Q), results)
    # 11. low lender disturbed before its handoff (lender += X_0 just before the warp): exactness check
    L = by_op[k]['lender']
    j = next(i for i, it in enumerate(P['B_items']) if it[0] == 'warp' and it[2] == k)
    Q = mutate_P(P)
    Q['B_items'].insert(j, ('add', L, 0, ONE, P['full']))
    ok &= expect_reject('low lender %d += X_0 just before its handoff' % L, 'lender', lambda: replay(Q), results)
    # 12. low warp treated as an ordinary climb
    kc = next(kk for kk in low_ops if by_op[kk]['U'] != by_op[kk]['E'])
    ok &= expect_reject('low warp %d as an ordinary climb U->E' % kc, 'frame',
                        lambda: frame_check(P, warp_as_climb=(kc,)), results)
    return ok


def controls_generic(P, claim, results):
    """Iteration-3 controls, applied to a low warp where a warp is chosen."""
    ok = True
    v = P['v']
    warps = P['warps']
    low_ops = set(t['op'] for t in P['corr'])
    k0 = next((w['op'] for w in warps if w['U'] != w['E'] and w['op'] in low_ops),
              next(w['op'] for w in warps if w['U'] != w['E']))
    Q2 = mutate_P(P)
    j = next(i for i, it in enumerate(P['cleanup']) if it[0] == 'warp' and it[2] == -k0)
    del Q2['cleanup'][j]
    ok &= expect_reject('drop inverse warp %d in cleanup' % k0, 'replay', lambda: replay(Q2), results,
                        also=[('frame', lambda: frame_check(Q2))])
    lender = next(w['lender'] for w in warps if w['op'] == k0)
    wi = next(i for i, it in enumerate(P['B_items']) if it[0] == 'warp' and it[2] == k0)
    bi = next(i for i in range(wi + 1, len(P['B_items']))
              if P['B_items'][i][0] == 'add' and lender in regs_of(P['B_items'][i]))
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

    def charged():
        fr = frame_check(P, charge_warps=True)
        profile_check(P, fr, claim)
    ok &= expect_reject('charge every warp as a climb of rank d(L_U,L_E)', 'profile', charged, results)
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
        for jj in range(h):
            for i in range(h):
                if i == jj:
                    continue
                G = list(wr['G'])
                G[jj] ^= G[i]
                if mat_inverse(G, h) is not None and span([mat_apply(G, u) for u in wr['U']]) != wr['E']:
                    wr['G'] = G
                    return
        raise Reject('control', 'no wrong-image G found')
    ok &= expect_reject('warp 1: invertible G with G span U != span E', 'warp', warp_mut(wrong_image), results)

    def dim_drop(wr):
        wr['E_list'] = wr['E_list'][:-1]
        wr['E'] = span(wr['E_list'])
    ok &= expect_reject('warp 1: dim E != dim U', 'warp', warp_mut(dim_drop), results)
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
    Q8 = mutate_P(P)
    del Q8['post'][0]
    ok &= expect_reject('delete restore gate 0', 'replay', lambda: replay(Q8), results)
    Q9 = mutate_P(P)
    del Q9['pre'][P['n_pre']]
    ok &= expect_reject('delete compensation gate 0', 'replay', lambda: replay(Q9), results)
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
    ok &= results[-1]['other_checks']['forward replay'] == 'accepted'
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
        profile_check(Qp, frame_check(Qp), claim)
        entry.update(accepted=True, ok=True)
    except Reject as e:
        entry.update(accepted=False, ok=False, reason=str(e))
    print('  control %-66s %s' % (entry['control'], 'ACCEPTED-OK' if entry['ok'] else 'NOT-OK'), flush=True)
    results.append(entry)
    ok &= entry['ok']
    return ok


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------

def check_word(label, w, claim, common, results_controls=None):
    """Warps, structure, frames/profile recount and both replays of one BORROW-WORD."""
    P = parse_borrow(w)
    res = dict(base_tag=w.get('base'))
    need(w.get('base') == claim['base_tag'], 'link', 'base tag')
    wres = check_all_warps(P)
    need(len(wres) == common['warps'], 'warp', 'warp count %d' % len(wres))
    need(len(P['corr']) == common['corrections'], 'anticipatory', 'correction count %d' % len(P['corr']))
    low_ops = set(t['op'] for t in P['corr'])
    need(len(low_ops) == common['low'], 'anticipatory', 'low operator count %d' % len(low_ops))
    res['warps'] = dict(count=len(wres), dims=dsort(Counter(x['dim'] for x in wres)),
                        low_ops=sorted(low_ops), lenders=[x['lender'] for x in wres],
                        lenders_that_are_X=[x['lender'] for x in wres if x['lender'] < P['v']],
                        U_equal_E=sum(1 for x in wres if x['U_eq_E']),
                        plain_fourier_distance=dsort(Counter(x['plain_fourier_distance'] for x in wres)),
                        anticipatory_terms=len(P['corr']), anticipatory_structure=check_corrections(P))
    fr = frame_check(P)
    profile_check(P, fr, claim['profile'])
    need(dict(fr['inventory']) == common['width_inventory'] == P['claimed_inventory'], 'profile', 'width inventory')
    need(fr['helpers'] == common['helpers'] == P['R'] - len(P['removed']), 'profile', 'helper count')
    need(fr['mass'] == common['mass'], 'profile', 'local mass %d' % fr['mass'])
    need(fr['mass'] == 1856 + fr['helper_width_sum'], 'profile', 'mass != 1856 + helper widths')
    frc = frame_check(P, charge_warps=True)
    res['frames'] = dict(paid_profile=dsort(fr['paid']), climbs=dsort(fr['climbs']), copy_charges=dsort(fr['copies']),
                         local_mass=fr['mass'], width_inventory=dsort(fr['inventory']), helpers=fr['helpers'],
                         helper_width_sum=fr['helper_width_sum'],
                         if_warps_charged_profile=dsort(frc['paid']), if_warps_charged_mass=frc['mass'])
    print('  [%s] warps %d PASS (dims %s, %d low, %d corrections); frames PASS: paid %s mass %d helpers %d '
          'inventory %s' % (label, len(wres), res['warps']['dims'], len(low_ops), len(P['corr']),
                            res['frames']['paid_profile'], fr['mass'], fr['helpers'], res['frames']['width_inventory']),
          flush=True)
    t0 = time.time()
    rf = replay(P)
    rd = replay(P, dual=True)
    need(rf['independent_inputs'] == common['inputs'] and rf['buffers'] == common['buffers'], 'replay',
         'input/buffer count %d/%d' % (rf['independent_inputs'], rf['buffers']))
    res['replay'] = dict(forward=rf, dual=rd)
    print('  [%s] replay forward+dual PASS over %d inputs, %d buffers, %d low lenders exact at handoff (%.1f s)' % (
        label, rf['independent_inputs'], rf['buffers'], rf.get('low_lenders_exact_at_handoff', 0), time.time() - t0),
        flush=True)
    return P, fr, res


def main():
    ap = argparse.ArgumentParser(description='Independent check of BORROW-WORD-80{base,extra} (low aliases)')
    ap.add_argument('--repo', default=DEFAULT_REPO, help='git checkout containing the PR2269 and PR2226 heads')
    ap.add_argument('--out', action='store_true', help='write %s next to this script' % RECEIPT)
    ap.add_argument('--skip-controls', action='store_true', help='skip negative controls (not a PASS run)')
    ap.add_argument('--skip-predecessor', action='store_true', help='skip the PR2269 43-word positive control')
    args = ap.parse_args()
    t0 = time.time()
    receipt = dict(checker='check_ext.py', python=sys.version.split()[0],
                   scope='BORROW-WORD-80{base,extra} + witness_80_*: warps, anticipatory structure, frames, '
                         'profiles, exact replay; links to PR2269 canonical/blocks/43-word and PR2226 terms',
                   adapted_from='fork commit 4a2f20ea339e30348448096ca789d0efe55df9bb '
                                'research/t74-borrow43-independent-check/words_check.py (own code)')
    ok = True
    try:
        js, pins, raw = load_inputs(args.repo)
        receipt['pins'] = pins
        print('pins: %d inputs verified (sha256 + git blob id)' % len(pins), flush=True)
        words = {}
        for tag in ('base', 'extra'):
            print('== word 80%s' % tag, flush=True)
            w = js['word80_' + tag]
            claim = CLAIMS['ext80'][tag]
            P, fr, res = check_word('80' + tag, w, claim, CLAIMS['ext80'])
            C = parse_canonical(js['canon_' + tag])
            res['links'] = link_checks(tag, P, C, js['witness80_' + tag], js['blocks'], w)
            L = res['links']
            need(L['removed_low'] == CLAIMS['ext80']['low'] and L['removed_high'] == CLAIMS['ext80']['high'], 'link',
                 'low/high split %d/%d' % (L['removed_low'], L['removed_high']))
            need(len(L['derived_rewrites']) == CLAIMS['ext80']['rewrites'], 'link', 'rewrite count')
            print('  links PASS: %d high + %d low removed; B = canonical B - %d deleted prefix + %d moved tail + %d '
                  'derived rewrites (renamed); low lenders entrance dims %s, canonical final dims %s' % (
                      L['removed_high'], L['removed_low'], L['deleted_prefix_gates'], L['moved_tail_gates'],
                      len(L['derived_rewrites']), L['low_lenders_entrance_frame_dims'],
                      L['low_lenders_canonical_final_dims']), flush=True)
            res['pr2226'] = link_pr2226(P, js['witness80_' + tag], js['pr2226_witness'], js['witness43_' + tag])
            need(sorted(l for _, l in res['pr2226']['new_high_pairs']) == CLAIMS['ext80']['new_high_X_lenders'],
                 'link2226', 'new high lenders')
            print('  PR2226 link PASS: 64 terms = PR2226 T8 terms (target, source, coefficient, aliased register); '
                  '%d low pairs = PR2226; %d PR2269 high pairs kept; new high pairs %s (PR2226 lenders %s)' % (
                      res['pr2226']['low_pairs_equal_pr2226'], res['pr2226']['high_pairs_from_pr2269'],
                      res['pr2226']['new_high_pairs'], res['pr2226']['new_high_pr2226_lenders']), flush=True)
            # canonical positive control + 566 link + mass bookkeeping
            frC = frame_check(C)
            need(dict(frC['paid']) == C['claimed_profile'] == CLAIMS['canonical'][tag], 'canonical',
                 'canonical profile not reproduced: %r' % dsort(frC['paid']))
            rC = replay(C)
            l566 = link_566(C, js['word566_' + tag])
            res['canonical'] = dict(paid_profile=dsort(frC['paid']), local_mass=frC['mass'], helpers=frC['helpers'],
                                    replay=rC, link_566=l566)
            need(frC['mass'] - fr['mass'] == L['mass_identity']['predicted_saving'] and frC['copies'] == fr['copies'],
                 'profile', 'saving does not match the width bookkeeping')
            res['saving_vs_canonical'] = frC['mass'] - fr['mass']
            print('  canonical positive control: profile %s mass %d, replay PASS, 566-link PASS; saving %d = removed '
                  'widths %d - widths added %d' % (res['canonical']['paid_profile'], frC['mass'],
                                                   res['saving_vs_canonical'], L['mass_identity']['removed_widths'],
                                                   L['mass_identity']['width_added_to_cold_now_FULL']), flush=True)
            if not args.skip_predecessor:
                print('  -- positive control: PR2269 BORROW-WORD-43%s through the same checker' % tag, flush=True)
                P43, fr43, r43 = check_word('43' + tag, js['word43_' + tag], CLAIMS['b43'][tag], CLAIMS['b43'])
                l43 = link_checks(tag, P43, C, js['witness43_' + tag], js['blocks'], js['word43_' + tag])
                need(l43['removed_low'] == 0 and l43['removed_high'] == 43, 'link', '43-word split')
                res['predecessor_43'] = dict(paid_profile=r43['frames']['paid_profile'],
                                             local_mass=r43['frames']['local_mass'], replay=r43['replay'],
                                             links=dict((k, l43[k]) for k in ('removed_high', 'removed_low',
                                                                              'deleted_prefix_gates', 'moved_tail_gates')))
                res['delta_vs_pr2269'] = dict((str(r), fr['paid'].get(r, 0) - fr43['paid'].get(r, 0))
                                              for r in sorted(set(fr['paid']) | set(fr43['paid'])))
                res['mass_delta_vs_pr2269'] = fr['mass'] - fr43['mass']
                print('  delta vs PR2269 43-word: %s, mass %+d' % (res['delta_vs_pr2269'], res['mass_delta_vs_pr2269']),
                      flush=True)
            if not args.skip_controls:
                results = []
                print('  -- negative controls (low pairs / anticipatory terms)', flush=True)
                cok = controls_low(P, results)
                print('  -- negative controls (iteration-3 set, on a low warp)', flush=True)
                cok &= controls_generic(P, claim['profile'], results)
                bad = bytearray(raw['word80_' + tag])
                bad[len(bad) // 2] ^= 1
                rel, blob, sha = LOCAL_PINS['word80_' + tag]
                cok &= expect_reject('pin: one flipped bit in the word file', 'pin',
                                     lambda: verify_bytes(rel, bytes(bad), blob, sha), results)
                wbad = copy.deepcopy(js['witness80_' + tag])
                pr0 = next(p for p in wbad['pairs'] if p['low'] and p['deleted_prefix_indices'])
                pr0['deleted_prefix_indices'] = pr0['deleted_prefix_indices'][:-1]
                cok &= expect_reject('witness: one deleted prefix gate of helper %d kept' % pr0['register'], 'prefix',
                                     lambda: link_checks(tag, P, C, wbad, js['blocks'], w), results)
                res['controls'] = results
                res['controls_ok'] = bool(cok)
                print('  controls: %d/%d as required' % (sum(1 for e in results if e['ok']), len(results)), flush=True)
                ok &= bool(cok)
            words[tag] = res
        receipt['words'] = words
        receipt['recounted'] = dict(
            (('gauge44' if tag == 'base' else 'extra'),
             dict(profile=words[tag]['frames']['paid_profile'], helpers=words[tag]['frames']['helpers'],
                  helper_width_sum=words[tag]['frames']['helper_width_sum'],
                  local_mass=words[tag]['frames']['local_mass'])) for tag in ('base', 'extra'))
        fb = words['base']
        receipt['findings'] = [
            'Both 80-alias words: 80 warps pass the GF(2) checks (rank-zero K_G handoffs); 64 anticipatory terms '
            'c K_k z_L read 32 frame-zero low lenders before the preconditioner, each with the warp of its own pair.',
            'Paid profiles recounted from the words alone: base %s, extra %s; mass %d each = 1856 + helper widths %d; '
            '%d helpers; inventory %s.' % (words['base']['frames']['paid_profile'],
                                           words['extra']['frames']['paid_profile'], fb['frames']['local_mass'],
                                           fb['frames']['helper_width_sum'], fb['frames']['helpers'],
                                           fb['frames']['width_inventory']),
            'Exact replay over Q<F_80> in both orientations on %d independent dirty inputs: Y += X, every other live '
            'register restored, %d buffers zero; each of the 32 low lenders is exactly its own input at its handoff.' % (
                fb['replay']['forward']['independent_inputs'], fb['replay']['forward']['buffers']),
            'B equals canonical B minus %d pre-handoff low-helper gates (echoes/net-zero temporaries), plus 48 moved '
            'tail gates and %d direct-read rewrites derived here independently, with helpers renamed to lenders.' % (
                fb['links']['deleted_prefix_gates'], len(fb['links']['derived_rewrites'])),
        ]
        receipt['not_checked'] = [
            'Exact Clifford (Gaussian, phase) lifts of K_G and their native lowering in either orientation.',
            'Hosting of the 64 frame-zero correction reads and of the X-register lenders (1,4,6,12,31,73) in a whole-call '
            'owner map; private cleanup buffers; owner fill at 400 helpers; global profile; kappa.',
        ]
    except Reject as e:
        ok = False
        receipt['failure'] = str(e)
        print('FAILED: %s' % e, flush=True)
    receipt['skip_controls'] = bool(args.skip_controls)
    receipt['result'] = PASS_LINE if (ok and not args.skip_controls) else FAIL_LINE
    receipt['model'] = __doc__.split('MODEL (stated precisely; see also the receipt field "model").')[1].strip()
    receipt['elapsed_s'] = round(time.time() - t0, 1)
    print('elapsed %.1f s' % (time.time() - t0))
    if args.out:
        with open(os.path.join(HERE, RECEIPT), 'w') as fh:
            json.dump(receipt, fh, indent=1, sort_keys=True, default=str)
            fh.write('\n')
        print('receipt written: %s' % os.path.join(HERE, RECEIPT))
    print(receipt['result'])
    return 0 if receipt['result'] == PASS_LINE else 1


if __name__ == '__main__':
    sys.exit(main())
