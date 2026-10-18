#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Audit: PR442 hosting windows and the partial width-seven rows of #1023 and #1281 (no new kappa).

Usage: python3 -I -B research/bit589-width7-windows-seed72/verify.py [--write] [--kmax K]

0. Binds the frontier1094 certificate (named by the selected record, or by a checkpoint record once
   the frontier moves) -> the PR589 record and engines pinned by #1023's packing.py.
1. Builds the nine-stage idle schedule, matches it event by event with the schedule the pinned
   global_k.py produces, and runs three window predicates on it (windows.py); the frozen PR589
   selection lies inside the windows. Capacity-7 children admit one stage each.
2. Checks the interval Hall reduction to two nested chains by max-flow over every distribution of
   the 6k residuals for k = 1, 2.
3. For every k = 0..74 converted helpers per call: the exact window-respecting optimum (DP lower bound),
   an explicit residual-level placement attaining it (window, width, offset, disjoint cells, every
   (stage, helper) hosted once; built and checked at run time by build()), its bit endpoint under both of #1023's local brackets with the pinned
   engines, a certificate that no window-feasible placement reaches the next 1e-24 grid point, and a
   tightness check against the engine moment of the explicit histogram.
4. Compares with the window-free rows: #1023's eight partial rows (its RESULT.json) and merged #1281's
   EXPECTED.json (digest-pinned). #1281's closed-form local optimum is transcribed in windowfree_idle(),
   checked against its 75 idle profiles and re-priced here for every k; its nine priced cases are
   reproduced exactly in local endpoint and local histogram; local and pooled32 endpoints of the
   priced cases lie above the per-replica bound.
