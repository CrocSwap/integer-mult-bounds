#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certificate that PR2374's owner fill is optimal for the PR2322 T74 words over all whole-helper fills.

PR2374 (jeremykothe2) claims "an exact window-free-optimal owner fill" on PR2322's words. Its published leftover
idle ranks are I = {1:21978, 3:8592, 5:2552, 32:1, 48:24560} and its claimed kappa is 0.0016971949509017704...
This script audits the optimality claim by a different method and over a larger class: the bin-pattern integer
program of PR2387/PR2360 (after PR1129).

Every legal whole-helper owner fill puts each helper role whole into one idle bin (ranks 8/16/32/48, counts
49728/33152/33152/33152). So its idle remainders come from an integer pattern-count vector x >= 0 with the bin
and width-inventory row sums. The moment is linear in x for fixed a.

Steps:
  1. Re-derive PR2374's root from the local profile plus I. The PR2322 profile is recounted in PR2402; both
     providers have {1:2335, 2:512, 3:426, 4:120, 5:38, 8:8}, with dispatch 249/417. Certify it lies within 1e-15
     of the claimed kappa.
  2. At a0 = kappa_2374 + 1e-15, take an exact rational dual (y, z) that is feasible against 800-bit LOWER
     enclosures of h(r) = (r/73)^(1-a0) for all 1163 patterns. Every integer x then satisfies
         66304 mu_x(a0) >= L_loc + D + sum_p rc_p x_p,   rc_p >= 0 exact.
     If sum rc_p x_p >= T := 66304 - L_loc - D, then mu_x(a0) >= 1, so b_x <= a0.
  3. Enumerate exactly every integer x with sum rc_p x_p < T. Only patterns with rc_p < T can appear; the LP
     basis system is solved in exact rationals. Degenerate patterns (rc ~ 0) are shown to swap only
     zero-remainder patterns, so they never change the idle multiset; they enter only through integrality,
     residues mod det(B). Each surviving x is shown to have idle multiset I exactly. Its moment at a0 is then
     certified >= 66304 directly with lower enclosures.
  Conclusion: every legal whole-helper owner fill of the PR2322 words on the unchanged T74 template has
  b <= kappa_2374 + 1e-15, and I is the only idle multiset within the dual gap. The negative control repeats the
  exclusion at kappa_2374 - 1e-12, where PR2374's own fill must survive.

Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.  Credits in README.md.
Usage: python3 -I -B owner_optimum.py [--out]
"""

import argparse
import hashlib
import importlib.util
import itertools
import json
import os
import sys
import time
from collections import Counter
from fractions import Fraction

if not __debug__:
    sys.stdout.write('FAIL_T74_OWNER_OPTIMUM refusing to run under python -O\n')
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = {  # byte copies of PR2387 (this author), as vendored and pinned in PR2402
    'vendor/pr2387/ceiling_lp.py': ('48362358660f74e0e235865df3e172494c191212',
                                    '63e2d35b07342508680e20f4b60c4da888acf4c771cd9b10400c21490f1491be'),
    'vendor/pr2387/vendor/iter3/price_check.py': ('708753e7703077a8ce4311293f02e42afb801934',
                                                  '19fcfb9f4d766959c599223090142edb03998229459cff1266960ca6b7ed1e0f'),
}
CLAIMS = {  # published in the PR bodies (owner fills audited here)
    'pr2374': dict(kappa=Fraction('0.001697194950901770426594081877309541199782925447437522970580'),
                   idle={1: 21978, 3: 8592, 5: 2552, 32: 1, 48: 24560},
                   inv={4: 33, 5: 9, 7: 38, 8: 114, 9: 240},
                   profile={1: 2335, 2: 512, 3: 426, 4: 120, 5: 38, 8: 8},
                   words='PR2322 words (recounted in PR2402)'),
    'pr2435': dict(kappa=Fraction('0.001698511343697629329051733814187744630805511096704593311278'),
                   idle={1: 20824, 3: 6695, 5: 1, 48: 25302},
                   inv={4: 33, 5: 9, 7: 62, 8: 90, 9: 240},
                   profile={1: 2359, 2: 632, 3: 330, 4: 120, 5: 38, 8: 8},
                   words='PR2435 words (24 copy-buffer entrances raised; profile and inventory as published)'),
}
KAPPA_2374 = CLAIMS['pr2374']['kappa']
IDLE_2374 = CLAIMS['pr2374']['idle']
EPS = Fraction(1, 10 ** 15)


class Fail(Exception):
    pass


def need(cond, what):
    if not cond:
        raise Fail(what)


def load_lp():
    for rel, (blob, sha) in VENDOR.items():
        data = open(os.path.join(HERE, rel), 'rb').read()
        need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == blob and
             hashlib.sha256(data).hexdigest() == sha, 'vendored pin ' + rel)
    spec = importlib.util.spec_from_file_location('pr2387_ceiling_lp', os.path.join(HERE, 'vendor/pr2387/ceiling_lp.py'))
    lp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lp)
    return lp


def audit(C, P, W, name):
    claim = CLAIMS[name]
    K, I = claim['kappa'], claim['idle']
    case = 'claim_' + name
    C.CASES[case] = dict(inv=dict(claim['inv']), pg=dict(claim['profile']), pe=dict(claim['profile']))
    need(sum(claim['profile'].values()) and sum(r * n for r, n in claim['profile'].items()) == 1856 + sum(w * n for w, n in claim['inv'].items()),
         name + ': local mass = 1856 + helper widths')
    W = C.W_LIVE
    loc = C.local_counts(case)
    need(sum(r * n for r, n in I.items()) + sum(r * n for r, n in loc.items()) == 73 * W - 23680,
         name + ': idle multiset + local profile = rank mass 73 W - deficit')

    def h_up(r, a):
        if r == 0:
            return Fraction(0)
        ll, lu = P.log_enclosure(C.M, r)
        el, eu = P.exp_enclosure((a.numerator * ll) // a.denominator, P.cdiv(a.numerator * lu, a.denominator))
        return Fraction(r * eu, C.M * P.ONE)

    def wmu_idle(idle, a, upper):
        f = h_up if upper else C.h_lower
        return sum(n * f(r, a) for r, n in loc.items()) + sum(n * f(r, a) for r, n in idle.items())

    # ---- 1. PR2374's root is within 1e-15 of its claimed kappa -------------------------------------------------
    hi_a, lo_a = K + EPS, K - EPS
    need(wmu_idle(I, hi_a, False) > W and wmu_idle(I, lo_a, True) < W,
         name + ': idle multiset root is not within 1e-15 of its claimed kappa')
    out = dict(object=name + ' owner fill on the ' + claim['words'] + ': optimality over all whole-helper fills',
               root_bracket=[str(lo_a), str(hi_a)], inventory=claim['inv'], profile=claim['profile'], idle=I,
               kappa=str(K))
    print('[%s] 1. local profile + published idle multiset: root certified in kappa +- 1e-15' % name)

    def exclusion(a0, label):
        """Return (T, survivors) for the exact dual at a0."""
        _mu, sol, du = C.lp_mu_float(case, float(a0))
        y = {R: Fraction(du[i]) for i, R in enumerate(C.NB)}
        z = {w: Fraction(du[len(C.NB) + i]) for i, w in enumerate(C.WID)}
        L = {r: C.h_lower(r, a0) for r in range(0, 49)}
        worst = {R: Fraction(0) for R in C.NB}
        for R, p in C.COLS:
            s = L[R - sum(p)] - y[R] - sum(z[w] for w in p)
            worst[R] = min(worst[R], s)
        y = {R: y[R] + worst[R] for R in C.NB}
        rc = [L[R - sum(p)] - y[R] - sum(z[w] for w in p) for R, p in C.COLS]
        need(min(rc) >= 0, 'exact dual feasibility')
        rhs = C.rhs_of(case)
        D = sum(C.NB[R] * y[R] for R in C.NB) + sum(rhs[len(C.NB) + i] * z[w] for i, w in enumerate(C.WID))
        Lloc = sum(n * C.h_lower(r, a0) for r, n in loc.items())
        T = W - Lloc - D
        basis = sorted(j for j, x in sol.items() if x > 1e-9)
        need(len(basis) == len(C.NB) + len(C.WID), 'LP basis size')
        cand = [j for j in range(len(C.COLS)) if rc[j] < T and j not in basis]
        need(all(rc[j] < T for j in basis), 'basic columns inside the budget')
        rows = len(C.NB) + len(C.WID)

        def col(j):
            R, p = C.COLS[j]
            return [Fraction(1 if R == RR else 0) for RR in C.NB] + [Fraction(p.count(w)) for w in C.WID]

        Bm = [[col(j)[i] for j in basis] for i in range(rows)]

        def solve(b):
            A = [Bm[i][:] + [Fraction(b[i])] for i in range(rows)]
            for c in range(rows):
                piv = next(r for r in range(c, rows) if A[r][c] != 0)
                A[c], A[piv] = A[piv], A[c]
                pv = A[c][c]
                A[c] = [v / pv for v in A[c]]
                for r in range(rows):
                    if r != c and A[r][c] != 0:
                        f = A[r][c]
                        A[r] = [u - f * v for u, v in zip(A[r], A[c])]
            return [A[i][rows] for i in range(rows)]

        # degenerate columns: rc tiny; check they only exchange zero-remainder patterns (idle multiset invariant)
        degen = [j for j in cand if rc[j] < T / 10 ** 6]
        heavy = [j for j in cand if j not in degen]
        for j in degen:
            lam = solve(col(j))
            need(C.COLS[j][0] - sum(C.COLS[j][1]) == 0 and
                 all(l == 0 or C.COLS[b][0] - sum(C.COLS[b][1]) == 0 for l, b in zip(lam, basis)),
                 'degenerate column %s changes the idle multiset' % (C.COLS[j],))
        # Completeness: det_den clears all denominators in degenerate basis representations.
        # Reduce each degenerate count modulo det_den. Basic counts change by integers,
        # only on zero-remainder columns; thus the idle multiset and integrality are preserved.
        # visit checks those canonical zero-remainder counts are nonnegative for every heavy
        # combination and residue. Other basic counts are unchanged, so every feasible original
        # has a feasible enumerated representative. The integral case additionally checks count 0.
        lam_integral = all(l.denominator == 1 for j in degen for l in solve(col(j)))
        det_den = 1
        for j in degen:
            for l in solve(col(j)):
                det_den = det_den * l.denominator // __import__('math').gcd(det_den, l.denominator)
        xb0 = solve(rhs)
        for v in xb0:
            det_den = det_den * v.denominator // __import__('math').gcd(det_den, v.denominator)
        maxc = {j: int(T // rc[j]) for j in heavy}
        survivors = []
        colv = {j: col(j) for j in heavy + degen}

        def visit(counts, b, s):
            # complete heavy part: try every degenerate residue
            if lam_integral:
                need(all(v >= 0 for v in solve(b)), 'count-0 representative negative for heavy part %s' % counts)
            for kz in itertools.product(range(det_den), repeat=len(degen)):
                bb = list(b)
                for c, j in zip(kz, degen):
                    bb = [bi - c * v for bi, v in zip(bb, colv[j])]
                xb = solve(bb)
                # Modulo det_den, integral lifts preserve integrality and the idle multiset.
                # Only zero-remainder basic columns change; their canonical counts must remain nonnegative.
                need(all(v >= 0 for v, j in zip(xb, basis) if C.COLS[j][0] == sum(C.COLS[j][1])),
                     'canonical degenerate residue has a negative zero-remainder basic count')
                if all(v.denominator == 1 and v >= 0 for v in xb):
                    idle = Counter()
                    for v, j in list(zip(xb, basis)) + [(c, j) for j, c in counts.items()] + list(zip(kz, degen)):
                        R, p = C.COLS[j]
                        if v and R - sum(p):
                            idle[R - sum(p)] += int(v)
                    full = Counter()
                    for v, j in list(zip(xb, basis)) + [(c, j) for j, c in counts.items()] + list(zip(kz, degen)):
                        if v:
                            full[str(C.COLS[j])] += int(v)
                    survivors.append(dict(heavy={str(C.COLS[j]): c for j, c in counts.items()}, patterns=dict(full),
                                          degenerate_residues=list(kz), sum_rc=float(s), idle=dict(sorted(idle.items()))))

        def dfs(i, b, s, counts):          # exact budget-pruned enumeration of heavy counts with sum rc < T
            if i == len(heavy):
                visit(counts, b, s)
                return
            j = heavy[i]
            c = 0
            while c <= maxc[j] and s + c * rc[j] < T:
                nb = [bi - c * v for bi, v in zip(b, colv[j])] if c else b
                if c:
                    counts[j] = c
                dfs(i + 1, nb, s + c * rc[j], counts)
                counts.pop(j, None)
                c += 1

        dfs(0, list(rhs), Fraction(0), {})
        info = dict(a0=str(a0), T=float(T), dual_repair={str(R): float(worst[R]) for R in C.NB},
                    basis=[str(C.COLS[j]) for j in basis], degenerate=[str(C.COLS[j]) for j in degen],
                    heavy={str(C.COLS[j]): dict(rc=float(rc[j]), max_count=maxc[j]) for j in heavy},
                    det_lcm=det_den, degenerate_representation_integral=lam_integral, survivors=len(survivors),
                    distinct_heavy_parts=len({json.dumps(s['heavy'], sort_keys=True) for s in survivors}),
                    survivor_idle_multisets=sorted({json.dumps(s['idle'], sort_keys=True) for s in survivors}))
        print('%s: a0 = %s; budget T = %.4e; basis %d, degenerate %d, heavy %d candidate patterns; integer survivors %d'
              % ('[%s] %s' % (name, label), '%.19f' % float(a0), float(T), len(basis),
                 len(degen), len(heavy), len(survivors)))
        return T, survivors, info

    # ---- 2. search: every integer pattern solution that could beat the claim at a = K ------------------------------
    _T, cands, _info = exclusion(K, '2. search')
    def froot(idle):
        lo, hi = float(K) - 1e-7, float(K) + 1e-7
        for _ in range(80):
            mid = (lo + hi) / 2
            if sum(n * C.h_float(r, mid) for r, n in loc.items()) + sum(n * C.h_float(r, mid) for r, n in idle.items()) < W:
                lo = mid
            else:
                hi = mid
        return lo
    multisets = {json.dumps({str(k): v for k, v in sorted(s['idle'].items())}, sort_keys=True): s for s in cands}
    ranked = sorted(((froot({int(k): v for k, v in json.loads(m).items()}), m) for m in multisets), reverse=True)
    best_root, best_key = ranked[0] if ranked else (float(K), json.dumps({str(k): v for k, v in I.items()}, sort_keys=True))
    best = {int(k): v for k, v in json.loads(best_key).items()}
    need(sum(r * n for r, n in best.items()) == sum(r * n for r, n in I.items()), 'best multiset keeps the idle mass')
    # certified bracket of the best multiset's root
    RB = Fraction(best_root).limit_denominator(10 ** 30)
    need(wmu_idle(best, RB + EPS, False) > W and wmu_idle(best, RB - EPS, True) < W, 'best root bracket')
    out['pattern_optimum'] = dict(idle={str(k): v for k, v in sorted(best.items())}, root_bracket=[str(RB - EPS), str(RB + EPS)],
                                  gain_over_claim=float(RB - K), candidates_better_than_claim=len(ranked) - 1,
                                  pattern_change_vs_lp_basis=(multisets[best_key]['heavy'] if best_key in multisets else {}),
                                  pattern_counts=(multisets[best_key]['patterns'] if best_key in multisets else {}),
                                  ranked=[dict(root=r, idle=json.loads(m)) for r, m in ranked[:6]])
    print('[%s] 2. pattern-IP optimum %s, root %.19f (%+.3e vs claimed kappa)' % (name, best_key, float(RB), float(RB - K)))
    # ---- 3. exclusion at a0 = best root + 1e-15 -----------------------------------------------------------------------
    a0 = RB + EPS
    T, surv, info = exclusion(a0, '3. exclusion')
    need(not surv, name + ': integer solutions survive above the pattern optimum')
    out['exclusion'] = info
    I, K = best, RB
    print('[%s] 3. no integer pattern solution survives at optimum + 1e-15: every legal whole-helper fill has '
          'b <= optimum root + 1e-15' % name)
    want = {str(k): v for k, v in sorted(I.items())}

    # ---- negative control -----------------------------------------------------------------------------------------
    a1 = K - Fraction(1, 10 ** 12)
    T1, surv1, info1 = exclusion(a1, 'control')
    need(any({str(k): v for k, v in s['idle'].items()} == want for s in surv1) and wmu_idle(I, a1, True) < W,
         name + ': negative control: below its root the claimed fill must survive the exclusion')
    norm = lambda d: json.dumps({str(k): v for k, v in d.items()}, sort_keys=True)
    others = sorted({norm(s['idle']) for s in surv1} - {norm(want)})
    need(not others, name + ': a different idle multiset survives at kappa - 1e-12: %s' % others)
    out['negative_control'] = dict(a=str(a1), survivors=len(surv1), claimed_fill_survives=True,
                                   survivor_idle_multisets=info1['survivor_idle_multisets'])
    print('[%s]    control: %d survivors at kappa - 1e-12 (degenerate copies of %d heavy part(s)), all with the '
          'optimal idle multiset (uniqueness within 1e-12)' % (name, len(surv1), info1['distinct_heavy_parts']))
    out['conclusion'] = ('Every legal whole-helper owner fill of the ' + claim['words'] + ' on the unchanged T74 '
                         'template has b <= %s + 1e-15 (pattern-IP optimum, idle %s); the published fill is %s.'
                         % (float(RB), out['pattern_optimum']['idle'],
                            'that optimum' if RB == Fraction(froot(CLAIMS[name]['idle'])).limit_denominator(10 ** 30) or
                            out['pattern_optimum']['gain_over_claim'] < 1e-15 else
                            'below it by %.3e' % out['pattern_optimum']['gain_over_claim']))
    return out, out['pattern_optimum']['gain_over_claim']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    C = load_lp()
    P = C.P
    W = C.W_LIVE
    base = C.CASES['pr2322_control']
    need(dict(base['inv']) == CLAIMS['pr2374']['inv'] and dict(base['pg']) == CLAIMS['pr2374']['profile'] ==
         dict(base['pe']), 'PR2374 claim data equals the PR2387/PR2402 recounted PR2322 case')
    out = dict(claims={})
    surv = {}
    for name in CLAIMS:
        out['claims'][name], surv[name] = audit(C, P, W, name)
    out['scope'] = ('Pattern relaxation of all whole-helper fills (windows, families and ports dropped), so each bound '
                    'covers every legal fill of that claim\'s words; realization of each fill and the word data '
                    '(profile, inventory) are the claimants\' own checks (PR2322 data recounted in PR2402).')
    out['python'] = sys.version.split()[0]
    if args.out:
        with open(os.path.join(HERE, 'owner_optimum.receipt.json'), 'w') as f:
            f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print('runtime %.1fs' % (time.time() - t0))
    need(surv['pr2374'] < 1e-15, 'PR2374 fill is the pattern optimum')
    print('PASS_T74_OWNER_OPTIMUM pr2374:claim_is_optimum pr2435:optimum_gain=%+.3e unique_within_1e-12 no_new_kappa'
          % surv['pr2435'])
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Fail as e:
        sys.stdout.write('FAIL_T74_OWNER_OPTIMUM %s\n' % e)
        sys.exit(1)
