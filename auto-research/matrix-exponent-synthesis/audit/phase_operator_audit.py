import sys as _checked_runtime
if _checked_runtime.flags.optimize:
    raise SystemExit('Checked audit requires Python without -O')
from pathlib import Path
import json,random,time,sys,hashlib
from fractions import Fraction as Q
base=Path(sys.argv[1]);dest=Path(sys.argv[2]);start=time.perf_counter()
d=json.loads((base/'circuit/flat16_2208_integer_circuit.json').read_text())
def gadd(x,y):return x[0]+y[0],x[1]+y[1]
def gscale(c,x):return c*x[0],c*x[1]
def gm(x,y):return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]
def phase(x,k):
 for _ in range(k%4):x=-x[1],x[0]
 return x
def conv(x,y):
 n=len(x);z=[(0,0)]*n
 for a,xa in enumerate(x):
  if xa==(0,0):continue
  for b,yb in enumerate(y):
   if yb!=(0,0):z[a^b]=gadd(z[a^b],gm(xa,yb))
 return z

def Cnumer(n,u,k):
 # C_u=((1+i)I+(1-i)X_u)/2, followed by one common unit phase.
 z=[(0,0)]*n;z[0]=phase((1,1),k);z[u]=gadd(z[u],phase((1,-1),k));return z

def lin(entries,values,n):
 z=[(0,0)]*n
 for index,c in entries:
  for g,x in enumerate(values[index]):z[g]=gadd(z[g],gscale(c,x))
 return z
trials=[];rng=random.Random(462208)
for dimension in (2,3):
 n=1<<dimension
 for trial in range(2):
  values=[Cnumer(n,rng.randrange(n),rng.randrange(4)) for _ in range(512)]
  products=[conv(lin(g['left'],values,n),lin(g['right'],values,n)) for g in d['gates']]
  recovered=[]
  for out in d['output_numerators']:
   raw=lin(out['terms'],products,n)
   assert all(a%8==b%8==0 for a,b in raw)
   recovered.append([(a//8,b//8) for a,b in raw])
  for i in range(16):
   for j in range(16):
    reference=[(0,0)]*n
    for k in range(16):reference=[gadd(x,y) for x,y in zip(reference,conv(values[16*i+k],values[256+16*k+j]))]
    assert recovered[16*i+j]==reference
  trials.append({'dimension':dimension,'translation_algebra_size':n,'trial':trial,'operator_matrix_outputs':256,'exact_kernel_coefficients':256*n,'mixed_operator_product_slots':2208,'input_common_binary_denominator':2,'output_common_product_binary_denominator':4})

def matrix(n,u,kind,v=0):
 if kind=='C':return [[gscale(Q(1,2),gadd((1,1) if y==x else(0,0),(1,-1) if y==x^u else(0,0))) for y in range(n)]for x in range(n)]
 if kind=='Z':return [[(Q((-1)**((x&v).bit_count()%2)),Q(0)) if x==y else(Q(0),Q(0)) for y in range(n)]for x in range(n)]
 if kind=='X':return [[(Q(1),Q(0)) if y==x^u else(Q(0),Q(0)) for y in range(n)]for x in range(n)]
def mm(A,B):
 n=len(A);out=[[(Q(0),Q(0)) for _ in range(n)]for _ in range(n)]
 for i in range(n):
  for j in range(n):
   for k in range(n):out[i][j]=gadd(out[i][j],gm(A[i][k],B[k][j]))
 return out
controls=[]
for dim in (2,3):
 n=1<<dim;u=1
 for v in (1,2):
  C=matrix(n,u,'C');Z=matrix(n,0,'Z',v);X=matrix(n,u,'X')
  cz,zc=mm(C,Z),mm(Z,C)
  defect=[[gadd(cz[i][j],gscale(-1,zc[i][j]))for j in range(n)]for i in range(n)]
  if (u&v).bit_count()%2==0:
   assert all(c==(0,0)for row in defect for c in row);rank=0
  else:
   xz=mm(X,Z)
   expected=[[gm((1,-1),x)for x in row]for row in xz]
   assert defect==expected
   assert all(sum(c!=(0,0)for c in row)==1 for row in defect)
   assert all(sum(defect[i][j]!=(0,0)for i in range(n))==1 for j in range(n))
   rank=n
  controls.append({'D':dim,'u':u,'v':v,'dot_parity':(u&v).bit_count()%2,'C_Z_commutator_rank':rank,'off_domain_Rosowski_first_column_equals_commutator':True,'identity':'[C_u,Z_v]=(1-i) X_u Z_v when dot(u,v)=1; zero when dot=0'})
receipt={'status':'PASS','source_pin':'7203497dc990e47c2391bff1b9863408d817faeb','model':'commutative XOR translation convolution algebra over Gaussian dyadics; C_u phase elements','actual_2208_circuit_trials':trials,'exact_operator_matrix_outputs':sum(t['operator_matrix_outputs']for t in trials),'exact_kernel_coefficients':sum(t['exact_kernel_coefficients']for t in trials),'noncommuting_and_orthogonal_controls':controls,'time_seconds':time.perf_counter()-start,'scope':'Valid restricted coefficient algebra, NOT arbitrary matrix-valued blocks. Operator convolution/action and basis transports carry separate costs. No new interchange child list, physical tape schedule, tensor-rank record or integer kappa.'}
dest.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
