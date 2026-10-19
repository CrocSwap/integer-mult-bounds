#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Hosted frame selection on PR3148's T740 fill of PR3133's words, stacked on PR3939 (pooled R438 bit).

New hypothesis: a bin hosting `used` helper cells may map those cells to ANY `used`-subset of its recipe frame;
the recipe order is not binding.  PR3190..PR3934 fixed the hosted cells to the recipe prefix [0, used) and the idle
remainder to the suffix [used, cap).  Here, per hosted bin, the frame is reordered so that the (cap - used) axes most
able to move (commuting with the stage and terminal translations and the bin's own terminal translation, then legal
toward the most children of the group) form the idle remainder; the hosted cells take the rest.  Everything after
that is PR3934's pipeline (exact phase 1, star phase 2, greedy phase 3, hosted receivers phase 5) with every move
still obeying PR1252's commuting rule, role exclusivity and the rank-51 cap.  A hosted receiver never donates, so its
legality is against its whole recipe frame, independent of the selection.

Lineage notes kept from the stacked builds: phase 1 is OpenCode's (Space bunny free) exact per-group search; the
greedy, star and hosted-receiver phases are PR3200 / PR3184 / PR3934.
"""
import argparse, gzip, hashlib, itertools, json, math
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
import os, sys
RELAY = os.environ.get('RELAY') is not None  # phase 4 found no relay moves on this fill; off by default
import random
TRIALS = int(os.environ.get('TRIALS', '1'))
FSEL = os.environ.get('NOFSEL') is None
HOSTED_RECV = os.environ.get('NOHOSTED') is None
P5IN = os.environ.get('P5IN') is not None
ITER = int(os.environ.get('ITER', '1'))
SPAN = os.environ.get('SPAN') is not None; SPANSTAT = [0]; DIAG = Counter()
NOEXCL = os.environ.get('NOEXCL') is not None
P5TRIALS = int(os.environ.get('P5TRIALS', '1')); P5TOP = int(os.environ.get('P5TOP', '3'))
PHASES = HERE.parents[1] / 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
PIN = dict(phases='c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
           fill_payload='8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00',
           order='927226d702bf3cada076f4c459da9063c0df7e7154a62955cf75c40cf30215b9',
           dispatch='90edc935320dd6264e98dc735d868df3c95f5901c70d7d96171001fcb295cce0',
           providers='52eb0d85caa7b2d4a93acdf5011f52b793f61ddca86235fb03cd9a09397ad4cd')
T = 740
LOCAL = {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8}
IDLE_PR3148 = {1: 173160, 3: 48951, 5: 13875, 48: 282569}
BIT = Q('1734900431583947157341/1000000000000000000000000')  # pooled R438 bit endpoint (research/rank7-pooled-r438-bit)   # R438 bit endpoint, research/r438-native-rehost CERTIFICATE.json
PR3148_KAPPA = Q('0.0017297774946785970118859999999999999999999998999999999999999999999999')
PR3198_KAPPA = Q('0.0017347705571115131604949999999999999999999998999999999999999999999999')
PR3939_KAPPA = Q('0.0017348651784727109982329999999999999999999998999999999999999999999999')
PR3251_KAPPA = Q('0.0017348157703850985634839999999999999999999998999999999999999999999999')
PR3200_KAPPA = Q('0.0017348070217261275520339999999999999999999998999999999999999999999999')
PR3184_KAPPA = Q('0.0017301890612338507600949999999999999999999998999999999999999999999999')


def need(ok, why):
    if not ok: raise SystemExit('FAIL: ' + why)


def sha(b): return hashlib.sha256(b).hexdigest()
def dot(a, b): return (a & b).bit_count() & 1
def Hf(r): return 0.0 if r == 0 else r * (73.0 / r) ** 0.00173

def f2solve(rows, k):
    # rows: list of (mask over k unknowns, rhs bit); returns (particular, nullbasis) or None
    piv = []  # list of (col, mask, rhs)
    for m, r in rows:
        for c, pm, pr in piv:
            if m >> c & 1: m ^= pm; r ^= pr
        if m == 0:
            if r: return None
            continue
        c = m.bit_length() - 1
        piv2 = []
        for c2, pm, pr in piv:
            if pm >> c & 1: pm ^= m; pr ^= r
            piv2.append((c2, pm, pr))
        piv = piv2 + [(c, m, r)]
    pc = {c for c, _, _ in piv}
    part = 0
    for c, m, r in piv:
        if r: part |= 1 << c
    null = []
    for f in range(k):
        if f in pc: continue
        v = 1 << f
        for c, m, r in piv:
            if m >> f & 1: v |= 1 << c
        null.append(v)
    return part, null


def onb(basis):
    # orthonormal basis (standard F2 form) of span(basis); basis vectors are ints; returns list or None
    W = [b for b in basis if b]
    out = []
    while W:
        u = None
        for i, b in enumerate(W):
            if dot(b, b):
                rest = [w ^ (u2 if dot(w, b) else 0) for w in W[:i] + W[i + 1:] for u2 in [b]]
                # need remaining space non-alternating (or empty) after reduction
                rr = [x for x in rest if x]
                if not rr or any(dot(x, x) for x in rr) or len(rr) == 0:
                    u = b; W = rr; break
        if u is None: return None
        out.append(u)
        # re-reduce W to a basis (drop dependents)
        red = []
        for w in W:
            for r in red:
                hb = r.bit_length() - 1
                if w >> hb & 1: w ^= r
            if w: red.append(w)
        W = red
    return out


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
        FR = {}
        for c, u in kids:
            fr = list(AX[p, c][:caps[p, c]])
            if FSEL and u > 0:
                full = {d: AX[p, d][:caps[p, d]] for d, _ in kids}
                def score(v):
                    lv = all(dot(v, x) == 0 for x in PT[p]) and dot(v, TR[p, c]) == 0
                    nr = sum(1 for d, ud in kids if d != c and legal(v, p, c, d, [x for x in full[d] if x != v]))
                    return (lv, nr)
                order = sorted(range(len(fr)), key=lambda i: (score(fr[i]), i))   # ascending: least movable first
                fr = [fr[i] for i in order]
            FR[c] = fr
        rank = {c: caps[p, c] - u for c, u in kids}; axes = {c: FR[c][u:caps[p, c]] for c, u in kids}
        hosted = {c: u > 0 for c, u in kids}; role = {c: None for c, _ in kids}; moves = []
        donors = sorted([c for c, u in kids if u > 0], key=lambda c: (rank[c], c))
        recv = [d for d, u in kids if u == 0]
        items = [(c, v) for c in donors for v in axes[c]]
        STARS = [True]
        r0 = {c: rank[c] for c, _ in kids}
        memo = {}
        def p5(axes, rank, role, moves):
            prefix = {c: FR[c][:u] for c, u in kids}
            gave = {m[0] for m in moves}; got = {m[1] for m in moves}
            while True:
                best = None
                for c, u in kids:
                    if role[c] == 'R' or rank[c] == 0 or c in got: continue
                    for d, ud in kids:
                        if d == c or role[d] == 'D' or d in gave or rank[d] >= 51 or rank[d] < rank[c]: continue
                        g = Hf(rank[c] - 1) + Hf(rank[d] + 1) - Hf(rank[c]) - Hf(rank[d])
                        if g >= -1e-12 or (best is not None and g >= best[0]): continue
                        for v in axes[c]:
                            if legal(v, p, c, d, prefix[d] + axes[d]): best = (g, c, d, v); break
                if best is None: break
                g, c, d, v = best
                axes[c].remove(v); axes[d].append(v); rank[c] -= 1; rank[d] += 1; role[c] = 'D'; role[d] = 'R'; moves.append([c, d, v]); gave.add(c); got.add(d)
            return rank
        def dfs2(i, recvd, cnt):
            # exact search: state = (item index, axes received per receiver, axes moved per donor); terminal cost runs
            # phases 2 (optional) and 3 on the resulting state, so phase 1 is chosen for the final sum of Hf(rank)
            key = (i, recvd, cnt)
            if key in memo: return memo[key]
            if i == len(items):
                rk = dict(r0)
                for k, c in enumerate(donors): rk[c] -= cnt[k]
                for o, d in enumerate(recv): rk[d] += len(recvd[o])
                ax2 = {c: list(axes[c]) for c in axes}
                for o, d in enumerate(recv): ax2[d] = ax2[d] + sorted(recvd[o])
                ro2 = {c: role[c] for c in role}
                for k, c in enumerate(donors):
                    if cnt[k]: ro2[c] = 'D'
                for o, d in enumerate(recv):
                    if recvd[o]: ro2[d] = 'R'
                best_t = None
                for st in (True, False):
                    mv2, rk2, ax3, ro3 = rest({c: list(x) for c, x in ax2.items()}, dict(rk), dict(ro2), [], st)
                    if P5IN: rk2 = p5(ax3, dict(rk2), dict(ro3), [[c, None, 0] for c in donors if ro2[c] == 'D'] + [[None, d, 0] for d in recv if ro2[d] == 'R'] + mv2)
                    cst = sum(Hf(x) for x in rk2.values())
                    if best_t is None or cst < best_t[0] - 1e-12: best_t = (cst, st)
                memo[key] = (best_t[0], (best_t[1],))
                return memo[key]
            c, v = items[i]; kd = donors.index(c)
            best = None
            for o in [None] + list(range(len(recv))):
                if o is None: nxt, nc = recvd, cnt
                else:
                    d = recv[o]
                    if r0[d] + len(recvd[o]) >= 51: continue
                    if not legal(v, p, c, d, list(axes[d]) + list(recvd[o])): continue
                    nxt = recvd[:o] + (recvd[o] | frozenset([v]),) + recvd[o + 1:]
                    nc = cnt[:kd] + (cnt[kd] + 1,) + cnt[kd + 1:]
                sub = dfs2(i + 1, nxt, nc)
                if best is None or sub[0] < best[0] - 1e-12: best = (sub[0], (o,) + sub[1])
            memo[key] = best
            return best
        def rest(axes, rank, role, moves, stars=True, multi=False):
            free = [c for c, u in kids if u == 0 and role[c] is None and caps[p, c] == 48]
            if stars and len(free) >= 2:
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
            un = [c for c, u in kids if u == 0]
            start = ({c: list(x) for c, x in axes.items()}, dict(rank), dict(role), list(moves))
            bestrun = None
            for trial in range(TRIALS if (multi and len(un) >= 2) else 1):
                rng = random.Random(1000003 * trial + p)
                axes, rank, role, moves = {c: list(x) for c, x in start[0].items()}, dict(start[1]), dict(start[2]), list(start[3])
                while True:
                    cands = []
                    for c in un:
                        if role[c] == 'R' or rank[c] == 0: continue
                        for d in un:
                            if d == c or role[d] == 'D' or rank[d] >= 51 or rank[d] < rank[c]: continue
                            g = Hf(rank[c] - 1) + Hf(rank[d] + 1) - Hf(rank[c]) - Hf(rank[d])
                            if g >= 0: continue
                            legal_v = [v for v in axes[c] if legal(v, p, c, d, axes[d])]
                            if legal_v: cands.append((g, c, d, legal_v[0] if trial == 0 else rng.choice(legal_v)))
                    if not cands: break
                    cands.sort(key=lambda x: (x[0], x[1], x[2]))
                    g, c, d, v = cands[0] if trial == 0 else rng.choice(cands[:3])
                    axes[c].remove(v); axes[d].append(v); rank[c] -= 1; rank[d] += 1; role[c] = 'D'; role[d] = 'R'; moves.append([c, d, v])
                cost = sum(Hf(x) for x in rank.values())
                if bestrun is None or cost < bestrun[0] - 1e-12: bestrun = (cost, moves, rank, axes, role)
            return bestrun[1], bestrun[2], bestrun[3], bestrun[4]
        if items:
            _, choices = dfs2(0, tuple(frozenset() for _ in recv), tuple(0 for _ in donors))
            STARS[0] = choices[-1]; choices = choices[:-1]
            for (c, v), o in zip(items, choices):
                if o is None: continue
                d = recv[o]
                axes[c].remove(v); axes[d].append(v); rank[c] -= 1; rank[d] += 1
                role[c] = 'D'; role[d] = 'R'; moves.append([c, d, v])
        moves, rank, axes, role = rest(axes, rank, role, moves, STARS[0], True)
        # phase 4 (new): relay moves.  A remainder axis v blocked at an unhosted receiver B only by one of B's own
        # original axes w is placed as  w: B -> C, then v: h -> B  (both PR1252-rule moves); B keeps its rank.
        if RELAY:
            orig = {c: set(FR[c][u:caps[p, c]]) for c, u in kids}
            un = [c for c, u in kids if u == 0]
            while True:
                best = None
                for h in [c for c, u in kids if rank[c] > 0 and role[c] != 'R']:
                    for v in axes[h]:
                        if not all(dot(v, x) == 0 for x in PT[p]) or dot(v, TR[p, h]): continue
                        for B in un:
                            if B == h or dot(v, TR[p, B]): continue
                            S = [w for w in axes[B] if dot(v, w)]
                            if len(S) != 1 or S[0] not in orig[B]: continue
                            w = S[0]
                            for C in un:
                                if C in (B, h) or role[C] == 'D' or rank[C] >= 51: continue
                                g = Hf(rank[h] - 1) - Hf(rank[h]) + Hf(rank[C] + 1) - Hf(rank[C])
                                if g >= -1e-12 or (best is not None and g >= best[0]): continue
                                if legal(w, p, B, C, axes[C]): best = (g, h, v, B, w, C)
                if best is None: break
                g, h, v, B, w, C = best
                axes[B].remove(w); axes[C].append(w); rank[C] += 1; moves.append([B, C, w])
                axes[h].remove(v); axes[B].append(v); rank[h] -= 1; moves.append([h, B, v])
                role[C] = 'R'; role[h] = 'D'
        # phase 5 (new): hosted receivers.  A remainder axis may also move into the idle remainder of another
        # partially hosted bin of the same (replica, port), when it commutes with that bin's FULL recipe frame
        # (hosted prefix and current remainder), the stage translations and both terminal translations.
        for _it in range(ITER if HOSTED_RECV else 0):
          if _it:
            n0 = len(moves); moves, rank, axes, role = rest(axes, rank, role, moves, False, False)
            if len(moves) == n0 and _it > 1: break
          if True:
            prefix = {c: FR[c][:u] for c, u in kids}
            st0 = ({c: list(x) for c, x in axes.items()}, dict(rank), dict(role), list(moves))
            bestrun = None
            for trial in range(P5TRIALS):
                rng = random.Random(7919 * trial + p)
                axes, rank, role, moves = {c: list(x) for c, x in st0[0].items()}, dict(st0[1]), dict(st0[2]), list(st0[3])
                gave = {m[0] for m in moves}; got = {m[1] for m in moves}; moved = {m[2] for m in moves}
                while True:
                    cands = []
                    for c, u in kids:
                        if rank[c] == 0 or (not NOEXCL and (role[c] == 'R' or c in got)): continue
                        for d, ud in kids:
                            if d == c or rank[d] >= 51 or rank[d] < rank[c] or (not NOEXCL and (role[d] == 'D' or d in gave)): continue
                            g = Hf(rank[c] - 1) + Hf(rank[d] + 1) - Hf(rank[c]) - Hf(rank[d])
                            if g >= -1e-12: continue
                            lv = [v for v in axes[c] if (not NOEXCL or v not in moved) and legal(v, p, c, d, prefix[d] + axes[d])]
                            if lv: cands.append((g, c, d, lv[0] if trial == 0 else rng.choice(lv)))
                    if not cands: break
                    cands.sort(key=lambda x: x[0])
                    g, c, d, v = cands[0] if trial == 0 else rng.choice(cands[:P5TOP])
                    axes[c].remove(v); axes[d].append(v); rank[c] -= 1; rank[d] += 1; role[c] = 'D'; role[d] = 'R'; moves.append([c, d, v]); gave.add(c); got.add(d); moved.add(v)
                cost = sum(Hf(x) for x in rank.values())
                if bestrun is None or cost < bestrun[0] - 1e-12: bestrun = (cost, moves, rank, axes, role)
            _, moves, rank, axes, role = bestrun
        if SPAN:
            prefix = {c: FR[c][:u] for c, u in kids}
            gave = {m[0] for m in moves}; got = {m[1] for m in moves}
            def spanv(c, d):
                R = axes[c]; k = len(R)
                cons = list(PT[p]) + [TR[p, c], TR[p, d]] + prefix[d] + axes[d]
                rows = [(sum(1 << i for i, r in enumerate(R) if dot(r, x)), 0) for x in cons] + [((1 << k) - 1, 1)]
                sol = f2solve(rows, k)
                if sol is None: return None
                a, null = sol; full = (1 << k) - 1
                if a == full and k > 1:
                    if not null: return None
                    a ^= null[0]
                v = 0
                for i, r in enumerate(R):
                    if a >> i & 1: v ^= r
                if k == 1: return v, []
                comp = [r for i, r in enumerate(R) if not dot(r, v)] + []
                # basis of R cap v-perp: reduce
                odd = [r for r in R if dot(r, v)]
                comp += [odd[0] ^ o for o in odd[1:]]
                nb = onb(comp)
                if nb is None or len(nb) != k - 1: return None
                return v, nb
            while True:
                best = None
                for c, u in kids:
                    if rank[c] == 0 or role[c] == 'R' or c in got: continue
                    for d, ud in kids:
                        if d == c or role[d] == 'D' or d in gave or rank[d] >= 51 or rank[d] < rank[c]: continue
                        g = Hf(rank[c] - 1) + Hf(rank[d] + 1) - Hf(rank[c]) - Hf(rank[d])
                        if g >= -1e-12 or (best is not None and g >= best[0]): continue
                        r = spanv(c, d)
                        if r is not None: best = (g, c, d, r)
                if best is None:
                    for c, u in kids:
                        if rank[c] == 0 or role[c] == 'R' or c in got: continue
                        for d, ud in kids:
                            if d == c or role[d] == 'D' or d in gave or rank[d] >= 51 or rank[d] < rank[c]: continue
                            DIAG[(rank[c], 'cand')] += 1
                    break
                g, c, d, (v, nb) = best
                axes[c] = nb; axes[d].append(v); rank[c] -= 1; rank[d] += 1; role[c] = 'D'; role[d] = 'R'; moves.append([c, d, v]); gave.add(c); got.add(d); SPANSTAT[0] += 1
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
    print('complex_lo', float(lo), 'moves', len(moves), 'span', SPANSTAT[0], sorted(DIAG.items())[:30], file=sys.stderr)
    need(kappa > PR3939_KAPPA > PR3251_KAPPA > PR3200_KAPPA > PR3198_KAPPA > PR3184_KAPPA > PR3148_KAPPA, 'gates')
    (HERE / 'BINS.json.gz').write_bytes(pgz(dict(T=T, columns=['replica', 'port', [['child', 'used']]], groups=[g for g in groups if g[2]])))
    (HERE / 'MOVES.json.gz').write_bytes(pgz(dict(columns=['replica', 'port', 'donor_child', 'receiver_child', 'axis'], moves=moves)))
    donors = Counter();
    res = dict(status='PASS_IDLE_FRAME_SELECT_T740', T=T, axis_moves=len(moves),
               donor_children=len({(m[0], m[1], m[2]) for m in moves}), receiver_children=len({(m[0], m[1], m[3]) for m in moves}),
               idle_before={str(k): v for k, v in IDLE_PR3148.items()}, idle_after={str(k): v for k, v in sorted(final.items())},
               profile={str(k): v for k, v in prof.items()}, complex_root=[str(lo), str(hi)],
               complex_root_decimal=f'{lo.numerator * 10**25 // lo.denominator}e-25', bit=str(BIT), binding='bit' if BIT < lo else 'complex',
               kappa=str(kappa), kappa_decimal='0.' + str(kappa.numerator * 10 ** 70 // kappa.denominator).rjust(70, '0'), gain_over_pr3939=str(kappa - PR3939_KAPPA), gain_over_pr3939_percent=str(float((kappa - PR3939_KAPPA) / PR3939_KAPPA * 100)), gain_over_pr3251=str(kappa - PR3251_KAPPA), gain_over_pr3200=str(kappa - PR3200_KAPPA), gain_over_pr3198=str(kappa - PR3198_KAPPA), gain_over_pr3184=str(kappa - PR3184_KAPPA), gain_over_pr3148=str(kappa - PR3148_KAPPA),
               max_child_rank=max(prof), halving=[5329, 2 * max(prof) ** 2])
    (HERE / 'RESULT.json').write_text(json.dumps(res, indent=1) + '\n')
    print('PASS', float(lo), res['binding'], float(kappa), float(kappa - PR3184_KAPPA), len(moves))


if __name__ == '__main__':
    main()
