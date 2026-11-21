"""GIBBS8 driver: SA on screened normal-form S1 (alpha+beta) over mod-8 quarter decoders, proposals = bursts of cost-tilted Gibbs steps.
usage: g8run.py SET START SEED NEVAL T BETA [MPAD]   START in {frame, e7:<pkl>, rand}"""
import sys,time,pickle; from g8lib import *
sn,start,seed,neval,T,beta=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6])
mpad=int(sys.argv[7]) if len(sys.argv)>7 else 0
import os; CCAP=int(os.environ.get('CCAP','999')); KK=int(os.environ.get('KK','8'))
thr={'HS64':38,'E7s':41}[sn]; Q=Q_std(std_set(sn)); rng=np.random.default_rng(seed)
if start=='frame': W,V=hs_frame_start(Q)
elif start.startswith('e7:'): W,V=load_start(start[3:],Q)
else: raise SystemExit
if mpad:
    n=len(Q); W=np.concatenate([W,np.zeros((n,mpad),dtype=np.int64)],1); V=np.concatenate([V,np.zeros((n,mpad),dtype=np.int64)],1)
m=W.shape[1]
if start.endswith('rand') or 'mix' in sys.argv[-1:]: pass
X,Y=random_gl8(m,rng,int(sys.argv[8]) if len(sys.argv)>8 else 0)
W=(W@X)%8; V=(V@Y)%8
D=Dec(Q,W,V); assert D.valid(); tag='%s_%s_s%d_m%d'%(sn,start.split('/')[-1].replace('.pkl','').replace(':','_'),seed,m)
def evalD(D,full=False):
    rows=to_rows(D); 
    if full: r=pipeline(rows,Q,thr,iters=800,seeds=2)
    else: r=pipeline(rows,Q,thr,iters=300,seeds=1)
    return r
log=open('run_%s.log'%tag,'w'); best=None; minC=10**9; minS=10**9; t0=time.time()
cur=evalD(D); cE=cur['S1']; print('start',D.C(),cur,flush=True)
hist=[]
TLIM=float(os.environ.get('TLIM','1e9'))
for it in range(neval):
    if time.time()-t0>TLIM: break
    snap=(D.W.copy(),D.V.copy(),list(D.pr))
    nb=int(rng.integers(1,30))
    for _ in range(nb): step(D,rng,beta=beta,K=KK)
    assert D.valid()
    C=D.C(); minC=min(minC,C)
    if C>CCAP: D.W,D.V=snap[0],snap[1]; D.pr=snap[2]; continue
    r=evalD(D); s=r['S1']
    if s<thr+3:
        r2=evalD(D,True); s=min(s,r2['S1']) if False else r2['S1']; r=r2
    hist.append((C,r['C1'],s))
    line='it %d t %.0f C %d C0 %d C1 %d S1 %d cls %s'%(it,time.time()-t0,C,r['C0'],r['C1'],s,r['classes']); log.write(line+'\n'); log.flush()
    if C<thr: print('LOUD C<thr',line,flush=True); pickle.dump((D.W.copy(),D.V.copy()),open('LOUD_C_%s_%d.pkl'%(tag,it),'wb'))
    if s<thr:
        print('FLAG S1<thr',line,flush=True); pickle.dump((D.W.copy(),D.V.copy()),open('FLAG_S1_%s_%d.pkl'%(tag,it),'wb'))
    minS=min(minS,s)
    if s<=cE or rng.random()<np.exp(-(s-cE)/T): cE=s
    else: D.W,D.V=snap[0],snap[1]; D.pr=snap[2]
print('done',tag,'minC',minC,'minS1',minS,'time %.0f'%(time.time()-t0),flush=True)
pickle.dump(hist,open('hist_%s.pkl'%tag,'wb'))
