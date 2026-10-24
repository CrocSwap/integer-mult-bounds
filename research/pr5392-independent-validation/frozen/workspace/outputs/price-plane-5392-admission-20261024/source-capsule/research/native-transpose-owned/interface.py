"""Check the complete local interface and scalar transposition rules.

The normalized interfaces are retained from query-thinned-controllers.
The scalar transpose is classical. Apache-2.0; OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from support import need

def add(a,b):
 out=dict(a)
 for k,v in b.items():
  out[k]=out.get(k,0)+v
  if not out[k]:del out[k]
 return out

def mul(a,b):
 out={}
 for (d,q),v in a.items():
  for (e,r),w in b.items():out=add(out,{(d+e,(q+r)%4):v*w})
 return out

def matmul(a,b):return [[add(mul(a[i][0],b[0][j]),mul(a[i][1],b[1][j])) for j in range(2)] for i in range(2)]
def transpose(a):return [list(r) for r in zip(*a)]

def run():
 zero={};one={(0,0):1};D={(1,0):1}
 F=[[D,zero],[{(1,3):1},D]]
 B=[[D,{(1,1):-1}],[zero,D]]
 J=[[{(0,2):1},zero],[zero,{(0,0):-1}]]
 need(matmul(matmul(J,transpose(B)),J)==F,'Exact complete forward interface')
 wrong=[[one,zero],[zero,{(0,0):-1}]]
 need(matmul(matmul(wrong,transpose(B)),wrong)!=F,'Q squared correction is necessary')
 need(matmul(matmul(J,B),J)!=F,'Circuit order and linear transpose are necessary')
 # Check overwritten COPY, CLEAR and ADD as complete two-register maps.
 def product(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
 clear=[[0,0],[0,1]];copy=[[0,1],[0,1]]
 clearT=transpose(clear)
 need(clearT==clear,'Owned CLEAR transpose')
 samples=0
 for c in (Q(-3,4),Q(-1),Q(1,4),Q(1),Q(2)):
  A=[[1,c],[0,1]];T=[[1,0],[c,1]]
  need(transpose(A)==T,'ADD transpose coefficient')
  S=[[c,0],[0,1]];need(transpose(S)==S,'SCALE transpose')
  samples+=1
 need(product(clear,[[1,0],[1,1]])==transpose(copy),'COPY transpose is ADD then CLEAR')
 from native import Native
 from native_identity import decide
 from check_certificate import check
 phase=Native.identity(9).json();phase['phase']=2
 problem={'axes':9,'roles':1,'generators':{'minus':phase},
          'program':[{'op':'apply','dst':0,'generator':'minus'}],
          'reference':[{'op':'scale','dst':0,'coefficient':-1}]}
 certificate=decide(problem)
 need(certificate['status']=='COUNTEREXAMPLE','Scalar sign must stay outside tensor powers')
 check(problem,certificate)
 # The matrix polynomial is valid for every commuting symmetric Q,D with Q^4=I.
 return {'identity':'F = J B^T J; J = diag(Q^2,-I)',
         'Q_exponents_modulus':4,'D_exponent_is_formal':True,
         'scalar_coefficients_checked':samples,'copy_and_clear_checked':True,
         'wrong_Q_correction_rejected':True,'missing_transpose_rejected':True,'scalar_sign_counterexample':certificate}
