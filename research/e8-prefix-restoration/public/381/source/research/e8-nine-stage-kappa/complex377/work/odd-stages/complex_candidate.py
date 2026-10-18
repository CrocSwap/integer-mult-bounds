"""Independent nine-stage compressed E8 composition: finite data geometry,
whole-block banks and two-engine moment. This is not full supplier admission.
"""
import json,gzip,hashlib,math,importlib.util,time
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
OUT=Path('work/odd-stages');t0=time.monotonic();CP=Path('work/pr361/complex/gcert1-e8-r783.json.gz');c=json.loads(gzip.decompress(CP.read_bytes()))
h,v,R=c['h'],c['v'],c['R'];assert (h,v,R,c['cst'])==(9,120,783,72)
k=4;L=9;m=73;T=8;perbank=8;banks=783;W=8*v*T+L*banks
I=tuple(1<<i for i in range(m));Z=(0,)*m
def mul(A,B):
 out=[]
 for row in A:
  s=0
  while row:
   low=row&-row;s^=B[low.bit_length()-1];row^=low
  out.append(s)
 return tuple(out)
def tr(A):return tuple(sum(((A[j]>>i)&1)<<j for j in range(m)) for i in range(m))
def xor(A,B):return tuple(x^y for x,y in zip(A,B))
def rank(A):
 piv={}
 for x in A:
  while x:
   i=x.bit_length()-1
   if i not in piv:piv[i]=x;break
   x^=piv[i]
 return len(piv)
def project(q):return tuple(q if q>>i&1 else 0 for i in range(m))
def local(q,kind):
 P=project(q);H=tuple((1<<i) if i<h else 0 for i in range(m))
 return {'P':P,'H':H,'0':Z,'K':xor(H,P)}[kind]
def route(q,i):
 if not i:return I
 # Orthogonal U maps e0 to q, using one coordinate swap and one even transvection.
 j=0 if not(q&1) else next(z for z in range(1,h) if not(q>>z&1));w=q^(1<<j)
 cols=[]
 for b in range(h):
  b=j if b==0 else 0 if b==j else b;x=1<<b
  if (w&x).bit_count()%2:x^=w
  cols.append(x)
 assert cols[0]==q
 assert all(((a&b).bit_count()%2)==(i==j) for i,a in enumerate(cols) for j,b in enumerate(cols))
 A=list(I);off=h+(i-1)*(h-1)
 for b in range(h):A[b]=(q if q>>b&1 else 0)|sum(((cols[j+1]>>b)&1)<<(off+j) for j in range(h-1))
 for j in range(h-1):A[off+j]=cols[j+1]
 return tuple(A)
rows=[];geometry_hash=hashlib.sha256()
for q in c['ports']:
 assert q.bit_count()%2 and q!=(1<<h)-1
 stages=[]
 for i in range(L):
  rho=route(q,i);assert mul(rho,rho)==I and tr(rho)==rho
  pref=tuple(1<<b if h<=b<h+i*(h-1) else 0 for b in range(m));stage={}
  for kind in ['P','H','0','K']:
   a=xor(local(q,kind),pref);p=mul(mul(rho,a),rho);assert mul(p,p)==p and tr(p)==p;stage[kind]=p
   geometry_hash.update(json.dumps(p).encode())
  if i:assert stage['P']==stages[-1]['H'] and stage['0']==stages[-1]['K']
  stages.append(stage)
 P0=local(q,'P');idle=[]
 def interval(a,b,want):
  assert mul(a,b)==mul(b,a)==a;d=xor(a,b);assert rank(d)==want and mul(d,d)==d;idle.append(want)
 for j in range(1,k):
  interval(P0,stages[2*j-1]['H'],2*j*(h-1));interval(Z,stages[2*j-1]['K'],2*j*(h-1))
  interval(stages[2*j-1]['H'],stages[2*j]['H'],h-1);interval(stages[2*j-1]['K'],stages[2*j]['K'],h-1)
 for j in range(1,k+1):
  interval(stages[2*j]['H'],I,2*(k-j)*(h-1));interval(stages[2*j]['K'],xor(I,P0),2*(k-j)*(h-1))
 rows.append(dict(port=q,idle_ranks_per_pair=idle))
print('all 120 ports x 9 exact binary data-route checks PASS',flush=True)
# One literal stage has T copies of every helper; 8 rank-nine residuals and
# one paid rank-one padding block exactly fill each 73-dimensional bank.
assign=[]
for rep in range(T):
 for helper in range(R):
  z=rep*R+helper;bank,slot=divmod(z,perbank);assign.append([rep,helper,bank,9*slot,9])
