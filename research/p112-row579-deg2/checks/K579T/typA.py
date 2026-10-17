# impl A: for each fundamental-weight direction h (perp type by |Off|), min over masks (La,Lb) of |Off(h) \ (La u Lb)|.
from base import *
MX=np.load('masks.npy'); MXp=np.packbits(MX,axis=1)  # (NM,15) bytes
v=np.array([1,2,3,5,8,13,21,34.5]); Rp=[r for r in R if np.dot(v,r)>0]
P=[r for r in Rp]; S=set(P)
simple=[r for r in P if not any(tuple(np.subtract(r,q))in S for q in P)]
assert len(simple)==8
B=np.array(simple,float).T
pc8=np.array([bin(i).count('1') for i in range(256)],np.uint8)
for i in range(8):
  off=np.zeros(120,bool)
  for t,l in enumerate(L):
    c=np.linalg.solve(B,np.array(l,float)); off[t]=abs(c[i])>1e-9
  n=off.sum()
  offp=np.packbits(off); best=999
  for a in range(len(MX)):
    Ra=offp&~MXp[a]
    cnt=pc8[Ra[None,:]&~MXp].sum(1,dtype=np.int32).min()
    if cnt<best: best=cnt
  print('|Off|',n,'min leftover',best,flush=True)
