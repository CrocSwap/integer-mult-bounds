"""Check physical transposition and exact phase recipes on source classes.

Uses the credited exact Clifford compiler. Ali Romman with OpenAI Codex
assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from copy import deepcopy
import json
from support import HERE,ROOT,read,need,load,CE,packed
ce=load(CE,'transpose_exact_clifford')

def primitive(n,e,conjugate=False):
 tag=e[0]
 if tag=='P':return ce.perm(n,tuple(e[1]))
 if tag=='D':return ce.diag(n,tuple(e[1]),tuple((-v)%4 for v in e[2]) if conjugate else tuple(e[2]))
 if tag=='C':return ce.cgate(n,e[1],-e[2] if conjugate else e[2])
 if tag=='X':return ce.xgate(n,e[1])
 if tag=='phase':
  k=(-e[1] if conjugate else e[1])%4
  return ce.Op(n,ce.identity(n),[('phase',k)])
 raise ValueError(tag)

def conj(op):
 ans=ce.ident(op.n)
 for e in op.circuit:ans=ans.then(primitive(op.n,e,True))
 return ans

def trans(op):
 ans=ce.ident(op.n)
 for e in reversed(op.circuit):
  if e[0]=='P':e=('P',ce.inv(tuple(e[1]),op.n))
  ans=ans.then(primitive(op.n,e))
 return ans

def decode(r):
 from native import Native
 Native.parse({k:list(v) if isinstance(v,tuple) else v for k,v in r.items()},9)
 n=len(r['matrix_rows'])
 q=tuple(r['quadratic_rows']);a=r['linear_Z4']
 need(ce.transpose(q,n)==q and all(a[i]%2==((q[i]>>i)&1) for i in range(n)),'Valid symmetric Gaussian phase recipe')
 return ce.diag(n,tuple(r['quadratic_rows']),tuple(r['linear_Z4'])).then(ce.perm(n,tuple(r['matrix_rows']))).then(ce.xgate(n,r['offset'])).then(primitive(n,('phase',r['phase'])))


def run(x):
 c=x['canonical'];p=x['programs']['backward']
 from word import base
 candidate=base.construct(x)['programs']['backward']
 expected=sorted({(e[3],e[4],e[5]) for e in candidate if e[0]=='climb'}|{(e[2],e[3],e[4]) for e in candidate if e[0]=='center'})
 receipts=read(HERE/'PHASES.json.gz')
 need([(r['old'],r['new'],r['rank']) for r in receipts]==expected,'Every transposed paid class exactly once')
 frames={}
 def frame(i):
  if i not in frames:frames[i]=ce.canonical_frame(9,c['frames'][i])
  return frames[i]
 def check_paid(row):
  a,b,r=row['old'],row['new'],row['rank']
  want=trans(conj(frame(a).adjoint().then(frame(b))))
  physical=decode(row['right']).then(ce.fourier(9,range(r))).then(decode(row['left']))
  need(physical.tab==want.tab and physical.zero_state()==want.zero_state(),'Transposed paid absolute phase')
  need(ce.rank([a for a,b,p in want.tab[9:]])==r,'Exact transposed paid rank')
 for i,row in enumerate(receipts):
  check_paid(row)
  if i%500==0:print('PAID_PHASES',i+1,len(receipts),flush=True)
 maps={}
 for w in c['warps']:
  G=ce.transpose(tuple(w['G_columns']),9);tr=ce.transpose(ce.inv(G,9),9)
  q=tuple((1<<i)^sum(ce.parity(a&b)<<j for j,b in enumerate(tr)) for i,a in enumerate(tr))
  maps[w['op']]=ce.perm(9,G).then(ce.diag(9,q))
 warps=sorted({(e[2],e[3],e[4]) for e in p if e[0]=='warp'})
 from native import Native
 columns=0
 for op,a,b in warps:
  K=maps[abs(op)] if op>0 else maps[abs(op)].adjoint()
  old=conj(frame(a).adjoint().then(K).then(frame(b)))
  want=trans(old)
  new=frame(b).adjoint().then(K.adjoint()).then(frame(a))
  need(want.tab==new.tab and want.zero_state()==new.zero_state(),'Exact inverse primal native warp')
  _,original=ce.monomial(old);_,changed=ce.monomial(want)
  def parse(r):return Native.parse({k:list(v) if isinstance(v,tuple) else v for k,v in r.items()},9)
  oldn,newn=parse(original),parse(changed)
  for a0 in range(512):
   b0=oldn.image(a0)
   need(newn.image(b0)==a0 and newn.exponent(b0)==oldn.exponent(a0),'Literal transpose entry and phase')
   columns+=1
 bad=deepcopy(receipts[0]);bad['left']['phase']=(bad['left']['phase']+2)%4
 try:check_paid(bad)
 except ValueError as error:control=str(error)
 else:raise ValueError('Wrong absolute phase accepted')
 # C_q is symmetric and C_q squared is the exact native translation X_q.
 for q in c['ports']:
  Q=ce.cgate(9,q);square=Q.then(Q);native=ce.xgate(9,q)
  need(square.tab==native.tab and square.zero_state()==native.zero_state(),'All actual port Q squared phases')
  need(trans(Q).tab==Q.tab and trans(Q).zero_state()==Q.zero_state(),'Symmetric port Gaussian')
 for rank in (4,7,8,9):
  C=ce.fourier(9,range(rank));T=trans(C)
  need(C.tab==T.tab and C.zero_state()==T.zero_state(),'Every productive standard Gaussian is symmetric')
  fixed=conj(C).then(ce.xgate(9,(1<<rank)-1))
  need(fixed.tab==C.tab and fixed.zero_state()==C.zero_state(),'Exact helper orientation correction')
 return {'paid_classes':len(receipts),'native_warp_classes':len(warps),
         'literal_native_transpose_columns':columns,'Q_squared_ports':len(c['ports']),
         'symmetric_helper_ranks':[4,7,8,9],'wrong_absolute_phase_rejected':control,
         'source_clifford_sha256':sha256((ROOT/CE).read_bytes()).hexdigest()}
