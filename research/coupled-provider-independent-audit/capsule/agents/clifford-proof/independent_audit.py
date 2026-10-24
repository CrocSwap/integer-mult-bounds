"""Bounded independent Fraction-pair oracle; submitted modules are DUTs only."""
from fractions import Fraction as F
from pathlib import Path
import sys, json, hashlib, time
HERE=Path(__file__).resolve().parent
PKG=HERE.parent.parent/'clifford-repository/research/clifford-tensor-gram'
Z=(F(0),F(0)); O=(F(1),F(0)); I=(F(0),F(1))
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[0],-a[1])
def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def conj(a):return (a[0],-a[1])
def power(a,n):
 out=O
 for _ in range(n):out=mul(out,a)
 return out
def scalar(x):
 if isinstance(x,int):return (F(x),F(0))
 return {'i':I,'-i':neg(I)}.get(x,(F(0),F(0))) if x in ('i','-i') else (F(x),F(0))
def external(x):return (F(x.real),F(x.imag))
def eye(d):return tuple(tuple(O if x==y else Z for y in range(d)) for x in range(d))
def zero(d):return tuple(tuple(Z for _ in range(d)) for _ in range(d))
def scale(a,c):return tuple(tuple(mul(c,x) for x in r) for r in a)
def plus(a,b):return tuple(tuple(add(x,y) for x,y in zip(r,s)) for r,s in zip(a,b))
def mm(a,b):
 bt=tuple(zip(*b))
 return tuple(tuple(sumg(mul(x,y) for x,y in zip(r,c)) for c in bt) for r in a)
def sumg(xs):
 out=Z
 for x in xs:out=add(out,x)
 return out
def adj(a):return tuple(tuple(conj(a[y][x]) for y in range(len(a))) for x in range(len(a)))
def trace(a):return sumg(a[j][j] for j in range(len(a)))
def kron(a,b):return tuple(tuple(mul(a[x][y],b[u][v]) for y in range(len(a)) for v in range(len(b))) for x in range(len(a)) for u in range(len(b)))
def tensor(a,f):
 out=((O,),)
 for _ in range(f):out=kron(out,a)
 return out
def gate(n,g):
 d=1<<n;k=g[0];out=[[Z]*d for _ in range(d)]
 for y in range(d):
  if k=='phase':out[y][y]=power(I,g[1]%4)
  elif k=='X':out[y^g[1]][y]=O
  elif k=='P':out[sum((((r&y).bit_count()&1)<<j) for j,r in enumerate(g[1]))][y]=O
  elif k=='D':
   rows,alpha=g[1:];e=sum(a*((y>>j)&1) for j,a in enumerate(alpha))
   e+=2*sum(((y>>j)&1)*((y>>k)&1) for j in range(n) for k in range(j+1,n) if (rows[j]>>k)&1)
   out[y][y]=power(I,e%4)
  elif k=='C':
   q,s=g[1:];a=(F(1,2),F(s,2));b=conj(a)
   out[y][y]=add(out[y][y],a);out[y^q][y]=add(out[y^q][y],b)
  else:raise ValueError(k)
 return tuple(tuple(r) for r in out)
def circuit(n,gs):
 out=eye(1<<n)
 for g in gs:out=mm(gate(n,g),out)
 return out
def bank(problem):return {k:circuit(problem['axes'],v) for k,v in problem['operators'].items()}
def direct_endpoint(p,seq,f):
 r=p['roles'];d=(1<<p['axes'])**f;ops={k:tensor(a,f) for k,a in bank(p).items()}
 rows=[[eye(d) if j==k else zero(d) for k in range(r)] for j in range(r)]
 for op in seq:
  k=op['op'];dst=op['dst'];src=op.get('src',dst)
  if k=='swap':rows[dst],rows[src]=rows[src],rows[dst];continue
  if k=='scale':rows[dst]=[scale(a,scalar(op['coefficient'])) for a in rows[dst]];continue
  image=rows[src][:]
  if k in ('apply','query'):
   a=ops[op['symbol']];a=adj(a) if op.get('inverse',False) else a
   image=[mm(a,b) for b in image]
  if k=='apply':rows[dst]=image
  else:rows[dst]=[plus(a,scale(b,scalar(op.get('coefficient',1)))) for a,b in zip(rows[dst],image)]
 return rows
