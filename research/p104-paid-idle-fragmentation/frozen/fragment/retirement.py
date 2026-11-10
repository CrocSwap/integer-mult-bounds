"""Literal independent body-bearing retirement, followed by retained D retirement."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
def ordinary_inverse(events):
    out=deepcopy(list(reversed(events)))
    for e in out:
        if e[0]=='ADD': e[-1]=str(-Q(e[-1]))
        elif e[0]=='SCALE': e[-1]=str(1/Q(e[-1]))
        elif e[0]=='LAMBDA': e[-1]=-e[-1]
        elif e[0]!='SWAP': raise ValueError('ordinary inverse opcode')
    return out

def matrix_events(rows,labels):
    a=[[Q(x)for x in row]for row in rows];n=len(labels);ops=[]
    def unit(q):return q and abs(q.numerator)&(abs(q.numerator)-1)==0 and q.denominator&(q.denominator-1)==0
    for j in range(n):
        while True:
            k=next(k for k in range(j,n)if a[k][j])
            if k!=j:a[j],a[k]=a[k],a[j];ops.append(['SWAP',labels[j],labels[k]])
            k=next((k for k in range(j+1,n)if a[k][j]),None)
            if k is None:break
            q=a[k][j]//a[j][j]
            if q:a[k]=[x-q*y for x,y in zip(a[k],a[j])];ops.append(['ADD',labels[k],labels[j],str(-q)])
            if a[k][j]:a[j],a[k]=a[k],a[j];ops.append(['SWAP',labels[j],labels[k]])
        assert unit(a[j][j]),'dyadic unit determinant'
        q=1/a[j][j]
        if q!=1:a[j]=[q*x for x in a[j]];ops.append(['SCALE',labels[j],str(q)])
        for k in range(j):
            if a[k][j]:
                q=-a[k][j];a[k]=[x+q*y for x,y in zip(a[k],a[j])];ops.append(['ADD',labels[k],labels[j],str(q)])
    assert a==[[Q(i==j)for j in range(n)]for i in range(n)]
    return ordinary_inverse(ops)

SLOTS={'ADD':(1,2),'SWAP':(1,2),'SCALE':(1,),'LAMBDA':(1,),'Q_POWER':(1,),'QUERY':(1,2),'LOCAL':(2,3),'IDLE':(1,2),'IDLE_ONE':(1,)}
def retire_body(w):
    w=deepcopy(w);pivot=6;fresh=w['roles']
    E=matrix_events([['-1/8','-2'],['45/16','37']],[6,7])
    A=[['ADD',0,2,'1/16'],['ADD',2,1,'-16'],['SWAP',2,6]]
    cut=w['events'].index(['IDLE_ONE',2,[5,6]])
    assert cut==122 and w['diagonal'][6]==w['diagonal'][7]
    def rename(e):
        e=deepcopy(e)
        for j in SLOTS[e[0]]:
            if e[j]==pivot:e[j]=fresh
        return e
    ev=E+w['events'][:cut+1]+A;handoff=len(ev)-1
    ev +=[rename(e)for e in ordinary_inverse(A)+w['events'][cut+1:]+ordinary_inverse(E)]
    old=w['diagonal'][pivot];prefix=[0]*(w['stages']+2);prefix[6]=prefix[7]=1
    suffix=[x-y for x,y in zip(old,prefix)]
    w['events']=ev;w['roles']+=1;w['diagonal'][pivot]=prefix;w['diagonal'].append(suffix)
    w['schema']='one-fragment-body-retirement/1'
    witness={'cut_after':cut,'handoff_after':handoff,'pivot':pivot,'fresh':fresh,'prefix_basis':E,'cut_basis':A,'prefix_target':prefix,'suffix_target':suffix}
    return w,witness


def retire_d(w):
    w=deepcopy(w);pivot=4;fresh=w['roles'];group=[4,20,21]
    G=[['SCALE',4,'-1'],['ADD',21,4,'1'],['ADD',4,20,'1']]
    J=[['SWAP',4,21],['ADD',4,1,'1'],['ADD',4,20,'-1'],['ADD',0,4,'2'],['ADD',2,4,'-2'],['ADD',20,4,'2']]
    cut=w['events'].index(['QUERY',20,21,-1])+1
    assert cut==374 and w['events'][cut]==['LAMBDA',20,1]
    assert len({tuple(w['diagonal'][r][1:])for r in group})==1
    normalized=w['events']+[['LAMBDA',r,1]for r in group]
    def rename(e):
        e=deepcopy(e)
        for j in SLOTS[e[0]]:
            if e[j]==pivot:e[j]=fresh
        return e
    ev=ordinary_inverse(G)+normalized[:cut+1]+J;handoff=len(ev)-1
    ev +=[rename(e)for e in ordinary_inverse(J)+normalized[cut+1:]+G]
    ev +=[['LAMBDA',r,-1]for r in group]
    old=deepcopy(w['diagonal'][pivot]);w['events']=ev;w['roles']+=1
    w['diagonal'][pivot]=[-1]+[0]*(w['stages']+1);w['diagonal'].append([0,*old[1:]])
    w['schema']='two-retirements-one-paid-fragment/1'
    return w,{'cut_after':cut,'handoff_after':handoff,'pivot':pivot,'fresh':fresh,'group':group,'boundary':G,'middle':J,
              'a':{'1':'1','20':'-1','21':'1'},'b':{'0':'-2','2':'2','20':'-2','21':'-1'},'c':{'20':'1','4':'-1'},'d':{'4':'-1','21':'-1'}}

def construct(base):
    body,a=retire_body(base);word,b=retire_d(body);return body,word,[a,b]
