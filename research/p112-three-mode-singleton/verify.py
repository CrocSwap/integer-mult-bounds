#!/usr/bin/env python3
"""Finite premises for the three-mode, singleton-sided P112 COPY theorem.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
Geometry: Mihir Srivastava / PR845, following DreamingOfClouds / PR717.
Support arrangements and compensation: PR1512 and Gareth Davidson / PR1468.
The quantified proof is in README.md; examples alone are not that proof.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations, permutations, product
import json
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
GEOMETRY = 'research/p112-single-lift/geometry.py'
INPUTS = {GEOMETRY, 'research/complex-decoder-field-extension-seed44/PROOF.md'}
TRIPLE = (2, 4, 5)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def bits(n):
    while n:
        b = n & -n
        yield b.bit_length() - 1
        n ^= b


def mask(indices):
    return sum(1 << i for i in indices)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def basis(rows):
    pivots = {}
    for r in rows:
        while r:
            k = r.bit_length() - 1
            if k not in pivots:
                pivots[k] = r
                break
            r ^= pivots[k]
    return [pivots[k] for k in sorted(pivots, reverse=True)]


def pairing(left_duals, right_labels):
    return len(basis(sum(((a & b).bit_count() % 2) << k
                         for k, a in enumerate(left_duals)) for b in right_labels))


def canonical(v):
    g = gcd(*v)
    if not g:
        return None
    v = tuple(x//g for x in v)
    return v if next(x for x in v if x) > 0 else tuple(-x for x in v)


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def load_geometry():
    rows = json.loads((PACKAGE/'SOURCES.json').read_text())['files']
    live = [r for r in rows if r['usage'] == 'input']
    require(len(live) == len(INPUTS) and {r['path'] for r in live} == INPUTS,
            'incomplete live source inventory')
    for r in live:
        p = ROOT/r['path']
        require(p.resolve().is_relative_to(ROOT.resolve()), 'external source path')
        data = p.read_bytes()
        require(hashlib.sha256(data).hexdigest() == r['sha256'], 'source SHA256: '+r['path'])
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == r['git_blob'],
                'source Git blob: '+r['path'])
    spec = importlib.util.spec_from_file_location('pinned_p112_geometry', ROOT/GEOMETRY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raw = module.build()
    module.check_geometry(raw)
    order = sorted(range(112), key=lambda i: max(tuple(raw['roots'][i]), tuple(-z for z in raw['roots'][i])))
    roots, x, labels, duals = [], [], [], []
    for i in order:
        sign = 1 if tuple(raw['roots'][i]) > tuple(-z for z in raw['roots'][i]) else -1
        roots.append([sign*z for z in raw['roots'][i]])
        x.append([sign*z for z in raw['X'][i]])
        labels.append(raw['labels'][i]); duals.append(raw['duals'][i])
    b = [[(duals[i]&labels[j]).bit_count() % 2 for j in range(112)] for i in range(112)]
    require(len(set(labels)) == 112 and all(labels), 'distinct nonzero labels')
    require(len(basis(labels)) == len(basis(duals)) == 9, 'nondegenerate nine-dimensional labels')
    require(all(dot(x[i], x[j]) == dot(roots[i], roots[j])//2
                and b[i][j] == (1+dot(roots[i], roots[j])//4) % 2
                for i in range(112) for j in range(112)), 'geometry identities')
    return roots, x, labels, duals, b


def strata(x):
    rows = [tuple(r[k] for k in TRIPLE) for r in x]
    normals = sorted({canonical(r) for r in rows}-{None})
    rank_two = {canonical(cross(a,b)) for a,b in combinations(normals,2)}-{None}
    require(len(normals) == 13 and len(rank_two) == 25, 'proper flat census')
    coefficients = set(rank_two)
    for n in normals:
        a = next((a for a in product(range(-4,5), repeat=3)
                  if any(a) and dot(a,n) == 0 and all(dot(a,m) for m in normals if m != n)), None)
        require(a is not None, 'rank-one flat representative')
        coefficients.add(canonical(a))
    require(all(dot((1,3,9),n) for n in normals), 'generic flat representative')
    coefficients.add((1,3,9))
    out = sorted((a,mask(i for i,r in enumerate(rows) if dot(r,a))) for a in coefficients)
    require(len(out) == len({s for _,s in out}) == 39, '39 distinct supports')
    return out


def coordinate_transports(x, b):
    tetrads = {mask(k for k,v in enumerate(r) if v) for r in x}
    lookup = {max(tuple(r),tuple(-v for v in r)):i for i,r in enumerate(x)}
    out = {}
    for perm in permutations(range(8)):
        target = tuple(sorted(perm[k] for k in TRIPLE))
        if target in out or any(mask(perm[k] for k in bits(t)) not in tetrads for t in tetrads):
            continue
        line_map, signs = [], []
        for r in x:
            new = [0]*8
            for k in range(8): new[perm[k]] = r[k]
            key = max(tuple(new),tuple(-v for v in new))
            require(key in lookup, 'invalid coordinate transport')
            i = lookup[key]; line_map.append(i); signs.append(1 if new == x[i] else -1)
        require(len(set(line_map)) == 112, 'transport bijection')
        require(all(b[i][j] == b[line_map[i]][line_map[j]] for i in range(112) for j in range(112)),
                'transport pairing')
        out[target] = {'target':list(target), 'permutation':list(perm), 'signed_map_sha256':digest([line_map,signs])}
        if len(out) == 56: break
    require(set(out) == set(combinations(range(8),3)), 'all triples covered')
    return [out[t] for t in sorted(out)]


# Exact Gaussian-rational examples test the factor contract, not the quantifier.
ZERO, ONE, IMAG = (0,0), (1,0), (0,1)
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def neg(a): return (-a[0],-a[1])
def mul(a,b): return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def conj(a): return (a[0],-a[1])
def divide(a,b):
    n = b[0]*b[0]+b[1]*b[1]
    require(bool(n), 'singular fixture matrix')
    z = mul(a,conj(b))
    return (Fraction(z[0],n),Fraction(z[1],n))
def identity(n): return [[ONE if i==j else ZERO for j in range(n)] for i in range(n)]
def transpose(a): return list(map(list,zip(*a)))
def mm(a,b):
    out=[]
    for row in a:
        values=[]
        for col in zip(*b):
            v=ZERO
            for s,t in zip(row,col):
                if s != ZERO and t != ZERO: v=add(v,mul(s,t))
            values.append(v)
        out.append(values)
    return out
def inverse(a):
    n=len(a); rows=[list(r)+e for r,e in zip(a,identity(n))]
    for k in range(n):
        pivot=next((i for i in range(k,n) if rows[i][k] != ZERO),None)
        require(pivot is not None,'singular fixture matrix')
        rows[k],rows[pivot]=rows[pivot],rows[k]
        z=rows[k][k]; rows[k]=[divide(v,z) for v in rows[k]]
        for i in range(n):
            if i != k:
                z=rows[i][k]; rows[i]=[add(v,neg(mul(z,w))) for v,w in zip(rows[i],rows[k])]
    return [r[n:] for r in rows]


def fixtures(x,labels,duals,b):
    y=[[(r[k],0) for k in TRIPLE] for r in x]
    site=0
    boundary=[(r[TRIPLE[0]],0) if not b[i][site] else ZERO for i,r in enumerate(x)]
    dense=[(1,i%3-1) if not b[i][site] else ZERO for i in range(112)]
    small=[ZERO]*112; small[next(i for i in range(112) if not b[i][site])]=(1,1)
    v=[ONE if i==site else ZERO for i in range(112)]
    shear=identity(4); shear[3][0]=(-1,0)
    complex_m=identity(4)
    for i,j,z in [(3,0,IMAG),(0,1,ONE),(2,3,(1,1)),(1,2,ONE)]:
        e=identity(4);e[i][j]=z; complex_m=mm(complex_m,e)
    right_pure=identity(4);right_pure[0][3]=ONE;right_pure[1][3]=IMAG
    cases=[('identity',boundary,identity(4),False),('compensation',boundary,shear,False),
           ('dense_complex',dense,complex_m,False),('singleton_entry',small,complex_m,False),
           ('zero_correction',[ZERO]*112,complex_m,False),('right_pure',dense,right_pure,False),
           ('transposed_compensation',boundary,shear,True)]
    results=[]; saved={}
    for name,u,m,transposed in cases:
        require(all(u[i]==ZERO or not b[i][site] for i in range(112)), 'nonfree correction')
        n=transpose(inverse(m))
        require(mm(m,transpose(n))==identity(4),'coupled inverse identity')
        left=[r+[z] for r,z in zip(y,u)];right=[r+[z] for r,z in zip(y,v)]
        d,t=mm(left,m),mm(right,n)
        expected=[[add((dot([x[i][k] for k in TRIPLE],[x[j][k] for k in TRIPLE]),0),mul(u[i],v[j]))
                   for j in range(112)] for i in range(112)]
        if transposed: d,t=t,d;expected=transpose(expected)
        require(mm(d,transpose(t))==expected,'full ordinary-transpose product')
        require(all(expected[i][j]==(dot([x[i][k] for k in TRIPLE],[x[j][k] for k in TRIPLE]),0)
                    for i in range(112) for j in range(112) if b[i][j]),'masked identity')
        ranks=[pairing(basis(duals[i] for i in range(112) if d[i][k]!=ZERO),
                       basis(labels[i] for i in range(112) if t[i][k]!=ZERO)) for k in range(4)]
        require(sum(ranks)>=24,'fixture COPY bound')
        a0=sum(all(m[k][h]==ZERO for k in range(3)) for h in range(4))
        b0=sum(all(n[k][h]==ZERO for k in range(3)) for h in range(4))
        sizes=[sum(z!=ZERO for z in u),1]
        if transposed: a0,b0=b0,a0;sizes.reverse()
        results.append({'name':name,'site':site,'correction_support_sizes':sizes,
                        'replacement_ranks':ranks,'whole_copy_sum':40+sum(ranks),
                        'zero_left_projections':a0,'zero_right_projections':b0,'checked_entries':112*112})
        saved[name]=(left,right,m,d,t,expected)
    require(results[0]['replacement_ranks']==[8,8,8,0],'attaining positive fixture')
    require(results[1]['replacement_ranks']==[7,8,8,7],'per-child rank-eight assertion must fail')
    require(results[2]['zero_left_projections']==results[2]['zero_right_projections']==0,'all-active fixture')
    left,right,m,d,t,target=saved['compensation']
    omitted=mm([r[:3] for r in d],transpose([r[:3] for r in t]))
    bad=next(((i,j) for i in range(112) for j in range(112) if b[i][j] and omitted[i][j]!=target[i][j]),None)
    require(bad is not None,'omitted compensation must violate constrained entry')
    require(mm(mm(left,m),transpose(mm(right,inverse(m))))!=target,'wrong inverse orientation must fail')
    left,right,m,d,t,target=saved['dense_complex']
    hermitian=transpose([[conj(z) for z in row] for row in inverse(m)])
    require(mm(mm(left,m),transpose(mm(right,hermitian)))!=target,'Hermitian substitution must fail')
    singular=identity(4);singular[3]=singular[2][:];rejected=False
    try: inverse(singular)
    except ValueError: rejected=True
    require(rejected,'singular mixing must fail')
    return results, {'omitted_compensation_entry':list(bad),'wrong_inverse_rejected':True,
                     'hermitian_substitution_rejected':True,'singular_mixing_rejected':True,
                     'rank_eight_per_active_term_refuted':True}


def build_certificate():
    roots,x,labels,duals,b=load_geometry();ss=strata(x)
    right=[basis(labels[i] for i in bits(s)) for _,s in ss]
    chars=[mask(i for i,l in enumerate(labels) if (l&q).bit_count()%2) for q in range(512)]
    require(len(set(chars))==512,'all label characters')
    spectra=Counter();slice_counts=Counter();pair_counts=Counter();original=Counter();rows=[]
    for a,s in ss:
        full=basis(duals[i] for i in bits(s));weights=Counter((s&c).bit_count() for c in chars)
        distance=min(w for w in weights if w);spectra[distance]+=1
        require(distance>=12,'singleton and small-erasure premise')
        orig=[pairing(full,c) for c in right]
        require(min(orig)>=8,'unmodified support pairing');original.update(orig)
        dimensions=[];table=[]
        for site in range(112):
            surviving=basis(duals[i] for i in bits(s) if b[i][site])
            dimensions.append(len(surviving));slice_counts[len(surviving)]+=1
            ranks=[pairing(surviving,c) for c in right]
            require(min(ranks)>=7,'one-anchor pairing bound')
            table.append(''.join(map(str,ranks)));pair_counts.update(ranks)
        rows.append({'coefficient':list(a),'support_hex':format(s,'028x'),'span':len(full),
                     'erasure_spectrum':{str(k):v for k,v in sorted(weights.items())},'minimum_erasure':distance,
                     'original_pair_ranks':''.join(map(str,orig)),'survivor_dimensions':''.join(map(str,dimensions)),
                     'survivor_pair_ranks':table})
    transports=coordinate_transports(x,b);examples,controls=fixtures(x,labels,duals,b)
    envelopes=[[8,8,8,0],[7,7,7,7],[7,7,7,3]]
    require(all(sum(v)>=24 and all(0<=t<=8 for t in v) for v in envelopes),'power-bill envelopes')
    require(2**3-1<12,'large-support pure-factor dimension')
    return {'schema_version':1,'status':'FINITE_PREMISES_FOR_WRITTEN_SINGLETON_THREE_MODE_THEOREM',
            'triple':list(TRIPLE),'geometry':{'roots_sha256':digest(roots),'coordinates_sha256':digest(x),
                                            'pairing_sha256':digest(b),'ports':112,'label_rank':9},
            'strata':rows,'transports':transports,'fixtures':examples,'controls':controls,
            'summary':{'strata':39,'proper_flats_by_rank':[1,13,25],'sites':112,'coordinate_triples':56,
                       'character_support_evaluations':39*512,'minimum_erasure':min(spectra),
                       'erasure_distance_counts':dict(sorted(spectra.items())),
                       'original_pair_counts':dict(sorted(original.items())),
                       'survivor_dimension_counts':dict(sorted(slice_counts.items())),
                       'survivor_pair_counts':dict(sorted(pair_counts.items())),
                       'survivor_pair_cases':39*112*39,'minimum_survivor_pair_rank':min(pair_counts),
                       'capped_lower_envelopes':envelopes,'sharp_whole_copy_sum':64,
                       'fixture_entries':len(examples)*112*112}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--write',type=Path,help='write a new deterministic receipt; refuses overwrite')
    group.add_argument('--check',type=Path,default=PACKAGE/'CERTIFICATE.json')
    args=parser.parse_args();result=json.loads(json.dumps(build_certificate()))
    if args.write:
        with args.write.open('x') as f: json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    else: require(result==json.loads(args.check.read_text()),'certificate mismatch')
    print('PASS_P112_THREE_MODE_SINGLETON strata=39 sites=112 pairings=170352 copy_floor=64 controls=5')


if __name__=='__main__': main()
