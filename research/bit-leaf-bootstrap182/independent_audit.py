from pathlib import Path
from fractions import Fraction as Q
from math import gcd
import hashlib,json,copy,sys
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;P=HERE.parent/'paired-cube-local-bit-168';raw=(P/'certificate.json').read_bytes();base=json.loads(raw);a=base['arithmetic'];c=Q(a['coarse_bit_saving']);l0=Q(a['actual_uniform_bit_saving']);u=a['bridge']['bit_uniform'];assert l0==(1-Q(u['atom_beta']))*c+Q(u['atom_beta'])*Q(u['old_atom_saving']);assert 0<l0<c<Q(a['complex_saving'])<Q(1,2)
def level(previous,result,theta):
 assert result==(1-theta)*c+theta*previous
 assert 0<previous<result<c
 assert result<theta<1-result
 return {'saving':str(result),'adapter_gap':str(theta-result),'row_gap':str(1-result-theta),'strict_improvement':str(result-previous)}
chain=[l0];levels=[]
for j in range(1,4):
 nxt=(1-c)*c+c*chain[-1];levels.append(level(chain[-1],nxt,c));chain.append(nxt);assert nxt==c-c**j*(c-l0)
eta=Q(1,10**24);q=chain[-1]*(1-2*eta);ceiling=(1-eta)*q/(1+q);den=10**18;grid=Q((ceiling.numerator*den-1)//ceiling.denominator,den);assert grid<ceiling<=grid+Q(1,den)
sibling=json.loads((HERE/'certificate.json').read_text())['selected'];assert chain[-1]==Q(sibling['ordinary_saving']);assert grid==Q(sibling['kappa'])
# Independent matrix proof of weighted leaves over genuine prime-power rings.
def mul(A,B,m):return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(2))%m for j in range(2)) for i in range(2))
J=((0,1),(1,0));cases=0
for m in (9,25,49,121):
 for weight in range(m):
  if gcd(weight,m)!=1:continue
  inv=pow(weight,-1,m);L=lambda x:((1,0),(x%m,1));U=lambda x:((1,x%m),(0,1));D=((1,0),(0,-1));target=((0,weight),(inv,0))
  assert mul(mul(J,L(weight),m),J,m)==U(weight)
  actual=mul(mul(mul(D,U(weight),m),L(-inv),m),U(weight),m)
  assert actual==target
  # Four complete ordinary swaps, with coefficients applied only in lower shears.
  factors=[D,J,L(weight),J,L(-inv),J,L(weight),J];M=((1,0),(0,1))
  for F in factors:M=mul(M,F,m)
  assert M==target;cases+=1
controls=[]
def reject(name,fn):
 try:fn()
 except (AssertionError,ValueError):controls.append(name)
 else:raise AssertionError('accepted '+name)
reject('attained_infinite_limit',lambda:level(chain[-1],c,c))
reject('circular_leaf_equal_to_coarse',lambda:level(c,c,c))
# Set theta equal to the actual resulting saving using its exact fixed-point value.
critical=c/(1+c-l0)
reject('exact_atom_threshold_without_strict_gap',lambda:level(l0,critical,critical))
rowcritical=l0/(1-c+l0)
reject('borrowing_gap_zero',lambda:level(l0,rowcritical,1-rowcritical))
reject('nonunit_prefix_weight',lambda:pow(3,-1,9))
def omitted_swap():
 M=((1,0),(0,1));factors=[((1,0),(0,-1)),((1,0),(2,1)),J,((1,0),(-5,1)),J,((1,0),(2,1)),J]
 for F in factors:M=mul(M,F,9)
 assert M==((0,2),(5,0))
reject('omit_one_ordinary_swap',omitted_swap)
result={'reference_certificate_sha256':hashlib.sha256(raw).hexdigest(),'coarse':str(c),'base_ordinary_saving':str(l0),'finite_levels':levels,'depth3_kappa':str(grid),'next_grid_rejected':True,'weighted_leaf_prime_power_cases':cases,'controls_rejected':controls,'scope':'independent exact recurrence and weighted-leaf algebra; written interface composition review separately; no new all-size hypotheses proved'}
print(json.dumps(result,sort_keys=True))
