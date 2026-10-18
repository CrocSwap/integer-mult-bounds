#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact chronological packing obstruction; standard library, read-only by default.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
The pattern relaxation credits Ali Romman (#1129), Jeremy Diviney (#2360),
and Sagar Thakrar (#2387/#2442). No predecessor checker is imported.
"""
import argparse
from bisect import bisect_left, bisect_right
from collections import Counter
import copy
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTHS = (4, 5, 7, 8, 9)
RANKS = (8, 16, 32, 48)
INVENTORY = (33, 9, 62, 78, 240)
BINS = (49728, 33152, 33152, 33152)
LOCAL = {1: 2369, 2: 632, 3: 320, 4: 118, 5: 26, 7: 8}
REPLICAS, CALLS, PORTS, M, LIVE = 74, 666, 112, 73, 66304
THRESHOLD = F('0.001714127696')
DYADIC = 1 << 192
CRITICAL = tuple((replica, child)
                 for children, last in (((1, 3), 24), ((5, 7), 16), ((9, 11), 8))
                 for child in children for replica in range(last + 1))
SUPPORT = ((8, (0, 0, 0, 1, 0)), (16, (0, 0, 1, 0, 1)),
           (32, (0, 0, 0, 0, 3)), (32, (0, 0, 1, 2, 1)),
           (32, (0, 0, 2, 0, 2)), (32, (0, 1, 0, 0, 3)),
           (32, (1, 0, 0, 0, 3)), (48, (0, 0, 0, 0, 0)),
           (48, (0, 0, 0, 0, 5)))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + '\n'


def authenticate(data, pin):
    need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'input SHA256 mismatch')
    if 'git_blob' in pin:
        blob = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
        need(blob == pin['git_blob'], 'input Git blob mismatch')


def load_inputs():
    manifest = json.loads((HERE / 'INPUTS.json').read_text())
    out = {}
    for pin in manifest['files']:
        path = Path(pin['path'])
        need(path.parts[0] == 'inputs' and len(path.parts) == 2, 'input path shape')
        need(path.name not in out, 'duplicate input')
        data = (HERE / path).read_bytes()
        authenticate(data, pin)
        out[path.name] = json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)
    need(set(out) == {'PR2435-TEMPLATE.json.gz', 'PR2530-PROVIDERS.json',
                     'PR2530-ORDER.json', 'PR2571-ORDER.json', 'PR2571-CLAIM.json'},
         'complete input set')
    return out, manifest


def source_context(parent):
    need(parent['m'] == M, 'source ambient width')
    ports = parent['port_restriction']['new_to_old']
    need(len(ports) == len(set(ports)) == PORTS, '112 source ports')
    need(Counter(c['child'] for c in parent['idle_children']) ==
         {child: PORTS for child in range(18)}, 'source child multiplicities')
    ranks = {}
    for child in parent['idle_children']:
        key, rank = child['child'], child['rank']
        need(key not in ranks or ranks[key] == rank, 'replica child-rank disagreement')
        ranks[key] = rank
    need(set(ranks) == set(range(18)), 'idle child set')
    need(Counter(ranks.values()) == {8: 6, 16: 4, 32: 4, 48: 4}, 'bin inventory')
    need(tuple(REPLICAS * PORTS * Counter(ranks.values())[r] for r in RANKS) == BINS,
         'physical bin counts')
    pairs = {e['stage']: e['pair'] for e in parent['recipe'] if e['kind'] == 'local'}
    need(pairs == {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3},
         'source stage pairs')
    blocks, stage, source_index = {}, None, 0
    for event in parent['execution_schedule']:
        if event['kind'] in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if event['kind'] == 'local_cover_sweep':
            stage = event['stage']
            need(stage not in blocks, 'duplicate stage')
            blocks[stage] = []
        need(stage is not None, 'event before first call')
        blocks[stage].append((source_index, event))
        source_index += 1
    need(set(blocks) == set(range(9)) and source_index == 30, 'thirty-event source')
    return ranks, pairs, blocks


def diagonal_order(shift):
    need(type(shift) is int and shift >= 0, 'nonnegative integer shift')
    return sorted(((stage, replica) for stage in range(9) for replica in range(REPLICAS)),
                  key=lambda c: (4*c[0] + c[1] + shift*(c[0] >= 1), c[0], c[1]))


def event_windows(order, context):
    """Rebuild strict windows from the original bridge-aware source events."""
    ranks, pairs, blocks = context
    need(len(order) == CALLS and set(order) == set(diagonal_order(0)), 'call permutation')
    for replica in range(REPLICAS):
        need([s for s, r in order if r == replica] == list(range(9)), 'replica stage order')
    last, intervals, call_positions, projection = {}, {}, [], [[] for _ in range(REPLICAS)]
    position = 0
    for stage, replica in order:
        for source_index, event in blocks[stage]:
            projection[replica].append(source_index)
            kind = event['kind']
            if kind == 'local_cover_sweep':
                call_positions.append(position)
                last[replica, pairs[stage]] = position
            elif kind == 'bridge':
                last[replica, event['src']] = last[replica, event['dst']] = position
            elif kind == 'idle_cover_sweep':
                for child in event['child_indices']:
                    if child in ranks:
                        key = replica, child
                        need(key not in intervals, 'duplicate idle window')
                        intervals[key] = last.get((replica, event['pair']), -1), position
            position += 1
    need(all(p == list(range(30)) for p in projection), 'per-replica event projection')
    need(len(intervals) == 1332 and len(call_positions) == CALLS, 'window count')
    return {key: tuple(range(bisect_right(call_positions, lo), bisect_left(call_positions, hi)))
            for key, (lo, hi) in intervals.items()}


def direct_rank8_windows(order):
    """Independent stage-position derivation for all 444 rank-eight windows."""
    at = {call: index for index, call in enumerate(order)}
    return {(replica, child): tuple(range(at[stage, replica] + 1, at[stage + 1, replica] + 1))
            for stage, children in ((1, (1, 3)), (3, (5, 7)), (5, (9, 11)))
            for child in children for replica in range(REPLICAS)}


def compare_windows(order, windows):
    for key, direct in direct_rank8_windows(order).items():
        need(windows[key] == direct, 'independent window derivations disagree')


def cut(windows, groups=CRITICAL, width8_supply=78):
    need(len(groups) == len(set(groups)) == 102, '102 distinct cut groups')
    need(all(child in (1, 3, 5, 7, 9, 11) for _, child in groups), 'rank-eight cut groups')
    times = set(t for group in groups for t in windows[group])
    need(bool(times) and times == set(range(min(times), max(times) + 1)), 'contiguous cut union')
    demand, supply = len(groups) * PORTS, len(times) * width8_supply
    return dict(first_call=min(times), last_call=max(times), eligible_calls=len(times),
                bins=demand, width8_supply=supply, defect=max(0, demand - supply))


def check_chronology(context, source):
    need([list(c) for c in diagonal_order(0)] == source['PR2530-ORDER.json'], 'PR2530 order binding')
    need([list(c) for c in diagonal_order(4)] == source['PR2571-ORDER.json'], 'PR2571 order binding')
    cases = []
    for shift in range(71):
        order = diagonal_order(shift)
        windows = event_windows(order, context)
        compare_windows(order, windows)
        result = cut(windows)
        # 117 calls from stages 1..8; at most 28 stage-zero calls intervene.
        expected = 117 + max(0, min(28, 69 - shift))
        need(result['eligible_calls'] == expected, 'closed-form union size')
        need(result['defect'] >= 114, 'universal 114-bin defect')
        cases.append(dict(shift=shift, **result))
    need(diagonal_order(70) == diagonal_order(71) == diagonal_order(10**6), 'stable terminal order')
    need(cases[0]['first_call'] == 6 and cases[0]['last_call'] == 150, 'original cut endpoints')
    need(cases[4]['first_call'] == 10 and cases[4]['last_call'] == 154, 'shifted cut endpoints')
    return cases


def dyadic_lower(x):
    return F((x.numerator * DYADIC) // x.denominator, DYADIC)


def dyadic_upper(x):
    return -dyadic_lower(-x)


@lru_cache(maxsize=None)
def log_bounds(x):
    """Atanh series, range reduction, explicit positive tail; exact rationals."""
    need(x >= 1, 'log domain')
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def series(v):
        z = (v - 1) / (v + 1)
        total, power = F(0), z
        for j in range(64):
            total += 2 * power / (2*j + 1)
            power *= z*z
        tail = 2 * power / (129 * (1 - z*z))
        return total, total + tail

    lo, hi = series(x)
    lo2, hi2 = series(F(2))
    return dyadic_lower(lo + k*lo2), dyadic_upper(hi + k*hi2)


def exp_bounds(lo, hi):
    need(0 <= lo <= hi < 5, 'exponential domain')

    def polynomial(x):
        term = total = F(1)
        for j in range(1, 65):
            term = term*x/j
            total += term
        next_term = term*x/65
        return total, total + next_term/(1 - x/66)

    lower, _ = polynomial(lo)
    _, upper = polynomial(hi)
    return dyadic_lower(lower), dyadic_upper(upper)


@lru_cache(maxsize=None)
def h_bounds(rank, a):
    need(0 <= rank <= M and 0 <= a <= 1, 'moment domain')
    if rank == 0:
        return F(0), F(0)
    lo, hi = log_bounds(F(M, rank))
    el, eu = exp_bounds(a*lo, a*hi)
    return F(rank, M)*el, F(rank, M)*eu


def patterns():
    out = []
    for rank in RANKS:
        def visit(i, remainder, counts):
            if i == len(WIDTHS):
                out.append((rank, tuple(counts), remainder))
                return
            for n in range(remainder // WIDTHS[i] + 1):
                visit(i + 1, remainder - n*WIDTHS[i], counts + [n])
        visit(0, rank, [])
    need(len(out) == 1163 and len(set(out)) == 1163, 'complete pattern enumeration')
    return out


def solve(matrix, rhs):
    """Exact Gaussian elimination; used only to propose a subsequently checked dual."""
    n = len(rhs)
    rows = [[F(v) for v in row] + [rhs[i]] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        d = rows[j][j]
        rows[j] = [x/d for x in rows[j]]
        for i in range(n):
            if i != j:
                d = rows[i][j]
                rows[i] = [x-d*y for x, y in zip(rows[i], rows[j])]
    return [row[-1] for row in rows]


def dual_slack(pattern, dual, lower):
    rank, counts, remainder = pattern
    return lower[remainder] - dual[RANKS.index(rank)] - sum(n*z for n, z in zip(counts, dual[4:]))


def validate_dual(pats, dual, lower, penalty):
    need(penalty > 0, 'positive defect penalty')
    for pattern in pats:
        rank, counts, _ = pattern
        need(dual_slack(pattern, dual, lower) >=
             (penalty if rank == 8 and counts[3] == 0 else 0), 'dual pattern inequality')


def validate_primal(counts):
    need(len(counts) == len(SUPPORT) and all(x >= 0 for x in counts), 'primal nonnegativity')
    for rank, bins in zip(RANKS, BINS):
        need(sum(x for x, (r, _) in zip(counts, SUPPORT) if r == rank) == bins,
             'primal bin balance')
    for j, supply in enumerate(INVENTORY):
        need(sum(x*ns[j] for x, (_, ns) in zip(counts, SUPPORT)) == CALLS*supply,
             'primal width balance')


def certify(a, defect=114):
    pats = patterns()
    lower = {r: h_bounds(r, a)[0] for r in range(49)}
    matrix = [[int(rank == r) for r in RANKS] + list(counts) for rank, counts in SUPPORT]
    rhs = [lower[rank - sum(w*n for w, n in zip(WIDTHS, counts))] for rank, counts in SUPPORT]
    dual = solve(matrix, rhs)
    # A separate closed-form derivation of the same nine equality constraints.
    t = (lower[3] - lower[48])/5
    y32 = lower[5] - 3*t
    closed = [y32/4, y32/2, y32, lower[48], lower[1]-lower[5],
              -lower[5], (t-lower[5])/2, -y32/4, t]
    need(dual == closed, 'closed-form and elimination duals disagree')
    repairs = []
    for i, rank in enumerate(RANKS):
        repair = min(F(0), min(dual_slack(p, dual, lower) for p in pats if p[0] == rank))
        dual[i] += repair
        repairs.append(str(repair))
    penalty = min(dual_slack(p, dual, lower) for p in pats if p[0] == 8 and p[1][3] == 0)
    validate_dual(pats, dual, lower, penalty)
    local = CALLS * sum(n*lower[r] for r, n in LOCAL.items())
    relaxed = local + sum(n*y for n, y in zip(BINS, dual[:4])) + CALLS*sum(n*z for n, z in zip(INVENTORY, dual[4:]))
    total = relaxed + defect*penalty
    primal_rhs = list(BINS) + [CALLS*n for n in INVENTORY]
    primal = solve(list(map(list, zip(*matrix))), list(map(F, primal_rhs)))
    validate_primal(primal)
    primal_upper = CALLS*sum(n*h_bounds(r, a)[1] for r, n in LOCAL.items())
    primal_upper += sum(x*h_bounds(rank-sum(w*n for w, n in zip(WIDTHS, ns)), a)[1]
                        for x, (rank, ns) in zip(primal, SUPPORT))
    need(relaxed <= primal_upper, 'weak duality control')
    result = dict(threshold=str(a), pattern_count=len(pats), dual=[str(v) for v in dual],
                  bin_dual_repairs=repairs,
                  window_free_primal_counts=[str(x) for x in primal],
                  window_free_primal_upper=str(primal_upper),
                  penalty_per_defect=str(penalty), defect=defect,
                  local_lower=str(local), window_free_lower=str(relaxed),
                  chronological_lower=str(total), live=LIVE, strict_margin=str(total-LIVE))
    return result, pats, dual, lower, penalty


def failure_controls(source, context, manifest):
    rejected = []

    def rejects(name, fn, expected):
        try:
            fn()
        except ValueError as exc:
            need(str(exc) == expected, 'wrong control failure: ' + name)
            rejected.append(name)
        else:
            raise ValueError('accepted negative control: ' + name)

    pin = manifest['files'][0]
    data = (HERE / pin['path']).read_bytes()
    rejects('changed_source_bytes', lambda: authenticate(data + b' ', pin), 'input SHA256 mismatch')
    order = diagonal_order(4)
    wrong = order[:]
    i, j = wrong.index((0, 0)), wrong.index((1, 0))
    wrong[i], wrong[j] = wrong[j], wrong[i]
    rejects('reversed_replica_stages', lambda: event_windows(wrong, context), 'replica stage order')
    windows = event_windows(order, context)
    wrong_windows = dict(windows)
    wrong_windows[0, 1] = (windows[0, 1][0] - 1,) + windows[0, 1]
    rejects('inclusive_pre_bridge_endpoint', lambda: compare_windows(order, wrong_windows),
            'independent window derivations disagree')
    bad_context = copy.deepcopy(context)
    bad_context[2][1] = [(i, e) for i, e in bad_context[2][1] if e['kind'] != 'bridge']
    rejects('omitted_source_bridge', lambda: event_windows(order, bad_context), 'per-replica event projection')
    rejects('duplicate_cut_group', lambda: cut(windows, CRITICAL[:-1] + (CRITICAL[0],)), '102 distinct cut groups')
    rejects('overstated_defect_115', lambda: need(cut(windows)['defect'] >= 115, 'cut deficiency'), 'cut deficiency')
    rejects('unbound_inventory_79', lambda: need(cut(windows, width8_supply=79)['defect'] >= 114, 'cut deficiency'), 'cut deficiency')
    result, pats, dual, lower, penalty = certify(THRESHOLD)
    bad_dual = dual[:]
    bad_dual[0] += F(1, 100)
    rejects('inflated_rank8_dual', lambda: validate_dual(pats, bad_dual, lower, penalty), 'dual pattern inequality')
    rejects('inflated_defect_penalty', lambda: validate_dual(pats, dual, lower, penalty + F(1, 10**6)), 'dual pattern inequality')
    primal = list(map(F, result['window_free_primal_counts']))
    primal[0] += 1
    rejects('unbalanced_relaxed_primal', lambda: validate_primal(primal), 'primal bin balance')
    need(F(result['window_free_primal_upper']) < LIVE < F(result['chronological_lower']), 'cut is essential')
    below, *_ = certify(F(source['PR2571-CLAIM.json']['complex_lower']))
    need(F(below['chronological_lower']) < LIVE, 'does not reject predecessor endpoint')
    # Separate arithmetic controls use algebraic identities, not a second exp implementation.
    for rank in (1, 7, 8, 16, 48, 73):
        lo, hi = h_bounds(rank, F(0))
        need(lo <= F(rank, M) <= hi, 'linear-cost control')
        lo, hi = h_bounds(rank, F(1, 2))
        need(lo*lo <= F(rank, M) <= hi*hi, 'square-root control')
        lo, hi = h_bounds(rank, F(1))
        need(lo <= 1 <= hi, 'constant-cost control')
    return dict(rejected=rejected, positive=['all_rank8_windows_two_derivations',
                'integer_shift_closed_form', 'stable_order_after_shift70',
                'linear_square_root_constant_costs', 'predecessor_endpoint_not_rejected',
                'window_free_primal_accepts_excluded_threshold'])


def verify():
    source, manifest = load_inputs()
    providers = source['PR2530-PROVIDERS.json']
    need(set(providers) == {'gauge44', 'extra'}, 'two source providers')
    for provider in providers.values():
        need(Counter(provider['widths']) == dict(zip(WIDTHS, INVENTORY)), 'source width inventory')
        need({int(r): n for r, n in provider['actual_paid_profile'].items()} == LOCAL, 'source local profile')
    need(sum(INVENTORY) == 422 and LIVE == REPLICAS*8*PORTS, 'whole-helper and live stock')
    total_mass = CALLS*sum(r*n for r, n in LOCAL.items()) + sum(r*n for r, n in zip(RANKS, BINS)) - CALLS*sum(w*n for w, n in zip(WIDTHS, INVENTORY))
    need(total_mass == 4816512 and M*LIVE-total_mass == 23680, 'complete rank mass and deficit')
    context = source_context(source['PR2435-TEMPLATE.json.gz'])
    cases = check_chronology(context, source)
    result, *_ = certify(THRESHOLD)
    need(F(result['strict_margin']) > 0, 'strict moment exclusion')
    controls = failure_controls(source, context, manifest)
    return dict(schema_version=1, status='PASS_T74_DIAGONAL_WINDOW_BOUND',
                model=dict(replicas=REPLICAS, calls=CALLS, width=M, live=LIVE,
                           widths=list(WIDTHS), inventory=list(INVENTORY), bins=list(BINS),
                           local_profile={str(r): n for r, n in LOCAL.items()}),
                critical_groups=[list(g) for g in CRITICAL], shift_cases=cases,
                union_formula='117 + max(0, min(28, 69-s)), for integer s >= 0',
                minimum_defect=114, price=result, controls=controls,
                source_sha256={p['path']: p['sha256'] for p in manifest['files']},
                scope='Fixed whole-helper inventory and uniform initial stage shifts only; no new kappa or supplier admission.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    result = verify()
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(canonical(result))
    else:
        need(canonical(json.loads(path.read_text())) == canonical(result),
             'stored certificate differs from exact replay')
    print(result['status'], 'shifts=71+stable_tail groups=102 deficit>=114 patterns=1163',
          'b<0.001714127696 controls=' + str(len(result['controls']['rejected'])), 'no_new_kappa')


if __name__ == '__main__':
    main()
