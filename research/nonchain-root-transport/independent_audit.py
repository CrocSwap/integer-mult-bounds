#!/usr/bin/env python3
"""Independent finite audit of the mixed-mask transport package.

Jerry Chen / @CubeJerry, with substantial OpenAI assistance; Apache-2.0.
The normalized query formulas and native census are credited to the authors
of retained/chain_root.py and retained/pricing.py, especially DreamingOfClouds
with Claude Opus 5.5. No package model, verifier, or predecessor is imported.

Capacities are ranks of explicitly constructed primal/dual pairing matrices.
Powers use a positive log series and reciprocal positive exponential bounds,
rather than the primary verifier's atanh and alternating-exponential bounds.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse
import ast
import gzip
import hashlib
import json
import time

C = Q('0.0033718004755')
N = 20
A = 0
F = list(range(1, 10))
H = list(range(10, 19))
EMPTY = 19
FULL_SITES = list(range(9)) + list(range(12, 21))
INTERVALS = [(a, b) for a in range(18) for b in range(a, 18)]
D = [Q(p) for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61)]
SOURCE_HEAD = '51f54e3c31f2f3a3e056a483b3ed66ae916ad06a'
NATIVE_PAYLOAD = 'd3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return sum((a*b for a, b in zip(x, y)), Q(0))


def vec(entries):
    answer = [Q(0)] * N
    for k, z in entries.items():
        answer[k] = Q(z)
    return answer


def identity(n=N):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def matmul(x, y):
    if not x:
        return []
    if not y:
        return [[] for _ in x]
    cols = list(zip(*y))
    return [[dot(row, col) for col in cols] for row in x]


def rref(rows, width):
    out = [[Q(z) for z in row] for row in rows]
    need(all(len(row) == width for row in out), 'Matrix shape')
    pivots = []
    pivot_row = 0
    for j in range(width):
        source = next((i for i in range(pivot_row, len(out)) if out[i][j]), None)
        if source is None:
            continue
        out[pivot_row], out[source] = out[source], out[pivot_row]
        s = out[pivot_row][j]
        out[pivot_row] = [z/s for z in out[pivot_row]]
        for i in range(len(out)):
            if i == pivot_row or not out[i][j]:
                continue
            s = out[i][j]
            out[i] = [z-s*w for z, w in zip(out[i], out[pivot_row])]
        pivots.append(j)
        pivot_row += 1
        if pivot_row == len(out):
            break
    return out, pivots


def nullspace(rows, width):
    reduced, pivots = rref(rows, width)
    free = [j for j in range(width) if j not in pivots]
    answer = []
    for j in free:
        row = [Q(0)]*width
        row[j] = Q(1)
        for i, pivot in enumerate(pivots):
            row[pivot] = -reduced[i][j]
        need(all(dot(original, row) == 0 for original in rows), 'Literal nullspace vector')
        answer.append(row)
    need(len(rref(answer, width)[1]) == len(answer), 'Independent nullspace basis')
    return answer


def inverse(matrix):
    n = len(matrix)
    augmented = [list(row) + eye for row, eye in zip(matrix, identity(n))]
    reduced, pivots = rref(augmented, 2*n)
    need(pivots == list(range(n)), 'Invertible ordinary interface')
    need([row[:n] for row in reduced] == identity(n), 'Ordinary inverse left block')
    answer = [row[n:] for row in reduced]
    need(matmul(matrix, answer) == identity(n), 'Literal ordinary inverse product')
    return answer


def query_word():
    # Direct transcription of sites() and the odd/odd branch of thin_vectors().
    # Both arm lengths are nine, hence twenty fields and three bridge queries.
    out = []
    for i in range(9):
        x = vec({A: 1, F[i]: 1, **{F[j]: 2 for j in range(i)}})
        y = vec({A: 1, F[i]: -1})
        out.append((x, y, 'L', i))
    for a, u, p, q in ((0, 1, 0, 1), (-1, 2, 1, 0), (-1, 3, 1, -1)):
        x, y = [Q(0)]*N, [Q(0)]*N
        x[A], y[A] = Q(a), Q(u)
        for j, f in enumerate(F):
            x[f], y[f] = Q(a+1), Q((1-u)*(-1)**j)
        for j, h in enumerate(reversed(H)):
            x[h], y[h] = Q(1-a), Q((u-1)*(-1)**j)
        x[EMPTY], y[EMPTY] = Q(q), Q(p)
        out.append((x, y, 'Q', len(out)-9))
    for i in range(9):
        x = vec({A: -1, H[i]: 1, **{H[j]: 2 for j in range(i+1, 9)}})
        y = vec({A: 1, H[i]: 1})
        out.append((x, y, 'R', i))
    need(len(out) == 21, 'Twenty-one normalized queries')
    for i, (x, y, _, _) in enumerate(out):
        for j, (z, _, _, _) in enumerate(out):
            need(dot(y, z) == Q((i > j)-(i < j)), 'Complete integer sign Gram')
    return out


QUERIES = query_word()


def masks(p, q):
    out = []
    for i in range(9):
        s = {A, *F[:i+1]}
        if i >= p:
            s.update(H[9-q:])
        out.append(s)
    for i in range(9):
        s = {A, *H[i:]}
        if i < 9-q:
            s.update(F[:p])
        out.append(s)
    return out


def sparse_basis(rows, support):
    return [{str(support[j]): str(v) for j, v in enumerate(row) if v} for row in rows]


def pairing_capacities(p, q):
    stage_masks = masks(p, q)
    records = []
    for a, b in INTERVALS:
        support = sorted(set.intersection(*stage_masks[a:b+1]))
        query_range = range(FULL_SITES[a], FULL_SITES[b]+1)
        primal_equations = [[QUERIES[k][1][f] for f in support] for k in query_range]
        dual_equations = [[QUERIES[k][0][f] for f in support] for k in query_range]
        primal = nullspace(primal_equations, len(support))
        dual = nullspace(dual_equations, len(support))
        pairing = [[dot(gamma, phi) for phi in primal] for gamma in dual]
        cap = len(rref(pairing, len(primal))[1])
        records.append({'interval': [a, b], 'support': support,
                        'primal_basis': sparse_basis(primal, support),
                        'dual_basis': sparse_basis(dual, support),
                        'pairing': [[str(z) for z in row] for row in pairing],
                        'capacity': cap})
    # Enlarging an interval cannot increase its common pairing capacity.
    for i, (a, b) in enumerate(INTERVALS):
        for j, (c, d) in enumerate(INTERVALS):
            if a <= c and d <= b:
                need(records[i]['capacity'] <= records[j]['capacity'], 'Nested interval capacity')
    targets = Counter(1+8*sum(f in s for s in stage_masks) for f in range(N))
    return records, [len(s)-2 for s in stage_masks], targets


def apply_rank_one(matrix, phi, gamma, multiplier):
    # Left multiplication by I + multiplier * phi * gamma.
    row = [sum((gamma[i]*matrix[i][j] for i in range(N)), Q(0)) for j in range(N)]
    return [[matrix[i][j] + multiplier*phi[i]*row[j] for j in range(N)] for i in range(N)]


def apply_query(matrix, index, sign):
    x, y = QUERIES[index][:2]
    return apply_rank_one(matrix, x, y, Q(sign-1))


def target_matrix(stage_masks, sign):
    out = [[Q(0)]*N for _ in range(N)]
    for f in range(N):
        value = Q(sign)
        for i, s in enumerate(stage_masks):
            if f in s:
                value *= D[i]
        out[f][f] = value
    return out


def direct_stage_replay(p, q):
    stage_masks = masks(p, q)
    stage_at = {k: i for i, k in enumerate(FULL_SITES)}
    for sign in (1, -1):
        current = identity()
        query_prefix = identity()
        for k in range(21):
            current = apply_query(current, k, sign)
            query_prefix = apply_query(query_prefix, k, sign)
            if k not in stage_at:
                continue
            i = stage_at[k]
            s = stage_masks[i]
            x, y = QUERIES[k][:2]
            need(all(not x[f] or f in s for f in range(N)), 'Query column support')
            need(all(not y[f] or f in s for f in range(N)), 'Query row support')
            need(all(not query_prefix[a][b] for a in range(N) for b in range(N)
                     if (a in s) != (b in s)), 'Full prefix commutation')
            for f in s:
                current[f] = [D[i]*z for z in current[f]]
        expected = target_matrix(stage_masks, sign)
        need(current == expected, 'All twenty arbitrary-input columns for staged word')
        need(query_prefix == [[Q(sign*(a == b)) for b in range(N)] for a in range(N)], 'Normalized root endpoint')
    return {'mask': [p, q], 'signs': [1, -1], 'independent_columns_per_sign': N,
            'stage_multipliers': [str(z) for z in D]}


def jobs():
    f, u, v = F[0], H[7], H[8]
    out = [
        ('cross_1', vec({f: 1, v: 1}), vec({A: 2, f: -1, u: -1, v: 2}), 1, 15),
        ('cross_2', vec({f: -1, u: 1}), vec({A: 2, f: -1, v: 1}), 1, 15),
        ('left_remainder', vec({f: 1, u: 1, v: 1}), vec({A: -2, f: 1, u: 1, v: -1}), 1, 8),
        ('right_remainder', vec({f: 1, u: 1, v: 1}), vec({f: 1, u: 1, v: -1}), 9, 15),
        ('right_boundary', vec({v: 1}), vec({A: 2, v: 1}), 16, 16),
    ]
    for j in range(1, 8):
        out.append((f'left_{j}', vec({F[j]: 1}), vec({F[j]: 1, A: -2}), j+1, 8))
    for j in range(1, 7):
        out.append((f'right_{j}', vec({H[j]: 1}), vec({H[j]: 1, A: 2}), 9, 8+j))
    need(len(out) == 18, 'Eighteen whole idle jobs')
    return out


def explicit_replay(omit_job=None, idle_jobs_override=None):
    idle_jobs = jobs() if idle_jobs_override is None else idle_jobs_override
    stage_masks = masks(1, 2)
    active = []
    basis_height = 0
    for name, phi, gamma, a, b in idle_jobs:
        need(dot(gamma, phi) == 1, 'Unit idle duality: '+name)
        for i in range(a, b+1):
            need(all((not phi[f] and not gamma[f]) or f in stage_masks[i] for f in range(N)), 'Idle support: '+name)
        for k in range(FULL_SITES[a], FULL_SITES[b]+1):
            x, y = QUERIES[k][:2]
            need(dot(y, phi) == dot(gamma, x) == 0, 'Idle actual-query annihilation: '+name)
    for i, s in enumerate(stage_masks):
        covered = [job for job in idle_jobs if job[3] <= i <= job[4]]
        need(len(covered) == len(s)-2, 'All idle dimensions covered')
        for j, first in enumerate(covered):
            for k, second in enumerate(covered):
                need(dot(first[2], second[1]) == int(j == k), 'Overlapping idle duality')
        a = [[Q(r == c and r in s)-sum(job[1][r]*job[2][c] for job in covered)
              for c in range(N)] for r in range(N)]
        x, y = QUERIES[FULL_SITES[i]][:2]
        need(matmul(a, a) == a and len(rref(a, N)[1]) == 2, 'Active native rank-two projector')
        need([dot(row, x) for row in a] == x, 'Active projector fixes native column')
        need([dot(y, col) for col in zip(*a)] == y, 'Active projector fixes native row')
        w = [row[A] for row in a]
        need(dot(y, w) == 1, 'Active plane standard interface')
        columns = [x, w] + [job[1] for job in covered] + [vec({f: 1}) for f in range(N) if f not in s]
        basis = [list(row) for row in zip(*columns)]
        inv = inverse(basis)
        need(all(z.denominator == 1 for row in basis+inv for z in row), 'Integral ordinary basis and inverse')
        basis_height = max(basis_height, max(abs(z.numerator).bit_length() for row in basis+inv for z in row))
        active.append(a)
    stage_at = {k: i for i, k in enumerate(FULL_SITES)}
    event_report = []
    for sign in (1, -1):
        current = identity()
        for k in range(21):
            current = apply_query(current, k, sign)
            if k not in stage_at:
                continue
            i = stage_at[k]
            native = [[Q(r == c)+(D[i]-1)*active[i][r][c] for c in range(N)] for r in range(N)]
            current = matmul(native, current)
            for name, phi, gamma, a, b in idle_jobs:
                if a != i or name == omit_job:
                    continue
                whole = Q(1)
                for j in range(a, b+1):
                    whole *= D[j]
                current = apply_rank_one(current, phi, gamma, whole-1)
                if sign == 1:
                    event_report.append({'name': name, 'executed_at_full_stage': i,
                                         'covered': [a, b], 'rank': 8*(b-a+1),
                                         'whole_multiplier': str(whole)})
        need(current == target_matrix(stage_masks, sign), 'Literal first-stage whole-idle schedule, all twenty columns')
    paid = Counter(8*(job[4]-job[3]+1) for job in idle_jobs)
    paid[1] += 3
    return paid, {'whole_idle_jobs': len(idle_jobs), 'signs': [1, -1],
                  'columns_per_sign': N, 'native_active_planes': 18,
                  'integral_basis_max_numerator_bits': basis_height,
                  'schedule': event_report}


LOG_TERMS = 120
EXP_TERMS = 20


def positive_log_series(z):
    # -log(1-z) = sum_{j>=1} z^j/j; after N terms the tail is at most
    # z^(N+1)/((N+1)*(1-z)), since every omitted denominator is >= N+1.
    need(0 <= z <= Q(1, 2), 'Positive log-series domain')
    total = Q(0)
    power = Q(1)
    for j in range(1, LOG_TERMS+1):
        power *= z
        total += power/j
    tail = power*z/((LOG_TERMS+1)*(1-z))
    return total, total+tail


def positive_exp_series(z):
    # exp(z) has positive terms. All omitted term ratios after term N+1
    # are <= z/(N+2), so a geometric tail bounds the remainder above.
    need(0 <= z < 1, 'Positive exponential-series domain')
    total = term = Q(1)
    for j in range(1, EXP_TERMS+1):
        term *= z/j
        total += term
    first = term*z/(EXP_TERMS+1)
    return total, total+first/(1-z/(EXP_TERMS+2))


@lru_cache(None)
def power_bounds(r):
    if r == 0:
        return Q(0), Q(0)
    need(isinstance(r, int) and r > 0, 'Positive integer request rank')
    k = r.bit_length()-1
    # log(r)=k log(2)+log(r/2^k), both represented by positive series.
    l2, h2 = positive_log_series(Q(1, 2))
    lm, hm = positive_log_series(1-Q(2**k, r))
    loglo, loghi = k*l2+lm, k*h2+hm
    exp_lower = positive_exp_series(C*loglo)[0]
    exp_upper = positive_exp_series(C*loghi)[1]
    return Q(r)/exp_upper, Q(r)/exp_lower


def moment(histogram):
    lo = hi = Q(0)
    for r, count in histogram.items():
        a, b = power_bounds(r)
        lo += count*(a if count >= 0 else b)
        hi += count*(b if count >= 0 else a)
    return lo, hi


def outward(value, upper, places=27):
    scale = 10**places
    q, remainder = divmod(value.numerator*scale, value.denominator)
    if upper and remainder:
        q += 1
    sign = '-' if q < 0 else ''
    q = abs(q)
    integer, frac = divmod(q, scale)
    return f'{sign}{integer}.{frac:0{places}d}'


def interval_text(bounds):
    return [outward(bounds[0], False), outward(bounds[1], True)]


def hist_text(histogram):
    return {str(k): v for k, v in sorted(histogram.items()) if v}


def pinned_profile(package, native_path):
    pin_path = package/'retained/SOURCE-PINS.json'
    if not pin_path.exists():
        pin_path = package/'SOURCES.json'
    manifest = json.loads(pin_path.read_text())
    need(manifest['source_head'] == SOURCE_HEAD, 'Pinned source head')
    for pin in manifest['files']:
        raw = (package/pin['retained_path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Retained SHA256')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'Retained Git blob')
    constants = {}
    parsed = ast.parse((package/'retained/pricing.py').read_text())
    for node in parsed.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('HELPERS', 'LOCAL_PAID'):
                    constants[target.id] = Counter(ast.literal_eval(node.value))
    need(set(constants) == {'HELPERS', 'LOCAL_PAID'}, 'Complete native profile constants')
    report = {'helpers': hist_text(constants['HELPERS']), 'paid': hist_text(constants['LOCAL_PAID']), 'native_word_recounted': False}
    if native_path is not None:
        w = json.loads(gzip.decompress(native_path.read_bytes()))
        payload = {k: v for k, v in w.items() if k != 'verifier_profile'}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        need(digest == NATIVE_PAYLOAD, 'Exact #6824 native payload')
        dims = [len(basis) for basis in w['frames']]
        main = set(w['live']) | {r+112 for r in w['live']}
        helpers = Counter(dims[w['final'][r]]-dims[w['initial'][r]] for r in range(w['public']) if r not in main)
        paid = Counter(abs(dims[e[3]]-dims[e[2]]) for e in w['program'] if e[0] == 'MOVE')
        need(helpers == constants['HELPERS'] and paid == constants['LOCAL_PAID'], 'Literal helper and all-MOVE census equals retained pricing')
        report.update({'native_word_recounted': True, 'native_payload_sha256': digest,
                       'helper_count': sum(helpers.values()), 'paid_move_count': sum(paid.values())})
    return constants['HELPERS'], constants['LOCAL_PAID'], report


def complete_gain(helpers, local, targets, paid):
    h = Counter({r: 18*n for r, n in helpers.items()})
    for r, n in local.items():
        h[r] -= 18*n
    for r, n in targets.items():
        h[r] += 104*n
    for r, n in paid.items():
        h[r] -= 104*n
    return moment(h)


def dual_audit(case, capacity_records, demands, targets, helpers, local):
    need(isinstance(case['scale'], int) and case['scale'] > 0, 'Positive rational dual scale')
    scale = case['scale']
    need(all(str(int(k)) == k and 0 <= int(k) < len(INTERVALS) for k in case['alpha']), 'All dual alpha indices are recognized')
    need(all(isinstance(v, int) for v in case['alpha'].values()), 'Integer alpha numerators')
    need(len(case['beta']) == 18 and all(isinstance(v, int) for v in case['beta']), 'Eighteen integer beta numerators')
    alpha = [Q(case['alpha'].get(str(i), 0), scale) for i in range(len(INTERVALS))]
    beta = [Q(v, scale) for v in case['beta']]
    need(all(v <= 0 for v in alpha), 'Dual signs')
    slacks = []
    for a, b in INTERVALS:
        lhs = sum(alpha[j] for j, (c, d) in enumerate(INTERVALS) if a <= c <= d <= b)
        lhs += sum(beta[a:b+1])
        cost = power_bounds(8*(b-a+1))
        need(lhs <= cost[0], 'Exact dual inequality for interval '+str((a, b)))
        slacks.append(cost[0]-lhs)
    lower_idle = sum(a*r['capacity'] for a, r in zip(alpha, capacity_records)) + dot(beta, demands)
    native_hist = Counter({r: 18*n for r, n in helpers.items()})
    for r, n in local.items():
        native_hist[r] -= 18*n
    native = moment(native_hist)
    target = moment(targets)
    upper = native[1]+104*(target[1]-3-lower_idle)
    need(upper < 0, 'Complete favorable dual bill is strictly negative')
    return {'mask': [case['p'], case['q']], 'intervals': len(INTERVALS), 'dual_columns': len(slacks),
            'idle_demands': demands, 'targets': hist_text(targets),
            'paid_idle_lower_bound_exact': str(lower_idle),
            'minimum_dual_slack_lower': outward(min(slacks), False),
            'complete_gain_upper_bound': outward(upper, True)}


def rejected(callback, expected_message):
    try:
        callback()
    except ValueError as error:
        need(expected_message in str(error), 'Negative control failed for an unrelated reason')
        return True
    raise ValueError('Negative control was accepted: '+expected_message)


def controls(case, records, demands, targets, helpers, local):
    # Nonzero primal/dual nullspaces can pair to zero; their dimensions alone
    # do not count an invertible idle projector.
    primal = nullspace([[1, 0]], 2)
    dual = nullspace([[0, 1]], 2)
    pair = [[dot(g, f) for f in primal] for g in dual]
    need(len(primal) == len(dual) == 1 and len(rref(pair, 1)[1]) == 0, 'Degenerate pairing control')
    # The unchanged source line fails on the opposite arm.
    gamma = vec({A: -2, F[0]: 1})
    need(dot(gamma, QUERIES[12][0]) == 2, 'Unchanged source idle opposite-arm defect')
    # The independently bounded tariff is exact at rank one.
    need(power_bounds(1) == (Q(1), Q(1)), 'Rank-one power control')
    bad_jobs = jobs()
    name, phi, gamma, a, b = bad_jobs[0]
    bad_gamma = list(gamma)
    bad_gamma[A] = 0
    bad_jobs[0] = (name, phi, bad_gamma, a, b)
    bad_dual = json.loads(json.dumps(case))
    bad_dual['beta'][0] += 1000*bad_dual['scale']
    return {'nonzero_nullspaces_zero_pairing': True, 'unchanged_source_line_fails': True,
            'rank_one_power_exact': True,
            'missing_cross_dual_hub_coefficient_rejected': rejected(lambda: explicit_replay(idle_jobs_override=bad_jobs), 'Idle actual-query annihilation'),
            'omitted_whole_idle_rejected_by_literal_endpoint': rejected(lambda: explicit_replay(omit_job='cross_1'), 'Literal first-stage whole-idle schedule'),
            'inflated_dual_rejected': rejected(lambda: dual_audit(bad_dual, records, demands, targets, helpers, local), 'Exact dual inequality')}



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--native-word', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    begun = time.monotonic()
    helpers, local, native_report = pinned_profile(args.package, args.native_word)
    certificate = json.loads((args.package/'certificate.json').read_text())
    need(Q(certificate['C']) == C, 'Fixed exact C')
    need([(case['p'], case['q']) for case in certificate['cases']] == [(4, 4), (1, 2)], 'Two declared masks')
    stage_reports = [direct_stage_replay(*pq) for pq in ((0, 0), (4, 4), (1, 2))]
    explicit_paid, literal_report = explicit_replay()
    print('LITERAL_SCHEDULE_PASS', literal_report['whole_idle_jobs'], 'jobs, both signs, twenty columns', flush=True)
    all_capacities = {}
    target_tables = {}
    demand_tables = {}
    for p, q in ((0, 0), (4, 4), (1, 2)):
        records, demands, targets = pairing_capacities(p, q)
        all_capacities[f'{p},{q}'] = records
        target_tables[p, q] = targets
        demand_tables[p, q] = demands
    baseline = all_capacities['0,0']
    need(all(r['capacity'] == 0 for r in baseline if r['interval'][0] <= 8 < r['interval'][1]), 'All eighty-one original bridge intervals have zero capacity')
    need(all_capacities['1,2'][INTERVALS.index((1, 15))]['capacity'] == 2, 'Two small mixed carriers')
    need(all_capacities['4,4'][INTERVALS.index((4, 13))]['capacity'] == 6, 'Six large mixed carriers')
    print('EXPLICIT_PAIRING_BASES_PASS', 342, 'modified capacities plus', 171, 'baseline capacities', flush=True)
    dual_reports = [dual_audit(case, all_capacities[f"{case['p']},{case['q']}"], demand_tables[case['p'], case['q']], target_tables[case['p'], case['q']], helpers, local) for case in certificate['cases']]
    original_paid = Counter({8*i: 2 for i in range(1, 9)})
    original_paid[1] = 3
    source_gain = complete_gain(helpers, local, target_tables[0, 0], original_paid)
    explicit_gain = complete_gain(helpers, local, target_tables[1, 2], explicit_paid)
    need(Q('-7.34153e-10') < source_gain[0] <= source_gain[1] < Q('-7.34151e-10'), 'Independent source complete bill calibration')
    need(Q('-45.137633381995714') < explicit_gain[0] <= explicit_gain[1] < Q('-45.137633381995712'), 'Independent explicit complete bill')
    report = {'schema': 'independent-mixed-transport-audit/1', 'claim': 'Finite algebra and complete signed budgets at one C only; no new kappa',
              'source_head': SOURCE_HEAD, 'C': str(C), 'no_external_code_imports': True,
              'capacity_method': 'Explicit ker(Y) and ker(X transpose) bases, followed by rank of their pairing matrix; no four-rank formula',
              'power_method': {'log': 'positive -log(1-z) series and geometric tail', 'log_terms': LOG_TERMS,
                               'exponential': 'positive exp(z) series and geometric tail, then reciprocal', 'exp_terms': EXP_TERMS},
              'native_census': native_report, 'stage_replays': stage_reports, 'first_stage_idle_replay': literal_report,
              'modified_interval_capacities_checked': 342, 'additional_baseline_capacities_checked': 171,
              'capacity_records': all_capacities, 'dual_bills': dual_reports,
              'source_complete_gain': interval_text(source_gain), 'explicit_complete_gain': interval_text(explicit_gain),
              'explicit_paid': hist_text(explicit_paid),
              'controls': controls(certificate['cases'][0], all_capacities['4,4'], demand_tables[4, 4], target_tables[4, 4], helpers, local),
              'runtime_seconds': round(time.monotonic()-begun, 6)}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print('PASS_INDEPENDENT_MIXED_TRANSPORT_AUDIT', json.dumps({'dual_bills': dual_reports, 'source_gain': report['source_complete_gain'], 'explicit_gain': report['explicit_complete_gain'], 'seconds': report['runtime_seconds']}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
