"""Small exact Gaussian-dyadic Clifford compiler, independent of gx internals.
Paulis use i^p X^x Z^z. State vectors use integer Gaussian numerators / 2^d.
The tableau is supplemented by a literal circuit, so global phases are kept.

Production exact gate-table zero_state (identical receipts):
research/clifford-state-performance/ and research/clifford-state-production/.
Prepared by Wentao Li with substantial AI assistance.
"""
from dataclasses import dataclass

def parity(x):return x.bit_count()&1
def rank(rows):
 p={}
 for x in rows:
  while x:
   b=x.bit_length()-1
   if b not in p:p[b]=x;break
   x^=p[b]
 return len(p)
def transpose(rows,n):return tuple(sum(((rows[j]>>i)&1)<<j for j in range(n)) for i in range(n))
def mv(rows,x):return sum(parity(r&x)<<i for i,r in enumerate(rows))
def inv(rows,n):
 a=[r|(1<<(n+i)) for i,r in enumerate(rows)]
 for j in range(n):
  k=next(i for i in range(j,n) if a[i]>>j&1);a[j],a[k]=a[k],a[j]
  for i in range(n):
   if i!=j and a[i]>>j&1:a[i]^=a[j]
 assert [r&((1<<n)-1) for r in a]==[1<<i for i in range(n)]
 return tuple(r>>n for r in a)
def basis_extend(cols,n):
 out=[]
 for x in list(cols)+[1<<i for i in range(n)]:
  if rank(out+[x])>len(out):out.append(x)
 assert len(out)==n
 return tuple(out)
def nullspace(rows,n):
 a=list(rows);p=[];k=0
 for j in range(n):
  t=next((i for i in range(k,len(a)) if a[i]>>j&1),None)
  if t is None:continue
  a[t],a[k]=a[k],a[t]
  for i in range(len(a)):
   if i!=k and a[i]>>j&1:a[i]^=a[k]
  p.append(j);k+=1
 return tuple((1<<j)|sum(((a[i]>>j)&1)<<v for i,v in enumerate(p)) for j in range(n) if j not in p)
def pmul(a,b):
 x,z,p=a;y,w,q=b
 return x^y,z^w,(p+q+2*parity(z&y))%4
def identity(n):return tuple([(1<<i,0,0) for i in range(n)]+[(0,1<<i,0) for i in range(n)])
def apply(T,p):
 n=len(T)//2;x,z,ph=p;out=(0,0,ph)
 for i in range(n):
  if x>>i&1:out=pmul(out,T[i])
 for i in range(n):
  if z>>i&1:out=pmul(out,T[n+i])
 return out
def compose(A,B):return tuple(apply(A,p) for p in B)
def inverse(T):
 n=len(T)//2;cols=[x|(z<<n) for x,z,p in T];rows=transpose(cols,2*n);cols_inv=transpose(inv(rows,2*n),2*n);out=[]
 for j,w in enumerate(cols_inv):
  x=w&((1<<n)-1);z=w>>n;u,v,p=apply(T,(x,z,0));assert (u,v)==identity(n)[j][:2];out.append((x,z,(-p)%4))
 return tuple(out)
def qvalue(Q,alpha,x,n):
 return (sum(alpha[i] for i in range(n) if x>>i&1)+2*sum(parity((Q[i]>>(i+1))&(x>>(i+1))) for i in range(n) if x>>i&1))%4
def mul_i(a,p):
 x,y=a;p%=4
 return [(x,y),(-y,x),(-x,-y),(y,-x)][p]

from functools import lru_cache

@lru_cache(maxsize=64)
def _permutation_table(n, rows):
 """Compute Gx from G(x xor lowbit(x)) xor G(lowbit(x))."""
 columns=[sum(((row>>j)&1)<<i for i,row in enumerate(rows)) for j in range(n)]
 table=[0]*(1<<n)
 for x in range(1,len(table)):
  bit=x&-x
  table[x]=table[x^bit]^columns[bit.bit_length()-1]
 return tuple(table)

