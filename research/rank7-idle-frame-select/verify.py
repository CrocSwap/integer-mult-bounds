#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent verifier (does not import build.py) for hosted frame selection on the PR3934 move classes.

Frame-selection hypothesis: a bin hosting `used` helper cells may map those cells to ANY `used`-subset of its
recipe frame (the recipe order is not binding), so its idle remainder is the complementary (cap - used)-subset.
Equivalently: a hosted donor may donate any axes of its own recipe frame, at most (cap - used) of them, and the
hosted cells occupy the remaining frame axes.  A hosted receiver keeps its entire frame (it never donates), so a
received axis must be orthogonal to the receiver's whole frame plus everything it has received.

Re-derives from BINS / MOVES / DATA-PHASES: donor axes come from the donor's own recipe frame, distinct, within the
(cap - used) idle budget; a hosted receiver must be orthogonal to its whole recipe frame;
no child both donates and receives;
every moved axis is a unit vector orthogonal to all of the receiver's axes held at that moment and
commutes with every stage entry/exit X/Y translation, the terminal Y translation and both
children's terminal translations; final ranks <= 51; per-group axis multisets unchanged; the
complete profile and rank mass; an exact complex root bracket with its own interval arithmetic;
kappa = min(floor24(complex_lower), PR589 bit) - 1e-46 - 1e-70 and its gates.
Optional --t740 rebinds BINS to PR3148's materialized fill. Mutation controls must be rejected.
"""
import argparse, copy, gzip, hashlib, json
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

PKG = Path(__file__).resolve().parent
PHASES = PKG.parents[1] / 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
T = 740
LOCAL = {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8}
IDLE = {1: 173160, 3: 48951, 5: 13875, 48: 282569}
BITCERT = PKG.parents[1] / 'research/r438-native-rehost/CERTIFICATE.json'
BIT = None  # R438 bit endpoint, re-derived from its certificate's bit profile in check_bit()
GATES = dict(PR3939=F('0.0017348651784727109982329999999999999999999998999999999999999999999999'), PR3934=F('0.0017348462641201991514749999999999999999999998999999999999999999999999'), PR3251=F('0.0017348157703850985634839999999999999999999998999999999999999999999999'), PR3200=F('0.0017348070217261275520339999999999999999999998999999999999999999999999'), PR3198=F('0.0017347705571115131604949999999999999999999998999999999999999999999999'), PR3148=F('0.0017297774946785970118859999999999999999999998999999999999999999999999'),
             PR3184=F('0.0017301890612338507600949999999999999999999998999999999999999999999999'))


class Reject(Exception): pass
def req(ok, why):
    if not ok: raise Reject(why)
def load(p):
    b = Path(p).read_bytes(); return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)
def par(a, b): return bin(a & b).count('1') & 1


def audit(rec, bins, moves):
    caps = {(p, c): ch['rank'] for p, r in rec.items() for c, ch in enumerate(r['idle_children'])}
    G = {}
    for rep, p, kids in bins['groups']:
        req((rep, p) not in G and 0 <= rep < T and p in rec, 'group key')
        G[rep, p] = {c: u for c, u in kids}
        req(all(0 <= u < caps[p, c] for c, u in kids), 'used below capacity')
    req(Counter(caps[p, c] - u for (rep, p), kids in G.items() for c, u in kids.items()) == Counter(IDLE), 'idle bill')
    trans = {}
    for p, rc in rec.items():
        trans[p] = {int(s[k]) for s in rc['stage_alignment'] for k in ('entry_X', 'exit_X', 'entry_Y', 'exit_Y')} | {int(rc['terminal_Y_translation'])}
        for c, ch in enumerate(rc['idle_children']):
            ax = [int(v) for v in ch['orthogonal_axes']]
            req(all(par(v, v) == 1 for v in ax) and all(par(a, b) == 0 for i, a in enumerate(ax) for b in ax[i + 1:]), 'recipe axes orthonormal')
    state = {}
    def cur(rep, p, c):
        k = (rep, p, c)
        if k not in state:
            u = G[rep, p][c]; fr = [int(v) for v in rec[p]['idle_children'][c]['orthogonal_axes'][:caps[p, c]]]
            req(len(fr) == caps[p, c], 'recipe frame length')
            state[k] = dict(axes=set(fr), budget=caps[p, c] - u, gave=0, got=0, role=None)
        return state[k]
    for m in moves:
        rep, p, c, d, v = m
        req((rep, p) in G and c in G[rep, p] and d in G[rep, p] and c != d, 'children of the group')
        prefix_d = [int(x) for x in rec[p]['idle_children'][d]['orthogonal_axes'][:G[rep, p][d]]]
        req(all(par(v, x) == 0 for x in prefix_d), 'axis not orthogonal to hosted receiver prefix')
        sc, sd = cur(rep, p, c), cur(rep, p, d)
        req(sc['role'] != 'R' and sd['role'] != 'D', 'child both donates and receives')
        own = set(int(x) for x in rec[p]['idle_children'][c]['orthogonal_axes'][:caps[p, c]])
        req(v in sc['axes'] and v in own, 'axis not in donor frame')
        req(sc['gave'] < sc['budget'], 'donor exceeds its idle budget (cap - used)')
        req(par(v, v) == 1 and all(par(v, x) == 0 for x in sd['axes']), 'axis not orthogonal to receiver axes')
        tc = int(rec[p]['idle_children'][c]['translation_after']); td = int(rec[p]['idle_children'][d]['translation_after'])
        req(all(par(v, x) == 0 for x in trans[p] | {tc, td}), 'axis does not commute with translations')
        sc['axes'].discard(v); sd['axes'].add(v); sc['role'] = 'D'; sd['role'] = 'R'; sc['gave'] += 1; sd['got'] += 1
        req(sd['budget'] + sd['got'] <= 51, 'rank above 51')
    final = Counter()
    for (rep, p), kids in G.items():
        for c, u in kids.items():
            st = state.get((rep, p, c))
            r = st['budget'] - st['gave'] + st['got'] if st else caps[p, c] - u
            if r: final[r] += 1
    return final


def mom(prof, b):
    Q72 = 10 ** 72
    def rd(x): return F(x.numerator * Q72 // x.denominator, Q72)
    def ru(x): return F(-((-x.numerator * Q72) // x.denominator), Q72)
    def at(z, n):
        s, p = F(0), z
        for j in range(n): s += p / (2 * j + 1); p *= z * z
        return 2 * s, 2 * p / ((2 * n + 1) * (1 - z * z))
    l2 = at(F(1, 3), 130); W = 896 * T; lo = hi = F(0)
    for r, n in sorted(prof.items()):
        y, k = F(73, r), 0
        while y >= 2: y /= 2; k += 1
        a, e = at((y - 1) / (y + 1), 90)
        L0, L1 = rd(a + k * l2[0]), ru(a + e + k * (l2[0] + l2[1]))
        def tay(x):
            s, t = F(1), F(1)
            for j in range(1, 34): t = t * x / j; s += t
            return s, t * x / 34 * 3
        e0, _ = tay(b * L0); e1, t1 = tay(b * L1)
        lo += n * r * rd(e0); hi += n * r * ru(e1 + t1)
    return lo / (73 * W), hi / (73 * W)


def check_bit():
    """Pooled R438 bit endpoint: re-run research/rank7-pooled-r438-bit's own role audit and endpoint check."""
    import importlib.util, gzip as _gz
    pk = PKG.parent / 'rank7-pooled-r438-bit'
    spec = importlib.util.spec_from_file_location('pooled_verify', pk / 'verify.py'); pv = importlib.util.module_from_spec(spec); spec.loader.exec_module(pv)
    alloc = [tuple(t) for t in json.loads(_gz.decompress((pk / 'ALLOC-R438.json.gz').read_bytes()))]
    hosting = pv.windows(); moves = json.loads((pk / 'POOL-MOVES.json').read_text())['moves']
    p1 = pv.bitprof(pv.audit(pv.roles(alloc, hosting, moves), hosting))
    c1 = F(json.loads((pk / 'CLAIM.json').read_text())['bit_pooled'])
    req(pv.moment(p1, 64, 28416, c1, True)[1] < 1 < pv.moment(p1, 64, 28416, c1 + F(1, 10 ** 24), True)[0], 'pooled bit endpoint')
    return c1


