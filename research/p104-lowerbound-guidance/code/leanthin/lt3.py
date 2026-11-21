# LEANTHIN lt3: INDEPENDENT exact verifier of an LP-dual certificate (reads certs/cert_k{k}.json only).
# LP (Q>=1, e=0, 'one' pattern, LC + TRIPLE-in-class, SET-RC2 c<=3): roles x_{D,P}, rows A x >= b, objective F = 2k-2 + sum x (val-1),
# val = (8D+1)^s - sum_pieces (8p)^s, s = 0.99 (rigorous mpmath interval arithmetic), chat = 104 F / k.
# Weak duality: y >= 0 integer/2^S.  For every type j: val_j - 1 + y.A_j <= eps (exhaustive partition DP over ALL (D,P), D<=k, in INTEGERS with
# rigorous rounding: ub for (8D+1)^s, lb for (8p)^s).  Then F <= 2k-2 - y.b + max(eps,0)*nmax, nmax = (2k-2)/(1-(9^s-8^s)) (valid for F>=0).
import sys,json
from math import comb
from fractions import Fraction
from mpmath import iv, mp
iv.dps=60
sI=iv.mpf(99)/iv.mpf(100)
def rows_of(k): return [(l,c) for c in range(1,min(3,k-1)+1) for l in range(2,k+1)]
def verify(k,path=None):
    J=json.load(open(path or f'certs/cert_k{k}.json')); S=J['S']; Y=[int(t) for t in J['y']]
    assert J['k']==k and all(t>=0 for t in Y)
    rows=rows_of(k); nr=len(rows); assert len(Y)==2+nr+4
    one=1<<S
    def up(x): return int(mp.ceil(mp.mpf(x.b)*one))
    def lo(x): return int(mp.floor(mp.mpf(x.a)*one))
    mp.dps=80
    ubA={D:up(iv.mpf(8*D+1)**sI) for D in range(1,k+1)}
    lbB={L:lo(iv.mpf(8*L)**sI) for L in range(1,k+1)}
    y0,y1=Y[0],Y[1]; yr=Y[2:2+nr]; yc,yl,ylc,yt=Y[2+nr:]
    eps=None; arg=None
    for D in range(1,k+1):
        g=[None]
        for L in range(1,D+1):
            t=-lbB[L]
            for q,(l,c) in enumerate(rows):
                av=comb(k-L,c)
                if D>=l:
                    if L<l: t+=yr[q]*L*av
                else: t+=yr[q]*L*(av-comb(k-D,c))
            if L==1: t+=y0+(y1 if D>=2 else 0)
            g.append(t)
        best=[0]+[None]*D
        for d in range(1,D+1): best[d]=max(best[d-L]+g[L] for L in range(1,d+1))
        rc=ubA[D]+best[D]-one+yc+yl*(k-(1 if D==1 else 0))+(ylc if D>=2 else 0)+yt*(comb(D,3)+comb(D,2)*(k-D))
        if eps is None or rc>eps: eps,arg=rc,D
    b=[2*k,2*k]+[2*k*comb(k-1,c) for (l,c) in rows]+[2*k-1,k*(2*k-2),k-2,3*comb(k,3)]
    ileaf=2+nr+1   # LEAFAVG row: coefficient k-[D=1] >= k-1 on EVERY type, so lowering its dual by delta=eps/(k-1) lowers every reduced cost by >= eps
    Y=list(Y)
    if eps>0:
        delta=-((-eps)//(k-1))          # ceil(eps/(k-1)), in 2^-S units
        if Y[ileaf]>=delta:
            Y[ileaf]-=delta; eps_used=0; mode='leafshift'
        else:
            eps_used=eps; mode='nmax'
    else: eps_used=0; mode='none'
    yb=sum(Fraction(Y[i]*b[i],one) for i in range(len(b)))
    F=2*k-2-yb
    if eps_used>0:
        v1=Fraction(up(iv.mpf(9)**sI),one)-Fraction(lo(iv.mpf(8)**sI),one)   # >= 9^s-8^s  (rigorous)
        assert v1<1
        F+=Fraction(eps_used,one)*Fraction(2*k-2)/(1-v1)
    chat=Fraction(104)*F/k
    return chat,eps,arg,J["float_chat"],mode
if __name__=='__main__':
    bar=Fraction(128891,1000)
    for k in map(int,sys.argv[1:]):
        chat,eps,arg,fl,mode=verify(k)
        print(f'k{k} [{mode}]: float {fl:.6f}  EXACT chat <= {float(chat):.6f}  ({"< bar" if chat<bar else ">= bar"}; margin {float(bar-chat):.4f})  max-pricing-slack {float(Fraction(eps,1<<110)):.3e} at D={arg}',flush=True)
