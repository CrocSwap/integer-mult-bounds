#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent recount of the whole-helper hosting fill of PR #2269.

Object: research/gmx-t74-borrow43/OWNERS.json.gz of CrocSwap/integer-mult-bounds
PR #2269 (jeremykothe2) at head b479fc5567bc09ab9185bffe89b62594f36d74e5:
291,042 literal roles that host the 437 live helpers of the two borrowed T74
local words ('base' = provider gauge44, 249 calls; 'extra', 417 calls) in idle
children of a 74-replica, nine-stage controller.

This checker is written from the written specification only.  It imports and
executes no code from PR #2269, PR #2226, PR #2260 or any vendored directory.
Every input is a git blob of the pinned head, read with `git cat-file`, and is
pinned by git blob id *and* sha256 (both re-derived here at run time).  All
accepted facts are integer or GF(2) bit-vector facts (exact); JSON reals are
parsed as Fractions.  The script refuses `python -O`.

Hosting rules implemented (sources: research/complex-double-replica-owners/
PROOF.md on main, "Actual windows and whole-helper ownership" and "Namespace";
research/t16-owner-audit-seed67/README.md on main, rules R1-R7/X1; the T74
package's PLAN.json windows/per_call_widths, GLOBAL-TEMPLATE.json.gz schedule,
CONSTRUCTION.json, SPEC.json and README):

  R-a  one role per (call, live helper): 666 calls x 437 helpers; helper index
       i is the i-th live helper register (registers 224..703 minus the 43
       `removed` ones, increasing order); role width = dim(final frame) -
       dim(start frame) of that helper in the borrowed word (GF(2) ranks).
  R-e  physical family = owner*896 + (2*pair(child)+side(child))*112 + port,
       copy = 112*owner + port; family inside the data namespace [0, 896*T);
       not the caller's active pair; at most one helper per family per call.
  R-d  the call lies strictly inside the owner's actual window: from the last
       local sweep / bridge touch of the child's pair on the owner replica to
       that child's idle sweep, rebuilt from the template's 30 source events
       expanded in the shipped ORDER (bridge-aware).  X1: the rebuilt windows
       equal PLAN.json windows exactly.
  R-b  slices [offset, offset+width) lie in [0, rank(child)), are disjoint in
       each bin (owner replica, child, port) and form an occupied prefix.
  R-c  idle remainders rank - occupied per bin (nonzero ones counted) and the
       global profile sum_calls P_provider + idle equal the shipped claims;
       rank mass and deficit identities.
  R-f  quantification of the physical-stock charge versus the 76 private zero
       buffers of each borrowed word (informational, exact integers).

Positive control: the same checker on the pre-borrow parent fill shipped in
the package (inputs/OWNERS.json.gz: PR1297 T37 fill, 333 calls x 480 helpers).
Negative controls: each mutation must be rejected by the check it targets.

Credits: PR #2269 (jeremykothe2; the borrowed T74 fill and package);
PR #2226 (Cinna Davis / 1337isnot1337, anticipatory dirty borrowing);
PR #2260 (Dugongue, concurrent borrowing package); the T74 lineage PR1319 and
PR1297 (Rohan Arun), PR1625 (mdumitrean, pivot-566 kernel) and PR1193 (Jeremy
Diviney, T37 flow fill); the hosting rules of Hao Yan's PR858 /
complex-double-replica-owners PROOF.md; the icekylinx / Zhihao Chen
independent-checker lineage and the T16 owner audit (Josie Elliston) whose
rule list R1-R7/X1 this follows.  No code from any of them is reused.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage:  python3 -I -B fill_check.py [--repo PATH | --blob-dir DIR] [--out]
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
    sys.stderr.write('FAIL_FILL_CHECK refusing to run under python -O\n')
    sys.exit(2)

REPO_DEFAULT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repository root
HEAD = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'
PKG = 'research/gmx-t74-borrow43'
RECEIPT_NAME = 'fill_check.receipt.json'

