# CONTROLS: rebuild #7620's realised instances on #7617 (best7616) with our engine; (r,X,p,side) read from #7620 as data.
import sys, time, collections, pickle
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import lb, tpl, check
import pricekit as pk
DATA=os.path.join(HERE,'data')
B=pk.load(DATA+'/word-7617.json.gz'); D=pk.load(DATA+'/word-7620.json.gz')
n=B['public']; dim=[len(b) for b in B['frames']]
def paths(W):
    p={r:[W['initial'][r]] for r in range(n)}
    for e in W['program']:
        if e[0]=='MOVE' and e[1]<n: p[e[1]].append(e[3])
    return p
pa,pd=paths(B),paths(D)
pairs=lambda L:set(zip(L,L[1:]))
inst=[]
for r in range(n):
    for k,X in enumerate(pa[r][1:-1],1):
        if X in pd[r]: continue
        A,Bc=pa[r][k-1],pa[r][k+1]
        ps=[]
        for q in range(n):
            if q==r: continue
            new=pairs(pd[q])-pairs(pa[q])
            if (X,Bc) in new: ps.append((q,'B'))
            if (A,X) in new: ps.append((q,'A'))
        inst.append((r,X,ps))
only=sys.argv[1:] 
Wd=lb.Word(B)
def gainP(W0,W1):
    a=pk.native_from_word(W0)['P']; b=pk.native_from_word(W1)['P']; d=b.copy(); d.subtract(a); return {k:v for k,v in d.items() if v}
res=collections.Counter(); t0=time.time()
for r,X,ps in inst:
    if only and '%d@%d'%(r,X) not in only: continue
    if not ps: print(r,X,'no partner in data'); res['no partner']+=1; continue
    done=False
    for p,side in ps:
        out,msg=tpl.try_instance(Wd,r,X,p,side)
        if out is None: print('%d@%d p=%d %s FAIL %s'%(r,X,p,side,msg)); continue
        W2,cd,sol=out; c=check.full(B,W2)
        print('%d@%d p=%d %s c=%d sol=%s dP=%s %s [%.0fs]'%(r,X,p,side,cd.meta['c'],{k:str(v) for k,v in sol.items()},gainP(B,W2),c,time.time()-t0),flush=True)
        if c['rows_ok'] and c['base_lifetimes_kept']: done=True; break
    res['rebuilt' if done else 'fail']+=1
print(dict(res))
