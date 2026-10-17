# impl A extension: A3 survivors (coverable U) -> A4..A7 by appending chain roots (all choices), new seven's flat over all masks,
# keep |U|<=CAP and U coverable by 3 cubes + plane.
import sys, glob, os
from base import *
from cover import cover, pts_of
CAP=int(sys.argv[1]); NOCOV=len(sys.argv)>2; XCAP=int(sys.argv[2]) if NOCOV else CAP
MX=np.load('masks.npy'); NM=len(MX)
W=np.array([1<<i for i in range(64)],dtype=np.uint64)
lo=(MX[:,:64].astype(np.uint64)*W).sum(1).astype(np.uint64); hi=(MX[:,64:].astype(np.uint64)*W[:56]).sum(1).astype(np.uint64)
def m2i(i): return int(lo[i])|(int(hi[i])<<64)
def pcnt(x):  # popcount uint64 array
  x=x-((x>>np.uint64(1))&np.uint64(0x5555555555555555)); x=(x&np.uint64(0x3333333333333333))+((x>>np.uint64(2))&np.uint64(0x3333333333333333))
  x=(x+(x>>np.uint64(4)))&np.uint64(0x0f0f0f0f0f0f0f0f); return (x*np.uint64(0x0101010101010101))>>np.uint64(56)
ch=[R[0]]
while len(ch)<3: ch.append(next(r for r in R if ip(r,ch[-1])==-1 and all(ip(r,c)==0 for c in ch[:-1])))
def offm(h): return sum(1<<t for t in range(120) if ip(L[t],h)!=0)
states=[]
for fn in sorted(glob.glob('surv_%d_*_2.txt'%CAP)):
  for line in open(fn):
    f=line.split(); U=int(f[5])|(int(f[6])<<64)
    if os.environ.get("SIZEONLY") or cover(set(pts_of(U)),3,1): states.append((tuple(ch),[m2i(int(x)) for x in f[:4]],U))
print('A3 coverable states',len(states)); sys.stdout.flush()
FULL=(1<<120)-1
for k in range(4,8):
  new=[]
  for chn,Ls,U in states:
    for c in R:
      if not (ip(c,chn[-1])==-1 and all(ip(c,x)==0 for x in chn[:-1])): continue
      pass
      ch2=chn+(c,)
      D=0
      for a in range(k):
        h=tuple(sum(x[i] for x in ch2[a:]) for i in range(8)); D|=offm(h)&~Ls[a]&FULL
      Dl=np.uint64(D&((1<<64)-1)); Dh=np.uint64(D>>64); Ul=np.uint64(U&((1<<64)-1)); Uh=np.uint64(U>>64)
      cnt=pcnt(Ul|(Dl&~lo))+pcnt(Uh|(Dh&~hi))
      for i in np.nonzero(cnt<=XCAP)[0]:
        Lm=m2i(i); U2=U|(D&~Lm)
        if NOCOV or cover(set(pts_of(U2)),3,1): new.append((ch2,Ls+[Lm],U2))
  states=new
  print('A%d states'%k,len(states),'U sizes',sorted({bin(s[2]).count('1') for s in states})); sys.stdout.flush()
  if NOCOV: break
  if not states: print('KILLED at A%d (cap %d)'%(k,CAP)); break
