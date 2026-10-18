#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Standalone independent recount of the 80-alias T74 whole-helper owner fill (OWNERS-80.json.gz).

Object: OWNERS-80.json.gz of this package (research/t74-80alias-owner-fill/, sha256 pinned below): 266,400
literal roles hosting the 400 live helpers of the two 80-alias T74 borrow words of PR #2339
(BORROW-WORD-80base = provider gauge44, BORROW-WORD-80extra = provider extra; commit bf1742ae) in the idle
children of PR #2269's unchanged T74 template (head b479fc55: 74 replicas, nine stages, 666 calls).

This file is an adaptation of our own iteration-3 independent checker (fill_check.py and the frame recount of
words_check.py, research/t74-borrow43-independent-check/ at commit 4a2f20ea, Apache-2.0, same author).  It is
standalone: standard library only, it imports no module of this package (not build_fill.py, not
check_fill.py, not vendor/), and no code of PR #2269 / #2322 / #2339 is imported or run.  Every input is a git
blob read with `git cat-file` at a pinned commit and is pinned by git blob id *and* sha256.  The PR #2339 files
are read from commit bf1742ae when it is present; otherwise from the byte-identical copies in inputs/, which
must match the same blob ids and sha256 pins.  The recount does not read PROFILE-80.json or BUILD-RECEIPT.json;
those, and the builder's reported numbers (CLAIMS below), are only compared with the recount at the end.
All accepted facts are integer or GF(2) facts.  The script refuses `python -O`.

Hosting rules (PR858 / complex-double-replica-owners PROOF.md lineage; T16 owner audit rules R1-R7/X1):
  R-a  one role per (call, live helper): 666 calls x 400 helpers; helper i = i-th live helper register of the
       word (224..703 minus the 80 `removed`, increasing); width = dim(final frame) - dim(start frame) over
       GF(2), re-derived from both words (they have equal live registers and ordered widths, asserted).
  R-e  family = owner*896 + (2*pair(child)+side(child))*112 + port, copy = 112*owner + port; family inside the
       data namespace [0, W), W = 896*74 = 66304; not the caller's active pair; at most one helper per family
       per call.
  R-d  the call lies strictly inside the owner's actual window, rebuilt from the template's 30 per-replica
       source events expanded in ORDER (bridge-aware).  X1: rebuilt windows == PR #2269 new/PLAN.json windows.
  R-b  slices [offset, offset+width) lie in [0, rank(child)), are disjoint per bin (owner, child, port) and
       form an occupied prefix.
  R-c  idle remainders (rank - occupied, per bin) and the global profile sum_calls P_provider + idle are
       recounted here; P_provider is recounted from the word by the frame-climb rule (nested climbs + COPY
       charges) and compared with the word report and PR #2339's AUDIT receipts; rank-mass, deficit, capacity
       and halving identities.
  R-f  private namespace, stated as PR #2322 does (README "complete physical stock" and
       evidence/PRIVATE-NAMESPACE-INJECTION.json): physical = W + 8 centres + R reserved tableau + 2
       coefficient work; centres [W, W+8), reserved tableau [W+8, W+8+R), coefficient [P-2, P); the NZ
       private cleanup zero buffers (buffer register r + 704 for every hyperplane-ended live helper r) are
       injected in increasing order into [W+8, W+8+NZ), which must lie inside the reserved tableau (NZ <= R);
       every hosted helper family is a live data family (< W), hence disjoint from all private names.
       The same rule applied to (R, NZ) = (434, 78) must reproduce PR #2322's stated geometry exactly.
  R-g  X2 and 73-column charts (rule of PR #2269 independent_core.py check_pending_axes / check_roles, Hao Yan
       checker lineage): DATA-PHASES.json is read at the PR #2269 commit (blob pinned; its sha256 must equal the
       template's exact_data_phase_recipe_sha256) and its 112 port vectors must equal both words' ports.  Per
       port, the owner 73-frame is orthonormal; every ranked child's pending orthogonal axes are rank-many,
       distinct and in that frame, and children sharing a family (pair, side) have disjoint axes (X2).  Every
       role's slice binds pending[offset:offset+width] to a residual/spectator permutation of the 73 columns;
       the distinct charts are counted (positive control: PR #2269's fill gives its SPEC actual_73column_sigmas).

Positive control: the same pipeline on PR #2269's own fill (OWNERS.json.gz, 437 helpers of the 43-alias
words), including the PLAN per_call_widths comparison, must reproduce its idle {1:23976,3:8673,5:813,7:150,
48:24479} and its global profile.  For the 80-alias fill the PLAN per_call_widths comparison (437-helper
lists) is replaced by the word-derived widths; everything else of the static checks, including X1, is kept.
Negative controls: each mutation must be rejected by the check it targets.

