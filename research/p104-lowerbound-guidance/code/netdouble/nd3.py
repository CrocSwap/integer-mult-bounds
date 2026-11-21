# NETDOUBLE nd3 (own code): half-type networks (Mbar o Q = 0). Random y ⊆ L(b^perp), f ⊆ L(a), h' on legal edges:
#  TORS : rank( (y Nb Fb + Gb Nb (f + h' Nb Fb)) o Q ) <= D      [proved: eps-torsion of an R=F2[e]/e^2 network]
#  SUMH : rank((y Nb Fb)oQ) + rank((Gb Nb (f + h' Nb Fb))oQ) <= D ?   [h'=0 is the proved master sum; h' != 0 = test]
#  control TORS-ILLEGAL: h' placed on an illegal edge (b_j not ⊆ a_k)
import random, sys
from ndlib import *
from nd2 import kernel_vec
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3]); random.seed(seed)
st={'tested':0,'tors':0,'sumh':0,'sum0':0,'ctrl':0,'ctrl_tested':0}
for tr in range(TR):
    net=rand_net(h); n,m,Q=net.n,net.m,net.Q
    Fb=[[0]*n for _ in range(m)]
    for p in range(n):
        K=[k for k in range(m) if net.inA[k][p]]
        if not K: continue
        Tp=[t for t in range(n) if Q[t][p]]
        x=kernel_vec([[net.ub[t][k] for k in K] for t in Tp],K)
        for i,k in enumerate(K): Fb[k][p]=x[i]
    net=Net(h,net.nodes,Fb,net.G,net.H); assert not any(any(r) for r in net.MQb)
    if not any(any(r) for r in Fb): continue
    Nb=net.Nb; st['tested']+=1
    legal=[(k,j) for k in range(m) for j in range(k) if net.nodes[j][1]<=net.nodes[k][0]]
    illegal=[(k,j) for k in range(m) for j in range(k) if not net.nodes[j][1]<=net.nodes[k][0]]
    for rep in range(4):
        y=[[net.inBp[k][t]&random.randint(0,1) for k in range(m)] for t in range(n)]
        f=[[net.inA[k][p]&random.randint(0,1) for p in range(n)] for k in range(m)]
        hp=[[0]*m for _ in range(m)]
        for (k,j) in legal: hp[k][j]=random.randint(0,1)
        Yh=had(mm(y,net.rb,2),Q)
        zf=[[ (a+b)%2 for a,b in zip(r1,r2)] for r1,r2 in zip(f,mm(hp,net.rb,2))]
        Zh=had(mm(net.Gb,mm(Nb,zf,2),2),Q); Z0=had(mm(net.Gb,mm(Nb,f,2),2),Q)
        S=[[ (a+b)%2 for a,b in zip(r,s)] for r,s in zip(Yh,Zh)]
        if rk2(S)>net.D: st['tors']+=1
        if rk2(Yh)+rk2(Zh)>net.D: st['sumh']+=1
        if rk2(Yh)+rk2(Z0)>net.D: st['sum0']+=1
        if illegal:
            hp2=[r[:] for r in hp]
            for (k,j) in illegal: hp2[k][j]=1
            # illegal relay also changes Nbar: rebuild with H2 = Hbar + 0 (only eps-part illegal): content perturbation through illegal edge
            zf2=[[ (a+b)%2 for a,b in zip(r1,r2)] for r1,r2 in zip(f,mm(hp2,net.rb,2))]
            S2=[[ (a+b)%2 for a,b in zip(r,s)] for r,s in zip(Yh,had(mm(net.Gb,mm(Nb,zf2,2),2),Q))]
            st['ctrl_tested']+=1
            if rk2(S2)>net.D: st['ctrl']+=1
print('h',h,st)
