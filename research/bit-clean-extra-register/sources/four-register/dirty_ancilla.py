"""Check two exact eleven-factor words from three binary basis layers."""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
import json,time,sys
from pathlib import Path

W=4; E=8; MAXREL=3
ID=sum(1<<(i*W+i) for i in range(W))
OFF=sum(1<<(i*W+j) for i in range(W) for j in range(W) if i!=j)
BITS=[tuple((s>>i)&1 for i in range(E)) for s in range(1<<E)]
UNIT=[BITS[1<<i] for i in range(E)]

@lru_cache(None)
def rref(rows):
    a=[list(map(Fraction,r)) for r in rows];out=[]
    for col in range(E):
        idx=next((i for i in range(len(a)) if a[i][col]),None)
        if idx is None:continue
        r=a.pop(idx);d=r[col];r=[x/d for x in r]
        a=[[x-s[col]*y for x,y in zip(s,r)] for s in a]
        out=[[x-s[col]*y for x,y in zip(s,r)] for s in out]
        out.append(r)
    return tuple(tuple(r) for r in out)

@lru_cache(None)
def rep(state,v):
    v=list(v)
    for r in state:
        p=next(i for i,x in enumerate(r) if x)
        d=v[p]
        if d:v=[x-d*y for x,y in zip(v,r)]
    return tuple(v)

@lru_cache(None)
def add(state,diff):
    nxt=rref(state+(diff,))
    if any(not any(rep(nxt,u)) for u in UNIT):return None
    return nxt

def outer(x,y):return sum(((x>>i)&1)*((y>>j)&1)<<(W*i+j) for i in range(W) for j in range(W))

def times_projection(m,x,y):
    mx=sum((((m>>(W*i))&15)&x).bit_count()%2<<i for i in range(W))
    return outer(mx,y)

def polynomial(word):
    poly={0:ID}
    for j,(x,y) in enumerate(word):
        nxt={}
        for a,m in poly.items():
            b=times_projection(m,x,y);c=m^b
            if c:nxt[a]=c
            if b:nxt[a|1<<j]=b
        poly=nxt
    return tuple(poly.items())

def gf2_rank(vs):
    b={}
    for v in vs:
        while v:
            k=v.bit_length()-1
            if k in b:v^=b[k]
            else:b[k]=v;break
    return len(b)

import math,functools

def primitive_parity(r):
    den=math.lcm(*(x.denominator for x in r))
    row=[int(x*den) for x in r]
    g=functools.reduce(math.gcd,row)
    return sum(((x//g)&1)<<i for i,x in enumerate(row))


def solve(word):
    poly=polynomial(word)
    first_order=[sum(((outer(x,y)>>bit)&1)<<j for j,(x,y) in enumerate(word)) for bit in range(W*W) if OFF>>bit&1]
    seen=set();stats={'nodes':0,'terminals':0,'low_rank_targets':0,'zero_frame_branches':0,'parity_branches':0,'terminal_relations':[],'wrong_zero_count':0}
    found=[]
    def rec(state):
        stats['nodes']+=1
        if state in seen:return False
        seen.add(state)
        if gf2_rank(first_order+[primitive_parity(r) for r in state])>MAXREL:
            stats['parity_branches']+=1;return False
        grouped={}
        for s,c in poly:
            key=rep(state,BITS[s]);grouped[key]=grouped.get(key,0)^c
        terms=[(a,c) for a,c in grouped.items() if c]
        offending=[(a,c&OFF) for a,c in terms if c&OFF]
        if not offending:
            stats['terminals']+=1
            stats['terminal_relations'].append([[str(x) for x in r] for r in state])
            targets=[]
            for i in range(W):
                tt=[v for v,c in terms if c>>(W*i+i)&1]
                assert len(tt)==1,(state,tt)
                targets.append(tt[0])
            for ancilla in range(W):
                nxt=state if not any(targets[ancilla]) else add(state,targets[ancilla])
                if nxt is None or len(nxt)>MAXREL:continue
                if gf2_rank(first_order+[primitive_parity(r) for r in nxt])>MAXREL:continue
                low=False
                for i,t in enumerate(targets):
                    if i==ancilla:continue
                    if any(not any(rep(rref(nxt+(UNIT[a],UNIT[b])),t)) for a,b in combinations(range(E),2)):
                        low=True;break
                if low:
                    stats['low_rank_targets']+=1;continue
                found.append({'ancilla':ancilla,'relations':[[str(x) for x in r] for r in nxt],'targets':[[str(x) for x in rep(nxt,t)] for t in targets]})
                return True
            return False
        if len(state)>=MAXREL:return False
        best=None
        for bit in range(W*W):
            if not OFF>>bit&1:continue
            tt=[v for v,c in offending if c>>bit&1]
            if tt and (best is None or len(tt)<len(best)):best=tt
        if len(best)<2:return False
        u=best[0]
        for v in best[1:]:
            nxt=add(state,tuple(a-b for a,b in zip(u,v)))
            if nxt is None:stats['zero_frame_branches']+=1;continue
            if rec(nxt):return True
        return False
    rec(())
    return {'stats':stats,'candidate':found,'word':word,'polynomial_terms':len(poly)}


from itertools import permutations,product

def permute_vector(x,p):
    return sum(((x>>i)&1)<<p[i] for i in range(W))

def canonical(layers):
    choices=[]
    for p in permutations(range(W)):
        ls=[tuple(sorted((permute_vector(x,p),permute_vector(y,p)) for x,y in layer)) for layer in layers]
        for seq in (ls,list(reversed(ls))):
            choices.append(tuple(pair for layer in seq for pair in layer))
    return min(choices)

def valid_distance(word):
    possible=set(range(4))
    for side in (0,1):
        for r in range(1,16):
            calls=sum((r&xy[side]).bit_count()%2 for xy in word)
            if calls<3:
                if r.bit_count()!=1:return False
                possible&={r.bit_length()-1}
    return bool(possible)

if __name__=='__main__':
    basisH=[(15^(1<<i),15^(1<<i)) for i in range(4)]
    basisI=[(1<<i,1<<i) for i in range(4)]
    jobs={}
    for sizes in ((3,2,3),(2,2,2,2)):
        bases=[basisH if i%2==0 else basisI for i in range(len(sizes))]
        for choices in product(*(list(combinations(b,n)) for b,n in zip(bases,sizes))):
            word=canonical(choices)
            if valid_distance(word):jobs[word]=sizes
    print(json.dumps({'jobs':len(jobs)}),flush=True)
    out=[]
    for i,(word,sizes) in enumerate(sorted(jobs.items())):
        start=time.time();result=solve(word);result['sizes']=sizes;result['seconds']=time.time()-start;result['job']=i
        print(json.dumps(result),flush=True);out.append(result)
        Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
        rref.cache_clear();rep.cache_clear();add.cache_clear()
