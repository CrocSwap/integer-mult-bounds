"""F2-REL with 16 tight slots + J generic loose slots (variable f_j in F2^8 \\ (0 u Zbar16)) + exemptions.
Equivalent to F2-REL (255 slots) at budget B <= 55 because (R1) rows merge per f and (R2) every loose row can be assumed
efficient (|D| >= dim U + 1, hence dim U >= 3, price >= 3), so at most floor(B/3) loose rows: J = 18 suffices for B <= 55.
WLOG constraints added: active generic slot has dim U >= 3 and #ports in U >= dim U + 1; active slots first, f strictly increasing.
usage: f2gen.py B J out.cnf  [env SYM=1 tight lex-leader; FORCEJ=k forces >= k generic slots active (controls)]"""
import sys,os,pickle
sys.path.insert(0,'../nonlin'); sys.path.insert(0,'../linear56')
from ncore import *
B=int(sys.argv[1]); J=int(sys.argv[2]); out=sys.argv[3]; SYM=int(os.environ.get('SYM','0')); FORCEJ=int(os.environ.get('FORCEJ','0'))
TMP=out+'.body'; fh=open(TMP,'w'); ncl=0; nv=0
def new():
    global nv; nv+=1; return nv
def add(c):
    global ncl; ncl+=1; fh.write(' '.join(map(str,c))+' 0\n')
vec=lambda v: int(sum(int(v[i])<<i for i in range(len(v))))
cb=[vec(Cb[t]) for t in range(n)]; zb=[vec(Zb[k]) for k in range(16)]
dot=lambda a,b: bin(a&b).count('1')&1
SL=[('z',k) for k in range(16)]+[('g',j) for j in range(J)]
f={}; used={}; L={}
for s in SL:
    for i in range(9):
        used[s,i]=new()
        for c in range(9): f[s,i,c]=new(); L[s,i,c]=new()
for s in SL:
    for i in range(9):
        u=used[s,i]
        if i>0: add([-u,used[s,i-1]])
        for c in range(9): add([u,-f[s,i,c]]); add([u,-L[s,i,c]])
        add([-u]+[L[s,i,c] for c in range(9)])
        for c in range(9):
            for c2 in range(c+1,9): add([-L[s,i,c],-L[s,i,c2]])
            add([-L[s,i,c],f[s,i,c]])
            for c2 in range(c): add([-L[s,i,c],-f[s,i,c2]])
            for i2 in range(9):
                if i2!=i: add([-L[s,i,c],-f[s,i2,c]])
            if i<8:
                for c2 in range(c+1): add([-L[s,i,c],-L[s,i+1,c2]])
def xorvar(lits):
    if len(lits)==1: return lits[0]
    a=lits[0]
    for b in lits[1:]:
        p=new(); add([-p,a,b]); add([-p,-a,-b]); add([p,-a,b]); add([p,a,-b]); a=p
    return a
hv=[list(map(int,H[t])) for t in range(n)]
m={}
for s in SL:
    for t in range(n):
        m[s,t]=new(); sup=[c for c in range(9) if hv[t][c]]
        for i in range(9): add([-m[s,t],-xorvar([f[s,i,c] for c in sup])])
nin={}
for k in range(16):
    s=('z',k); nz=np.concatenate([[1],Zb[k]]); sup=[c for c in range(9) if nz[c]]
    nin[k]=new()
    for i in range(9): add([-nin[k],-xorvar([f[s,i,c] for c in sup])])
    add([-used[s,7],used[s,8],-nin[k]])
