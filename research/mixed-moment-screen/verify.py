"""Exact exploratory bounds on the frozen PR4470 raw mixed-target moment.

Prepared for SHIN09-git with OpenAI Codex assistance. Apache-2.0.
The input invoice is Cinna Davis's PR4470 result, retaining its predecessors.
This does not replay its native construction, compiler, or outer inequalities.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = 'c7b2388f6511c19976b337d8c8ac374610af616866a249d75dace704eb5d9e21'
UPSTREAM_SHA256 = '0ce7e7137422d5ffeda22085c81fa88471bbe963100fdad62e659f1e3bf89326'
BITS = 192
LOG_TERMS = 72

def need(ok, message):
    if not ok:
        raise ValueError(message)

def dyadic(lo, hi):
    scale = 1 << BITS
    return (Q((lo.numerator * scale) // lo.denominator, scale),
            Q(-((-hi.numerator * scale) // hi.denominator), scale))

def atanh_log(x):
    need(1 <= x <= 2, 'log range reduction')
    z = (x - 1) / (x + 1)
    total = 2 * sum((z**(2*k+1) / (2*k+1) for k in range(LOG_TERMS)), Q(0))
    remainder = 2*z**(2*LOG_TERMS+1) / ((2*LOG_TERMS+1)*(1-z*z))
    return total, total + remainder

@lru_cache(maxsize=None)
def log_interval(r):
    need(isinstance(r, int) and r >= 1, 'positive integer rank')
    k = r.bit_length()-1
    lo, hi = atanh_log(Q(r, 1 << k))
    l2, h2 = atanh_log(Q(2))
    return dyadic(lo+k*l2, hi+k*h2)

def poly_interval(xlo, xhi, degree):
    lo = hi = Q(0)
    for k in range(degree+1):
        a, b = xlo**k/math.factorial(k), xhi**k/math.factorial(k)
        if k % 2:
            lo, hi = lo-b, hi-a
        else:
            lo, hi = lo+a, hi+b
    return lo, hi

def signed_taylor_exp(a, r, degree):
    need(a >= 0 and degree >= 0 and degree % 2 == 0, 'even Taylor degree and nonnegative rate')
    lo, hi = log_interval(r)
    # Taylor's integral remainder for exp(-x): odd partial sums are lower,
    # even partial sums are upper, for every x >= 0.
    lower = poly_interval(a*lo, a*hi, degree+1)[0]
    upper = poly_interval(a*lo, a*hi, degree)[1]
    return lower, upper

def reciprocal_exp(a, r, degree=24):
    need(a >= 0, 'nonnegative rate')
    lo, hi = log_interval(r)
    xlo, xhi = a*lo, a*hi
    need(xhi < degree+2, 'positive exponential tail ratio below one')
    lower = sum((xlo**k/math.factorial(k) for k in range(degree+1)), Q(0))
    upper = sum((xhi**k/math.factorial(k) for k in range(degree+1)), Q(0))
    upper += xhi**(degree+1)/math.factorial(degree+1)/(1-xhi/(degree+2))
    return 1/upper, 1/lower

def margin(targets, paid, a, engine):
    lo = hi = Q(0)
    # Cancel equal bases exactly before enclosing the signed difference.
    for r in sorted(targets.keys() | paid.keys()):
        coefficient = r*(targets.get(r, 0)-paid.get(r, 0))
        if not coefficient:
            continue
        lower, upper = engine(a, r)
        if coefficient > 0:
            lo, hi = lo+coefficient*lower, hi+coefficient*upper
        else:
            lo, hi = lo+coefficient*upper, hi+coefficient*lower
    return lo, hi

def decision(bounds):
    lo, hi = bounds
    need(lo <= hi, 'ordered enclosure')
    return 'accept' if lo > 0 else 'reject' if hi < 0 else 'inconclusive'

def display(bounds):
    bounds = dyadic(*bounds)
    return {'lower':str(bounds[0]), 'upper':str(bounds[1]),
            'decimal_approx':[float(x) for x in bounds], 'decision':decision(bounds)}

def load_upstream():
    path = HERE/'upstream_moment.py'
    need(sha256(path.read_bytes()).hexdigest() == UPSTREAM_SHA256, 'frozen upstream moment engine hash')
    spec = importlib.util.spec_from_file_location('frozen_upstream_moment',path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return engine

def upstream_margin(engine,targets,paid,a):
    tlo,thi = engine.moment(targets,1-a)
    plo,phi = engine.moment(paid,1-a)
    return tlo-phi,thi-plo

def adaptive_margin(targets,paid,a,fallback):
    for degree in [2,4,6]:
        bounds = margin(targets,paid,a,lambda b,r: signed_taylor_exp(b,r,degree))
        if decision(bounds) != 'inconclusive':
            return bounds,degree
    return fallback(targets,paid,a),'fallback'

def reject_gate_margin(targets,paid,a,fallback):
    bounds,stage=adaptive_margin(targets,paid,a,fallback)
    if decision(bounds)=='reject' or stage=='fallback':
        return bounds,stage
    # Downstream certificates may need the original quantitative interval,
    # even when a cheap positive sign has already been established.
    return fallback(targets,paid,a),'accepted_then_full'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='authoring only: replace the expected receipt')
    args=parser.parse_args()
    raw = (HERE/'INPUT.json').read_bytes()
    need(sha256(raw).hexdigest() == EXPECTED, 'frozen PR4470 source receipt hash')
    source = json.loads(raw)
    targets = {int(k):v for k,v in source['targets'].items()}
    paid = {int(k):v for k,v in source['paid'].items()}
    need(all(r > 0 and isinstance(n, int) and n > 0 for d in [targets,paid] for r,n in d.items()), 'valid profiles')
    need(sum(targets.values()) == 10928 and sum(paid.values()) == 64620, 'source field and paid counts')
    need(sum(r*n for r,n in targets.items()) == 239886, 'target rank mass')
    need(sum(r*n for r,n in paid.items()) == 239134, 'paid rank mass')
    root_lo, root_hi = map(Q,source['fixed_profile_ceiling']['root'])
    engine = load_upstream()
    cases = [('zero',Q(0)), ('previous_4447_rate',Q('.00300123')),
             ('selected_kappa_as_raw_test_only',Q(source['kappa'])),
             ('admission_raw_test',Q('.003020155')),
             ('published_root_lower',root_lo), ('published_root_upper',root_hi),
             ('larger_rate_control',Q('.0031'))]
    results = []
    for name,a in cases:
        full = margin(targets,paid,a,reciprocal_exp)
        upstream = upstream_margin(engine,targets,paid,a)
        need(max(full[0],upstream[0]) <= min(full[1],upstream[1]), 'source engine enclosure intersects independent exponential engine')
        need(decision(upstream) == decision(full), 'source engine agrees with independent exponential engine')
        row = {'case':name,'rate':str(a),'full_positive_exp':display(full),'upstream_source_engine':display(upstream),'screens':{}}
        for degree in [2,4,6]:
            bounds = margin(targets,paid,a,lambda b,r: signed_taylor_exp(b,r,degree))
            need(max(bounds[0],full[0]) <= min(bounds[1],full[1]), 'independent exponential enclosures intersect')
            need(decision(bounds) == 'inconclusive' or decision(bounds) == decision(full), 'screen decision agrees with full engine')
            row['screens'][str(degree)] = display(bounds)
        results.append(row)
    by_case = {row['case']:row for row in results}
    need(by_case['published_root_lower']['full_positive_exp']['decision'] == 'accept', 'reproduce published lower root sign')
    need(by_case['published_root_upper']['full_positive_exp']['decision'] == 'reject', 'reproduce published upper root sign')
    # A migration foil: freezing productive credit at its a=0 value would
    # accept a rate that the actual mixed-target moment rejects.
    a = Q('.0031')
    fixed_target = {1:sum(r*n for r,n in targets.items())}
    bad = margin(fixed_target, paid, a, reciprocal_exp)
    need(decision(bad) == 'accept', 'frozen-target migration foil accepts')
    need(by_case['larger_rate_control']['full_positive_exp']['decision'] == 'reject', 'actual mixed moment rejects migration foil')
    # Independent exact controls at zero, shared-base cancellation, sign swap,
    # strict equality, and a genuinely changed rank/cost profile.
    need(margin(targets,paid,Q(0),reciprocal_exp) == (Q(752),Q(752)), 'zero-rate mass identity')
    need(margin({2:3},{2:3},a,reciprocal_exp) == (Q(0),Q(0)), 'equal-profile cancellation')
    need(decision((Q(0),Q(0))) == 'inconclusive', 'strict boundary is not acceptance')
    actual = margin(targets,paid,a,reciprocal_exp)
    swapped = margin(paid,targets,a,reciprocal_exp)
    need(swapped == (-actual[1],-actual[0]), 'signed target/paid reversal')
    more = dict(paid); more[1] += 1000
    need(decision(margin(targets,more,Q(0),reciprocal_exp)) == 'reject', 'charged extra rank-one work rejects')
    other = margin({2:1},{1:2},Q(1),reciprocal_exp)
    need(other[0] <= -1 <= other[1] and decision(other) == 'reject', 'independent exact r^(0) fixture')
    calls = []
    def fallback(t,p,a):
        calls.append((t,p,a))
        return upstream_margin(engine,t,p,a)
    eq,stage = adaptive_margin({2:3},{2:3},a,fallback)
    need(len(calls)==1 and stage=='fallback' and decision(eq)=='inconclusive', 'ambiguous equality invokes the full fallback once')
    calls.clear()
    accepted,stage = adaptive_margin(targets,paid,Q('.003020155'),fallback)
    need(not calls and stage==4 and decision(accepted)=='accept', 'admission fixture short circuits only after a certified sign')
    calls.clear()
    accepted,stage=reject_gate_margin(targets,paid,Q('.003020155'),fallback)
    need(len(calls)==1 and stage=='accepted_then_full' and decision(accepted)=='accept', 'reject-only gate preserves full accepted evaluation')
    calls.clear()
    rejected,stage=reject_gate_margin(targets,paid,Q('.0031'),fallback)
    need(not calls and decision(rejected)=='reject', 'reject-only gate skips full evaluation only for certified rejection')
    out = {'status':'PASS_SCOPED_MIXED_MOMENT_PROBE','input_sha256':EXPECTED,
           'base':'b91956876e5b4122fd89179f1b57557ff8378f15',
           'source_pr':4470,'source_head':'b9a13c1673e0e9697de410de16e8bbf3207a7363',
           'log_interval_bits':BITS,'log_series_terms':LOG_TERMS,
           'definition':'sum target_n*r^(1-a) minus sum paid_n*r^(1-a)',
           'scope':'Frozen raw invoice only; no native, compiler, completion, outer, or speed claim. The two new exponential engines share proved rational log intervals; the upstream source engine has its own log implementation.',
           'upstream_engine_sha256':UPSTREAM_SHA256,
           'cases':results,'frozen_target_migration_foil':display(bad),
           'controls_passed':11}
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    else:
        need(json.loads((HERE/'RESULT.json').read_bytes())==out,'complete deterministic receipt equality')
    print(json.dumps({'status':out['status'],'cases':[{ 'case':r['case'],'full':r['full_positive_exp']['decision'],'screens':{k:v['decision'] for k,v in r['screens'].items()}} for r in results],'controls':out['controls_passed']},indent=2))

if __name__ == '__main__':
    main()
