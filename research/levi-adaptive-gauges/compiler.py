"""Adaptive dyadic row gauges and their inverse-dual schedules. Apache-2.0.
Dugongue with substantial OpenAI assistance; TI_SP/Levi-inspired, no new kappa.
"""
from fractions import Fraction as Q

def need(ok,msg):
 if not ok:raise ValueError(msg)
def valuation(q):
 q=Q(q);need(q!=0 and not q.denominator&(q.denominator-1),'Nonzero dyadic')
 n=abs(q.numerator);return (n&-n).bit_length()-1-(q.denominator.bit_length()-1)
def power(e):return Q(2**e) if e>=0 else Q(1,2**(-e))
def add_cost(q):
 q=Q(q)
 if not q:return 0
 n,d=abs(q.numerator),q.denominator;valuation(q)
 return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
def row_plan(row,target):
 row=[Q(q) for q in row];points=[-valuation(q) for q in row if q]
 if not points:return {'program':[],'new':0,'interval':[0,0],'constant':0}
 constant=sum(add_cost(q)-2*abs(valuation(q)) for q in row if q)
 candidates=[(constant+4*(H-L)+2*sum(max(L-x,0,x-H) for x in points),H-L,L,H) for L in {0,*[min(0,x) for x in points]} for H in {0,*[max(0,x) for x in points]}]
 cost,width,L,H=min(candidates);groups={}
 for i,q in enumerate(row):
  if q:groups.setdefault(min(H,max(L,-valuation(q))),[]).append((i,q))
 program=[];current=0
 def move(b):
  nonlocal current
  if b!=current:
   q=power(b-current);program.append(['scale',['Y',target],q.numerator,q.denominator]);current=b
 move(L)
 for b in sorted(groups):
  move(b)
  for i,q in groups[b]:
   q*=power(b);program.append(['add',['Y',target],['X',i],q.numerator,q.denominator])
 move(H);move(0)
 return {'program':program,'new':cost,'interval':[L,H],'constant':constant,'support_indices':[i for i,q in enumerate(row) if q]}
def compile_rows(matrix):
 M=[[Q(q) for q in row] for row in matrix]
 need(M and M[0] and all(len(row)==len(M[0]) for row in M),'Nonempty rectangular matrix')
 rows=[row_plan(row,j) for j,row in enumerate(M)]
 return {'program':[e for r in rows for e in r['program']],'new':sum(r['new'] for r in rows),'rows':rows,'owned_peak':0,'mechanism':'adaptive-row-gauge'}
def inverse_dual(program):
 def flip(role):return ['Y' if role[0]=='X' else 'X',role[1]]
 out=[]
 # The group map A -> A^{-T} is a homomorphism: keep execution order.
 for e in program:
  if e[0]=='add':out.append(['add',flip(e[2]),flip(e[1]),-e[3],e[4]])
  else:
   need(e[0]=='scale','Invertible scalar-only dual');q=1/Q(e[2],e[3]);out.append(['scale',flip(e[1]),q.numerator,q.denominator])
 return out