# relative path in PKG -> (git blob id, sha256 of the blob bytes)
PINS = {
    'OWNERS.json.gz': ('fc874cb553af5b984e34c1d8696d2213d7458f8f', '5a8c9a18c21f635563c9a6b6a433bcb1e804175ef23d677459033344aa2bd4e6'),
    'PROFILE.json': ('48249b94604daccf0552c0c3b2489716344f7ff2', '7012a58b4078d41e3b4412204d7dfdf9eb401bfe7da5429002150bdfc3558865'),
    'new/PROFILE.json': ('3e103605dd46c8754028056eb9dde9a73b9bfdca', '50fcc0960a47f6d35064d3b55ea6dcb4cebbd305aec215c8034f626718595538'),
    'SPEC.json': ('5158049eeff8240d59528441d3f1fcfd8f420783', 'da49a85190eac2b553fe982ed295b15fcde6d2dd449d976b503de25c277f2029'),
    'new/SPEC.json': ('2431d1cebbb2e155356d2da160d60808498bc33d', 'bd091ed9e7f4939d06abb467d0d2c56ce0f34ba800d74132669f7b667e125d2d'),
    'PLAN.json': ('ea617c2fad0a9581723e9c05bb111631a5af7f17', '334709f65761928e02f83bf1f2e7f537d783381bab6689669bffe111b8f60bea'),
    'new/PLAN.json': ('7cacd857edd0f29be5bd2ca9590a17fed4da17ba', 'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2'),
    'CONSTRUCTION.json': ('034ec6c6309bd1279661918f2a8706268f9a1200', '37b8605607b2877d82b8403d509f5cd224240064c93fa67ce89a8894acc6b460'),
    'GLOBAL-TEMPLATE.json.gz': ('5327fc2f4e8ea82ed356c94ff040d23fc73c731f', '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db'),
    'ORDER.json': ('7409c4df1092241729739596c7648bda504e6aad', '519d1d5dbb997a219fcfcad34c0b03e7838bef24199784d7e964fa10090f66e1'),
    'DISPATCH.json': ('20807cc27c82db1f8f9cd47c79713e066d6ad816', '6aad7f628f4c9b510a95c5b34357736303069ecf92a551659900b1ba540bc7e0'),
    'new/BORROW-PROVIDERS.json': ('42563d218a5c7321f686c1cf9b98e75883d85abc', '8324fcf5fd652af9793c1acbc5f5099ee0d2f1eefa0adfbb8335f3d31d891da2'),
    'new/borrow/words/BORROW-WORD-43base.json.gz': ('448dd795adba29392a90b34aa3f1b1b796c7e0bd', '9492a5537fb87d9ca98dffcd0230f7625b3789744fa94e2f18acf23d91d998b5'),
    'new/borrow/words/BORROW-WORD-43extra.json.gz': ('2b51ba96256283bbc5578f99b694c50edd8a0e35', '87d51f5298101d5947f45c43ee02f0ec45d6acbddabb808d0d02db1eaf063734'),
    'new/gauge44-word-566.json.gz': ('76c01583a0286cddb0f71e0cb13077e4317104f6', 'eeb6a236ed0ea8873b8800947d0cd19c36a6fcfdf857fc42913cb45cd984f219'),
    'new/extra-word-566.json.gz': ('e86142b352466f54a3da38c96a6e1484145c3b5c', 'cd417b904408c221d9840d08faff8af040cc4207f9804284f2f5375d21298a62'),
    'new/borrow/receipts/AUDIT-43base.json': ('65728eff3ef61c275c873b58f0f8cebc095ef6f9', '9af87b149b8efa58e2454541dd1c5aef86d893c71ec488ae69fb8680c2f7936e'),
    'new/borrow/receipts/AUDIT-43extra.json': ('f9c2401401612b3b0b6e652e142e65bceadc1170', '849fbe9b9267180ba914237d751b118b4539731249c4482e6264d4772932fd2d'),
    'evidence/INDEPENDENT.json': ('16bb558f2472df730076a8163454c6f70b9e9fe3', '78cd00f832ed3c0a4b0e0d202095f7beb6111eaeb4457849d5bb920e983098a0'),
    'PARENT-LIFT-RECEIPT.json': ('0c6ccc1f8957d0ca97877e81ab83fd06eb10dcad', '925a2c2bae44d69c0ac9d930abe63cf73bf22765b49e6a1eb9d7a0f5f0f4ea84'),
    'inputs/OWNERS.json.gz': ('34fa5d69aaa2574af60f1e8f7d43640b03698bca', '3a56f578b2db5647cf6cb811bc6263c7a802ae3e31e9e672596d43185e4e5c9f'),
    'inputs/PLAN.json': ('5af9dd20821ae5b79778d85cd7183873c5999732', '163431bf8d3bc0d9b894994b1a3cfa7947367b2243b3c0b3a97d740195a1cb08'),
    'inputs/SPEC.json': ('c15990ace61b32f7233c82580d720e3097a900c3', '2daedf579c8abf30ceed79fe739bdd7659fce4c514de3894a028933143265d98'),
    'inputs/GLOBAL-TEMPLATE.json.gz': ('114808c32b1799da53524bdc25cea67efb60009e', '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'),
    'inputs/DISPATCH.json': ('613e01490d24a39e551ba75915320617003c1c81', 'b7b971df9dce435556145df307e2bb5138d87e5aa933f1fe61fcc5b5163301c4'),
    'vendor/pr1297/gauge44-word.json.gz': ('eacf8c773cb50637f93a762342b3b5f0853fe29a', 'e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e'),
    'vendor/pr1297/extra-word.json.gz': ('4d464f55a2955e5c832b5ce789d5d0e0a39fb4e1', '7b0e9fbda32749aabc7e156d9fe09bceb0624a178628fe69e5dfea783462f905'),
    'vendor/pr1297/PROFILE.json': ('cb96b9560ef7f08512601da484ca3b4550d5c602', 'd9bbe0d73ba005749615915a2d884819a6b141e3402d9e7f87f4592a2d27af99'),
}

# Geometry of the nine-stage, four-pair, 112-port controller (template/PLAN):
V = 112            # data ports per (pair, side)
H = 9              # local frame dimension
M = 73             # global dimension m
STAGES = 9
PAIRS = 4
FAMILIES_PER_REPLICA = 2 * PAIRS * V   # 896
CENTRES, COEFFICIENT_WORK = 8, 2
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


def load_blobs(repo, blob_dir=None):
    """Read every pinned input.  Default: git blobs of HEAD in `repo`.  With blob_dir: the files
    DIR/<package-relative path> of an exported copy (e.g. `git archive HEAD PKG`), which must match
    the same git blob ids and sha256 pins (the path-to-blob resolution at HEAD is then not re-done)."""
    if blob_dir is None:
        need(git(repo, 'cat-file', '-t', HEAD).strip() == b'commit', 'input.pin', 'head commit missing')
    blobs, record = {}, {}
    for rel in sorted(PINS):
        oid, sha = PINS[rel]
        path = PKG + '/' + rel
        if blob_dir is None:
            got = git(repo, 'rev-parse', '--verify', HEAD + ':' + path).decode().strip()
            need(got == oid, 'input.pin', path + ' resolves to ' + got + ', pinned ' + oid)
            data = git(repo, 'cat-file', 'blob', oid)
        else:
            src = os.path.join(blob_dir, rel)
            need(os.path.isfile(src), 'input.pin', 'exported blob missing: ' + src)
            with open(src, 'rb') as handle:
                data = handle.read()
        header = ('blob %d' % len(data)).encode() + b'\0'
        need(hashlib.sha1(header + data).hexdigest() == oid, 'input.pin', 'git blob id of ' + path)
        need(hashlib.sha256(data).hexdigest() == sha, 'input.pin', 'sha256 of ' + path)
        blobs[rel] = data
        record[path] = dict(git_blob=oid, sha256=sha, bytes=len(data))
    return blobs, record


def parse(blobs, rel):
    data = blobs[rel]
    if rel.endswith('.gz'):
        data = gzip.decompress(data)
    return json.loads(data.decode('utf-8'), parse_float=Fraction)


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


# ------------------------------------------------------------ word widths ---

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


def word_helpers(word, label):
    """Live helper registers, their residual widths and the hyperplane-ended set."""
    check = 'R-a.word'
    report = word['report']
    need((report.get('v'), report.get('h'), report.get('R')) == (V, H, 480), check, label + ' dimensions')
    need(len(word['ports']) == V, check, label + ' port count')
    first, end = 2 * V, 2 * V + 480
    removed = list(word.get('removed', []))
    need(all(type(r) is int and first <= r < end for r in removed) and len(set(removed)) == len(removed),
         check, label + ' removed registers')
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


