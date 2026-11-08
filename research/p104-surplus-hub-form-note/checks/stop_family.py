"""Stop families used by form_capacity.py (variants of the one-pass family). All compressed: no per-port crossing sets.
 family 'rowline': down rows land at a line r (bottom dim 1, T3 style) on the helpers h_r*, after X reached V: stops L2_r. Zero-form helpers can then deliver x_t to Y_t.
 family 'gather' : X_r climbs line -> block G_S -> V. Up rows land at G_S before the block helpers read X (multi-pass: X written then read). Down rows V->0 as before.
 family 'both'   : rowline + gather.
 'dbl' = 2 helpers per ordered pair. Controls: planted same size; F at (1,0)."""
import sys,os,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from stop_solver import solve,forward,legal,target,GS,assert_frames
def skel(v,kd,ku,fam,dbl=False,blocks=None):
    V=frozenset(range(v));Z=frozenset()
    X=['X%d'%r for r in range(v)];Y=['Y%d'%t for t in range(v)]
    K=[f'h{r}_{t}' for r in range(v) for t in range(v) if r!=t]
    if dbl:K+=[f'i{r}_{t}' for r in range(v) for t in range(v) if r!=t]
    lk=lambda r:[k for k in K if k[1:].startswith(f'{r}_')]
    pk=lambda t:[k for k in K if k.endswith(f'_{t}')]
    B=[f'B{i}' for i in range(kd)];A=[f'A{i}' for i in range(ku)]
    E=[f'E{i}' for i in range(v)];OV=[f'O{i}' for i in range(v)];OL=[f'Ol{r}' for r in range(v)];OP=[f'Op{t}' for t in range(v)]
    pub=X+Y+K;own=B+A+E+OV+OL+OP;names=pub+own;idx={n:i for i,n in enumerate(names)};st=[]
    blocks=blocks or [list(range(v))[:v//2],list(range(v))[v//2:]]
    gather=fam in('gather','both');rowline=fam in('rowline','both')
    st.append((Z,Y+K+E+A))
    for r in range(v):st.append((frozenset([r]),[X[r],OL[r]]+lk(r)))
    if gather:
        # block stop: only helpers leaving toward t outside the block may ride; a second visit of those helpers reads the X just written by the row
        for bi,S in enumerate(blocks):
            hs=[k for k in K if int(k[1:].split('_')[0]) in S and int(k.split('_')[1]) not in S]
            st.append((frozenset(S),[X[r] for r in S]+[A[j] for j in range(ku) if j%len(blocks)==bi]+hs))
    st.append((V,X+A+B+OV))
    if rowline:
        for r in range(v):st.append((frozenset([r]),lk(r)+[B[i] for i in range(kd) if i%v==r]+[OL[r]]))
    else:st.append((Z,Y+B+E))
    for t in range(v):st.append((V-{t},[Y[t],OP[t]]+pk(t)))
    st.append((V,X+K+A+OV))
    return names,len(pub),[(f,[idx[n] for n in r]) for f,r in st],len(K)
def go(v,kd,ku,fam,tg,rs,dbl=False,planted=False,seed=0,iters=800):
    names,npub,stops,nk=skel(v,kd,ku,fam,dbl)
    if fam not in('gather','both'):assert_frames(names,npub,stops,v)
    else:
        seen={}
        for f,regs in stops:
            for i in regs:
                n=names[i]
                if i<npub:
                    if n in seen:assert seen[n]<=f,('descent',n,seen[n],f)
                    seen[n]=f
    rng=np.random.default_rng(seed);nreg=len(names)
    if planted:
        Ms=[np.eye(len(r))+rng.normal(0,.5,(len(r),len(r))) for f,r in stops];T=forward(Ms,stops,nreg,npub)[0][:npub]
    else:T=target(v,GS[tg],nk)
    h=l=0;b=1e9
    for i in range(rs):
        Ms,res,it=solve(T,stops,nreg,npub,rng,iters=iters);b=min(b,res)
        if res<1e-8:h+=1;l+=legal(Ms,stops,nreg,npub)[0]
    return '%d(%d)/%d %.0e'%(h,l,rs,b)
if __name__=='__main__':
    v=int(sys.argv[1]);rs=int(sys.argv[2]);fam=sys.argv[3];dbl=len(sys.argv)>4;t0=time.time()
    print(v,fam,'dbl' if dbl else '','planted(1,1)',go(v,1,1,fam,'x',2,dbl,planted=True),'planted(2,1)',go(v,2,1,fam,'x',1,dbl,planted=True),flush=True)
    for tg in ('FB','F','W','J'):
        for kd in range(0,v+1):
            print(tg,'kd',kd,' ku0..v:',' | '.join(go(v,kd,ku,fam,tg,rs,dbl,seed=kd*10+ku) for ku in range(0,v+1)),'t=%.0f'%(time.time()-t0),flush=True)
