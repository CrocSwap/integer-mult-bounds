#!/usr/bin/env python3
"""Charles Bethin, with OpenAI Codex assistance. Apache-2.0.
Independent finite lemmas for the written arbitrary-shear port argument.
No imported predecessor verifier. No supplier or complete theorem claim.
"""
import itertools as it
M=((1,1,1),(1,1,-1),(1,-1,0))

def need(ok,msg):
    if not ok: raise ValueError(msg)

def differences(vertices):
    return {tuple(a-b for a,b in zip(u,v)) for u in vertices for v in vertices}

def event_model(target):
    count=0; good=0; sets=set()
    for word in it.permutations(tuple((j,s) for j in range(3) for s in (-1,1))):
        q=[0,0,0]; vertices=[tuple(q)]
        for j,s in word:
            q[j]+=s; vertices.append(tuple(q))
        need(q==[0,0,0],'source restoration')
        ds=differences(vertices); good+=all(row in ds for row in target)
        count+=1;sets.add(tuple(sorted(set(vertices))))
    return count,good,sets

def graph_model(target):
    # Traverse the cube using edge-label counts; retain only reachable state sets.
    # No signed event list, permutation loop, or prefix recurrence is shared.
    frontier={(0,(0,0,0),1)}
    sizes=[len(frontier)]
    for _ in range(6):
        following=set()
        for v,counts,mask in frontier:
            for axis in range(3):
                if counts[axis]==2:continue
                w=v^(1<<axis); c=list(counts);c[axis]+=1
                following.add((w,tuple(c),mask|(1<<w)))
        frontier=following;sizes.append(len(frontier))
    masks={mask for v,c,mask in frontier if v==0 and c==(2,2,2)}
    result=set(); good=0
    for mask in masks:
        for signs in it.product((-1,1),repeat=3):
            vertices=tuple(sorted(tuple(signs[k]*((v>>k)&1) for k in range(3)) for v in range(8) if mask>>v&1))
            result.add(vertices)
            # Check rows via bit-pattern endpoint equations, without differences().
            accepted=True
            for row in target:
                has=False
                for v in range(8):
                    if not (mask>>v&1):continue
                    for w in range(8):
                        if mask>>w&1 and all(signs[k]*(((v>>k)&1)-((w>>k)&1))==row[k] for k in range(3)):
                            has=True
                accepted &= has
            good+=accepted
    return good,result,sizes,len(masks)
