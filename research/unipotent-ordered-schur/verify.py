"""Literal Schur intertwiners for the unipotent compressed component.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

def need(ok,message):
 if not ok:raise ValueError(message)

from itertools import product

def mm(a,b,p):return [[sum(x*y for x,y in zip(r,c))%p for c in zip(*b)] for r in a]
def add(a,b,p,s=1):return [[(x+s*y)%p for x,y in zip(r,t)] for r,t in zip(a,b)]
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def rr(a,p):
 a=[r[:] for r in a];i=0;piv=[]
 for j in range(len(a[0])):
  k=next((k for k in range(i,len(a)) if a[k][j]%p),None)
  if k is None:continue
  a[i],a[k]=a[k],a[i];v=pow(a[i][j],-1,p);a[i]=[x*v%p for x in a[i]]
  for k in range(len(a)):
   if k!=i:
    v=a[k][j];a[k]=[(x-v*y)%p for x,y in zip(a[k],a[i])]
  piv.append(j);i+=1
  if i==len(a):break
 return a,piv

def rank(a,p):return len(rr(a,p)[1])
def ker(a,p):
 r,piv=rr(a,p); n=len(a[0]);out=[]
 for j in range(n):
  if j not in piv:
   v=[0]*n;v[j]=1
   for i,k in enumerate(piv):v[k]=-r[i][j]%p
   out.append(v)
 return out

def inv(a,p):
 n=len(a);r,piv=rr([x+y for x,y in zip(a,eye(n))],p);need(piv==list(range(n)),"invertible header");return [x[n:] for x in r]

def tr(a):return [list(x) for x in zip(*a)]
def mv(a,v,p):return [sum(x*y for x,y in zip(r,v))%p for r in a]
def power(a,k,p):
 out=eye(len(a))
 for _ in range(k):out=mm(out,a,p)
 return out

def complement(w,p):
 d=len(w);cols=tr(w);r=rank(w,p);out=[]
 for v in eye(d):
  if rank(tr(cols+[v]),p)>r:
   cols.append(v);out.append(v);r+=1
 return tr(out)

def fixture(w,x0,y0,p,pads=(0,0,0),twist=False):
 d=len(w);r0=len(y0);a=d-rank(w,p);s10,s01,s11=pads
 need(all(sum(x0[i][k]*y0[k][j] for k in range(r0))%p==(-w[i][j])%p for i in range(d) for j in range(d)),'sector00 product')
 nn=complement(w,p);h=add(eye(d),w,p,-1);hi=inv(h,p);cc=inv(add(eye(d),w,p),p)
 x10=[r+t+[0]*s10 for r,t in zip(w,nn)];x01=[r+t+[0]*s01 for r,t in zip(w,nn)]
 y10=eye(d)+[[0]*d for _ in range(a+s10)];y01=eye(d)+[[0]*d for _ in range(a+s01)]
 xx=[u+v+t+z+[0]*s11 for u,v,t,z in zip(x0,x10,x01,h)]
 yy=y0+y10+y01+eye(d)+[[0]*d for _ in range(s11)]
 sizes=[r0,d+a+s10,d+a+s01,d+s11];n=sum(sizes);m=n-d
 need(mm(xx,yy,p)==eye(d),'split identity')
 def physical(v):
  at=0
  def take(k):
   nonlocal at
   out=v[at:at+k];at+=k;return out
  t=take(r0);x=take(d);b=take(a);y=take(d);c=take(a);j10=take(s10);j01=take(s01);j11=take(s11)
  xt=mv(x0,t,p);shift=mv(cc,xt,p)
  x=[(v-z)%p for v,z in zip(x,shift)];y=[(v-z)%p for v,z in zip(y,shift)]
  total=[sum(v)%p for v in zip(xt,mv(w,x,p),mv(nn,b,p),mv(w,y,p),mv(nn,c,p))]
  z=[-v%p for v in mv(hi,total,p)]
  return t+x+b+j10+y+c+j01+z+j11
 bcan=tr([physical(v) for v in eye(m)])
 if twist:
  gg=eye(n);start=0
  for size in sizes:
   if size>=2:
    gg[start][start+1]=1
   start+=size
  yy=mm(gg,yy,p);xx=mm(xx,inv(gg,p),p);bcan=mm(gg,bcan,p)
 need(mm(xx,bcan,p)==[[0]*m for _ in range(d)],'normal form lies in kernel')
 raw=ker(xx,p);header=[r+s for r,s in zip(yy,tr(raw))];hinv=inv(header,p)
 link=[r[:] for r in mm(hinv,bcan,p)[d:]];need(rank(link,p)==m,'residual intertwiner invertible')
 pair=[]
 for roles in ((0,1,0,1),(0,0,1,1)):
  diag=[v for size,v in zip(sizes,roles) for _ in range(size)]
  pp=[[int(i==j)*diag[i] for j in range(n)] for i in range(n)]
  aa=mm(mm(hinv,pp,p),header,p)
  need([r[:d] for r in aa[:d]]==eye(d),'common identity pivot')
  pair.append(add([r[d:] for r in aa[d:]],mm([r[:d] for r in aa[d:]],[r[d:] for r in aa[:d]],p),p,-1))
 # Build the ordered normal form independently in its declared coordinate order.
 expected=[]
 e=d+a
 aa=[r+t for r,t in zip(w,nn)]+[[0]*e for _ in range(a)]
 for which in (0,1):
  mat=[[0]*m for _ in range(m)]
  for i in range(e):
   if which==0:
    mat[r0+i][r0+i]=1
    for j in range(e):mat[r0+i][r0+e+j]=aa[i][j]
   else:
    mat[r0+e+i][r0+e+i]=1
    for j in range(e):mat[r0+e+i][r0+j]=aa[i][j]
  off=r0+2*e
  for count,value in zip(pads,((1,0,1) if which==0 else (0,1,1))):
   for j in range(count):mat[off+j][off+j]=value
   off+=count
  expected.append(mat)
 for actual,target in zip(pair,expected):
  need(mm(actual,link,p)==mm(link,target,p),'whole ordered residual intertwiner')
  need(mm(actual,actual,p)==actual,'idempotent residual')
 ss,tt=pair;comm=add(mm(ss,tt,p),mm(tt,ss,p),p,-1)
 need(rank(comm,p)==2*d,'sharp commutator')
 zz=power(add(ss,tt,p,-1),2,p)
 for j in (1,d+1):
  need(rank(power(add(zz,eye(m),p,-1),j,p),p)==r0+s11+2*rank(power(w,2*j-1,p),p),'central one-primary power ranks')
  need(rank(power(zz,j,p),p)==2*e+s10+s01,'central zero-primary power ranks')
 return m

def matrices(r,c,p):
 for entries in product(range(p),repeat=r*c):yield [list(entries[i*c:(i+1)*c]) for i in range(r)]

def main():
 cases=0;scanned=0;changed=0;zero_factor_controls=[]
 for p,d,maxr in [(2,1,2),(3,1,2),(5,1,2),(2,2,2),(3,2,1)]:
  for w in matrices(d,d,p):
   if any(any(r) for r in power(w,d,p)):continue
   for r0 in range(max(1,rank(w,p)),maxr+1):
    for x0 in matrices(d,r0,p):
     for y0 in matrices(r0,d,p):
      scanned+=1
      if any(sum(x0[i][k]*y0[k][j] for k in range(r0))%p!=(-w[i][j])%p for i in range(d) for j in range(d)):continue
      fixture(w,x0,y0,p);cases+=1
      if cases%31==0:
       fixture(w,x0,y0,p,(1,1,1),True);changed+=1
 # Higher nilpotent blocks and the exact zero-sector lower boundary.
 higher=0
 for p in (2,3,5,7):
  for d in (1,2,3,4):
   w=[[int(j==i+1) for j in range(d)] for i in range(d)]
   r0=d-1;x0=[[-w[i][j+1]%p for j in range(r0)] for i in range(d)]
   y0=[[int(j==i+1) for j in range(d)] for i in range(r0)]
   fixture(w,x0,y0,p,(1,2,1),True);higher+=1
 # Different sector00 ranks cannot give equivalent full splits.
 for x,y in ((0,0),(1,0),(0,1)):
  fixture([[0]],[[x]],[[y]],3)
  zero_factor_controls.append((int(x!=0),int(y!=0)))
 need(len(set(zero_factor_controls))==3,'inequivalent original factor systems')
 rejected=0
 try:fixture([[0]],[[1]],[[1]],3)
 except ValueError:rejected+=1
 try:fixture([[1]],[[2]],[[1]],3)
 except ValueError:rejected+=1
 need(rejected==2,'bad product and nonunipotent boundary reject')
 print('PASS_UNIPOTENT_ORDERED_SCHUR',dict(factor_pairs_scanned=scanned,complete_domain_intertwiners=cases,padded_basis_changes=changed,higher_block_fixtures=higher,inequivalent_split_controls=3,rejections=2))

if __name__=='__main__':main()
