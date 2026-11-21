"""SOUND cube for inactive set I (I lexmax in its Aut-orbit, or I=0): base CNF must have NO global d-lex-leader.
Adds units z in I <-> used[z,8], plus the d-vector lex-leader restricted to Stab(I) (perms p with I o p = I).
Soundness: every solution has an image with lexmax inactive set; the stabiliser of I then still acts, so the d-lex-leader over Stab(I) is valid.
usage: mkcube2.py base.cnf mask out.cnf"""
import pickle,sys
base,mask,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
mp=pickle.load(open(base+'.map','rb'))
U=mp['used']; key=(lambda k,i:U[('z',k),i]) if ('z',0) in U or ('z',0,0) in U or any(isinstance(a,tuple) for a in [next(iter(U))[0]]) else None
k0=next(iter(U))[0]
if isinstance(k0,tuple): uz=lambda k,i:U[('z',k),i]
else: uz=lambda k,i:U[k,i]
P=[tuple(p) for p in pickle.load(open('../tight55/perms.pkl','rb'))]
ind=[mask>>j&1 for j in range(16)]
stab=[p for p in P if all(ind[p[j]]==ind[j] for j in range(16)) and any(p[j]!=j for j in range(16))]
with open(base) as fh: hdr=fh.readline().split(); body=fh.read()
nv=int(hdr[2]); cls=[]
def new():
    global nv; nv+=1; return nv
for z in range(16): cls.append([uz(z,8)] if ind[z] else [-uz(z,8)])
import os
# EXTRA: semicolon-separated clauses over 'u<z>_<i>' tokens (used[z,i]) with optional '-' prefix, e.g. "u0_7;-u0_8"
for c in os.environ.get('EXTRA','').split(';'):
    if not c: continue
    lits=[]
    for tok in c.split(','):
        neg=tok.startswith('-'); tok=tok.lstrip('-'); z,i=tok[1:].split('_')
        lits.append(-uz(int(z),int(i)) if neg else uz(int(z),int(i)))
    cls.append(lits)
for p in stab:
    prev=None
    for j in range(16):
        if p[j]==j: continue
        e=new(); pre=[] if prev is None else [-prev]
        for v in range(9): cls.append(pre+[-uz(p[j],v),uz(j,v)])
        ss=[]
        for v in range(9):
            sv=new(); ss.append(sv); cls.append([-sv,uz(j,v)]); cls.append([-sv,-uz(p[j],v)])
        cls.append(pre+[e]+ss); prev=e
with open(out,'w') as fh:
    fh.write(f'p cnf {nv} {int(hdr[3])+len(cls)}\n'); fh.write(body.rstrip('\n')+'\n')
    for c in cls: fh.write(' '.join(map(str,c))+' 0\n')
print('stab size',len(stab)+1)
