"""Rohan Arun's PR31 independent exact audit (research/two-stage-corners/independent.py),
parametrized by the factor dimensions; the checks themselves are unchanged."""
from pathlib import Path
from fractions import Fraction as Q
from math import gcd
import json

def rank(matrix):
    a=[r[:] for r in matrix];rr=0
    for j in range(len(a[0]) if a else 0):
        z=next((i for i in range(rr,len(a)) if a[i][j]),None)
        if z is None:continue
        a[rr],a[z]=a[z],a[rr];pivot=a[rr][j]
        for i in range(rr+1,len(a)):
            q=a[i][j]
            if not q:continue
            a[i]=[pivot*x-q*y for x,y in zip(a[i],a[rr])]
            d=0
            for x in a[i]:d=gcd(d,abs(x))
            if d>1:a[i]=[x//d for x in a[i]]
        rr+=1
        if rr==len(a):break
    return rr

def run(c,expected_runs):
    a,b=c['dimensions'];m=a*b;d=a+b-1
    assert a==b+2 and c['m']==m and c['d']==d
    R=(list(range(a))+list(range(1,a))+[0])[:d];C=([a-1]+list(range(a-1))+list(range(a)))[-d:]
    assert R==c['R'] and C==c['C'] and c['gamma_offset']==(m-d)%b
    pivots=[(r,col) for r,col,v in c['witness']['pivots']];zeros={(z['row'],z['col']):z for z in c['zero_minor_certificates']};checked=0
    for i,pivot in pivots:
        assert i==len([r for r,_ in pivots if r<i])
        prior=[col for r,col in pivots if r<i]
        for j in range(pivot+1,d):
            if j in prior:continue
            z=zeros.pop((i,j));mask=z['partition'];cols=[v for v in range(a+b+1) if mask>>v&1];dual=[v for v in range(a+b+1) if not mask>>v&1]
            assert 0<=mask<(1<<(a+b+1))
            left=[[int(v==R[r] or v==a+r%b or v==a+b) for v in cols] for r in range(i+1)]
            right=[[int(v==C[col] or v==a+(m-d+col)%b or v==a+b) for v in dual] for col in prior+[j]]
            l,r=rank(left),rank(right);assert (l,r)==(z['row_rank'],z['column_rank']) and l+r<i+1==z['size'];checked+=1
    assert not zeros
    x=list(map(Q,c['witness']['left_weights']));y=list(map(Q,c['witness']['right_weights']));assert sum(x)==sum(y)==1 and all(x+y)
    mat=[[int(R[i]==C[j])/x[R[i]]+int(i%b==(m-d+j)%b)/y[i%b]-1 for j in range(d)] for i in range(d)]
    active=set(range(d));actual=[]
    for i,pivot in pivots:
        j=max(z for z in active if mat[i][z]);assert j==pivot;active.remove(j);v=mat[i][j];actual.append([i,j,str(v)])
        for r in range(i+1,d):
            q=mat[r][j]/v
            if q:mat[r]=[u-q*v for u,v in zip(mat[r],mat[i])]
    assert [list(p) for p in actual]==[list(p) for p in c['witness']['pivots']]
    runs=[]
    for r,col in pivots:
        if runs and (r,col)==(runs[-1][-1][0]+1,runs[-1][-1][1]+1):runs[-1].append((r,col))
        else:runs.append([(r,col)])
    assert [len(r) for r in runs]==expected_runs
    big=[len(r) for r in runs if len(r)>1]
    assert checked==sum(w*(w-1)//2 for w in big)
    blocks=[dict(rows=[r[0][0],r[-1][0]],columns=[m-d+r[0][1],m-d+r[-1][1]],width=len(r)) for r in runs if len(r)>1]
    # Physical contiguity: runs occupy disjoint index ranges, disjoint from the middle block d..m-d-1.
    for blk in blocks:assert blk['rows'][1]<d and blk['columns'][0]>=m-d
    return dict(status='PASS independent exact identity audit',dims=[a,b],zero_certificates=checked,integer_ranks=2*checked,
        rational_pivots=len(actual),runs=[len(r) for r in runs],blocks=blocks,middle=[d,m-d-1],
        profile=dict(singletons=sum(len(r)==1 for r in runs),blocks=big+[m-2*d],rank=m-d))