def exact_terms(p,seq):
 r=p['roles'];d=1<<p['axes'];ops=bank(p)
 rows=[[{eye(d):O} if j==k else {} for k in range(r)] for j in range(r)]
 def combine(a,b,c):
  out=dict(a)
  for m,v in b.items():out[m]=add(out.get(m,Z),mul(c,v))
  return {m:v for m,v in out.items() if v!=Z}
 for op in seq:
  k=op['op'];dst=op['dst'];src=op.get('src',dst)
  if k=='swap':rows[dst],rows[src]=rows[src],rows[dst];continue
  if k=='scale':rows[dst]=[combine({},a,scalar(op['coefficient'])) for a in rows[dst]];continue
  image=[dict(a) for a in rows[src]]
  if k in ('apply','query'):
   a=ops[op['symbol']];a=adj(a) if op.get('inverse',False) else a
   image=[{mm(a,m):v for m,v in b.items()} for b in image]
  if k=='apply':rows[dst]=image
  else:rows[dst]=[combine(a,b,scalar(op.get('coefficient',1))) for a,b in zip(rows[dst],image)]
 return rows

def rank_mod(a,p=65537):
 a=[r[:] for r in a];i=0
 for j in range(len(a[0])):
  k=next((k for k in range(i,len(a)) if a[k][j]),None)
  if k is None:continue
  a[i],a[k]=a[k],a[i];inv=pow(a[i][j],-1,p);a[i]=[(x*inv)%p for x in a[i]]
  for k in range(i+1,len(a)):
   c=a[k][j]
   if c:a[k]=[(x-c*y)%p for x,y in zip(a[k],a[i])]
  i+=1
 return i

