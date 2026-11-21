"""LEVELTEST lib (own code). Level-cut sum S = sum_l rank M_l for decoders (relay-free networks).
Row k: gather support S_k = supp(V[:,k]) (F row), deposit support D_k = supp(W[:,k]) (G col), mod 4.
a_k = span labels(S_k) (dim = rank_F2 Q[S,:]); drop_k = price = rank_F2 Q[D,S]; dim b_k = dim a_k - drop_k.
M_l = sum_{k: dim b_k < l <= dim a_k} W[:,k] V[:,k]^T  (integer lift), rank over Q (mod big prime = lower bound, == generically).
Lift-independent floor: sum_l rank_F2 (M_l mod 2)."""
import json, numpy as np
D56='<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/'
LAB=[int(x) for x in open(D56+'labels.txt').read().split()]
dot=lambda a,b: bin(a&b).count('1')&1
Q104=np.array([[dot(a,b) for b in LAB] for a in LAB],dtype=np.int64)
E=json.load(open(D56+'e8base.json')); C104=np.array(E['C'],dtype=np.int64)[:104]; Gb=np.array(E['Gb'],dtype=np.int64)
P1=2147483647; P2=2147483629
def f2rank_rows(rows):
    b=[]
    for v in rows:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
def toint(r): return sum(int(x)<<i for i,x in enumerate(r))
def rankp(M,p=P1):
    M=np.array(M,dtype=np.int64)%p; r=0; rows,cols=M.shape
    for c in range(cols):
        if r==rows: break
        nz=np.nonzero(M[r:,c])[0]
        if len(nz)==0: continue
        i=nz[0]+r
        if i!=r: M[[r,i]]=M[[i,r]]
        inv=pow(int(M[r,c]),p-2,p); M[r]=(M[r]*inv)%p
        idx=np.nonzero(M[:,c])[0]; idx=idx[idx!=r]
        if len(idx): M[idx]=(M[idx]-(M[idx,c][:,None]*M[r][None,:])%p)%p
        r+=1
    return r
def rows_info(Q,Wm,Vm):
    """per-row (dim a, price) for gather=V, deposit=W (mod-4 supports)."""
    n=Q.shape[0]; Qi=[toint(Q[i]) for i in range(n)]; out=[]
    for k in range(Wm.shape[1]):
        S=np.nonzero(Vm[:,k]%4)[0]; D=np.nonzero(Wm[:,k]%4)[0]
        if len(S)==0 or len(D)==0: out.append((0,0)); continue
        da=f2rank_rows([Qi[int(i)] for i in S]); mask=sum(1<<int(i) for i in S)
        pr=f2rank_rows([Qi[int(i)]&mask for i in D]); out.append((da,pr))
    return out
def levels(info,h):
    """list over l=1..h of row-index lists R_l."""
    return [[k for k,(da,pr) in enumerate(info) if da-pr<l<=da] for l in range(1,h+1)]
def lift(Wm,mode,rng=None):
    Wm=Wm%4
    if mode=='std': return Wm.copy()
    if mode=='sym': return np.where(Wm==3,-1,Wm)
    if mode=='rand':
        up=np.where(Wm==0,0,rng.integers(0,2,Wm.shape)); 
        base=np.where(Wm==3,-1,Wm); alt=np.where(Wm==1,-3,np.where(Wm==2,-2,np.where(Wm==3,3,0)))
        return np.where(up==1,alt,base)
def level_sum(Q,Wm,Vm,Wl,Vl,info=None,h=9,primes=(P1,),want_f2=True):
    """returns (sum rank_Q (mod p max), per-level ranks list, f2 floor, D)"""
    if info is None: info=rows_info(Q,Wm,Vm)
    Ls=levels(info,h); rk=[]; f2=0
    for R in Ls:
        if not R: rk.append(0); continue
        M=Wl[:,R]@Vl[:,R].T
        rk.append(max(rankp(M,p) for p in primes))
        if want_f2:
            M2=(Wm[:,R]%2)@(Vm[:,R]%2).T%2; f2+=f2rank_rows([toint(r) for r in M2])
    return sum(rk),rk,f2,sum(pr for _,pr in info)
def evaluate(Q,Wm,Vm,rng,nrand=6,h=9,primes=(P1,)):
    """both orientations; lifts std/sym/rand. returns dict."""
    res={}
    for orient,(A,B) in (('fwd',(Wm,Vm)),('mir',(Vm,Wm))):
        info=rows_info(Q,A,B)   # deposit=A gather=B
        best=None; vals={}
        for mode in ('std','sym'):
            s=level_sum(Q,A,B,lift(A,mode),lift(B,mode),info,h,primes); vals[mode]=s[0]
            if best is None or s[0]<best[0]: best=s
        f2=s[2]
        for _ in range(nrand):
            Al=lift(A,'rand',rng); Bl=lift(B,'rand',rng)
            s=level_sum(Q,A,B,Al,Bl,info,h,primes,want_f2=False)
            if s[0]<best[0]: best=(s[0],s[1],f2,s[3])
        res[orient]=dict(D=best[3],S=best[0],lev=best[1],f2=f2,std=vals['std'],sym=vals['sym'])
    return res
