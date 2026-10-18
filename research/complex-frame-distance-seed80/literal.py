"""Literal phase-forgetting P/D/C action; no producer or verifier imports.

Conventions attributed to icekylinx's exact Clifford compiler. This module
uses explicit binary matrices and elementary actions instead of its Pauli
tableau, lower_child routine or recursive-rank field. Apache-2.0.
"""
def parity(x):return x.bit_count()%2
def mv(rows,x):return sum(parity(a&x)<<i for i,a in enumerate(rows))
def transpose(rows,n):return tuple(sum(((rows[j]>>i)&1)<<j for j in range(n)) for i in range(n))
def rank(vs):
 a=list(vs);r=0
 for b in range(max(a,default=0).bit_length()):
  k=next((k for k in range(r,len(a)) if a[k]>>b&1),None)
  if k is None:continue
  a[r],a[k]=a[k],a[r]
  for j in range(len(a)):
   if j!=r and a[j]>>b&1:a[j]^=a[r]
  r+=1
 return r
def inverse(rows,n):
 a=[r|(1<<(i+n)) for i,r in enumerate(rows)]
 for j in range(n):
  k=next((k for k in range(j,n) if a[k]>>j&1),None)
  if k is None:raise ValueError('singular matrix')
  a[j],a[k]=a[k],a[j]
  for k in range(n):
   if k!=j and a[k]>>j&1:a[k]^=a[j]
 return tuple(x>>n for x in a)
def frame(n,U,omit_diagonal=False):
 if not U:return tuple(1<<i for i in range(2*n))
 if len(U)==n:
  return tuple([1<<i for i in range(n)]+[(1<<i)|(1<<(n+i)) for i in range(n)])
 # Literal compiler basis extension and P_G ; D_Q conjugating gate sequence.
 cols=[]
 for v in list(U)+[1<<i for i in range(n)]:
  if rank(cols+[v])>len(cols):cols.append(v)
 if len(cols)!=n:raise ValueError('basis extension')
 G=transpose(cols,n);Gi=inverse(G,n);Git=transpose(Gi,n)
 Q=tuple((1<<i)^sum(parity(Git[i]&Git[j])<<j for j in range(n)) for i in range(n))
 def apply(x,z):
  # K^-1: inverse D (identical without phase), then inverse P.
  if not omit_diagonal:z^=mv(Q,x)
  x,z=mv(Gi,x),mv(transpose(G,n),z)
  # One C gate per active axis. Its sign affects phase only.
  for i in range(len(U)):
   if z>>i&1:x^=1<<i
  # K: P followed by D.
  x,z=mv(G,x),mv(Git,z)
  if not omit_diagonal:z^=mv(Q,x)
  return x|(z<<n)
 return tuple(apply((1<<i) if i<n else 0,(1<<(i-n)) if i>=n else 0) for i in range(2*n))
def act(columns,v):
 out=0
 while v:
  b=(v&-v).bit_length()-1;out^=columns[b];v&=v-1
 return out
def inverse_columns(columns):
 n=len(columns);return transpose(inverse(transpose(columns,n),n),n)
def transition_rank(n,left_inverse,right):
 mask=(1<<n)-1
 return rank([act(right,left_inverse[n+j])&mask for j in range(n)])
def port_frame(n,q,target=False):
 # Source C_q; target C_q^-1 followed by full C. Signs are invisible here.
 return tuple([1<<i for i in range(n)]+[
  (1<<(n+i))^((q if q>>i&1 else 0))^((1<<i) if target else 0)
  for i in range(n)])
def symplectic(columns,n):
 mask=(1<<n)-1
 def pair(a,b):return parity((a&mask)&(b>>n))^parity((a>>n)&(b&mask))
 return all(pair(a,b)==int(abs(i-j)==n) for i,a in enumerate(columns) for j,b in enumerate(columns))