def main():
 start=time.monotonic();sys.path.insert(0,str(PKG));import quadratic as dutq;import compact as dutc;import check_witness as dutw
 counts={'native_entries':0,'native_traces':0,'conditional_inners':0,'programs':0,'dense_tensor_widths':0,'literal_witnesses':0,'rejected_witness_mutations':0}
 words=[(0,[['phase',3]]),(1,[['C',0,1]]),(1,[['C',1,-1],['D',[1],[1]],['X',1],['phase',1]]),(2,[['D',[3,1],[1,0]],['P',[1,3]],['C',3,1],['X',2],['C',1,-1],['phase',3]])]
 # The last diagonal rows must be symmetric: row 0 has off-diagonal 1 and row 1 has bit 0.
 for n,gs in words:
  a=circuit(n,gs);path=dutq.Paths(n,gs);d=1<<n
  assert mm(a,adj(a))==eye(d)
  for x in range(d):
   for y in range(d):assert external(path.entry(x,y))==a[x][y];counts['native_entries']+=1
  assert external(path.trace())==trace(a);counts['native_traces']+=1
  inv=dutq.Paths(n,dutq.inverse_circuit(n,gs));b=adj(a)
  for xp,yp in [((),()),((0,),())] if n else [((),())]:
   expect=sumg(mul(conj(a[x][y]),b[x][y]) for x in range(d) for y in range(d) if all((x>>j)&1==bit for j,bit in enumerate(xp)))
   assert external(dutq.partial_inner(path,inv,xp,yp))==expect;counts['conditional_inners']+=1
 def op(kind,dst=0,**kw):return {'op':kind,'dst':dst,**kw}
 cases=[]
 for n in range(3):
  ops={'I':[],'phase':[['phase',1]],'C':[['C',(1<<n)-1,1]],'S':[['D',[1<<j for j in range(n)],[1]*n]]}
  def case(label,program,reference=()):cases.append((label,{'axes':n,'roles':2,'operators':ops,'program':program,'reference':list(reference)}))
  case('native_phase_vs_outer_scalar', [op('apply',symbol='phase')],[op('scale',coefficient='i')])
  case('C_inverse',[op('apply',symbol='C'),op('apply',symbol='C',inverse=True)])
  case('query_sign',[op('query',src=0,dst=1,symbol='C',coefficient='-1')],[op('query',src=0,dst=1,symbol='C',coefficient='1')])
  case('self_query_snapshot',[op('query',src=0,symbol='C',coefficient='1/2'),op('apply',symbol='S')])
  case('noncommuting_order',[op('apply',symbol='C'),op('apply',symbol='S')],[op('apply',symbol='S'),op('apply',symbol='C')])
  case('dirty_second_input',[op('scale',dst=1,coefficient='0')])
  case('swap_and_scale',[op('swap',src=1),op('scale',coefficient='1/2')])
  case('coefficient_grouping',[op('query',src=0,dst=1,symbol='C',coefficient='1/2'),op('query',src=0,dst=1,symbol='C',coefficient='1/2')],[op('query',src=0,dst=1,symbol='C')])
 for label,p in cases:
  left,right=exact_terms(p,p['program']),exact_terms(p,p['reference']);equal=left==right
  cert=dutc.certify(p);assert cert['equivalent_at_all_positive_widths']==equal,(label,p['axes']);counts['programs']+=1
  for f in range(1,3 if p['axes']==2 else 4):
   a,b=direct_endpoint(p,p['program'],f),direct_endpoint(p,p['reference'],f)
   if equal:assert a==b
   # Direct dense endpoints independently bind each exact-matrix expansion.
   for output in range(2):
    for inp in range(2):
     expected=zero((1<<p['axes'])**f)
     for m,c in left[output][inp].items():expected=plus(expected,scale(tensor(m,f),c))
     assert a[output][inp]==expected
   counts['dense_tensor_widths']+=1
  if not equal:
   failure=cert['failure'];w=failure['witness'];o,j=failure['output_role'],failure['input_role']
   def evaluate(terms):return sumg(mul(c,product_entries(m,w['output_tuple'],w['input_tuple'])) for m,c in terms.items())
   value=add(evaluate(left[o][j]),neg(evaluate(right[o][j])))
   assert value!=Z and value==external(dutc.c.G(w['discrepancy']));counts['literal_witnesses']+=1
   dense={**p,'operators':{k:[[to_string(x) for x in r] for r in m] for k,m in bank(p).items()}}
   dc={**cert,'schema':'clifford-tensor-gram/v1','problem_sha256':hashlib.sha256(json.dumps(dense,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
   assert external(dutw.G(dutw.check(dense,dc)))==value
   for mutation in ('wrong_value','wrong_digest','positive_flag','wrong_width'):
    mc=json.loads(json.dumps(dc))
    if mutation=='wrong_value':mc['failure']['witness']['discrepancy']='0'
    elif mutation=='wrong_digest':mc['problem_sha256']='0'*64
    elif mutation=='positive_flag':mc['equivalent_at_all_positive_widths']=True
    else:mc['failure']['witness']['width']+=1
    try:dutw.check(dense,mc)
    except (ValueError,KeyError):counts['rejected_witness_mutations']+=1
    else:raise AssertionError(mutation)
 # Independent one-axis closure from explicit 2x2 C and S matrices.
 gens=[gate(1,['C',1,1]),gate(1,['D',[1],[1]])];group=[eye(2)];seen=set(group)
 for a in group:
  for g in gens:
   b=mm(g,a)
   if b not in seen:seen.add(b);group.append(b)
 assert len(group)==96
 ranks=[sumg(power(trace(g),f) for g in group) for f in range(1,9)]
 assert ranks[:7]==[Z]*7 and ranks[7]==(F(96*15),F(0))
 # K is a sum of four Gram matrices; invertible mod p implies invertible over Q(i).
 def mod(z):return (z[0].numerator*pow(z[0].denominator,-1,65537)+256*z[1].numerator*pow(z[1].denominator,-1,65537))%65537
 K=[]
 for g in group:
  row=[]
  for h in group:
   t=trace(mm(adj(g),h));t=(t[0]/2,t[1]/2);z=mod(t);row.append(sum(pow(z,f,65537) for f in range(5,9))%65537)
  K.append(row)
 assert rank_mod(K)==96
 # No submitted arithmetic or trace/filter helper used in this independent polynomial audit.
 norms=[]
 for n in range(9):
  coeff=[F(1)];den=F(1)
  for j in range(1,2*n+1):
   root=F((-1)**j,4**j);new=[F(0)]*(len(coeff)+1)
   for k,x in enumerate(coeff):new[k]-=root*x;new[k+1]+=x
   coeff=new;den*=1-root
  norm=sum(abs(x/den) for x in coeff);assert norm<=F(77,75);norms.append(str(norm))
 result={'head':'848cdce9003262c4b6e02ec4558f302e4fae56ad','scope':'Independent theorem-boundary and tiny exact matrix ground truth; no complete provider replay',**counts,'one_axis_group_size':len(group),'one_axis_K_rank_mod_65537':96,'Reynolds_ranks_1_to_8':[str(x[0]/96) for x in ranks],'independent_filter_l1_n0_to8':norms,'elapsed_seconds':round(time.monotonic()-start,3)}
 (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
def product_entries(m,xs,ys):
 v=O
 for x,y in zip(xs,ys):v=mul(v,m[x][y])
 return v
def to_string(z):
 a,b=z
 if not b:return str(a)
 if not a:return ('i' if b==1 else '-i' if b==-1 else str(b)+'i')
 return str(a)+('+' if b>0 else '')+str(b)+'i'
if __name__=='__main__':main()
