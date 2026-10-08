#!/usr/bin/env python3
"""Exact copied-center / fixed-I+J composition, conditional on retained proofs.

Credits: icekylinx PR32/36 (projectors, copied centers), Dominik Scholz PR35
(two fixed factors and CRT bounds), Zhihao Chen PR29/23, Paureel/Aurel Prosz,
Swapnil Jain, Rohan Arun PR25/31, RaD/hipotures and all inherited notices.
Prepared locally with OpenAI Codex assistance; no formal theorem claim.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from math import comb, factorial, isqrt, prod
from pathlib import Path
import argparse
import importlib.util
from itertools import combinations
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import copied_centers_network as baseline
from structured_bulk_assembly import js
sys.path.insert(0,str(HERE))
from balanced_assembly import assembly, cutoffs

AB = Q(82375901, 2*10**12)
AC = Q(717, 10000000)
# Strictly below the recomputed balanced assembly margin.
KAPPA = Q(411862541, 10**13)
PR47_KAPPA = Q(4105106623,10**14)
PR46_KAPPA = Q(410062945,10**13)
PR44_KAPPA = Q(2050314627,5*10**13)
PR37_KAPPA = Q(3850771033, 10**14)
PR38_KAPPA = Q(242889, 6250000000)
PR43_KAPPA = Q(409953,10**10)
PR42_KAPPA = Q(4099494519,10**14)
PR41_KAPPA = Q(1008542031,25000000000000)
PR40_KAPPA = Q(1959367447,50000000000000)
PR39_KAPPA = Q(971668963, 25000000000000)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    def reject(x):
        raise ValueError('Floating point input forbidden: ' + x)
    return json.loads(path.read_text(), parse_float=reject, parse_constant=reject)


def check_sources():
    sources = read(HERE / 'SOURCE.json')
    for name, digest in sources['files'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                'Pinned source changed: ' + name)
    return sources


def mersenne(exponent):
    require(exponent >= 3 and all(exponent % d for d in range(2, isqrt(exponent)+1)),
            'Composite Lucas-Lehmer exponent')
    p = 2**exponent - 1
    s = 4
    for _ in range(exponent - 2):
        s = (s*s-2) % p
    require(s == 0, 'Lucas-Lehmer failed')
    return p


def exactness(h):
    require(h in (23, 25), 'Uncertified dimension')
    primes = [mersenne(e) for e in (61, 31, 19)]
    Z = 3*h-7
    B0 = (4*h-2)*Z + 27*(h+1)
    D = 3*(h+1)*(h-1)**2
    B = 2*(h-1)*B0
    bounds = {r: sum(comb(h,j)*factorial(j)*B**j*D**(r-j)
                     for j in range(r+1)) for r in (2,3,4)}
    require(bounds[2] < primes[0], 'Rank-two minor modulus insufficient')
    require(max(bounds[3],bounds[4]) < prod(primes), 'CRT minor modulus insufficient')
    require(3*(h+1)*(h-1) < min(primes), 'Denominator may vanish')
    return dict(h=h, primes=primes, prime_product=prod(primes),
                single_numerator_bound=B0, common_denominator_bound=D,
                correction_numerator_bound=B, minor_bounds=bounds,
                modulus_gaps={2: primes[0]-bounds[2],
                              3: prod(primes)-bounds[3],4: prod(primes)-bounds[4]})


def tree(edges, n):
    require(len(edges) == n-1 and len(set(edges)) == n-1, 'Wrong tree edge count')
    seen = {0}
    while True:
        new = seen | {v for u,v in edges if u in seen} | {u for u,v in edges if v in seen}
        if new == seen:
            break
        seen = new
    require(len(seen) == n, 'Disconnected restriction graph')


def data_corners():
    c = read(HERE/'data-corners.json')
    prime = c['prime']
    require(prime == 1000003 and all(prime % j for j in range(2,isqrt(prime)+1)),
            'Data witness prime not proved')
    require(c['dimensions'] == [23,25], 'Data dimensions')
    require([tuple(r[:3]) for r in c['records']] == list(combinations(range(23),3)),
            'Incomplete first triple coverage')
    require(all(0 <= r[3] <= 2300 and 0 < r[4] < prime for r in c['records']),
            'Invalid modular product record')
    failures = c['fallback_pairs']
    require(len({tuple(r[:6]) for r in failures}) == len(failures), 'Duplicate fallback')
    counts = Counter()
    for aa,bb,cc,u,v,w,row in failures:
        require(0<=aa<bb<cc<23 and 0<=u<v<w<25 and 0<=row<47,'Invalid fallback pair')
        counts[aa,bb,cc] += 1
    require(all(r[3]+counts[tuple(r[:3])]==2300 for r in c['records']), 'Pair coverage gap')
    require(c['good'] == sum(r[3] for r in c['records']), 'Wrong good count')
    require(c['fallback'] == len(failures) and c['pairs'] == c['good']+c['fallback']==4073300,
            'Wrong exhaustive pair count')
    require(c['nonzero_pivots'] == 47*c['good']+sum(r[6] for r in failures),
            'Wrong complete nonvanishing coverage')
    from data_recovery import recover
    recovery=recover(tuple(tuple(pair) for pair in failures))
    require(len(recovery)==len(failures)==10,'Incomplete exact recovery')
    require(all(len(row['pivots'])==47 and all(Q(x) for x in row['pivots'])
                for row in recovery),'Incomplete rational pivot proof')
    return dict(c, primary_good=c['good'],primary_fallback=c['fallback'],
                good=c['pairs'],fallback=0,exact_recovery=recovery)


def geometry():
    spec=importlib.util.spec_from_file_location('fixed_both_reversed_geometry',HERE/'reversed/geometry.py')
    inherited=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inherited)
    g=inherited.run()  # Exact all-weight cuts and actual common-basis contractions.
    c=data_corners()
    require(g['dimensions']==[23,25] and g['profile']==[1]*9+[21,17,481], 'Reversed family')
    require(g['rows']==[(r,i%25) for i,r in enumerate(list(range(23))+[22]+list(range(23)))],
            'Rational recovery row geometry mismatch')
    require(g['columns']==[(r,(528+i)%25) for i,r in enumerate(list(range(23))+[0]+list(range(23)))],
            'Rational recovery column geometry mismatch')
    coordinates={}
    for h in (23,25):
        primal=[Q(3),Q(4)]
        dual=[-Q(5,3*(h+1)),Q(1,2)-Q(5,3*(h+1))]
        require(all(primal) and all(dual), 'Zero fixed line coordinate')
        coordinates[h]=dict(primal=primal,dual=dual)
    return dict(dimensions=[23,25],inherited=g,modular=c,line_coordinates=coordinates,
                row_tree=[(r,23+be) for r,be in g['rows']],
                column_tree=[(r,23+be) for r,be in g['columns']],
                accepted_profile=dict(singletons=9,blocks=[21,17,481]),
                fallback_profile=dict(singletons=47,blocks=[481]),
                scope='Nonzero modular pivots certify rational nonvanishing at the actual two fixed bases; '
                      'zeros follow separate exact rank cuts. Ten primary-prime failures are replayed '
                      'with exact rational elimination, yielding the same profile for every pair.')


@lru_cache(None)
def logs(x):
    x = Q(x)
    require(x >= 1, 'Log domain')
    k = 0
    while x > 2:
        x /= 2
        k += 1
    def small(y):
        z = (y-1)/(y+1)
        lo = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(32)), Q())
        return lo, lo+2*z**65/(65*(1-z*z))
    lo,hi = small(x)
    lo2,hi2 = small(Q(2))
    lo,hi = lo+k*lo2,hi+k*hi2
    scale = 10**30
    return Q((lo*scale).numerator//(lo*scale).denominator,scale), \
        Q(-(-(hi*scale).numerator//(hi*scale).denominator),scale)


def moment(m,W,rows,saving):
    require(type(saving) is Q and 0 < saving < 1, 'Exact positive saving required')
    lower,upper = Q(),Q()
    enclosure = {}
    for t,n in sorted(rows.items()):
        require(type(t) is int and type(n) is int and 0<t<m and n>0, 'Invalid child')
        lo,hi = logs(Q(m,t))
        u,v = saving*lo,saving*hi
        require(0 <= u <= v < 1, 'Exponential enclosure domain')
        weight = Q(t*n,m*W)
        lower += weight*(1+u+u*u/2+u*u*u/6)
        upper += weight*(1+v+v*v/(2*(1-v/3)))
        enclosure[t] = dict(lower=lo,upper=hi)
    return dict(saving=saving,exponent=1-saving,lower=lower,upper=upper,
                strict_gap=1-upper,logarithms=enclosure)


def profile():
    a,b = 23,25
    m = a*b
    rows = [read(HERE / f'original-{h}.json') for h in (a,b)]
    N = comb(a,3)*comb(b,3)
    W = 2*N+sum(N//r['v']*r['R'] for r in rows)
    L = sum(N//r['v']*r['loss'] for r in rows)
    data = data_corners()
    good,bad = data['good'],data['fallback']
    parts = {'data':Counter({1:2*(9*good+47*bad),21:2*good,17:2*good,481:2*N}),
             'paid_endpoint_copy':Counter({1:N})}
    axes = []
    for row in rows:
        h = row['h']
        require(row['v'] == comb(h,3), 'Triple count')
        require(row['R'] == row['c']+row['q']-row['matched'], 'Role allocation')
        require(row['loss'] == h*(h-1), 'Retained center loss')
        require(sum(r*n for r,n in enumerate(row['histogram'])) == h*row['R']+2*row['loss'],
                'Original frame rank mass')
        f = read(HERE / f'profiles-{h}.json')
        for key in ('h','v','R','loss','rank_sum'):
            require(f[key] == row[key], 'Fixed/original mismatch: '+key)
        require(f['crt_disagreements'] == 0 and f['field_prime'] == 2**61-1,
                'Invalid CRT profile')
        blocks = f['blocks'][:]
        require(len(blocks) == h+1 and all(type(n) is int and n>=0 for n in blocks),
                'Invalid fixed blocks')
        require(sum(t*n for t,n in enumerate(blocks)) == f['rank_sum'], 'Fixed profile mass')
        require(blocks[h] == h, 'Exactly h full center cleanup calls expected')
        # Preserve every transformed copy. Replace only its original's full cleanup.
        blocks[h] -= h
        blocks[1] += h
        require(sum(t*n for t,n in enumerate(blocks)) == h*row['R']+row['loss'],
                'Copied fixed profile mass')
        rep = N//row['v']
        bank = rep*row['R']
        parts[f'internal_{h}'] = Counter({t:n*rep for t,n in enumerate(blocks) if t and n})
        parts[f'exterior_{h}'] = Counter({h:bank,m-2*h:bank})
        parts[f'data_growth_{h}'] = Counter({1:2*N,h-2:2*N})
        axes.append(dict(original=row,fixed=f,copied_blocks=blocks,exactness=exactness(h)))
    hist = sum(parts.values(),Counter())
    s = sum(t*n for t,n in hist.items())
    require(s == W*m-N+L == 102078397025, 'Complete rank mass')
    require((m,N,W,L) == (575,4073300,177530859,2226400), 'Physical constants')
    require(max(hist) == 529 and all(0<t<m and n>0 for t,n in hist.items()), 'Proper children')
    return dict(m=m,N=N,W=W,L=L,total_rank=s,deficit=W*m-s,maxchild=max(hist),
                child_multiplicities=dict(sorted(hist.items())),parts=parts,axes=axes)


def run():
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    sources = check_sources()
    prior = baseline.certificate()
    geo,p = geometry(),profile()
    exact = moment(p['m'],p['W'],p['child_multiplicities'],AB)
    require(exact['upper'] < 1, 'Bit characteristic failed')
    old = prior['bit']['counts']
    old_at_new = moment(old['m'],old['W'],old['child_multiplicities'],AB)
    require(old_at_new['lower'] > 1, 'Old construction not excluded at new saving')
    forward=read(HERE/'comparison-pr40.json')
    forward_rows={int(t):n for t,n in forward['child_multiplicities'].items()}
    require(sum(t*n for t,n in forward_rows.items())==108202762275, 'PR40 rank mismatch')
    forward_at_new=moment(forward['m'],forward['W'],forward_rows,AB)
    require(forward_at_new['lower']>1,'PR40 network not excluded at new saving')
    rad=read(HERE/'comparison-pr41.json')
    rad_rows={int(t):n for t,n in rad['child_multiplicities'].items()}
    require(sum(t*n for t,n in rad_rows.items())==rad['total_rank']==102565738275,'PR41 rank mismatch')
    rad_at_new=moment(rad['m'],rad['W'],rad_rows,AB)
    require(rad_at_new['lower']>1,'PR41 alternating network not excluded at new saving')
    newest=read(HERE/'comparison-pr42.json')
    newest_rows={int(t):n for t,n in newest['child_multiplicities'].items()}
    require(sum(t*n for t,n in newest_rows.items())==newest['total_rank']==102565738275,'PR42 rank mismatch')
    newest_at_new=moment(newest['m'],newest['W'],newest_rows,AB)
    require(newest_at_new['lower']>1,'PR42 network not excluded at new saving')
    previous=read(HERE/'comparison-pr43.json')
    previous_rows={int(t):n for t,n in previous['child_multiplicities'].items()}
    require(sum(t*n for t,n in previous_rows.items())==previous['total_rank']==102565738275,'PR43 rank mismatch')
    previous_at_new=moment(previous['m'],previous['W'],previous_rows,AB)
    require(previous_at_new['lower']>1,'PR43 network not excluded at new saving')
    frontier=read(HERE/'comparison-pr44.json')
    frontier_rows={int(t):n for t,n in frontier['child_multiplicities'].items()}
    require(sum(t*n for t,n in frontier_rows.items())==frontier['total_rank']==102565738275,'PR44 rank mismatch')
    frontier_at_new=moment(frontier['m'],frontier['W'],frontier_rows,AB)
    require(frontier_at_new['lower']>1,'PR44 network not excluded at new saving')
    parent=read(HERE/'comparison-pr46.json')
    parent_rows={int(t):n for t,n in parent['child_multiplicities'].items()}
    require(sum(t*n for t,n in parent_rows.items())==parent['total_rank']==102565738275,'PR46 rank mismatch')
    parent_at_new=moment(parent['m'],parent['W'],parent_rows,AB)
    require(parent_at_new['lower']>1,'PR46 network not excluded at new saving')
    latest=read(HERE/'comparison-pr47.json')
    latest_rows={int(t):n for t,n in latest['child_multiplicities'].items()}
    require(sum(t*n for t,n in latest_rows.items())==latest['total_rank']==latest['W']*latest['m']-1846900,'PR47 rank mismatch')
    latest_at_new=moment(latest['m'],latest['W'],latest_rows,AB)
    require(latest_at_new['lower']>1,'PR47 network not excluded at new saving')
    phase = prior['complex']['counts']
    phase_row = read(ROOT / 'certificates/copied-centers-complex-input.json')
    bridge = baseline.finite_bridge(p,phase,[phase_row,phase_row])
    require(all(js(bridge[k])==js(prior['finite_bridge'][k]) for k in ('complex','semantic','rows')), 'Unexpected phase or stock change')
    final = assembly(bridge,AB,KAPPA,a_complex=AC)
    eventual = cutoffs(bridge,final)
    require(KAPPA > PR47_KAPPA > PR46_KAPPA > PR44_KAPPA > PR43_KAPPA > PR42_KAPPA > PR41_KAPPA > PR40_KAPPA > PR39_KAPPA > PR38_KAPPA > PR37_KAPPA > prior['kappa'] > Q(1,2**15), 'Comparison failed')
    require(KAPPA < Q(1,2**14), 'Unexpected power-of-two bracket')
    own_files = sorted(HERE.glob('*.py'))+sorted(HERE.glob('*.cpp'))+[HERE/'PROOF.md',HERE/'SOURCE.json']
    own_files += [HERE/f'{kind}-{h}.json' for h in (23,25) for kind in ('profiles','original','scalar')]
    own_files += [HERE/'data-corners.json',HERE/'comparison-pr40.json',HERE/'comparison-pr41.json',HERE/'comparison-pr42.json',HERE/'comparison-pr43.json',HERE/'comparison-pr44.json',HERE/'comparison-pr46.json',HERE/'comparison-pr47.json',HERE/'search-record.json',HERE/'links-23.uses',HERE/'links-25.uses']
    return dict(status='Conditional exact arithmetic witness; general transfer proofs are dependencies',
                kappa=KAPPA,bit=dict(counts=p,**exact),complex=prior['complex'],
                geometry=geo,finite_bridge=bridge,assembly=final,eventual_bounds=eventual,sources=sources,
                comparison=dict(PR47=PR47_KAPPA,ratio_PR47=KAPPA/PR47_KAPPA,PR46=PR46_KAPPA,ratio_PR46=KAPPA/PR46_KAPPA,PR44=PR44_KAPPA,ratio_PR44=KAPPA/PR44_KAPPA,PR36=prior['kappa'],PR37=PR37_KAPPA,PR38=PR38_KAPPA,PR39=PR39_KAPPA,PR40=PR40_KAPPA,PR41=PR41_KAPPA,PR42=PR42_KAPPA,PR43=PR43_KAPPA,
                    ratio_PR36=KAPPA/prior['kappa'],ratio_PR37=KAPPA/PR37_KAPPA,
                    ratio_PR38=KAPPA/PR38_KAPPA,ratio_PR39=KAPPA/PR39_KAPPA,ratio_PR40=KAPPA/PR40_KAPPA,ratio_PR41=KAPPA/PR41_KAPPA,ratio_PR42=KAPPA/PR42_KAPPA,ratio_PR43=KAPPA/PR43_KAPPA,
                    dyadic_corollary='2^-15',next_dyadic_not_reached='2^-14'),
                controls=dict(PR47_bit_at_new_lower=latest_at_new['lower'],PR46_bit_at_new_lower=parent_at_new['lower'],PR44_bit_at_new_lower=frontier_at_new['lower'],old_bit_at_new_lower=old_at_new['lower'],PR40_bit_at_new_lower=forward_at_new['lower'],PR41_bit_at_new_lower=rad_at_new['lower'],PR42_bit_at_new_lower=newest_at_new['lower'],PR43_bit_at_new_lower=previous_at_new['lower']),
                local_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in own_files},
                scope='Changed leave-one-out graphs with RaD alternating point order, newly pinned weighted carrier matching and fixed-basis internal blocks at (23,25); '
                      'all actual data pairs checked for 9 singletons +21+17+481; '
                      'ten failed modular tests are recovered by exact rational elimination. Exact scalar/label/'
                      'matching/profile reconstruction is producer.py. OpenAI base theorem, '
                      'written residual compiler, fixed-tape recursion, analytic/semantic/'
                      'routing/recovery and eventual-threshold interfaces remain assumed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        args.output.write_text(json.dumps(js(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(AB))
    print('47 strict inequalities; seven margins; all-exact enclosures; inherited balanced assembly')
