"""LOOSE esat.py: TIGHT55 encoding + per-port exemption e_t (singleton loose row, price 1).
CNF: tight B-linear class (rows z in Z16, v_z = C G z), A-side free. Row z has A-span U_z (subspace of F2^9),
encoded by RREF basis of U_z^perp (<=9 rows, used flags). Port t may use z iff h_t in U_z. Covering clauses from zclauses.pkl
(= exact decodability, cross-checked vs brute force). price_z = dim U_z - [n_z in U_z], n_z = (1,z).
Constraint: sum_z price_z <= B  <=>  sum_z (u_z + nin_z) >= 144 - B.  Optional: fix rows (unit clauses) for controls."""
import sys,os
sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
from ncore import *
import pickle,sys
CL=pickle.load(open(os.environ.get('CLF','../nonlin/zclauses.pkl'),'rb'))
B=int(sys.argv[1]); out=sys.argv[2]; fix=sys.argv[3] if len(sys.argv)>3 else None
nv=0; cls=[]
def new():
    global nv; nv+=1; return nv
f={}; used={}; L={}
for z in range(16):
    for i in range(9):
        used[z,i]=new()
        for c in range(9): f[z,i,c]=new(); L[z,i,c]=new()
for z in range(16):
    for i in range(9):
        u=used[z,i]
        if i>0: cls.append([-u,used[z,i-1]])
        for c in range(9): cls.append([u,-f[z,i,c]]); cls.append([u,-L[z,i,c]])
        cls.append([-u]+[L[z,i,c] for c in range(9)])
        for c in range(9):
            for c2 in range(c+1,9): cls.append([-L[z,i,c],-L[z,i,c2]])
            cls.append([-L[z,i,c],f[z,i,c]])
            for c2 in range(c): cls.append([-L[z,i,c],-f[z,i,c2]])
            for i2 in range(9):
                if i2!=i: cls.append([-L[z,i,c],-f[z,i2,c]])
            if i<8:
                for c2 in range(c+1): cls.append([-L[z,i,c],-L[z,i+1,c2]])
def xorvar(lits):
    """var p with p <-> XOR(lits)"""
    if len(lits)==1: return lits[0]
    a=lits[0]
    for b in lits[1:]:
        p=new()
        cls.extend([[-p,a,b],[-p,-a,-b],[p,-a,b],[p,a,-b]]); a=p
    return a
hv=[list(map(int,H[t])) for t in range(n)]
m={}
for z in range(16):
    for t in range(n):
        m[z,t]=new()
        sup=[c for c in range(9) if hv[t][c]]
        for i in range(9):
            p=xorvar([f[z,i,c] for c in sup]); cls.append([-m[z,t],-p])
nin={}
for z in range(16):
    nz=np.concatenate([[1],Zb[z]]); sup=[c for c in range(9) if nz[c]]
    nin[z]=new()
    for i in range(9):
        p=xorvar([f[z,i,c] for c in sup]); cls.append([-nin[z],-p])
ex={t:new() for t in range(n)}   # port t exempt = covered by a singleton loose row y=G c_t (price 1)
for t in range(n):
    for r in CL[t]:
        cls.append([m[z,t] for z in range(16) if r>>z&1]+[ex[t]])
# normalization (TIGHT55): price-0 row U=<n_z> -> U=0
for z in range(16): cls.append([-used[z,7],used[z,8],-nin[z]])
# cardinality: at least K of lits true  (totalizer, upward outputs needed: we need outputs r_j true => at least j inputs true)
lits=[used[z,i] for z in range(16) for i in range(9)]+[nin[z] for z in range(16)]+[-ex[t] for t in range(n)]
K=248-B   # sum_z price_z + #exempt <= B
def tot(ls):
    """returns list o[1..len] with o_j -> (at least j of ls true)  (downward direction only)"""
    if len(ls)==1: return [ls[0]]
    h=len(ls)//2; a=tot(ls[:h]); b=tot(ls[h:]); o=[new() for _ in range(len(ls))]
    # o_k -> exists i+j=k with a_i and b_j  : encode as  o_k -> a_i or b_{k-i}  for all splits (standard: ~a_i & ~b_j -> ~o_{i+j-1}... use
    # clause form: for i in 0..p, j in 0..q with i+j=k-1+1: (~o_{i+j+1}) or a_{i+1} or b_{j+1}
    p=len(a); q=len(b)
    for i in range(p+1):
        for j in range(q+1):
            k=i+j+1
            if k>p+q: continue
            c=[-o[k-1]]
            if i<p: c.append(a[i])
            if j<q: c.append(b[j])
            cls.append(c)
    return o
if K>0:
    o=tot(lits); cls.append([o[K-1]])
EFF=int(__import__('os').environ.get('EFF','0'))
if EFF:
    # WLOG (R2): an active tight row has #ports in U_z >= price_z + 1, price = (9-#used) - nin
    for z in range(16):
        o=tot([m[z,t] for t in range(n)])
        for k in range(9):
            cls.append([used[z,k],nin[z],o[10-k-1]])
            if 9-k>=1: cls.append([used[z,k],-nin[z],o[9-k-1]])
SYM=int(__import__('os').environ.get('SYM','0'))

PERMS=pickle.load(open('../tight55/perms.pkl','rb'))
if SYM:
  for p in PERMS:
    if all(p[j]==j for j in range(16)): continue
    prev=None
    for j in range(16):
        if p[j]==j: continue
        e=new()
        pre=[] if prev is None else [-prev]
        for v in range(9):
            cls.append(pre+[-used[p[j],v],used[j,v]])
        ss=[]
        for v in range(9):
            sv=new(); ss.append(sv); cls.append([-sv,used[j,v]]); cls.append([-sv,-used[p[j],v]])
        cls.append(pre+[e]+ss)
        prev=e
if fix:
    Kt=pickle.load(open(fix,'rb'))
    # control: force each port to be allowed on the rows E8 uses (m true)
    for t in range(n):
        for z in range(16):
            if Kt[t]>>z&1: cls.append([m[z,t]])
with open(out,'w') as fh:
    fh.write(f'p cnf {nv} {len(cls)}\n')
    for c in cls: fh.write(' '.join(map(str,c))+' 0\n')
print('vars',nv,'clauses',len(cls))
pickle.dump({'f':f,'used':used,'m':m,'nin':nin,'ex':ex},open(out+'.map','wb'))
