from itertools import product
R=4; D=3; n=R*D
I2=((1,0),(0,1)); Z=(0,0)
def mul(f,g):
 A,b=f; C,d=g
 return (tuple(tuple(sum(A[i][k]*C[k][j] for k in range(2))%2 for j in range(2)) for i in range(2)),tuple((sum(A[i][k]*d[k] for k in range(2))+b[i])%2 for i in range(2)))
def act(f,p):
 A,b=f
 q=tuple(sum(A[i][j]*p[j] for j in range(2))%2 for i in range(2))
 return tuple((q[i]+b[i])%2 for i in range(2))
a=(((1,1),(0,1)),Z); b=(((1,0),(1,1)),Z); tx=(I2,(1,0)); ty=(I2,(0,1))
def prod(*fs):
 z=(I2,Z)
 for f in fs:z=mul(z,f)
 return z
def hom(f):
 A,b=f; return tuple((sum(A[i][j]<<j for j in range(2)) | (b[i]<<2)) for i in range(2))+(4,)
# rows of affine homogeneous 3x3 over F2

def matmul3(A,B):return tuple(sum(((((A[i]>>k)&1)&((B[k]>>j)&1))<<j) for k in range(3)) for i in range(3))
def gmat(f):
 rows=hom(f); return rows
def xor(a,b):return tuple(x^y for x,y in zip(a,b))
def mat_rank(rows):
 rows=list(rows); r=0
 for col in range(n):
  p=next((i for i in range(r,n) if (rows[i]>>col)&1),None)
  if p is None:continue
  rows[r],rows[p]=rows[p],rows[r]
  for i in range(n):
   if i!=r and ((rows[i]>>col)&1):rows[i]^=rows[r]
  r+=1
 return r
# affine homogeneous blocks
letters=[a,b,tx,ty]
G=[gmat(x) for x in letters]
# rank one factorization D=G+I as u v^T
def outer_uv(M):
 for u in product((0,1),repeat=D):
  if not any(u):continue
  for v in product((0,1),repeat=D):
   if not any(v):continue
   if tuple(sum(u[i]*v[j]<<j for j in range(D)) for i in range(D))==M:return u,v
# Note row encoding
I3=(1,2,4)
uv=[]
for g in G:
 M=xor(g,I3); uv.append(outer_uv(M))
print('G',G,'uv',uv)
# projectors (x,y) over F2, yTx=1
proj=[]
for x in range(1,16):
 for y in range(1,16):
  if (x&y).bit_count()%2:proj.append((x,y))
assert len(proj)==120
factors=[]
for gi,(u,v) in enumerate(uv):
 ub=sum(u[d]<<(r*D+d) for r in range(R) for d in range(D) if u[d])
 # fix vector outer bits with x and y
 for x,y in proj:
  vx=sum(((x>>r)&1)*u[d]<<(r*D+d) for r in range(R) for d in range(D))
  wy=sum(((y>>r)&1)*v[d]<<(r*D+d) for r in range(R) for d in range(D))
  factors.append((gi,x,y,vx,wy))
# target block diagonal
els=[prod(a,b,a,tx),prod(tx,a,b,a),tx,ty]
blocks=[gmat(x) for x in els]
T=[]
for r in range(R):
 for d in range(D):
  row=0
  for s in range(R):
   for e in range(D):
    if s==r and ((blocks[r][d]>>e)&1):row|=1<<(s*D+e)
  T.append(row)
I=tuple(1<<i for i in range(n))
M0=xor(T,I)
r0=mat_rank(M0)
print('target',blocks,'rank',r0,'factors',len(factors))

def mv(M,v):
 return sum(((row&v).bit_count()%2)<<i for i,row in enumerate(M))
def step(M, fac):
 gi,x,y,v,w=fac
 u=mv(M,v)
 return tuple(row^(w if (u>>i)&1 else 0) for i,row in enumerate(M))
# Complete radius-seven rank trajectory: six rank drops and one neutral step.
T=tuple(T)
layers={(T,0)}
for depth in range(1,8):
 nxt=set(); counts={}
 for M,neutral_used in layers:
  rm=mat_rank(xor(M,I))
  for fac in factors:
   P=step(M,fac)
   rp=mat_rank(xor(P,I))
   if rp==rm-1:
    state=(P,neutral_used)
   elif neutral_used==0 and rp==rm:
    state=(P,1)
   else:
    continue
   nxt.add(state)
   counts[(neutral_used,state[1])]=counts.get((neutral_used,state[1]),0)+1
 layers=nxt
 print('depth',depth,'states',len(layers),'neutral0',sum(u==0 for _,u in layers),'neutral1',sum(u==1 for _,u in layers),'goal',any(M==I and u==1 for M,u in layers))
 if not layers:break