# --------------------------------------------------------------- context ---

def build_context(name, T, helpers, order, dispatch, widths, local_profiles, template, plan, claims):
    """Static data of one fill; nothing here reads the OWNERS rows."""
    return dict(name=name, T=T, R=helpers, W=FAMILIES_PER_REPLICA * T, order=order, dispatch=dispatch,
                widths=widths, local_profiles=local_profiles, template=template, plan=plan, claims=claims)


def derive_schedule(ctx):
    """Expand the 30 per-replica source events in call order; rebuild windows."""
    T, template = ctx['T'], ctx['template']
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
    for t, (s, r) in enumerate(ctx['order']):
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
                    # A swept child with no idle_children record has no capacity (rank 0) and hosts nothing.
                    rankless.add(child)
                    continue
                need((r, child) not in windows, 'R-d.schedule', 'idle sweep child')
                need(child_pair.setdefault(child, e['pair']) == e['pair'] and
                     child_side.setdefault(child, side) == side, 'R-d.schedule', 'child pair/side')
                windows[r, child] = (last.get((r, e['pair']), -1), pos)
        else:   # terminal events touch every pair; they follow every idle sweep of the replica
            for p in range(PAIRS):
                last[r, p] = pos
    need(len(windows) == T * len(rank) and set(callpos) == set(range(len(ctx['order']))), 'R-d.schedule',
         'window inventory')
    positions = [callpos[t] for t in range(len(ctx['order']))]
    need(all(a < b for a, b in zip(positions, positions[1:])), 'R-d.schedule', 'call positions increase')
    times = {}
    for key, (lo, hi) in windows.items():
        a = bisect.bisect_right(positions, lo)
        b = bisect.bisect_left(positions, hi)
        times[key] = list(range(a, b))
    return dict(stage_pair=stage_pair, rank=rank, windows=windows, callpos=positions, child_pair=child_pair,
                child_side=child_side, window_times=times, bridges=bridges, events=len(events),
                rankless_children=sorted(rankless))


def check_static(ctx, sched):
    """Order, dispatch, PLAN widths and X1 (PLAN windows == rebuilt windows)."""
    T, order, plan = ctx['T'], ctx['order'], ctx['plan']
    need(len(order) == STAGES * T and set(order) == {(s, r) for s in range(STAGES) for r in range(T)},
         'R-0.order', 'call inventory')
    need(plan['order'] == [list(x) for x in order], 'R-0.order', 'PLAN order')
    need(set(ctx['dispatch']) == set(order), 'R-0.dispatch', 'dispatch inventory')
    need(len(plan['provider_calls']) == len(order) and len(plan['per_call_widths']) == len(order),
         'R-0.dispatch', 'PLAN call records')
    for t, (s, r) in enumerate(order):
        pc = plan['provider_calls'][t]
        need((pc['stage'], pc['replica']) == (s, r) and pc.get('time', t) == t and
             pc['provider'] == ctx['dispatch'][s, r], 'R-0.dispatch', 'PLAN provider call %d' % t)
        pw = plan['per_call_widths'][t]
        need((pw['stage'], pw['replica']) == (s, r) and pw.get('time', t) == t, 'R-0.widths', 'PLAN width call %d' % t)
        need(pw['widths'] == ctx['widths'][ctx['dispatch'][s, r]], 'R-0.widths', 'PLAN per-call widths at %d' % t)
    pw = plan['windows']
    need(len(pw) == len(sched['windows']), 'R-d.plan_windows', 'window count')
    for (r, c), times in sched['window_times'].items():
        key = '%d,%d' % (r, c)
        need(key in pw and pw[key] == [sched['rank'][c], times], 'R-d.plan_windows', 'PLAN window ' + key)


def check_roles(ctx, sched, rows):
    """Phases R-a, R-e, R-d, R-b, R-c on the literal roles; returns recounts."""
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
        need(z['width'] == ctx['widths'][provider[t]][z['helper']], 'R-a.width',
             'width of helper %d in call %d' % (z['helper'], t))
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
        need(lo < callpos[z['time']] < hi, 'R-d.window', 'role outside window of owner %d child %d' %
             (z['owner_replica'], z['child']))
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
    # ---- R-c: idle remainders, global profile, mass identities
    idle = Counter()
    for (owner, child) in windows:
        for port in range(V):
            left = rank[child] - bin(used.get((owner, child, port), 0)).count('1')
            if left:
                idle[left] += 1
    claims = ctx['claims']
    for source, claimed in claims['idle']:
        need(idle == claimed, 'R-c.idle', 'idle remainders differ from ' + source)
    local = Counter()
    for p in provider:
        local.update(ctx['local_profiles'][p])
    profile = local + idle
    for source, claimed in claims['profile']:
        need(profile == claimed, 'R-c.profile', 'global profile differs from ' + source)
    total = mass(profile)
    need(total == claims['rank_mass'], 'R-c.mass', 'rank mass')
    need(M * W - total == claims['deficit'] == 320 * T, 'R-c.mass', 'deficit identity m*W - mass = 320*T')
    capacity = T * V * sum(rank.values())
    hosted_width = sum(z['width'] for z in rows)
    need(mass(idle) == capacity - hosted_width, 'R-c.mass', 'idle mass = capacity - hosted width')
    need(total == mass(local) + capacity - hosted_width, 'R-c.mass', 'mass decomposition')
    need(M * M > 2 * max(profile) ** 2, 'R-c.mass', 'halving guard m^2 > 2*maxchild^2')
    need(len(rows) == claims['hosted'], 'R-c.counts', 'hosted residual count')
    need(cross == claims['cross_replica'], 'R-c.counts', 'cross-replica role count')
    need(sum(idle.values()) == claims['idle_remainders'], 'R-c.counts', 'idle remainder count')
    family_children = {}
    for z in rows:
        family_children.setdefault(z['family'], set()).add(z['child'])
    return dict(roles=len(rows), calls=len(order), helpers_per_call=R, bins=T * V * len(rank),
                occupied_bins=len(used), cross_replica_roles=cross, idle=plain(idle),
                hosted_families=len(family_children),
                hosted_families_with_slices_of_two_or_more_children=sum(1 for c in family_children.values() if len(c) > 1),
                idle_remainders=sum(idle.values()), profile=plain(profile), rank_mass=total,
                deficit=M * W - total, live=W, idle_capacity=capacity, hosted_width=hosted_width,
                idle_mass=mass(idle), local_mass=mass(local), max_child=max(profile))


