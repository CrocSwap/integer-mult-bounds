# frame-only slot-recycling bound: min chain cover of helper lifetimes (death<birth, deathframe<=birthframe)
import json,gzip,sys
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching
w=json.load(gzip.open(sys.argv[1]))
v,R=w['v'],w['R']
fr=[sum(1<<s for s in f) for f in w['frames']]
gates=[g for g in w['A']]+[None]+[g for g in w['B']]
ks=len(w['A'])
ret=set(w['ret'])
first={};last={};ff={};lf={}
for k,g in enumerate(gates):
    if g is None: continue
    f,d,srcs=g[0],g[1],g[2]
    for r in [d]+list(srcs):
        if r>=2*v:
            if r not in first: first[r]=k; ff[r]=fr[f]
            last[r]=k; lf[r]=fr[f]
# totals: live to the end
for q in ret: last[q]=10**9; lf[q]=(1<<v)-1
hs=sorted(first)
n=len(hs)
rows=[];cols=[]
for i,a in enumerate(hs):
    for j,b in enumerate(hs):
        if last[a]<first[b] and (lf[a]&~ff[b])==0:
            rows.append(i);cols.append(j)
M=csr_matrix((np.ones(len(rows)),(rows,cols)),shape=(n,n))
m=maximum_bipartite_matching(M,perm_type='column')
mm=int((m>=0).sum())
print(sys.argv[1].split('/')[-1],'lifetimes',n,'edges',len(rows),'max matching',mm,'=> frame-only min slots',n-mm)
# liveness peak (time only)
ev=[]
for a in hs:
    ev.append((first[a],1)); ev.append((last[a]+0.5,-1))
ev.sort(); cur=0; pk=0
for t,dl in ev:
    cur+=dl; pk=max(pk,cur)
print('time-only peak live',pk)