Credits: PR2339 (this author: the 80-alias words); PR2269 Jeremy Kothe (jeremykothe2; T74 template,
windows, dispatch, owner-row format); PR2322 Vlado Vojdanovski (owner exchanges; the private-namespace
statement followed here); PR2312/PR2302 jeremykothe2; PR2226 Cinna Davis (anticipatory dirty borrowing);
PR1319/PR1297 T74 lineage (Rohan Arun et al.); hosting rules of Hao Yan's PR858 / complex-double-replica-owners
PROOF.md and the T16 owner audit (Josie Elliston; icekylinx / Zhihao Chen checker lineage).
Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B fill_check80.py [--repo PATH] [--words-from-inputs] [--skip-positive-control] [--out]
The final stdout line starts with PASS_T74_80ALIAS_FILL_INDEPENDENT or FAIL_T74_80ALIAS_FILL_INDEPENDENT.
"""

import argparse
import bisect
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter
from fractions import Fraction

if not __debug__:
    sys.stdout.write('FAIL_T74_80ALIAS_FILL_INDEPENDENT refusing to run under python -O\n')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
RECEIPT_NAME = 'fill_check80.receipt.json'
PASS_LINE = 'PASS_T74_80ALIAS_FILL_INDEPENDENT'
FAIL_LINE = 'FAIL_T74_80ALIAS_FILL_INDEPENDENT'

HEAD_2269 = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'
PKG_2269 = 'research/gmx-t74-borrow43'
HEAD_2322 = '002304ef01c4416a127916169ae6d94c1bee052b'
PKG_2322 = 'research/t74-joint-owner-hillclimb'
HEAD_2339 = 'bf1742aee4d855efb8bbd44a8419eddb33a679e5'
PKG_2339 = 'research/t74-low-alias-borrowing'

# package-relative path -> (git blob id, sha256)
PINS_2269 = {
    'OWNERS.json.gz': ('fc874cb553af5b984e34c1d8696d2213d7458f8f', '5a8c9a18c21f635563c9a6b6a433bcb1e804175ef23d677459033344aa2bd4e6'),
    'new/PROFILE.json': ('3e103605dd46c8754028056eb9dde9a73b9bfdca', '50fcc0960a47f6d35064d3b55ea6dcb4cebbd305aec215c8034f626718595538'),
    'new/SPEC.json': ('2431d1cebbb2e155356d2da160d60808498bc33d', 'bd091ed9e7f4939d06abb467d0d2c56ce0f34ba800d74132669f7b667e125d2d'),
    'new/PLAN.json': ('7cacd857edd0f29be5bd2ca9590a17fed4da17ba', 'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2'),
    'CONSTRUCTION.json': ('034ec6c6309bd1279661918f2a8706268f9a1200', '37b8605607b2877d82b8403d509f5cd224240064c93fa67ce89a8894acc6b460'),
    'GLOBAL-TEMPLATE.json.gz': ('5327fc2f4e8ea82ed356c94ff040d23fc73c731f', '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db'),
    'ORDER.json': ('7409c4df1092241729739596c7648bda504e6aad', '519d1d5dbb997a219fcfcad34c0b03e7838bef24199784d7e964fa10090f66e1'),
    'DISPATCH.json': ('20807cc27c82db1f8f9cd47c79713e066d6ad816', '6aad7f628f4c9b510a95c5b34357736303069ecf92a551659900b1ba540bc7e0'),
    'new/borrow/words/BORROW-WORD-43base.json.gz': ('448dd795adba29392a90b34aa3f1b1b796c7e0bd', '9492a5537fb87d9ca98dffcd0230f7625b3789744fa94e2f18acf23d91d998b5'),
    'new/borrow/words/BORROW-WORD-43extra.json.gz': ('2b51ba96256283bbc5578f99b694c50edd8a0e35', '87d51f5298101d5947f45c43ee02f0ec45d6acbddabb808d0d02db1eaf063734'),
    'new/borrow/receipts/AUDIT-43base.json': ('65728eff3ef61c275c873b58f0f8cebc095ef6f9', '9af87b149b8efa58e2454541dd1c5aef86d893c71ec488ae69fb8680c2f7936e'),
    'new/borrow/receipts/AUDIT-43extra.json': ('f9c2401401612b3b0b6e652e142e65bceadc1170', '849fbe9b9267180ba914237d751b118b4539731249c4482e6264d4772932fd2d'),
    'evidence/INDEPENDENT.json': ('16bb558f2472df730076a8163454c6f70b9e9fe3', '78cd00f832ed3c0a4b0e0d202095f7beb6111eaeb4457849d5bb920e983098a0'),
}
# DATA-PHASES.json of the template (outside the PR2269 package dir, present in the b479fc55 tree and on main).
PKG_PHASES = 'research/community-cold617-audit/pr600/replay/mixed-global/base/work/complex-nine-native'
PINS_PHASES = {
    'DATA-PHASES.json': ('d9a4f84211182ca200c081ea061d724c8a2cfb70', 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
}
PINS_2322 = {
    'evidence/PRIVATE-NAMESPACE-INJECTION.json': ('3588cb8991177c10059ce99bd3949220bbe52580', 'fad0f68aa273e39f63904462b7ade93c7c50c29d7278d0c37eee2139bbdcad65'),
    'CLAIM.json': ('e10747182e8bdfa2fea1c8631bf738c15619eccb', '439ded151e7897b8e7d5ef9ad47f3cd8d1daf0b69219ef507a922519c7003530'),
}
# PR #2339 files; inputs/<basename> is a byte-identical copy used when commit bf1742ae is absent.
PINS_2339 = {
    'words/BORROW-WORD-80base.json.gz': ('c5953dfdb0ee9ac0c2c73eb29e320582b4569d2b', '61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493'),
    'words/BORROW-WORD-80extra.json.gz': ('852868543ed36efa799b3ed6dd76a0442b0d6ff1', '1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5'),
    'receipts/AUDIT-80base.json': ('fc16634cfd3a9c5190e5b97b93cb29ddbd1547ca', 'd65a79658cba82932a9abd2c9af5dd345527141b098130b98850572420166cdd'),
    'receipts/AUDIT-80extra.json': ('b1b0c4d69e4c1a5edc3e9dd968f6f58b5eb8aaf0', '6d05abbc122d72b1eec05e7654a118dd492e55db34b30b718603521231094099'),
}
# The object under test (this package, untracked build output of build_fill.py).
OWNERS_80 = ('OWNERS-80.json.gz', 'b79d678dc8ae685fdecedca994e41b41c8a2930564ec0c58c707d7d13a3870a5')

# Builder's reported numbers (claims under test, written here from the build report; compared at the end only).
CLAIMS_80 = dict(
    roles=266400, cross_replica=251101, idle_remainders=69734,
    idle={1: 2644, 3: 10310, 5: 27847, 7: 6114, 41: 33, 48: 22786},
    profile={1: 1529770, 2: 354318, 3: 267386, 4: 83250, 5: 52489, 7: 6114, 8: 5328, 41: 33, 48: 22786},
    local={'gauge44': {1: 2303, 2: 527, 3: 386, 4: 125, 5: 37, 8: 8},
           'extra': {1: 2287, 2: 535, 3: 386, 4: 125, 5: 37, 8: 8}},
    inventory={4: 4, 5: 4, 7: 36, 8: 84, 9: 272}, zero_buffers=44)
CLAIMS_2269 = dict(idle={1: 23976, 3: 8673, 5: 813, 7: 150, 48: 24479})

# Geometry of the nine-stage, four-pair, 112-port controller (template/PLAN):
V = 112            # data ports per (pair, side)
H = 9              # local frame dimension
M = 73             # global dimension m
STAGES = 9
PAIRS = 4
FAMILIES_PER_REPLICA = 2 * PAIRS * V   # 896
CENTRES, COEFFICIENT_WORK = 8, 2
REGISTERS = 2 * V + 480                # n = 704: X, Y and helper registers of a word
ROW_LIMIT = 20161
ROW_CONSTANTS = 9909 + 252             # retained row formula 2*stock + 9909 + 252 + 2*payload
TAIL_KINDS = ('bank_padding_cover_sweep', 'translate_every_live_family')
ROLE_KEYS = ('child', 'copy', 'family', 'helper', 'offset', 'owner_replica',
             'port', 'replica', 'stage', 'time', 'width')


class CheckFailure(Exception):
    def __init__(self, check, detail):
        Exception.__init__(self, check + ': ' + detail)
        self.check = check
        self.detail = detail


def need(condition, check, detail):
    if not condition:
        raise CheckFailure(check, detail)


# ---------------------------------------------------------------- inputs ---

def git(repo, *args):
    proc = subprocess.run(['git', '-C', repo] + list(args), stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, check=False)
    need(proc.returncode == 0, 'input.git', 'git ' + ' '.join(args) + ' failed: '
         + proc.stderr.decode('utf-8', 'replace').strip())
    return proc.stdout


def commit_present(repo, commit):
    proc = subprocess.run(['git', '-C', repo, 'cat-file', '-e', commit + '^{commit}'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return proc.returncode == 0


def blob_id(data):
    return hashlib.sha1(('blob %d' % len(data)).encode() + b'\0' + data).hexdigest()


def verify(data, oid, sha, what):
    need(blob_id(data) == oid, 'input.pin', 'git blob id of ' + what)
    need(hashlib.sha256(data).hexdigest() == sha, 'input.pin', 'sha256 of ' + what)


def read_pinned(repo, commit, pkg, pins, label):
    need(commit_present(repo, commit), 'input.pin', '%s commit %s missing from %s (run run_all.py --fetch)'
         % (label, commit, repo))
    blobs, record = {}, {}
    for rel in sorted(pins):
        oid, sha = pins[rel]
        path = pkg + '/' + rel
        got = git(repo, 'rev-parse', '--verify', commit + ':' + path).decode().strip()
        need(got == oid, 'input.pin', path + ' resolves to ' + got + ', pinned ' + oid)
        data = git(repo, 'cat-file', 'blob', oid)
        verify(data, oid, sha, path)
        blobs[rel] = data
        record['%s:%s' % (commit[:12], path)] = dict(git_blob=oid, sha256=sha, bytes=len(data))
    return blobs, record


def read_2339(repo, force_inputs=False):
    """PR #2339 words/receipts: git blobs at bf1742ae if present (inputs/ copies must then be identical),
    else the inputs/ copies (same pins)."""
    use_git = commit_present(repo, HEAD_2339) and not force_inputs
    blobs, record = {}, {}
    for rel in sorted(PINS_2339):
        oid, sha = PINS_2339[rel]
        copy = os.path.join(HERE, 'inputs', os.path.basename(rel))
        path = PKG_2339 + '/' + rel
        if use_git:
            got = git(repo, 'rev-parse', '--verify', HEAD_2339 + ':' + path).decode().strip()
            need(got == oid, 'input.pin', path + ' resolves to ' + got + ', pinned ' + oid)
            data = git(repo, 'cat-file', 'blob', oid)
            if os.path.isfile(copy):
                with open(copy, 'rb') as handle:
                    need(handle.read() == data, 'input.pin', 'inputs copy differs from the git blob: ' + copy)
            source = 'git %s:%s' % (HEAD_2339[:12], path)
        else:
            need(os.path.isfile(copy), 'input.pin', 'commit %s absent and inputs copy missing: %s' % (HEAD_2339, copy))
            with open(copy, 'rb') as handle:
                data = handle.read()
            source = 'inputs/' + os.path.basename(rel)
        verify(data, oid, sha, path)
        blobs[rel] = data
        record['%s:%s' % (HEAD_2339[:12], path)] = dict(git_blob=oid, sha256=sha, bytes=len(data), read_from=source)
    return blobs, record, ('git' if use_git else 'inputs')


def parse_bytes(data, gz):
    if gz:
        data = gzip.decompress(data)
    return json.loads(data.decode('utf-8'), parse_float=Fraction)


def parse(blobs, rel):
    return parse_bytes(blobs[rel], rel.endswith('.gz'))


def as_profile(mapping, check, what):
    out = Counter()
    for key, value in mapping.items():
        need(type(value) is int and value >= 0 and str(int(key)) == str(key), check, what + ' profile entry')
        if value:
            out[int(key)] = value
    return out


def plain(counter):
    return {str(k): counter[k] for k in sorted(counter) if counter[k]}


def mass(counter):
    return sum(r * n for r, n in counter.items())


# ------------------------------------------------- GF(2) frames and widths ---
# (from our iteration-3 fill_check.py / words_check.py)

FULL = [1 << i for i in range(H)]


def gf2_rank(vectors, check):
    pivots = {}
    for x in vectors:
        need(type(x) is int and 0 <= x < 1 << H, check, 'frame vector outside GF(2)^9')
        while x:
            top = x.bit_length() - 1
            if top in pivots:
                x ^= pivots[top]
            else:
                pivots[top] = x
                break
    return len(pivots)


def parity(x):
    return bin(x).count('1') & 1


def echelon(vectors):
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


def contains(small, big):
    piv = echelon(big)
    for x in small:
        for b, vec in piv.items():
            if (x >> b) & 1:
                x ^= vec
        if x:
            return False
    return True


def perp(sub, h):
    return span([x for x in range(1, 1 << h) if all(parity(x & u) == 0 for u in sub)])


def word_helpers(word, label, removed_count):
    """Live helper registers, their residual widths and the hyperplane-ended set (R-a)."""
    check = 'R-a.word'
    report = word['report']
    need((report.get('v'), report.get('h'), report.get('R')) == (V, H, 480), check, label + ' dimensions')
    need(len(word['ports']) == V, check, label + ' port count')
    first, end = 2 * V, 2 * V + 480
    removed = list(word.get('removed', []))
    need(all(type(r) is int and first <= r < end for r in removed) and len(set(removed)) == len(removed),
         check, label + ' removed registers')
    need(len(removed) == removed_count, check, label + ' removed register count')
    removed_set = set(removed)
    for table in ('helper_final', 'start_extra'):
        for key in word[table]:
            need(first <= int(key) < end and int(key) not in removed_set, check,
                 label + ' ' + table + ' names a non-live register ' + key)
    live = [r for r in range(first, end) if r not in removed_set]
    widths, ended = [], []
    for r in live:
        final = word['helper_final'].get(str(r))
        if final is None:
            final = FULL
        else:
            ended.append(r)
        start = word['start_extra'].get(str(r), [])
        rank_final, rank_start = gf2_rank(final, check), gf2_rank(start, check)
        need(rank_final == len(final) and rank_start == len(start), check, label + ' dependent frame list at %d' % r)
        need(gf2_rank(list(final) + list(start), check) == rank_final, check,
             label + ' start frame not inside final frame at %d' % r)
        widths.append(rank_final - rank_start)
    return dict(live=live, removed=sorted(removed), widths=widths, hyperplane_ended=ended)


# ------------------------------------------------- local paid-profile recount ---
# Frame-climb rule of our iteration-3 words_check.py (frame_check), extended to the anticipatory initial
# corrections of PR2226/PR2339: they run first, at frame 0, and pay nothing.

def _dyadic(q):
    return q.denominator & (q.denominator - 1) == 0


def _gate(g, frame_of, where, allow_warp=False):
    check = 'R-c.local_format'
    need(isinstance(g, list) and g, check, 'gate is not a list at %s' % where)
    op = g[0]
    if op == 'add':
        need(len(g) == 6 and all(type(x) is int for x in g[1:5]) and g[4] > 0 and g[3] != 0 and g[1] != g[2],
             check, 'bad add at %s' % where)
        need(_dyadic(Fraction(g[3], g[4])), check, 'non-dyadic coefficient at %s' % where)
        return ('add', g[1], g[2], frame_of(g[5]))
    if op == 'scale':
        need(len(g) == 5 and all(type(x) is int for x in g[1:4]) and g[2] != 0 and g[3] != 0, check,
             'bad scale at %s' % where)
        q = Fraction(g[2], g[3])
        need(_dyadic(q) and abs(q.numerator) & (abs(q.numerator) - 1) == 0, check, 'scale not a dyadic unit at %s' % where)
        return ('scale', g[1], frame_of(g[4]))
    if op == 'warp' and allow_warp:
        need(len(g) == 4 and type(g[1]) is int and type(g[2]) is int and g[2] != 0, check, 'bad warp at %s' % where)
        return ('warp', g[1], frame_of(g[3]))
    raise CheckFailure(check, 'unknown primitive %r at %s' % (op, where))


def _regs(item):
    return (item[1], item[2]) if item[0] == 'add' else (item[1],)


def local_recount(w, label):
    """Paid local profile, helper widths and private zero buffers of one BORROW-WORD, recounted."""
    check = 'R-c.local'
    need(w.get('kind') == 'BORROW-WORD', check, label + ' not a BORROW-WORD')
    v, h, n = V, H, REGISTERS
    full = span(FULL)

    def frame_lit(F):
        if F is None:
            return None
        need(isinstance(F, list) and all(type(x) is int and 0 < x < (1 << h) for x in F), check, 'frame literal')
        return span(F)

    ports = w['ports']
    removed = set(w['removed'])
    live = [r for r in range(n) if r not in removed]
    start, end = {}, {}
    for i in range(v):
        start[i], end[i] = span([ports[i]]), full
        start[v + i], end[v + i] = (), perp(span([ports[i]]), h)
    for r in live:
        if r >= 2 * v:
            start[r], end[r] = (), full
    for k, F in w['start_extra'].items():
        need(int(k) in start and int(k) >= 2 * v, check, label + ' start_extra register')
        start[int(k)] = frame_lit(F)
    restored = set()
    for k, F in w['helper_final'].items():
        need(int(k) in end and int(k) >= 2 * v, check, label + ' helper_final register')
        end[int(k)] = frame_lit(F)
        restored.add(int(k))
    buffers = set(r + n for r in restored)
    sec = {name: [_gate(g, frame_lit, '%s[%d]' % (name, i)) for i, g in enumerate(w[name])]
           for name in ('precondition', 'compensation', 'A', 'cut', 'B', 'restore')}
    cleanup = [_gate(g, frame_lit, 'cleanup[%d]' % i, allow_warp=True) for i, g in enumerate(w['cleanup'])]
    warps = {}
    by_pos = {}
    for k, rec in enumerate(w['warps'], 1):
        need(isinstance(rec, list) and len(rec) == 5, check, 'warp record shape')
        pos, lender, _cols, U, E = rec
        need(type(pos) is int and 0 <= pos <= len(sec['B']) and lender in start and not (v <= lender < 2 * v), check,
             'warp %d position/lender' % k)
        warps[k] = dict(lender=lender, U=span(U), E=span(E))
        need(len(warps[k]['U']) == len(U) == len(E) == len(warps[k]['E']), check, 'warp %d frame dimensions' % k)
        by_pos.setdefault(pos, []).append(k)
    need(len(set(x['lender'] for x in warps.values())) == len(warps), check, 'a register lends twice')
    cur = {r: start[r] for r in live}
    paid, copies, per_reg = Counter(), Counter(), Counter()
    istarget = lambda r: v <= r < 2 * v

    def climb(r, F, where):
        need(r in cur, check, 'register %d is not live (%s)' % (r, where))
        need(contains(cur[r], F), check, 'non-nested climb of %d at %s' % (r, where))
        d = len(F) - len(cur[r])
        if d:
            paid[d] += 1
            per_reg[r] += d
        cur[r] = F

    # initial (anticipatory) corrections: t += c K_k s, both at frame 0, k a warp lent by s; pay nothing.
    for i, c in enumerate(w['initial_corrections']):
        t, s, word_k = c['target'], c['source'], c['operator_word']
        q = Fraction(c['coefficient'])
        need(istarget(t) and s in cur and not istarget(s) and cur[t] == () and cur[s] == (), check,
             'initial correction %d: target/source not at frame 0' % i)
        need(isinstance(word_k, list) and len(word_k) == 1 and word_k[0] in warps and warps[word_k[0]]['lender'] == s
             and q != 0 and _dyadic(q), check, 'initial correction %d: operator/coefficient' % i)
    for i, g in enumerate(sec['precondition'] + sec['compensation']):
        need(g[-1] == () and istarget(g[1]), check, 'precondition/compensation gate %d' % i)
        for r in _regs(g):
            climb(r, (), 'pre[%d]' % i)
    items = []
    for p in range(len(sec['B']) + 1):
        items.extend(('warp', k) for k in by_pos.get(p, []))
        if p < len(sec['B']):
            items.append(sec['B'][p])
    for i, g in enumerate(list(sec['A']) + [it for it in items if it[0] != 'warp'] + list(sec['restore'])):
        need(not (g[0] == 'add' and not istarget(g[1]) and istarget(g[2])), check,
             'a non-target register reads a target (item %d of A+B+restore)' % i)
    for i, g in enumerate(sec['A']):
        need(g[-1] is not None, check, 'unframed gate in A')
        for r in _regs(g):
            climb(r, g[-1], 'A[%d]' % i)
    levels = {int(k): frame_lit(F) for k, F in w['target_levels'].items()}
    for t in range(v):
        need(cur[v + t] == levels.get(t, ()), check, 'target %d not at its level after A' % t)
    centers, cframes = list(w['centers']), [frame_lit(F) for F in w['center_frames']]
    need(len(set(centers)) == len(centers) == len(cframes), check, 'centres')
    for q, U in zip(centers, cframes):
        need(q in cur and cur[q] == U, check, 'centre %d not at its centre frame after A' % q)
    served = {q: set() for q in centers}
    for i, g in enumerate(sec['cut']):
        need(g[0] == 'add' and g[-1] is None and istarget(g[1]) and g[2] in served, check, 'cut[%d]' % i)
        need(cur[g[1]] == levels.get(g[1] - v, ()), check, 'cut[%d] target off its level' % i)
        served[g[2]].add(cur[g[1]])
    for q, U in zip(centers, cframes):
        prev = U
        for T in sorted(served[q], key=lambda S: (-len(S), S)):
            need(contains(T, prev), check, 'centre %d copy levels not nested' % q)
            if T != prev:
                paid[len(prev) - len(T)] += 1
                copies[len(prev) - len(T)] += 1
            prev = T
    for i, it in enumerate(items):
        if it[0] == 'warp':
            wr = warps[it[1]]
            need(cur[wr['lender']] == wr['U'], check, 'warp %d: lender frame != U' % it[1])
            cur[wr['lender']] = wr['E']
        else:
            need(it[-1] is not None, check, 'unframed gate in B')
            for r in _regs(it):
                climb(r, it[-1], 'B item %d' % i)
    for i, g in enumerate(sec['restore']):
        need(g[-1] is not None, check, 'unframed gate after B')
        for r in _regs(g):
            climb(r, g[-1], 'restore[%d]' % i)
    for r in live:
        climb(r, end[r], 'end frame')
    touched_buffers = set()
    for i, it in enumerate(cleanup):
        need(it[-1] == full, check, 'cleanup item %d not at FULL' % i)
        for r in ((it[1],) if it[0] == 'warp' else _regs(it)):
            if r in buffers:
                touched_buffers.add(r)
                continue
            need(r in cur and cur[r] == full, check, 'cleanup item %d touches %d not at FULL / not a buffer' % (i, r))
    need(touched_buffers == buffers, check, label + ' cleanup does not use exactly the declared zero buffers')
    for r in live:
        need(per_reg[r] == len(end[r]) - len(start[r]), check, 'per-register charge != width for %d' % r)
    helpers = [r for r in live if r >= 2 * v]
    return dict(paid=+paid, copies=+copies, widths=[len(end[r]) - len(start[r]) for r in helpers], live_helpers=helpers,
                buffers=sorted(buffers), mass=mass(paid), corrections=len(w['initial_corrections']),
                warps=len(warps))


def load_word(blobs, rel, audit_rel, label, removed_count, claimed_local=None, claimed_inventory=None):
    word = parse(blobs, rel)
    audit = parse(blobs, audit_rel) if audit_rel else None
    info = word_helpers(word, label, removed_count)
    rec = local_recount(word, label)
    need(rec['live_helpers'] == info['live'] and rec['widths'] == info['widths'], 'R-a.word',
         label + ' frame-recount widths != GF(2) rank widths')
    inventory = Counter(info['widths'])
    need(inventory == as_profile(word['report']['width_inventory'], 'R-a.word', label), 'R-a.word',
         label + ' width inventory vs word report')
    local = rec['paid']
    need(local == as_profile(word['report']['local_profile'], 'R-c.local', label), 'R-c.local',
         label + ' recounted local profile %s != word report %s' % (plain(local), word['report']['local_profile']))
    need(rec['copies'] == Counter({8: 8}), 'R-c.local', label + ' COPY children')
    need(rec['buffers'] == sorted(r + REGISTERS for r in info['hyperplane_ended']), 'R-f.zero_buffers',
         label + ' buffers = r + 704 for the hyperplane-ended live helpers')
    if audit is not None:
        need(as_profile(audit['local_profile'], 'R-c.local', 'audit') == local and
             as_profile(audit['width_inventory'], 'R-a.word', 'audit') == inventory and
             audit['zero_buffers'] == audit['restored_cold'] == len(rec['buffers']), 'R-c.local',
             label + ' vs AUDIT receipt')
    if claimed_local is not None:
        need(local == Counter(claimed_local), 'R-c.local', label + ' local profile vs build report')
    if claimed_inventory is not None:
        need(inventory == Counter(claimed_inventory), 'R-a.word', label + ' inventory vs build report')
    return dict(widths=info['widths'], live=info['live'], removed=info['removed'], local=local, inventory=inventory,
                buffers=rec['buffers'], local_mass=rec['mass'], width_sum=sum(info['widths']),
                corrections=rec['corrections'], warps=rec['warps'])


# --------------------------------------------------------------- context ---

def derive_schedule(T, template, order):
    """Expand the 30 per-replica source events in call order; rebuild windows (verbatim iteration-3 rule)."""
    src = template['execution_schedule']
    need([i for i, e in enumerate(src) if e['kind'] in TAIL_KINDS] == [len(src) - 2, len(src) - 1],
         'R-d.schedule', 'global tail events')
    per_replica = [i for i, e in enumerate(src) if e['kind'] not in TAIL_KINDS]
    need(per_replica == list(range(30)), 'R-d.schedule', 'thirty per-replica source events')
    stage_pair = {}
    for e in template['recipe']:
        if e['kind'] == 'local':
            need(e['stage'] not in stage_pair and 0 <= e['pair'] < PAIRS, 'R-d.schedule', 'recipe stage/pair')
            stage_pair[e['stage']] = e['pair']
    need(set(stage_pair) == set(range(STAGES)), 'R-d.schedule', 'recipe stages')
    blocks, stage = {}, None
    for i in per_replica:
        e = src[i]
        if e['kind'] == 'local_cover_sweep':
            stage = e['stage']
            need(stage not in blocks and e['replicas'] == list(range(T)), 'R-d.schedule', 'local sweep block')
            blocks[stage] = []
        need(stage is not None, 'R-d.schedule', 'event before first local sweep')
        need(e['kind'] in ('local_cover_sweep', 'idle_cover_sweep', 'bridge', 'terminal_Y_translations', 'terminal'),
             'R-d.schedule', 'unknown source event kind ' + str(e['kind']))
        blocks[stage].append((i, e))
    need(set(blocks) == set(range(STAGES)), 'R-d.schedule', 'stage blocks')
    rank = {}
    for c in template['idle_children']:
        need(c['replicas'] == T and 0 <= c['port'] < V and type(c['rank']) is int and c['rank'] > 0,
             'R-d.schedule', 'idle child record')
        need(rank.setdefault(c['child'], c['rank']) == c['rank'], 'R-d.schedule', 'child rank depends on port')
    need(len(template['idle_children']) == V * len(rank), 'R-d.schedule', 'idle children per port')
    seen = Counter((c['child'], c['port']) for c in template['idle_children'])
    need(all(n == 1 for n in seen.values()), 'R-d.schedule', 'duplicate idle child record')
    events = []
    for t, (s, r) in enumerate(order):
        for i, e in blocks[s]:
            events.append((i, e, r, t))
    projection = {}
    for i, e, r, t in events:
        projection.setdefault(r, []).append(i)
    need(set(projection) == set(range(T)) and all(p == per_replica for p in projection.values()),
         'R-d.schedule', 'per-replica source-event projection')
    last, windows, callpos, child_pair, child_side = {}, {}, {}, {}, {}
    rankless = set()
    bridges = 0
    for pos, (i, e, r, t) in enumerate(events):
        kind = e['kind']
        if kind == 'local_cover_sweep':
            callpos[t] = pos
            last[r, stage_pair[e['stage']]] = pos
        elif kind == 'bridge':
            bridges += 1
            last[r, e['src']] = pos
            last[r, e['dst']] = pos
        elif kind == 'idle_cover_sweep':
            for side, child in enumerate(e['child_indices']):
                if child not in rank:
                    rankless.add(child)   # a swept child without an idle_children record has no capacity
                    continue
                need((r, child) not in windows, 'R-d.schedule', 'idle sweep child')
                need(child_pair.setdefault(child, e['pair']) == e['pair'] and
                     child_side.setdefault(child, side) == side, 'R-d.schedule', 'child pair/side')
                windows[r, child] = (last.get((r, e['pair']), -1), pos)
        else:   # terminal events touch every pair; they follow every idle sweep of the replica
            for p in range(PAIRS):
                last[r, p] = pos
    need(len(windows) == T * len(rank) and set(callpos) == set(range(len(order))), 'R-d.schedule', 'window inventory')
    positions = [callpos[t] for t in range(len(order))]
    need(all(a < b for a, b in zip(positions, positions[1:])), 'R-d.schedule', 'call positions increase')
    times = {}
    for key, (lo, hi) in windows.items():
        times[key] = list(range(bisect.bisect_right(positions, lo), bisect.bisect_left(positions, hi)))
    return dict(stage_pair=stage_pair, rank=rank, windows=windows, callpos=positions, child_pair=child_pair,
                child_side=child_side, window_times=times, bridges=bridges, events=len(events),
                rankless_children=sorted(rankless))


def check_static(ctx, sched):
    """Order, dispatch, (optionally) PLAN per-call widths, and X1 (PLAN windows == rebuilt windows)."""
    T, order, plan = ctx['T'], ctx['order'], ctx['plan']
    need(len(order) == STAGES * T and set(order) == {(s, r) for s in range(STAGES) for r in range(T)},
         'R-0.order', 'call inventory')
    need(plan['order'] == [list(x) for x in order], 'R-0.order', 'PLAN order')
    need(set(ctx['dispatch']) == set(order), 'R-0.dispatch', 'dispatch inventory')
    need(len(plan['provider_calls']) == len(order), 'R-0.dispatch', 'PLAN call records')
    for t, (s, r) in enumerate(order):
        pc = plan['provider_calls'][t]
        need((pc['stage'], pc['replica']) == (s, r) and pc.get('time', t) == t and
             pc['provider'] == ctx['dispatch'][s, r], 'R-0.dispatch', 'PLAN provider call %d' % t)
        if ctx['plan_widths']:
            pw = plan['per_call_widths'][t]
            need((pw['stage'], pw['replica']) == (s, r) and pw.get('time', t) == t, 'R-0.widths', 'PLAN width call %d' % t)
            need(pw['widths'] == ctx['widths'][ctx['dispatch'][s, r]], 'R-0.widths', 'PLAN per-call widths at %d' % t)
    pw = plan['windows']
    need(len(pw) == len(sched['windows']), 'R-d.plan_windows', 'window count')
    for (r, c), times in sched['window_times'].items():
        key = '%d,%d' % (r, c)
        need(key in pw and pw[key] == [sched['rank'][c], times], 'R-d.plan_windows', 'PLAN window ' + key)


def check_roles(ctx, sched, rows):
    """R-a, R-e, R-d, R-b on the literal roles and the R-c recount (no claim is read here)."""
    T, R, W, order = ctx['T'], ctx['R'], ctx['W'], ctx['order']
    at = {key: t for t, key in enumerate(order)}
    provider = [ctx['dispatch'][key] for key in order]
    # ---- R-a: one role per (call, live helper) at the helper's width
    need(len(rows) == len(order) * R, 'R-a.count', '%d roles, expected %d calls x %d helpers' % (len(rows), len(order), R))
    have = [0] * len(order)
    seen_helper = set()
    for z in rows:
        need(type(z) is dict and tuple(sorted(z)) == ROLE_KEYS and all(type(z[k]) is int for k in ROLE_KEYS),
             'R-a.schema', 'role fields')
        t = at.get((z['stage'], z['replica']))
        need(t is not None and z['time'] == t, 'R-a.call', 'role call/time')
        need(0 <= z['helper'] < R, 'R-a.helper_range', 'helper index')
        key = (t, z['helper'])
        need(key not in seen_helper, 'R-a.duplicate_helper', 'helper %d twice in call %d' % (z['helper'], t))
        seen_helper.add(key)
        need(z['width'] == ctx['widths'][provider[t]][z['helper']], 'R-a.width', 'width of helper %d in call %d' % (z['helper'], t))
        have[t] += 1
    need(all(n == R for n in have), 'R-a.complete', 'per-call helper inventory')
    # ---- R-e: physical family identity, namespace, active pair, one helper per family per call
    rank, pair, side, stage_pair = sched['rank'], sched['child_pair'], sched['child_side'], sched['stage_pair']
    seen_family = set()
    cross = 0
    for z in rows:
        need(0 <= z['owner_replica'] < T and z['child'] in rank and 0 <= z['port'] < V, 'R-e.coords', 'owner coordinates')
        need(0 <= z['family'] < W, 'R-e.namespace', 'family %d outside data namespace [0,%d)' % (z['family'], W))
        expect = z['owner_replica'] * FAMILIES_PER_REPLICA + (2 * pair[z['child']] + side[z['child']]) * V + z['port']
        need(z['family'] == expect and z['copy'] == V * z['owner_replica'] + z['port'], 'R-e.family_identity',
             'family/copy identity')
        need(not (z['owner_replica'] == z['replica'] and pair[z['child']] == stage_pair[z['stage']]),
             'R-e.active_pair', 'helper hosted on the caller active pair')
        key = (z['time'], z['family'])
        need(key not in seen_family, 'R-e.family_unique_per_call', 'two helpers on family %d in call %d' % key[::-1])
        seen_family.add(key)
        cross += z['owner_replica'] != z['replica']
    # ---- R-d: strictly inside the owner's actual (bridge-aware) window
    callpos, windows = sched['callpos'], sched['windows']
    for z in rows:
        lo, hi = windows[z['owner_replica'], z['child']]
        need(lo < callpos[z['time']] < hi, 'R-d.window', 'role outside window of owner %d child %d' % (z['owner_replica'], z['child']))
    # ---- R-b: capacity, disjoint slices per bin, occupied prefix
    used = {}
    for z in rows:
        need(z['offset'] >= 0 and z['width'] >= 1 and z['offset'] + z['width'] <= rank[z['child']], 'R-b.capacity',
             'slice outside child capacity')
        b = (z['owner_replica'], z['child'], z['port'])
        cells = ((1 << z['width']) - 1) << z['offset']
        old = used.get(b, 0)
        need(not old & cells, 'R-b.overlap', 'overlapping slices in bin %s' % (b,))
        used[b] = old | cells
    for b, cells in used.items():
        need(cells & (cells + 1) == 0, 'R-b.prefix', 'occupied cells of bin %s are not a prefix' % (b,))
    # ---- R-c: recount idle remainders and the global profile; pure identities
    idle = Counter()
    for (owner, child) in windows:
        for port in range(V):
            left = rank[child] - bin(used.get((owner, child, port), 0)).count('1')
            if left:
                idle[left] += 1
    local = Counter()
    for p in provider:
        local.update(ctx['local_profiles'][p])
    profile = local + idle
    total = mass(profile)
    need(M * W - total == 320 * T, 'R-c.mass', 'deficit identity m*W - mass = 320*T')
    need(total == (M - 1) * W + 64 * len(order), 'R-c.mass', 'mass = (m-1)W + 64 calls')
    capacity = T * V * sum(rank.values())
    hosted_width = sum(z['width'] for z in rows)
    need(mass(idle) == capacity - hosted_width, 'R-c.mass', 'idle mass = capacity - hosted width')
    need(total == mass(local) + capacity - hosted_width, 'R-c.mass', 'mass decomposition')
    need(M * M > 2 * max(profile) ** 2, 'R-c.mass', 'halving guard m^2 > 2*maxchild^2')
    family_children = {}
    for z in rows:
        family_children.setdefault(z['family'], set()).add(z['child'])
    return dict(roles=len(rows), calls=len(order), helpers_per_call=R, bins=T * V * len(rank),
                occupied_bins=len(used), cross_replica_roles=cross, idle=plain(idle),
                hosted_families=len(family_children), max_hosted_family=max(family_children),
                idle_remainders=sum(idle.values()), profile=plain(profile), rank_mass=total,
                deficit=M * W - total, live=W, idle_capacity=capacity, hosted_width=hosted_width,
                idle_mass=mass(idle), local_mass=mass(local), max_child=max(profile),
                provider_counts=dict(Counter(provider)))


def compare_claims(ctx, rec):
    """Compare the recount with the claims (only after the recount)."""
    claims = ctx['claims']
    idle = as_profile(rec['idle'], 'R-c.idle', 'recount')
    profile = as_profile(rec['profile'], 'R-c.profile', 'recount')
    for source, claimed in claims['idle']:
        need(idle == claimed, 'R-c.idle', 'recounted idle %s differs from %s %s' % (rec['idle'], source, plain(claimed)))
    for source, claimed in claims['profile']:
        need(profile == claimed, 'R-c.profile', 'recounted global profile differs from ' + source)
    for key, source, value in claims.get('scalars', []):
        need(rec[key] == value, 'R-c.counts', '%s %r differs from %s %r' % (key, rec[key], source, value))


def run_pipeline(ctx, sched, rows):
    check_static(ctx, sched)
    rec = check_roles(ctx, sched, rows)
    compare_claims(ctx, rec)
    return rec


def dispatch_map(records, check):
    out = {}
    for s, r, p in records:
        need((s, r) not in out, check, 'duplicate dispatch')
        out[s, r] = p
    return out


# ------------------------------------------------------------ case setup ---

def template_2269(blobs):
    plan = parse(blobs, 'new/PLAN.json')
    spec = parse(blobs, 'new/SPEC.json')
    template = parse(blobs, 'GLOBAL-TEMPLATE.json.gz')
    order = [tuple(x) for x in parse(blobs, 'ORDER.json')]
    dispatch = dispatch_map(parse(blobs, 'DISPATCH.json'), 'R-0.dispatch')
    construction = parse(blobs, 'CONSTRUCTION.json')
    T = plan['T']
    need(T == 74 and (plan['K'], plan['L'], plan['M']) == (PAIRS, STAGES, M), 'R-0.plan', 'PLAN geometry')
    need(order == [tuple(x) for x in plan['order']] == [tuple(x) for x in spec['call_order']], 'R-0.order',
         'ORDER.json = PLAN order = SPEC call_order')
    need(dispatch == dispatch_map(spec['dispatch'], 'R-0.dispatch'), 'R-0.dispatch', 'DISPATCH.json = SPEC dispatch')
    need(Counter(dispatch.values()) == Counter({'gauge44': 249, 'extra': 417}) ==
         Counter(construction['dispatch']), 'R-0.dispatch', 'provider call counts 249 gauge44 + 417 extra')
    need(spec['expected']['live'] == plan['live'] == FAMILIES_PER_REPLICA * T, 'R-0.plan', 'live data families')
    return dict(T=T, plan=plan, spec=spec, template=template, order=order, dispatch=dispatch, construction=construction)


def context(name, tpl, helpers, widths, local_profiles, claims, plan_widths):
    return dict(name=name, T=tpl['T'], R=helpers, W=FAMILIES_PER_REPLICA * tpl['T'], order=tpl['order'],
                dispatch=tpl['dispatch'], widths=widths, local_profiles=local_profiles, plan=tpl['plan'],
                claims=claims, plan_widths=plan_widths)


def words_80(b2339):
    out = {}
    for pid, tag in (('gauge44', 'base'), ('extra', 'extra')):
        out[pid] = load_word(b2339, 'words/BORROW-WORD-80%s.json.gz' % tag, 'receipts/AUDIT-80%s.json' % tag,
                             '80' + tag, 80, CLAIMS_80['local'][pid], CLAIMS_80['inventory'])
        need(len(out[pid]['live']) == 400 and len(out[pid]['buffers']) == CLAIMS_80['zero_buffers'], 'R-a.word',
             pid + ' 400 live helpers / 44 zero buffers')
        need(out[pid]['local_mass'] == 1856 + out[pid]['width_sum'], 'R-c.local', pid + ' local mass = 1856 + widths')
    need(out['gauge44']['live'] == out['extra']['live'] and out['gauge44']['widths'] == out['extra']['widths'],
         'R-a.word', 'helper map is provider independent (same live registers and ordered widths)')
    need(out['gauge44']['removed'] == out['extra']['removed'], 'R-a.word', 'both words remove the same registers')
    return out


def load_owners80():
    path = os.path.join(HERE, OWNERS_80[0])
    with open(path, 'rb') as handle:
        raw = handle.read()
    need(hashlib.sha256(raw).hexdigest() == OWNERS_80[1], 'input.pin', 'sha256 of ' + OWNERS_80[0])
    return json.loads(gzip.decompress(raw).decode('utf-8')), raw


def claim_files_80():
    """PROFILE-80.json and BUILD-RECEIPT.json (builder outputs): claims only, compared after the recount."""
    out, record = {}, {}
    for name in ('PROFILE-80.json', 'BUILD-RECEIPT.json'):
        path = os.path.join(HERE, name)
        if os.path.isfile(path):
            with open(path, 'rb') as handle:
                data = handle.read()
            out[name] = json.loads(data.decode('utf-8'))
            record[name] = hashlib.sha256(data).hexdigest()
    return out, record


def case_80(repo, force_inputs):
    b2269, rec2269 = read_pinned(repo, HEAD_2269, PKG_2269, PINS_2269, 'PR2269')
    b2339, rec2339, mode = read_2339(repo, force_inputs)
    tpl = template_2269(b2269)
    words = words_80(b2339)
    rows, raw = load_owners80()
    files, file_record = claim_files_80()
    claims = dict(idle=[('build report (hard-coded)', Counter(CLAIMS_80['idle']))],
                  profile=[('build report (hard-coded)', Counter(CLAIMS_80['profile']))],
                  scalars=[('roles', 'build report', CLAIMS_80['roles']),
                           ('cross_replica_roles', 'build report', CLAIMS_80['cross_replica']),
                           ('idle_remainders', 'build report', CLAIMS_80['idle_remainders'])])
    if 'PROFILE-80.json' in files:
        claims['profile'].append(('PROFILE-80.json', as_profile(files['PROFILE-80.json'], 'R-c.profile', 'PROFILE-80')))
    if 'BUILD-RECEIPT.json' in files:
        b = files['BUILD-RECEIPT.json']
        claims['idle'].append(('BUILD-RECEIPT.json idle', as_profile(b['idle'], 'R-c.idle', 'receipt')))
        claims['profile'].append(('BUILD-RECEIPT.json profile', as_profile(b['profile'], 'R-c.profile', 'receipt')))
        claims['scalars'] += [(k, 'BUILD-RECEIPT.json', b[k]) for k in
                              ('roles', 'cross_replica_roles', 'idle_remainders', 'rank_mass', 'hosted_width',
                               'idle_mass', 'idle_capacity')]
        need(b['owners_sha256'] == OWNERS_80[1], 'R-0.pins', 'BUILD-RECEIPT owners sha256')
    ctx = context('ext80-T74', tpl, 400, {p: words[p]['widths'] for p in words},
                  {p: words[p]['local'] for p in words}, claims, plan_widths=False)
    record = dict(rec2269)
    record.update(rec2339)
    record['package:' + OWNERS_80[0]] = dict(sha256=OWNERS_80[1], git_blob=blob_id(raw), bytes=len(raw))
    return ctx, rows, tpl, words, b2269, dict(inputs=record, pr2339_source=mode, claim_files_sha256=file_record)


def case_2269(b2269, tpl):
    """Positive control: PR #2269's own 437-helper fill on the same template, PLAN widths included."""
    words = {}
    for pid, tag in (('gauge44', 'base'), ('extra', 'extra')):
        words[pid] = load_word(b2269, 'new/borrow/words/BORROW-WORD-43%s.json.gz' % tag,
                               'new/borrow/receipts/AUDIT-43%s.json' % tag, '43' + tag, 43)
    spec, construction = tpl['spec'], tpl['construction']
    exp = spec['expected']
    claims = dict(idle=[('hard-coded #2269 idle', Counter(CLAIMS_2269['idle'])),
                        ('CONSTRUCTION.json idle', as_profile(construction['idle'], 'R-c.idle', 'construction')),
                        ('new/SPEC.json idle_remainder_profile', as_profile(exp['idle_remainder_profile'], 'R-c.idle', 's'))],
                  profile=[('new/PROFILE.json', as_profile(parse(b2269, 'new/PROFILE.json'), 'R-c.profile', 'p')),
                           ('new/SPEC.json global_profile', as_profile(exp['global_profile'], 'R-c.profile', 's'))],
                  scalars=[('roles', 'new/SPEC.json hosted_residuals', exp['hosted_residuals']),
                           ('cross_replica_roles', 'new/SPEC.json', exp['cross_replica_helper_roles']),
                           ('idle_remainders', 'new/SPEC.json', exp['idle_remainders']),
                           ('rank_mass', 'new/SPEC.json', exp['rank_mass'])])
    ctx = context('pr2269-borrow43-T74', tpl, 437, {p: words[p]['widths'] for p in words},
                  {p: words[p]['local'] for p in words}, claims, plan_widths=True)
    return ctx, parse(b2269, 'OWNERS.json.gz'), words


