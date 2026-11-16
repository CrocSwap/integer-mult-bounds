# Greedy loan+snapshot stacking on #7621 over the shape census, gain-ordered, re-censusing after each pass. Own code.
import sys, time, math, json, gzip, collections, pickle, resource
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import lb, tpl, check
import pricekit as pk
import jl
BASE=pk.load(sys.argv[1]); out=sys.argv[2]; maxpass=int(sys.argv[3]) if len(sys.argv)>3 else 6
f=lambda x: x*math.log(x) if x>0 else 0.0
def census(Wd):
    W=Wd.W; dim=Wd.dim; P=W['program']; out=[]
    for r in range(Wd.n):
        S=Wd.seg[r]
        for k in range(1,len(S)-1):
            X=S[k][0]; info=tpl.r_xinfo(Wd,r,X)
            if info is None: continue
            A,B=info[0],info[1]; cl=tpl.classify(Wd,r,info[6])
            if cl is None: continue
            Wr,Rd=cl; g=f(dim[B]-dim[A])-f(dim[X]-dim[A])-f(dim[B]-dim[X])
            srcs={s for _,s,_ in Wr}
            if len(srcs)==1:
                p=next(iter(srcs)); js=Wd.segidx(p,X)
                if len(js)==1 and js[0]+1<len(Wd.seg[p]):
                    C=Wd.seg[p][js[0]+1][0]
                    if Wd.lt(B,C):
                        c=f(dim[C]-dim[X])-f(dim[B]-dim[X])-f(dim[C]-dim[B])
                        if g-c>1e-9: out.append((g-c,r,X,p,'B'))
            if len(Rd)==1:
                p=Rd[0][1]; js=Wd.segidx(p,X)
                if len(js)==1 and js[0]>0:
                    Z=Wd.seg[p][js[0]-1][0]
                    if Wd.lt(Z,A):
                        c=f(dim[X]-dim[Z])-f(dim[A]-dim[Z])-f(dim[X]-dim[A])
                        if g-c>1e-9: out.append((g-c,r,X,p,'A'))
    return sorted(out,reverse=True)
def kap(W): return jl.kappa(W)['kappa']['lo']
W=BASE; Wd=lb.Word(W); k0=kap(W); kc=k0; t0=time.time(); log=[]; landed=0
print('base kappa',k0,flush=True)
for ps in range(maxpass):
    cs=census(Wd); print('pass',ps,'census',len(cs),'sum net %.2f'%sum(x[0] for x in cs),flush=True)
    acc=0; why=collections.Counter()
    for net,r,X,p,side in cs:
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss>3.8e9: print('MEM BAIL'); break
        if tpl.r_xinfo(Wd,r,X) is None: continue   # stale after an earlier hit
        res,msg=tpl.try_instance(Wd,r,X,p,side,maxc=8)
        if res is None: why[str(sorted(msg)) if isinstance(msg,dict) else msg]+=1; continue
        W2,cd,sol=res; c=check.full(W,W2)
        if not (c['rows_ok'] and c['base_lifetimes_kept'] and c['peak']<=50): why['check']+=1; continue
        k2=kap(W2)
        if not k2>kc: why['no kappa gain']+=1; continue
        W=W2; Wd=lb.Word(W); kc=k2; acc+=1; landed+=1
        rec=dict(r=r,X=X,p=p,side=side,net=net,c=cd.meta['c'],sol={a:str(b) for a,b in sol.items()},kappa=str(k2),new_lifetimes=c['new_lifetimes'])
        log.append(rec); print('HIT',landed,rec,'[%.0fs]'%(time.time()-t0),flush=True)
        if landed%5==0: json.dump(W,gzip.open(out+'_tmp.json.gz','wt'))
    print('pass',ps,'accepted',acc,'kappa',kc,'x%.8f'%(float(kc)/float(k0)),dict(why.most_common(8)),'[%.0fs]'%(time.time()-t0),flush=True)
    if not acc: break
json.dump(W,gzip.open(out+'_%d.json.gz'%landed,'wt')); json.dump(log,open(out+'_log.json','w'),indent=0)
print('DONE landed',landed,'kappa',kc,'vs base',k0)
