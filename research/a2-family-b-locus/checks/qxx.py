# Q_XX: min cost of a square (8-term) inside decoder of G with the triangle X deleted on BOTH sides (rows and columns), via opt3u exact duality B&B. Also Z_r, Z_c subsets.
import os,sys,io,contextlib,itertools
os.environ['NDIM']='8'; os.environ['NT']='8'
from a2lib import *
import opt3u
Xt=list(X)
def run(Zr,Zc):
    ph=[([0]*8 if u in Zr else list(L[u])) for u in range(v)]; qh=[([0]*8 if u in Zc else list(L[u])) for u in range(v)]
    out={}
    for co,w in cls.items():
        Oc=bits(w); nr=nullspace([ph[u] for u in Oc],8); nc=nullspace([qh[u] for u in Oc],8)
        if nr or nc: out[co]=(len(Oc),nr,nc)
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
        r=opt3u.run(list(Zr),list(Zc),[0]*v,[0]*v,out,80,verbose=False,PH=(ph,qh))
    ok=all(len(x[1])<=1 and len(x[2])<=1 for x in out.values())
    return r,ok
args=sys.argv[1:]
kr,kc=int(args[0]),int(args[1])
Zr=Xt[:kr]; Zc=Xt[:kc] if len(args)<3 else Xt[3-kc:]
print(UNIT,'Zr',Zr,'Zc',Zc,run(Zr,Zc),flush=True)
