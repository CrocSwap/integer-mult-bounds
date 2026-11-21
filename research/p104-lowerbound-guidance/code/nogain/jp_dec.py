"""NOGAIN jp_dec.py: test JUNK-PAYS on relay-free networks (P104 Z4 decoders, Gibbs walks; imports LEVELTEST lib read-only).
loss = sum_{l=2..8} (8 - rank M_l)_+, junk = D - sum_l rank M_l. JUNK-PAYS <=> loss <= junk <=> D >= sum_{l not in 2..8} rk_l + sum_{l in 2..8} max(8,rk_l)."""
import sys, numpy as np
sys.path.insert(0,'../leveltest'); sys.argv=[sys.argv[0]]+sys.argv[1:]
from lt import *
import run_gibbs_lib as RG
seed=int(sys.argv[1]); steps=int(sys.argv[2]); mode=sys.argv[3]; every=int(sys.argv[4])
rng=np.random.default_rng(seed); RG.rng=rng; n=104
if mode=='e8':
    W=np.load('../orbitlp/e8W.npy')%4; V=np.load('../orbitlp/e8V.npy')%4
    W=np.concatenate([W,np.zeros((n,8),np.int64)],1); V=np.concatenate([V,np.zeros((n,8),np.int64)],1)
else:
    from run_all_inv import inv4
    W0=C104%4; V0=(C104@Gb)%4; m=int(mode[2:])
    while True:
        Xm=rng.integers(0,4,(8,m)); Pi=inv4(Xm[:,:8])
        if Pi is not None: break
    Ym=np.zeros((8,m),dtype=np.int64); Ym[:,:8]=Pi.T; W=(W0@Xm)%4; V=(V0@Ym)%4
worst=None; viol=0; tot=0
for s in range(steps+1):
    if s%every==0:
        assert RG.check(W,V)
        r=evaluate(Q104,W,V,rng,nrand=3)
        for o in ('fwd','mir'):
            x=r[o]; rk=x['lev']; D=x['D']; S=sum(rk)
            loss=sum(max(0,8-rk[l-1]) for l in range(2,9)); junk=D-S; tot+=1
            if loss>junk: viol+=1; print('VIOL',s,o,'D',D,'lev',rk,'loss',loss,'junk',junk,flush=True); np.save(f'viol_W_{mode}{seed}_{s}.npy',W); np.save(f'viol_V_{mode}{seed}_{s}.npy',V)
            if worst is None or junk-loss<worst[0]: worst=(junk-loss,s,o,D,rk)
        if s%(every*10)==0: print(mode,seed,s,'D',r['fwd']['D'],'lev',r['fwd']['lev'],flush=True)
    t=int(rng.integers(n)); W,V=RG.resample(W,V,t,'W' if rng.random()<0.5 else 'V')
print('SUMMARY',mode,seed,'evals',tot,'violations',viol,'min junk-loss',worst)
