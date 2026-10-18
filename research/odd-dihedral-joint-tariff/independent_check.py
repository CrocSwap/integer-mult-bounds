#!/usr/bin/env python3
"""Separate Codex exact-verification specialist check; Apache-2.0.

No package imports. Original independent script SHA256:
5ebb07e7b470229874676ae57917b3c22ba8164da3bf0bc91e8621c99fedf206.
Parent added this header, optimized-mode refusal and expected receipt comparison.
Finite corroboration only; the universal proof is PROOF.md.
"""
if not __debug__:
    raise RuntimeError("independent checker requires assertions; do not use -O")

from collections import Counter
from itertools import product
import hashlib,json

# Independent plain-set address action. No import of package functions.
# A word tuple gives displayed factors; evaluation acts rightmost first.
def action(word,a,e,n):
    for letter in reversed(word):
        a = (-a - (letter=='y')) % n
        e = 1-e
    return a,e

def normal_action(k,s,a,e,n):
    return (k + (-a if s else a)) % n, e^s

def rank(rows):
    work=list(rows); result=0
    while any(work):
        p=max(work); bit=p.bit_length()-1
        work=[q^p if q>>bit&1 else q for q in work]
        result+=1
    return result

def times(A,B):
    return tuple(_xor(B[j] for j in range(len(B)) if a>>j&1) for a in A)
def _xor(xs):
    out=0
    for x in xs:out^=x
    return out

def eye(d): return tuple(1<<i for i in range(d))
def lift(S,L):
    return tuple(sum(1<<(j*L+a) for j in range(len(S)) if S[i]>>j&1)
                 for i in range(len(S)) for a in range(L))
def gate(n,letter,u,v):
    L=2*n; rows=list(eye(2*L))
    for out_role in range(2):
        if not u>>out_role&1:continue
        for a,e in product(range(n),range(2)):
            b,f=action((letter,),a,e,n)
            for in_role in range(2):
                if v>>in_role&1:
                    rows[out_role*L+2*a+e]^=(1<<(in_role*L+2*a+e))^(1<<(in_role*L+2*b+f))
    return tuple(rows)
def cross(rows,H,L):
    # Proof convention: outputs K, inputs H.
    mask=sum(1<<(i*L+a) for i in range(2) for a in H)
    return rank(rows[i*L+a]&mask for i in range(2) for a in range(L) if a not in H)
counts=Counter(); digest=hashlib.sha256()
for n in range(3,102,2):
    m=n//2
    H={(a%n,0) for a in range(-m,1)}|{(b,1) for b in range(m)}
    assert len(H)==n
    # BFS generated directly from action on identity; records all count-Pareto points
    # up to maximum shortest length n, independent of closed-form target words.
    states={(0,0):{(0,0)}}
    frontier={(0,0,0,0)}
    for depth in range(n):
        nxt=set()
        for k,e,nx,ny in frontier:
            for letter in ('x','y'):
                h,f=action((letter,),k,e,n)
                pair=(nx+(letter=='x'),ny+(letter=='y'))
                old=states.get((h,f),set())
                if any(x<=pair[0] and y<=pair[1] for x,y in old):continue
                old={p for p in old if not(pair[0]<=p[0] and pair[1]<=p[1])}
                old.add(pair); states[h,f]=old
                nxt.add((h,f,*pair))
        frontier=nxt
    for k,e in product(range(n),range(2)):
        distance=lambda z:min(z%n,n-z%n)
        A=distance(k+e);B=distance(k);t=int(e==1 and k==m)
        target={(normal_action(k,e,a,f,n)) for a,f in H}
        q=len(target-H)
        assert q==A+B+t
        predicted={(A+j,B+t-j) for j in range(t+1)}
        assert states[k,e]==predicted,(n,k,e,states[k,e],predicted)
        for c,want in ((m,A),(m-1,B)):
            I=set(range(m)); image={(k+(c-a if e else a))%n for a in I}
            assert len(image-I)==want
        digest.update(json.dumps((n,k,e,q,sorted(states[k,e]))).encode())
        counts['single_targets_odd_3_through_101']+=1
    counts['periods']+=1
# Exhaust every two-role free invertible scalar map, every projector, and both letters.
GL=[(a,b) for a,b in product(range(4),repeat=2) if rank((a,b))==2]
projectors=[(u,v) for u,v in product(range(1,4),repeat=2) if (u&v).bit_count()%2]
for n in (3,5,7):
    m=n//2;L=2*n;H={2*(a%n) for a in range(-m,1)}|{2*b+1 for b in range(m)}
    for S in GL:
        Sinv=next(T for T in GL if times(S,T)==eye(2))
        s,si=lift(S,L),lift(Sinv,L)
        assert cross(s,H,L)==cross(si,H,L)==0
        for u,v in projectors:
            # outer(u,v) gives N; conjugation independently as binary row matrices
            N=tuple(v if u>>i&1 else 0 for i in range(2))
            C=times(times(S,N),Sinv)
            up,vp=next((a,b) for a,b in projectors if tuple(b if a>>i&1 else 0 for i in range(2))==C)
            for letter in ('x','y'):
                original=gate(n,letter,u,v)
                conj=times(times(s,original),si)
                assert conj==gate(n,letter,up,vp)
                assert cross(conj,H,L)==1
                counts['all_GL2_projector_conjugations']+=1
result = {'counts':dict(counts),'sha256':digest.hexdigest(),'status':'PASS_INDEPENDENT_ODD_DIHEDRAL_REVIEW'}
expected = {'counts':{'all_GL2_projector_conjugations':216, 'periods':50, 'single_targets_odd_3_through_101':5200}, 'sha256':'52e3d7c91a93c51fe5e115ebfcdd7e2730308fafb83bc9a8e14739128d0b2724', 'status':'PASS_INDEPENDENT_ODD_DIHEDRAL_REVIEW'}
if result != expected:
    raise ValueError('independent mathematical receipt mismatch')
print(json.dumps(result,sort_keys=True))
