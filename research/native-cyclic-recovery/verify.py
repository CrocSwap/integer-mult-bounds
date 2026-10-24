"""End-to-end rounded native consumer; references may use exact rationals."""
from pathlib import Path
from fractions import Fraction as Q
import importlib.util,sys,json,random,hashlib
ROOT=Path(__file__).resolve().parent

def load(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
 mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
D=load('fixed_divisor');C=load('cascade_free')
def need(ok,msg):
 if not ok:raise ValueError(msg)

def rounded_decode(v,w,n,labels,phases,q,bits,mutation=False):
 """Integer grid data. Every rational scale uses the bounded-word datapath."""
 ops=0
 def scaled(pair,p,d):
  nonlocal ops
  out=[]
  for x in pair:
   y,c,guard=D.fixed_rational(x,p,d,bits,'nearest_even');out.append(y);ops+=c
  return tuple(out)
 z=list(v)
 for unused in range(w-1):
  term=C.shift(z,w,n,labels,phases)
  z=[C.add(a,scaled(b,-1,2))for a,b in zip(v,term)]
 route=C.compile_return(w,n,labels,phases)
 out=list(z);sgn=(-1 if w%2 else 1)
 if mutation:sgn=-sgn
 for unused in range(q-1):
  term=C.apply_map(out,route)
  out=[C.add(a,scaled(b,sgn,1<<w))for a,b in zip(z,term)]
 p=1<<(q*w);out=[scaled(x,p,p-1)for x in out]
 return out,ops

rng=random.Random(22885);cases=[];controls=0
for w,n,labels,q,phasecase in [(3,8,[1,2,4],2,False),(3,8,[1,2,4],4,True),(13,16,list(range(1,14)),2,False)]:
 phases=[[(k+1+2*((x&(k+1)).bit_count()))%4 for x in range(n)]for k in range(w)]if phasecase else[[0]*n for k in range(w)]
 # Reference and datapath are separated: exact rational inverse vs bounded-word rounding.
 limit=1<<(w+9);payload_bits=max(24,w+20)
 values=[(rng.randrange(-limit,limit+1),rng.randrange(-limit,limit+1))for unused in range(w*n)]
 got,ops=rounded_decode(values,w,n,labels,phases,q,payload_bits)
 exact=C.decode_factored([(Q(a),Q(b))for a,b in values],w,n,labels,phases,q)
 error=max(abs(Q(x)-y)for a,b in zip(got,exact)for x,y in zip(a,b))
 need(error<=5,'five-grid-unit bound versus stored observations')
 # A separate quantization check uses true non-grid observations and l1 inverse bound.
 true=[(Q(a)+Q(rng.randrange(-1,2),2),Q(b)+Q(rng.randrange(-1,2),2))for a,b in values]
 target=C.decode_factored(true,w,n,labels,phases,q)
 total=max(abs(Q(x)-y)for a,b in zip(got,target)for x,y in zip(a,b))
 need(total<=6,'six-grid-unit bound including observation quantization')
 bad,_=rounded_decode(values,w,n,labels,phases,q,payload_bits,True)
 need(any(abs(Q(x)-y)>5 for a,b in zip(bad,exact)for x,y in zip(a,b)),'changed beta sign must reject')
 controls+=1
 cases.append(dict(roles=w,addresses_per_role=n,total_entries=w*n,cycle_order_divisor=q,
                   monomial_passes=w+q-2,payload_bits=payload_bits,stored_observation_error=str(error),quantized_observation_error=str(total),
                   counted_scalar_data_operations=ops))
receipt=dict(status='PASS_ROUNDED_NATIVE_CYCLIC_RECOVERY',cases=cases,mutation_controls=controls,
             arithmetic='fixed rational scales use Boolean/both-shift/add bounded-word code, no MUL/DIV primitive',
             complete_supplier=False,new_kappa=None)
print(json.dumps(receipt,indent=2))
