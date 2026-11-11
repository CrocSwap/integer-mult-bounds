from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Independent modular tests of the retained generic-child algebra, m=100.
Every equality checks all 200 matrix columns over a field and a local ring.
These tests accompany the universal algebraic proof; they do not replace it.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
import numpy as np
from pathlib import Path
import hashlib,json,math,sys
if not __debug__:raise RuntimeError('Assertions required')
HERE=support.BANK;SPLIT=tuple(map(int,sys.argv[1].split(',')))if len(sys.argv)>1 else (49,11)
assert SPLIT == (49,11)
OUT=HERE/('split_'+str(SPLIT[0])+'_'+str(SPLIT[1]));OUT.mkdir(exist_ok=True)
N=100;rng=np.random.default_rng(771292);I=np.eye(N,dtype=np.int64);C=I[:,::-1];Z=np.zeros((N,N),dtype=np.int64)
def mm(A,B,M):return (A@B)%M
def inv(A,M,p):
 n=len(A);a=np.concatenate((A%M,np.eye(n,dtype=np.int64)),axis=1)
 for j in range(n):
  k=next((k for k in range(j,n)if int(a[k,j])%p),None)
  if k is None:return None
  a[[j,k]]=a[[k,j]];a[j]=a[j]*pow(int(a[j,j]),-1,M)%M
  q=a[:,j].copy();q[j]=0;a=(a-q[:,None]*a[j][None,:])%M
 assert np.array_equal(a[:,:n],np.eye(n,dtype=np.int64));return a[:,n:]
def edge(P,A,AI,M):return np.block([[(I-mm(mm(A,P,M),AI,M))%M,mm(mm(A,P,M),C,M)],[mm(mm(C,P,M),AI,M),(I-mm(mm(C,P,M),C,M))%M]])
def lower(X,r,M,p):
 X=X.copy();L=I.copy();R=I.copy();piv=[]
 for j in range(r):
  k=N-1-j;a=int(X[j,k])
  if a%p==0:return None
  ai=pow(a,-1,M);piv.append(a)
  q=X[:,k]*ai%M;q[:j+1]=0
  X=(X-q[:,None]*X[j][None,:])%M;L=(L-q[:,None]*L[j][None,:])%M
  q=X[j]*ai%M;q[k:]=0
  X=(X-X[:,k,None]*q[None,:])%M;R=(R-R[:,k,None]*q[None,:])%M
 target=np.zeros_like(X)
 for j,a in enumerate(piv):target[j,N-1-j]=a
 assert np.array_equal(X,target)
 assert np.array_equal(np.diag(L),np.ones(N)) and np.array_equal(np.diag(R),np.ones(N))
 assert not np.any(np.triu(L,1)) and not np.any(np.triu(R,1))
 return L,R,piv
