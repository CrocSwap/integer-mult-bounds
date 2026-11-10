"""Hub rank law, exact check, v=2 (two ports share D), L=2 and L=4. stdlib + fractions. python3 -I -B hub_law.py
Model (hypotheses of Theorem 4): coordinate masks, units I-2xy^T (yx=0), x,y inside mask, product=-I at D=1,
D enters as Phi_k=Delta_k T_k. Port-coupling gauges: (g1) per-field GL2 mixing of the two port copies,
(g2) conjugation of the thin units alone by Omega(x)I on the port index (thin units become cross-port).
Claims tested at generic AND degenerate nonzero D:
 (A) rank Z(D)=N-n=2  (B) Z_kl=1/2 Z_km Z_ml for LOCAL blocks (C) Z_fl(D)=Z_fl(1)*prod E_k, rank Z_fl(1)=2
 (D) overlap coordinates of y_l,x_f lie in every LOCAL mask, >=2 of them.
Control: same pipeline on a v=1 root must give rank 1 (known)."""
import random, itertools, sys
from fractions import Fraction as Q
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chain_root import units, mm
random.seed(7)
fails=[]
def ck(c,m):
    if not c: fails.append(m); print("FAIL",m)
    return c
def rank(M):
    M=[r[:] for r in M]; r=0; nr=len(M); nc=len(M[0]) if M else 0
    for c in range(nc):
        p=next((i for i in range(r,nr) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(nr):
            if i!=r and M[i][c]!=0:
                f=M[i][c]/M[r][c]; M[i]=[a-f*b for a,b in zip(M[i],M[r])]
        r+=1
    return r
def inv(A):
    n=len(A); M=[A[i][:]+[Q(int(i==j)) for j in range(n)] for i in range(n)]
    for c in range(n):
        p=next(r for r in range(c,n) if M[r][c]!=0); M[c],M[p]=M[p],M[c]
        pv=M[c][c]; M[c]=[v/pv for v in M[c]]
        for r in range(n):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[a-f*b for a,b in zip(M[r],M[c])]
    return [r[n:] for r in M]
def matvec(A,x): return [sum(a*b for a,b in zip(r,x)) for r in A]
def build(gL,gR,v,coupling):
    n,Ls,Rs,th=units(gL,gR)
    nn=v*n
    def lift(x,p): # port p copy: coordinate (c,p) -> c*v+p
        out=[Q(0)]*nn
        for c in range(n): out[c*v+p]=x[c]
        return out
    # blocks: list of (kind, [(x,y)...], mask-set-of-big-coords or None, siteindex)
    sites=[]
    for kind,seq in (('L',Ls),('T',th),('R',Rs)): pass
    seq=Ls+th+Rs
    # order: Ls, thin, Rs
    for idx,(x,y,m) in enumerate(seq):
        pairs=[(lift(x,p),lift(y,p)) for p in range(v)]
        mask=None if m is None else {c*v+p for c in m for p in range(v)}
        sites.append(dict(pairs=pairs,mask=mask,local=m is not None))
    if 'g2' in coupling:
        while True:
            Om=[[Q(random.randint(-3,3)) for _ in range(v)] for _ in range(v)]
            if rank(Om)==v: break
        O=[[Q(0)]*nn for _ in range(nn)]
        for c in range(n):
            for a in range(v):
                for b in range(v): O[c*v+a][c*v+b]=Om[a][b]
        Oi=inv(O)
        for s in sites:
            if not s['local']:
                s['pairs']=[(matvec(O,x),[sum(y[i]*Oi[i][j] for i in range(nn)) for j in range(nn)]) for x,y in s['pairs']]
    # gauge g1: per-field GL_v acting on port copies
    if 'g1' in coupling:
        W=[[Q(int(i==j)) for j in range(nn)] for i in range(nn)]
        for c in range(n):
            while True:
                B=[[Q(random.randint(-2,2)) for _ in range(v)] for _ in range(v)]
                if rank(B)==v: break
            for a in range(v):
                for b in range(v): W[c*v+a][c*v+b]=B[a][b]
        Wi=inv(W)
        for s in sites:
            s['pairs']=[(matvec(W,x),[sum(y[i]*Wi[i][j] for i in range(nn)) for j in range(nn)]) for x,y in s['pairs']]
    return nn,sites
def Tm(x,y,nn): return [[Q(int(i==j))-2*x[i]*y[j] for j in range(nn)] for i in range(nn)]
def check_instance(gL,gR,v,coupling,Dlist):
    nn,sites=build(gL,gR,v,coupling)
    # product = -I at D=1
    P=[[Q(int(i==j)) for j in range(nn)] for i in range(nn)]
    for s in sites:
        for x,y in s['pairs']: P=mm(Tm(x,y,nn),P)
    ck(all(P[i][j]==(-1 if i==j else 0) for i in range(nn) for j in range(nn)),f"{gL,gR,v,coupling}: product -I")
    # unit list with site id
    U=[(si,x,y) for si,s in enumerate(sites) for x,y in s['pairs']]
    N=len(U); loc=[si for si,s in enumerate(sites) if s['local']]
    ck(N-nn==v,"excess N-n=v")
    def delta_inv_pref(D):
        # diag of prod_{k<i} Delta_k for each unit position: Lam_i
        lam=[];cur=[Q(1)]*nn
        for si,s in enumerate(sites):
            for _ in s['pairs']: lam.append(cur[:])
            if s['local']:
                cur=[cur[c]*(D[si] if c in s['mask'] else 1) for c in range(nn)]
        return lam
    def Zmat(D):
        lam=delta_inv_pref(D)
        G=[[sum(U[i][2][c]*lam[i][c]/lam[j][c]*U[j][1][c] for c in range(nn)) for j in range(N)] for i in range(N)]
        # units I-2x'y' ; convention I - xt y with xt=2x: Gamma=2G
        Z=[[Q(0)]*N for _ in range(N)]
        for i in range(N):
            for j in range(N):
                g=2*G[i][j]
                Z[i][j]= 2 if i==j else (g if i>j else -g)
        return Z
    # block index sets for LOCAL sites
    blk={}; pos=0
    for si,s in enumerate(sites):
        k=len(s['pairs']); blk[si]=list(range(pos,pos+k)); pos+=k
    def sub(Z,a,b): return [[Z[i][j] for j in blk[b]] for i in blk[a]]
    Z1=Zmat({si:Q(1) for si in loc})
    f,l=loc[0],loc[-1]
    for D in Dlist:
        Dd={si:D[t] for t,si in enumerate(loc)}
        Z=Zmat(Dd)
        ck(rank(Z)==N-nn,f"rank Z(D) {gL,gR,v,coupling} D={[str(d) for d in D]}: {rank(Z)}")
        for a,m,b in itertools.product(loc,loc,loc):
            if a==m or m==b: continue  # a=m trivial identity needs Z_mm; skip degenerate
            Zam,Zmb,Zab=sub(Z,a,m),sub(Z,m,b),sub(Z,a,b)
            prod=mm(Zam,Zmb)
            ck(all(Zab[i][j]==prod[i][j]/2 for i in range(v) for j in range(v)),f"cocycle {a,m,b}")
        Zfl=sub(Z,f,l); Z1fl=sub(Z1,f,l)
        pe=Q(1)
        for si in loc:
            if f<=si<l: pe/=Dd[si]
        ck(all(Zfl[i][j]==Z1fl[i][j]*pe for i in range(v) for j in range(v)),"Z_fl = const*prod E")
    ck(rank(sub(Z1,f,l))==v,"rank Z_fl const = v")
    # overlap coordinates
    xf=[x for x,y in sites[f]['pairs']]; yl=[y for x,y in sites[l]['pairs']]
    ov={c for c in range(nn) if any(x[c]!=0 for x in xf) and any(y[c]!=0 for y in yl)}
    allm=set.intersection(*[sites[si]['mask'] for si in loc])
    ck(ov<=allm,"overlap coords in every LOCAL mask"); ck(len(ov)>=v,"overlap >= v coords")
    return len(ov),len(allm)
def Dsets(nl):
    g=lambda: Q(random.randint(2,40),random.randint(2,40))
    out=[[g() for _ in range(nl)] for _ in range(3)]
    out+= [[Q(1)]*nl, [Q(-1)]*nl, [Q(-1) if i%2 else Q(1) for i in range(nl)],
           [Q(2)]*nl, [Q(2) if i%2 else Q(1,2) for i in range(nl)],   # D_jD_k=1
           [Q(1)]*(nl-1)+[Q(3)], [Q(-1,3)]*nl, [Q(random.choice([1,-1,2,Q(1,2),-2])) for _ in range(nl)]]
    return out
for (gL,gR) in [(1,1),(2,2)]:
    nl=gL+gR
    for v,cp in [(1,''),(2,''),(2,'g1'),(2,'g2'),(2,'g1g2')]:
        r=check_instance(gL,gR,v,cp,Dsets(nl)); print(f"L={nl} v={v} coupling={cp or 'none'}: ok overlap={r[0]} allmask={r[1]}",flush=True)
print("PASS_HUB_LAW" if not fails else f"FAILS {len(fails)}")
