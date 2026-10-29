# impl B (independent): CNF for the p=3 (A2) relaxed pair-cover problem, own E8 build/basis/labels, solved by kissat.
import itertools, sys, subprocess
from fractions import Fraction as Fr
nx=int(sys.argv[1]); x1=int(sys.argv[2]); P=int(sys.argv[3]); TAG=sys.argv[4]; FREE=int(sys.argv[5]) if len(sys.argv)>5 else -1   # nx = number of functionals defining X (3 -> rank 6, 2 -> rank 7); x1 = one extra free line
R=[]
for i,j in itertools.combinations(range(8),2):
    for s in (1,-1):
        for u in (1,-1):
            v=[0]*8; v[i]=s; v[j]=u; R.append(tuple(2*x for x in v))   # doubled coords
for sg in itertools.product((1,-1),repeat=8):
    if sg.count(-1)%2==0: R.append(sg)
def canon(v):
    for x in v:
        if x: return v if x>0 else tuple(-y for y in v)
L=sorted({canon(r) for r in R}); n=len(L); assert n==120
ipf=lambda a,b: sum(x*y for x,y in zip(a,b))//4
S=[(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)][::-1]
def coords(v):   # solve sum c_i S_i = v exactly (gauss)
    M=[[Fr(S[j][i]) for j in range(8)]+[Fr(v[i])] for i in range(8)]
    for c in range(8):
        p=next(r for r in range(c,8) if M[r][c]!=0); M[c],M[p]=M[p],M[c]
        M[c]=[x/M[c][c] for x in M[c]]
        for r in range(8):
            if r!=c and M[r][c]!=0: M[r]=[x-M[r][c]*y for x,y in zip(M[r],M[c])]
    return [M[i][8] for i in range(8)]
lab=[]
for l in L:
    ci=coords(l); assert all(x.denominator==1 for x in ci)
    lab.append([1]+[int(x)%2 for x in ci])

ch=[R[0]]
while len(ch)<P-1:
    ch.append(next(r for r in R if ipf(r,ch[-1])==-1 and all(ipf(r,c)==0 for c in ch[:-1])))
def hh(a,b):
    v=[0]*8
    for c in ch[a:b]: v=[x+y for x,y in zip(v,c)]
    return tuple(v)
pairs=[(a,b) for a in range(P) for b in range(a+1,P)]
root=[L.index(canon(hh(a,b))) for a,b in pairs]
nv=0; cl=[]
def new():
    global nv; nv+=1; return nv
def xorvar(bits):   # returns var equal to xor of list of vars (Tseitin chain)
    cur=bits[0]
    for b in bits[1:]:
        z=new(); cl.extend([[-z,cur,b],[-z,-cur,-b],[z,-cur,b],[z,cur,-b]]); cur=z
    return cur
def functional(): return [new() for _ in range(9)]
def nonzero(f): cl.append(list(f))
def indep(fs):
    for m in range(1,1<<len(fs)):
        sub=[fs[i] for i in range(len(fs)) if m>>i&1]
        if len(sub)==1: nonzero(sub[0]); continue
        zs=[xorvar([f[k] for f in sub]) for k in range(9)]
        cl.append(zs)
def sval(f,t):  # var = f . lab_t
    bits=[f[k] for k in range(9) if lab[t][k]]
    return xorvar(bits)
c=[[new() for t in range(n)] for a in range(P)]; FS=[]
for a in range(P):
    fs=[functional(),functional()]; indep(fs); FS.append(fs)
    for t in range(n):
        for f in fs: cl.append([-c[a][t],-sval(f,t)])
gs=[functional() for _ in range(nx)]; indep(gs)
e=[new() for t in range(n)]
free=[new() for t in range(n)]
for t in range(n):
    for g in gs: cl.append([-e[t],free[t],-sval(g,t)])
if x1:
    for t in range(n):
        for u in range(t+1,n): cl.append([-free[t],-free[u]])
else:
    for t in range(n): cl.append([-free[t]])
# coverage: for pair (a,b), t in Off(root_ab): e_t or c_a,t or c_b,t
for (a,b),r in zip(pairs,root):
    for t in range(n):
        if ipf(L[t],L[r])!=0: cl.append([e[t],c[a][t],c[b][t]])
if FREE>=0: cl.append([free[FREE]])
fn=sys.argv[6]
with open(fn,'w') as f:
    f.write('p cnf %d %d\n'%(nv,len(cl)))
    for c_ in cl: f.write(' '.join(map(str,c_))+' 0\n')
sys.exit(0)
