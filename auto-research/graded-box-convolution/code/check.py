from pathlib import Path
from fractions import Fraction as Q
from itertools import product
from math import prod
import importlib.util,json,random,hashlib,sys
import graded as G
here=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Assertions must remain enabled')
assert len(sys.argv)==2
out=Path(sys.argv[1]).resolve();assert not out.exists() and not out.is_relative_to(here.parent)
spec=importlib.util.spec_from_file_location('recenter',here/'recenter_fixture.py');R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
shapes=[[2],[3],[2,2],[3,5],[2,3,4],[3,3,3,3],[2]*5,[2]*8,[1,3,1,2]]
identity_pairs=0;aliases_rejected=0
for shape in shapes:
 L=G.layout(shape);coords=L['coordinates'];N=L['N'];idx={v:i for i,v in enumerate(coords)}
 for i,a in enumerate(coords):
  for j,b in enumerate(coords):
   s=L['indices'][i]+L['indices'][j]
   if s>=N:continue
   gamma=[];rem=s
   for n in shape:gamma.append(rem%n);rem//=n
   assert rem==0
   carry=0;count=0
   for x,y,z,n in zip(a,b,gamma,shape):
    q=x+y+carry;assert q%n==z;carry=q//n;assert carry in [0,1];count+=carry
   assert carry==0 and count<L['T']
   target=idx[tuple(gamma)];delta=(L['grades'][i]+L['grades'][j]-L['grades'][target])%L['T']
   assert delta==count%L['T']
   valid=all(x+y<n for x,y,n in zip(a,b,shape));assert (delta==0)==valid
   identity_pairs+=1;aliases_rejected+=not valid
results=[];rng=random.Random(102)
for shape in shapes:
 N=prod(shape);stats={}
 for case in range(8):
  f=[rng.randrange(-127,128)for _ in range(N)];g=[rng.randrange(-63,64)for _ in range(N)]
  assert G.apply(f,g,shape,stats)==G.oracle(f,g,shape)
 results.append(dict(shape=shape,cases=8,**stats))
# Large separable inputs have an independent tensor-product oracle.
large=[]
for shape in [[2]*12,[3]*8]:
 coords=list(product(*(range(n)for n in shape)));fa=[[(-1)**j*(j+2)for j in range(n)]for n in shape];ga=[[(-1)**(j+1)*(j+1)for j in range(n)]for n in shape]
 f=[prod(fa[d][v[d]]for d in range(len(shape)))for v in coords];g=[prod(ga[d][v[d]]for d in range(len(shape)))for v in coords]
 ha=[[sum(fa[d][j]*ga[d][k-j]for j in range(k+1))for k in range(n)]for d,n in enumerate(shape)]
 expected=[prod(ha[d][v[d]]for d in range(len(shape)))for v in coords];stats={};assert G.apply(f,g,shape,stats)==expected
 old_slots=prod(2*n-1 for n in shape);assert stats['layout_product_slots']<old_slots
 large.append(dict(shape=shape,outputs=len(coords),old_padded_slots=old_slots,**stats))
# Correct upper orientation is lower convolution after reflecting the input/output coordinates.
def weighted(shape,bits,upper):
 matrix=R.dense(shape,upper);kernel,weights,*_=R.prepare(shape,upper,bits);coords=R.coordinates(shape);index={v:i for i,v in enumerate(coords)};reflect=[index[tuple(n-1-x for n,x in zip(shape,v))]for v in coords]
 vectors=[[Q(int(j==k))for j in range(len(coords))]for k in range(len(coords))]+[[Q((-1)**j*(j%7+1),8)for j in range(len(coords))],[Q((j*13)%17-8,8)for j in range(len(coords))]]
 stats={};worst=Q(0);scale=1<<bits
 for x in vectors:
  transformed=[int(R.rnd(a/w,bits)*scale)for a,w in zip(x,weights)];hh=[int(a*scale)for a in kernel]
  inp=[transformed[i]for i in reflect]if upper else transformed
  z=G.apply(hh,inp,shape,stats);z=[z[i]for i in reflect]if upper else z
  got=[R.rnd(R.rnd(Q(a,scale*scale),bits)*w,bits)for a,w in zip(z,weights)]
  expected=[sum((a*b for a,b in zip(row,x)),Q(0))for row in matrix]
  worst=max(worst,max(abs(a-b)for a,b in zip(got,expected)))
 eta=Q(1,scale);H=prod(Q(15,14)for _ in shape);bound=max(weights)*(len(coords)*(H*eta+eta/min(weights)+eta*eta)+eta)+eta
 assert worst<=bound<R.pow2(-12)
 return dict(shape=shape,bits=bits,orientation='upper'if upper else'lower',vectors=len(vectors),worst_error=str(worst),rounding_bound=str(bound),**stats)
weighted_results=[weighted(shape,bits,upper)for shape in [[3]*4,[3,2,4]]for bits in [32,64]for upper in [False,True]]
controls=[]
for mutation,shape in [('no_grade',[3,5]),('small_modulus',[2]*4),('wrong_recurrence',[3,5]),('no_index_padding',[2,3,4]),('missing_signed_cross',[3,5])]:
 found=False;N=prod(shape)
 for trial in range(8):
  f=[rng.randrange(-9,10)for _ in range(N)];g=[rng.randrange(-9,10)for _ in range(N)]
  if G.apply(f,g,shape,mutation=mutation)!=G.oracle(f,g,shape):found=True;break
 assert found,mutation;controls.append(mutation)
family=[]
for a in [26,27,32,64]:
 p=1<<(10*a);D=(1<<(4*a))-1;k=1<<(3*a-11)
 assert 4*D<4*(1<<(4*a)) and (4*D)**5<4**5*p**2
 assert D+1==1<<(4*a);assert D*(3*a-11)<p
 family.append(dict(a=a,p_log2=10*a,dimensions=D,tile_axis=k+1,new_slot_overhead_upper=4*D,new_overhead_power_bound='strictly below 4*p^(2/5)',old_log2_overhead_lower=str(Q(D,2)),new_log2_overhead_upper=4*a+2))
result=dict(status='PASS_EXACT_GRADED_BOX_CONVOLUTION_AND_WEIGHTED_FIXTURES',carry_identity_pairs=identity_pairs,invalid_flat_aliases_rejected=aliases_rejected,integer_cases=results,large_separable_cases=large,weighted=weighted_results,controls=controls,uniform_family=family,sources={f.name:hashlib.sha256(f.read_bytes()).hexdigest()for f in [here/'graded.py',here/'check.py',here/'recenter_fixture.py']},scope='Exact finite integer convolutions, general written carry-count identity and polynomial slot-count bound. Weighted tests are the prior rational analogue. No certified transcendental tables, complete phase-cell cover, tensor Schur-boundary composition, fast tape routing, all-size time bound or new kappa.')
out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],identity_pairs,aliases_rejected,len(weighted_results),controls)
