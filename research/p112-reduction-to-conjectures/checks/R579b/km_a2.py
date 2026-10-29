# impl A (K5^- kill): 4 sevens with A3 pattern (K579T A3 states, |U|<=CAP) + 5th seven k whose pairs to 3 of them are ROOTS and to the 4th (m) a NON-ROOT.
# Rigidity (root triangles through k) => u_a - u_k = s_a + x are roots (a != m) in the chain scaling; h_mk = s_m + x (norm 4 or 6).
import sys, glob, os
sys.path.insert(0,'../K579T'); os.chdir('../K579T')
from base import *
CAP=int(sys.argv[1]); NNR=int(sys.argv[2]) if len(sys.argv)>2 else 1
MX=np.load('masks.npy'); NM=len(MX)
W=np.array([1<<i for i in range(64)],dtype=np.uint64)
lo=(MX[:,:64].astype(np.uint64)*W).sum(1).astype(np.uint64); hi=(MX[:,64:].astype(np.uint64)*W[:56]).sum(1).astype(np.uint64)
def m2i(i): return int(lo[i])|(int(hi[i])<<64)
def pcnt(x):
  x=x-((x>>np.uint64(1))&np.uint64(0x5555555555555555)); x=(x&np.uint64(0x3333333333333333))+((x>>np.uint64(2))&np.uint64(0x3333333333333333))
  x=(x+(x>>np.uint64(4)))&np.uint64(0x0f0f0f0f0f0f0f0f); return (x*np.uint64(0x0101010101010101))>>np.uint64(56)
ch=[R[0]]
while len(ch)<3: ch.append(next(r for r in R if ip(r,ch[-1])==-1 and all(ip(r,c)==0 for c in ch[:-1])))
def add(*vs): return tuple(sum(v[i] for v in vs) for i in range(8))
def neg(v): return tuple(-a for a in v)
Z8=(0,)*8
s=[add(*ch[a:]) if a<3 else Z8 for a in range(4)]   # u_a - u_3
Rset=set(R)|{neg(r) for r in R}
def offm(h): return sum(1<<t for t in range(120) if ip(L[t],h)!=0)
ext=set()
for r in Rset:
  for a0 in range(4):
    x=add(r,neg(s[a0]))
    nr=[a for a in range(4) if add(s[a],x) not in Rset]
    def bad(h): return ip(h,h)==0 or any(add(h,neg(add(q,q)))==Z8 for q in Rset)
    if len(nr)==NNR and not any(bad(add(s[a],x)) for a in nr): ext.add((x,tuple(nr),max(ip(add(s[a],x),add(s[a],x)) for a in nr)))
print('A3 + K5^- extensions (x,m):',len(ext),'norms',sorted({e[2] for e in ext})); sys.stdout.flush()
states=[]
for fn in sorted(glob.glob('surv_28_*_2.txt')):
  for line in open(fn):
    f=line.split(); U=int(f[5])|(int(f[6])<<64); states.append(([m2i(int(q)) for q in f[:4]],U))
print('A3 states',len(states))
FULL=(1<<120)-1; tot=0; best=999; per={}
for Ls,U in states:
  for x,m,n in ext:
    D=0
    for a in range(4): D|=offm(add(s[a],x))&~Ls[a]&FULL
    Dl=np.uint64(D&((1<<64)-1)); Dh=np.uint64(D>>64); Ul=np.uint64(U&((1<<64)-1)); Uh=np.uint64(U>>64)
    cnt=pcnt(Ul|(Dl&~lo))+pcnt(Uh|(Dh&~hi)); c=int(cnt.min()); best=min(best,c); per[n]=min(per.get(n,999),c)
    tot+=int((cnt<=CAP).sum())
print('K5^- solutions with |U|<=%d: %d ; min |U| %d ; min by norm of h_mk %s'%(CAP,tot,best,per))
