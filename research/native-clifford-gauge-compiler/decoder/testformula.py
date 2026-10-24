#!/usr/bin/env python3
"""Exact transvection-distance cross-check, standard library only."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random


def require(ok, label):
    if not ok:
        raise ValueError(label)


def symp(a, b, n):
    mask=(1<<n)-1
    return (((a & mask) & (b>>n)).bit_count()+((a>>n) & (b & mask)).bit_count()) & 1


def span(rows):
    s={0}
    for x in rows:
        s|={y^x for y in tuple(s)}
    return frozenset(s)


def rank(rows):
    piv={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k not in piv:
                piv[k]=x
                break
            x^=piv[k]
    return len(piv)


def all_lagrangians(n):
    spaces={frozenset({0})}
    for dim in range(n):
        nxt=set()
        for s in spaces:
            for a in range(1,1<<(2*n)):
                if a not in s and all(symp(a,x,n)==0 for x in s):
                    nxt.add(s | frozenset(x^a for x in s))
        spaces=nxt
    return sorted(spaces,key=lambda s:tuple(sorted(s)))


def change_formula(U,V,a,n):
    if a in U or a in V:
        return 0
    u=next((u for u in U if a^u in V),None)
    if u is None:
        return 1
    return -symp(u,a,n)


def actual_change(U,V,a,n):
    moved=frozenset(x ^ (a if symp(x,a,n) else 0) for x in U)
    return (len(U&V).bit_length()-1)-(len(moved&V).bit_length()-1)


def small():
    out=[]
    false_old=0
    for n,expected in [(1,3),(2,15),(3,135)]:
        ls=all_lagrangians(n)
        require(len(ls)==expected,'Lagrangian count')
        count=0
        for U in ls:
            moves={a:frozenset(x ^ (a if symp(x,a,n) else 0) for x in U) for a in range(1,1<<(2*n))}
            for V in ls:
                old=(len(U&V).bit_length()-1)
                summed={u^v:u for u in U for v in V}
                for a,moved in moves.items():
                    actual=old-(len(moved&V).bit_length()-1)
                    if a in U or a in V:
                        predicted=0
                    elif a not in summed:
                        predicted=1
                    else:
                        predicted=-symp(summed[a],a,n)
                        if predicted==0:
                            false_old+=1
                    require(actual==predicted,'Exact small transvection distance')
                    count+=1
        out.append({'n':n,'lagrangians':len(ls),'ordered_pair_axis_cases':count})
    require(false_old>0,'Quadratic-free false formula rejected')
    return {'exhaustive':out,'quadratic_free_negative_controls':false_old}


def mv(cols,x):
    out=0
    while x:
        k=(x & -x).bit_length()-1
        out^=cols[k]
        x&=x-1
    return out


def actual_graph(path):
    raw=path.read_bytes();t=iter(map(int,raw.split()))
    n,f,m,e=[next(t) for _ in range(4)]
    nodes=[(next(t),next(t)) for _ in range(n)]
    frames=[[next(t) for _ in range(9)] for _ in range(f)]
    maps=[[next(t) for _ in range(18)] for _ in range(m)]
    edges=[tuple(next(t) for _ in range(5)) for _ in range(e)]
    require(next(t,None) is None,'Whole graph input consumed')
    for B in frames:
        require(rank(B)==9,'Actual Lagrangian dimension')
        require(all(symp(x,y,9)==0 for x in B for y in B),'Actual isotropic frame')
    for C in maps:
        require(rank(C)==18,'Actual map invertible')
        require(all(symp(C[i],C[j],9)==symp(1<<i,1<<j,9) for i in range(18) for j in range(18)),'Actual symplectic native map')
    rng=random.Random(20261022)
    chosen=[x for x in edges if x[4]!=0]
    chosen += rng.sample([x for x in edges if x[4]==0],min(1000,sum(x[4]==0 for x in edges)))
    count=0;fixed=0;quadratic_zero=0
    for a,b,r,sign,mapid in chosen:
        U=frames[nodes[a][0]]
        V=frames[nodes[b][0]]
        U=[mv(maps[mapid],x) for x in U]
        require(rank(U+V)-9==r,'Actual source mapped rank')
        US,VS=span(U),span(V)
        for axis in [rng.randrange(1,1<<18) for _ in range(64)]:
            actual=actual_change(US,VS,axis,9)
            predicted=change_formula(US,VS,axis,9)
            require(actual==predicted,'Actual nine-dimensional mapped contact delta')
            count+=1
            fixed+=axis in US
            quadratic_zero+=axis not in US and axis not in VS and predicted==0
    return {'source_sha256':sha256(raw).hexdigest(),'nodes':n,'frames_checked':f,'symplectic_maps_checked':m,'mapped_warp_edges':sum(x[4]!=0 for x in edges),'sampled_edges':len(chosen),'exact_axis_cases':count,'fixed_U_axes':fixed,'quadratic_zero_cases':quadratic_zero}


def main():
    p=argparse.ArgumentParser();p.add_argument('--graph',type=Path);p.add_argument('--write',type=Path)
    args=p.parse_args()
    out={'status':'PASS_EXACT_TRANSVECTION_DISTANCE','small':small()}
    if args.graph:
        out['actual']=actual_graph(args.graph)
    if args.write:
        args.write.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(out,sort_keys=True))


if __name__=='__main__':
    main()
