#!/usr/bin/env python3
"""Exact boundary-contract controls; no native-word or new-bound claim.
Yiyang (@Lyy-iiis), with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import json
from pathlib import Path


def zero(n, m=None):
    return [[Q(0) for _ in range(n if m is None else m)] for _ in range(n)]


def eye(n):
    a=zero(n)
    for k in range(n): a[k][k]=Q(1)
    return a


def add(a,b): return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(a,c): return [[c*x for x in r] for r in a]
def mul(a,b): return [[sum((a[i][k]*b[k][j] for k in range(len(b))),Q(0)) for j in range(len(b[0]))] for i in range(len(a))]

def block(a,b,c,d):
    return [r+s for r,s in zip(a,b)]+[r+s for r,s in zip(c,d)]


def inverse(a):
    n=len(a); b=[list(r)+s for r,s in zip(a,eye(n))]
    for j in range(n):
        p=next((p for p in range(j,n) if b[p][j]),None)
        if p is None: raise RuntimeError('singular fixture')
        b[j],b[p]=b[p],b[j]
        v=b[j][j]; b[j]=[x/v for x in b[j]]
        for i in range(n):
            if i != j:
                v=b[i][j]; b[i]=[x-v*y for x,y in zip(b[i],b[j])]
    return [r[n:] for r in b]


def require(cond,msg):
    if not cond: raise RuntimeError(msg)


def check_lanes(n):
    I=eye(n); Z=zero(n); S=zero(n); R=zero(n)
    for j in range(n-1): S[j+1][j]=R[j][j+1]=Q(1)
    U=block(I,scale(I,-1),Z,I)
    L=block(I,Z,S,I)
    B=block(I,scale(I,-1),I,Z)
    K=block(Z,I,I,Z)
    F=mul(U,L)
    F_inv=inverse(F)  # oracle: no inverse formula or symbolic factor reversal
    require(mul(F,F_inv)==eye(2*n) and mul(F_inv,F)==eye(2*n),'actual inverse mismatch')
    core=mul(mul(mul(mul(F,K),F_inv),K),B)
    ideal=block(scale(I,-1),Z,scale(I,2),scale(I,-1))
    require(mul(mul(mul(mul(U,K),inverse(U)),K),B)==ideal,'exact ideal control')
    ur=[r[n:] for r in core[:n]]
    require(ur==add(scale(S,2),scale(mul(S,S),-1)),'upper-right formula')
    transported=mul(mul(block(I,Z,Z,S),core),block(I,Z,Z,R))
    actual_ur=[r[n:] for r in transported[:n]]
    expected_ur=mul(add(scale(S,2),scale(mul(S,S),-1)),R)
    require(actual_ur==expected_ur,'transported upper-right')
    require([actual_ur[i][i] for i in range(n)]==[Q(0)]+[Q(2)]*(n-1),'constant-grade leakage')
    # A repair to the Y <- Y boundary block cannot change this X <- Y block.
    repair=block(Z,Z,Z,scale(mul(I,[[Q(int(i==0 and j==0)) for j in range(n)] for i in range(n)]),-1))
    require([r[n:] for r in add(transported,repair)[:n]]==actual_ur,'boundary repair wrongly alters upper-right')
    # Same-size output-side perturbation is a discriminating benign control.
    left=mul(L,U)
    leftcore=mul(mul(mul(mul(left,K),inverse(left)),K),B)
    require([r[n:] for r in leftcore[:n]]==Z,'output-side control should have no pole')
    return {'lanes':n,'independent_columns':2*n,'actual_inverse_both_orders':True,
            'upper_right_diagonal':[int(actual_ur[i][i]) for i in range(n)],
            'output_side_control_upper_right_zero':True}


def stock():
    H={4:28,7:7,8:47,9:326}
    P={1:4656,2:920,3:1386}
    T={k:2*v for k,v in H.items()}; T[17]=112
    target=sum(k*v for k,v in T.items()); paid=sum(k*v for k,v in P.items())
    require(target==8846 and paid==10654,'stock mass')
    require(min(T)==4 and max(P)==3 and target<paid,'separated-stock inequality premises')
    return {'exact_outputs_after_boundary_pass_through_subtraction':T,'paid':P,
            'target_rank_mass':target,'paid_rank_mass':paid,
            'ratio_at_t_one':str(Q(target,paid)),
            'all_0_lt_t_le_1_ratio_bound':'(4/3)^(t-1)*4423/5327 < 1',
            'scope':'uniform exact-minimal-lane provisioning only'}


def main():
    result={'schema':'boundary-contract-controls/v1','no_new_kappa':True,
            'native_word_replayed':False,'leakage_cases':[check_lanes(n) for n in range(2,9)],
            'exact_stock':stock()}
    print(json.dumps(result,indent=2,sort_keys=True))
    return result

if __name__=='__main__': main()
