"""usage: NCH=k python run19.py OUT.json.gz : top-k route chains (identical projective content, giveq) from chains19.pkl, exact settle."""
import os, sys, time, pickle
sys.path.insert(0,'.')
from m19 import *
import usweep14
from run_netc5 import relay_phase
from settle6 import settle_and_check6
t0=time.time(); log=lambda *a: print('[%5.0fs]'%(time.time()-t0),*a,flush=True)
N=load19(); H0=N.H0; U=units(N,H0)
for _k,_h in enumerate(H0): PIK[_k]=full_content(N,_h)
base=sum(N.hcost(h)[0] for h in H0); log('baseline plan cost %.1f helpers %d'%(base,len(H0)))
allc=pickle.load(open(os.environ.get('CF','chains19.pkl'),'rb')); k=int(os.environ['NCH'])
sel=[c for c in allc if c[0]>0][:k]
ch=[]
for sav,n_,hs in sel:
    mk(N,H0,U,hs); ch.append(dict(hs=hs,diffs=[[]]*(len(hs)-1)))
    log('chain units',len(hs),'frames',[U[i]['G'] for i in hs],'t1',[U[i]['t1'] for i in hs],'plan saving %.2f'%sav)
def setc(keep):
    N.chains11=[ch[i] for i in sorted(keep)]
    W1,lz=evaluate(N)
    if not lz:
        for spec in [x for x in os.environ.get('PB','').split(',') if x]:
            o,td,tr,q,fr=spec.split(':'); N.add_pickback(int(o),int(td),int(tr),Q(q),int(fr))
        from dual import dual_scan as _ds
        lz=_ds(N.emit())[0]
    return W1,lz
keep=set(range(len(ch))); W1,lz=setc(keep)
log('chains %d merging %d units; cost %.1f helpers %d lossy %d'%(len(ch),sum(len(c['hs']) for c in ch),N.cost()[0],len(N.H),len(lz)))
if lz:
    keys=sorted(keep); keep=set()
    for kk in keys:
        keep.add(kk)
        if setc(keep)[1]: keep.discard(kk)
    W1,lz=setc(keep); evaluate(N); log('DUAL repair kept %d of %d chains; cost %.1f lossy %d'%(len(keep),len(ch),N.cost()[0],len(lz)))
os.environ['PB']=','.join(':'.join(a) for a in N.PB)
W1,lz=relay_phase(N,log)
if lz: log('STOP: lossy after relays',lz); sys.exit(1)
log('plan cost after relays %.1f'%N.cost()[0])
for i in sorted(keep): 
    h=ch[i]['hs']; log('KEPT chain',h[:3],'...',len(h))
settle_and_check6(N,W1,sys.argv[1],log)
