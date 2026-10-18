"""Independent finite invoice and rational-rank check for the schematic model."""
from pathlib import Path
from itertools import combinations,product
from functools import lru_cache
from fractions import Fraction
import hashlib,importlib.util,json,platform,sys,time
P=Path('/tmp/pr-efficient1800');pkg=P/'sources/2844/research/p104-signed-mixed-carrier-bank';start=time.monotonic()
def need(x,m):
 if not x:raise ValueError(m)
def rankq(rows):
 a=[[Fraction(x) for x in row] for row in rows];k=0
 for j in range(8):
  pos=next((i for i in range(k,len(a)) if a[i][j]),None)
  if pos is None:continue
  a[k],a[pos]=a[pos],a[k];z=a[k][j];a[k]=[x/z for x in a[k]]
  for i in range(k+1,len(a)):
   if a[i][j]:z=a[i][j];a[i]=[x-z*y for x,y in zip(a[i],a[k])]
  k+=1
 return k
E=[(i,j) for i in range(8) for j in range(i+1,8) if (i^j) in (1,2,4)]
F=[]
for mask in range(1,255):
 vertices={i for i in range(8) if mask>>i&1};edges=[e for e in E if set(e)<=vertices];seen={min(vertices)}
 while True:
  new=seen|{v for u in seen for v in vertices if (u^v) in (1,2,4)}
  if new==seen:break
  seen=new
 complement={i for i in range(8) if not mask>>i&1}
 if (2<=len(vertices)<=5 and seen==vertices and len(edges)==len(vertices)-1) or (len(complement)==2 and tuple(sorted(complement)) in E):F.append(mask)
need(len(F)==104,'support census')
s=importlib.util.spec_from_file_location('mixed_submission',pkg/'verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
need(F==v.support_family(),'independent support family')
# Independent vertex deletion/pair recurrence; no edge-conflict DP reused.
costs=[]
for bank in range(4096):
 adj=[0]*8
 for j,(x,y) in enumerate(E):
  if bank>>j&1:adj[x]|=1<<y;adj[y]|=1<<x
 @lru_cache(None)
 def maximum(mask):
  if not mask:return 0
  bit=mask&-mask;x=bit.bit_length()-1;rest=mask^bit
  best=maximum(rest);neighbours=adj[x]&rest
  while neighbours:
   b=neighbours&-neighbours;neighbours^=b;best=max(best,1+maximum(rest^b))
  return best
 reads=travel1=travel2=0
 for mask in F:
  n=mask.bit_count();pairs=maximum(mask);reads+=n-pairs
  travel1+=(n-pairs)*(n-pairs-1)
  dimension=0
  for width in [1]*(n-2*pairs)+[2]*pairs:travel2+=2*dimension;dimension+=width
  need(dimension==n,'frame coverage')
 q=bank.bit_count();costs.append([832+10*q+travel1,4*q+reads,832+20*q+travel1,8*q+reads,832+16*q+travel2])
winners=[i for i,x in enumerate(costs) if x[0]==min(c[0] for c in costs)]
need(winners==[4095] and costs[4095][:2]==[1312,288],'unrestored invoice')
expected=[1781,1995,2526,2995,3437,3646]
for column,floor in [(2,1408),(4,1520)]:
 best=min(x[column] for x in costs);win=[i for i,x in enumerate(costs) if x[column]==best]
 need(best==floor and win==expected and all(costs[i][3]==320 for i in win),'restored minima')
need(min(x[1] for x in costs)==288 and min(x[3] for x in costs)==320,'ADD minima')
rank_hist={7:0,8:0}
for label in range(1,256):
 bad=[[(mask>>i)&1 for i in range(8)] for mask in F if (label&(255^mask)).bit_count()%2]
 rank=rankq(bad);need(rank==(7 if label.bit_count()==1 else 8),'rational static-basis obstruction');rank_hist[rank]+=1
# Whole-family character proof of the no-root-line pair-sum screen.
roots=[]
for i,j in combinations(range(8),2):
 for a,b in product((2,-2),repeat=2):
  x=[0]*8;x[i]=a;x[j]=b;roots.append(tuple(x))
roots += [x for x in product((1,-1),repeat=8) if x.count(-1)%2==0]
lines=sorted({x if next(a for a in x if a)>0 else tuple(-a for a in x) for x in roots})
labels=[]
for x in lines:
 row=0
 for j,y in enumerate(lines):
  dot=sum(a*b for a,b in zip(x,y));need(dot%4==0,'integral root pairing');row|=((dot//4+1)&1)<<j
 labels.append(row)
need(len(lines)==len(set(labels))==120,'root lines')
need(v.rank(tuple(labels))==v.rank(tuple(x|(1<<120) for x in labels)),'all labels admit constant-one linear functional')
need(all((x^y) not in set(labels) for x,y in combinations(labels,2)),'pair sums')
detail=dict(banks=4096,invoice_sha256=hashlib.sha256(json.dumps(costs,separators=(',',':')).encode()).hexdigest(),rank_histogram=rank_hist,restored_winners=expected,rank1_restored=[1408,320],rank2_restored=[1520,320],roots=120,pair_sums=7140,scope='Independent vertex recursion and rational elimination in the declared simplified model. No native carrier, physical invoice or selected supplier admitted.')
log=P/'check-2844-supplement.log';log.write_text(json.dumps(dict(status='PASS',**detail),sort_keys=True)+'\n')
d=dict(number=2844,head=json.loads((P/'2844.json').read_text())['headRefOid'],status='passed',seconds=time.monotonic()-start,commands=[dict(argv=[sys.executable,str(Path(__file__).resolve())],exit_code=0)],input_sha256={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),pkg/'verify.py',pkg/'PROOF.md']},log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),environment=dict(python=sys.version,platform=platform.platform()),details=detail)
(P/'check-2844-supplement.json').write_text(json.dumps(d,indent=2)+'\n');print('2844 PASS independent4096bank invoices and255rational ranks',flush=True)
