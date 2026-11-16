import sys,itertools,time,numpy as np
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..','g777'))
import carrier_lib as lib
from carrier_lib import lab,lines,simple,solve,n
coef=[[int(v) for v in solve(simple,l)] for l in lines]
def parab(I): return [t for t in range(n) if all(coef[t][k]==0 for k in range(8) if k not in I)]
I=(0,1,2,3,4,5)
P=set(parab(I)); T=[t for t in range(n) if t not in P]
print(n,len(P),len(T),'labels distinct',len(set(lab))==n, max(lab))
gm={4:8,5:12,6:20}
Tidx={t:i for i,t in enumerate(T)}
B=np.zeros((512,2),dtype=np.uint64)
for t in T:
    i=Tidx[t]; B[lab[t],i//64]|=np.uint64(1)<<np.uint64(i%64)
def pcnt(a):
    a=a.copy(); c=np.zeros(a.shape,dtype=np.int64)
    for s in range(0,64,16): c+=np.array([bin(x).count('1') for x in range(1<<16)],dtype=np.int64)[((a>>np.uint64(s))&np.uint64(0xffff)).astype(np.int64)]
    return c
def flats(k,need):
    out=set()
    for piv in itertools.combinations(range(9),k):
        # RREF: row r has leading 1 at bit piv[r] (bit index counted from high=0), free entries at non-pivot columns right of pivot
        free=[(r,c) for r in range(k) for c in range(piv[r]+1,9) if c not in piv]
        nf=len(free); idx=np.arange(1<<nf,dtype=np.int64)
        rows=[]
        for r in range(k):
            v=np.full(1<<nf,1<<(8-piv[r]),dtype=np.int64); rows.append(v)
        for b,(r,c) in enumerate(free): rows[r]=rows[r]|(((idx>>b)&1)<<(8-c))
        elems=[]
        for m in range(1,1<<k):
            e=np.zeros(1<<nf,dtype=np.int64)
            for r in range(k):
                if m>>r&1: e^=rows[r]
            elems.append(e)
        lo=np.zeros(1<<nf,dtype=np.uint64); hi=np.zeros(1<<nf,dtype=np.uint64)
        for e in elems: lo|=B[e,0]; hi|=B[e,1]
        cnt=pcnt(lo)+pcnt(hi)
        sel=np.nonzero(cnt==need)[0]
        for s in sel: out.add((int(lo[s]),int(hi[s])))
    return out
# NB label bit order is irrelevant: any linear coordinate system works as long as lab are the 9-bit labels
t0=time.time()
F={k:[a|(b<<64) for a,b in flats(k,gm[k])] for k in (4,5,6)}
print({k:len(v) for k,v in F.items()},time.time()-t0,flush=True)
full=(1<<len(T))-1
def search(rem,mask,ws):
    if not ws: return mask==full
    unc=full&~mask
    if unc==0: return False
    low=unc&-unc
    w=ws[0]
    # flats must be chosen in order of dims; branch: lowest uncovered line must be in some flat of any remaining dim
    for w in set(ws):
        rest=list(ws); rest.remove(w)
        for f in F[w]:
            if f&low and not (f&mask):
                if search(rem,mask|f,rest): return True
    return False
print('comp 6,6,5,5,5,4 tight cover exists:',search(None,0,[6,6,5,5,5,4]))
