#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Window-exact whole-helper owner fill for the 80-alias T74 borrow words (PR2339).

Object: the two 80-alias local words BORROW-WORD-80{base,extra} of PR #2339 (this author, local
commit bf1742aee4d855efb8bbd44a8419eddb33a679e5, research/t74-low-alias-borrowing/words/): 400 live
helpers per call, width inventory {4:4,5:4,7:36,8:84,9:272} (sum 3408), hosted on the unchanged T74
template of PR #2269 (Jeremy Kothe, head b479fc5567bc09ab9185bffe89b62594f36d74e5,
research/gmx-t74-borrow43/): 74 replicas, nine stages, 666 calls (249 gauge44 + 417 extra by
DISPATCH.json), 18 ranked idle children per (replica, port) with ranks {8:6, 16:4, 32:4, 48:4}.

Helper index convention (as PR #2269): helper i is the i-th live helper register of the word, i.e.
registers 224..703 minus the 80 `removed` ones, in increasing order; its width is
rank(final frame) - rank(start frame) over GF(2).  Both words have the same live registers and the
same ordered widths, so the index map is provider independent (asserted).

Hosting rules (PR #2269 / complex-double-replica-owners PROOF.md lineage): one role per
(call, live helper); the role sits in a bin (owner replica, child, port) whose PLAN window contains
the call; slices in a bin are disjoint and prefix filled; physical family
owner*896 + (2*pair(child)+side(child))*112 + port carries at most one helper per call; never the
caller's active pair.  Row format = PR #2269 OWNERS.json.gz rows (keys child, copy, family, helper,
offset, owner_replica, port, replica, stage, time, width), sorted by (time, helper).

Method (deterministic, no randomness; defaults in DEFAULTS): (1) an earliest-deadline time sweep over the 666
calls (direction 'forward'; a meet-in-the-middle variant is available via --direction) whose pattern progressions
come from the width-aware pattern LP of ceiling_lp.py: rank 8 <- (8); rank 16 <- (7,9) / (8,8) / (9);
rank 32 <- (9,9,9) / (4,9,9,9) / (5,9,9,9); rank 48 <- (9,9,9,9,9) or empty.  Partial bins are continued before
new bins are opened; empty rank-16 bins are rescued with a 9 at their last call; roles with no LP-progression host
(sweep fallbacks, all in calls 662-665) take any legal bin with room.  (2) a hill-climb over legal whole-role
relocations and whole-bin dissolves, scored by the exact moment weight (rem/73)^(1-a) at a = A_PRICE (mu is linear
in the counts at fixed a), accepted only on strict improvement.  The idle recount and global profile are written
to BUILD-RECEIPT.json / PROFILE-80.json; legality is re-checked independently by check_fill.py.

Credits: PR2339 (this author: the 80-alias words); PR2269 Jeremy Kothe (T74 borrow43 template,
PLAN windows, DISPATCH, owner-map format and the exact-fill lineage); PR2322 Vlado Vojdanovski
(owner exchanges / hill-climb on the T74 fill); PR2312/PR2302 jeremykothe2 (width-exchange supplier
and kernels); PR2226 Cinna Davis (anticipatory dirty borrowing); PR1319/PR1297 Rohan Arun et al.
(T74 exact fill lineage); hosting rules of Hao Yan's PR858 / complex-double-replica-owners PROOF.md.
The word-width routine follows our own iteration-3 independent checker (fill_check.py,
commit 4a2f20ea).  No code from PR2269/PR2322 is imported or run.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.

Usage: python3 -I -B build_fill.py [--repo PATH] [--out-dir DIR]
"""

import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter

if not __debug__:
    sys.exit('refusing to run under python -O')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(os.path.dirname(HERE))
HEAD_2269 = 'b479fc5567bc09ab9185bffe89b62594f36d74e5'
HEAD_2339 = 'bf1742aee4d855efb8bbd44a8419eddb33a679e5'
PKG_2269 = 'research/gmx-t74-borrow43/'
PKG_2339 = 'research/t74-low-alias-borrowing/'
PINS = {  # (commit, path) -> (git blob id, sha256)
    (HEAD_2269, PKG_2269 + 'new/PLAN.json'): ('7cacd857edd0f29be5bd2ca9590a17fed4da17ba',
                                              'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2'),
    (HEAD_2269, PKG_2269 + 'DISPATCH.json'): ('20807cc27c82db1f8f9cd47c79713e066d6ad816',
                                              '6aad7f628f4c9b510a95c5b34357736303069ecf92a551659900b1ba540bc7e0'),
    (HEAD_2269, PKG_2269 + 'ORDER.json'): ('7409c4df1092241729739596c7648bda504e6aad',
                                           '519d1d5dbb997a219fcfcad34c0b03e7838bef24199784d7e964fa10090f66e1'),
    (HEAD_2269, PKG_2269 + 'GLOBAL-TEMPLATE.json.gz'): ('5327fc2f4e8ea82ed356c94ff040d23fc73c731f',
                                                        '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db'),
    (HEAD_2339, PKG_2339 + 'words/BORROW-WORD-80base.json.gz'): (
        'c5953dfdb0ee9ac0c2c73eb29e320582b4569d2b', '61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493'),
    (HEAD_2339, PKG_2339 + 'words/BORROW-WORD-80extra.json.gz'): (
        '852868543ed36efa799b3ed6dd76a0442b0d6ff1', '1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5'),
}
V, H, NREG = 112, 9, 480
FAM = 896
M, W_LIVE, T_REP = 73, 66304, 74
LOCAL = {'gauge44': {1: 2303, 2: 527, 3: 386, 4: 125, 5: 37, 8: 8},
         'extra': {1: 2287, 2: 535, 3: 386, 4: 125, 5: 37, 8: 8}}
INVENTORY = {4: 4, 5: 4, 7: 36, 8: 84, 9: 272}

# Final patterns per rank that the sweep aims for (sorted tuples).  A state is "allowed" if it is a
# sub-multiset of one of them; a state is "final" if it is one of them.  Order = preference.
TARGETS = {
    8: [(8,), (4, 4), (7,)],
    16: [(7, 9), (8, 8), (9,)],
    32: [(9, 9, 9), (4, 9, 9, 9), (5, 9, 9, 9)],
    48: [(9, 9, 9, 9, 9)],
}
DEFAULTS = dict(direction='forward', rescue_window=1, rounds=3)   # the configuration that produced OWNERS-80


def git(repo, *args):
    p = subprocess.run(['git', '-C', repo] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        sys.exit('git %s failed: %s' % (' '.join(args), p.stderr.decode()))
    return p.stdout


def load(repo, commit, path):
    oid, sha = PINS[(commit, path)]
    got = git(repo, 'rev-parse', '--verify', commit + ':' + path).decode().strip()
    assert got == oid, (path, got)
    data = git(repo, 'cat-file', 'blob', oid)
    assert hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == oid
    assert hashlib.sha256(data).hexdigest() == sha, path
    if path.endswith('.gz'):
        data = gzip.decompress(data)
    return json.loads(data)


def gf2_rank(vectors):
    piv = {}
    for x in vectors:
        while x:
            top = x.bit_length() - 1
            if top in piv:
                x ^= piv[top]
            else:
                piv[top] = x
                break
    return len(piv)


def word_helpers(word):
    """Live helper registers and widths (rule of our iteration-3 fill_check.py)."""
    first, end = 2 * V, 2 * V + NREG
    removed = set(word['removed'])
    live = [r for r in range(first, end) if r not in removed]
    widths = []
    for r in live:
        final = word['helper_final'].get(str(r), [1 << i for i in range(H)])
        start = word['start_extra'].get(str(r), [])
        assert gf2_rank(final) == len(final) and gf2_rank(start) == len(start)
        assert gf2_rank(list(final) + list(start)) == len(final)
        widths.append(len(final) - len(start))
    return live, sorted(removed), widths


def sub_multiset(a, b):
    ca, cb = Counter(a), Counter(b)
    return all(cb[k] >= v for k, v in ca.items())


def build(repo, direction=DEFAULTS['direction'], rescue_window=DEFAULTS['rescue_window']):
    plan = load(repo, HEAD_2269, PKG_2269 + 'new/PLAN.json')
    order = [tuple(x) for x in load(repo, HEAD_2269, PKG_2269 + 'ORDER.json')]
    dispatch = {(s, r): p for s, r, p in load(repo, HEAD_2269, PKG_2269 + 'DISPATCH.json')}
    assert order == [tuple(x) for x in plan['order']] and len(order) == 666
    words = {'gauge44': load(repo, HEAD_2339, PKG_2339 + 'words/BORROW-WORD-80base.json.gz'),
             'extra': load(repo, HEAD_2339, PKG_2339 + 'words/BORROW-WORD-80extra.json.gz')}
    info = {p: word_helpers(w) for p, w in words.items()}
    assert info['gauge44'] == info['extra'], 'provider-independent helper map'
    live, removed, widths = info['gauge44']
    assert len(live) == 400 and len(removed) == 80 and Counter(widths) == Counter(INVENTORY)
    for p, w in words.items():
        assert {int(k): v for k, v in w['report']['local_profile'].items()} == LOCAL[p]
        assert sum(r * n for r, n in LOCAL[p].items()) == 1856 + sum(widths)
    helpers_of_width = {w: [i for i, x in enumerate(widths) if x == w] for w in INVENTORY}
    pair = {int(c): v for c, v in plan['pairs'].items()}
    side = {int(c): v for c, v in plan['sides'].items()}
    template = load(repo, HEAD_2269, PKG_2269 + 'GLOBAL-TEMPLATE.json.gz')
    stage_pair = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    assert sorted(stage_pair) == list(range(9))
    windows = []      # (r, c, a, b, rank)
    for key, (rk, ts) in plan['windows'].items():
        r, c = map(int, key.split(','))
        if not ts:
            continue
        assert ts == list(range(ts[0], ts[-1] + 1)), 'windows are contiguous call intervals'
        windows.append((r, c, ts[0], ts[-1], rk))
    NT = len(order)
    # Processing sequence: forward over [0, meet), then backward from NT-1 down to meet.
    meet = NT if direction == 'forward' else (0 if direction == 'reverse' else int(direction))
    assert 0 <= meet <= NT
    sequence = list(range(meet)) + list(range(NT - 1, meet - 1, -1))
    windows.sort(key=lambda x: (x[3], x[2], x[0], x[1]))   # deterministic
    nwin = len(windows)
    # allowed states and their completions
    allowed = {R: set() for R in TARGETS}
    for R, pats in TARGETS.items():
        for p in pats:
            for mask in range(1 << len(p)):
                allowed[R].add(tuple(sorted(p[i] for i in range(len(p)) if mask >> i & 1)))
    final = {R: set(p) for R, p in TARGETS.items()}

    def need(R, st):
        """Fewest further roles to reach a final pattern from state st (0 if final)."""
        if st in final[R]:
            return 0
        return min(len(p) - len(st) for p in TARGETS[R] if sub_multiset(st, p))

    # state[j] : dict state-tuple -> list of ports (stack, deterministic)
    state = [{(): list(range(V - 1, -1, -1))} for _ in range(nwin)]
    roles = []          # (t, j, port, width)
    shortfall = Counter()
    by_time = [[] for _ in range(NT)]
    for j, (r, c, a_, b_, rk) in enumerate(windows):
        for t in range(a_, b_ + 1):
            by_time[t].append(j)
    for t in sequence:
        s_call, r_call = order[t]
        forward = t < meet
        # unprocessed calls of each open window (including t): EDF key
        if forward:
            rem = {j: windows[j][3] - t + 1 for j in by_time[t]}
        else:
            rem = {j: t - max(windows[j][2], meet) + 1 for j in by_time[t]}
        active = sorted(by_time[t], key=lambda j: (rem[j], j))
        moves = []
        fam_used = set()

        def take(j, st, w):
            ports = state[j].get(st)
            if not ports:
                return False
            r, c = windows[j][0], windows[j][1]
            for k in range(len(ports) - 1, -1, -1):
                port = ports[k]
                fam = r * FAM + (2 * pair[c] + side[c]) * V + port
                if fam in fam_used:
                    continue
                ports.pop(k)
                fam_used.add(fam)
                moves.append((j, port, st, tuple(sorted(st + (w,)))))
                roles.append((t, j, port, w))
                return True
            return False

        def place(w, n, rules):
            """Place n roles of width w following rules = list of (rank, predicate on state, urgency)."""
            left = n
            for R, pred, mode in rules:
                if left == 0:
                    break
                for j in active:
                    if left == 0:
                        break
                    r, c, a, b, rk = windows[j]
                    if R is not None and rk != R:
                        continue
                    if r == r_call and pair[c] == stage_pair.get(s_call, -1):
                        continue
                    remaining_calls = rem[j]
                    sts = sorted(state[j], key=lambda st: (-sum(st), st)) if mode == 'free' else sorted(state[j])
                    for st in sts:
                        if not state[j][st] or not pred(st):
                            continue
                        new = tuple(sorted(st + (w,)))
                        if mode == 'rescue':
                            if remaining_calls > rescue_window:
                                continue
                            quota = -(-len(state[j][st]) // remaining_calls)
                            while left and quota and take(j, st, w):
                                left -= 1
                                quota -= 1
                            continue
                        if mode == 'free':
                            if sum(new) > rk:
                                continue
                        else:
                            if new not in allowed[R]:
                                continue
                            nd = need(R, new)
                            if mode == 'urgent' and remaining_calls > max(1, need(R, st)):
                                continue
                            if nd > remaining_calls - 1:   # could not be completed in time
                                continue
                        while left and take(j, st, w):
                            left -= 1
                        if left == 0:
                            break
            return left

        anyst = lambda st: True
        nonempty = lambda st: len(st) > 0
        empty = lambda st: len(st) == 0
        FREE = [(16, nonempty, 'free'), (32, nonempty, 'free'), (48, nonempty, 'free'), (8, anyst, 'free'),
                (None, anyst, 'free')]
        # 8s
        left = place(8, INVENTORY[8], [
            (8, empty, 'urgent'), (16, lambda st: st == (8,), 'any'), (8, empty, 'any'),
            (16, empty, 'any')])
        shortfall[8] += left
        if left:
            left = place(8, left, FREE)
        # 7s
        left = place(7, INVENTORY[7], [
            (8, empty, 'urgent'), (16, lambda st: st == (9,), 'any'), (16, empty, 'any')])
        shortfall[7] += left
        if left:
            left = place(7, left, FREE)
        # 4s and 5s
        for w in (4, 5):
            left = place(w, INVENTORY[w], [
                (32, lambda st: st == (9, 9, 9), 'any'), (32, lambda st: st in ((9, 9), (9,)), 'any'),
                (32, empty, 'any')])
            shortfall[w] += left
            if left:
                left = place(w, left, FREE)
        # 9s
        left = place(9, INVENTORY[9], [
            (16, lambda st: st == (7,), 'any'),
            (32, nonempty, 'urgent'), (48, nonempty, 'urgent'), (16, empty, 'rescue'),
            (32, nonempty, 'any'), (48, nonempty, 'any'),
            (32, empty, 'any'), (48, empty, 'any')])
        shortfall[9] += left
        if left:
            left = place(9, left, FREE)
        assert left == 0, ('no legal host left at call', t)
        for j, port, st, new in moves:
            state[j].setdefault(new, []).append(port)
    return dict(plan=plan, order=order, dispatch=dispatch, windows=windows, roles=roles, widths=widths,
                stage_pair=stage_pair,
                live=live, removed=removed, helpers_of_width=helpers_of_width, pair=pair, side=side,
                state=state, shortfall=shortfall)



# ---------------------------------------------------------------- hill-climb ---

A_PRICE = 0.0016866   # exponent at which bin costs are evaluated: cost(rem) = (rem/73)^(1-a); mu is linear in counts


def bin_cost(rem):
    return 0.0 if rem == 0 else (rem / M) ** (1.0 - A_PRICE)


def hill_climb(res, rounds=3, log=print):
    """Deterministic improvement of the sweep result by legal relocations of whole roles.

    Moves: (1) relocate one role (call t, width w) to another bin whose window contains t, whose physical
    family is free at t and which has room; (2) dissolve a bin: relocate all of its roles (accepted only if
    the summed exact cost change is negative, else rolled back).  Legality is preserved move by move.
    """
    windows, pair, side, order = res['windows'], res['pair'], res['side'], res['order']
    stage_pair = res['stage_pair']
    NT = len(order)
    by_time = [[] for _ in range(NT)]
    for j, (r, c, a, b, rk) in enumerate(windows):
        for t in range(a, b + 1):
            by_time[t].append(j)
    fam = lambda j, port: windows[j][0] * FAM + (2 * pair[windows[j][1]] + side[windows[j][1]]) * V + port
    content = {}            # (j, port) -> {t: w}
    used = {}
    for (t, j, port, w) in res['roles']:
        content.setdefault((j, port), {})[t] = w
        used[(j, port)] = used.get((j, port), 0) + w
    fam_used = set((fam(j, port), t) for (t, j, port, w) in res['roles'])
    by_used = [dict() for _ in windows]      # j -> used value -> set of ports
    for j in range(len(windows)):
        for port in range(V):
            by_used[j].setdefault(used.get((j, port), 0), set()).add(port)

    def rank(j):
        return windows[j][4]

    def set_used(j, port, new):
        old = used.get((j, port), 0)
        by_used[j][old].discard(port)
        by_used[j].setdefault(new, set()).add(port)
        used[(j, port)] = new

    def best_target(t, w, avoid):
        s_call, r_call = order[t]
        best = None
        for j in by_time[t]:
            r, c, a, b, rk = windows[j]
            if r == r_call and pair[c] == stage_pair[s_call]:
                continue
            for u, ports in by_used[j].items():
                if not ports or u + w > rk:
                    continue
                d = bin_cost(rk - u - w) - bin_cost(rk - u)
                if best is not None and d >= best[0]:
                    continue
                for port in sorted(ports):
                    if (j, port) in avoid or (fam(j, port), t) in fam_used:
                        continue
                    best = (d, j, port)
                    break
        return best

    def move(t, w, src, dst):
        j0, p0 = src
        j1, p1 = dst
        del content[src][t]
        set_used(j0, p0, used[src] - w)
        fam_used.discard((fam(j0, p0), t))
        content.setdefault(dst, {})[t] = w
        set_used(j1, p1, used.get(dst, 0) + w)
        fam_used.add((fam(j1, p1), t))

    total_gain = 0.0
    for rnd in range(rounds):
        gain_round = 0.0
        moves_round = 0
        keys = sorted(k for k in content if content[k])
        # cost-ordered: the most expensive bins first
        keys.sort(key=lambda k: -bin_cost(rank(k[0]) - used[k]))
        for key in keys:
            if not content.get(key):
                continue
            j0, p0 = key
            rk = rank(j0)
            # (2) dissolve: relocate every role of this bin
            items = sorted(content[key].items())
            done = []
            delta = 0.0
            ok = True
            for t, w in items:
                rem_before = rk - used[key]
                d_out = bin_cost(rem_before + w) - bin_cost(rem_before)
                tgt = best_target(t, w, {key})
                if tgt is None:
                    ok = False
                    break
                move(t, w, key, (tgt[1], tgt[2]))
                done.append((t, w, (tgt[1], tgt[2])))
                delta += d_out + tgt[0]
            if ok and delta < -1e-12:
                gain_round -= delta
                moves_round += 1
                continue
            for t, w, dst in reversed(done):       # roll back
                move(t, w, dst, key)
            # (1) single relocations from this bin
            for t, w in sorted(content[key].items()):
                rem_before = rk - used[key]
                d_out = bin_cost(rem_before + w) - bin_cost(rem_before)
                tgt = best_target(t, w, {key})
                if tgt is not None and d_out + tgt[0] < -1e-12:
                    move(t, w, key, (tgt[1], tgt[2]))
                    gain_round -= d_out + tgt[0]
                    moves_round += 1
        total_gain += gain_round
        log('hill-climb round %d: accepted %d, cost gain %.6f' % (rnd, moves_round, gain_round))
        if moves_round == 0:
            break
    res['roles'] = sorted((t, j, port, w) for (j, port), d in content.items() for t, w in d.items())
    return total_gain

def emit(res):
    order, windows, pair, side = res['order'], res['windows'], res['pair'], res['side']
    per_call_width = {}
    rows = []
    for t, j, port, w in res['roles']:
        per_call_width.setdefault((t, w), []).append((j, port))
    for (t, w), hosts in sorted(per_call_width.items()):
        hs = res['helpers_of_width'][w]
        assert len(hosts) == len(hs), ('call', t, 'width', w, len(hosts), len(hs))
        s, r = order[t]
        for helper, (j, port) in zip(hs, hosts):
            rr, c = windows[j][0], windows[j][1]
            rows.append(dict(child=c, copy=V * rr + port, family=rr * FAM + (2 * pair[c] + side[c]) * V + port,
                             helper=helper, offset=None, owner_replica=rr, port=port, replica=r, stage=s,
                             time=t, width=w))
    # prefix offsets in each bin, in call order
    bins = {}
    for z in sorted(rows, key=lambda z: (z['time'], z['helper'])):
        key = (z['owner_replica'], z['child'], z['port'])
        z['offset'] = bins.get(key, 0)
        bins[key] = z['offset'] + z['width']
    rows.sort(key=lambda z: (z['time'], z['helper']))
    return rows, bins


def recount(res, rows, bins):
    windows = res['windows']
    idle = Counter()
    for (r, c, a, b, rk) in windows:
        for port in range(V):
            left = rk - bins.get((r, c, port), 0)
            assert left >= 0
            if left:
                idle[left] += 1
    calls = Counter(res['dispatch'][k] for k in res['order'])
    prof = Counter()
    for p, n in calls.items():
        for rk, k in LOCAL[p].items():
            prof[rk] += n * k
    prof.update(idle)
    mass = sum(r * n for r, n in prof.items())
    return idle, prof, mass, calls


def float_root(prof):
    """Float bisection for mu(a) = sum_r n_r (r/m)^(1-a) / W = 1 (estimate only; not certified)."""
    lo, hi = 0.0, 0.01
    for _ in range(200):
        mid = (lo + hi) / 2
        if sum(n * (r / M) ** (1 - mid) for r, n in prof.items()) / W_LIVE < 1:
            lo = mid
        else:
            hi = mid
    return lo


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--out-dir', default=HERE)
    ap.add_argument('--direction', default=DEFAULTS['direction'],
                    help="'forward', 'reverse' or a meeting call index (forward to it, backward from the end)")
    ap.add_argument('--rescue-window', type=int, default=DEFAULTS['rescue_window'])
    ap.add_argument('--rounds', type=int, default=DEFAULTS['rounds'])
    ap.add_argument('--no-write', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    res = build(a.repo, a.direction, a.rescue_window)
    sweep_short = {str(k): v for k, v in sorted(res['shortfall'].items())}
    print('sweep fallbacks (roles placed outside the LP progressions):', sweep_short)
    rows0, bins0 = emit(dict(res))
    idle0, prof0, _m0, _c0 = recount(res, rows0, bins0)
    gain = hill_climb(res, a.rounds) if a.rounds else 0.0
    rows, bins = emit(res)
    idle, prof, mass, calls = recount(res, rows, bins)
    assert len(rows) == 666 * 400
    assert mass == M * W_LIVE - 23680 == 4816512, 'rank mass identity m*W - D'
    hosted = sum(z['width'] for z in rows)
    capacity = T_REP * V * sum(rk for (r, c, a_, b_, rk) in res['windows'] if r == 0)
    assert hosted == 666 * 3408 and sum(r * n for r, n in idle.items()) == capacity - hosted
    assert max(prof) == 48 and M * M > 2 * 48 * 48
    pats = Counter()
    contents = {}
    for z in rows:
        contents.setdefault((z['owner_replica'], z['child'], z['port']), []).append(z['width'])
    for (r, c, a_, b_, rk) in res['windows']:
        for port in range(V):
            pats[(rk, tuple(sorted(contents.get((r, c, port), []))))] += 1
    b_sweep, b_fill = float_root(prof0), float_root(prof)
    print('roles', len(rows), 'idle', dict(sorted(idle.items())))
    print('profile', dict(sorted(prof.items())), 'mass', mass)
    print('b (float) sweep only %.16f, after hill-climb %.16f' % (b_sweep, b_fill))
    for k in sorted(pats):
        print('  pattern', k, pats[k])
    data = gzip.compress(canonical(rows), mtime=0)
    owners_sha = hashlib.sha256(data).hexdigest()
    content_sha = hashlib.sha256(canonical(rows)).hexdigest()
    print('OWNERS-80 sha256', owners_sha, 'content', content_sha)
    plain = lambda c: {str(k): c[k] for k in sorted(c) if c[k]}
    receipt = dict(
        status='BUILT_T74_80ALIAS_OWNER_FILL',
        scope='Finite whole-helper owner fill of the PR2339 80-alias words on the unchanged PR2269 T74 template; '
              'built and self-recounted here, legality re-checked separately by check_fill.py. No kappa claim.',
        inputs={'%s:%s' % (c[:12], p): dict(git_blob=v[0], sha256=v[1]) for (c, p), v in sorted(PINS.items())},
        params=dict(direction=a.direction, rescue_window=a.rescue_window, rounds=a.rounds, a_price=A_PRICE,
                    targets={str(R): [list(p) for p in v] for R, v in TARGETS.items()}, randomness='none'),
        helper_map=dict(rule='helper i = i-th live helper register of BORROW-WORD-80{base,extra} (registers 224..703 '
                             'minus the 80 removed ones, increasing); width = rank(final) - rank(start); identical '
                             'for both providers', live_registers=res['live'], removed_registers=res['removed'],
                        widths=res['widths']),
        dispatch=plain(calls), roles=len(rows), helpers_per_call=400, width_per_call=3408,
        sweep=dict(fallback_roles=sweep_short, idle=plain(idle0), b_float=b_sweep),
        hill_climb=dict(cost_gain=gain),
        idle=plain(idle), profile=plain(prof), rank_mass=mass, deficit=M * W_LIVE - mass, live=W_LIVE,
        idle_capacity=capacity, hosted_width=hosted, idle_mass=capacity - hosted,
        cross_replica_roles=sum(z['owner_replica'] != z['replica'] for z in rows),
        idle_remainders=sum(idle.values()),
        patterns=[[rk, list(p), n] for (rk, p), n in sorted(pats.items())],
        b_float_estimate=b_fill,
        owners_sha256=owners_sha, owners_content_sha256=content_sha,
        identities=dict(mass='73*66304 - 23680 = 4816512 = local 666*1856 + idle capacity %d (= 1856 + 3408 per call '
                             'local mass, minus hosted width)' % capacity,
                        halving='73^2 = 5329 > 2*48^2 = 4608'),
        credits='PR2339 (this author); PR2269 Jeremy Kothe; PR2322 Vlado Vojdanovski; PR2312/PR2302 jeremykothe2; '
                'PR2226 Cinna Davis; PR1319/PR1297 T74 lineage (Rohan Arun et al.). Prepared with substantial AI '
                'assistance (Claude Code, Anthropic); Apache-2.0.')
    if not a.no_write:
        with open(os.path.join(a.out_dir, 'OWNERS-80.json.gz'), 'wb') as h:
            h.write(data)
        with open(os.path.join(a.out_dir, 'PROFILE-80.json'), 'w') as h:
            h.write(json.dumps(plain(prof), sort_keys=True) + '\n')
        with open(os.path.join(a.out_dir, 'BUILD-RECEIPT.json'), 'w') as h:
            h.write(json.dumps(receipt, indent=1, sort_keys=True) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    print('PASS_T74_80ALIAS_OWNER_FILL_BUILT roles=%d b_float=%.16f' % (len(rows), b_fill))


if __name__ == '__main__':
    main()