@lru_cache(maxsize=64)
def _phase_table(n, rows, linear):
 """Remove the lowest bit; all remaining quadratic partners have larger indices."""
 table=[0]*(1<<n)
 for x in range(1,len(table)):
  bit=x&-x
  i,rest=bit.bit_length()-1,x^bit
  table[x]=(table[rest]+linear[i]+2*((rows[i]&rest).bit_count()&1))%4
 return tuple(table)

@dataclass
class Op:
 n:int
 tab:tuple
 circuit:list
 def then(self,b):
  assert self.n==b.n
  return Op(self.n,compose(b.tab,self.tab),self.circuit+b.circuit)
 def adjoint(self):
  circ=[]
  for e in reversed(self.circuit):
   if e[0]=='P':circ.append(('P',inv(e[1],self.n)))
   elif e[0]=='D':circ.append(('D',e[1],tuple((-x)%4 for x in e[2])))
   elif e[0]=='C':circ.append(('C',e[1],-e[2]))
   elif e[0]=='phase':circ.append(('phase',(-e[1])%4))
   else:circ.append(e)
  return Op(self.n,inverse(self.tab),circ)
 def zero_state(self,basis=0):
  # Exact gate-table evaluator (research/clifford-state-performance/); identical receipts.
  N=1<<self.n;vec=[(0,0)]*N;vec[basis]=(1,0);den=0
  for e in self.circuit:
   if e[0]=='P':
    mapping=_permutation_table(self.n,tuple(e[1]));v=[(0,0)]*N
    for x,a in enumerate(vec):v[mapping[x]]=a
    vec=v
   elif e[0]=='X':vec=[vec[x^e[1]] for x in range(N)]
   elif e[0]=='D':
    phases=_phase_table(self.n,tuple(e[1]),tuple(e[2]));v=[]
    for (a,b),phase in zip(vec,phases):
     if phase==0:v.append((a,b))
     elif phase==1:v.append((-b,a))
     elif phase==2:v.append((-a,-b))
     else:v.append((b,-a))
    vec=v
   elif e[0]=='phase':
    phase=e[1]%4;v=[]
    for a,b in vec:
     if phase==0:v.append((a,b))
     elif phase==1:v.append((-b,a))
     elif phase==2:v.append((-a,-b))
     else:v.append((b,-a))
    vec=v
   elif e[0]=='C':
    q,sgn=e[1:];v=[]
    for x,(a,b) in enumerate(vec):
     c,d=vec[x^q]
     # C=(1+i)I/2+(1-i)X/2; inverse conjugates both coefficients.
     v.append((a-sgn*b+c+sgn*d,b+sgn*a+d-sgn*c))
    vec=v;den+=1
   else:raise AssertionError(e)
   while den and all((a&1)==(b&1)==0 for a,b in vec):vec=[(a//2,b//2) for a,b in vec];den-=1
  return vec,den
def ident(n):return Op(n,identity(n),[])
def perm(n,G):
 cols=transpose(G,n);gi=inv(G,n)
 return Op(n,tuple([(a,0,0) for a in cols]+[(0,a,0) for a in gi]),[('P',tuple(G))])
def diag(n,Q,alpha=None):
 Q=tuple(Q);assert transpose(Q,n)==Q
 alpha=tuple(alpha) if alpha is not None else tuple((Q[i]>>i)&1 for i in range(n))
 assert all(alpha[i]%2==(Q[i]>>i)&1 for i in range(n))
 return Op(n,tuple([(1<<i,Q[i],alpha[i]) for i in range(n)]+[(0,1<<i,0) for i in range(n)]),[('D',Q,alpha)])
def cgate(n,q,sgn=1):
 return Op(n,tuple([(1<<i,0,0) for i in range(n)]+[(q if q>>i&1 else 0,1<<i,(3*sgn)%4 if q>>i&1 else 0) for i in range(n)]),[('C',q,sgn)])
def xgate(n,b):return Op(n,tuple([(1<<i,0,0) for i in range(n)]+[(0,1<<i,2*((b>>i)&1)) for i in range(n)]),[('X',b)])
def fourier(n,axes=None):
 out=ident(n)
 for i in range(n) if axes is None else axes:out=out.then(cgate(n,1<<i))
 return out
def hadamard(n,axes):
 axes=list(axes);Q=tuple(1<<i if i in axes else 0 for i in range(n));S=diag(n,Q)
 return S.then(fourier(n,axes)).then(S)
def canonical_frame(n,U):
 r=len(U)
 if r==0:return ident(n)
 if r==n:return fourier(n)
 G=transpose(basis_extend(U,n),n);gi=inv(G,n);Q=tuple((1<<i)^sum(parity(gi_i&gi_j)<<j for j,gi_j in enumerate(transpose(gi,n))) for i,gi_i in enumerate(transpose(gi,n)))
 K=perm(n,G).then(diag(n,Q))
 return K.adjoint().then(fourier(n,range(r))).then(K)
def monomial(op):
 n=op.n;T=op.tab;assert all(x==0 and p%2==0 for x,z,p in T[n:]);G=transpose([x for x,z,p in T[:n]],n);b=mv(G,sum((p//2)<<i for i,(x,z,p) in enumerate(T[n:])))
 gt=transpose(G,n);cols=[mv(gt,z) for x,z,p in T[:n]];Q=transpose(cols,n);alpha=[(p-2*parity(b&z))%4 for x,z,p in T[:n]]
 out=diag(n,Q,alpha).then(perm(n,G)).then(xgate(n,b));assert out.tab==T
 vec,den=op.zero_state();assert den==0 and all(a==(0,0) for i,a in enumerate(vec) if i!=b);phase=[(1,0),(0,1),(-1,0),(0,-1)].index(vec[b]);out=out.then(Op(n,identity(n),[('phase',phase)]));assert out.zero_state()==op.zero_state()
 return out,dict(matrix_rows=G,offset=b,quadratic_rows=Q,linear_Z4=alpha,phase=phase)
def lower_child(op):
 n=op.n;Bcols=[x for x,z,p in op.tab[n:]];r=rank(Bcols)
 if not r:
  mon,rec=monomial(op);return dict(rank=0,left=rec,right=None),mon
 G=transpose(basis_extend(Bcols,n),n);A=inv(G,n);PA=perm(n,A);part=op.then(PA);Bcols=[x for x,z,p in part.tab[n:]];Dcols=[z for x,z,p in part.tab[n:]]
 picks=[];selected=[]
 for j,x in enumerate(Bcols):
  if rank(selected+[x])>len(selected):picks.append(j);selected.append(x)
 assert len(picks)==r and all(x>>r==0 for x in Bcols)
 Br=transpose(selected,r);Bi=inv(Br,r);Dr=transpose([Dcols[j]&((1<<r)-1) for j in picks],r)
 Qsmall=tuple(sum(parity(row&col)<<j for j,col in enumerate(transpose(Bi,r))) for row in Dr);Q=Qsmall+(0,)*(n-r);DQ=diag(n,Q)
 V=part.then(DQ).then(hadamard(n,range(r)));assert all(x==0 for x,z,p in V.tab[n:]);Vmon,Vrec=monomial(V)
 S=diag(n,tuple(1<<i if i<r else 0 for i in range(n)))
 left=S.adjoint().then(DQ.adjoint()).then(PA.adjoint());right=Vmon.then(S.adjoint()).then(xgate(n,(1<<r)-1))
 lmon,lrec=monomial(left);rmon,rrec=monomial(right);compiled=rmon.then(fourier(n,range(r))).then(lmon)
 assert compiled.tab==op.tab and compiled.zero_state()==op.zero_state()
 return dict(rank=r,left=lrec,right=rrec),compiled
