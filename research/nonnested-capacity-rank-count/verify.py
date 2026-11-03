"""Compare joint rank counts with literal finite maps and vector sets.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from itertools import product, combinations
from collections import Counter
from math import comb
import hashlib
import json
import random
import runpy
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
C = runpy.run_path(str(ROOT/'completion.py'))
check = C['require']


def span(basis,n,p):
    vectors = {(0,)*n}
    for b in basis:
        vectors = {tuple((x+c*y)%p for x,y in zip(a,b)) for a in vectors for c in range(p)}
    return frozenset(vectors)


def apply(matrix,vector,p):
    return tuple(sum(x*y for x,y in zip(row,vector))%p for row in matrix)


def matrix_rank(matrix,n,p):
    images = {apply(matrix,x,p) for x in product(range(p),repeat=n)}
    size,r = len(images),0
    while size>1:
        check(size%p == 0,'image size is not a field power')
        size//=p;r+=1
    return r


def all_maps(n,p):
    return [(tuple(tuple(values[i*n:(i+1)*n]) for i in range(n)),
             matrix_rank(tuple(tuple(values[i*n:(i+1)*n]) for i in range(n)),n,p))
            for values in product(range(p),repeat=n*n)]


def literal_histogram(n,p,fixed,capacities,maps):
    targets = [span(b,n,p) for _,b in capacities]
    result = [0]*(n+1)
    for matrix,r in maps:
        if not all(apply(matrix,a,p)==b for a,b in fixed):
            continue
        if all(all(apply(matrix,a,p) in target for a in source)
               for (source,_),target in zip(capacities,targets)):
            result[r]+=1
    return result


def inspect(n,p,fixed,capacities,maps,counts,witness=False):
    eq = C['capacity_equations'](n,p,fixed,capacities)
    actual = C['rank_counts'](n,p,eq)['rank_counts']
    expected = literal_histogram(n,p,fixed,capacities,maps)
    check(actual==expected,'literal contract rank counts differ')
    counts['literal_contracts']+=1
    if witness:
        valid_injection=C['rank'](tuple(a for a,_ in fixed),p,n)==len(fixed) and C['rank'](tuple(b for _,b in fixed),p,n)==len(fixed)
        if valid_injection:
            compressed=C['fixed_rank_counts'](n,p,fixed,capacities)['rank_counts']
            check(compressed==actual,'compressed count differs')
            counts['compressed_literal_comparisons']+=1
        for r in range(n+1):
            if valid_injection:
                other=C['fixed_construct'](n,p,fixed,capacities,r)
                check((other is not None)==(actual[r]>0),'compressed witness existence')
                if other is not None:
                    check(matrix_rank(other,n,p)==r and all(apply(other,a,p)==b for a,b in fixed),'compressed witness rank/fixed image')
                    check(all(all(apply(other,a,p) in span(b,n,p) for a in source) for source,b in capacities),'compressed witness original inclusion')
                    counts['compressed_rank_witnesses']+=1
            matrix = C['construct'](n,p,eq,r)
            check((matrix is not None)==(actual[r]>0),'witness existence differs')
            if matrix is not None:
                check(matrix_rank(matrix,n,p)==r,'independent witness rank')
                check(all(apply(matrix,a,p)==b for a,b in fixed),'fixed image fails')
                check(all(all(apply(matrix,a,p) in span(b,n,p) for a in source)
                          for source,b in capacities),'witness capacity fails')
                counts['rank_witnesses']+=1
    return actual


def subspace_oracle(n,p):
    zero=frozenset({(0,)*n})
    spaces={zero}
    for v in product(range(p),repeat=n):
        for space in tuple(spaces):
            spaces.add(frozenset(tuple((x+c*y)%p for x,y in zip(a,v)) for a in space for c in range(p)))
    return spaces


def run():
    counts=Counter()
    origin=json.loads((ROOT/'ORIGIN.json').read_text());data=(ROOT/origin['local']).read_bytes()
    check(hashlib.sha256(data).hexdigest()==origin['sha256'],'source pin')
    check(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==origin['git_blob'],'source Git blob')
    with tempfile.TemporaryDirectory() as tmp:
        dest=Path(tmp);(dest/'inputs').mkdir()
        for name in ('completion.py','verify.py','ORIGIN.json'):
            shutil.copyfile(ROOT/name,dest/name)
        (dest/origin['local']).write_bytes(data+b'\n')
        try:
            runpy.run_path(str(dest/'verify.py'))['run']()
        except ValueError as error:
            check(str(error)=='source pin','wrong source rejection');counts['source_corruptions']+=1
        else:
            raise ValueError('source mutation accepted')
    domains=((0,2),(1,2),(2,2),(3,2),(2,3),(2,5))
    for n,p in domains:
        exact=subspace_oracle(n,p)
        generated=C['subspaces'](n,p)
        check(len(generated)==len(exact) and {span(b,n,p) for b in generated}==exact,'RREF space census differs')
        counts['subspace_oracle_cases']+=len(exact)
    spaces=C['subspaces'](2,2);maps=all_maps(2,2)
    nonzero=[v for v in product(range(2),repeat=2) if any(v)]
    fixed_cases=[()]+[((a,b),) for a in nonzero for b in nonzero]
    for i,(a,b,c,d,fixed) in enumerate(product(spaces,spaces,spaces,spaces,fixed_cases)):
        inspect(2,2,fixed,((a,b),(c,d)),maps,counts,witness=i%97==0)
    check(counts['literal_contracts']==6250,'incomplete binary joint census')
    rng=random.Random(20261103)
    for n,p in ((3,2),(2,3),(2,5)):
        spaces=C['subspaces'](n,p);maps=all_maps(n,p);vectors=list(product(range(p),repeat=n))
        for i in range(128):
            fixed=tuple((rng.choice(vectors),rng.choice(vectors)) for _ in range(rng.randrange(3)))
            capacities=tuple((rng.choice(spaces),rng.choice(spaces)) for _ in range(rng.randrange(6)))
            inspect(n,p,fixed,capacities,maps,counts,witness=i%17==0)
        for _ in range(24):
            equations=tuple(tuple(rng.randrange(p) for _ in range(n*n+1)) for _ in range(rng.randrange(n*n+2)))
            expected=[0]*(n+1)
            for matrix,r in maps:
                flat=tuple(x for row in matrix for x in row)
                if all(sum(x*y for x,y in zip(row[:-1],flat))%p==row[-1] for row in equations):
                    expected[r]+=1
            check(C['rank_counts'](n,p,equations)['rank_counts']==expected,'arbitrary affine rank histogram')
            counts['arbitrary_affine_systems']+=1
    cross=[]
    sources=((1,0),(0,1),(1,1),(1,2));targets=((1,0),(0,1),(1,1),(1,3))
    maps=all_maps(2,5)
    expected=((1,144,480),(1,44,80),(1,8,16),(1,0,4),(1,0,0))
    for length in range(5):
        for subset in combinations(range(4),length):
            capacities=tuple(((sources[i],),(targets[i],)) for i in subset)
            actual=inspect(2,5,(),capacities,maps,counts,witness=True)
            check(actual==list(expected[length]),'cross-ratio count')
            if subset:
                source_sets=[span((sources[i],),2,5) for i in subset]
                target_sets=[span((targets[i],),2,5) for i in subset]
                check(len(span(tuple(sources[i] for i in subset),2,5))==len(span(tuple(targets[i] for i in subset),2,5)),'subset sum dimensions')
                check(len(set.intersection(*map(set,source_sets)))==len(set.intersection(*map(set,target_sets))),'subset intersection dimensions')
            eq=C['capacity_equations'](2,5,capacities=capacities)
            witness=C['construct'](2,5,eq)
            cross.append(dict(subset=list(subset),rank_counts=actual,
                maximum_rank_witness=None if witness is None else [list(row) for row in witness]))
    # Retained nested source: separate counts 4 and 12, joint count zero.
    n,p=3,2;maps=all_maps(n,p);fixed=(((1,1,0),(0,0,1)),)
    one=(((1,0,0),),((1,0,0),));two=(((0,1,0),),((1,0,0),(0,1,0)))
    nested=[inspect(n,p,fixed,c,maps,counts,witness=True)[n] for c in ((one,),(two,),(one,two))]
    check(nested==[4,12,0],'retained nested compatibility example')
    formulas=[]
    for p in (2,3,5):
        n=4;unit=tuple(tuple(int(i==j) for i in range(n)) for j in range(n))
        free=C['rank_counts'](n,p,())['rank_counts']
        expected_free=[]
        for r in range(n+1):
            numerator=denominator=1
            for i in range(r):
                numerator*=(p**n-p**i)**2
                denominator*=p**r-p**i
            expected_free.append(numerator//denominator)
        check(free==expected_free and sum(free)==p**(n*n),'free matrix rank formula')
        diagonal=tuple(((v,),(v,)) for v in unit)
        eq=C['capacity_equations'](n,p,capacities=diagonal)
        actual=C['rank_counts'](n,p,eq)['rank_counts']
        check(actual==[comb(n,r)*(p-1)**r for r in range(n+1)],'diagonal rank formula')
        block=((unit[:2],unit[:2]),(unit[2:],unit[2:]))
        eq=C['capacity_equations'](n,p,capacities=block)
        actual_block=C['rank_counts'](n,p,eq)['rank_counts']
        h=[1,(p*p-1)**2//(p-1),(p*p-1)*(p*p-p)]
        convolution=[sum(h[i]*h[j] for i in range(3) for j in range(3) if i+j==r) for r in range(5)]
        check(actual_block==convolution,'independent block rank formula')
        formulas.append(dict(field=p,free=free,diagonal=actual,block=actual_block))
        counts['dimension_four_formulas']+=3
    for target in (unit,unit[:3]):
        eq=C['capacity_equations'](4,5,capacities=((unit,target),))
        matrix=C['construct'](4,5,eq)
        check(matrix_rank(matrix,4,5)==len(target),'dimension-four maximum rank')
        check(all(apply(matrix,v,5) in span(target,4,5) for v in unit),'dimension-four inclusion')
        counts['dimension_four_witnesses']+=1
    compressed_records=[]
    for n in (9,12):
        p=2;u=n-2
        unit=tuple(tuple(int(i==j) for i in range(n)) for j in range(n))
        # Use different nontrivial ambient domain and target charts.
        sources=list(unit);targets=list(unit)
        for j in range(n-1):
            sources[j]=tuple(x^y for x,y in zip(sources[j],sources[j+1]))
            targets[j+1]=tuple(x^y for x,y in zip(targets[j+1],targets[j]))
        fixed=tuple(zip(sources[:u],targets[:u]))
        hist=C['fixed_rank_counts'](n,p,fixed)['rank_counts']
        check(hist==[0]*u+[2**(2*u)*x for x in (1,9,6)],'compressed free rank formula')
        mixed_a=tuple(x^y for x,y in zip(sources[0],sources[-1]))
        mixed_b=tuple(x^y for x,y in zip(targets[0],targets[-1]))
        capacities=(((sources[-2],),(targets[-2],)),((mixed_a,),(mixed_b,)))
        constrained=C['fixed_rank_counts'](n,p,fixed,capacities)['rank_counts']
        literal=[0]*(n+1)
        for a,b in product(range(2),repeat=2):
            images=targets[:u]+[tuple(a*x for x in targets[-2]),
                tuple((b*x+(b-1)*y)%2 for x,y in zip(targets[-1],targets[0]))]
            dimension=len(span(tuple(images),n,p)).bit_length()-1
            literal[dimension]+=1
            counts['large_literal_basis_maps']+=1
        check(constrained==literal==[0]*u+[1,2,1],'coupled compressed rank formula')
        for r in (u,u+1,n):
            matrix=C['fixed_construct'](n,p,fixed,capacities,r)
            check(matrix_rank(matrix,n,p)==r,'large independent witness rank')
            check(all(apply(matrix,a,p)==b for a,b in fixed),'large fixed image')
            check(all(all(apply(matrix,a,p) in span(b,n,p) for a in source) for source,b in capacities),'large joint capacity')
            counts['large_compressed_witnesses']+=1
        compressed_records.append(dict(ambient=n,quotient=2,full_lattice_subspaces=sum(C['gaussian'](n,j,p) for j in range(n+1)),used_subspaces=5,free_histogram=hist,coupled_histogram=constrained))
    check(C['rank_counts'](0,2,())['rank_counts']==[1] and C['construct'](0,2,())==(),'zero-dimensional contract')
    invalid=[lambda:C['rank_counts'](5,2,()),lambda:C['rank_counts'](-1,2,()),
             lambda:C['rank_counts'](1,4,()),lambda:C['rank_counts'](True,2,()),
             lambda:C['rank_counts'](1,2,((2,0),)),lambda:C['rank_counts'](1,2,((1,),)),
             lambda:C['rank_counts'](1,2,[(1,0)]),lambda:C['construct'](1,2,(),2),
             lambda:C['capacity_equations'](2,2,(((1,0),(2,0)),)),
             lambda:C['capacity_equations'](2,2,capacities=((((1,),),()),)),
             lambda:C['capacity_equations'](2,2,fixed=[])]
    invalid += [lambda:C['fixed_rank_counts'](5,2,()),
                lambda:C['fixed_rank_counts'](2,2,(((1,0),(1,0)),((1,0),(0,1)))),
                lambda:C['fixed_rank_counts'](2,2,(((1,0),(0,0)),))]
    for f in invalid:
        try:f()
        except ValueError:counts['invalid_inputs']+=1
        else:raise ValueError('invalid input accepted')
    hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('completion.py','verify.py','PROOF.md','ORIGIN.json')}
    return dict(status='PASS_NONNESTED_CAPACITY_RANK_COUNT',counts=dict(counts),cross_ratio=cross,
                nested_source_counts=nested,dimension_four=formulas,compressed=compressed_records,source_hashes=hashes,
                scope='Exact finite-field GL count and construction; exponential bounded API; no native admission or kappa.')


if __name__=='__main__':
    result=run()
    if sys.argv[1:]==['--write']:
        (ROOT/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        check(not sys.argv[1:],'unknown command option')
        check(result==json.loads((ROOT/'RESULT.json').read_text()),'receipt differs')
    print(json.dumps(result,sort_keys=True))