5. Checks that #1023's all-width-7 optimum {42:340, 21:1} is window-feasible.
Expected last line: PASS_BIT589_WIDTH7_WINDOWS
"""
import argparse
import itertools
import json
import sys
from collections import Counter, deque
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wopt  # noqa: E402
from wopt import CAP, M, N, P, R, REST, SEVEN, SHIFT, STG, T, WIN  # noqa: E402

PR1281 = dict(merged='e4a7f61f168837f628a1d8b54aa5cff0680f9a38', path='research/bit-partial-width7-optimum/EXPECTED.json',
              sha256='a6ec64866b949626d6508ee7172b144c3fd29f1065822b523fafd7d2a59e2e91')


ASSEMBLY = 'research/community-frontier1094-audit/ASSEMBLY.json'


def bind():
    """frontier1094 ASSEMBLY -> the PR589 record and engines that #1023's packing.py pins. The certificate
    must be named, with its digest, by the selected record or (after the frontier moves) by a record in
    certificates/checkpoints/; which one is not written to RESULT.json."""
    raw = (P.ROOT / ASSEMBLY).read_bytes()
    records = [P.ROOT / 'certificates/selected-result.json'] + sorted((P.ROOT / 'certificates/checkpoints').glob('*.json'))
    named = False
    for f in records:
        try:
            rec = json.loads(f.read_text()) if f.is_file() else {}
        except ValueError:
            rec = {}
        rec = rec if isinstance(rec, dict) else {}
        named = named or (rec.get('certificate') == ASSEMBLY and rec.get('certificate_sha256') == P.sha256(raw))
    need(named, 'a selected or checkpoint record names the frontier1094 certificate')
    asm = json.loads(raw)
    need(asm['input_sha256']['package:inputs/PR589-EXPECTED.json'] == P.SOURCES['inputs']['bit_record']['sha256'],
         'the certificate pins the PR589 record that packing.py reads')
    for name in ('moment.py', 'base_two_moment.py', 'outer.py'):
        need(asm['input_sha256']['engines/' + name] == P.SOURCES['engines'][name], 'the certificate pins engine ' + name)
    need(Q(asm['bit_lower']) == Q(P.pinned_json('bit_record')['nine']['bit_lower']), 'certificate bit endpoint = PR589 record')
    return dict(assembly=ASSEMBLY, assembly_sha256=P.sha256(raw), bit_lower=asm['bit_lower'],
                named_by='certificates/selected-result.json or certificates/checkpoints/*.json')


def need(ok, label):
    if not ok:
        raise SystemExit('FAIL ' + label)


def maxflow_assign(supply, demand, allowed):
    """Transportation by augmenting paths: x[(stage, child)] or None if infeasible."""
    src, snk = 'S', 'T'
    cap, adj = {}, {}

    def add(u, v, c):
        cap[(u, v)] = cap.get((u, v), 0) + c
        cap.setdefault((v, u), 0)
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    for s, n in supply.items():
        if n:
            add(src, ('s', s), n)
    for i, n in demand.items():
        if n:
            add(('c', i), snk, n)
            for s in allowed[i]:
                if supply.get(s, 0):
                    add(('s', s), ('c', i), 10 ** 9)
    flow = 0
    while True:
        par, dq = {src: None}, deque([src])
        while dq and snk not in par:
            u = dq.popleft()
            for v in sorted(adj.get(u, ()), key=str):
                if v not in par and cap[(u, v)] > 0:
                    par[v] = u
                    dq.append(v)
        if snk not in par:
            break
        b, v = None, snk
        while par[v] is not None:
            u = par[v]
            b = cap[(u, v)] if b is None else min(b, cap[(u, v)])
            v = u
        v = snk
        while par[v] is not None:
            u = par[v]
            cap[(u, v)] -= b
            cap[(v, u)] += b
            v = u
        flow += b
    if flow != sum(supply.values()) or flow != sum(demand.values()):
        return None
    return {(s, i): cap[(('c', i), ('s', s))] for i in demand for s in allowed[i]
            if (('c', i), ('s', s)) in cap and cap[(('c', i), ('s', s))]}


def w8_vacuous(k):
    for lo in range(STG):
        for hi in range(lo, STG):
            if (lo, hi) == (0, STG - 1):
                continue
            J = set(range(lo, hi + 1))
            if sum(N * (CAP[i] // 8) for i in WIN if set(WIN[i][1]) <= J) > (R - k) * len(J):
                return False
    return True


def chain_ok(B, k):
    """The two nested chains (children 0,2,4 and 8,7,6) and the total, as derived in README."""
    L0, L1, L2 = B[0], B[0] + B[2], B[0] + B[2] + B[4]
    R0, R1, R2 = B[8], B[8] + B[7], B[8] + B[7] + B[6]
    return L0 <= 2 * k and L1 <= 3 * k and L2 <= 4 * k and R0 <= 2 * k and R1 <= 3 * k and R2 <= 4 * k and L2 + R2 == 6 * k


def brute_force_reduction(k):
    """Every distribution of the 6k non-7-slot width-7 residuals over children 0,2,4,6,7,8 (all
    compositions of 6k into six parts): window transport feasibility (max-flow) must equal the chain
    predicate."""
    supply = {s: (0 if s in (2, 4, 6) else k) for s in range(STG)}
    count = agree = 0
    for bars in itertools.combinations(range(6 * k + 5), 5):
        cuts = (-1,) + bars + (6 * k + 5,)
        B = dict(zip(REST, [cuts[i + 1] - cuts[i] - 1 for i in range(6)]))
        feasible = maxflow_assign(supply, {i: B[i] for i in REST}, {i: set(WIN[i][1]) for i in REST}) is not None
        count += 1
        agree += feasible == chain_ok(B, k)
    return count, agree


def build(k, plan, slots_out=None):
    """Explicit per-replica hosting from the DP plan, verified in the audit_hosted_k style. Returns the idle
    remainder histogram; if slots_out is a list, the checked slots (child, copy, offset, width, stage,
    helper) are appended to it."""
    copies = {i: [] for i in WIN}
    for i in WIN:
        for (l, b, r) in plan['copies'][i]:
            copies[i].append([CAP[i] // 8 - l, b])
    for c, l in plan['pure8']:
        opts = [i for i in WIN if CAP[i] == c and len(copies[i]) < N]
        need(bool(opts), 'free copy of capacity %d' % c)
        copies[opts[0]].append([c // 8 - l, 0])
    for i in WIN:
        need(len(copies[i]) <= N, 'copy count')
        copies[i] += [[CAP[i] // 8, 0] for _ in range(N - len(copies[i]))]
    out = {}
    for w, per_stage in ((7, k), (8, R - k)):
        dem = {i: sum(cp[0 if w == 8 else 1] for cp in copies[i]) for i in WIN}
        x = maxflow_assign({s: per_stage for s in range(STG)}, dem, {i: set(WIN[i][1]) for i in WIN})
        need(x is not None, 'stage transport k=%d width %d' % (k, w))
        out[w] = x
    pool = {(s, w): deque(range(0, k) if w == 7 else range(k, R)) for s in range(STG) for w in (7, 8)}
    slots = []
    for i in WIN:
        want = {w: deque() for w in (7, 8)}
        for w in (7, 8):
            for (s, j), n in sorted(out[w].items()):
                if j == i:
                    want[w].extend([s] * n)
        for cp, (a8, b7) in enumerate(copies[i]):
            off = 0
            for w, n in ((8, a8), (7, b7)):
                for _ in range(n):
                    s = want[w].popleft()
                    slots.append((i, cp, off, w, s, pool[(s, w)].popleft()))
                    off += w
        need(not want[7] and not want[8], 'every residual placed')
    used, hosted, rem = {}, set(), Counter()
    for i, cp, off, w, s, h in slots:
        need(s in WIN[i][1], 'slot inside its window')
        need(w == (7 if h < k else 8), 'residual width')
        need(0 <= off and off + w <= CAP[i], 'slot within capacity')
        cells = set(range(off, off + w))
        need(not cells & used.get((i, cp), set()), 'disjoint cells')
        used.setdefault((i, cp), set()).update(cells)
        need((s, h) not in hosted, 'hosted once')
        hosted.add((s, h))
    need(hosted == {(s, h) for s in range(STG) for h in range(R)}, 'every (stage, helper) hosted')
    if slots_out is not None:
        slots_out.extend(slots)
    for i in WIN:
        for cp in range(N):
            r = CAP[i] - len(used.get((i, cp), ()))
            if r:
                rem[r] += 1
    return +rem


def certificate_bound(k, local, at, calls, W):
    """Moment lower bound at `at` over every window-feasible replica-local placement (DP over the idle
    children, exact moment of the fixed local histogram), and the DP argmin plan there."""
    tot5, _, plan, _ = wopt.solve(k, at, True)
    lo_local, _ = P.MOMENT.moment(dict(Counter({r: n * calls for r, n in local.items()})), M, W, at, True)
    return lo_local + Q(T * tot5, 5 * SHIFT * M * W), plan


def windowfree_idle(k):
    """#1281's replica-local optimum without windows, transcribed from its closed form (every width-7 role in
    a 7-slot; S = 45 + 9k = 5q + t) and checked against its EXPECTED.json idle profiles in main()."""
    S = 45 + 9 * k
    q, t = divmod(S, 5)
    idle = Counter({7: 666 - 9 * k, 6: 444, 4: 444, 2: 444})
    idle[2] -= q
    idle[42] += q
    part = {1: (14, 6, 14), 2: (28, 4, 20), 3: (28, 4, 28), 4: (42, 2, 34)}
    if t:
        _, old, new = part[t]
        idle[old] -= 1
        idle[new] += 1
    return +idle


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--kmax', type=int, default=74)
    a = ap.parse_args()
    binding = bind()
    record = P.pinned_json('bit_record')
    selection = P.pinned_json('selection')
    model = P.slot_model(record, selection)
    W = record['nine']['bit']['live']
    calls = model['calls']
    need(model['caps'] == {i: CAP[i] for i in CAP}, 'slot model = idle children with the same capacities')
    c0 = Q(record['nine']['bit_lower'])
    out = dict(binding=binding, windows={str(i): dict(capacity=c, stages=list(st)) for i, (c, st) in WIN.items()},
               capacity7_children={str(i): list(WIN[i][1]) for i in SEVEN})
    need(all(len(WIN[i][1]) == 1 for i in SEVEN), 'each capacity-7 child admits exactly one stage')

    # Hall reduction, brute force
    bf = {}
    for k in (1, 2):
        n, agree = brute_force_reduction(k)
        need(n == agree, 'chain reduction brute force k=%d' % k)
        bf[str(k)] = n
    out['chain_reduction_brute_force'] = dict(distributions_checked=bf, agree='all')

    def price(local, idle):
        H = Counter({r: n * calls for r, n in local.items()})
        H.update({r: n * T for r, n in idle.items()})
        H = +H
        need(sum(r * n for r, n in H.items()) == sum(r * n for r, n in model['H'].items()), 'rank mass')
        return P.endpoint(dict(H), W), H

    rows, windowfree_H = {}, {}
    for k in range(0, a.kmax + 1):
        need(w8_vacuous(k), 'width-8 Hall conditions vacuous k=%d' % k)
        tot5, best, plan, F = wopt.solve(k, Q(1, 570), True)
        idle = build(k, plan)
        need(5 * sum(F[r] * n for r, n in idle.items()) == tot5, 'DP value attained by the explicit placement k=%d' % k)
        opt, pes = P.local_bracket(model['local'], k)
        row = dict(idle=dict(sorted((str(r), n) for r, n in idle.items())), width7_distribution=[[i, B] for i, B, _ in best[1]])
        for name, local in (('optimistic', opt), ('pessimistic', pes)):
            c, H = price(local, idle)
            cwf, Hwf = price(local, windowfree_idle(k))
            windowfree_H[(k, name)] = Hwf
            nxt = c + Q(1, 10 ** 24)
            lb, plan_n = certificate_bound(k, local, nxt, calls, W)
            need(lb > 1, 'certificate k=%d %s' % (k, name))
            lo_full, _ = P.MOMENT.moment(dict(H), M, W, nxt, True)
            need(abs(lb - lo_full) < Q(1, 10 ** 50), 'tight certificate k=%d %s' % (k, name))
            row[name] = dict(endpoint=str(c), endpoint_decimal=P.dec(c, 22), certified_bound=str(nxt),
                             lb_minus_one_at_bound='%.3e' % float(lb - 1), same_argmin_at_bound=build(k, plan_n) == idle,
                             windowfree_endpoint=str(cwf), windowfree_decimal=P.dec(cwf, 22),
                             gain_percent='%.6f' % float(100 * (c - c0) / c0),
                             windowfree_gain_percent='%.6f' % float(100 * (cwf - c0) / c0),
                             retained_fraction=None if k == 0 else '%.6f' % float((c - c0) / (cwf - c0)),
                             windowfree_unreachable=k == 0 or cwf >= nxt)
            if k == 0:
                need(c == c0, 'k = 0 reproduces the selected bit endpoint')
        rows[str(k)] = row
    out['rows'] = rows

    # #1023 (merged): its eight partial rows against the certified bounds
    rec1023 = json.loads((P.ROOT / 'research/bit589-width-packing/RESULT.json').read_text())['scenarios']
    unreach = {}
    for k in (1, 10, 37, 74):
        if str(k) not in rows:
            continue
        for name in ('optimistic', 'pessimistic'):
            v = Q(rec1023['width7_k%d_%s' % (k, name)]['bit_lower'])
            unreach['k%d_%s' % (k, name)] = dict(pr1023=P.dec(v, 22), certified_bound=rows[str(k)][name]['certified_bound'],
                                                 unreachable=v >= Q(rows[str(k)][name]['certified_bound']))
    need(all(x['unreachable'] for x in unreach.values()), '#1023 partial rows unreachable under windows')
    out['pr1023_partial_rows'] = unreach
    # #1281 (merged): its EXPECTED.json, digest-pinned, read as data (no #1281 code is run)
    raw = (P.ROOT / PR1281['path']).read_bytes()
    need(P.sha256(raw) == PR1281['sha256'], '#1281 EXPECTED.json digest')
    e1281 = json.loads(raw)
    need(e1281['status'] == 'PASS_BIT_PARTIAL_WIDTH7_OPTIMUM' and len(e1281['cases']) == 75, '#1281 EXPECTED.json shape')
    for case in e1281['cases']:
        if case['k'] <= a.kmax:
            need(Counter({int(r): n for r, n in case['idle'].items()}) == windowfree_idle(case['k']), '#1281 local idle optimum k=%d' % case['k'])
    priced = {}
    for key, case in sorted(e1281['priced_cases'].items()):
        k, name = int(key[1:key.index('_')]), key[key.index('_') + 1:]
        if k > a.kmax:
            continue
        r = rows[str(k)][name]
        need(Q(case['optimal']['lower']) == Q(r['windowfree_endpoint']), '#1281 %s local endpoint reproduced' % key)
        need(Counter({int(x): n for x, n in case['histogram'].items()}) == windowfree_H[(k, name)], '#1281 %s histogram' % key)
        bound = Q(r['certified_bound'])
        priced[key] = dict(local=P.dec(Q(case['optimal']['lower']), 22), pooled32=P.dec(Q(case['pooled32']['lower']), 22),
                           certified_bound=r['certified_bound'],
                           local_above_bound=Q(case['optimal']['lower']) >= bound,
                           pooled32_above_per_replica_bound=Q(case['pooled32']['lower']) >= bound)
    need(all(v['local_above_bound'] and v['pooled32_above_per_replica_bound'] for key, v in priced.items()
             if not key.startswith('k0_')), '#1281 priced rows above the per-replica bound')
    local_unreach = sum(rows[str(k)][b]['windowfree_unreachable'] for k in range(1, a.kmax + 1) for b in ('optimistic', 'pessimistic'))
    need(local_unreach == 2 * a.kmax, '#1281 local rows unreachable under windows')
    out['pr1281'] = dict(PR1281, idle_optima_matched=sum(c['k'] <= a.kmax for c in e1281['cases']), priced_cases=priced,
                         local_rows_unreachable='%d of %d priced here (both brackets, k = 1..%d; %d priced by #1281)' % (
                             local_unreach, 2 * a.kmax, a.kmax, sum(1 for x in priced if not x.startswith('k0_'))))

    # #1023's all-width-7 optimum stays window-feasible
    feasible = []
    for x4 in range(104):
        cps = {i: ([CAP[i] // 7] * N if CAP[i] in (7, 14, 28) else []) for i in WIN}
        cps[4] = [6] * x4
        cps[6] = [6] * (103 - x4) + [3]
        if len(cps[4]) > N or len(cps[6]) > N:
            continue
        if maxflow_assign({s: R for s in range(STG)}, {i: sum(cps[i]) for i in WIN}, {i: set(WIN[i][1]) for i in WIN}) is not None:
            feasible.append(x4)
    need(bool(feasible), 'all-width-7 optimum window-feasible')
    out['all_width7'] = dict(idle_per_replica={'42': 340, '21': 1}, feasible_sextet_splits=[min(feasible), max(feasible), len(feasible)])

    text = json.dumps(dict(status='PASS_BIT589_WIDTH7_WINDOWS', **out), indent=1, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if a.write:
        target.write_text(text)
    elif a.kmax == 74:
        need(text == target.read_text(), 'RESULT.json reproduced byte for byte')
    for k in (1, 2, 10, 37, 74):
        if str(k) in rows:
            r = rows[str(k)]['optimistic']
            print('k=%2d window-respecting %s (+%s%%)  window-free %s (+%s%%)  retained %s' % (
                k, r['endpoint_decimal'][:14], r['gain_percent'][:6], r['windowfree_decimal'][:14],
                r['windowfree_gain_percent'][:6], r['retained_fraction']))
    print('PASS_BIT589_WIDTH7_WINDOWS' if a.kmax == 74 else 'PASS_PARTIAL kmax=%d' % a.kmax)


if __name__ == '__main__':
    main()