results=[]
for p,w in [(101,1),(101,2)]:
 M=p**w
 for offset,r in [(40,SPLIT[0]),(40+SPLIT[0],SPLIT[1])]:
  P0=Z.copy();P0[np.arange(offset,offset+r),np.arange(offset,offset+r)]=1
  for attempt in range(20):
   h=rng.integers(0,M,(N,N),dtype=np.int64);hi=inv(h,M,p)
   if hi is None:continue
   P=mm(mm(h,P0,M),hi,M);a=rng.integers(1,M,N,dtype=np.int64)
   a[a%p==0]=1;A=np.diag(a);AI=np.diag([pow(int(x),-1,M)for x in a])
   G=edge(P,A,AI,M);data=lower(G[:N,N:],r,M,p)
   if data is not None:break
  else:raise AssertionError('Failed to draw generic class')
  assert np.array_equal(mm(P,P,M),P)
  assert np.array_equal(mm(G,G,M),np.eye(2*N,dtype=np.int64))
  L,R,d=data;Li=inv(L,M,p);Ri=inv(R,M,p)
  T=np.block([[L,Z],[Z,Ri]]);Ti=np.block([[Li,Z],[Z,R]])
  g=mm(mm(T,G,M),Ti,M);diff=(g-np.eye(2*N,dtype=np.int64))%M
  E=I[:,:r];F0=I[:,::-1][:,:r];D=np.diag(d);Di=np.diag([pow(x,-1,M)for x in d])
  A0=diff[:r,:N];B=mm(diff[N:,N+np.arange(N-1,N-r-1,-1)],Di,M)
  U=np.concatenate((E,B),axis=0);V=np.concatenate((A0,mm(D,F0.T,M)),axis=1)
  assert np.array_equal(mm(U,V,M),diff)
  assert np.array_equal(mm(V,U,M),(-2*np.eye(r,dtype=np.int64))%M)
  K=(-mm((B+mm(F0,Di,M))%M,E.T,M)+mm(mm(mm(F0,Di,M),A0,M),(I-mm(E,E.T,M))%M,M))%M
  assert np.array_equal(mm(K,E,M),(-B-mm(F0,Di,M))%M)
  assert np.array_equal(mm(mm(D,F0.T,M),K,M),(A0+E.T)%M)
  S=np.block([[I,Z],[K,I]]);Si=np.block([[I,Z],[(-K)%M,I]])
  target=np.block([[(I-mm(E,E.T,M))%M,mm(mm(E,D,M),F0.T,M)],[mm(mm(F0,Di,M),E.T,M),(I-mm(F0,F0.T,M))%M]])
  assert np.array_equal(mm(mm(S,g,M),Si,M),target)
  assert not np.array_equal(mm(S,g,M),target),'Omitting inverse lower wrapper must fail'
  results.append({'prime':p,'w':w,'ring_modulus':M,'rank':r,'support':[offset,offset+r],'generic_draw':attempt+1,'all_columns_checked':200,'unit_lower_row_and_column_adapters':True,'factorization_g_minus_I':True,'VU_minus2I':True,'K_identities':True,'one_weighted_reversed_child_exact':True,'omitted_wrapper_rejected':True})
 # A common arbitrary h,A conjugates the complete partition, including dirty
 # real coordinates and both paid complement blocks.
 product=np.eye(2*N,dtype=np.int64)
 for offset,r in [(0,20),(20,20),(40,SPLIT[0]),(40+SPLIT[0],SPLIT[1])]:
  P0=Z.copy();P0[np.arange(offset,offset+r),np.arange(offset,offset+r)]=1
  P=mm(mm(h,P0,M),hi,M);product=mm(edge(P,A,AI,M),product,M)
 full=edge(I,A,AI,M);assert np.array_equal(product,full)
 assert np.array_equal(mm(product,product,M),np.eye(2*N,dtype=np.int64))
 results.append({'prime':p,'w':w,'common_GL_and_weight_chart_endpoint_all_columns':200,'arbitrary_dirty_full_rank':True,'inverse_all_columns':True})
# Explicit local-ring bad profile: a nonzero nonunit cannot be inverted, but
# the full involution still has unit Gaussian pivots as the retained fallback requires.
p=101;M=p*p;h=I.copy();h[0,40]=1;h[40,0]=p;h[40,40]=1+p
hi=inv(h,M,p);P0=Z.copy();P0[40:82,40:82]=np.eye(42,dtype=np.int64);P=mm(mm(h,P0,M),hi,M)
assert P[0,0] and P[0,0]%p==0
G=edge(P,I,I,M);assert lower(G[:N,N:],42,M,p) is None
Gi=inv(G,M,p);assert Gi is not None and np.array_equal(Gi,G)
results.append({'bad_local_ring_nonzero_nonunit':int(P[0,0]),'generic_branch_rejected':True,'full_unit_pivot_fallback_inversion':True,'ring_modulus':M})
out={'status':'PASS_INDEPENDENT_GENERIC_LOWERING_AND_LOCAL_RING_CONTROLS','split':list(SPLIT),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'tests':results,'scope':'Finite all-column algebra checks plus explicit nonunit fallback control; universal compiler and common-chart hypotheses remain inherited.'}
(OUT/'GENERIC-RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
