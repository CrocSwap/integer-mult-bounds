from load import *
from collections import defaultdict, Counter
N=n+W['owned_fields']
cur=list(W['initial'])+[None]*W['owned_fields']
stays=defaultdict(list)   # reg -> list of dict(f, i0, i1, ins:[], outs:[])
for r in range(n): stays[r].append(dict(f=cur[r],i0=-1,i1=None,ins=[],outs=[],scale=0))
for i,e in enumerate(P):
    op,r=e[0],e[1]
    if op=='INIT':
        cur[r]=e[2]; stays[r].append(dict(f=e[2],i0=i,i1=None,ins=[],outs=[],scale=0,init=True))
    elif op=='CLEAR':
        stays[r][-1]['i1']=i; stays[r][-1]['clear']=True; cur[r]=None
    elif op=='MOVE':
        stays[r][-1]['i1']=i; cur[r]=e[3]; stays[r].append(dict(f=e[3],i0=i,i1=None,ins=[],outs=[],scale=0))
    elif op=='SCALE':
        stays[r][-1]['scale']+=1
    else:
        s=e[2]
        stays[r][-1]['ins'].append((i,s,len(stays[s])-1))
        stays[s][-1]['outs'].append((i,r,len(stays[r])-1))