def run_pipeline(ctx, sched, rows):
    check_static(ctx, sched)
    return check_roles(ctx, sched, rows)


# ------------------------------------------------------------ case setup ---

def dispatch_map(records, check):
    out = {}
    for s, r, p in records:
        need((s, r) not in out, check, 'duplicate dispatch')
        out[s, r] = p
    return out


def borrow_case(blobs):
    owners = parse(blobs, 'OWNERS.json.gz')
    plan = parse(blobs, 'new/PLAN.json')
    plan_top = parse(blobs, 'PLAN.json')
    spec = parse(blobs, 'new/SPEC.json')
    construction = parse(blobs, 'CONSTRUCTION.json')
    template = parse(blobs, 'GLOBAL-TEMPLATE.json.gz')
    order = [tuple(x) for x in parse(blobs, 'ORDER.json')]
    dispatch = dispatch_map(parse(blobs, 'DISPATCH.json'), 'R-0.dispatch')
    providers = parse(blobs, 'new/BORROW-PROVIDERS.json')
    T = plan['T']
    need(T == 74 and (plan['K'], plan['L'], plan['M']) == (PAIRS, STAGES, M), 'R-0.plan', 'PLAN geometry')
    need(order == [tuple(x) for x in plan['order']] == [tuple(x) for x in spec['call_order']], 'R-0.order',
         'ORDER.json = PLAN order = SPEC call_order')
    need(dispatch == dispatch_map(spec['dispatch'], 'R-0.dispatch'), 'R-0.dispatch', 'DISPATCH.json = SPEC dispatch')
    # The top-level PLAN.json carries the same hosting data as new/PLAN.json.
    for key in ('order', 'windows', 'per_call_widths', 'profile', 'T', 'live', 'deficit', 'assignment_sha256',
                'assignment_content_sha256'):
        need(plan_top[key] == plan[key], 'R-0.plan', 'PLAN.json and new/PLAN.json differ in ' + key)
    for pid in plan['provider_registry']:
        for key in ('widths', 'actual_paid_profile'):
            need(plan_top['provider_registry'][pid][key] == plan['provider_registry'][pid][key], 'R-0.plan',
                 'PLAN.json registry ' + key)
    owners_sha = hashlib.sha256(blobs['OWNERS.json.gz']).hexdigest()
    need(plan['assignment_sha256'] == owners_sha == spec['data']['owners_sha256'], 'R-0.pins', 'owners pin')
    need(spec['data']['plan_sha256'] == hashlib.sha256(blobs['new/PLAN.json']).hexdigest(), 'R-0.pins', 'plan pin')
    content = hashlib.sha256(json.dumps(owners, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    need(plan['assignment_content_sha256'] == content, 'R-0.pins', 'owners content identity')
    words = {'gauge44': 'new/borrow/words/BORROW-WORD-43base.json.gz',
             'extra': 'new/borrow/words/BORROW-WORD-43extra.json.gz'}
    pre_words = {'gauge44': 'new/gauge44-word-566.json.gz', 'extra': 'new/extra-word-566.json.gz'}
    audits = {'gauge44': 'new/borrow/receipts/AUDIT-43base.json', 'extra': 'new/borrow/receipts/AUDIT-43extra.json'}
    widths, profiles, helpers_info = {}, {}, {}
    for pid in ('gauge44', 'extra'):
        word = parse(blobs, words[pid])
        pre = parse(blobs, pre_words[pid])
        audit = parse(blobs, audits[pid])
        need(word['base'] == hashlib.sha256(blobs[pre_words[pid]]).hexdigest()[:8], 'R-a.word',
             pid + ' borrow word base binding')
        info = word_helpers(word, pid)
        pre_info = word_helpers(pre, pid + '-pre')
        need(len(pre_info['live']) == 480 and not pre_info['removed'], 'R-a.word', pid + ' pre-borrow helper count')
        need(len(info['removed']) == 43 and len(info['live']) == 437, 'R-a.word', pid + ' 43 removed helpers')
        inventory = Counter(info['widths'])
        claimed_widths = [providers[pid]['widths'], plan['provider_registry'][pid]['widths']]
        need(all(w == info['widths'] for w in claimed_widths), 'R-a.word', pid + ' provider widths')
        for source, inv in (('word report', word['report']['width_inventory']),
                            ('SPEC inventory', spec['providers'][pid]['inventory']),
                            ('AUDIT receipt', audit['width_inventory'])):
            need(as_profile(inv, 'R-a.word', source) == inventory, 'R-a.word', pid + ' inventory vs ' + source)
        local = as_profile(word['report']['local_profile'], 'R-c.local', pid)
        for source, prof in (('BORROW-PROVIDERS', providers[pid]['actual_paid_profile']),
                             ('PLAN registry', plan['provider_registry'][pid]['actual_paid_profile']),
                             ('SPEC expected_profile', spec['providers'][pid]['expected_profile']),
                             ('AUDIT receipt', audit['local_profile'])):
            need(as_profile(prof, 'R-c.local', source) == local, 'R-c.local', pid + ' local profile vs ' + source)
        need(audit['zero_buffers'] == audit['restored_cold'] == len(info['hyperplane_ended']), 'R-f.zero_buffers',
             pid + ' zero buffers = hyperplane-ended live helpers')
        pre_width = dict(zip(pre_info['live'], pre_info['widths']))
        new_width = dict(zip(info['live'], info['widths']))
        helpers_info[pid] = dict(
            removed_registers=info['removed'], removed_helper_indices_of_480=[r - 2 * V for r in info['removed']],
            removed_width_histogram_pre=plain(Counter(pre_width[r] for r in info['removed'])),
            live_width_changes=[[r, pre_width[r], new_width[r]] for r in info['live'] if pre_width[r] != new_width[r]],
            width_inventory_pre=plain(Counter(pre_info['widths'])), width_inventory=plain(inventory),
            width_per_call_pre=sum(pre_info['widths']), width_per_call=sum(info['widths']),
            local_profile=plain(local), local_mass=mass(local),
            local_profile_pre=plain(as_profile(pre['report']['local_profile'], 'R-c.local', 'pre')),
            local_mass_pre=mass(as_profile(pre['report']['local_profile'], 'R-c.local', 'pre')),
            hyperplane_ended_live=len(info['hyperplane_ended']), hyperplane_ended_pre=len(pre_info['hyperplane_ended']))
        widths[pid] = info['widths']
        profiles[pid] = local
    need(helpers_info['gauge44']['removed_registers'] == helpers_info['extra']['removed_registers'], 'R-a.word',
         'both words remove the same registers')
    for pid in helpers_info:
        helpers_info[pid]['ordered_widths_identical_across_providers'] = widths['gauge44'] == widths['extra']
    counts = Counter(dispatch.values())
    need(counts == as_profile_str(construction['dispatch']) == as_profile_str(spec['expected']['provider_counts']),
         'R-0.dispatch', 'provider call counts')
    need(construction['helpers_per_call'] == 437 and construction['roles'] == len(owners), 'R-0.construction',
         'CONSTRUCTION helper/role counts')
    exp = spec['expected']
    idle_claims = [('CONSTRUCTION.json idle', as_profile(construction['idle'], 'R-c.idle', 'construction')),
                   ('new/SPEC.json idle_remainder_profile', as_profile(exp['idle_remainder_profile'], 'R-c.idle', 'spec'))]
    profile_claims = [(src, as_profile(parse(blobs, src), 'R-c.profile', src)) for src in ('PROFILE.json', 'new/PROFILE.json')]
    profile_claims.append(('new/PLAN.json profile', as_profile(plan['profile'], 'R-c.profile', 'plan')))
    profile_claims.append(('new/SPEC.json global_profile', as_profile(exp['global_profile'], 'R-c.profile', 'spec')))
    claims = dict(idle=idle_claims, profile=profile_claims, rank_mass=exp['rank_mass'], deficit=plan['deficit'],
                  hosted=exp['hosted_residuals'], cross_replica=exp['cross_replica_helper_roles'],
                  idle_remainders=exp['idle_remainders'])
    need(exp['live'] == plan['live'] == FAMILIES_PER_REPLICA * T, 'R-0.plan', 'live data families')
    ctx = build_context('borrow43-T74', T, 437, order, dispatch, widths, profiles, template, plan, claims)
    return ctx, owners, helpers_info, dict(spec=spec, template=template, construction=construction)


def as_profile_str(mapping):
    return Counter({str(k): v for k, v in mapping.items()})


def parent_case(blobs):
    owners = parse(blobs, 'inputs/OWNERS.json.gz')
    plan = parse(blobs, 'inputs/PLAN.json')
    spec = parse(blobs, 'inputs/SPEC.json')
    template = parse(blobs, 'inputs/GLOBAL-TEMPLATE.json.gz')
    dispatch = dispatch_map(parse(blobs, 'inputs/DISPATCH.json'), 'R-0.dispatch')
    T = plan['T']
    need(T == 37, 'R-0.plan', 'parent replicas')
    order = [tuple(x) for x in plan['order']]
    need(order == [tuple(x) for x in spec['call_order']], 'R-0.order', 'parent PLAN order = SPEC call_order')
    need(dispatch == dispatch_map(spec['dispatch'], 'R-0.dispatch'), 'R-0.dispatch', 'parent dispatch')
    need(plan['assignment_sha256'] == hashlib.sha256(blobs['inputs/OWNERS.json.gz']).hexdigest()
         == spec['data']['owners_sha256'], 'R-0.pins', 'parent owners pin')
    widths, profiles = {}, {}
    for pid, rel in (('gauge44', 'vendor/pr1297/gauge44-word.json.gz'), ('extra', 'vendor/pr1297/extra-word.json.gz')):
        word = parse(blobs, rel)
        info = word_helpers(word, 'parent-' + pid)
        need(len(info['live']) == 480 and info['widths'] == plan['provider_registry'][pid]['widths'], 'R-a.word',
             'parent widths ' + pid)
        need(Counter(info['widths']) == as_profile(spec['providers'][pid]['inventory'], 'R-a.word', 'parent'),
             'R-a.word', 'parent inventory ' + pid)
        local = as_profile(word['report']['local_profile'], 'R-c.local', 'parent')
        need(local == as_profile(spec['providers'][pid]['expected_profile'], 'R-c.local', 'parent')
             == as_profile(plan['provider_registry'][pid]['actual_paid_profile'], 'R-c.local', 'parent'),
             'R-c.local', 'parent local profile ' + pid)
        widths[pid], profiles[pid] = info['widths'], local
    exp = spec['expected']
    claims = dict(idle=[('inputs/SPEC.json idle_remainder_profile', as_profile(exp['idle_remainder_profile'], 'R-c.idle', 'p'))],
                  profile=[('inputs/PLAN.json profile', as_profile(plan['profile'], 'R-c.profile', 'p')),
                           ('inputs/SPEC.json global_profile', as_profile(exp['global_profile'], 'R-c.profile', 'p')),
                           ('vendor/pr1297/PROFILE.json', as_profile(parse(blobs, 'vendor/pr1297/PROFILE.json'), 'R-c.profile', 'p'))],
                  rank_mass=exp['rank_mass'], deficit=plan['deficit'], hosted=exp['hosted_residuals'],
                  cross_replica=exp['cross_replica_helper_roles'], idle_remainders=exp['idle_remainders'])
    ctx = build_context('parent-PR1297-T37', T, 480, order, dispatch, widths, profiles, template, plan, claims)
    return ctx, owners


# ------------------------------------------------------- R-f and staleness ---

def stock_group():
    """The retained 73-dimensional group factor 2^(36*36) * prod_{i=1}^{36} (2^(2i) - 1)."""
    g = 2 ** (36 * 36)
    for i in range(1, 37):
        g *= 2 ** (2 * i) - 1
    return g


def physical_analysis(blobs, ctx, helpers_info, extra):
    spec_new, template = extra['spec'], extra['template']
    spec_old = parse(blobs, 'SPEC.json')
    independent = parse(blobs, 'evidence/INDEPENDENT.json')
    lift = parse(blobs, 'PARENT-LIFT-RECEIPT.json')
    W, calls = ctx['W'], len(ctx['order'])
    g = stock_group()
    payload = 1 << (192 + (M + 1) // 2 + 2 * calls + 4).bit_length()

    def charge(physical):
        bits = (g * physical).bit_length()
        return dict(physical=physical, stock_bits=bits, row_coefficient=2 * bits + ROW_CONSTANTS + 2 * payload)

    # Formula cross-check against the shipped (pre-borrow) independent receipt.
    ref = charge(independent['physical'])
    need((ref['stock_bits'], ref['row_coefficient'], independent['charged_prefix_bits']) ==
         (independent['physical_stock_bits'], independent['physical_row_coefficient'], payload),
         'R-f.formula', 'stock/row formula does not reproduce evidence/INDEPENDENT.json')
    geo_old, geo_new = spec_old['geometry'], spec_new['geometry']
    need(geo_old == geo_new, 'R-f.parent', 'parent geometry changed between SPEC.json and new/SPEC.json')
    parent_physical = geo_new['parent_physical']
    need(parent_physical == template['physical'] == lift['geometry']['parent_physical'] and
         geo_new['parent_live'] == template['live'] and
         parent_physical == template['live'] + geo_new['parent_helpers'] + CENTRES + COEFFICIENT_WORK,
         'R-f.parent', 'parent physical = parent live + 504 + 8 + 2')
    pre_phys, post_phys = spec_old['expected']['physical'], spec_new['expected']['physical']
    need(pre_phys == W + CENTRES + 480 + COEFFICIENT_WORK, 'R-f.physical', 'pre-borrow hosted physical identity')
    need(post_phys == W + CENTRES + 437 + COEFFICIENT_WORK, 'R-f.physical', 'post-borrow hosted physical identity')
    zero = {pid: helpers_info[pid]['hyperplane_ended_live'] for pid in helpers_info}
    need(set(zero.values()) == {76}, 'R-f.zero_buffers', 'zero buffers per call')
    z = 76
    rows = dict(pre_borrow_charged=charge(pre_phys), post_borrow_charged=charge(post_phys),
                post_borrow_plus_zero_buffers=charge(post_phys + z), parent_charged=charge(parent_physical),
                parent_plus_zero_buffers=charge(parent_physical + z))
    for name, row in rows.items():
        need(row['row_coefficient'] < ROW_LIMIT, 'R-f.row', name + ' row coefficient')
    need(rows['post_borrow_plus_zero_buffers']['stock_bits'] == rows['post_borrow_charged']['stock_bits'] ==
         rows['pre_borrow_charged']['stock_bits'], 'R-f.row', 'hosted stock bits change')
    need(rows['parent_plus_zero_buffers']['stock_bits'] == rows['parent_charged']['stock_bits'], 'R-f.row',
         'parent stock bits change')
    bits = rows['post_borrow_charged']['stock_bits']
    return dict(
        spec_charge='physical = data families W + 8 centres + R local helpers (reserved tableau) + 2 coefficient work; '
                    'parent_physical = parent live + 504 + 8 + 2 (inherited dedicated-bank parent, R0 = 504)',
        W=W, helpers_pre=480, helpers_post=437, charged_physical_pre=pre_phys, charged_physical_post=post_phys,
        charged_physical_change=post_phys - pre_phys, parent_physical=parent_physical,
        parent_geometry_unchanged=True, zero_buffers_per_call=zero,
        zero_buffers_in_physical_identity=False,
        zero_buffer_note='Each borrowed word allocates one private FULL-frame zero buffer per hyperplane-ended live '
                         'helper (76) inside its final cleanup and frees it; calls are serial, so dedicating them '
                         'costs 76 families once, not per call.',
        payload_bits=payload, row_limit=ROW_LIMIT, charges=rows,
        max_physical_with_same_stock_bits=((1 << bits) - 1) // g,
        formula_reproduces_independent_receipt=dict(physical=independent['physical'], stock_bits=ref['stock_bits'],
                                                    row=ref['row_coefficient']))


def package_tree_sha256(repo, blob_dir=None):
    """sha256 of every blob in the package tree at the head (to ask whether a cited input is shipped).
    With blob_dir: sha256 of every regular file of the exported copy (a full export of the package
    gives the same set; a partial export can only under-report what is shipped)."""
    if blob_dir is not None:
        out, count = set(), 0
        for root, dirs, files in os.walk(blob_dir):
            dirs.sort()
            for name in sorted(files):
                with open(os.path.join(root, name), 'rb') as handle:
                    out.add(hashlib.sha256(handle.read()).hexdigest())
                count += 1
        return out, count
    listing = git(repo, 'ls-tree', '-r', HEAD, PKG).decode().splitlines()
    out = set()
    for line in listing:
        meta, _path = line.split('\t', 1)
        _mode, kind, oid = meta.split()
        if kind == 'blob':
            out.add(hashlib.sha256(git(repo, 'cat-file', 'blob', oid)).hexdigest())
    return out, len(listing)


def staleness(blobs, repo, blob_dir=None):
    """Arithmetic facts about the shipped pre-borrow evidence (its OWNERS blob is not in the package tree)."""
    independent = parse(blobs, 'evidence/INDEPENDENT.json')
    spec_old = parse(blobs, 'SPEC.json')
    owners_sha = hashlib.sha256(blobs['OWNERS.json.gz']).hexdigest()
    ind_owner_sha = [v for k, v in independent['input_sha256'].items() if k.endswith('OWNERS.json.gz')]
    shipped, tree_entries = package_tree_sha256(repo, blob_dir)
    lp = {p: as_profile(v, 'R-s', 'independent') for p, v in independent['local_profiles'].items()}
    counts = independent['provider_counts']
    recomputed = Counter()
    for p, n in counts.items():
        for r, c in lp[p].items():
            recomputed[r] += n * c
    recomputed += as_profile(independent['idle'], 'R-s', 'independent idle')
    widths = {p: sum(int(k) * v for k, v in inv.items()) for p, inv in independent['width_inventories'].items()}
    return dict(
        independent_roles=independent['roles'], shipped_roles=len(parse(blobs, 'OWNERS.json.gz')),
        independent_owner_sha256=ind_owner_sha, shipped_owner_sha256=owners_sha,
        independent_owner_blob_in_package_tree=bool(set(ind_owner_sha) & shipped), package_tree_blobs=tree_entries,
        spec_owner_blob_in_package_tree=spec_old['data']['owners_sha256'] in shipped,
        independent_profile_identity_holds=recomputed == as_profile(independent['profile'], 'R-s', 'profile'),
        independent_local_profiles=independent['local_profiles'],
        independent_rank_mass_identity=mass(recomputed) == independent['rank_mass'] == 73 * independent['live'] - independent['deficit'],
        independent_width_per_call=widths,
        top_level_spec_owners_sha256=spec_old['data']['owners_sha256'],
        top_level_spec_expected_hosted=spec_old['expected']['hosted_residuals'],
        top_level_spec_is_pre_borrow=spec_old['data']['owners_sha256'] != owners_sha)


# ------------------------------------------------------- negative controls ---

def controls(ctx, sched, rows):
    T, W = ctx['T'], ctx['W']
    order = ctx['order']
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

    def run(name, expected, mutant_rows, mutant_ctx=None):
        try:
            run_pipeline(mutant_ctx or ctx, sched, mutant_rows)
        except CheckFailure as exc:
            need(exc.check == expected, 'control', name + ' rejected by ' + exc.check + ' (' + exc.detail +
                 '), expected ' + expected)
            out.append(dict(name=name, rejected_by=exc.check, detail=exc.detail))
            return
        raise CheckFailure('control', 'negative control accepted: ' + name)

    # 1 duplicate a helper inside one call (two equal-width helpers, so R-a.width stays silent)
    call0 = by_call[0]
    a, b = next((i, j) for i in call0 for j in call0
                if i < j and rows[i]['width'] == rows[j]['width'])
    run('duplicate_helper_in_call', 'R-a.duplicate_helper', replaced({b: dict(rows[b], helper=rows[a]['helper'])}))
    # 2 drop one role
    run('dropped_role', 'R-a.count', rows[1:])
    # 3 narrowed width
    i = next(k for k, z in enumerate(rows) if z['width'] > 1)
    run('narrowed_width', 'R-a.width', replaced({i: dict(rows[i], width=rows[i]['width'] - 1)}))
    # 4 family in the private namespace
    run('private_namespace_family', 'R-e.namespace', replaced({0: dict(rows[0], family=W)}))
    # 5 consistent role placed on the caller's active pair
    z = rows[0]
    active = stage_pair[z['stage']]
    child = next(c for c in sorted(rank) if pair[c] == active)
    fam = z['replica'] * FAMILIES_PER_REPLICA + (2 * active + side[child]) * V + z['port']
    run('caller_active_pair', 'R-e.active_pair', replaced({0: dict(z, owner_replica=z['replica'], child=child, offset=0,
                                                                     family=fam, copy=V * z['replica'] + z['port'])}))
    # 6 two helpers on one family in one invocation
    a, b = call0[0], call0[1]
    host = {k: rows[a][k] for k in ('owner_replica', 'child', 'port', 'family', 'copy', 'offset')}
    run('two_helpers_one_family', 'R-e.family_unique_per_call', replaced({b: dict(rows[b], **host)}))
    # 7 role moved outside its owner's window: swap the hosts of one helper between two calls so that
    #   R-a and R-e still hold for both mutated roles.
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
    run('role_outside_owner_window', 'R-d.window', replaced(swap))
    # 8 overlapping slices in one bin (second slice moved onto the first one's offset)
    bins = {}
    for k, z in enumerate(rows):
        bins.setdefault((z['owner_replica'], z['child'], z['port']), []).append(k)
    pick = None
    for b, members in sorted(bins.items()):
        if len(members) >= 2:
            members = sorted(members, key=lambda k: rows[k]['offset'])
            a, c = members[0], members[1]
            if rows[a]['offset'] + rows[c]['width'] <= rank[b[1]]:
                pick = (a, c)
                break
    need(pick is not None, 'control', 'no overlap control could be built')
    a, c = pick
    run('overlapping_slices', 'R-b.overlap', replaced({c: dict(rows[c], offset=rows[a]['offset'])}))
    # 9 gap in the occupied prefix (last slice of a non-full bin shifted up by one)
    gap = None
    for b, members in sorted(bins.items()):
        last = max(members, key=lambda k: rows[k]['offset'])
        if rows[last]['offset'] + rows[last]['width'] + 1 <= rank[b[1]]:
            gap = last
            break
    need(gap is not None, 'control', 'no prefix control could be built')
    run('gap_in_prefix', 'R-b.prefix', replaced({gap: dict(rows[gap], offset=rows[gap]['offset'] + 1)}))
    # 10 tampered idle remainder claim (one 48-remainder claimed as 47)
    claims = dict(ctx['claims'])
    src, claimed = claims['idle'][0]
    tampered = Counter(claimed)
    tampered[48] -= 1
    tampered[47] += 1
    claims['idle'] = [(src, +tampered)] + claims['idle'][1:]
    run('tampered_idle_remainder', 'R-c.idle', rows, dict(ctx, claims=claims))
    # 11 tampered global profile claim
    claims = dict(ctx['claims'])
    src, claimed = claims['profile'][0]
    tampered = Counter(claimed)
    tampered[1] += 1
    claims['profile'] = [(src, tampered)] + claims['profile'][1:]
    run('tampered_global_profile', 'R-c.profile', rows, dict(ctx, claims=claims))
    # 12 committed PLAN window time list truncated (X1)
    plan = dict(ctx['plan'])
    windows = dict(plan['windows'])
    key = next(k for k in sorted(windows) if windows[k][1])
    windows[key] = [windows[key][0], windows[key][1][:-1]]
    plan['windows'] = windows
    run('truncated_plan_window', 'R-d.plan_windows', rows, dict(ctx, plan=plan))
    return out


# -------------------------------------------------------------------- main ---

def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--repo', default=REPO_DEFAULT)
    parser.add_argument('--blob-dir', default=None,
                        help='exported package copy: DIR/<package-relative path> (instead of git blobs)')
    parser.add_argument('--out', action='store_true', help='write ' + RECEIPT_NAME + ' next to this script')
    args = parser.parse_args()
    started = time.time()
    try:
        blobs, record = load_blobs(args.repo, args.blob_dir)
        ctx, rows, helpers_info, extra = borrow_case(blobs)
        sched = derive_schedule(ctx)
        result = run_pipeline(ctx, sched, rows)
        physical = physical_analysis(blobs, ctx, helpers_info, extra)
        stale = staleness(blobs, args.repo, args.blob_dir)
        rejected = controls(ctx, sched, rows)
        pctx, prows = parent_case(blobs)
        psched = derive_schedule(pctx)
        presult = run_pipeline(pctx, psched, prows)
        calls = result['calls']
        live, deficit = result['live'], result['deficit']
        need(result['rank_mass'] == (M - 1) * live + (live - deficit) and live - deficit == 64 * calls,
             'R-c.mass', 'mass = (m-1)W + (W-D) with W-D = 64 per call')
        per_call = {p: helpers_info[p]['local_mass'] - helpers_info[p]['width_per_call'] for p in helpers_info}
        per_call_pre = {p: helpers_info[p]['local_mass_pre'] - helpers_info[p]['width_per_call_pre'] for p in helpers_info}
        need(len(set(per_call.values()) | set(per_call_pre.values())) == 1, 'R-c.mass',
             'local mass - hosted width per call is one constant before and after borrowing')
    except CheckFailure as exc:
        print('FAIL_FILL_CHECK ' + str(exc))
        return 1
    except Exception as exc:   # malformed input: report, never pass
        print('FAIL_FILL_CHECK unexpected ' + type(exc).__name__ + ': ' + str(exc))
        return 1
    identities = dict(
        rank_mass='mass = m*W - D = 73*66304 - 23680 = %d' % result['rank_mass'],
        decomposition='mass = (m-1)*W + (W - D) = 72*66304 + 42624; W - D = 576*T = 64*(9T) = 64*666',
        capacity='idle capacity = T*112*sum(child ranks) = %d; idle mass = capacity - hosted width = %d - %d = %d'
                 % (result['idle_capacity'], result['idle_capacity'], result['hosted_width'], result['idle_mass']),
        per_call='local mass - hosted width per call = %s (pre-borrow %s): the borrowing lowers both by the same '
                 'amount, so the rank mass and deficit are unchanged' % (per_call, per_call_pre),
        halving='73^2 = 5329 > 2*%d^2 = %d' % (result['max_child'], 2 * result['max_child'] ** 2))
    receipt = dict(
        status='PASS_INDEPENDENT_T74_BORROW43_FILL_RECOUNT',
        object=dict(pr=2269, head=HEAD, package=PKG, owners='OWNERS.json.gz'),
        inputs=record,
        windows=dict(rebuilt=len(sched['windows']), equal_to_plan=True, expanded_events=sched['events'],
                     bridges=sched['bridges'], child_ranks={str(c): sched['rank'][c] for c in sorted(sched['rank'])},
                     swept_children_without_capacity=sched['rankless_children']),
        borrow=result, helpers=helpers_info, identities=identities, physical=physical, stale_evidence=stale,
        controls_rejected=rejected,
        parent_positive_control=dict(package_path=PKG + '/inputs/OWNERS.json.gz', windows_equal_to_plan=True, **presult),
        not_checked=['local paid profiles of the borrowed words (taken from the word reports; recount = task A)',
                     'X2 pending-axis disjointness and 73-axis charts (DATA-PHASES.json is not shipped outside the '
                     'vendored tarball)', 'native LOCAL-PROGRAMS, controller emission, invoice and prefix bits',
                     'physical location of the 76 zero buffers (not stated in the shipped text)'],
        scope='Finite recount of the shipped hosting fill under the stated rules. Not a proof of the conditional '
              'kappa; local words, invoice, moments and outer assembly are outside this check.',
        credits='PR2269 jeremykothe2; PR2226 Cinna Davis / 1337isnot1337; PR2260 Dugongue; T74 lineage PR1319, '
                'PR1625, PR1297 (and PR1193); rules from PR858 / complex-double-replica-owners PROOF.md and the T16 '
                'owner audit (icekylinx checker lineage). Prepared with substantial AI assistance (Claude Code, '
                'Anthropic); Apache-2.0.')
    if args.blob_dir is not None:   # default (git) mode keeps the receipt layout unchanged
        receipt['inputs_source'] = ('exported copy (--blob-dir); pins re-verified; package-tree membership '
                                    'from the %d files of the copy' % stale['package_tree_blobs'])
    if args.out:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), RECEIPT_NAME)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(json.dumps(receipt, indent=1, sort_keys=True) + '\n')
    print('borrow fill: roles=%d calls=%d helpers/call=%d idle=%s' % (result['roles'], calls,
                                                                       result['helpers_per_call'], result['idle']))
    print('borrow profile=%s mass=%d deficit=%d cross_replica=%d' % (result['profile'], result['rank_mass'],
                                                                   result['deficit'], result['cross_replica_roles']))
    print('physical: pre=%d post=%d parent=%d zero_buffers/call=%s stock_bits=%s' % (
        physical['charged_physical_pre'], physical['charged_physical_post'], physical['parent_physical'],
        physical['zero_buffers_per_call'],
        sorted({row['stock_bits'] for row in physical['charges'].values()})))
    print('stale: INDEPENDENT roles=%d (shipped %d), owner blob shipped=%s; top-level SPEC pre-borrow=%s' % (
        stale['independent_roles'], stale['shipped_roles'], stale['independent_owner_blob_in_package_tree'],
        stale['top_level_spec_is_pre_borrow']))
    print('parent control: roles=%d idle=%s mass=%d' % (presult['roles'], presult['idle'], presult['rank_mass']))
    print('controls rejected: %d (%s)' % (len(rejected), ', '.join(c['name'] + '->' + c['rejected_by'] for c in rejected)))
    print('runtime_s=%.1f' % (time.time() - started))
    print('PASS_INDEPENDENT_T74_BORROW43_FILL_RECOUNT roles=%d parent_roles=%d controls=%d' % (
        result['roles'], presult['roles'], len(rejected)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
