# global g(6), g(5): validate gT.rref_spaces (count = Gaussian binomial, all distinct, all full dim), own masks
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', '..', 'data', 'data.json'))
WORK = os.environ.get('BX_WORK', '.')
import sys, json, numpy as np, itertools
sys.path.insert(0,os.path.join(HERE,'..','rb'))
from gT import rref_spaces   # only the enumerator is reused, validated here
D=json.load(open(DATA)); LAB=[int(x) for x in D['LAB']]
lab=np.array(LAB,dtype=np.int64)
par=np.array([bin(i).count('1')&1 for i in range(512)])
Z=(par[np.bitwise_and.outer(np.arange(512),lab)]==0)   # 512 x 112 bool: phi(label)=0
def gauss(n,k):
    num=den=1
    for i in range(k): num*=(2**(n-i)-1); den*=(2**(i+1)-1)
    return num//den
for c in (3,4):
    S=np.array(rref_spaces(c),dtype=np.int64)
    # spans
    combos=[m for m in range(1,1<<c)]
    span=np.zeros((len(S),len(combos)),dtype=np.int64)
    for j,m in enumerate(combos):
        v=np.zeros(len(S),dtype=np.int64)
        for i in range(c):
            if m>>i&1: v^=S[:,i]
        span[:,j]=v
    span.sort(axis=1)
    fulldim=bool((span[:,0]>0).all()) and bool((np.diff(span,axis=1)>0).all())
    nd=len(np.unique(span,axis=0))
    best=0
    for a in range(0,len(S),200000):
        blk=S[a:a+200000]; M=Z[blk[:,0]].copy()
        for i in range(1,c): M&=Z[blk[:,i]]
        best=max(best,int(M.sum(axis=1).max()))
    print('codim',c,'count',len(S),'gauss',gauss(9,c),'distinct',nd,'fulldim',fulldim,'g(%d)='%(9-c),best,flush=True)
