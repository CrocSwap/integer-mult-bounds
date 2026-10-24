"""Independent source-restored raw-dual derivation; no candidate emitter import.
Substantial OpenAI Codex assistance; Apache-2.0; upstream pins in SOURCES.json.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from collections import Counter
import types, json, gzip, sys
ROOT=Path(__file__).resolve().parent
S=(0,7,20,23,86,93,108,111)
def require(v,m):
 if not v: raise ValueError(m)
def mm(A,B):
 return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*B)] for row in A]
def sub(A,B):return [[x-y for x,y in zip(a,b)] for a,b in zip(A,B)]
def conjugate(op,ce):
 circ=[]
 for e in op.circuit:
  if e[0]=='C':circ.append(('C',e[1],-e[2]))
  elif e[0]=='D':circ.append(('D',e[1],tuple((-a)%4 for a in e[2])))
  elif e[0]=='phase':circ.append(('phase',(-e[1])%4))
  else:circ.append(e)
 return ce.Op(op.n,tuple((x,z,(-a)%4) for x,z,a in op.tab),circ)
def sparse(circuit,k,n=9):
 # Gaussian-integer interpreter, independent of ce.zero_state/tableau code.
 values={k:(1,0)};power=0
 for e in circuit:
  tag=e[0]
  if tag=='P':values={sum(((x&r).bit_count()%2)<<j for j,r in enumerate(e[1])):v for x,v in values.items()}
  elif tag=='X':values={x^e[1]:v for x,v in values.items()}
  elif tag in ('D','phase'):
   new={}
   for x,(a,b) in values.items():
    if tag=='phase':phase=e[1]
    else:
     M,alpha=e[1:];phase=sum(alpha[j] for j in range(n) if (x>>j)&1)
     phase+=2*sum(((M[j]>>(j+1))&(x>>(j+1))).bit_count()%2 for j in range(n) if (x>>j)&1)
    new[x]=((a,b),(-b,a),(-a,-b),(b,-a))[phase%4]
   values=new
  elif tag=='C':
   q,sgn=e[1:];new={}
   for x,(a,b) in values.items():
    for y,v in ((x,(a-sgn*b,b+sgn*a)),(x^q,(a+sgn*b,b-sgn*a))):
     u=new.get(y,(0,0));new[y]=(u[0]+v[0],u[1]+v[1])
   values={x:v for x,v in new.items() if v!=(0,0)};power+=1
  else:raise ValueError(('unsupported exact gate',tag))
  while power and all(a%2==b%2==0 for a,b in values.values()):
   values={x:(a//2,b//2) for x,(a,b) in values.items()};power-=1
 return values,power

def main():
 origins=json.loads((ROOT/'SOURCES.json').read_text())
 for row in origins['files']:require(sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'Pinned bytes '+row['path'])
 source=json.loads(gzip.decompress((ROOT/'inputs/SOURCE-WORD.json.gz').read_bytes()))
 coded=json.loads(gzip.decompress((ROOT/'inputs/CODED-WORDS.json.gz').read_bytes()))
 forward=json.loads(gzip.decompress((ROOT/'inputs/INVOLUTIVE-WORD.json.gz').read_bytes()))
 c=source['canonical'];require(coded['canonical']['frames']==c['frames'],'Same physical frames')
 R=[[Q(v) for v in row] for row in json.loads((ROOT/'inputs/R.json').read_text())]
 K=[[R[k][i]/4 for k in range(8)] for i in range(112)]
 P=[K[i] if i in S else [Q(0)]*8 for i in range(112)]
 I8=[[Q(i==j) for j in range(8)] for i in range(8)]
 require(mm(R,K)==[[14*x for x in r] for r in I8],'RK=14I')
 require(mm(R,P)==I8,'RP=I')
 KR=mm(K,R);I=[[Q(i==j) for j in range(112)] for i in range(112)]
 A=sub(I,KR);D=[[12*x for x in row] for row in mm(P,R)]
 F=[[a+d for a,d in zip(ar,dr)] for ar,dr in zip(A,D)]
 require(F==[[Q(v) for v in row] for row in forward['F']],'Actual4935 target F')
 require(mm(F,F)==I,'F involution')
 require({j for j,row in enumerate(D) if any(row)}==set(S),'Only selected Y source rows')
 coeff=Counter(-x for row in D for x in row if x)
 # Backward normalized x is x-A^T y. The suffix adds -D^T y.
 require(sub([[A[j][i] for j in range(112)] for i in range(112)],
             [[-D[j][i] for j in range(112)] for i in range(112)])==[[F[j][i] for j in range(112)] for i in range(112)],'Backward sign/transpose')
 require(any(A[j][i]-D[j][i]!=F[j][i] for i in range(112) for j in range(112)),'Wrong-sign semantic control')
 ce=types.ModuleType('independent_rawdual_ce');sys.modules[ce.__name__]=ce
 exec(compile((ROOT/'inputs/clifford_exact.py').read_bytes(),'pinned_ce','exec'),ce.__dict__)
 barT=conjugate(ce.canonical_frame(9,c['frames'][1]),ce)
 require(c['final'][:112]==[1]*112,'Common full X exit')
 repairs=[];wrong_conjugation=False;wrong_adjoint=False
 for j in S:
  frame=c['final'][112+j];V=ce.canonical_frame(9,c['frames'][frame]);barV=conjugate(V,ce)
  require(len(c['frames'][frame])==8,'Pure selected rank8Y source')
  L=barV.adjoint().then(barT);cert,compiled=ce.lower_child(L)
  require(cert['rank']==1,'Actual rank1 lift')
  require(L.tab==compiled.tab,'Literal compiler tableau')
  # C0=barV y; lifted C0 must equal barT y including global phase.
  for k in range(512):
   target=sparse(barT.circuit,k)
   require(sparse(barV.circuit+compiled.circuit,k)==target,'All512 actual phase/composition columns')
   if not wrong_conjugation:
    wrong_conjugation=sparse(barV.circuit+V.adjoint().then(ce.canonical_frame(9,c['frames'][1])).circuit,k)!=target
   if not wrong_adjoint:wrong_adjoint=sparse(barV.circuit+L.adjoint().circuit,k)!=target
  repairs.append({'port':j,'Y_owner':112+j,'frame':frame,'rank':cert['rank'],'phase_columns':512,'scatter_count':sum(bool(x) for x in D[j]),'compiled_circuit_sha256':sha256(json.dumps(compiled.circuit,separators=(',',':')).encode()).hexdigest()})
 require(wrong_conjugation,'No-conjugation mutation rejected')
 require(wrong_adjoint,'Adjoint/reversed lift mutation rejected')
 out={'status':'PASS_INDEPENDENT_RAW_DUAL_DERIVATION','upstream_head':'64c9f99693c92fb370096fb43dbc58a085b30e36','selected_ports':S,'phase_columns':4096,'repairs':repairs,'scatter_coefficients':{str(v):n for v,n in sorted(coeff.items())},'added_paid':{'1':8},'complete_expected_paid':{'1':2209,'2':412,'3':510,'4':127,'5':40},'owned_scratch':'Only C0 COPY/CLEAR; Y/main/helper owners never overwritten or cleared','suffix':'COPY barV_j y_j; apply barF9 barV_j^*; scatter -12(PR)_(j,i); CLEAR C0','endpoint':'x-F^T y, y unchanged; all independent helper jobs unchanged','semantic_controls':['wrong correction sign','unconjugated physical lift','adjoint/reversed physical lift'],'full_source_replay':'Pending independent replay of frozen A word; inherited4929 physical event semantics distinct from new4096 phase checks','source_mutating_variant':False,'new_kappa':None}
 print(json.dumps(out,indent=2))
 if '--emit' in sys.argv:(ROOT/'DERIVATION.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