# ------------------------------------------------------- R-f: private namespace ---

def private_namespace(W, R, buffers, hosted_max):
    """Rule as stated by PR #2322: physical = W + 8 + R + 2; centres [W, W+8), reserved tableau [W+8, W+8+R),
    coefficient [P-2, P); zero buffers injected in increasing order into [W+8, W+8+NZ); NZ <= R; every hosted
    family is live (< W).  Returns the geometry in PR #2322's PRIVATE-NAMESPACE-INJECTION field names."""
    check = 'R-f.namespace'
    NZ = len(buffers)
    P = W + CENTRES + R + COEFFICIENT_WORK
    need(0 < NZ <= R, check, '%d zero buffers do not fit the %d-field reserved tableau' % (NZ, R))
    zp = {z: W + CENTRES + j for j, z in enumerate(sorted(buffers))}
    centres = set(range(W, W + CENTRES))
    work = {P - 2, P - 1}
    aux = set(zp.values()) | centres | work
    need(len(aux) == NZ + CENTRES + COEFFICIENT_WORK and min(aux) == W and max(aux) == P - 1, check, 'private names')
    need(max(zp.values()) < W + CENTRES + R and not set(zp.values()) & (work | centres), check,
         'buffer fields outside the reserved tableau')
    need(hosted_max < W, check, 'a hosted helper family is not a live data family')
    return dict(live=W, centers=[W, W + CENTRES], reserved_tableau=[W + CENTRES, W + CENTRES + R],
                coefficient=[P - 2, P], physical=P, buffer_fields=[W + CENTRES, W + CENTRES + NZ],
                remaining_reserve=R - NZ, native_helpers=R, zero_buffers=NZ)


