#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Idle-remainder donor exchanges on PR3148's T740 fill of PR3133's words.

Every idle remainder of a (replica, port) - including the remainder of a partially hosted bin,
whose axes are the recipe axes [used, cap) - may donate axes to a fully idle (unhosted) child of
the same replica and port.  Each moved axis obeys PR1252's commuting rule (commutes with all of the
receiver's current axes, every stage entry/exit X and Y translation, the terminal Y translation and
both children's terminal translations).  Receivers are capped at rank 51 (73^2 > 2*51^2).
Phase 1 drains remainders smallest-first into the largest legal receiver; phase 2 runs the
frontier1094 star optimum (PR3184) on the untouched fully idle rank-48 children.

Inputs (pinned): DATA-PHASES.json on main; PR3148's materialized COMPOSED-FILL/ORDER/DISPATCH and
its PR3133 provider widths (PR3148-PROVIDERS.json, copied from PR3148 vendor/).
"""
import argparse, gzip, hashlib, itertools, json, math
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASES = HERE.parents[1] / 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
PIN = dict(phases='c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
           fill_payload='8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00',
           order='927226d702bf3cada076f4c459da9063c0df7e7154a62955cf75c40cf30215b9',
           dispatch='90edc935320dd6264e98dc735d868df3c95f5901c70d7d96171001fcb295cce0',
           providers='52eb0d85caa7b2d4a93acdf5011f52b793f61ddca86235fb03cd9a09397ad4cd')
T = 740
LOCAL = {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8}
IDLE_PR3148 = {1: 173160, 3: 48951, 5: 13875, 48: 282569}
BIT = Q('0.001733427039589844234749')   # PR589 bit saving, as pinned in the T74 outer ledger
PR3148_KAPPA = Q('0.0017297774946785970118859999999999999999999998999999999999999999999999')
PR3184_KAPPA = Q('0.0017301890612338507600949999999999999999999998999999999999999999999999')


def need(ok, why):
    if not ok: raise SystemExit('FAIL: ' + why)


def sha(b): return hashlib.sha256(b).hexdigest()
def dot(a, b): return (a & b).bit_count() & 1
def Hf(r): return 0.0 if r == 0 else r * (73.0 / r) ** 0.00173


def pgz(obj):
    d = bytearray(gzip.compress(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode(), mtime=0)); d[9] = 255
    return bytes(d)


# ---- exact root (rational intervals, directed rounding 1e-60) ----
S = 10 ** 60
def dn(x): return Q(math.floor(x * S), S)
def upr(x): return Q(math.ceil(x * S), S)
def atanh2(z, n):
    s, p = Q(0), z
    for j in range(n): s += p / (2 * j + 1); p *= z * z
    return 2 * s, 2 * p / ((2 * n + 1) * (1 - z * z))
L2 = atanh2(Q(1, 3), 120)
LN = {}
def lnr(r):
    if r not in LN:
        x, k = Q(73, r), 0
        while x > 2: x /= 2; k += 1
        a, e = atanh2((x - 1) / (x + 1), 80)
        LN[r] = (dn(a + k * L2[0]), upr(a + e + k * (L2[0] + L2[1])))
    return LN[r]
def ex(x0, x1):
    def ser(x):
        s, t = Q(0), Q(1)
        for n in range(1, 40): s += t; t = t * x / n
        return s, t
    a, _ = ser(x0); b, t = ser(x1)
    return dn(a), upr(b + 2 * t)
def moment(prof, b):
    W = 896 * T; lo = hi = Q(0)
    for r, n in prof.items():
        l0, l1 = lnr(r); e0, e1 = ex(b * l0, b * l1); lo += n * r * e0; hi += n * r * e1
    return lo / (73 * W), hi / (73 * W)
def root(prof, digits=25):
    f = lambda b: sum(n * r * (73 / r) ** b for r, n in prof.items()) / (73 * 896 * T) - 1
    a, c = 0.0, 0.01
    for _ in range(200):
        m = (a + c) / 2
        if f(m) < 0: a = m
        else: c = m
    g = 10 ** digits; k0, k1 = int(a * g) - 10 ** 10, int(a * g) + 10 ** 10
    need(moment(prof, Q(k0, g))[1] < 1 and moment(prof, Q(k1, g))[0] > 1, 'bracket')
    while k1 - k0 > 1:
        k = (k0 + k1) // 2; lo, hi = moment(prof, Q(k, g))
        if hi < 1: k0 = k
        elif lo > 1: k1 = k
        else: raise SystemExit('wide interval')
    return Q(k0, g), Q(k1, g)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--t740', type=Path, required=True, help='directory written by PR3148 materialize.py')
    a = ap.parse_args()
    raw = PHASES.read_bytes(); need(sha(raw) == PIN['phases'], 'phases pin')
    rec = {r['port']: r for r in json.loads(raw)['recipes']}
    fraw = gzip.decompress((a.t740 / 'COMPOSED-FILL.json.gz').read_bytes()); need(sha(fraw) == PIN['fill_payload'], 'fill pin')
    need(sha((a.t740 / 'ORDER.json').read_bytes()) == PIN['order'] and sha((a.t740 / 'DISPATCH.json').read_bytes()) == PIN['dispatch'], 'order/dispatch pins')
    praw = (HERE / 'PR3148-PROVIDERS.json').read_bytes(); need(sha(praw) == PIN['providers'], 'providers pin')
    prov = json.loads(praw); order = json.loads((a.t740 / 'ORDER.json').read_bytes())
    disp = {(s, r): p for s, r, p in json.loads((a.t740 / 'DISPATCH.json').read_bytes())}
    fill = json.loads(fraw)
    need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'] and fill['dispatch_overrides'] == [], 'fill format')
    caps = {(p, c): ch['rank'] for p, r in rec.items() for c, ch in enumerate(r['idle_children'])}
    AX = {(p, c): [int(v) for v in ch['orthogonal_axes']] for p, r in rec.items() for c, ch in enumerate(r['idle_children'])}
    TR = {(p, c): int(ch['translation_after']) for p, r in rec.items() for c, ch in enumerate(r['idle_children'])}
    PT = {p: [int(s[k]) for s in rc['stage_alignment'] for k in ('entry_Y', 'exit_Y', 'entry_X', 'exit_X')] + [int(rc['terminal_Y_translation'])] for p, rc in rec.items()}
    used, top = Counter(), Counter()
    for time, helper, rep, child, port, offset in fill['rows']:
        s, r = order[time]; w = prov[disp[s, r]]['widths'][helper]
        used[rep, child, port] += w; top[rep, child, port] = max(top[rep, child, port], offset + w)
    need(all(used[k] == top[k] for k in used), 'compact helper prefixes')
    groups = []
    for rep in range(T):
        for p in range(112):
            kids = [[c, used[rep, c, p]] for c in range(len(rec[p]['idle_children'])) if caps[p, c] - used[rep, c, p] > 0]
            groups.append([rep, p, kids])
    idle = Counter(caps[p, c] - u for _, p, kids in groups for c, u in kids)
    need(dict(idle) == IDLE_PR3148, 'idle bill equals PR3148')

    def legal(v, p, c, d, axes_d):
        return all(dot(v, x) == 0 for x in axes_d) and all(dot(v, x) == 0 for x in PT[p]) and dot(v, TR[p, c]) == 0 and dot(v, TR[p, d]) == 0

    def solve(p, kids):
        rank = {c: caps[p, c] - u for c, u in kids}; axes = {c: AX[p, c][u:caps[p, c]] for c, u in kids}
        hosted = {c: u > 0 for c, u in kids}; role = {c: None for c, _ in kids}; moves = []
        for c in sorted([c for c, u in kids if u > 0], key=lambda c: (rank[c], c)):
            for v in list(axes[c]):
                best = None
                for d in sorted([d for d, _ in kids if not hosted[d] and role[d] != 'D' and d != c and rank[d] < 51], key=lambda d: (-rank[d], d)):
                    if rank[d] < rank[c] - 1: break
                    if legal(v, p, c, d, axes[d]): best = d; break
                if best is None or Hf(rank[c] - 1) + Hf(rank[best] + 1) - Hf(rank[c]) - Hf(rank[best]) >= 0: continue
                axes[c].remove(v); axes[best].append(v); rank[c] -= 1; rank[best] += 1
                role[c] = 'D'; role[best] = 'R'; moves.append([c, best, v])
        free = [c for c, u in kids if u == 0 and role[c] is None and caps[p, c] == 48]
        if len(free) >= 2:
            MV = {(d, r): [v for v in axes[d] if legal(v, p, d, r, axes[r])] for d in free for r in free if d != r}
            best = [len(free) * Hf(48), []]
            def match(c, leaves):
                opts = [MV[c, l] for l in leaves]
                if any(len(o) < 3 for o in opts): return None
                def go(k, usedax):
                    if k == len(leaves): return []
                    for trip in itertools.combinations([v for v in opts[k] if v not in usedax], 3):
                        rest = go(k + 1, usedax | set(trip))
                        if rest is not None: return [(c, leaves[k], list(trip))] + rest
                    return None
                return go(0, set())
            def assign(i, roles):
                if i == len(free):
                    leaves = defaultdict(list)
                    for c in free:
                        if isinstance(roles[c], tuple): leaves[roles[c][1]].append(c)
                    cents = [c for c in free if roles[c] == 'c']
                    if any(not leaves[c] for c in cents) or any(roles[x] != 'c' for x in leaves): return
                    mv = []
                    for c in cents:
                        m = match(c, leaves[c])
                        if m is None: return
                        mv += m
                    rk = [48 - 3 * len(leaves[c]) if roles[c] == 'c' else 51 if isinstance(roles[c], tuple) else 48 for c in free]
                    cost = sum(Hf(x) for x in rk)
                    if cost < best[0] - 1e-12: best[0], best[1] = cost, mv
                    return
                c = free[i]
                for opt in ['n', 'c'] + [('l', d) for d in free if d != c]:
                    roles[c] = opt; assign(i + 1, roles)
                del roles[c]
            assign(0, {})
            for c, l, trip in best[1]:
                for v in trip:
                    axes[c].remove(v); axes[l].append(v); rank[c] -= 1; rank[l] += 1; moves.append([c, l, v])
        return moves, rank

    cache, moves, final = {}, [], Counter()
    for rep, p, kids in groups:
        key = (p, tuple(map(tuple, kids)))
        if key not in cache: cache[key] = solve(p, kids)
        mv, rank = cache[key]
        moves += [[rep, p] + m for m in mv]
        final.update(r for r in rank.values() if r)
    prof = Counter({r: n * 9 * T for r, n in LOCAL.items()}); prof.update(final); prof = dict(sorted(prof.items()))
    need(sum(r * n for r, n in prof.items()) == 65088 * T and 73 * 73 > 2 * max(prof) ** 2, 'mass and halving')
    lo, hi = root(prof)
    C = min(Q(math.floor(lo * 10 ** 24), 10 ** 24), BIT)
    kappa = C - Q(1, 10 ** 46) - Q(1, 10 ** 70)
    need(kappa > PR3184_KAPPA > PR3148_KAPPA, 'gates')
    (HERE / 'BINS.json.gz').write_bytes(pgz(dict(T=T, columns=['replica', 'port', [['child', 'used']]], groups=[g for g in groups if g[2]])))
    (HERE / 'MOVES.json.gz').write_bytes(pgz(dict(columns=['replica', 'port', 'donor_child', 'receiver_child', 'axis'], moves=moves)))
    donors = Counter();
    res = dict(status='PASS_IDLE_REMAINDER_DONOR_EXCHANGES_T740', T=T, axis_moves=len(moves),
               donor_children=len({(m[0], m[1], m[2]) for m in moves}), receiver_children=len({(m[0], m[1], m[3]) for m in moves}),
               idle_before={str(k): v for k, v in IDLE_PR3148.items()}, idle_after={str(k): v for k, v in sorted(final.items())},
               profile={str(k): v for k, v in prof.items()}, complex_root=[str(lo), str(hi)],
               complex_root_decimal=f'{lo.numerator * 10**25 // lo.denominator}e-25', bit=str(BIT), binding='bit' if BIT < lo else 'complex',
               kappa=str(kappa), kappa_decimal='0.0017334270395898442347489999999999999999999998999999999999999999999999', gain_over_pr3184=str(kappa - PR3184_KAPPA), gain_over_pr3148=str(kappa - PR3148_KAPPA),
               max_child_rank=max(prof), halving=[5329, 2 * max(prof) ** 2])
    (HERE / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
    print('PASS', float(lo), res['binding'], float(kappa), float(kappa - PR3184_KAPPA), len(moves))


if __name__ == '__main__':
    main()