assert max(x[2] for x in assign)+1==banks and len(assign)==T*R
for b in range(banks):
 slots=[x[3] for x in assign if x[2]==b];assert slots==list(range(0,72,9))
bank_columns=0;bad_controls=0
for col in range(2*m):
 s=list(range(2*m))
 for a,d in [(9*j,9) for j in range(8)]+[(72,1)]:
  for z in range(a,a+d):s[z],s[m+z]=s[m+z],s[z]
 assert s[col]==(col+m)%(2*m);bank_columns+=1
 # The omitted padding leaves exactly the two last-axis columns incorrect.
 broken=list(range(2*m))
 for z in range(72):broken[z],broken[m+z]=broken[m+z],broken[z]
 bad_controls+=broken[col]!=(col+m)%(2*m)
assert bad_controls==2
H=Counter()
for block in c['blocks'].values():
 for r,n in block.items():H[int(r)]+=L*T*n
idles=[16,8,32,8,48,8,48,32,16,0]
for r in idles:
 if r:H[r]+=2*v*T
H[1]+=L*banks
assert m*W-sum(r*n for r,n in H.items())==T*(2*k*v-L*c['cst'])==2496
def load(name):
 s=importlib.util.spec_from_file_location('cx9_'+name,Path('work/pr361/code/engines')/(name+'.py'));a=importlib.util.module_from_spec(s);s.loader.exec_module(a);return a
M=load('moment');B=load('base_two_moment');root=M.certify(H,m,W,True);b=Q(int(Q(root['lower'])*10**18),10**18);grid=Q(1,10**18)
lo,hi=M.moment(H,m,W,b,True);nl,nu=M.moment(H,m,W,b+grid,True);assert hi<1<nl
fb=32*m*m*sum(H.values());_,up=B.moment(m,W,list(H.items()),b);_,bad=B.moment(m,W,[(1,fb)],b);low,_=B.moment(m,W,list(H.items()),b+grid);badlo,_=B.moment(m,W,[(1,fb)],b+grid);assert up+Q(1,10**16)*bad<1<low+Q(1,10**16)*badlo
maxchild=max(H);halving=next(t for t in range(1,100) if m**t>2*maxchild**t);assert halving==2
rr=m//2;group=2**(rr*rr)*math.prod(2**(2*i)-1 for i in range(1,rr+1));physical=W+R+len(c['ret'])+1
row=halving*(group*physical).bit_length()+9909+252
assert row<20161
result=dict(status='PASS_FINITE_DATA_ROUTES_BANKS_AND_CONDITIONAL_PROFILE_NOT_FULL_SUPPLIER',certificate_gzip_sha256=hashlib.sha256(CP.read_bytes()).hexdigest(),m=m,pairs=k,stages=L,replicas=T,live=W,physical_lower_bound=physical,local_cst=c['cst'],profile=dict(sorted(H.items())),deficit=2496,max_child=maxchild,coarse_candidate=str(b),coarse_candidate_float=float(b),two_rational_engines=True,next_grid_rejected=True,inherited_fallback_assumed=True,geometry=dict(ports=len(rows),checks=rows,sha256=geometry_hash.hexdigest(),orthogonal_involutions=L*v),banks=dict(count_per_stage=banks,whole_residual_assignments_per_stage=len(assign),pattern=[9]*8+[1],paid_padding_rank_one_per_stage=banks,exact_endpoint_columns=bank_columns,omission_control_columns=bad_controls,assignment_sha256=hashlib.sha256(json.dumps(assign).encode()).hexdigest()),depth=dict(halving_degree=halving,inequality=[m**halving,2*maxchild**halving],orthogonal_group_bits=group.bit_length(),provisional_physical_stock_bits=(group*physical).bit_length(),provisional_row_coefficient=row,retained_limit=20161),unresolved=['Complete new source-bound signed local splices and global word including every copied-center lifecycle and its work routing.','Exact phase/canonical adapter account for all internal Clifford labels, not only endpoint data projectors.','Physical scratch, basis selector, adapter and whole-program finite invoice with changed dimension, nine invocations and two-level depth.','Proof integration of general halving degree and inherited bad-envelope charge; retained guard cannot be silently bypassed.','Bit side remains at fixed baseline, so no final kappa improvement or PR milestone is claimed.'],seconds=time.monotonic()-t0)
(OUT/'COMPLEX-NINE-CANDIDATE.json').write_text(json.dumps(result,indent=2));print('candidate coarse',float(b),'halving',halving,'row provisional',row,flush=True)
