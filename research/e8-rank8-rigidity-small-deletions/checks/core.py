# Core search for Step 1: for a line set U (containing u0,s0) and frames inside U, is "N_{u0 s0}=0" refutable (zero-pattern model)?
import sys, random, subprocess, os, pickle
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from e8lib import E,N,G,O,frames
def build(L, FRs, FRall, goal, path):
    L=sorted(L); var={}; cl=[]
    def v(k):
        if k not in var: var[k]=len(var)+1
        return var[k]
    def Z(u,s): return v(('z',u,s))
    def T(u,f,s):
        key=('t',u,f,s)
        if key not in var:
            t=v(key); a=[Z(p,q) for (p,q) in ((u,f),(f,s)) if p!=q]
            for x in a: cl.append([-t,-x])
            cl.append([t]+a)
        return var[key]
    for F in FRs:
        Fs=set(F)
        for u in L:
            if u in Fs: continue
            Tu=[f for f in F if G[u][f]!=0]
            for s in L:
                if s in Fs: continue
                I=[f for f in Tu if G[s][f]!=0]
                ts=[T(u,f,s) for f in I]
                if u==s: cl.append(ts); continue
                if G[u][s]==0:
                    for i,t in enumerate(ts): cl.append([-t]+[x for j,x in enumerate(ts) if j!=i])
                else:
                    z=Z(u,s); cl.append([z]+ts)
                    for i,t in enumerate(ts): cl.append([-z,-t]+[x for j,x in enumerate(ts) if j!=i])
    for F in FRall:
        Fs=set(F)
        for w in L:
            if w in Fs: continue
            Tw=[f for f in F if G[w][f]!=0]
            cl.append([-Z(w,f) for f in Tw]); cl.append([-Z(f,w) for f in Tw])
    cl.append([Z(*goal)])
    with open(path,'w') as fh:
        fh.write('p cnf %d %d\n'%(len(var),len(cl)))
        for c in cl: fh.write(' '.join(map(str,c))+' 0\n')
    return {k:i for k,i in var.items() if k[0]=='z'}
def kissat(path, tl=1200, proof=None):
    cmd=['kissat','--factor=false','--preprocessfactor=false','-q',path]+([proof] if proof else [])
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=tl)
    return r.returncode, r.stdout
def cegar(L, goal, nfr=20, maxit=40, tag='c', seed=1, proof=None, tl=1200, verbose=True):
    """returns (status, frames used). status 'UNSAT' (refuted) or 'SAT'"""
    Ls=set(L); FR=frames(L); rnd=random.Random(seed)
    FRs=FR if nfr>=len(FR) else rnd.sample(FR,nfr)
    for it in range(maxit):
        m=build(L,FRs,FR,goal,tag+'.cnf')
        rc,out=kissat(tag+'.cnf',tl,proof)
        if verbose: print('  it',it,'frames',len(FRs),'of',len(FR),'rc',rc,flush=True)
        if rc==20: return 'UNSAT',FRs,FR
        if rc!=10: return 'TIMEOUT',FRs,FR
        val=set()
        for line in out.splitlines():
            if line.startswith('v '): val|={int(x) for x in line[2:].split() if int(x)>0}
        Zs=[(k[1],k[2]) for k,i in m.items() if i in val]
        S=set(u for u,s in Zs)|set(s for u,s in Zs)
        have=set(FRs)
        sc=sorted([F for F in FR if F not in have],key=lambda F:-len(S&set(F)))
        if not sc: return 'SAT',FRs,FR
        FRs=FRs+sc[:10]
    return 'MAXIT',FRs,FR
if __name__=='__main__':
    u0=0; s0=[s for s in range(N) if G[0][s]!=0 and s!=0][0]
    L=list(range(N)); print('goal',u0,s0)
    st,FRs,FR=cegar(L,(u0,s0),tag='r1rig_full')
    print(st,len(FRs)); U=set([u0,s0]); 
    for F in FRs: U|=set(F)
    print('union size',len(U))
