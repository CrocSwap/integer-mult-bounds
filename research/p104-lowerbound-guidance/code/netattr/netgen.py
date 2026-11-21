# random legal NetW (own code, mirrors net2dec conventions): nodes (a,b), b<=a; F_kp!=0 only if q_p in a_k;
# G_tk!=0 only if q_t in b_k^perp; relay H_kj (j<k) only if b_j <= a_k. M = G (I-H)^{-1} F over Z.
import random
from common import *
def rand_sub(h,dim,inside=None):
    base=list(range(1<<h)) if inside is None else sorted(inside)
    if dim==0: return frozenset({0})
    while True:
        S=span([random.choice(base) for _ in range(dim)])
        if len(S)==1<<dim: return S
def matmul(X,Y): return [[sum(X[i][k]*Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
def net_M(G,H,F):
    m=len(H); N=[[int(i==j) for j in range(m)] for i in range(m)]; P=[r[:] for r in N]
    for _ in range(m):
        P=matmul(P,H); N=[[N[i][j]+P[i][j] for j in range(m)] for i in range(m)]
    return matmul(matmul(G,N),F),N
def rand_net(h,labs,nodes,edges,dens=.6,vals=(1,2,3,-1,-2)):
    n=len(labs); m=len(nodes)
    F=[[0]*n for _ in range(m)]; G=[[0]*m for _ in range(n)]; H=[[0]*m for _ in range(m)]
    for k,(a,b) in enumerate(nodes):
        for p,q in enumerate(labs):
            if q in a and random.random()<dens: F[k][p]=random.choice(vals)
            if all(dot(q,y)==0 for y in b) and random.random()<dens: G[p][k]=random.choice(vals)
    for (j,k) in edges:
        assert nodes[j][1]<=nodes[k][0]; H[k][j]=random.choice(vals)
    return F,G,H
