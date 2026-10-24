#!/usr/bin/env python3
"""Tiny exact f2/f3 tensor bookkeeping probes; no native suite or source imports."""
import gzip,hashlib,itertools,json,pathlib,subprocess,time
from . import source
PIN="ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c"
def raw(path):return source.raw(path)
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def plus(a,b):return a[0]+b[0],a[1]+b[1]
def ipow(q):return ((1,0),(0,1),(-1,0),(0,-1))[q%4]
def mono(rec,x,omit_phase=False):
 y=sum(((row&x).bit_count()%2)<<j for j,row in enumerate(rec['matrix_rows']))^rec['offset']
 q=0 if omit_phase else rec['phase']
 q+=sum(rec['linear_Z4'][j] for j in range(9) if x>>j&1)
 q+=2*sum((((rec['quadratic_rows'][j]>>(j+1))&(x>>(j+1))).bit_count()%2) for j in range(9) if x>>j&1)
 return y,ipow(q)
def one_column(rec,x):
 r=rec['rank'];y,a=mono(rec['right'],x);out={}
 for flip in range(1<<r):
  b=a
  for j in range(r):b=mul(b,(1,-1) if flip>>j&1 else (1,1))
  z,c=mono(rec['left'],y^flip);out[z]=mul(b,c)
 return out # common denominator2^r

def tensor_column(rec,xs):
 out={(): (1,0)}
 for x in xs:
  out={prefix+(y,):mul(a,b) for prefix,a in out.items() for y,b in one_column(rec,x).items()}
 return out

def wide_column(rec,xs,wrong_phase_once=False):
 r=rec['rank'];ys=[];amp=(1,0)
 for x in xs:
  y,a=mono(rec['right'],x,omit_phase=True);ys.append(y);amp=mul(amp,a)
 amp=mul(amp,ipow(rec['right']['phase']*(1 if wrong_phase_once else len(xs))))
 out={}
 for flip in range(1<<(r*len(xs))):
  state=ys[:];a=amp
  for j in range(r):
   for c in range(len(xs)):
    bit=flip>>(j*len(xs)+c)&1 # explicit axis-major child order
    state[c]^=bit<<j;a=mul(a,(1,-1) if bit else (1,1))
  target=[]
  for x in state:
   z,b=mono(rec['left'],x,omit_phase=True);target.append(z);a=mul(a,b)
  a=mul(a,ipow(rec['left']['phase']*(1 if wrong_phase_once else len(xs))))
  out[tuple(target)]=a
 return out # common denominator2^(r*f)

def run():
 t=time.monotonic();path='research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz';data=json.loads(gzip.decompress(raw(path)));pair=data['new_paid_pairs'][0];assert (pair['input'],pair['output'],pair['rank'])==(0,131,2)
 checks=[]
 for f in (2,3):
  xs=tuple((0,1,511)[:f])
  for d,rec in pair['recipes'].items():
   a=tensor_column(rec,xs);b=wide_column(rec,xs);assert a==b
   # Nonseparable sum of two basis states; equality extends by linearity.
   alt=tuple((511,256,7)[:f]);left=a.copy();right=b.copy()
   for k,v in tensor_column(rec,alt).items():left[k]=plus(left.get(k,(0,0)),mul((2,-1),v))
   for k,v in wide_column(rec,alt).items():right[k]=plus(right.get(k,(0,0)),mul((2,-1),v))
   assert left==right
   assert wide_column(rec,xs,True)!=a
   # True inverse of each lifted monomial, including phase.
   for m in (rec['left'],rec['right']):
    table=[mono(m,x) for x in range(512)];back={y:(x,mul(a,(1,0))) for x,(y,a) in enumerate(table)};assert len(back)==512
    for x in xs:
     y,a=table[x];z,b=back[y];assert z==x and mul(a,(b[0],-b[1]))==(1,0)
   checks.append({'f':f,'direction':d,'rank':2*f,'nonzero_basis_column_entries':1<<(2*f),'tensor_equals_shuffled_lift':True,'global_phase_once_mutant_rejected':True,'arbitrary_two_term_state':True})
 # A genuine source Fourier relation at f1 is NOT a universal tensor-substitution identity.
 # C eigenvalues1,i; C⊗C additionally has eigenvalue-1.
 relation_f1=all(ipow(2*k)==plus(plus(ipow(k),ipow(-k)),(-1,0)) for k in (0,1));relation_f2=ipow(4)==plus(plus(ipow(2),ipow(-2)),(-1,0));assert relation_f1 and not relation_f2
 sources=['research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','research/kappa-rebuild/complex/native_extensions.py','research/kappa-rebuild/complex/rebuild_native.py','research/kappa-function-composition/complex/prune_native.py','research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py','research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','research/kappa-round3-warp-20261022/NATIVE-VALIDATION.json','research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz']
 out={'status':'PASS_SCOPED_TENSOR_BOOKKEEPING_CONTROLS','source_pin':PIN,'probes':checks,'finite_numeric_identity_does_not_imply_tensor_substitution':{'source_relation':'C²=C+C^-1-I atf1','fails_f2_on_minus_minus_eigenvector':True},'source_sha256':{p:hashlib.sha256(raw(p)).hexdigest() for p in sources},'elapsed_seconds':time.monotonic()-t,'scope':'Bookkeeping controls only. Quantified algebraic lift is proved in package PROOF.md; physical layout/cost/precision not inferred.'}
 return out
