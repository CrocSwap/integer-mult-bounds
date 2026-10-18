#!/usr/bin/env python3
"""Self-contained exact geometry audit for the canonical-span overcomplete bound."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import hashlib,json,math,tarfile
ROOT=Path(__file__).resolve().parents[2]
CANDIDATE_SHA='dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
PAYLOAD_SHA='c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
def need(x,s):
    if not x:raise ValueError(s)
def basis(vectors):
    pivots={}
    for x in vectors:
        while x:
            j=x.bit_length()-1
            if j in pivots:x^=pivots[j]
            else:pivots[j]=x;break
    for j in sorted(pivots):
        for k in pivots:
            if k>j and ((pivots[k]>>j)&1):pivots[k]^=pivots[j]
    return tuple(pivots[j] for j in sorted(pivots))
def rho(a,b):
    return len(basis(sum(((x&y).bit_count()%2)<<j for j,y in enumerate(b)) for x in a))
def closure_premises(spaces,seeds):
    need(() in spaces and all(x in spaces for x in seeds),"missing generator")
    need(all(basis(a+b) in spaces for a in spaces for b in seeds),"not span-closed")
def rejects(fn,label):
    try:fn()
    except ValueError:return label
    raise ValueError("mutation accepted: "+label)
def main():
    raw=(ROOT/'research/p112-rational-decoder-gate/CANDIDATE.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest()==CANDIDATE_SHA,'candidate pin');c=json.loads(raw)
    with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz') as a:
        p=a.extractfile('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json').read()
    need(hashlib.sha256(p).hexdigest()==PAYLOAD_SHA,'payload pin')
    r=sorted(json.loads(p)['recipes'],key=lambda x:x['port']);need([x['port'] for x in r]==list(range(112)),'ports');q=[x['q'] for x in r];g=c['groups']
    need(sorted(x for s in g for x in s)==list(range(112)),'group partition')
    E=[[q[x] for x in s] for s in g]
    need(all((x&y).bit_count()%2==(i==j) for s in E for i,x in enumerate(s) for j,y in enumerate(s)),'orthonormal groups')
    H=[basis(E[i]+E[i+1]) for i in range(1,37,2)];J=basis(E[37]);base=H+[J]
    need(all(rho(x,x)==6 for x in H) and rho(J,J)==3,'component ranks')
    need(all(rho(J,x)==rho(x,J)==3 for x in H),'pureJ cross tariff')
    pair_hist=Counter(rho(a,b) for a in H for b in H);need(min(pair_hist)>=4,'nonpure tariff floor')
    expanded_hist=Counter(rho(J+a,J+b) for a in H for b in H);need(min(expanded_hist)>=6,'bothJ cross floor')
    need(rho(E[0]+E[15]+E[16],E[0]+E[15]+E[16])==7,'residual rank')
    # Induction on subset size: start with zero, repeatedly add each generator.
    # Closure of the resulting set proves every component-support span is present.
    allspaces={()};pending=[()]
    while pending:
        a=pending.pop()
        for b in base:
            z=basis(a+b)
            if z not in allspaces:allspaces.add(z);pending.append(z)
    need(len(allspaces)==40,'forty-space closure')
    closure_premises(allspaces,base)
    controls=[rejects(lambda:closure_premises(allspaces-{H[0]},base),'drop paired-space generator')]
    derived=next(x for x in allspaces if len(x)==8 and x not in base)
    controls.append(rejects(lambda:closure_premises(allspaces-{derived},base),'drop generated non-seed span'))
    closures={a:tuple(i for i,b in enumerate(base) if basis(a+b)==a) for a in allspaces}
    rectangles=Counter();selection_discounts=[]
    for a in allspaces:
        for b in allspaces:
            A=closures[a];B=closures[b]
            if not any(i<18 for i in A) or not any(i<18 for i in B):continue
            rank=rho(a,b)
            if rank>=6:continue
            need(rank in (4,5),'low nonpure rank')
            need(not set(A)&set(B),'disjoint rectangle supports')
            probability=Fraction(1,math.comb(len(A)+len(B),len(A)))
            need(Fraction(6-rank)<=4*probability,'acyclic discount inequality')
            rectangles[(len(A),len(B),rank)]+=1
            selection_discounts.append({'left':A,'right':B,'rank':rank,'probability':str(probability)})
    expected={(1,1,4):20,(1,1,5):178,(1,2,5):33,(2,1,5):33,(1,3,5):4,(3,1,5):4}
    need(dict(rectangles)==expected,'exact cheap-rectangle census')
    # Beyond s=27 the increasing second line is >=309; no unbounded scan needed.
    bounds=[max(334-s,228+3*s) for s in range(28)]
    need(min(bounds)==308 and bounds.index(308)==26 and 228+3*27==309,'integer floor308')
    need(Fraction(308)>Fraction(2672,9),'zero-saving gate rejected')
    out={'candidate_lf_sha256':CANDIDATE_SHA,'payload_sha256':PAYLOAD_SHA,'generated_spaces':40,'seed_spaces':base,'span_closure':sorted(allspaces,key=lambda x:(len(x),x)),'controls':controls,
         'space_dimension_histogram':dict(sorted(Counter(map(len,allspaces)).items())),
         'paired_space_pairing_histogram':dict(sorted(pair_hist.items())),
         'J_enlarged_pairing_histogram':dict(sorted(expanded_hist.items())),
         'pureJ_pairing_rank':3,'low_rectangles':{str(k):v for k,v in sorted(rectangles.items())},
         'bound':'C >= max(334-s,228+3s) >= 308','integer_minimizer_s':26,
         'scope':'Rank57 fitting matrix; BOTH factor sides retained in its canonical row/column spaces; m=57+s nonzero scalar terms. Exterior-factor and higher-rank fits excluded.'}
    print(json.dumps(out,sort_keys=True))
    print('PASS_P112_CANONICAL_SPAN_COST_FLOOR_308')
if __name__=='__main__':main()
