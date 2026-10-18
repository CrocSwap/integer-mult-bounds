"""Case-B census: S with |S| <= P, every root g has q_g = |S cap g^perp| >= QB, and at least NQ roots with d >= 3.
Kernels: with q_g >= QB, |S cap N(g)| <= P - QB; only d>=3 kernels of size <= P-QB can fit (3-dim Z kernels: sizes 37,41,44,...).
WLOG (W transitive on roots, Stab(0) transitive on root-0 kernels of each listed class) root 0 in Q with kernel = a fixed class rep.
Usage: censusB.py P QB NQ   -> cnf/cB_P_QB_NQ.cnf ; kissat + drat-trim."""
import sys, pickle, subprocess, os; os.chdir('/Users/mason/repo_clones/intmult-work/cards/PUNCTTHEORY'); sys.path.insert(0,'.')
from anal import *
from pysat.card import CardEnc, EncType
P,QB,NQ=map(int,sys.argv[1:4]); FIX=len(sys.argv)>4
KER=[k for k in pickle.load(open('ker3_51.pkl','rb')) if bin(k).count('1')<=P-QB]
assert P-QB<=51
sizes=sorted(set(bin(k).count('1') for k in KER)); print('root-0 d>=3 kernels fitting:',len(KER),'sizes',sizes,flush=True)
# transporters 0 -> g
def refl_perm(b):
    rb=L[b]; Pp=[]
    for t in range(NL):
        v=L[t]-G[t,b]*rb
        Pp.append(next(s for s in range(NL) if (L[s]==v).all() or (L[s]==-v).all()))
    return Pp
from collections import deque
perms={r:refl_perm(r) for r in range(NL)}
prev={0:None}; dq=deque([0])
while dq:
    u=dq.popleft()
    for r in range(NL):
        w=perms[r][u]
        if w not in prev: prev[w]=(u,r); dq.append(w)
def transporter(b):
    path=[]; w=b
    while prev[w]: u,r=prev[w]; path.append(r); w=u
    Pp=list(range(NL))
    for r in reversed(path): Pp=[perms[r][Pp[t]] for t in range(NL)]
    assert Pp[0]==b; return Pp
nv=120
card=CardEnc.atmost(lits=list(range(1,121)),bound=P,top_id=nv,encoding=EncType.seqcounter); cls=list(card.clauses); nv=card.nv
for g in range(NL):
    c=CardEnc.atleast(lits=[t+1 for t in ORTH[g]],bound=QB,top_id=nv,encoding=EncType.seqcounter); cls+=c.clauses; nv=max(nv,c.nv)
ys=[]
# kernel classes of root 0 among fitting kernels: we fix root 0's kernel to each class rep in turn? simpler: root 0 in Q via OR over its kernels
# (no symmetry breaking on the kernel; root 0 fixed in Q by W-transitivity)
for g in range(NL):
    Pp=transporter(g) if g else list(range(NL))
    nv+=1; y=nv; ys.append(y); head=[-y]
    for k in KER:
        nv+=1; z=nv; head.append(z)
        for t in bits(k): cls.append([-z,Pp[t]+1])
    cls.append(head)
cls.append([ys[0]])
if FIX:
    for t in bits(KER[0]): cls.append([t+1])
c=CardEnc.atleast(lits=ys,bound=NQ,top_id=nv,encoding=EncType.seqcounter); cls+=c.clauses; nv=max(nv,c.nv)
fn=f'cnf/cB3_{P}_{QB}_{NQ}.cnf'
with open(fn,'w') as f:
    f.write(f'p cnf {nv} {len(cls)}\n'); [f.write(' '.join(map(str,x))+' 0\n') for x in cls]
print('vars',nv,'clauses',len(cls),flush=True)
DT='/Users/mason/repo_clones/intmult-work/tmp_dratchk/drat-trim/drat-trim'
import time
res={}
for b in range(1,NL):
    fb=fn[:-4]+f'_b{b}.cnf'
    with open(fb,'w') as f:
        f.write(f'p cnf {nv} {len(cls)+1}\n'); [f.write(' '.join(map(str,x))+' 0\n') for x in cls]; f.write(f'{ys[b]} 0\n')
    t0=time.time()
    r=subprocess.run(['kissat','-q','--no-binary',fb,fb[:-4]+'.drat'],capture_output=True,text=True)
    st={10:'SAT',20:'UNSAT'}.get(r.returncode,str(r.returncode)); ver=''
    if st=='UNSAT':
        v=subprocess.run([DT,fb,fb[:-4]+'.drat'],capture_output=True,text=True)
        ver='VERIFIED' if 's VERIFIED' in v.stdout else 'NOT-VERIFIED'
    os.remove(fb); 
    if os.path.exists(fb[:-4]+'.drat'): os.remove(fb[:-4]+'.drat')
    print('cube b',b,st,ver,'%.1fs'%(time.time()-t0),flush=True)
    if st=='SAT':
        sol=set(int(x) for l in r.stdout.split('\n') if l.startswith('v') for x in l.split()[1:])
        print('S',[t for t in range(NL) if (t+1) in sol]); break
