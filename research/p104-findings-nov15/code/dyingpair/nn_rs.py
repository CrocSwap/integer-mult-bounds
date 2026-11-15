"""NONNEST: exact-ish (float 1e-10) feasibility rows for layouts given as role stage-sets. Thin block position pos in 0..L."""
import sys, time, json
from rs2 import *
def build(rolesets, L, pos):
    n=len(rolesets); Z=[[r for r,s in enumerate(rolesets) if k in s] for k in range(L)]; th=n+2-2*L
    o=[('S',Z[k]) for k in range(pos)]+[('T',)]*th+[('S',Z[k]) for k in range(pos,L)]
    return n,o
def s(x): return {i for i,c in enumerate(x) if c=='1'}
LAY={
 'ctlB4': None,
 'ilpmin': ['1...','.1..','..1.','.11.','...1','1..1','1111','1111'],
 'srch':   ['1...','.1..','..1.','.1..','...1','...1','111.','1..1','1111','.1.1','..11'][:0] or
           ['1...','1...','.1..','..1.','111.','...1','...1','1..1','.1.1','..11','1111'],
}
if __name__=='__main__':
    name=sys.argv[1]; pos=int(sys.argv[2]); starts=int(sys.argv[3]); L=4
    if name=='ctlB4': n,o,_=two_arm(4,2)
    else: n,o=build([s(x) for x in LAY[name]],L,pos)
    m=Model(n,o,-0.5,()); t0=time.time(); h,b,z=run(m,starts,seed=5,nfev=1500)
    print('%s pos=%d n=%d N=%d vars=%d solved %d/%d best %.1e (%.0fs)'%(name,pos,n,m.N,m.dim,h,starts,b,time.time()-t0),flush=True)
    if h: np.save('sol_%s_%d.npy'%(name,pos),z)
