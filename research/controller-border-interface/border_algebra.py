#!/usr/bin/env python3
"""Exact no-idle controller identity and exploratory border-profile pricing.

Apache-2.0; Dillon with substantial OpenAI assistance. The literal source
controller is credited to zxv / Cinna Davis and its retained predecessor chain.
Floating-point root estimates below are discovery evidence, not certificates.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import ast
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research/kappa-rebuild/bit/complex_controller_factor.py'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reference_functions():
    """Load only three pure functions; no source imports or external loaders."""
    tree = ast.parse(SOURCE.read_text())
    wanted = {'plus', 'monomial_times', 'controller'}
    body = [node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in wanted]
    need({node.name for node in body} == wanted, 'Exact reference function set')
    space = {'Q': Q}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(SOURCE), 'exec'), space)
    return space


def thin_reference(p, wrong_reverse_sign=False):
    source = reference_functions()
    coeff, events, idles = source['controller'](p, 0, wrong_reverse_sign)
    need(not any(e[0] == 'IDLE' for e in events), 'Every whole idle omitted')
    thick = {0, 2*p, *range(1, 2*p, 2)}
    out = {}
    for term, matrix in coeff.items():
        key = (term[0],)+tuple(x if s in thick else 0
                              for s, x in enumerate(term[1:]))
        target = out.setdefault(key, [[Q(0)]*(2*p) for _ in range(2*p)])
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                target[i][j] += value
    return {k: v for k, v in out.items() if any(any(row) for row in v)}


def formula(p):
    """Independent closed formula in the original Q,D_0,...,D_(2p) variables."""
    need(p >= 1, 'At least one pair')
    size = 2*p
    width = 2*p+2
    zero = (0,)*width
    stages = [[0, 1, 2]] if p == 1 else (
        [[0, 1]]+[[2*j+1] for j in range(1, p-1)]+[[2*p-1, 2*p]])
    ds = [tuple(int(s in selected) for s in range(2*p+1)) for selected in stages]
    out = {}

    def put(i, j, q, factors, value):
        term = (q,)+tuple(sum(ds[k][s] for k in factors) for s in range(2*p+1))
        matrix = out.setdefault(term, [[Q(0)]*size for _ in range(size)])
        matrix[i][j] += value

    for i in range(p):
        put(2*i, 2*i, -1, [i], 1)
        put(2*i+1, 2*i+1, 1, [i], 1)
        for j in range(i+1, p):
            sign = (-1)**(j-i-1)
            put(2*i, 2*j, -1, [], sign)
            put(2*i, 2*j, -1, [j], -sign)
        for j in range(i):
            sign = (-1)**(i-j-1)
            put(2*i+1, 2*j+1, 1, range(j, i), sign)
            put(2*i+1, 2*j+1, 1, range(j, i+1), -sign)
    return {k: v for k, v in out.items() if any(any(row) for row in v)}


def weighted_limit(coeff, p, reverse=False):
    weights = [j if parity == 0 else p-1-j for j in range(p) for parity in (0, 1)]
    if reverse:
        weights = [-x for x in weights]
    constant = {}
    degrees = set()
    for term, matrix in coeff.items():
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                if not value:
                    continue
                degree = weights[j]-weights[i]
                need(degree >= 0, 'No negative border degree')
                need(i == j or degree > 0, 'Every off-diagonal term vanishes')
                degrees.add(degree)
                if degree == 0:
                    constant.setdefault(term, [[Q(0)]*(2*p) for _ in range(2*p)])[i][j] += value
    return constant, sorted(degrees)



def decoder_check(p):
    def multiply(a, b):
        return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]
    def rank(matrix):
        work = [[Q(x) for x in row] for row in matrix]
        pivots = 0
        for j in range(p):
            chosen = next((i for i in range(pivots, p) if work[i][j]), None)
            if chosen is None:
                continue
            work[pivots], work[chosen] = work[chosen], work[pivots]
            factor = work[pivots][j]
            work[pivots] = [x/factor for x in work[pivots]]
            for i in range(p):
                if i != pivots:
                    factor = work[i][j]
                    work[i] = [a-factor*b for a, b in zip(work[i], work[pivots])]
            pivots += 1
        return pivots
    identity = [[int(i == j) for j in range(p)] for i in range(p)]
    S = [[(-1)**(j-i-1) if i < j else 0 for j in range(p)] for i in range(p)]
    M = [[int(i == j)+int(j == i+1) for j in range(p)] for i in range(p)]
    N = [[-int(j == i+1) for j in range(p)] for i in range(p)]
    IS = [[identity[i][j]-S[i][j] for j in range(p)] for i in range(p)]
    need(multiply(M, IS) == identity, 'Unique decoder coefficient on every d_j')
    MS = multiply(M, S)
    need(all(MS[i][j]+N[i][j] == 0 for i in range(p) for j in range(p)), 'Exact copied-input correction')
    need(rank(N) == p-1, 'Fresh-query correction rank')
    if p > 1:
        wrong = [row[:] for row in N]
        wrong[0][1] = 0
        need(any(MS[i][j]+wrong[i][j] != 0 for i in range(p) for j in range(p)), 'Missing query correction rejected')
    return {'fresh_query_rank': p-1, 'scalar_additions': 2*(p-1),
            'owned_saved_fields': p-1, 'missing_query_rejected': p > 1}


def main_profile(p, block, ports):
    return Counter({1+3*block: 2*ports}) if p == 1 else Counter(
        {1+2*block: 4*ports, 1+block: 2*(p-2)*ports})


def local_profiles():
    complex_data = json.loads((ROOT/'research/joint-helper-lattice/RESULT.json').read_text())
    bit = json.loads((ROOT/'research/query-thinned-controllers/BIT-CONTROLLER.json').read_text())['invoice']
    full, thin = bit['thick_calls'], bit['thin_queries']
    bt, bp = Counter({int(k): v for k, v in bit['targets'].items()}), Counter({int(k): v for k, v in bit['paid'].items()})
    bt.subtract({int(k): v for k, v in bit['main'].items()})
    bp.subtract({int(k): v for k, v in bit['whole_idle'].items()})
    bp[1] -= thin
    need(all(v >= 0 and v % full == 0 for v in [*bt.values(), *bp.values()]), 'Integral BIT local source decomposition')
    return {
        'complex': (8, 112, {int(k): v for k, v in complex_data['local_helpers'].items()},
                    {int(k): v for k, v in complex_data['local_paid'].items()}),
        'bit': (7, 111, {k: v//full for k, v in bt.items() if v},
                {k: v//full for k, v in bp.items() if v})}


def profiles(p, kind, locals_):
    block, ports, helpers, paid = locals_[kind]
    targets = Counter({k: (p+2)*v for k, v in helpers.items()})
    targets.update(main_profile(p, block, ports))
    bill = Counter({k: (p+2)*v for k, v in paid.items()})
    bill[1] += ports*(p-1)
    need(sum(k*v for k, v in targets.items())-sum(k*v for k, v in bill.items()) == 48*(p+2)-ports,
         'No-idle rank-mass identity')
    return +targets, +bill



def correction_moment_certificate(locals_):
    certificates = {}
    for kind, (_, ports, _, _) in locals_.items():
        cumulative = []
        for p in (2, 3, 4):
            targets, paid = profiles(p, kind, locals_)
            paid[1] += ports*(p-1)
            total, row = 0, {}
            for r in sorted(set(targets) | set(paid)):
                total += r*(paid[r]-targets[r])
                row[r] = total
            cumulative.append(row)
        base, second, third = cumulative
        need(base.keys() == second.keys() == third.keys(), 'Constant corrected support')
        rows = []
        for r, value in base.items():
            slope = second[r]-value
            need(value > 0 and slope > 0, 'Positive cumulative rank-mass for every p>=2')
            need(third[r] == value+2*slope, 'Affine count control')
            rows.append({'rank': r, 'at_p2': value, 'slope_in_p': slope})
        certificates[kind] = rows
    return certificates


def estimate_root(targets, paid):
    def margin(c):
        return sum(v*k**(1-c) for k, v in targets.items())-sum(v*k**(1-c) for k, v in paid.items())
    lo, hi = 0., .2
    need(margin(lo) > 0 and margin(hi) < 0, 'Discovery root bracket')
    for _ in range(54):
        mid = (lo+hi)/2
        if margin(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def run():
    cases = []
    for p in range(1, 9):
        actual = thin_reference(p)
        need(actual == formula(p), 'Full exact Laurent formula, p='+str(p))
        size = 2*p
        total = [[sum(m[i][j] for m in actual.values()) for j in range(size)] for i in range(size)]
        need(total == [[Q(i == j) for j in range(size)] for i in range(size)], 'A(1)=identity; no normalization needed')
        limit, degrees = weighted_limit(actual, p)
        need(sum(sum(m[i][i] for m in limit.values()) for i in range(size)) == size, 'Full diagonal rank')
        need(max(degrees) == p-1, 'Exact border degree')
        # Reduction mod 2 is coefficientwise; no complex-to-BIT native lift is claimed.
        need(all(x.denominator == 1 for m in actual.values() for row in m for x in row), 'Integral identity reduces to characteristic two')
        need(thin_reference(p, True) != actual, 'Incorrect reverse sign is rejected over Q')
        if p > 1:
            try:
                weighted_limit(actual, p, reverse=True)
            except ValueError:
                pass
            else:
                raise ValueError('Reversed scaling must be rejected')
        cases.append({'pairs': p, 'laurent_coefficients': len(actual), 'border_degree': p-1,
                      'exact_formula': True, 'integral_reduction': True, 'decoder': decoder_check(p)})
    locals_ = local_profiles()
    sweep = []
    for p in range(1, 65):
        row = {'pairs': p}
        for kind in locals_:
            targets, paid = profiles(p, kind, locals_)
            block, ports, helpers, _ = locals_[kind]
            main = main_profile(p, block, ports)
            mean = sum(k*v for k, v in main.items())/sum(main.values())
            optimistic = Counter({k: (p+2)*v for k, v in helpers.items()})
            optimistic[mean] += sum(main.values())
            row[kind] = {'raw_border_root_estimate': estimate_root(targets, paid),
                         'balanced_main_root_estimate': estimate_root(optimistic, paid)}
            if p == 16:
                row[kind].update(targets=dict(sorted(targets.items())), paid=dict(sorted(paid.items())))
        sweep.append(row)
    return {'status': 'PASS_EXACT_NO_IDLE_BORDER_ALGEBRA', 'cases': cases,
            'root_evidence': 'floating-point discovery only; no certified kappa or admitted supplier',
            'sweep': sweep, 'corrected_all_moment_certificate': correction_moment_certificate(locals_)}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