def stock_group():
    """The retained 73-dimensional group factor 2^(36*36) * prod_{i=1}^{36} (2^(2i) - 1)."""
    g = 2 ** (36 * 36)
    for i in range(1, 37):
        g *= 2 ** (2 * i) - 1
    return g


def physical_rows(b2269, W, calls, physicals):
    """Stock bits and row coefficient (iteration-3 R-f formula, re-derived against PR #2269 INDEPENDENT.json)."""
    independent = parse(b2269, 'evidence/INDEPENDENT.json')
    g = stock_group()
    payload = 1 << (192 + (M + 1) // 2 + 2 * calls + 4).bit_length()

    def charge(physical):
        bits = (g * physical).bit_length()
        return dict(physical=physical, stock_bits=bits, row_coefficient=2 * bits + ROW_CONSTANTS + 2 * payload)

    ref = charge(independent['physical'])
    need((ref['stock_bits'], ref['row_coefficient'], independent['charged_prefix_bits']) ==
         (independent['physical_stock_bits'], independent['physical_row_coefficient'], payload),
         'R-f.formula', 'stock/row formula does not reproduce PR2269 evidence/INDEPENDENT.json')
    rows = {name: charge(p) for name, p in physicals.items()}
    for name, row in rows.items():
        need(row['row_coefficient'] < ROW_LIMIT, 'R-f.row', name + ' row coefficient')
    return dict(payload_bits=payload, row_limit=ROW_LIMIT, rows=rows,
                formula_reproduces=dict(physical=independent['physical'], stock_bits=ref['stock_bits'],
                                        row=ref['row_coefficient']))


# ------------------------------------------- R-g: X2 pending axes and 73-column charts ---

def load_phases(repo, template, port_lists):
    """DATA-PHASES.json at the PR2269 commit, bound to the template's data-phase pin and to the word ports."""
    blobs, record = read_pinned(repo, HEAD_2269, PKG_PHASES, PINS_PHASES, 'PR2269 tree')
    need(PINS_PHASES['DATA-PHASES.json'][1] == template['exact_data_phase_recipe_sha256'], 'R-g.phases',
         'DATA-PHASES sha256 != GLOBAL-TEMPLATE exact_data_phase_recipe_sha256')
    phases = parse(blobs, 'DATA-PHASES.json')
    ports = [x['q'] for x in phases['recipes']]
    need(phases['ports'] == V and [x['port'] for x in phases['recipes']] == list(range(V)), 'R-g.phases', 'port records')
    need(all(p == ports for p in port_lists), 'R-g.phases', 'DATA-PHASES port vectors != word ports')
    return phases, ports, record


def owner_bases(ports):
    """Orthonormal 73-column owner frame per port (PR2269 independent_core.py make_context, verbatim rule)."""
    bases = []
    for q in ports:
        zero = next(i for i in range(H) if not (q >> i & 1))
        correction = q ^ (1 << zero)
        axes = list(range(H))
        axes[0], axes[zero] = axes[zero], axes[0]
        frame = [(1 << i) ^ (correction if correction >> i & 1 else 0) for i in axes] + [1 << i for i in range(H, M)]
        need(all(bin(x & y).count('1') % 2 == int(i == j) for i, x in enumerate(frame) for j, y in enumerate(frame)),
             'R-g.pending_axes', 'non-orthonormal owner basis')
        bases.append(frame)
    return bases


def pending_axes_and_charts(sched, phases, bases, rows):
    """X2 (disjoint pending axes of children sharing a family) and one 73-column chart per role slice."""
    rank, pair, side = sched['rank'], sched['child_pair'], sched['child_side']
    checked = 0
    for port, frame in enumerate(bases):
        used, fset = {}, set(frame)
        for child in sorted(rank):
            axes = [int(x) for x in phases['recipes'][port]['idle_children'][child]['orthogonal_axes']]
            need(len(axes) == rank[child] == len(set(axes)) and set(axes) <= fset, 'R-g.pending_axes',
                 'pending axes of child %d at port %d' % (child, port))
            fam = used.setdefault((pair[child], side[child]), set())
            need(not fam & set(axes), 'R-g.pending_axes', 'overlapping pending children on one family (X2)')
            fam.update(axes)
            checked += 1
    charts, cache = set(), {}
    for z in rows:
        key = (z['port'], z['child'], z['offset'], z['width'])
        if key not in cache:
            frame = bases[z['port']]
            pending = [int(x) for x in phases['recipes'][z['port']]['idle_children'][z['child']]['orthogonal_axes']]
            need(z['offset'] + z['width'] <= len(pending) and z['width'] <= H, 'R-g.chart', 'slice beyond pending axes')
            occupied = [frame.index(x) for x in pending[z['offset']:z['offset'] + z['width']]]
            spectators = [i for i in range(M) if i not in occupied][:H - z['width']]
            perm = occupied + spectators + [i for i in range(M) if i not in occupied and i not in spectators]
            need(len(set(occupied + spectators)) == H and sorted(perm) == list(range(M)) and
                 [frame[i] for i in perm[:z['width']]] == pending[z['offset']:z['offset'] + z['width']],
                 'R-g.chart', 'residual/spectator permutation')
            cache[key] = tuple(frame[i] for i in perm)
        charts.add(cache[key])
    return dict(pending_axis_checks=checked, chart_keys=len(cache), actual_73column_charts=len(charts))


# ------------------------------------------------------- negative controls ---

def controls(ctx, sched, rows, words, b2339, phases=None, bases=None):
    T, W, order = ctx['T'], ctx['W'], ctx['order']
    pair, side, stage_pair, rank = sched['child_pair'], sched['child_side'], sched['stage_pair'], sched['rank']
    by_call = {}
    for i, z in enumerate(rows):
        by_call.setdefault(z['time'], []).append(i)
    family_index = {(z['time'], z['family']): i for i, z in enumerate(rows)}
    helper_index = {(z['time'], z['helper']): i for i, z in enumerate(rows)}
    out = []

    def replaced(changes):
        new = list(rows)
        for i, z in changes.items():
            new[i] = z
        return new

    def expect(name, expected, fn):
        try:
            fn()
        except CheckFailure as exc:
            need(exc.check == expected, 'control', name + ' rejected by ' + exc.check + ' (' + exc.detail +
                 '), expected ' + expected)
            out.append(dict(name=name, rejected_by=exc.check, detail=exc.detail[:200]))
            return
        raise CheckFailure('control', 'negative control accepted: ' + name)

    def run(name, expected, mutant_rows, mutant_ctx=None):
        expect(name, expected, lambda: run_pipeline(mutant_ctx or ctx, sched, mutant_rows))

    call0 = by_call[0]
    a, b = next((i, j) for i in call0 for j in call0 if i < j and rows[i]['width'] == rows[j]['width'])
    run('duplicate_role (helper twice in one call)', 'R-a.duplicate_helper',
        replaced({b: dict(rows[b], helper=rows[a]['helper'])}))
    run('dropped_role', 'R-a.count', rows[1:])
    i = next(k for k, z in enumerate(rows) if z['width'] > 1)
    run('narrowed_width', 'R-a.width', replaced({i: dict(rows[i], width=rows[i]['width'] - 1)}))
    run('family_in_private_namespace', 'R-e.namespace', replaced({0: dict(rows[0], family=W + CENTRES)}))
    z = rows[0]
    active = stage_pair[z['stage']]
    child = next(c for c in sorted(rank) if pair[c] == active)
    fam = z['replica'] * FAMILIES_PER_REPLICA + (2 * active + side[child]) * V + z['port']
    run('caller_active_pair', 'R-e.active_pair', replaced({0: dict(z, owner_replica=z['replica'], child=child, offset=0,
                                                                     family=fam, copy=V * z['replica'] + z['port'])}))
    a, b = call0[0], call0[1]
    host = {k: rows[a][k] for k in ('owner_replica', 'child', 'port', 'family', 'copy', 'offset')}
    run('two_helpers_one_family', 'R-e.family_unique_per_call', replaced({b: dict(rows[b], **host)}))
    # role moved outside its owner's window: swap the hosts of one helper between two calls (R-a/R-e still hold)
    swap = None
    for i, z in enumerate(rows):
        lo, hi = sched['windows'][z['owner_replica'], z['child']]
        for t2 in range(len(order) - 1, -1, -1):
            if lo < sched['callpos'][t2] < hi:
                continue
            j = helper_index[t2, z['helper']]
            y = rows[j]
            s2, r2 = order[t2]
            zz = dict(z, stage=s2, replica=r2, time=t2)
            yy = dict(y, stage=z['stage'], replica=z['replica'], time=z['time'])
            if ctx['widths'][ctx['dispatch'][s2, r2]][z['helper']] != z['width']:
                continue
            if ctx['widths'][ctx['dispatch'][z['stage'], z['replica']]][y['helper']] != y['width']:
                continue
            if family_index.get((t2, z['family']), j) != j or family_index.get((z['time'], y['family']), i) != i:
                continue
            if (zz['owner_replica'] == r2 and pair[zz['child']] == stage_pair[s2]) or \
               (yy['owner_replica'] == z['replica'] and pair[yy['child']] == stage_pair[z['stage']]):
                continue
            swap = {i: zz, j: yy}
            break
        if swap:
            break
    need(swap is not None, 'control', 'no window control could be built')
    run('out_of_window_role', 'R-d.window', replaced(swap))
    bins = {}
    for k, z in enumerate(rows):
        bins.setdefault((z['owner_replica'], z['child'], z['port']), []).append(k)
    pick = None
    for bkey, members in sorted(bins.items()):
        if len(members) >= 2:
            members = sorted(members, key=lambda k: rows[k]['offset'])
            if rows[members[0]]['offset'] + rows[members[1]]['width'] <= rank[bkey[1]]:
                pick = (members[0], members[1])
                break
    need(pick is not None, 'control', 'no overlap control could be built')
    run('overlapping_slices', 'R-b.overlap', replaced({pick[1]: dict(rows[pick[1]], offset=rows[pick[0]]['offset'])}))
    gap = None
    for bkey, members in sorted(bins.items()):
        last = max(members, key=lambda k: rows[k]['offset'])
        if rows[last]['offset'] + rows[last]['width'] + 1 <= rank[bkey[1]]:
            gap = last
            break
    need(gap is not None, 'control', 'no prefix control could be built')
    run('gap_in_prefix', 'R-b.prefix', replaced({gap: dict(rows[gap], offset=rows[gap]['offset'] + 1)}))
    over = next(k for k, z in enumerate(rows) if z['offset'] + z['width'] == rank[z['child']])
    run('slice_beyond_child_capacity', 'R-b.capacity', replaced({over: dict(rows[over], offset=rows[over]['offset'] + 1)}))
    claims = dict(ctx['claims'])
    src, claimed = claims['idle'][0]
    tampered = Counter(claimed)
    tampered[48] -= 1
    tampered[47] += 1
    claims['idle'] = [(src, +tampered)] + claims['idle'][1:]
    run('tampered_idle (one 48 claimed as 47)', 'R-c.idle', rows, dict(ctx, claims=claims))
    claims = dict(ctx['claims'])
    src, claimed = claims['profile'][-1]
    tampered = Counter(claimed)
    tampered[1] += 1
    claims['profile'] = claims['profile'][:-1] + [(src, tampered)]
    run('tampered_global_profile (%s)' % src, 'R-c.profile', rows, dict(ctx, claims=claims))
    plan = dict(ctx['plan'])
    windows = dict(plan['windows'])
    key = next(k for k in sorted(windows) if windows[k][1])
    windows[key] = [windows[key][0], windows[key][1][:-1]]
    plan['windows'] = windows
    run('truncated_plan_window (X1)', 'R-d.plan_windows', rows, dict(ctx, plan=plan))
    # namespace: one more zero buffer than reserved-tableau fields
    expect('zero_buffers_exceed_reserve (NZ = R + 1)', 'R-f.namespace',
           lambda: private_namespace(W, ctx['R'], list(range(ctx['R'] + 1)), 0))
    # local profile: the word report claims one rank-1 child moved to rank 2
    word = parse(b2339, 'words/BORROW-WORD-80base.json.gz')
    lp = dict(word['report']['local_profile'])
    lp['1'] -= 1
    lp['2'] += 1
    word['report'] = dict(word['report'], local_profile=lp)
    mutant = dict(b2339)
    mutant['words/BORROW-WORD-80base.json.gz'] = gzip.compress(json.dumps(word).encode())
    expect('tampered_word_local_profile', 'R-c.local',
           lambda: load_word(mutant, 'words/BORROW-WORD-80base.json.gz', None, '80base-mutant', 80))
    if phases is not None:
        # X2: one pending axis of a child copied into another child of the same family (PR2269 control)
        bad = json.loads(json.dumps(phases))
        a, b = next((a, b) for a in sorted(rank) for b in sorted(rank)
                    if a < b and (pair[a], side[a]) == (pair[b], side[b]))
        kids = bad['recipes'][0]['idle_children']
        kids[b]['orthogonal_axes'][0] = kids[a]['orthogonal_axes'][0]
        expect('cross_child_pending_axis_alias (X2)', 'R-g.pending_axes',
               lambda: pending_axes_and_charts(sched, bad, bases, []))
    return out


# -------------------------------------------------------------------- API ---

def recount(repo=REPO_DEFAULT, force_inputs=False):
    """Main recount only (no controls): used by price80.py."""
    ctx, rows, tpl, words, b2269, meta = case_80(repo, force_inputs)
    sched = derive_schedule(ctx['T'], tpl['template'], ctx['order'])
    rec = run_pipeline(ctx, sched, rows)
    return dict(recount=rec, ctx=ctx, words=words, meta=meta, sched=sched, rows=rows, tpl=tpl, b2269=b2269)


# -------------------------------------------------------------------- main ---

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--words-from-inputs', action='store_true',
                    help='read the PR2339 files from inputs/ even if commit bf1742ae is present')
    ap.add_argument('--skip-positive-control', action='store_true')
    ap.add_argument('--out', action='store_true', help='write ' + RECEIPT_NAME + ' next to this script')
    args = ap.parse_args()
    started = time.time()
    try:
        R = recount(args.repo, args.words_from_inputs)
        ctx, rec, words, sched, rows = R['ctx'], R['recount'], R['words'], R['sched'], R['rows']
        print('windows: %d rebuilt from %d expanded events (%d bridges) = PR2269 new/PLAN.json windows (X1)' % (
            len(sched['windows']), sched['events'], sched['bridges']), flush=True)
        print('R-a..R-e PASS: roles=%d = %d x %d; cross-replica %d; occupied bins %d of %d' % (
            rec['roles'], rec['calls'], rec['helpers_per_call'], rec['cross_replica_roles'], rec['occupied_bins'],
            rec['bins']), flush=True)
        print('R-c recount: idle=%s' % rec['idle'], flush=True)
        print('R-c recount: profile=%s mass=%d deficit=%d' % (rec['profile'], rec['rank_mass'], rec['deficit']), flush=True)
        # ---- R-f: private namespace (rule as PR2322 states it) + its positive control on PR2322's numbers
        b2322, rec2322 = read_pinned(args.repo, HEAD_2322, PKG_2322, PINS_2322, 'PR2322')
        inj = parse(b2322, 'evidence/PRIVATE-NAMESPACE-INJECTION.json')
        claim2322 = parse(b2322, 'CLAIM.json')
        geo2322 = private_namespace(inj['geometry']['live'], claim2322['native_helpers'],
                                    list(range(inj['geometry']['zero_buffers'])), 0)
        need(all(inj['geometry'][k] == geo2322[k] for k in geo2322), 'R-f.namespace',
             'rule does not reproduce PR2322 PRIVATE-NAMESPACE-INJECTION.json geometry')
        need(words['gauge44']['buffers'] == words['extra']['buffers'], 'R-f.zero_buffers',
             'both words use the same buffer registers')
        geo = private_namespace(ctx['W'], ctx['R'], words['gauge44']['buffers'], rec['max_hosted_family'])
        need(geo['physical'] == 66714 and geo['buffer_fields'] == [66312, 66356] and geo['remaining_reserve'] == 356,
             'R-f.namespace', 'expected geometry 66714 = 66304 + 400 + 8 + 2')
        phys = physical_rows(R['b2269'], ctx['W'], rec['calls'],
                             {'ext80_this_fill': geo['physical'],
                              'pr2269_43alias': ctx['W'] + CENTRES + 437 + COEFFICIENT_WORK,
                              'pr2322': geo2322['physical']})
        print('R-f namespace: physical %d = %d + %d + 8 + 2; centres %s, reserved tableau %s, %d zero buffers -> %s, '
              'coefficient %s; remaining reserve %d (PR2322 rule reproduces its own geometry %d)' % (
                  geo['physical'], ctx['W'], ctx['R'], geo['centers'], geo['reserved_tableau'], geo['zero_buffers'],
                  geo['buffer_fields'], geo['coefficient'], geo['remaining_reserve'], geo2322['physical']), flush=True)
        print('R-f stock bits: %s' % {k: v['stock_bits'] for k, v in phys['rows'].items()}, flush=True)
        # ---- R-g: X2 pending-axis disjointness and 73-column charts (template DATA-PHASES)
        b2339, _rec, _mode = read_2339(args.repo, args.words_from_inputs)
        word_ports = [parse(b2339, 'words/BORROW-WORD-80%s.json.gz' % t)['ports'] for t in ('base', 'extra')]
        phases, pports, recph = load_phases(args.repo, R['tpl']['template'], word_ports)
        bases = owner_bases(pports)
        xg = pending_axes_and_charts(sched, phases, bases, rows)
        print('R-g X2: %d (port, child) pending-axis sets disjoint per family; %d distinct 73-column charts '
              '(%d slice keys)' % (xg['pending_axis_checks'], xg['actual_73column_charts'], xg['chart_keys']), flush=True)
        # ---- negative controls
        rejected = controls(ctx, sched, rows, words, b2339, phases, bases)
        print('negative controls rejected: %d (%s)' % (len(rejected), ', '.join(
            c['name'].split(' ')[0] + '->' + c['rejected_by'] for c in rejected)), flush=True)
        # ---- positive control: PR2269's own fill
        presult = None
        if not args.skip_positive_control:
            pctx, prows, pwords = case_2269(R['b2269'], R['tpl'])
            presult = run_pipeline(pctx, sched, prows)
            pxg = pending_axes_and_charts(sched, phases, bases, prows)
            need(pxg['actual_73column_charts'] == R['tpl']['spec']['expected']['actual_73column_sigmas'], 'R-g.chart',
                 'positive control: PR2269 chart count != its SPEC actual_73column_sigmas')
            presult['pending_axes_and_charts'] = pxg
            print('positive control PR2269 fill: roles=%d idle=%s (PLAN per_call_widths checked); charts %d = SPEC '
                  'actual_73column_sigmas' % (presult['roles'], presult['idle'], pxg['actual_73column_charts']),
                  flush=True)
    except CheckFailure as exc:
        print('%s %s' % (FAIL_LINE, exc))
        return 1
    except Exception as exc:   # malformed input: report, never pass
        print('%s unexpected %s: %s' % (FAIL_LINE, type(exc).__name__, exc))
        return 1
    meta = R['meta']
    meta['inputs'].update(rec2322)
    meta['inputs'].update(recph)
    receipt = dict(
        status=PASS_LINE,
        object=dict(owners=OWNERS_80[0], sha256=OWNERS_80[1], template='PR2269 head %s %s' % (HEAD_2269, PKG_2269),
                    words='PR2339 commit %s %s/words' % (HEAD_2339, PKG_2339)),
        inputs=meta['inputs'], pr2339_files_read_from=meta['pr2339_source'],
        claim_files_sha256=meta['claim_files_sha256'],
        windows=dict(rebuilt=len(sched['windows']), equal_to_pr2269_plan=True, expanded_events=sched['events'],
                     bridges=sched['bridges'], child_ranks={str(c): sched['rank'][c] for c in sorted(sched['rank'])},
                     swept_children_without_capacity=sched['rankless_children']),
        words={pid: dict(removed_registers=w['removed'], width_inventory=plain(w['inventory']),
                         width_per_call=w['width_sum'], local_profile_recount=plain(w['local']),
                         local_mass=w['local_mass'], zero_buffers=len(w['buffers']),
                         buffer_registers=w['buffers'], initial_corrections=w['corrections'], warps=w['warps'])
               for pid, w in words.items()},
        recount=rec,
        claims_compared=dict(idle=[s for s, _ in ctx['claims']['idle']], profile=[s for s, _ in ctx['claims']['profile']],
                             scalars=[(k, s) for k, s, _ in ctx['claims']['scalars']], all_equal=True),
        private_namespace=dict(
            rule='As PR2322 states it (README "complete physical stock"; evidence/PRIVATE-NAMESPACE-INJECTION.json): '
                 'physical = W + 8 centres + R reserved tableau + 2 coefficient work; centres [W,W+8), reserved '
                 'tableau [W+8,W+8+R), coefficient [P-2,P); the NZ zero buffers (r + 704 for each hyperplane-ended '
                 'live helper r) are injected in increasing order into [W+8,W+8+NZ) and must fit (NZ <= R); all '
                 'hosted helper families are live (< W). Calls are serial and every buffer is allocated and freed '
                 'inside one call, so the same NZ fields serve every call.',
            this_fill=geo, pr2322_reproduced=geo2322, stock=phys),
        pending_axes_and_charts=dict(
            rule='R-g: PR2269 independent_core.py check_pending_axes (X2) and the per-role 73-column chart binding, on '
                 'DATA-PHASES.json read at the PR2269 commit (sha256 = GLOBAL-TEMPLATE exact_data_phase_recipe_sha256)',
            this_fill=xg),
        controls_rejected=rejected,
        positive_control=None if presult is None else dict(
            object='PR2269 OWNERS.json.gz (437 helpers, 43-alias words) on the same template; PLAN per_call_widths '
                   'compared; claims of new/SPEC.json, CONSTRUCTION.json and new/PROFILE.json reproduced', **presult),
        adaptation='For the 400-helper fill the PR2269 PLAN per_call_widths (437-helper lists) are not compared; '
                    'per-call widths come from the 80-alias words (positive control checks the PLAN widths for 437).',
        not_checked=['warp algebra and exact free-operator replay of the 80-alias words (PR2339 check_ext.py)',
                     'native lowering in both orientations of the 64 anticipatory initial corrections (the 43-alias '
                     'words have none) and the 37 new warps (80 lenders: 74 hosted helpers, 6 X fields)',
                     'X-field lender ownership and frame-zero read lifetimes of hosted correction sources in the '
                     'whole-call map; physical lowering of the 44 zero buffers (R-f only follows PR2322 statement)',
                     'native local prefix bits (needed for prefix < payload), controller emission, physical Clifford '
                     'phases, invoice; PLAN/SPEC refreeze for 400 helpers; assembly and outer ledger'],
        scope='Finite recount of OWNERS-80.json.gz under the stated hosting rules on PR2269\'s unchanged template; '
              'not a kappa claim.',
        credits='PR2339 (this author); PR2269 Jeremy Kothe; PR2322 Vlado Vojdanovski; PR2312/PR2302 jeremykothe2; '
                'PR2226 Cinna Davis; PR1319/PR1297 T74 lineage (Rohan Arun et al.); PR858 / T16 owner-audit rules. '
                'Adapted from our iteration-3 fill_check.py/words_check.py (commit 4a2f20ea). Prepared with '
                'substantial AI assistance (Claude Code, Anthropic); Apache-2.0.',
        python=sys.version.split()[0])
    if args.out:
        with open(os.path.join(HERE, RECEIPT_NAME), 'w', encoding='utf-8') as handle:
            handle.write(json.dumps(receipt, indent=1, sort_keys=True) + '\n')
    print('runtime_s=%.1f' % (time.time() - started))
    print('%s roles=%d idle=%s physical=%d buffers=%d/%d charts=%d controls=%d positive_control=%s' % (
        PASS_LINE, rec['roles'], json.dumps(rec['idle'], separators=(',', ':')), geo['physical'], geo['zero_buffers'],
        ctx['R'], xg['actual_73column_charts'], len(rejected), 'PASS' if presult is not None else 'skipped'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
