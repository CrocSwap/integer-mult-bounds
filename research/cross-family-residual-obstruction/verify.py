"""Exact obstruction to replacing one residual by factors on different families.
Read-only review of PR448 head9b966d8188e1cadd00aa834078ee6a8742a9d9b4.
Chafreaky with OpenAI Codex assistance. Standard library only.
"""
from itertools import product
from pathlib import Path
import hashlib,json

def bit(q,m,a,b):
 states=list(product(range(2),product(range(q),repeat=2*m)))
 index={x:i for i,x in enumerate(states)}
 def perm(first,second):
  out=[]
  for family,word in states:
   w=list(word)
   for i in (first if family==0 else second):w[i],w[m+i]=w[m+i],w[i]
   out.append(index[family,tuple(w)])
  assert sorted(out)==list(range(len(states))) and all(out[out[i]]==i for i in range(len(out)))
  return out
 A=list(range(a));B=list(range(a,a+b))
 whole=perm(A+B,[]);left=perm(A,[]);right=perm(B,[]);split=perm(A,B)
 compose=[left[right[i]] for i in range(len(left))]
 assert compose==whole,'same-family factorization must hold'
 count=lambda p:sum(i==j for i,j in enumerate(p))
 w,s=count(whole),count(split)
 assert w==q**(2*m)+q**(2*m-a-b)
 assert s==q**(2*m-a)+q**(2*m-b)
 assert w-s==q**(2*m-a-b)*(q**a-1)*(q**b-1)>0
 bad=next(i for i in range(len(states)) if whole[i]!=split[i])
 return dict(q=q,m=m,ranks=[a,b],dimension=len(states),whole_trace=w,split_trace=s,
  same_family_identity=True,not_similar_by_trace=True,
  distinct_column=dict(input=states[bad],whole=states[whole[bad]],split=states[split[bad]]),
  whole_sha256=hashlib.sha256(json.dumps(whole).encode()).hexdigest(),split_sha256=hashlib.sha256(json.dumps(split).encode()).hexdigest())

def complex_case(m,a,b):
 # In the exact Fourier basis C_u has multiplier i^parity(u.y).
 # Store eigenvalues by their exponents modulo four; sum as Gaussian integers.
 whole=[];split=[]
 for family in range(2):
  for y in range(1<<m):
   whole.append((y&((1<<(a+b))-1)).bit_count()%4 if family==0 else 0)
   mask=(1<<a)-1 if family==0 else ((1<<b)-1)<<a
   split.append((y&mask).bit_count()%4)
 def trace(exponents):
  c=[exponents.count(i) for i in range(4)];return [c[0]-c[2],c[1]-c[3]]
 w,s=trace(whole),trace(split);assert w!=s
 # Same-family products add the Fourier exponents, including their phases.
 for y in range(1<<m):assert ((y&((1<<a)-1)).bit_count()+((y>>a)&((1<<b)-1)).bit_count())%4==(y&((1<<(a+b))-1)).bit_count()%4
 return dict(m=m,ranks=[a,b],dimension=2*(1<<m),whole_trace_gaussian_integer=w,split_trace_gaussian_integer=s,same_family_identity=True,not_similar_by_trace=True)

rows=[bit(3,2,1,1),bit(3,3,1,1),bit(3,3,1,2)]
complex_rows=[complex_case(2,1,1),complex_case(3,1,2)]
# The actual bit family has m=64. No huge matrix is allocated.
actual=[]
for a in range(1,8):
 b=8-a;q=3;m=64
 w=q**(2*m)+q**(2*m-a-b);s=q**(2*m-a)+q**(2*m-b)
 assert w>s;actual.append(dict(m=m,q=q,ranks=[a,b],whole_trace=str(w),split_trace=str(s),difference=str(w-s)))
def mul(z,w):return (z[0]*w[0]-z[1]*w[1],z[0]*w[1]+z[1]*w[0])
def power(n):
 z=(1,0)
 for _ in range(n):z=mul(z,(1,1))
 return z
def scale(n,z):return (n*z[0],n*z[1])
actual_complex=[]
for a in range(1,9):
 b=9-a;m=73
 z=scale(2**(m-9),power(9));whole=(z[0]+2**m,z[1])
 x=scale(2**(m-a),power(a));y=scale(2**(m-b),power(b));split=(x[0]+y[0],x[1]+y[1])
 pa,pb=power(a),power(b)
 difference=scale(2**(m-9),mul((2**a-pa[0],-pa[1]),(2**b-pb[0],-pb[1])))
 assert difference==(whole[0]-split[0],whole[1]-split[1]) and difference!=(0,0)
 actual_complex.append(dict(m=m,ranks=[a,b],whole_trace_gaussian_integer=whole,split_trace_gaussian_integer=split,difference=difference))
out=dict(status='PASS_CROSS_FAMILY_ROUTE_OBSTRUCTION',reviewed_pr=448,reviewed_head='9b966d8188e1cadd00aa834078ee6a8742a9d9b4',
 bit=rows,complex=complex_rows,actual_bit_rank8=actual,actual_complex_rank9=actual_complex,
 conclusion='D_(P1+P2) on one family plus identity on a second family is not similar to D_P1 on the first and D_P2 on the second. The analogous exact complex residual also fails the trace invariant.',
 scope='Refutes the stated elementary-permutation derivation for splitting one residual across two families. Does not rule out a different compiler with additional operations, changed storage or charged work.')
expected=json.loads(Path(__file__).with_name('EXPECTED.json').read_text())
assert json.loads(json.dumps(out))==expected, 'exact counterexample differs from frozen output'
print(json.dumps(out,indent=2))
