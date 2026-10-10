"""Retained independently authored IR routines. Upstream production code is never executed. Apache-2.0. Prepared with substantial OpenAI assistance."""
import numpy as np

def stage_template(stage,records,frames):
    rev=stage in (1,3);out=[]
    for index in (range(len(records)-1,-1,-1) if rev else range(len(records))):
        row=records[index];op,a,b,c,f,*extra=row;z=extra[0] if extra else 0
        if op==0:out.append([0,a,c if rev else b,b if rev else c,f,0,stage,int(rev),index])
        elif op==1:out.append([1,a,b,-c if rev else c,f,z,stage,int(rev),index])
        elif op==(3 if rev else 2):
            out.append([2,b,a,0,c,0,stage,int(rev),index])
            out.append([0,b,c,f,frames[str(c)]['rank'],0,stage,int(rev),index])
        else:
            assert op==(2 if rev else 3)
            out.append([3,b,-1,0,f,0,stage,int(rev),index])
    return np.asarray(out,dtype='<i4')

def permutation(stage,start,width):
    original=list(range(stage*20,stage*20+width)); target=list(range(start,start+width))
    a=original+[x for x in range(100) if x not in original]
    b=target+[x for x in range(100) if x not in target]
    d=dict(zip(a,b));return [d[x] for x in range(100)]

def factor_perm(pi):
    work=list(range(100)); out=[]
    for i,x in enumerate(pi):
        if work[i]!=x:
            j=work.index(x);work[i],work[j]=work[j],work[i];out.append([i,j])
    assert work==pi
    return out

def emit_boundary(x):
    t=x['replica']; kind=x['kind']
    def f(bank,port):return (4*t+bank)*960+port
    if kind=='idle':
        groups={0:((2,38,0),(3,38,1)),1:((2,19,2),(3,19,3)),2:((0,42,4),(1,42,5),(2,4,6),(3,4,7))}[x['which']]
        for bank,rank,projector in groups:
            for port in range(960):yield [4,f(bank,port),-1,0,rank,projector,port]
    elif kind=='bridge':
        groups={0:((0,2,1),(3,1,-1)),1:((3,1,1),(0,2,-1)),2:((1,3,-1),(2,0,1))}[x['which']]
        for a,b,c in groups:
            for port in range(960):yield [5,f(a,port),f(b,port),c,0,x['which'],port]
    else:
        assert kind=='terminal_exchange'
        for a,b in ((0,1),(2,3)):
            for port in range(960):yield [7,f(a,port),f(b,port),-1,0,0,port]
