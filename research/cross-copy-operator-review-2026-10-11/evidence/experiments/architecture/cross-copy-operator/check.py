"""Exact signed address permutation obstruction to naive cross-family axis split."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parents[2]
def swap_axes(x,m,axes):
 for i in axes:
  a=(x>>i)&1;b=(x>>(m+i))&1
  if a!=b:x^=(1<<i)|(1<<(m+i))
 return x
def cert(m,w1,w2,q=2):
 N=q**(2*m);w=w1+w2
 def perm(x,axes):
  digits=[]
  for _ in range(2*m):digits.append(x%q);x//=q
  for a in axes:digits[a],digits[m+a]=digits[m+a],digits[a]
  return sum(d*q**i for i,d in enumerate(digits))
 old=[perm(x,range(w))for x in range(N)]+[N+x for x in range(N)]
 new=[perm(x,range(w1))for x in range(N)]+[N+perm(x,range(w2))for x in range(N)]
 assert sorted(old)==list(range(2*N))and sorted(new)==list(range(2*N))
 assert all(old[old[x]]==x and new[new[x]]==x for x in range(2*N))
 of=sum(i==v for i,v in enumerate(old));nf=sum(i==v for i,v in enumerate(new));assert of!=nf
 return {'address_field_size':q,'m':m,'pieces':[w1,w2],'value_columns':2*N,'old_Dw_plus_identity_trace':of,'new_Dw1_directsum_Dw2_trace':nf,'old_minus1_eigenspace_rank':(2*N-of)//2,'new_minus1_eigenspace_rank':(2*N-nf)//2,'all_basis_columns_and_inverse_checked':True,'conclusion':'Not conjugate even by arbitrary invertible linear value-selector: trace/eigen multiplicities differ.'}
res={'status':'EXACT_OBSTRUCTION_TO_UNCHANGED_ONE_STREAM_SELECTOR_TRANSFER','source_PR448_head':'9b966d8188e1cadd00aa834078ee6a8742a9d9b4','source_geometry':'PR386 exact D_P=[[I-P,P],[P,I-P]] acts on doubled ADDRESS coordinate space; it induces a permutation of VALUE addresses. Distinct physical families are direct sums of value-stream spaces, not a tensor factorization of one stream.','instances':[cert(2,1,1,3),cert(8,7,1)],'binary_instance_scope':'The q2 enumeration is a coordinate-permutation model, not the admitted odd-field bit supplier. q3 m2 enumerates every actual odd-field basis column. The general trace formula holds for every admitted odd q and all m; m78 counts need no exponential enumeration.','general':'For N=(address-alphabet-size)^(2m), one width(w1+w2) residual plus one untouched stream has trace N+N/q^(w1+w2). Two independent-family residuals have trace N/q^w1+N/q^w2. Difference N*(1-q^-w1)*(1-q^-w2)>0. Any address/permutation or linear value-selector conjugation preserves trace.','what_still_holds':'On ONE family, D_P1 D_P2=D_(P1+P2) for orthogonal projectors. Each split piece factor and inverse individually correct. These do not identify one virtual helper stream with two physical family streams.','minimum_new_interface':'An explicit virtual-helper value embedding/extraction across families (not only an isometry of address AXES), legal ADD/COPY/READ/MOVE lowering for every split local operand, arbitrary correlated dirty state, full endpoint/inverse and prefix/work/route fees. If a larger/different dirty helper contract makes split pieces independent, prove the new local supplier under that contract rather than transfer unchanged signed95.','scope':'Scoped obstruction to deriving PR448 cross-copy ownership from the unchanged signed95/PR442 one-stream selector contract. Does not rule out a separately paid redesigned local operator with different interface. No allegation that the explicitly conditional extension is an unconditional theorem.'}
if (O/'RESULT.json').exists():
 res['compressed_domain_caveat']=json.loads((O/'RESULT.json').read_text()).get('compressed_domain_caveat','See DIMENSION-AUDIT.json.')
(O/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status']);print(res['instances'])
