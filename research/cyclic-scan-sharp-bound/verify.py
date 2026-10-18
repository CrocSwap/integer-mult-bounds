"""Exact independent evidence for PROOF.md; standard library only.

The all-length result is proved in the note, not inferred from this census.
"""
from fractions import Fraction as F
from pathlib import Path
from itertools import product
import argparse
import ast
import hashlib
import importlib.util
import json
import random
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import fixed_scan as fixed

ZERO, ONE = (F(0), F(0)), (F(1), F(0))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def minus(a, b):
    return a[0]-b[0], a[1]-b[1]


def quotient(a, b):
    t = times(a, (b[0], -b[1]))
    d = b[0]**2+b[1]**2
    return t[0]/d, t[1]/d


def norm2(a):
    return a[0]**2+a[1]**2


def exact_inverse(x, bs, direction):
    """Finite geometric inverse: independent of the two-pass scan/closure path.

    W^L = product(b_i) I, so (I-W)^-1 = sum_(j=0)^(L-1) W^j/(1-product(b_i)).
    Every row is evaluated directly from its own cyclic predecessors.
    """
    n = len(x)
    all_product = ONE
    for b in bs:
        all_product = times(all_product, b)
    den = minus(ONE, all_product)
    result = []
    for i in range(n):
        total, weight = ZERO, ONE
        for j in range(n):
            pos = (i-direction*j) % n
            total = plus(total, times(weight, x[pos]))
            weight = times(weight, bs[pos])
        result.append(quotient(total, den))
    return result


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_check():
    source = json.loads((ROOT/'SOURCE.json').read_text())
    for path, pin in source['vendor'].items():
        require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == pin['sha256'],
                'source drift: '+path)
    original = import_file('original_scan', ROOT/'vendor/scan.py')
    # Execute the original weighted scan function without importing its unrelated
    # kernel factorizer. The function AST is unchanged; c is its original arithmetic.
    tree = ast.parse((ROOT/'vendor/weighted.py').read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'scan']
    require(len(nodes) == 1, 'weighted scan extraction')
    namespace = {'c': original, 'F': F}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'vendor/weighted.py', 'exec'), namespace)
    return source, original, namespace['scan'], import_file('old_budgets', ROOT/'vendor/check_budgets.py')


