#!/usr/bin/env python3
"""Exact boundary evidence for PROOF.md, not a proof of its quantifiers.

Philipp / mightyOil, with substantial OpenAI Codex assistance. Apache-2.0.
Only the standard library is required. All guards survive -O.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 21
ZERO = (0, 0)
ONE = (1, 0)
I = (0, 1)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def neg(a):
    return (-a[0], -a[1])


def mul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def plus(a, b):
    return [add(x, y) for x, y in zip(a, b)]


def minus(a, b):
    return plus(a, [neg(v) for v in b])


def scale(a, c):
    return [mul(v, c) for v in a]


def linear(columns, coefficients):
    result = [ZERO] * len(columns[0])
    for col, c in zip(columns, coefficients):
        result = plus(result, scale(col, c))
    return result


def rank_q(rows):
    basis = {}
    for original in rows:
        row = list(map(Fraction, original))
        for p, pivot in sorted(basis.items()):
            c = row[p]
            if c:
                row = [a-c*b for a, b in zip(row, pivot)]
        p = next((j for j, a in enumerate(row) if a), None)
        if p is not None:
            basis[p] = [a/row[p] for a in row]
    return len(basis)


def rank_c(columns):
    """Exact Q-rank of realification is twice Q(i)-rank."""
    if not columns:
        return 0
    rows = list(zip(*columns))
    block = [[z[0] for z in row]+[-z[1] for z in row] for row in rows]
    block += [[z[1] for z in row]+[z[0] for z in row] for row in rows]
    r = rank_q(block)
    require(r % 2 == 0, 'odd realification rank')
    return r // 2


def rank_f2(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def beta(d, z, geometry):
    """Build the actual restricted pairing matrix, not a support-size proxy."""
    sources = [j for j, a in enumerate(z) if a != ZERO]
    rows = [sum(((geometry['duals'][i] & geometry['labels'][j]).bit_count() % 2) << k
                for k, j in enumerate(sources))
            for i, a in enumerate(d) if a != ZERO]
    return rank_f2(rows)


def outer_sum(readers, sources):
    n = len(readers[0])
    rr, ii = [[0]*n for _ in range(n)], [[0]*n for _ in range(n)]
    for d, z in zip(readers, sources):
        ds = [(j, a) for j, a in enumerate(d) if a != ZERO]
        zs = [(j, a) for j, a in enumerate(z) if a != ZERO]
        for j, a in ds:
            for k, b in zs:
                c = mul(a, b)
                rr[j][k] += c[0]
                ii[j][k] += c[1]
    return rr, ii


def require_identity(x, t, d, z):
    n = len(x[0])
    require(len(x) == len(t) == 8 and len(d) == len(z), 'term count')
    require(all(len(c) == n for c in x+t+d+z), 'port count')
    require(outer_sum(x+d, t+z) == outer_sum(x, x), 'all-pairs identity')


def collapse(columns, other):
    """Collapse a rank-one column family; factors stay Gaussian rational."""
    n = len(columns[0])
    pivot = next((v for v in columns if any(a != ZERO for a in v)), None)
    if pivot is None:
        return [ZERO]*n, [ZERO]*n
    i = next(i for i, a in enumerate(pivot) if a != ZERO)
    a, b = pivot[i]
    inv = (Fraction(a, a*a+b*b), Fraction(-b, a*a+b*b))
    cs = [mul(col[i], inv) for col in columns]
    require(all(col == scale(pivot, c) for col, c in zip(columns, cs)), 'rank-one collapse premise')
    return pivot, linear(other, cs)


def fixture(name, x, a, d, z, merged_z):
    t = [minus(col, scale(merged_z, c)) for col, c in zip(x, a)]
    return {'name': name, 'T': t, 'D': d, 'Z': z}


def coupled_fixture(name, x, coefficients, sources):
    d = [linear(x, a) for a in coefficients]
    t = [minus(col, linear(sources, [a[j] for a in coefficients]))
         for j, col in enumerate(x)]
    return {'name': name, 'T': t, 'D': d, 'Z': sources}


def examples(x):
    n = len(x[0]); zero = [ZERO]*n
    j, h = list(combinations(range(8), 2))[SEED % 28]
    a = [ZERO]*8; a[j] = ONE
    port = [ZERO]*n; port[SEED] = ONE
    port2 = [ZERO]*n; port2[SEED+1] = ONE
    port3 = [ZERO]*n; port3[SEED+2] = ONE
    cases = []
    cases.append(fixture('zero-added-readers', x, [ZERO]*8, [zero, zero], [x[j], x[h]], zero))
    cases.append(fixture('zero-added-sources-outside', x, [ZERO]*8, [port, port2], [zero, zero], zero))
    for c in [ONE, (-1, 0), I, (1, 1)]:
        # d1 + c*d2 = x_j, while both d's may be outside col(X).
        d2 = port; d1 = minus(x[j], scale(port, c))
        cases.append(fixture('off-column-'+str(c), x, a, [d1, d2], [x[h], scale(x[h], c)], x[h]))
    cases.append(fixture('canceling-off-column', x, [ZERO]*8, [port, scale(port,I)],
                         [x[h], scale(x[h],I)], zero))
    cases.append(fixture('reader-rank-one-source-rank-two', x, a, [x[j], scale(x[j],I)],
                         [minus(x[h],scale(port,I)), port], x[h]))
    cases.append(fixture('three-totals-quotient-two', x, a,
                         [port, port2, minus(minus(x[j],port),port2)], [x[h]]*3, x[h]))
    cases.append(fixture('four-totals-quotient-three', x, a,
                         [port,port2,port3,minus(minus(minus(x[j],port),port2),port3)], [x[h]]*4, x[h]))
    t = [list(col) for col in x]; t[j] = zero; t[h] = zero
    cases.append({'name':'rank-two-disjoint-coordinate-retirement','T':t,'D':[x[j],x[h]],'Z':[x[j],x[h]]})
    cases.append({'name':'basis-mixed-retirement','T':t,
                  'D':[plus(x[j],x[h]),minus(x[j],x[h])],
                  'Z':[scale(plus(x[j],x[h]),(Fraction(1,2),0)),
                       scale(minus(x[j],x[h]),(Fraction(1,2),0))]})
    aa = [[ONE,ZERO,I,ZERO,ZERO,ZERO,ZERO,ZERO],
          [ZERO,ZERO,ZERO,ZERO,ONE,ZERO,(1,1),ZERO]]
    cases.append(coupled_fixture('disjoint-two-complex-lifts',x,aa,
                                 [plus(x[j],scale(port,I)),plus(x[h],port2)]))
    aa = [[ONE,I,ZERO,ZERO,ZERO,ZERO,ZERO,ZERO],
          [ZERO,ZERO,ONE,ONE,ZERO,ZERO,ZERO,ZERO],
          [ZERO,ZERO,ZERO,ZERO,ONE,(0,-1),ZERO,ZERO]]
    cases.append(coupled_fixture('disjoint-three-complex-lifts',x,aa,[x[j],x[h],port]))
    # All four factors nontrivial; exact rank-two block is not a collapse.
    t = [list(col) for col in x]
    t[j] = minus(x[j], plus(x[j],x[h])); t[h] = minus(x[h], minus(x[j],x[h]))
    cases.append({'name':'dense-rank-two-inside-remains-open','T':t,
                  'D':[plus(x[j],x[h]),minus(x[j],x[h])], 'Z':[x[j],x[h]]})
    return cases


def inspect(case, x, geometry):
    t,d,z = case['T'],case['D'],case['Z']
    require_identity(x,t,d,z)
    rd,rz = rank_c(d),rank_c(z)
    q = rank_c(x+d)-8
    require(rz <= len(d)-q, 'quotient rank inequality')
    costs = [beta(v,w,geometry) for v,w in zip(x+d,t+z)]
    collapse_info = None
    if rz <= 1:
        common, merged = collapse(z,d)
        collapse_info = (merged, common)
    elif rd <= 1:
        collapse_info = collapse(d,z)
    else:
        require(q == 0 or len(d) > 2, 'two-total outside reader with independent sources')
    contracted_cost = None
    disjoint_blocks = None
    if collapse_info is not None:
        merged,common = collapse_info
        require_identity(x,t,[merged],[common])
        merged_beta = beta(merged,common,geometry)
        require(merged_beta <= sum(costs[8:]), 'support-rank subadditivity')
        contracted_cost = sum(costs[:8])+merged_beta
        require(contracted_cost >= 64, 'inherited single-lift floor on fixture')
    if q == 0:
        # This finite left inverse is checked, not assumed by the theorem.
        require([[sum(mul(a,b)[0] for a,b in zip(u,v)) for v in x] for u in x]
                == [[56*int(i==j) for j in range(8)] for i in range(8)], 'X Gram left inverse')
        coefficients = [[scale([sum_gaussian(mul(a,b) for a,b in zip(v,col))],
                                (Fraction(1,56),0))[0] for v in x] for col in d]
        require(all(linear(x,a)==col for a,col in zip(coefficients,d)), 'coordinate coefficient reconstruction')
        supports = [{j for j,c in enumerate(a) if c != ZERO} for a in coefficients]
        if sum(map(len,supports)) == len(set().union(*supports)):
            disjoint_blocks = []
            for h,support in enumerate(supports):
                cost = sum(costs[j] for j in support)+costs[8+h]
                require(cost >= 8*len(support), 'disjoint single-lift block floor')
                disjoint_blocks.append({'support':sorted(support),'cost':cost,'floor':8*len(support)})
            require(sum(costs)>=64,'disjoint lifts floor')
    return {'name':case['name'],'extra_terms':len(d),'reader_rank':rd,'source_rank':rz,
            'quotient_rank':q,'source_quotient_rank':rank_c(x+z)-8,
            'ordered_costs':costs,'total_cost':sum(costs),
            'collapsed_cost':contracted_cost,
            'disjoint_blocks':disjoint_blocks,
            'classification':'covered' if collapse_info is not None or disjoint_blocks is not None else 'outside_claim',
            'identity_entries_checked':len(x[0])**2}


def sum_gaussian(values):
    result = ZERO
    for value in values:
        result = add(result,value)
    return result


def controls(x,g,cases):
    names=[]
    def rejects(name, call):
        try: call()
        except ValueError: names.append(name)
        else: raise ValueError('control accepted: '+name)
    import copy
    c=copy.deepcopy(cases[2]);c['Z'][1][SEED]=add(c['Z'][1][SEED],ONE)
    rejects('source-perturbation-breaks-all-pairs',lambda: require_identity(x,c['T'],c['D'],c['Z']))
    c=cases[2]
    rejects('omit-nonzero-extra-term',lambda: require_identity(x,c['T'],c['D'][:1],c['Z'][:1]))
    c=copy.deepcopy(cases[4]);c['Z']=[[(a,-b) for a,b in v] for v in c['Z']]
    rejects('conjugation-is-not-transpose',lambda: require_identity(x,c['T'],c['D'],c['Z']))
    rejects('rank-two-source-cannot-collapse',lambda: collapse(cases[-1]['Z'],cases[-1]['D']))
    require(rank_c([x[0],scale(x[0],I)])==1, 'complex rank control')
    names.append('complex-rank-not-real-column-rank')
    require(inspect(cases[-1],x,g)['classification']=='outside_claim','reject overbroad two-total floor argument')
    names.append('coupled-rank-two-inside-not-classified-as-covered')
    by_name={case['name']:inspect(case,x,g) for case in cases
             if case['name'] in ('rank-two-disjoint-coordinate-retirement','basis-mixed-retirement')}
    require(by_name['rank-two-disjoint-coordinate-retirement']['total_cost']==64
            and by_name['basis-mixed-retirement']['total_cost']==66,'GL2 mixing changes separate-total cost')
    names.append('GL2-basis-change-is-not-cost-free')
    # k=3, q=1 still allows source rank2: an outside canceling pair plus a lift.
    p=[ZERO]*112;p[SEED]=ONE
    a=[ZERO]*8;a[0]=ONE
    boundary=fixture('k3-one-outside-insufficient',x,a,[p,scale(p,(-1,0)),x[0]],
                     [x[1],x[1],x[2]],x[2])
    b=inspect(boundary,x,g)
    require(b['quotient_rank']==1 and b['source_rank']==2 and b['classification']=='outside_claim',
            'k>=3 threshold boundary')
    names.append('k3-one-outside-does-not-force-source-rank-one')
    require(rank_f2([3,5,6])==2 and rank_f2([3,5,7])==3,'F2 rank controls')
    names.append('dependent-and-independent-binary-rows')
    return names,b


def check_sources():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for name,record in manifest['inputs'].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==record['sha256'],'source hash: '+name)
    return manifest


def compute():
    check_sources()
    path=ROOT/'research/p112-single-lift/geometry.py'
    spec=importlib.util.spec_from_file_location('p112_retained_geometry',path)
    gmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(gmod)
    geometry=gmod.build();gmod.check_geometry(geometry)
    x=[[(row[j],0) for row in geometry['X']] for j in range(8)]
    require(rank_c(x)==8,'complex X rank')
    cases=examples(x)
    receipts=[inspect(c,x,geometry) for c in cases]
    names,boundary=controls(x,geometry,cases)
    return {'schema':1,'assignment_seed':SEED,'field':'Gaussian rational, algebraic transpose',
            'scope':'finite boundary fixtures for written quotient/collapse theorem',
            'examples':receipts,'controls':names,'k3_boundary':boundary,
            'full_identity_entries':112*112*(len(cases)+1),
            'classification_counts':dict(Counter(r['classification'] for r in receipts)),
            'no_new_kappa':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',type=Path)
    parser.add_argument('--check',type=Path,default=HERE/'CERTIFICATE.json')
    parser.add_argument('--with-predecessors',action='store_true')
    args=parser.parse_args()
    result=compute()
    if args.with_predecessors:
        # Pinned #998 driver replays both #845 checkers plus its independent checker.
        subprocess.run([sys.executable,'-I','-S','-B',str(ROOT/'research/p112-complex-single-lift/verify.py')],check=True)
    if args.write:
        require(not args.write.exists(),'refusing to overwrite output')
        args.write.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        require(result==json.loads(args.check.read_text()),'certificate mismatch')
    print('PASS_P112_TWO_TOTAL_REDUCTION examples=%d controls=%d floor=64 coupled_rank_two=open no_new_kappa'
          %(len(result['examples']),len(result['controls'])))

if __name__=='__main__':
    main()
