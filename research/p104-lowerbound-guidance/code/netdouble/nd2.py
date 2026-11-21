# NETDOUBLE nd2 (own code): HALF-type networks (Mbar o Q = 0 mod 2, built by choosing Fbar in a kernel), exact checks:
#  SUM   : rho_B^net + rho_A^net <= D           (proved; rho by Rado = random GF(2^16) transversal, a rigorous lower bound)
#  HC    : B := (M o Q)/2 mod 2 equals X_walk + Y + Z_full (identity) ; IX: rank(B + X_walk) <= D ?  (needs H' = 0 for the proof)
#  WALK  : forward walk decoder W=(G_k, r_k), backward W*=(u_k, F_k): is rho_A+rho_B <= D for either (single-decoder realisation)?
import random, sys
from ndlib import *
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3]); noHp=len(sys.argv)>4 and sys.argv[4]=='noHp'
random.seed(seed)
def kernel_vec(rows,K):
    # random vector x on index set K with rows·x = 0 over F2 (rows: list of lists over K)
    A=[r[:] for r in rows]; R=len(A); C=len(K); piv=[]; r=0
    for c in range(C):
        p=next((i for i in range(r,R) if A[i][c]),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        for i in range(R):
            if i!=r and A[i][c]: A[i]=[a^b for a,b in zip(A[i],A[r])]
        piv.append(c); r+=1
    free=[c for c in range(C) if c not in piv]; x=[0]*C
    for c in free: x[c]=random.randint(0,1)
    for i,c in enumerate(piv): x[c]=sum(A[i][d]*x[d] for d in free)%2
    return x
def rnd(): return random.randrange(1,65536)
def rado_rows(gens_per_row,n):
    # gens_per_row[t] = list of n-vectors (0/1); random GF combination per row; returns rank
    A=[]
    for gl in gens_per_row:
        row=[0]*n
        for g in gl:
            c=rnd(); row=[x^(c if v else 0) for x,v in zip(row,g)]
        A.append(row)
    return grank(A)
def masked(vec,Qrow): return [a*b for a,b in zip(vec,Qrow)]
stats={'tested':0,'sum_viol':0,'hc_id_fail':0,'ix_viol':0,'W_viol':0,'Ws_viol':0,'tight_sum':0}
ex={}
for tr in range(TR):
    net=rand_net(h)
    if noHp: net=Net(h,net.nodes,net.F,net.G,[[v%2 for v in r] for r in net.H])
    n,m=net.n,net.m; Q=net.Q
    Fb=[[0]*n for _ in range(m)]
    for p in range(n):
        K=[k for k in range(m) if net.inA[k][p]]
        if not K: continue
        Tp=[t for t in range(n) if Q[t][p]]
        x=kernel_vec([[net.ub[t][k] for k in K] for t in Tp],K)
        for i,k in enumerate(K): Fb[k][p]=x[i]
    F=[[ (Fb[k][p]+2*random.randint(0,1))*net.inA[k][p] for p in range(n)] for k in range(m)]
    net=Net(h,net.nodes,F,net.G,net.H)
    assert net.legal() and not any(any(r) for r in net.MQb)
    MQ4=[[ (net.M[i][j]*Q[i][j])%4 for j in range(n)] for i in range(n)]
    if not any(any(r) for r in MQ4): continue
    stats['tested']+=1
    B=[[v//2 for v in r] for r in MQ4]
    # cover over Z with hat (0/1) matrices
    Gh=net.Gb; Hh=[[v%2 for v in r] for r in net.H]; Fh=net.Fb
    Nh=[[int(i==j) for j in range(m)] for i in range(m)]; P=[r[:] for r in Nh]
    for _ in range(m):
        P=mm(P,Hh); Nh=[[Nh[i][j]+P[i][j] for j in range(m)] for i in range(m)]
    cov=mm(mm(Gh,Nh),Fh)
    X=[[ ((cov[i][j]*Q[i][j])//2)%2 for j in range(n)] for i in range(n)]
    Gp=[[(v//2)%2 for v in r] for r in net.G]; Fp=[[(v//2)%2 for v in r] for r in net.F]; Hp=[[(v//2)%2 for v in r] for r in net.H]
    Nb=[[v%2 for v in r] for r in Nh]
    Y=had(mm(mm(Gp,Nb),Fh,2),Q)
    Zf=had(mm(mm(Gh,Nb),Fp,2),Q); Zh=had(mm(mm(mm(mm(Gh,Nb),Hp),Nb),Fh,2),Q)
    S=[[ (x+y+z+w)%2 for x,y,z,w in zip(*rows)] for rows in zip(X,Y,Zf,Zh)]
    if S!=[[v%2 for v in r] for r in B]: stats['hc_id_fail']+=1
    BX=[[ (a+b)%2 for a,b in zip(r,s)] for r,s in zip(B,X)]
    rix=rk2(BX)
    if rix>net.D:
        stats['ix_viol']+=1
        if 'ix' not in ex or rix-net.D>ex['ix'][0]: ex['ix']=(rix-net.D,rix,net.D,rk2(Y),rk2(Zf),rk2(Zh))
    # rho^net
    rB=rado_rows([[masked(net.rb[k],Q[t]) for k in range(m) if net.inBp[k][t]] for t in range(n)],n)
    rA=rado_rows([[masked([net.ub[t][k] for t in range(n)],[Q[t][p] for t in range(n)]) for k in range(m) if net.inA[k][p]] for p in range(n)],n)
    if rB+rA>net.D: stats['sum_viol']+=1
    if rB+rA==net.D: stats['tight_sum']+=1
    # walk decoders
    wB=rado_rows([[masked(net.rb[k],Q[t]) for k in range(m) if net.G[t][k]%4] for t in range(n)],n)
    wA=rado_rows([[masked([net.Gb[t][k] for t in range(n)],[Q[t][p] for t in range(n)]) for k in range(m) if net.r4[k][p]] for p in range(n)],n)
    sB=rado_rows([[masked(net.Fb[k],Q[t]) for k in range(m) if net.u4[t][k]] for t in range(n)],n)
    sA=rado_rows([[masked([net.ub[t][k] for t in range(n)],[Q[t][p] for t in range(n)]) for k in range(m) if net.F[k][p]%4] for p in range(n)],n)
    assert wB<=rB and sA<=rA
    if wA+wB>net.D:
        stats['W_viol']+=1
        if 'W' not in ex or wA+wB-net.D>ex['W'][0]: ex['W']=(wA+wB-net.D,wA,wB,rA,rB,net.D)
    if sA+sB>net.D:
        stats['Ws_viol']+=1
        if 'Ws' not in ex or sA+sB-net.D>ex['Ws'][0]: ex['Ws']=(sA+sB-net.D,sA,sB,rA,rB,net.D)
print('h',h,'noHp',noHp,stats,ex)
