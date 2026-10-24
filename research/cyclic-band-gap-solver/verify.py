"""Check variable-gap cyclic solves with exact independent arithmetic.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from solver import factor, solve, budget, need


def oracle(rows, p, rhs):
    n = len(rows); scale = 1 << p
    a = [[Q(rows[i].get(j, 0), scale) for j in range(n)]+[Q(rhs[i][c], scale) for c in (0, 1)] for i in range(n)]
    for k in range(n):
        pivot = max(range(k, n), key=lambda i: abs(a[i][k]))
        need(a[pivot][k] != 0, 'oracle singular')
        a[k], a[pivot] = a[pivot], a[k]
        d = a[k][k]; a[k] = [x/d for x in a[k]]
        for i in range(n):
            if i != k:
                c = a[i][k]; a[i] = [x-c*y for x, y in zip(a[i], a[k])]
    return [row[n:] for row in a]


def fixture(n, width, p, gap_power, signed):
    rng = random.Random(n*100+width*10+gap_power)
    s = 1 << p; gap = 1 << (p-gap_power)
    rows = []
    for i in range(n):
        neighbors = sorted({(i+j)%n for j in range(-width, width+1)}-{i})
        row = {i:s}
        if neighbors:
            mass, rem = divmod(s-gap, len(neighbors))
            for k, j in enumerate(neighbors):
                value = mass+(k < rem)
                row[j] = value*(rng.choice((-1, 1)) if signed else -1)
        rows.append(row)
    return rows


def factor_checks(rows, p, factors):
    n = len(rows); s = 1 << factors['plan']['bits']; plan = factors['plan']
    lower, upper = factors['lower'], factors['upper']
    maximum_residual = Q(0)
    for i in range(n):
        product = {j: Q(x, s) for j, x in upper[i].items()}
        for k, a in lower[i].items():
            for j, b in upper[k].items(): product[j] = product.get(j, Q(0))+Q(a*b, s*s)
        for j, a in rows[i].items(): product[j] = product.get(j, Q(0))-Q(a, 1 << p)
        maximum_residual = max(maximum_residual, sum(map(abs, product.values())))
    need(maximum_residual <= plan['factor_residual'], 'factor residual exceeds theorem')
    need(max(1+sum(abs(x) for x in row.values())/Q(s) for row in lower) <= plan['lower_norm'], 'lower norm bound')
    need(max(sum(abs(x) for x in row.values())/Q(s) for row in upper) <= plan['upper_norm'], 'upper norm bound')
    need(all(Q(row[i]-sum(abs(x) for j, x in row.items() if j != i), s) >= plan['delta']/2
             for i, row in enumerate(upper)), 'upper row gap')
    return maximum_residual


def check_case(n, width, gap_power, signed, use_oracle=True):
    p = max(8, gap_power); rows = fixture(n, width, p, gap_power, signed)
    delta = Q(1, 1 << gap_power); tolerance = Q(1, 1 << 20)
    original = deepcopy(rows)
    f = factor(rows, p, width, delta, 2, 1, tolerance)
    residual = factor_checks(rows, p, f)
    rhs_set = [[((1 << p), 0)]*n,
               [(((-1)**i)*(1 << (p-1)), ((-1)**(i//2))*(1 << (p-1))) for i in range(n)]]
    worst = Q(0); max_bits = f['statistics']['peak_integer_bits']
    for rhs in rhs_set:
        saved = deepcopy(rhs); x, counts = solve(f, rhs, p); scale = 1 << f['plan']['bits']
        need(rhs == saved and rows == original, 'input changed')
        exact = oracle(rows, p, rhs) if use_oracle else None
        for i in range(n):
            if exact is not None:
                error = sum(abs(Q(x[i][c], scale)-exact[i][c]) for c in (0, 1))
                need(error <= f['plan']['error'] <= tolerance, 'oracle error exceeds theorem')
                worst = max(worst, error)
        # A separate residual bound gives a rigorous error certificate at every size.
        defect = max(sum(abs(sum(Q(a*x[j][c], (1 << p)*scale) for j, a in row.items())-Q(rhs[i][c], 1 << p))
                         for c in (0, 1)) for i, row in enumerate(rows))
        need(defect/delta <= tolerance, 'original-matrix residual fails target')
        max_bits = max(max_bits, counts['peak_integer_bits'])
    return {'n': n, 'width': width, 'gap': str(delta), 'signed': signed,
            'fraction_bits': f['plan']['bits'], 'word_bits': f['plan']['word_bits'],
            'observed_peak_integer_bits': max_bits, 'factor_residual': str(residual),
            'error_bound': str(f['plan']['error']), 'oracle_max_error': str(worst) if use_oracle else None,
            'factor': f['statistics'], 'solve': counts}


def reject(call):
    try: call()
    except ValueError: return
    raise ValueError('control accepted')


def controls():
    rows = fixture(9, 1, 8, 4, False)
    args = (8, 1, Q(1, 16), 2, 1, Q(1, 1 << 20))
    bad = deepcopy(rows); bad[0][4] = 1
    reject(lambda: factor(bad, *args))
    bad = deepcopy(rows); bad[0][0] = 0
    reject(lambda: factor(bad, *args))
    reject(lambda: factor(rows, 8, 1, Q(1, 2), 2, 1, Q(1, 1 << 20)))
    reject(lambda: factor(rows, 8, 1, Q(1, 16), 1, 1, Q(1, 1 << 20)))
    reject(lambda: budget(9, 0, 2, 1, Q(1, 2), 8))
    f = factor(rows, *args)
    reject(lambda: solve(f, [(257, 0)]*9, 8))
    reject(lambda: solve(f, [(1, 0)]*9, f['plan']['bits']+1))
    rhs = [(256, 0)]*9
    x, _ = solve(f, rhs, 8)
    scale = 1 << f['plan']['bits']
    # An ordinary-band replacement changes the actual cyclic problem.
    dropped = [{j:v for j, v in row.items() if abs(i-j) <= 1} for i, row in enumerate(rows)]
    wrong, _ = solve(factor(dropped, *args), rhs, 8)
    need(wrong != x, 'wrap control is ineffective')
    defect = max(abs(sum(Q(a*wrong[j][0], 256*scale) for j, a in row.items())-1) for row in rows)
    need(defect > Q(1, 1 << 20), 'dropped wrap unexpectedly accepted')
    return 8


def symbolic_fill():
    count = 0
    for n in range(1, 25):
        for width in range(min(n, 6)):
            pat = [[min(abs(i-j), n-abs(i-j)) <= width for j in range(n)] for i in range(n)]
            products = 0
            for k in range(n):
                low = [i for i in range(k+1, n) if pat[i][k]]
                high = [j for j in range(k+1, n) if pat[k][j]]
                need(max(len(low), len(high)) <= 2*width, 'independent symbolic front')
                for i in low:
                    for j in high: pat[i][j] = True; products += 1
            need(products <= 4*n*width**2, 'independent symbolic count')
            count += 1
    return count


def scaled_cases():
    count = 0
    for alpha in (Q(1,8), Q(1), Q(8)):
        for y in (Q(1,8), Q(3), Q(16)):
            p = 12
            rows = [{j:int(alpha*x) for j,x in row.items()} for row in fixture(7,2,p,4,False)]
            f = factor(rows,p,2,alpha/16,2*alpha,y,Q(1,1<<16))
            factor_checks(rows,p,f)
            rhs = [(int(y*(1<<p))*(-1)**i,0) for i in range(7)]
            output,_ = solve(f,rhs,p); exact = oracle(rows,p,rhs)
            need(max(sum(abs(Q(output[i][c],1<<f['plan']['bits'])-exact[i][c]) for c in (0,1))
                     for i in range(7)) <= f['plan']['error'], 'scaled oracle error')
            count += 1
    return count


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--write', action='store_true'); ap.add_argument('--small', action='store_true')
    args = ap.parse_args()
    cases = [check_case(n, width, gap, signed) for n, width in ((1,0),(3,1),(5,2),(8,2),(13,3),(21,4))
             for gap in (1,4,8) for signed in (False,True)]
    report = {'small_cases': len(cases), 'oracle_rhs_checks': 2*len(cases), 'cases': cases,
              'controls': controls(), 'symbolic_fill_shapes': symbolic_fill(), 'scaled_oracle_checks': scaled_cases()}
    if args.small:
        print('PASS_SMALL_CYCLIC_GAP', report['small_cases']); return
    report['large_cases'] = [check_case(n, width, gap, signed, False) for n,width,gap,signed in
                             ((257,4,12,False),(1025,4,12,True),(4097,4,12,False))]
    report['files'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.iterdir())
                       if p.is_file() and p.name != 'RESULT.json'}
    if args.write: (HERE/'RESULT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    else: need(report == json.loads((HERE/'RESULT.json').read_text()), 'receipt drift')
    print('PASS_CYCLIC_BAND_GAP', json.dumps({k:v for k,v in report.items() if k not in ('cases','files')},sort_keys=True))


if __name__ == '__main__': main()
