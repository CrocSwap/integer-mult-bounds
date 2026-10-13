"""Exact checks of the new precision bounds and unchanged scan execution."""
from pathlib import Path
import importlib.util
import hashlib
import json
import math
import sys
import argparse

sys.set_int_max_str_digits(100000)
P = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


b = load('budget', P/'budget.py')
s = load('source_scan', P/'source_scan.py')
o = load('dense', P/'dense.py')
k = load('kernel', P/'vendor/check.py')
F = s.F


def check_uniform(z):
    r, n, phi = z['radix'], z['n'], z['phi']
    ell, c = z['ell'], z['c']
    d, a, g = z['circle_exponent'], z['full_inverse_exponent'], z['margin_exponent']
    h, e, j, v = (z[key] for key in ('partial_inverse_exponent', 'coefficient_error_exponent', 'execution_error_exponent', 'forward_product_exponent'))
    W, p, w, D = (z[key] for key in ('working_bits', 'target_bits', 'coarse_bits', 'magnitude_bits'))
    s.need(r >= 3 and n == r-1 and phi == sum(math.gcd(i,r)==1 for i in range(1,r)), 'degree binding')
    s.need(r <= 1 << ell and n <= 1 << c, 'ceil bindings')
    s.need(d >= 1+2*ell+r*n*phi, 'circle lower bound')
    s.need(a >= 2*d+r+2, 'full inverse bound')
    s.need(g >= d+ell+2*r+2, 'root radial gap')
    s.need(h >= n+r+a+1, 'complement subproduct bound')
    s.need(e >= d+1 and e >= a+1 and e >= p+2*a+D+3, 'coefficient perturbation')
    s.need(z['factor_bits'] >= max(n*ell, e+r+3), 'factor preparation')
    s.need(W >= 2*g+1 and W >= c+h+3*g+4, 'scan and prefix contraction')
    s.need(j >= c+2*h+3*g+ell+D+5, 'global execution error')
    s.need(v >= 2*n+ell+r, 'forward complement bound')
    s.need(W >= p+j+2, 'target precision')
    s.need(W >= w+v+j+3, 'coarse recovery')


