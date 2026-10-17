import numpy as np, itertools
from res_setup import *

# labels as bit vectors in F2^9
U=np.array([[ (LAB[t]>>i)&1 for i in range(9)] for t in range(v)])
Bd=np.array([[1 if (t==s or abs(L[t]@L[s])<1e-9) else 0 for s in range(v)] for t in range(v)])
# solve U G U^T = Bd mod 2 for G (9x9) : unknown 81 bits
rows=[];rhs=[]
import random
# use basis of 9 independent labels
def rref2(M):
    M=M.copy()%2; r=0; piv=[]
    for c in range(M.shape[1]-1):
        p=[i for i in range(r,M.shape[0]) if M[i,c]]
        if not p: continue
        M[[r,p[0]]]=M[[p[0],r]]
        for i in range(M.shape[0]):
            if i!=r and M[i,c]: M[i]^=M[r]
        piv.append(c); r+=1
    return M,piv
eq=[]
for t in range(v):
    for s in range(v):
        row=np.outer(U[t],U[s]).reshape(81)
        eq.append(np.concatenate([row,[Bd[t,s]]]))
eq=np.array(eq,dtype=np.int64)
M,piv=rref2(eq)
assert 81 not in piv, 'inconsistent'
G=np.zeros(81,dtype=np.int64)
for i,c in enumerate(piv): G[c]=M[i,81]
G=G.reshape(9,9)
print('free vars',81-len(piv)); print('sym',(G==G.T).all())
# rank of G
def rk2(A):
    M,piv=rref2(np.concatenate([A,np.zeros((A.shape[0],1),dtype=np.int64)],axis=1)); return len(piv)
print('rank G',rk2(G))
Om=lambda x,y: int(x@G@y)%2
# frame classes: functional z (bits) -> vector x with G x = z-bits
def vec_of_functional(zbits):
    zv=np.array([(zbits>>i)&1 for i in range(9)])
    # solve G x = zv
    A=np.concatenate([G,zv.reshape(9,1)],axis=1)%2
    M,piv=rref2(A); assert 9 not in piv
    x=np.zeros(9,dtype=np.int64)
    for i,c in enumerate(piv): x[c]=M[i,9]
    return x
# check functional/orthogonality: O_z membership = Om(u_s, x_z)
for z in [455,379,100,300]:
    x=vec_of_functional(z)
    assert all(Om(U[s],x)==(bin(z&LAB[s]).count('1')&1) for s in range(v))
xf=[vec_of_functional(framez[i][0]) for i in range(8)]
print('Om(x_i,x_j)',[[Om(xf[i],xf[j]) for j in range(8)] for i in range(2)])
print('Om(x_i,x_j) all ==1?', all(Om(xf[i],xf[j])==1 for i in range(8) for j in range(8)))

# lemma test: pairwise non-orth cliques (<=5 lines) ; for every frame j with all lines non-perp f_j : x_j not in span
nonorth=[[1 if (s!=t and abs(L[t]@L[s])>1e-9) else 0 for s in range(v)] for t in range(v)]
import sys
def inspan(vecs,x):
    A=np.array(vecs+[x]).T%2  # 9 x (k+1)
    return rk2(A.T.copy())==rk2(np.array(vecs))
bad=0;tot=0
sys.setrecursionlimit(10000)
def cliques(cur,cand,maxs):
    global bad,tot
    if cur:
        for j in range(8):
            if all(abs(L[t]@F0[j])>1e-9 for t in cur):
                tot+=1
                if inspan([U[t] for t in cur],xf[j]): bad+=1
    if len(cur)==maxs: return
    for i,c in enumerate(cand):
        cliques(cur+[c],[d for d in cand[i+1:] if nonorth[c][d]],maxs)
cliques([],list(range(v)),4)
print('tested',tot,'bad',bad)