def check_bit_r438():
    inv = json.loads(BITCERT.read_text())['pipeline']['candidate']['hosted']['invoice']
    prof = {int(k): v for k, v in inv['bit_profile'].items()}
    c, cn = F(inv['bit_lower']), F(inv['next_grid_point_rejected'])
    req(c == F(inv['bit_lower_decimal']) and cn - c == F(1, 10 ** 24) and 2 * max(prof) ** 2 < 64 ** 2, 'R438 certificate fields')
    W = 28416; N = sum(prof.values())
    def bm(b):
        lo = hi = F(0)
        for r, n in sorted(prof.items()) + [(1, F(32 * 64 * 64 * N, 10 ** 16))]:
            l0, l1 = ln64(r); e0, e1 = exbox(b * l0, b * l1); lo += n * r * e0; hi += n * r * e1
        return lo / (64 * W), hi / (64 * W)
    req(bm(c)[1] < 1 and bm(cn)[0] > 1, 'R438 bit endpoint accepted at c, rejected at c+1e-24')
    return c


def ln64(r):
    Q72 = 10 ** 72
    def at(z, n):
        s, p = F(0), z
        for j in range(n): s += p / (2 * j + 1); p *= z * z
        return 2 * s, 2 * p / ((2 * n + 1) * (1 - z * z))
    y, k = F(64, r), 0
    while y >= 2: y /= 2; k += 1
    l2 = at(F(1, 3), 130); a, e = at((y - 1) / (y + 1), 90)
    return F((a + k * l2[0]).numerator * Q72 // (a + k * l2[0]).denominator, Q72), F(-((-(a + e + k * (l2[0] + l2[1])).numerator * Q72) // (a + e + k * (l2[0] + l2[1])).denominator), Q72)


def exbox(x0, x1):
    def tay(x):
        s, t = F(1), F(1)
        for j in range(1, 34): t = t * x / j; s += t
        return s, t * x / 34 * 3
    a, _ = tay(x0); b, t = tay(x1)
    return a, b + t


def run(rec, bins, moves, result):
    final = audit(rec, bins, moves)
    prof = Counter({r: n * 9 * T for r, n in LOCAL.items()}); prof.update(final); prof = dict(sorted(prof.items()))
    req({str(k): v for k, v in prof.items()} == result['profile'], 'declared profile')
    req(sum(r * n for r, n in prof.items()) == 65088 * T, 'rank mass 65088*T')
    req(max(prof) <= 51 and 73 * 73 > 2 * max(prof) ** 2, 'halving guard')
    lo, hi = F(result['complex_root'][0]), F(result['complex_root'][1])
    req(hi - lo == F(1, 10 ** 25) and mom(prof, lo)[1] < 1 and mom(prof, hi)[0] > 1, 'complex root bracket')
    C = min(F(lo.numerator * 10 ** 24 // lo.denominator, 10 ** 24), BIT)
    req(BIT < F(lo.numerator * 10 ** 24 // lo.denominator, 10 ** 24) and C == BIT, 'bit binds: complex floor above the pooled R438 bit endpoint')
    kappa = C - F(1, 10 ** 46) - F(1, 10 ** 70)
    req(kappa == F(result['kappa']), 'headline kappa')
    for n, g in GATES.items(): req(kappa > g, 'kappa must exceed ' + n)
    return prof, kappa, lo


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--t740', type=Path)
    ap.add_argument('--providers', type=Path, default=PKG / 'PR3148-PROVIDERS.json')
    ap.add_argument('--write', action='store_true', help='rewrite the committed AUDIT.json receipt')
    a = ap.parse_args()
    if not __debug__: raise SystemExit('assertions required')
    raw = PHASES.read_bytes()
    req(hashlib.sha256(raw).hexdigest() == 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa', 'phases pin')
    rec = {r['port']: r for r in json.loads(raw)['recipes']}
    global BIT
    BIT = check_bit()
    bins, mv, result = load(PKG / 'BINS.json.gz'), load(PKG / 'MOVES.json.gz')['moves'], load(PKG / 'RESULT.json')
    rebound = False
    if a.t740:
        fraw = gzip.decompress((a.t740 / 'COMPOSED-FILL.json.gz').read_bytes())
        req(hashlib.sha256(fraw).hexdigest() == '8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00', 'fill pin')
        prov = load(a.providers); order = load(a.t740 / 'ORDER.json'); disp = {(s, r): p for s, r, p in load(a.t740 / 'DISPATCH.json')}
        used = Counter()
        for time, helper, rep, child, port, offset in json.loads(fraw)['rows']:
            s, r = order[time]; used[rep, child, port] += prov[disp[s, r]]['widths'][helper]
        caps = {(p, c): ch['rank'] for p, r in rec.items() for c, ch in enumerate(r['idle_children'])}
        derived = [[rep, p, [[c, used[rep, c, p]] for c in range(len(rec[p]['idle_children'])) if caps[p, c] - used[rep, c, p] > 0]] for rep in range(T) for p in range(112)]
        req([g for g in derived if g[2]] == bins['groups'], 'BINS equal the fill')
        rebound = True
    prof, kappa, lo = run(rec, bins, mv, result)
    rej = {}
    first_hosted = next(i for i, m in enumerate(mv) if {c: u for c, u in next(g for g in bins['groups'] if g[0] == m[0] and g[1] == m[1])[2]}[m[2]] > 0)
    rep, p, c, d, v = mv[first_hosted]
    kids = {cc: u for cc, u in next(g for g in bins['groups'] if g[0] == rep and g[1] == p)[2]}
    hosted_other = next((cc for cc, u in kids.items() if u > 0 and cc != c), None)
    gmap = {(g[0], g[1]): {cc: u for cc, u in g[2]} for g in bins['groups']}
    def find_prefix_conflict():
        # redirect one move to another hosted child of its group whose hosted prefix anticommutes with the axis
        for i, (r0, p0, c0, d0, v0) in enumerate(mv):
            for e, ue in gmap[r0, p0].items():
                if e in (c0, d0) or ue == 0: continue
                pre = [int(x) for x in rec[p0]['idle_children'][e]['orthogonal_axes']]
                if any(par(v0, y) for y in pre): return i, [r0, p0, c0, e, v0]
        raise SystemExit('no hosted-frame-conflict control found')
    hr_index, hr_bad = find_prefix_conflict()
    def find_noncommuting():
        for i, (r0, p0, c0, d0, v0) in enumerate(mv):
            trans = [int(st[k]) for st in rec[p0]['stage_alignment'] for k in ('entry_X', 'exit_X', 'entry_Y', 'exit_Y')] + [int(rec[p0]['terminal_Y_translation'])]
            for a in rec[p0]['idle_children'][c0]['orthogonal_axes']:
                a = int(a)
                dfr = [int(y) for y in rec[p0]['idle_children'][d0]['orthogonal_axes']] + [m[4] for m in mv[:i] if (m[0], m[1], m[3]) == (r0, p0, d0)]
                if a != v0 and a not in {m[4] for m in mv[:i] if (m[0], m[1], m[2]) == (r0, p0, c0)} and any(par(a, y) for y in trans) and not any(par(a, y) for y in dfr): return i, [r0, p0, c0, d0, a]
        raise SystemExit('no non-commuting control found')
    nc_index, nc_move = find_noncommuting()
    def find_over_budget():
        # add one more legal-looking donation from a hosted donor that has already used its whole idle budget
        gave = Counter((m[0], m[1], m[2]) for m in mv)
        for i, (r0, p0, c0, d0, v0) in enumerate(mv):
            k = (r0, p0, c0); u0 = gmap[r0, p0][c0]
            if u0 and gave[k] == rec[p0]['idle_children'][c0]['rank'] - u0:
                last = max(j for j, m in enumerate(mv) if (m[0], m[1], m[2]) == k)
                taken = {m[4] for m in mv if (m[0], m[1], m[2]) == k}
                for a in rec[p0]['idle_children'][c0]['orthogonal_axes']:
                    if int(a) not in taken: return last + 1, [r0, p0, c0, d0, int(a)]
        raise SystemExit('no over-budget control found')
    ob_index, ob_move = find_over_budget()
    def mut(f):
        x = copy.deepcopy(mv); f(x); return x
    cases = dict(
        hosted_frame_conflict=mut(lambda x: x.__setitem__(hr_index, hr_bad)),
        non_commuting_axis=mut(lambda x: x.__setitem__(nc_index, nc_move)),
        over_budget=mut(lambda x: x.insert(ob_index, ob_move)),
        foreign_axis=mut(lambda x: x.__setitem__(first_hosted, [rep, p, c, d, 1 << 80])),
        axis_moved_twice=mut(lambda x: x.insert(first_hosted + 1, list(x[first_hosted]))),
        receiver_donates=mut(lambda x: x.append([rep, p, d, c, v])),
        dropped_move=mut(lambda x: x.pop(first_hosted)),
    )
    for name, x in cases.items():
        try: run(rec, bins, x, result)
        except Reject as e: rej[name] = str(e)
        else: raise SystemExit('mutation accepted: ' + name)
    r2 = copy.deepcopy(result); r2['complex_root'] = [str(lo + F(1, 10 ** 25)), str(lo + F(2, 10 ** 25))]
    try: run(rec, bins, mv, r2)
    except Reject as e: rej['next_root_grid'] = str(e)
    else: raise SystemExit('mutation accepted: next_root_grid')
    r3 = copy.deepcopy(result); r3['kappa'] = str(F(result['kappa']) + F(1, 10 ** 24))
    try: run(rec, bins, mv, r3)
    except Reject as e: rej['kappa_above_bit'] = str(e)
    else: raise SystemExit('mutation accepted: kappa_above_bit')
    out = dict(status='PASS_IDLE_FRAME_SELECT_AUDIT', moves=len(mv), fill_rebound=rebound, kappa=str(kappa),
               complex_root_lower=str(lo), binding='bit' if BIT < lo else 'complex', rejected_controls=rej)
    if a.write: (PKG / 'AUDIT.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    else:
        strip = lambda d: {k: v for k, v in d.items() if k != 'fill_rebound'}
        req(strip(load(PKG / 'AUDIT.json')) == strip(json.loads(json.dumps(out))), 'committed AUDIT.json receipt')
    print('PASS_IDLE_FRAME_SELECT_AUDIT moves=%d controls=%d kappa=%s binding=%s' % (len(mv), len(rej), float(kappa), out['binding']))


if __name__ == '__main__':
    try: main()
    except Reject as e: raise SystemExit('FAIL: ' + str(e))