def uniform_cases():
    rows = []
    for r in range(3, 513):
        if not b.prime_power(r): continue
        for p in (1, 32, 128, 512, 4096):
            for coarse in (0, p, 2*p):
                for magnitude in (0, 8, 64):
                    row = b.uniform(r, p, coarse, magnitude)
                    check_uniform(row)
                    s.need(row['working_bits'] <= max(p,coarse)+12*r**3+magnitude, 'cubic working bound')
                    s.need(row['factor_bits'] <= p+6*r**3+magnitude, 'cubic factor bound')
                    rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    out = parser.parse_args().out.resolve()
    s.need(not out.is_relative_to(P), 'output must be outside the source package')
    out.mkdir(parents=True, exist_ok=False)
    for path, digest in json.loads((P/'SOURCE.json').read_text())['files'].items():
        s.need(hashlib.sha256((P/path).read_bytes()).hexdigest() == digest, 'source hash')
    uniform = uniform_cases()
    cases, certificates, controls = [], [], []
    units = (s.ONE, (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13)))
    for fixture in json.loads((P/'vendor/FACTORS.json').read_text()):
        state = k.certify(fixture)
        roots = [tuple(map(F, v)) for v in fixture['roots']]
        r, beta = state['radix'], state['beta']
        # This finite bound is supplied by the pinned existing factor proof.
        # The uniform cubic theorem instead uses PR621's global bound.
        AQ = F(state['certificate']['inverse_norm_bound'])
        qnorm = sum(s.l1(z) for z in state['q'])
        product_K = F(1)
        for rho in roots: product_K *= 1+s.l1(rho)
        s.need(product_K <= 3**len(roots)*r*qnorm, 'Mahler forward-product consequence')
        certificates.append(dict(radix=r, embedding=state['embedding'], qnorm=str(qnorm),
                                 supplied_inverse_bound=str(AQ), product_K=str(product_K),
                                 forward_Mahler_bound=str(3**len(roots)*r*qnorm)))
        for n in (1,2,3,8,17,64):
            for direction in (-1,1):
                phase = lambda i:units[(i*i+3*i+1) % 4]
                factors = [(rho,beta,phase,direction) for rho in roots]
                coarse = 4 if n % 2 else 160
                original = [(F((5*i)%7-3,1 << coarse),F((7*i)%11-5,1 << coarse)) for i in range(n)]
                source_bound = max(s.l1(v) for v in original)
                bits, error, recovery, partial, contraction = b.choose(factors,r,source_bound,qnorm,AQ,coarse,130)
                s.need(all(v == s.rnd(v,coarse) for v in original), 'input grid')
                s.need(all(s.norm2(phase(i)) == 1 for i in range(n)), 'unit phases')
                x = [(v[0]*r,v[1]*r) for v in original]
                exact = x[:]
                for factor in factors:
                    s.inverse_factor(x,factor,bits)
                    if n <= 3:
                        exact = o.oracle(exact,[factor],1)
                        o.close(x,exact,error,'all-prefix independent dense error')
                increment = x[:]
                for factor in reversed(factors): s.forward_factor(x,factor,bits)
                for i in range(n): x[i] = s.rnd((x[i][0]/r,x[i][1]/r),bits)
                o.close(x,original,recovery,'pre-round recovery error')
                x = [s.rnd(v,coarse) for v in x]
                s.need(x == original,'exact source restoration')
                # Q(U) is expanded directly; no inverse-factor implementation.
                residual = []
                for i in range(n):
                    value, weight = s.ZERO,s.ONE
                    for j, coefficient in enumerate(state['q']):
                        col = (i-direction*j) % n
                        value = o.plus(value,o.times(o.times(coefficient,weight),increment[col]))
                        weight = o.times(weight,phase(col))
                    residual.append(value)
                o.close(residual,original,qnorm*error,'expanded polynomial residual')
                total = error+source_bound*F(state['certificate']['factorization_inverse_error_bound'])
                s.need(total <= F(1,1 << 128),'true kernel error')
                cases.append(dict(radix=r,embedding=state['embedding'],length=n,direction=direction,
                                  coarse_bits=coarse,working_bits=bits,dense=n<=3,
                                  global_execution_error=str(error),recovery_error=str(recovery),
                                  true_kernel_error=str(total),partial_inverse_bound=str(partial),
                                  contraction=str(contraction),exact_restoration=True))
        print('PASS kernel',r,state['embedding'],flush=True)
    def reject(name,fn):
        try: fn()
        except ValueError as exc: controls.append(dict(name=name,rejected=str(exc)))
        else: raise ValueError('accepted control '+name)
    sample = b.uniform(16,128,128)
    for name,key,value in (
        ('missing_complement_factor','partial_inverse_exponent',sample['full_inverse_exponent']),
        ('insufficient_target_precision','working_bits',sample['target_bits']+sample['execution_error_exponent']),
        ('insufficient_recovery_precision','working_bits',sample['coarse_bits']+sample['forward_product_exponent']+sample['execution_error_exponent']+1),
        ('insufficient_coefficient_precision','coefficient_error_exponent',sample['target_bits']+sample['full_inverse_exponent']),
    ):
        mutation={**sample,key:value}
        reject(name,lambda mutation=mutation:check_uniform(mutation))
    fs=[((F(1,2),F(0)),F(1,2),lambda i:s.ONE,1),((F(1,2),F(0)),F(1,2),lambda i:(F(0),F(1)),1)]
    reject('nonshared_shift',lambda:b.choose(fs,1,F(1),F(3),F(4),4,40))
    reject('prefix_contraction_lost',lambda:b.prefix_error(2,F(1,2),1,F(1),F(3),F(4),4))
    report=dict(status='passed',uniform_budget_cases=len(uniform),uniform_radices=sorted({z['radix'] for z in uniform}),
                comparison=[b.uniform(r,128,128) for r in (3,4,8,16,32,64,128,256,512)],
                certificates=certificates,cases=cases,controls=controls,
                cubic_guard='max(p,w)+12*r^3+log2_source_bound',new_kappa=False)
    (out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'UNIFORM-BUDGETS.json').write_text(json.dumps(uniform,indent=2)+'\n')
    print(json.dumps(dict(status='passed',uniform=len(uniform),kernel_cases=len(cases),dense=sum(z['dense'] for z in cases),controls=len(controls))))


if __name__ == '__main__': main()
