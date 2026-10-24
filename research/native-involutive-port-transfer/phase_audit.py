from pathlib import Path
from fractions import Fraction as Q
import json,gzip,importlib.util,hashlib,time
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('ce_ind',P/'clifford_exact.py');ce=importlib.util.module_from_spec(s);s.loader.exec_module(ce)
a=json.loads(gzip.decompress((P/'INVOLUTIVE-WORD.json.gz').read_bytes()));c=a['canonical'];n=9
# An independent sparse integer Gaussian interpreter; no tableau/compiler evaluator.
def phase(v,k):
 x,y=v;k%=4
 return ((x,y),(-y,x),(-x,-y),(y,-x))[k]
def run(circ,basis):
 d={basis:(1,0)};den=0
 for e in circ:
  typ=e[0]
  if typ=='P':d={sum(((x&r).bit_count()%2)<<i for i,r in enumerate(e[1])):v for x,v in d.items()}
  elif typ=='X':d={x^e[1]:v for x,v in d.items()}
  elif typ=='phase':d={x:phase(v,e[1])for x,v in d.items()}
  elif typ=='D':
   R,alpha=e[1:];out={}
   for x,v in d.items():
    k=sum(alpha[i]for i in range(n)if x>>i&1)+2*sum(((R[i]>>(i+1))&(x>>(i+1))).bit_count()%2 for i in range(n)if x>>i&1)
    out[x]=phase(v,k)
   d=out
  elif typ=='C':
   q,sgn=e[1:];out={}
   for x,(r,i) in d.items():
    v=out.get(x,(0,0));out[x]=(v[0]+r-sgn*i,v[1]+i+sgn*r)
    y=x^q;v=out.get(y,(0,0));out[y]=(v[0]+r+sgn*i,v[1]+i-sgn*r)
   d={x:v for x,v in out.items()if v!=(0,0)};den+=1
  else:raise ValueError(typ)
 while den and all(not(r&1 or i&1)for r,i in d.values()):d={x:(r//2,i//2)for x,(r,i)in d.items()};den-=1
 return d,den
checks=[];t=time.monotonic()
for repair in a['native_repairs']:
 fi=repair['to'];op=ce.canonical_frame(n,c['frames'][1]).adjoint().then(ce.canonical_frame(n,c['frames'][fi]))
 for j in range(512):
  if run(op.circuit,j)!=run(repair['literal_circuit'],j):raise ValueError(('Gaussian column',repair['port'],j))
 checks.append({'port':repair['port'],'exact_basis_columns':512})
out={'status':'PASS_INDEPENDENT_ALL4096_REPAIR_COLUMNS','word_sha256':hashlib.sha256((P/'INVOLUTIVE-WORD.json.gz').read_bytes()).hexdigest(),'checks':checks,'seconds':time.monotonic()-t,'method':'Independent sparse Gaussian-integer interpreter, all 512 basis inputs per repair; compiler evaluator/tableau equality not used for comparisons.'}
print(json.dumps(out,sort_keys=True))
