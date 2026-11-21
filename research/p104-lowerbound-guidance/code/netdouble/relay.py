# NETDOUBLE relay (own code): exact checks on N2D's relay counterexample (h=5, 2 nodes, 1 relay, D=4, mu4=7>6).
import itertools, random
from ndlib import *
h=5
labs=[1,2,4,7,8,11,13,14,16,19,21,22,25,26,28,31]
bj=frozenset([0,2,8,10,20,22,28,30]); aj=frozenset(range(32)); ak=bj; bk=frozenset([0,22])
F=[[1,3,1,1,3,3,3,0,3,3,0,0,1,3,3,3],[0,2,0,0,3,0,0,0,0,0,0,3,0,0,3,0]]
Gj=[3,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0]; Gk=[0,0,0,1,3,0,0,3,0,1,1,0,0,0,1,0]
G=[[a,b] for a,b in zip(Gj,Gk)]; H=[[0,0],[3,0]]
net=Net(h,[(aj,bj),(ak,bk)],F,G,H); assert net.labs==labs and net.legal()
n,m,Q=net.n,net.m,net.Q
MQ4=[[(net.M[i][j]*Q[i][j])%4 for j in range(n)] for i in range(n)]
print('D',net.D,'Mbar o Q zero?',not any(any(r) for r in net.MQb),'rank_F2(Mbar o Q)',rk2(net.MQb))
T=lambda A:[list(r) for r in zip(*A)]
Ys=[t for t in range(n) if net.inBp[0][t]]; Yk=[t for t in range(n) if net.inBp[1][t]]
Fj=[p for p in range(n) if net.inA[0][p]]; Fk=[p for p in range(n) if net.inA[1][p]]
print('|L(bj^perp)|',len(Ys),'|L(bk^perp)|',len(Yk),'|L(aj)|',len(Fj),'|L(ak)|',len(Fk))
Nb=net.Nb
def blockrank(y,f):
    z=mm(Nb,f,2)
    A=had(mm(y,net.rb,2),Q); B=had(mm(y,z,2),Q); E=had(mm(net.Gb,z,2),Q)
    return rk2([ra+rb for ra,rb in zip(A,B)]+[rc+re for rc,re in zip(net.MQb,E)])
# exhaustive over y (10 bits) with f random; and exhaustive rho's
best=0; random.seed(5)
for bits in range(1<<(len(Ys)+len(Yk))):
    y=[[0,0] for _ in range(n)]
    for i,t in enumerate(Ys): y[t][0]=(bits>>i)&1
    for i,t in enumerate(Yk): y[t][1]=(bits>>(len(Ys)+i))&1
    for rep in range(20):
        f=[[random.randint(0,1)*net.inA[k][p] for p in range(n)] for k in range(m)]
        best=max(best,blockrank(y,f))
print('max sampled master block rank (canonical lower-left = Mbar o Q):',best,'<= D =',net.D)
# exact rho_B^net (y exhaustive) and rho_A^net (f exhaustive, 2^20)
rB=0
for bits in range(1<<(len(Ys)+len(Yk))):
    y=[[0,0] for _ in range(n)]
    for i,t in enumerate(Ys): y[t][0]=(bits>>i)&1
    for i,t in enumerate(Yk): y[t][1]=(bits>>(len(Ys)+i))&1
    rB=max(rB,rk2(had(mm(y,net.rb,2),Q)))
# rho_A: columns p: sum_k f_k(p) u_k o Q_p ; per column choose element of span -> exact via enumerating column choices is product; use Rado = max over f exhaustively by columns
cols=[]
for p in range(n):
    gens=[sum((net.ub[t][k]*Q[t][p])<<t for t in range(n)) for k in range(m) if net.inA[k][p]]
    cols.append(sorted(span(gens)))
# max rank transversal: greedy is exact for matroid-union-type? do exhaustive DFS with pruning (small)
import functools
bestA=0
def dfs(i,basis,r):
    global bestA
    if r+ (n-i) <= bestA: return
    if i==n: bestA=max(bestA,r); return
    for v in cols[i]:
        x=v
        for b in basis: x=min(x,x^b)
        if x: dfs(i+1,basis+[x],r+1); 
    dfs(i+1,basis,r)
dfs(0,[],0)
print('rho_B^net',rB,'rho_A^net',bestA)
# walk decoders
def radoF2(sets):
    best=[0]
    def d(i,basis,r):
        if r+(len(sets)-i)<=best[0]: return
        if i==len(sets): best[0]=max(best[0],r); return
        for v in sets[i]:
            x=v
            for b in basis: x=min(x,x^b)
            if x: d(i+1,basis+[x],r+1)
        d(i+1,basis,r)
    d(0,[],0); return best[0]
rowsW=[sorted(span([sum((net.rb[k][p]*Q[t][p])<<p for p in range(n)) for k in range(m) if net.G[t][k]%4])) for t in range(n)]
colsW=[sorted(span([sum((net.Gb[t][k]*Q[t][p])<<t for t in range(n)) for k in range(m) if net.r4[k][p]])) for p in range(n)]
rowsWs=[sorted(span([sum((net.Fb[k][p]*Q[t][p])<<p for p in range(n)) for k in range(m) if net.u4[t][k]])) for t in range(n)]
colsWs=[sorted(span([sum((net.ub[t][k]*Q[t][p])<<t for t in range(n)) for k in range(m) if net.F[k][p]%4])) for p in range(n)]
print('walk W: rhoB,rhoA',radoF2(rowsW),radoF2(colsW),' backward W*: rhoB,rhoA',radoF2(rowsWs),radoF2(colsWs))
def price(Wc,Vc): 
    Dk=[i for i in range(n) if Wc[i]%4]; Sk=[i for i in range(n) if Vc[i]%4]
    return rk2([[Q[i][j] for j in Sk] for i in Dk]) if Dk and Sk else 0
print('walk W row prices',[price([G[t][k] for t in range(n)],net.r4[k]) for k in range(m)],'W* row prices',[price([net.u4[t][k] for t in range(n)],F[k]) for k in range(m)])
