import sys
sys.argv=[sys.argv[0]]
exec(open('cluster2.py').read().split("names=list(ops)")[0])
import time,os
TL=float(os.environ.get("TL","100"))
import os
VA=os.environ.get('VA','pre');VB=os.environ.get('VB','pre')
if VA=='post':
    for k in ('a3','a1'): del ops[k]
    ops['a2']=(591,283); pre.append(('W1','a2')); pre.append(('a2','W3'))
if VB=='post':
    for k in ('b9','b7'): del ops[k]
    ops['b2']=(591,299); pre.append(('W2','b2')); pre.append(('b2','W3'))
pre[:]=[(a,b) for a,b in pre if a in ops and b in ops]
names=list(ops)
chk=[(124,12),(125,13),(148,36),(149,37),(591,58),(591,63)]
DROP=os.environ.get('DROP')
if DROP: chk=[c for c in chk if c[0]!=int(DROP)]
sys.setrecursionlimit(10000)
seen=set();t0=time.time();found=[];deepest=[0,None]
def ok(cur): return all(inperp(cur[r],t,P) for r,t in chk)
def dfs(rem,cur,path):
    if time.time()-t0>TL: return True
    if not rem: found.append(list(path));return True
    key=(rem,tuple(cur[r] for r in regs))
    key=hash(key)
    if key in seen: return False
    seen.add(key)
    if len(path)>deepest[0]: deepest[0]=len(path);deepest[1]=list(path)
    for n in sorted(rem):
        if any(b==n and a in rem for a,b in pre): continue
        t,s=ops[n];F=G.basis(list(cur[t])+list(cur[s]))
        c2=dict(cur);c2[t]=c2[s]=F
        if not ok(c2): continue
        if dfs(rem-{n},c2,path+[n]): return True
    return False
dfs(frozenset(names),dict(cur0),[])
print('found',found[:1],'deepest',deepest,'seen',len(seen),'time',time.time()-t0)
