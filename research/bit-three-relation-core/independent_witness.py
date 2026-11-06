#!/usr/bin/env python3
"""Independent binary enumeration for the explicit five-dimensional core."""
import itertools
import json


def require(ok,message):
    if not ok: raise AssertionError(message)

def parity(x): return x.bit_count()&1

def outer(x,y,n=5): return sum(y<<(i*n) for i in range(n) if x>>i&1)

def span(basis):
    out=[0]
    for v in basis: out += [x^v for x in out]
    return set(out)

def subspaces(n):
    for dim in range(1,n):
        for pivots in itertools.combinations(range(n),dim):
            slots=[(i,j) for i,pivot in enumerate(pivots) for j in range(pivot+1,n) if j not in pivots]
            for mask in range(1<<len(slots)):
                rows=[1<<p for p in pivots]
                for k,(i,j) in enumerate(slots):
                    if mask>>k&1: rows[i]|=1<<j
                yield rows

def action(projector,v):
    x,y=projector
    return x if parity(y&v) else 0

def invariant(projectors,basis):
    vs=span(basis)
    return all(action(p,v) in vs for p in projectors for v in basis)

def run():
    n=5; diag=sum(1<<(i*n+i) for i in range(n))
    off=lambda x:x&~diag
    prescribed=[(1,3),(3,2),(4,12),(12,8),(26,21)]
    patterns=span([1<<1,1<<13,off(outer(26,21))])
    require(len(patterns)==8,'three-dimensional pattern space')
    edge_patterns=[p for p in patterns if p and p.bit_count()==1]
    require(set(edge_patterns)=={1<<1,1<<13},'exactly two edges')
    all_idempotents=[(x,y) for x in range(1,32) for y in range(1,32) if parity(x&y)]
    require(len(all_idempotents)==496,'rank-one idempotent census')
    pool=[(x,y) for x,y in all_idempotents if off(outer(x,y)) in patterns and off(outer(x,y))]
    require(set(pool)==set(prescribed),'complete explicit pool')
    require(len(span([x for x,y in pool]))==32,'joint image dimension five')
    S=[3,2,12,8,16]
    def left(x): return sum(parity(row&x)<<i for i,row in enumerate(S))
    def right(y):
        result=0
        for i,row in enumerate(S):
            if y>>i&1: result^=row
        return result
    require(all(left(left(x))==x for x in range(32)),'involutory shear')
    transformed={(left(x),right(y)) for x,y in pool}
    wanted={(1,1),(2,2),(4,4),(8,8),(31,31)}
    require(transformed==wanted,'exact normal-form alphabet')
    all_subspaces=list(subspaces(5))
    require(len(all_subspaces)==372,'proper nonzero subspace census')
    invariant_original=[b for b in all_subspaces if invariant(pool,b)]
    invariant_normal=[b for b in all_subspaces if invariant(list(wanted),b)]
    require(not invariant_original and not invariant_normal,'irreducibility in both bases')
    require(invariant(pool[:-1],[1,2,4,8]),'control: deleting exceptional projector is reducible')
    require(not invariant(pool,[1,2,4,8]),'exceptional projector breaks four-coordinate core')
    require(off(outer(26,20)) not in patterns or not parity(26&20),'control: wrong covector is rejected')
    print(json.dumps({'status':'PASS_INDEPENDENT_FIVE_DIMENSIONAL_CORE','rank_one_idempotents':len(all_idempotents),'pattern_dimension':3,'edge_count':2,'pool':pool,'joint_image_dimension':5,'proper_nonzero_subspaces':len(all_subspaces),'invariant_subspaces_original':len(invariant_original),'invariant_subspaces_normal_form':len(invariant_normal),'normal_form':sorted(wanted),'controls':2,'scope':'Finite explicit pool, conjugation and irreducibility only; written all-width classification and word-relevance arguments audited separately.'},indent=2))

if __name__=='__main__':run()
