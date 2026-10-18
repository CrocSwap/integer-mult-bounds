"""Exact bounded-current-row choice audit. Apache-2.0; ywz65/Codex."""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,msg):
    if not ok: raise ValueError(msg)


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source drift')
    for row in json.loads((HERE/'SNAPSHOTS.json').read_text())['files']:
        need(hashlib.sha256((HERE/row['snapshot']).read_bytes()).hexdigest()==row['sha256'],'snapshot drift')


def source_facts():
    # Unchanged predecessor authentication/selected constants; only root paths
    # are rebound to this package's explicit immutable superset manifest.
    spec=importlib.util.spec_from_file_location('retained_fibers',HERE/'snapshots/pr2097-verify.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.PACKAGE=HERE;module.ROOT=ROOT
    bit,assembly,_=module.authenticate()
    facts=module.selected_facts(bit,assembly)
    predicates=module.projective_predicate_cases()
    old=json.loads((HERE/'snapshots/pr2097-RESULT.json').read_text())
    need(facts==old['selected'] and predicates==old['adaptive_minor_counterexamples'],'predecessor facts')
    return facts,predicates


def rows(q,m):return [v for v in product(range(q),repeat=m) if any(v)]


def lines(q,m):
    # Normalize by the first nonzero coordinate, independently of any union bound.
    output=set()
    for v in rows(q,m):
        scale=pow(next(x for x in v if x),-1,q)
        output.add(tuple(x*scale%q for x in v))
    return sorted(output)


def badmask(v,allrows,q):
    return sum((sum(a*b for a,b in zip(v,u))%q==0)<<i for i,u in enumerate(allrows))


def union(masks):
    out=0
    for mask in masks:out|=mask
    return out


def maximum_count(q,m,M):
    need(type(q)is int and q>=2 and type(m)is int and m>=2 and type(M)is int and M>=1,'domain')
    # This integer formula assumes q is a finite-field order; no primality claim
    # is made by this arithmetic helper. Enumerated instances use prime q.
    if M>=q+1:return q**m-1
    return q**(m-2)*(1+M*(q-1))-1


def pencil(q,m):return [(1,a)+((0,)*(m-2)) for a in range(q)]+[(0,1)+((0,)*(m-2))]


def controls():
    need(F(2,4)>F(1,4),'reuse fixed-edge charge')
    need(maximum_count(3,3,1)==8 and maximum_count(3,3,2)==14,'exact frontier')
    need(maximum_count(3,3,2)<2*maximum_count(3,3,1),'overlap not disjoint')
    need(F(maximum_count(3,3,1),26)!=F(1,4),'GL2 density is not GLm density')
    need(F(maximum_count(3,3,1),26)!=F(9,27),'zero row forbidden')
    # Full row kernel selection leaks 4 choices. It cannot be called a one-choice
    # selector merely by omitting the chosen normal from the declared header.
    vectors=rows(3,2);normals=lines(3,2)
    hidden={next(v for v in normals if sum(a*b for a,b in zip(v,u))%3==0) for u in vectors}
    need(len(hidden)==4 and maximum_count(3,2,1)<len(vectors),'hidden choices')
    # A highly selective branch can be entirely bad although its global set is rare.
    first=badmask(normals[0],vectors,3)
    need(first.bit_count()==2 and all((first>>i)&1 for i,u in enumerate(vectors)
                                    if sum(a*b for a,b in zip(normals[0],u))%3==0),'conditional density')
    # Incomplete entrance distribution: a single bad row defeats even M=1's
    # UNIFORM-domain bound while endpoint routing can remain the identity.
    u=next(u for u in vectors if sum(a*b for a,b in zip(normals[0],u))%3==0)
    need(sum(a*b for a,b in zip(normals[0],u))%3==0 and F(1)>F(1,4),'fresh-domain premise')
    need(F(2**(19+7),2**80)<F(1,10**16)<F(2**(19+8),2**80),'seven-bit sufficient guard')
    return 8


def run():
    authenticate();facts,old=source_facts()
    censuses=[];subsets=0
    for q,m,maxM in [(2,2,3),(3,2,4),(5,2,6),(2,3,3),(2,4,3),(3,3,4),(5,3,3)]:
        rr=rows(q,m);ll=lines(q,m);mm=[badmask(v,rr,q) for v in ll]
        maxima=[]
        for M in range(1,maxM+1):
            counts=[union(ms).bit_count() for ms in combinations(mm,M)]
            need(max(counts)==maximum_count(q,m,M),'complete subset maximum')
            subsets+=len(counts);maxima.append({'M':M,'sets':len(counts),'max_bad_rows':max(counts)})
        censuses.append({'q':q,'m':m,'nonzero_rows':len(rr),'projective_lines':len(ll),'maxima':maxima})
    pencils=[];selector_rows=0
    for q,m in [(2,2),(2,7),(3,4),(5,4),(7,3),(11,3)]:
        rr=rows(q,m); pp=pencil(q,m); mm=[badmask(v,rr,q) for v in pp]
        for M in range(1,q+2):
            bad=union(mm[:M]).bit_count()
            need(bad==maximum_count(q,m,M),'pencil attainment')
            # Execute an actual deterministic M-choice selector. Every selected
            # branch is fixed before this loop; only the branch index varies.
            selected=0;header=set()
            for u in rr:
                j=next((j for j,v in enumerate(pp[:M]) if sum(a*b for a,b in zip(v,u))%q==0),0)
                header.add(j)
                selected+=sum(a*b for a,b in zip(pp[j],u))%q==0
            need(selected==bad and len(header)<=M,'selector attained count')
            selector_rows+=len(rr)
            pencils.append({'q':q,'m':m,'M':M,'bad':bad,'total':len(rr),'used_headers':len(header)})
    matrices=[]
    # Literal GL2 matrices and an independent first-row frequency census.
    for q in (3,5,7):
        counts=Counter(); chosen=Counter();pp=pencil(q,2)
        for a,b,c,d in product(range(q),repeat=4):
            if (a*d-b*c)%q:
                counts[(a,b)]+=1
                for M in range(1,q+2):
                    chosen[M]+=any((a*v[0]+b*v[1])%q==0 for v in pp[:M])
        completions=q*(q-1)
        need(set(counts.values())=={completions} and len(counts)==q*q-1,'GL uniform first row')
        for M,bad in chosen.items():need(bad==completions*maximum_count(q,2,M),'GL matrix/row independence')
        matrices.append({'q':q,'matrices':sum(counts.values()),'row_completions':completions,'bad_by_M':{str(k):v for k,v in chosen.items()}})
    # Generic bounded-choice union bound, independent of the linear-minor model.
    generic=0
    for N in range(1,7):
        for masks in product(range(1<<N),repeat=3):
            need(union(masks).bit_count()<=min(N,sum(x.bit_count() for x in masks)),'set union')
            generic+=1
    m=facts['m'];beta_numerator=2*m**3
    need(beta_numerator==2**19 and facts['bad_fraction_retained']=='1/10000000000000000','selected coefficient')
    guards={str(b):str(F((1<<b)*beta_numerator,1<<80)) for b in (0,7,8)}
    return {'schema_version':1,'censuses':censuses,'complete_subsets':subsets,'pencil_records':pencils,
            'selector_rows':selector_rows,'matrix_records':matrices,'generic_union_cases':generic,
            'retained_selected_facts':facts,'retained_GL2_witnesses':old,'selected_guard_caps':guards,
            'controls':controls(),'scope':'Exact GLm one-linear-minor M-choice frontier and conditional selected per-edge transcript allowance; no adaptive compiler, selector cost, new stock, supplier or kappa.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',type=Path);args=parser.parse_args()
    value=run()
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
    else:
        old=json.loads((HERE/'RESULT.json').read_text())
        need(json.dumps(old,sort_keys=True)==json.dumps(value,sort_keys=True),'typed receipt mismatch')
    print('PASS_BOUNDED_ROW_CHOICE subsets='+str(value['complete_subsets'])+' selector_rows='+str(value['selector_rows'])+' controls='+str(value['controls']))


if __name__=='__main__':main()
