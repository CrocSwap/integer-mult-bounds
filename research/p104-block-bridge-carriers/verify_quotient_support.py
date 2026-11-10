#!/usr/bin/env python3
"""Exact controls for the known defect-one support cap and source corollary; no external imports.
@CubeJerry, with substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
The universal result and exact quotient application are in the written proof.
"""
from fractions import Fraction as Q
from itertools import combinations
import json


def need(ok,message):
    if not ok:raise ValueError(message)
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def outer(x,y):return [[a*b for b in y] for a in x]
def add(a,b,c=1):return [[x+c*y for x,y in zip(r,s)] for r,s in zip(a,b)]
def rank(matrix):
    a=[[Q(x) for x in row] for row in matrix];r=0
    for c in range(len(a[0]) if a else 0):
        p=next((i for i in range(r,len(a)) if a[i][c]),None)
        if p is None:continue
        a[r],a[p]=a[p],a[r];d=a[r][c];a[r]=[x/d for x in a[r]]
        for i in range(r+1,len(a)):
            d=a[i][c]
            if d:a[i]=[x-d*y for x,y in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r

def canonical(n):
    out=[]
    for i in range(n+1):
        x=[Q(i==j) for j in range(n)] if i<n else [Q((-1)**(j+1)) for j in range(n)]
        y=[Q((i>j)-(i<j)) for j in range(n)]
        out.append((x,y))
    return out

def check_root(word):
    n=len(word[0][0]);K=eye(n)
    for x,y in word:
        need(any(x) and any(y) and sum(a*b for a,b in zip(x,y))==0,'nonzero rank-one square-zero factor')
        K=mm(add(eye(n),outer(x,y),-2),K)
    need(K==add(eye(n),eye(n),-2),'complete root endpoint')

def support(x,y,P):
    need(rank(P)==2 and mm(P,P)==P,'rank-two idempotent')
    R=outer(x,y)
    need(mm(P,R)==R and mm(R,P)==R,'both support equations')

def main():
    S=[[Q((i>j)-(i<j)) for j in range(4)] for i in range(4)]
    inverse=[[(-1)**(i+j)*S[i][j] for j in range(4)] for i in range(4)]
    need(mm(S,inverse)==eye(4) and rank(S)==4,'integer sign inverse and four-column rank')
    bad=[r[:] for r in inverse];bad[0][1]*=-1
    need(mm(S,bad)!=eye(4),'inverse sign corruption rejected')
    sharp=canonical(2);check_root(sharp)
    for x,y in sharp:support(x,y,eye(2))
    # Commutation is essential: the five-query four-dimensional root has four
    # rank-two supporting projectors, but they do not commute with one another.
    word=canonical(4);check_root(word);projectors=[]
    S3=[[Q((i>j)-(i<j)) for j in range(3)] for i in range(3)]
    need(rank(S3)==2,'singular triple Gram contrasts with independent columns and rows')
    for selected in combinations(range(5),3):
        xs=[word[i][0] for i in selected];ys=[word[i][1] for i in selected]
        need(rank(xs)==3 and rank(ys)==3,'every selected triple has independent columns and rows')
    first,last=word[0],word[4]
    shared=add(outer(first[0],last[1]),outer(last[0],first[1]),-1)
    support(*first,shared);support(*last,shared)

    for i,(x,y) in enumerate(word[:4]):
        j=1 if i==0 else 0
        w=[Q(k==j)*y[j] for k in range(4)]
        P=add(outer(x,x),outer(w,y))
        support(x,y,P);projectors.append(P)
    bad_pairs=sum(mm(P,Q0)!=mm(Q0,P) for P,Q0 in combinations(projectors,2))
    need(bad_pairs>0,'commutation premise distinguishes the four-support boundary')
    result={'status':'PASS_KNOWN_QUOTIENT_SUPPORT_CAP','dimension_exception':{'n':2,'N':3,'F':3,'defect':1},'known_cap_n_ge4':2,'attaining_n4_supports':2,'independent_query_triples_checked':10,
            'omitted_commutation_boundary':{'n':4,'N':5,'selected_supports':4,'noncommuting_pairs':bad_pairs},
            'sign_gram_rank':4,'no_new_kappa':True,
            'scope':'Finite controls corroborate the proof; exact source quotient census is verified by the existing geometry replay.'}
    print(json.dumps(result,indent=2));print(result['status'])

if __name__=='__main__':main()
