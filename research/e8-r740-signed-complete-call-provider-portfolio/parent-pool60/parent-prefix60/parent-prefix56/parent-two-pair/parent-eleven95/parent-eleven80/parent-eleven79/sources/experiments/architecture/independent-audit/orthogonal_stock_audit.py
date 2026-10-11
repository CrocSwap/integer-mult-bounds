from pathlib import Path
import json,hashlib,itertools
P=Path(__file__).resolve().parent;R=P.parents[2];S=R/'experiments/verification/proposal-scout/pr445'
# Enumeration is a diagnostic for the all-q induction, not its justification.
tests=[]
for q in (3,5,7):
 for diag in ((1,),(1,1),(1,2),(1,1,1)):
  n=len(diag);vectors=[v for v in itertools.product(range(q),repeat=n) if sum(a*x*x for a,x in zip(diag,v))%q==diag[0]%q]
  assert len(vectors)<=2*q**(n-1)
  tests.append(dict(q=q,diagonal=diag,norm_fiber=len(vectors),fiber_bound=2*q**(n-1)))
m=78;physical=9609;child=56;t=0
while 3**t<=physical:t+=1
assert t==9 and m*m<=2*child*child and m**3>2*child**3
stock=m*(m+1)//2+t;row=3*stock+9909+252
assert stock==3090 and row==19431 and row<20161
out=dict(status='PASS_UNIFORM_GROUP_STOCK_AND_CONDITIONAL_ROW_ARITHMETIC',uniform_proof='In odd characteristic any nondegenerate symmetric form has a diagonal basis with all diagonal norms nonzero. A prescribed nonzero norm fiber has at most 2q^(d-1) points by fixing d-1 coordinates. Such a vector has a nondegenerate complement. Choosing successive basis images bounds the group by the product of those fiber bounds, namely 2^m q^(m(m-1)/2), strictly less than q^(m(m+1)/2) for q>=3.',diagnostics=tests,dimension=m,physical=physical,stock_exponent=stock,row_coefficient=row,halving_depth=3,remaining='Uniform theorem changes stock only, not enumeration/routing time. Numeric restored-row conversion requires inherited finite coefficient contract 9909+252 and depth conversion; cached inherited tex confirms restored sequential reuse and asymptotic reserve only. Native profile is F2 and cannot replace actual signed75 inventory or prefix invoice.',pins={f:hashlib.sha256((S/f).read_bytes()).hexdigest() for f in ('code/row_bound.py','proof/INHERITED-ROW-DIVISOR.tex','PROOF.md')})
(P/'ORTHOGONAL-STOCK-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',row,stock,len(tests))
