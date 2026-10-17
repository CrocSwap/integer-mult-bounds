#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent verifier for the idle rank-48 star exchanges on PR3148's T740 fill.

Does not import build.py.  From the committed IDLE-48-BINS / STAR-MOVES, the
pinned DATA-PHASES recipe and PR3148's complete paid profile it re-derives:
every moved axis's commuting rule, disjointness of stars and axes, orthonormal
final axis sets, unchanged per-group axis multisets (hence each group's Z4 phase
polynomial), the rank cap 51 and halving guard, the complete changed profile and
rank mass, and an exact rational root bracket with its own interval arithmetic.
Optional --fill re-derives IDLE-48-BINS from PR3148's materialized fill.
Mutation controls must all be rejected.
"""
import argparse, copy, gzip, hashlib, json, sys
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

PKG = Path(__file__).resolve().parent
PHASES = PKG.parents[1] / 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
PHASES_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
FILL_PAYLOAD_SHA = '8f4d6965ba573ff2b71fd7bf6b552643e086739d90bd73c55889502077638e00'
T = 740
BASE = {1: 16376940, 2: 4821840, 3: 1567431, 4: 679320, 5: 147075, 8: 53280, 48: 282569}
GATES = {
    'PR3148': F('17297774946785970118859999999999999999999998999999999999999999999999/10000000000000000000000000000000000000000000000000000000000000000000000'),
    'PR3143': F('172977608940512033423846781989357386829999999999999999999998999999999999999999999999/100000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
}


class Reject(Exception):
    pass


def req(ok, why):
    if not ok:
        raise Reject(why)


def load(p):
    b = Path(p).read_bytes()
    return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)


def parity(a, b):
    return bin(a & b).count('1') % 2


def gf2_rank(vs):
    rows = []
    for v in vs:
        for r in rows:
            v = min(v, v ^ r)
        if v:
            rows.append(v)
    return len(rows)


def check_moves(rec, bins, moves):
    groups = {(g[0], g[1]): list(g[2]) for g in bins['groups']}
    req(len(groups) == len(bins['groups']), 'duplicate group')
    req(all(set(k) <= {8, 10, 12, 13} and k == sorted(set(k)) and k for k in groups.values()), 'group children')
    req(all(0 <= r < T and 0 <= p < 112 for r, p in groups), 'group index range')
    req(sum(map(len, groups.values())) == BASE[48], 'idle rank-48 count')
    per = defaultdict(list)
    for m in moves:
        rep, p, c, l, ax = m
        req((rep, p) in groups, 'move outside an idle group')
        req(c in groups[rep, p] and l in groups[rep, p] and c != l, 'centre/leaf must be idle children of the group')
        req(isinstance(ax, list) and len(ax) == 3 and len(set(ax)) == 3, 'exactly three distinct axes')
        per[rep, p].append((c, l, [int(v) for v in ax]))
    ranks = Counter()
    for (rep, p), kids in groups.items():
        rc = rec[p]
        axes = {c: [int(v) for v in rc['idle_children'][c]['orthogonal_axes']] for c in kids}
        for c in kids:
            req(rc['idle_children'][c]['rank'] == 48 and len(axes[c]) == 48, 'rank-48 source child')
        ys = {int(s['entry_Y']) for s in rc['stage_alignment']} | {int(s['exit_Y']) for s in rc['stage_alignment']} | {int(rc['terminal_Y_translation'])}
        xs = {int(s['entry_X']) for s in rc['stage_alignment']} | {int(s['exit_X']) for s in rc['stage_alignment']}
        mv = per.get((rep, p), [])
        centres = {c for c, _, _ in mv}; leaves = [l for _, l, _ in mv]
        req(len(leaves) == len(set(leaves)), 'leaf reused')
        req(not centres & set(leaves), 'centre is also a leaf')
        seen = set()
        final = {c: list(axes[c]) for c in kids}
        for c, l, ax in mv:
            trans = {int(rc['idle_children'][c]['translation_after']), int(rc['idle_children'][l]['translation_after'])}
            for v in ax:
                req((c, v) not in seen, 'axis moved twice')
                seen.add((c, v))
                req(v in axes[c], 'foreign axis')
                req(all(parity(v, x) == 0 for x in axes[l]), 'axis does not commute with leaf axes')
                req(all(parity(v, x) == 0 for x in ys | xs | trans), 'axis does not commute with stage/terminal translations')
                final[c].remove(v); final[l].append(v)
        for c in kids:
            fs = final[c]
            req(len(fs) <= 51, 'rank above 51')
            req(all(parity(v, v) == 1 for v in fs), 'unit axis')
            req(all(parity(a, b) == 0 for i, a in enumerate(fs) for b in fs[i + 1:]), 'final axes orthogonal')
            req(gf2_rank(fs) == len(fs), 'independent final axes')
            ranks[len(fs)] += 1
        req(sorted(v for c in kids for v in final[c]) == sorted(v for c in kids for v in axes[c]), 'group axis multiset unchanged')
    return ranks


# -------- independent exact moment: directed rounding at 10^-72 --------
Q72 = 10 ** 72


def rd(x):
    return F(x.numerator * Q72 // x.denominator, Q72)


def ru(x):
    return F(-((-x.numerator * Q72) // x.denominator), Q72)


def log_box(y):
    """[lo, hi] for ln(y), y rational >= 1, argument reduction by 2 then atanh series."""
    k = 0
    while y >= 2:
        y = y / 2; k += 1
    def atanh2(z, n):
        acc, pw = F(0), z
        for j in range(n):
            acc += pw / (2 * j + 1); pw *= z * z
        return 2 * acc, 2 * pw / ((2 * n + 1) * (1 - z * z))
    a, ea = atanh2((y - 1) / (y + 1), 90)
    l2, e2 = atanh2(F(1, 3), 130)
    return rd(a + k * l2), ru(a + ea + k * (l2 + e2))


def exp_box(x0, x1):
    def taylor(x):
        s, t = F(1), F(1)
        for n in range(1, 34):
            t = t * x / n; s += t
        return s, t * x / 34 * 3  # Lagrange tail, 0 <= x <= 1
    a, _ = taylor(x0); b, e = taylor(x1)
    return rd(a), ru(b + e)


def moment_box(profile, b):
    W = 896 * T; lo = hi = F(0)
    for r, n in sorted(profile.items()):
        L0, L1 = log_box(F(73, r))
        e0, e1 = exp_box(b * L0, b * L1)
        lo += n * r * e0; hi += n * r * e1
    return lo / (73 * W), hi / (73 * W)


def verify_root(profile, root):
    lo, hi = F(root[0]), F(root[1])
    req(hi - lo == F(1, 10 ** 25), 'root bracket width 1e-25')
    req(moment_box(profile, lo)[1] < 1, 'moment < 1 at lower endpoint')
    req(moment_box(profile, hi)[0] > 1, 'moment > 1 at upper endpoint')
    return lo


def run(rec, bins, moves, result):
    ranks = check_moves(rec, bins, moves)
    prof = Counter(BASE); del prof[48]; prof.update(ranks)
    prof = dict(sorted(prof.items()))
    req({str(k): v for k, v in prof.items()} == result['profile'], 'declared profile')
    req(sum(r * n for r, n in prof.items()) == 65088 * T, 'complete rank mass 65088*T')
    req(73 * 73 > 2 * max(prof) ** 2 and max(prof) == 51, 'halving guard 5329 > 5202')
    lo = verify_root(prof, result['root'])
    kappa = F(lo.numerator * 10 ** 24 // lo.denominator, 10 ** 24) - F(1, 10 ** 46) - F(1, 10 ** 70)
    req(kappa == F(result['kappa']), 'headline kappa')
    for name, g in GATES.items():
        req(kappa > g, 'kappa must exceed ' + name)
    return prof, kappa


def controls(rec, bins, moves, result):
    rej = {}
    mv = moves['moves']
    rep, p, c, l, ax = mv[0]
    rc = rec[p]
    bad = [int(v) for v in rc['idle_children'][c]['orthogonal_axes'] if int(v) not in ax
           and any(parity(int(v), int(x)) for x in rc['idle_children'][l]['orthogonal_axes'])]
    def m(f):
        x = copy.deepcopy(mv); f(x); return x
    cases = {
        'non_commuting_axis': m(lambda x: x[0][4].__setitem__(0, bad[0])),
        'axis_moved_twice': m(lambda x: x.append([rep, p, c, next(k for k in [8, 10, 12, 13] if k not in (c, l)), list(ax)])),
        'reused_leaf': m(lambda x: x.append(list(x[0]))),
        'foreign_axis': m(lambda x: x[0][4].__setitem__(0, 1 << 80)),
        'centre_is_leaf': m(lambda x: x.append([rep, p, l, c, [int(v) for v in rc['idle_children'][l]['orthogonal_axes']][:3]])),
        'hosted_child': m(lambda x: x.__setitem__(0, [rep, p, c, next(k for k in [8, 10, 12, 13] if k not in dict.fromkeys(
            {(g[0], g[1]): g[2] for g in bins['groups']}[rep, p])) if len({(g[0], g[1]): g[2] for g in bins['groups']}[rep, p]) < 4 else 99, ax])),
        'two_axes_only': m(lambda x: x[0].__setitem__(4, ax[:2])),
    }
    for name, x in cases.items():
        try:
            run(rec, bins, x, result)
        except Reject as e:
            rej[name] = str(e)
        else:
            raise SystemExit('mutation accepted: ' + name)
    r2 = copy.deepcopy(result); r2['profile']['51'] += 1; r2['profile']['48'] -= 1
    try: run(rec, bins, mv, r2)
    except Reject as e: rej['wrong_profile'] = str(e)
    else: raise SystemExit('mutation accepted: wrong_profile')
    r3 = copy.deepcopy(result); lo = F(result['root'][0]) + F(1, 10 ** 25)
    r3['root'] = [str(lo), str(lo + F(1, 10 ** 25))]
    try: run(rec, bins, mv, r3)
    except Reject as e: rej['next_root_grid'] = str(e)
    else: raise SystemExit('mutation accepted: next_root_grid')
    return rej


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fill', type=Path, help="optional PR3148 COMPOSED-FILL.json.gz to rebind IDLE-48-BINS")
    ap.add_argument('--write', action='store_true', help='rewrite the committed AUDIT.json receipt')
    a = ap.parse_args()
    if not __debug__:
        raise SystemExit('assertions required')
    raw = PHASES.read_bytes()
    req(hashlib.sha256(raw).hexdigest() == PHASES_SHA, 'DATA-PHASES pin')
    rec = {r['port']: r for r in json.loads(raw)['recipes']}
    bins = load(PKG / 'IDLE-48-BINS.json.gz'); moves = load(PKG / 'STAR-MOVES.json.gz'); result = load(PKG / 'RESULT.json')
    req(bins['T'] == T and bins['fill_payload_sha256'] == FILL_PAYLOAD_SHA, 'bins provenance')
    rebound = False
    if a.fill:
        data = gzip.decompress(a.fill.read_bytes())
        req(hashlib.sha256(data).hexdigest() == FILL_PAYLOAD_SHA, 'PR3148 fill payload')
        touched = {(row[2], row[3], row[4]) for row in json.loads(data)['rows']}
        derived = [[r, p, [c for c in (8, 10, 12, 13) if (r, c, p) not in touched]] for r in range(T) for p in range(112)]
        req([g for g in derived if g[2]] == bins['groups'], 'IDLE-48-BINS equals untouched capacity-48 bins of the fill')
        rebound = True
    prof, kappa = run(rec, bins, moves['moves'], result)
    rej = controls(rec, bins, moves, result)
    out = dict(status='PASS_IDLE48_STAR_EXCHANGE_AUDIT', moves=len(moves['moves']), profile={str(k): v for k, v in prof.items()},
               kappa=str(kappa), gain_over_pr3148=str(kappa - GATES['PR3148']), fill_rebound=rebound,
               rejected_controls=rej)
    if a.write: (PKG / 'AUDIT.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    else:
        strip = lambda d: {k: v for k, v in d.items() if k != 'fill_rebound'}
        req(strip(load(PKG / 'AUDIT.json')) == strip(json.loads(json.dumps(out))), 'committed AUDIT.json receipt')
    print('PASS_IDLE48_STAR_EXCHANGE_AUDIT moves=%d controls=%d kappa=%s' % (len(moves['moves']), len(rej), float(kappa)))


if __name__ == '__main__':
    try:
        main()
    except Reject as e:
        raise SystemExit('FAIL: ' + str(e))
