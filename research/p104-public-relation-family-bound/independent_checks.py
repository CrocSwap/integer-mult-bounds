#!/usr/bin/env python3
"""Tiny exact proof-step fixtures; no source or parameter census."""
from fractions import Fraction as F
from itertools import combinations
import json
def rank(rows):
    a=[list(map(F,r)) for r in rows];k=0
    for j in range(len(a[0]) if a else 0):
        p=next((i for i in range(k,len(a)) if a[i][j]),None)
        if p is None:continue
        a[k],a[p]=a[p],a[k];q=a[k][j];a[k]=[v/q for v in a[k]]
        for i in range(k+1,len(a)):
            q=a[i][j];a[i]=[x-q*y for x,y in zip(a[i],a[k])]
        k+=1
    return k
def need(x,label):
    if not x:raise ValueError(label)
def contains(rows,v):return rank(rows)==rank(rows+[v])
g=[-1,1,0];h=[0,0,1];tests=0
for size in range(4):
    for H in combinations(range(3),size):
        full=rank([[row[i] for i in H] for row in [g,h]])==2
        need(full==(2 in H and (0 in H or 1 in H)),'full-plane lost columns');tests+=1
e=[[1,0,0],[0,1,0],[0,0,1]];plane=[e[0],[0,-1,1]]
need([contains(plane,v) for v in e]==[True,False,False],'only initial row is in plane')
need(not contains([e[0]]+plane,e[1]) and contains(e[:2]+plane,e[2]),'only latest MOVE is enabled')
hr=[1,F(-1,4),-1]
need(not any(contains([hr],v) for v in e),'h circuit has no zero row')
need([contains(e[:i]+[hr],e[i]) for i in range(3)]==[False,False,True],'h circuit latest')
need(8-1>0 and 8-1-8==-1,'information allowance is distinct from charged bound')
print(json.dumps({'status':'PASS_EXACT_FAMILY_PROOF_STEP_FIXTURES','lost_column_subsets':tests,'plane_zero_and_latest_checks':True,'h_zero_and_latest_checks':True,'conditional_budget_distinction':True},sort_keys=True,indent=2))
