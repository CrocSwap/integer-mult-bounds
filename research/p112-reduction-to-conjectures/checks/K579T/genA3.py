# impl A data: masks (from base), A3 chain Off sets (ip!=0, incl. h), W(D5)=pointwise stabiliser reflections as line perms.
from base import *
MX=np.load('masks.npy')
ch=[R[0]]
while len(ch)<3: ch.append(next(r for r in R if ip(r,ch[-1])==-1 and all(ip(r,c)==0 for c in ch[:-1])))
P=4; pairs=[(a,b) for a in range(P) for b in range(a+1,P)]
offs=[]
for a,b in pairs:
  h=tuple(sum(c[k] for c in ch[a:b]) for k in range(8)); assert ip(h,h)==2
  offs.append([t for t in range(120) if ip(L[t],h)!=0])
D5=[l for l in L if all(ip(l,c)==0 for c in ch)]; print('perp roots',len(D5))
def refl(s,v): k=ip(v,s); return tuple(v[i]-k*s[i] for i in range(8))
perms=[[idx[canon(refl(s,l))] for l in L] for s in D5]
def w(f,bits): v=sum(1<<int(t) for t in bits); f.write('%d %d\n'%(v&((1<<64)-1),v>>64))
with open('a3.txt','w') as f:
  f.write('%d %d %d\n'%(len(pairs),len(MX),len(perms)))
  for o in offs: w(f,o)
  for m in MX: w(f,np.nonzero(m)[0])
  for p in perms: f.write(' '.join(map(str,p))+'\n')
print('off sizes',[len(o) for o in offs])
