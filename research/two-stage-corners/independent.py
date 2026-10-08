"""Independent exact audit of PR29 two-stage contiguous data corners."""
from pathlib import Path
from fractions import Fraction as Q
from math import gcd
import json,importlib.util
HERE=Path(__file__).resolve().parent;SOURCE=HERE

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

def run(data=None):
    c=json.loads((SOURCE/'a5-residual-two-stage.json').read_text()) if data is None else data;a,b=c['dimensions'];m=a*b;d=a+b-1
    assert (a,b,m,d)==(55,53,2915,107)
    R=(list(range(a))+list(range(1,a))+[0])[:d];C=([a-1]+list(range(a-1))+list(range(a)))[-d:]
    assert R==c['R'] and C==c['C'] and c['gamma_offset']==(m-d)%b==52
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
    assert not zeros and checked==2265
    x=list(map(Q,c['witness']['left_weights']));y=list(map(Q,c['witness']['right_weights']));assert sum(x)==sum(y)==1 and all(x+y)
    mat=[[int(R[i]==C[j])/x[R[i]]+int(i%b==(m-d+j)%b)/y[i%b]-1 for j in range(d)] for i in range(d)]
    active=set(range(d));actual=[]
    for i,pivot in pivots:
        j=max(z for z in active if mat[i][z]);assert j==pivot;active.remove(j);v=mat[i][j];actual.append([i,j,str(v)])
        for r in range(i+1,d):
            q=mat[r][j]/v
            if q:mat[r]=[u-q*v for u,v in zip(mat[r],mat[i])]
    assert actual==c['witness']['pivots']
    runs=[]
    for r,col in pivots:
        if runs and (r,col)==(runs[-1][-1][0]+1,runs[-1][-1][1]+1):runs[-1].append((r,col))
        else:runs.append([(r,col)])
    assert [len(r) for r in runs]==[1,51,1,1,1,1,1,1,45,1,1,1,1]
    return dict(status='PASS independent two-stage exact identity audit',zero_certificates=checked,integer_ranks=2*checked,rational_pivots=len(actual),runs=[len(r) for r in runs],blocks=[dict(rows=[r[0][0],r[-1][0]],columns=[m-d+r[0][1],m-d+r[-1][1]],width=len(r)) for r in runs if len(r)>1],middle=[d,m-d-1],profile=dict(singletons=11,blocks=[51,45,2701],rank=m-d))

if __name__=='__main__':
    r=run();(HERE/'two-stage-independent.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