def ceil_log2(n):
    return (n-1).bit_length()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', type=Path)
    args = ap.parse_args()
    source, original, weighted, old_budgets = source_check()
    counts = dict(closed_form_cases=0, residual_cases=0, original_weighted_matches=0,
                  original_constant_matches=0, expanded_admission_cases=0)
    digest = hashlib.sha256()

    def record(value):
        digest.update(json.dumps(value, sort_keys=True, default=str, separators=(',', ':')).encode())
        digest.update(b'\n')

    def check(x, bs, beta, bits, direction, use_residual=False):
        y = fixed.run(x, bs, beta, bits, direction)
        B = max(abs(a)+abs(b) for a, b in x)
        bound = fixed.error_bound(B, beta, bits)
        require(bound <= 4*(B+1)*F(1, 1 << bits)/beta**2, 'bound simplification')
        if use_residual:
            # A residual norm divided by beta bounds forward error for every length.
            residuals = [minus(minus(y[i], times(bs[i], y[(i-direction) % len(x)])), x[i])
                         for i in range(len(x))]
            require(all(norm2(v) <= (beta*bound)**2 for v in residuals), 'residual certificate')
            counts['residual_cases'] += 1
        else:
            exact = exact_inverse(x, bs, direction)
            require(all(norm2(minus(a, b)) <= bound**2 for a, b in zip(y, exact)), 'forward error')
            counts['closed_form_cases'] += 1
        if F(1, 1 << bits) <= beta**2/2:
            require(y == weighted(x, bs, beta, bits, direction), 'original weighted mismatch')
            counts['original_weighted_matches'] += 1
            if all(b == bs[0] for b in bs):
                require(y == original.scan(x, bs[0], beta, bits, direction), 'original constant mismatch')
                counts['original_constant_matches'] += 1
        else:
            counts['expanded_admission_cases'] += 1
        record((x, bs, beta, bits, direction, y))

    # Complete finite domain: variable real coefficients and inputs, L <= 3.
    values = [-F(1), F(0), F(1)]
    coeffs = [-F(1, 2), F(0), F(1, 2)]
    for n in (1, 2, 3):
        for xv in product(values, repeat=n):
            x = [(a, F(0)) for a in xv]
            for bv in product(coeffs, repeat=n):
                bs = [(a, F(0)) for a in bv]
                for bits in (2, 3, 8):
                    for direction in (-1, 1):
                        check(x, bs, F(1, 2), bits, direction)

    # Exact rational complex directions, changing magnitudes, both orientations.
    rng = random.Random(68)
    units = [ONE, (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))]
    for g in (1, 4, 8):
        beta = F(1, 1 << g)
        for n in (1, 2, 3, 5, 8, 16):
            x = [(F(rng.randrange(-8, 9), 16), F(rng.randrange(-8, 9), 16)) for _ in range(n)]
            bs = [times(((1-beta)*F(rng.choice((1, 2, 4)), 4), F(0)), rng.choice(units)) for _ in range(n)]
            for bits in (g+1, 2*g+1, 2*g+8):
                for direction in (-1, 1):
                    check(x, bs, beta, bits, direction)
    for g in (4, 8):
        beta = F(1, 1 << g)
        for n in (64, 257, 2048):
            x = [(F((i*7) % 17-8, 16), F((i*11) % 19-9, 16)) for i in range(n)]
            bs = [times((1-beta, F(0)), units[(i*i+3*i) % 4]) for i in range(n)]
            for bits in (g+1, 2*g+8):
                for direction in (-1, 1):
                    check(x, bs, beta, bits, direction, use_residual=True)
    # Endpoint beta=1 (all coefficients zero).
    for direction in (-1, 1):
        check([(F(1, 8), F(-1, 8)), ONE], [ZERO, ZERO], F(1), 1, direction)

    sharp = []
    for k in range(2, 66):
        bits, a = 3*k, F(1, 1 << k)
        u = F(1, 1 << bits)
        beta, b = a+u/2, 1-a-u/2
        y = original.scan([ONE], (b, F(0)), beta, bits, 1)[0]
        formula = F(1 << k)-F(1 << (k-1))*u
        require(y == (formula, F(0)), 'sharp output formula')
        error = y[0]-1/beta
        require(error == b*u/(2*a*beta), 'sharp exact error identity')
        require(error >= u/(4*beta**2), 'sharp lower bound')
        require(y == fixed.run([ONE], [(b, F(0))], beta, bits)[0], 'sharp integer replay')
        sharp.append(dict(k=k, beta=str(beta), error_over_u_beta_squared=str(error*beta**2/u)))

    # General cascade inequality, checked with exact recurrence on moderate sizes.
    recurrence_cases = 0
    for n in range(1, 33):
        r = n+1
        for g in (1, 2, 4, 8):
            beta = F(1, 1 << g)
            for p in (1, 32, 128):
                w = max(g+ceil_log2(10*n), p+(n+1)*g+ceil_log2(20*n*(r+1)))
                u = F(1, 1 << w)
                E, amplification = F(0), F(r)
                for _ in range(n):
                    E = E/beta+5*(amplification+E+1)*u/beta**2
                    amplification /= beta
                require(E <= 10*n*(r+1)*u/beta**(n+1) <= F(1, 1 << (p+1)), 'cascade bound')
                recurrence_cases += 1
    budgets = []
    for r in range(3, 257):
        try:
            old_budgets.prime_power_data(r)
        except ValueError:
            continue
        for p in (1, 128, 1024, 1048576):
            old = old_budgets.budgets(r, p)
            old_budgets.check(old)
            n, g = r-1, old['g']
            new = max(g+ceil_log2(10*n), p+(n+1)*g+ceil_log2(20*n*(r+1)))
            require(new <= old['w']-g, 'execution guard saving')
            require(new-g >= ceil_log2(10*n), 'new growth guard')
            require(new-p-(n+1)*g >= ceil_log2(20*n*(r+1)), 'new target guard')
            budgets.append(dict(radix=r, p=p, g=g, old=old['w'], new=new, saved=old['w']-new))

    controls = []
    def rejected(name, fn):
        try:
            fn()
        except (ValueError, ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError('control accepted: '+name)
    x, bs, beta, bits = [ONE, ZERO, (F(1, 2), F(1, 4))], [(F(1, 2), F(0)), (F(0), F(1, 2)), (F(-1, 4), F(0))], F(1, 2), 24
    exact = exact_inverse(x, bs, 1)
    bound = fixed.error_bound(F(1), beta, bits)
    for mutation in ('zero_seed', 'plus_denominator', 'constant_coefficient'):
        def test(mutation=mutation):
            y = fixed.run(x, bs, beta, bits, 1, mutation)
            require(all(norm2(minus(a, b)) <= bound**2 for a, b in zip(y, exact)), mutation)
        rejected(mutation, test)
    rejected('wrong_orientation', lambda: require(all(norm2(minus(a,b)) <= bound**2 for a,b in zip(fixed.run(x,bs,beta,bits,-1),exact)), 'orientation'))
    rejected('unstable_coefficient', lambda: fixed.run([ONE], [ONE], beta, bits))
    rejected('below_closure_guard', lambda: fixed.run([ONE], [ZERO], F(1, 16), 4))
    k=8; u=F(1,1<<(3*k)); a=F(1,1<<k); beta=a+u/2; b=1-beta
    rejected('false_inverse_linear_margin_bound', lambda: require(b*u/(2*a*beta) <= 10*u/beta, 'false beta exponent'))

    result = dict(status='PASS_SHARP_CYCLIC_SCAN_BOUND', source_head=source['head'], seed=68,
                  counts=counts, scan_transcript_sha256=digest.hexdigest(), sharp_family=sharp,
                  cascade_recurrence_cases=recurrence_cases, budget_cases=len(budgets),
                  budget_examples=[b for b in budgets if b['p']==128 and b['radix'] in (3,4,9,16,256)],
                  budget_transcript_sha256=hashlib.sha256(json.dumps(budgets,sort_keys=True).encode()).hexdigest(),
                  controls=controls,
                  scope='Exact finite support for the written all-length proof; no factorizer, full kernel, tape runtime, or multiplication theorem validation.')
    text = json.dumps(result, indent=2)+'\n'
    if args.write:
        with args.write.open('x') as f:
            f.write(text)
    else:
        require(json.loads((ROOT/'EXPECTED.json').read_text()) == result, 'expected evidence mismatch')
    print(json.dumps({k:result[k] for k in ('status','counts','cascade_recurrence_cases','budget_cases','controls')}))


if __name__ == '__main__':
    main()
