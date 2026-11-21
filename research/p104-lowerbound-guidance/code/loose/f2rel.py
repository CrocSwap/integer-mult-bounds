"""F2-REL SAT (relaxation of the WHOLE B-linear class, any y, incl. loose):
rows f in F2^8\\0 (f = ybar), subspace U_f of F2^9 (RREF of U^perp, as in zsat), port t usable on f iff h_t in U_f.
Port t: cbar_t in span_F2{f : h_t in U_f} or exempt (singleton row, price 1).  [mod-2 image of the Z4 condition]
price_f = dim U_f - [f in Zbar16 and (1,f) in U_f]   (<= true price of any row with ybar=f; 2e rows (ybar=0) dropped: price>=0)
Constraint sum price + #ex <= B. Clauses: for every functional phi (plain dot) with phi(cbar_t)=1: OR_{f: phi(f)=1} m[f,t] OR ex[t].
usage: f2rel.py B out.cnf [SYM=1]  (streams clauses)"""
import sys,os,pickle
sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
from ncore import *
B=int(sys.argv[1]); out=sys.argv[2]; SYM=int(os.environ.get('SYM','0'))
TMP=out+'.body'; fh=open(TMP,'w'); ncl=0; nv=0
def new():
    global nv; nv+=1; return nv
def add(c):
    global ncl; ncl+=1; fh.write(' '.join(map(str,c))+' 0\n')
vec=lambda v: int(sum(int(v[i])<<i for i in range(len(v))))
cb=[vec(Cb[t]) for t in range(n)]; zb=[vec(Zb[k]) for k in range(16)]
FS=list(range(1,256)); tight={zb[k]:k for k in range(16)}
f={}; used={}; L={}
for g in FS:
    for i in range(9):
        used[g,i]=new()
        for c in range(9): f[g,i,c]=new(); L[g,i,c]=new()
for g in FS:
    for i in range(9):
        u=used[g,i]
        if i>0: add([-u,used[g,i-1]])
        for c in range(9): add([u,-f[g,i,c]]); add([u,-L[g,i,c]])
        add([-u]+[L[g,i,c] for c in range(9)])
        for c in range(9):
            for c2 in range(c+1,9): add([-L[g,i,c],-L[g,i,c2]])
            add([-L[g,i,c],f[g,i,c]])
            for c2 in range(c): add([-L[g,i,c],-f[g,i,c2]])
            for i2 in range(9):
                if i2!=i: add([-L[g,i,c],-f[g,i2,c]])
            if i<8:
                for c2 in range(c+1): add([-L[g,i,c],-L[g,i+1,c2]])
def xorvar(lits):
    if len(lits)==1: return lits[0]
    a=lits[0]
    for b in lits[1:]:
        p=new(); add([-p,a,b]); add([-p,-a,-b]); add([p,-a,b]); add([p,a,-b]); a=p
    return a
hv=[list(map(int,H[t])) for t in range(n)]
m={}
for g in FS:
    for t in range(n):
        m[g,t]=new(); sup=[c for c in range(9) if hv[t][c]]
        for i in range(9): add([-m[g,t],-xorvar([f[g,i,c] for c in sup])])
nin={}
for g in tight:
    nz=[1]+[(g>>i)&1 for i in range(8)]; sup=[c for c in range(9) if nz[c]]
    nin[g]=new()
    for i in range(9): add([-nin[g],-xorvar([f[g,i,c] for c in sup])])
    add([-used[g,7],used[g,8],-nin[g]])   # normalization: U=<n> (price 0) -> U=0
ex={t:new() for t in range(n)}
dot=lambda a,b: bin(a&b).count('1')&1
for t in range(n):
    for phi in range(1,256):
        if dot(phi,cb[t]): add([m[g,t] for g in FS if dot(phi,g)]+[ex[t]])
# cost: sum_g (#unused rows) - sum nin + #ex <= B  <=>  #(~used) + #(~nin) + #ex <= B+16
lits=[-used[g,i] for g in FS for i in range(9)]+[-nin[g] for g in tight]+[ex[t] for t in range(n)]
K=B+16
# sequential counter at-most-K (Sinz)
s=[[new() for j in range(K)] for i in range(len(lits))]
for i,x in enumerate(lits):
    add([-x,s[i][0]])
    if i>0:
        for j in range(K): add([-s[i-1][j],s[i][j]])
        for j in range(1,K): add([-x,-s[i-1][j-1],s[i][j]])
        add([-x,-s[i-1][K-1]])
if SYM:
    PERMS=pickle.load(open('f2perms.pkl','rb'))   # list of dicts g->g' on FS
    for p in PERMS:
        if all(p[g]==g for g in FS): continue
        prev=None
        for g in FS:
            if p[g]==g: continue
            e=new(); pre=[] if prev is None else [-prev]
            for v in range(9): add(pre+[-used[p[g],v],used[g,v]])
            ss=[]
            for v in range(9):
                sv=new(); ss.append(sv); add([-sv,used[g,v]]); add([-sv,-used[p[g],v]])
            add(pre+[e]+ss); prev=e
fh.close()
with open(out,'w') as o:
    o.write(f'p cnf {nv} {ncl}\n')
    with open(TMP) as i:
        for line in i: o.write(line)
os.remove(TMP)
pickle.dump({'f':f,'used':used,'m':m,'nin':nin,'ex':ex},open(out+'.map','wb'))
print('vars',nv,'clauses',ncl)