ex={t:new() for t in range(n)}
# generic generators
F={(j,i):new() for j in range(J) for i in range(8)}
act={j:-used[('g',j),8] for j in range(J)}       # active <=> U != 0
for j in range(J):
    a=act[j]
    for i in range(8): add([a,-F[j,i]])            # inactive -> f=0
    add([-a]+[F[j,i] for i in range(8)])           # active -> f != 0
    for z in zb:                                    # f not in Zbar16
        add([-a]+[(-F[j,i] if (z>>i)&1 else F[j,i]) for i in range(8)])
    add([-a,-used[('g',j),6]])                       # dim U >= 3
    if j+1<J:
        add([-act[j+1],a])
        # f_j < f_{j+1} as 8-bit numbers (bit 7 most significant), when j+1 active
        x=[F[j,i] for i in range(8)]; y=[F[j+1,i] for i in range(8)]
        eq=None
        for i in range(7,-1,-1):
            pre=[-act[j+1]]+([] if eq is None else [-eq])
            add(pre+[-x[i],y[i]])                   # equal-so-far -> x_i <= y_i
            e2=new()                                # e2 -> equal so far incl bit i
            if eq is not None: add([-e2,eq])
            add([-e2,-x[i],y[i]]); add([-e2,x[i],-y[i]])
            # if equal-so-far and x_i==y_i then e2 (so strictness is enforced at the end)
            add(pre+[x[i],y[i],e2]); add(pre+[-x[i],-y[i],e2])
            eq=e2
        add([-act[j+1],-eq])                        # not all equal
# efficiency: #ports in U_j >= dim U_j + 1  (totalizer outputs o_r -> >= r)
def tot(ls):
    if len(ls)==1: return [ls[0]]
    h=len(ls)//2; a=tot(ls[:h]); b=tot(ls[h:]); o=[new() for _ in range(len(ls))]
    p=len(a); q=len(b)
    for i in range(p+1):
        for j2 in range(q+1):
            k=i+j2+1
            if k>p+q: continue
            c=[-o[k-1]]
            if i<p: c.append(a[i])
            if j2<q: c.append(b[j2])
            add(c)
    return o
for j in range(J):
    s=('g',j); o=tot([m[s,t] for t in range(n)])
    for k in range(9):            # ~used[s,k] => #used<=k => dim>=9-k => need >= 10-k ports
        add([used[s,k],o[10-k-1]])
# port coverage (mod 2): for every phi with phi(c_t)=1
X={(j,phi):xorvar([F[j,i] for i in range(8) if (phi>>i)&1]) for j in range(J) for phi in range(1,256)}
for t in range(n):
    for phi in range(1,256):
        if not dot(phi,cb[t]): continue
        cl=[m[('z',k),t] for k in range(16) if dot(phi,zb[k])]+[ex[t]]
        for j in range(J):
            g=new(); add([-g,m[('g',j),t]]); add([-g,X[j,phi]]); cl.append(g)
        add(cl)
# cost <= B : #(~used) + #(~nin) + #ex <= B+16
lits=[-used[s,i] for s in SL for i in range(9)]+[-nin[k] for k in range(16)]+[ex[t] for t in range(n)]
K=B+16
sq=[[new() for _ in range(K)] for _ in range(len(lits))]
for i,x in enumerate(lits):
    add([-x,sq[i][0]])
    if i>0:
        for j2 in range(K): add([-sq[i-1][j2],sq[i][j2]])
        for j2 in range(1,K): add([-x,-sq[i-1][j2-1],sq[i][j2]])
        add([-x,-sq[i-1][K-1]])
if FORCEJ:
    for j in range(FORCEJ): add([act[j]])
if SYM:
    PERMS=pickle.load(open('../tight55/perms.pkl','rb'))
    for p in PERMS:
        if all(p[j2]==j2 for j2 in range(16)): continue
        prev=None
        for j2 in range(16):
            if p[j2]==j2: continue
            e=new(); pre=[] if prev is None else [-prev]
            for v in range(9): add(pre+[-used[('z',p[j2]),v],used[('z',j2),v]])
            ss=[]
            for v in range(9):
                sv=new(); ss.append(sv); add([-sv,used[('z',j2),v]]); add([-sv,-used[('z',p[j2]),v]])
            add(pre+[e]+ss); prev=e
fh.close()
with open(out,'w') as o:
    o.write(f'p cnf {nv} {ncl}\n')
    with open(TMP) as i:
        for line in i: o.write(line)
os.remove(TMP)
pickle.dump({'f':f,'used':used,'m':m,'nin':nin,'ex':ex,'F':F,'J':J},open(out+'.map','wb'))
print('vars',nv,'clauses',ncl)
