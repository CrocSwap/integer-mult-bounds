from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import companion as packet
packet.require_assertions()
packet.verify_base()
packet.verify_sources()
"""Independent new endpoint charts and literal bank assignment for PR322+323.
Prepared with substantial OpenAI assistance. Apache-2.0. No upstream execution.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from math import lcm,gcd
import json,gzip,struct,hashlib
if not __debug__:raise RuntimeError('Assertions required')
P=packet.EXPERIMENT;R=json.loads((P/'RESULT.json').read_text());OLD=packet.BASE_BANK;roles=json.loads((packet.BASE_LOWER/"compact-role-index.json").read_text())['roles'];widths={}
for r,t,b,o,w,s in struct.iter_unpack('>6I',gzip.decompress((OLD/'literal-assignments.bin.gz').read_bytes())):
 assert r not in widths or widths[r]==w;widths[r]=w
assert set(widths)==set(roles)
def eliminate(A):
 n=len(A);a=[list(map(Q,row))+[Q(int(i==j))for j in range(n)]for i,row in enumerate(A)];ops=[]
 for j in range(n):
  i=next(i for i in range(j,n)if a[i][j])
  if i!=j:a[i],a[j]=a[j],a[i];ops.append(['swap',i,j,None])
  d=a[j][j]
  if d!=1:a[j]=[x/d for x in a[j]];ops.append(['scale',j,j,str(1/d)])
  for i in range(n):
   if i!=j and a[i][j]:
    d=-a[i][j];a[i]=[x+d*y for x,y in zip(a[i],a[j])];ops.append(['add',i,j,str(d)])
 assert all(a[i][j]==int(i==j)for i in range(n)for j in range(n));return [row[n:]for row in a],ops
def null(A):
 a=[list(map(Q,row))for row in A];piv=[];k=0
 for j in range(20):
  i=next((i for i in range(k,len(a))if a[i][j]),None)
  if i is None:continue
  a[i],a[k]=a[k],a[i];d=a[k][j];a[k]=[x/d for x in a[k]]
  for i in range(len(a)):
   if i!=k and a[i][j]:d=a[i][j];a[i]=[x-d*y for x,y in zip(a[i],a[k])]
  piv.append(j);k+=1
  if k==len(a):break
 out=[]
 for j in range(20):
  if j in piv:continue
  row=[Q(int(j==i))for i in range(20)]
  for k,p in enumerate(piv):row[p]=-a[k][j]
  den=lcm(*(x.denominator for x in row));row=[int(x*den)for x in row];g=gcd(*row);out.append([x//g for x in row])
 return out
charts=[]
for e in R['new_kernel_entries']:
 role=roles[e['pivot']-1920];assert widths[role]==20;widths[role]=18
 D=e['basis'];res=null([[9*x-sum(row)for x in row]for row in D]);assert len(res)==18
 assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in D for b in res)
 B=list(map(list,zip(*(res+D))));BI,ops=eliminate(B)
 for A,C in [(B,BI),(BI,B)]:assert all(sum(x*y for x,y in zip(a,b))==int(i==j)for i,a in enumerate(A)for j,b in enumerate(zip(*C)))
 assert len(ops)<=400
 maxnum=max(abs(Q(x[3]).numerator)for x in ops if x[3]is not None);maxden=max(Q(x[3]).denominator for x in ops if x[3]is not None);assert max(maxnum,maxden)<2**80
 charts.append({'compact_pivot':e['pivot'],'virtual_role':role,'entrance_rank':2,'residual_rank':18,'basis_columns':res+D,'inverse':[[str(x)for x in row]for row in BI],'factor_program':ops,'factor_count':len(ops),'max_numerator':maxnum,'max_denominator':maxden,'exact_orthogonal_endpoint_projector':True})
assert Counter(widths.values())=={int(r):n for r,n in R['residual_census'].items()}
queues={w:iter([(r,t)for r in roles if widths[r]==w for t in range(60)])for w in set(widths.values())};assign=bytearray();completion=[];used=set();bank=0;normalizer_patterns=0
for p in R['packing_patterns']:
 widths0=p['widths'];cw=p.get('paid_complement_widths',[]);assert sum(widths0)+sum(cw)==100
 offsets=[];q=0
 for w in widths0+cw:offsets.append(q);q+=w
 state=list(range(200))
 for o,w in zip(offsets,widths0+cw):
  for j in range(o,o+w):state[j],state[199-j]=state[199-j],state[j]
 assert state==list(range(199,-1,-1))
 for s in range(5):
  outside=next(j for j in range(100)if not 20*s<=j<20*(s+1));witness=[]
  for b,(o,w)in enumerate(zip(offsets,widths0)):
   a=list(range(20*s,20*s+w));z=list(range(o,o+w));pi=dict(zip(a+[j for j in range(100)if j not in a],z+[j for j in range(100)if j not in z]));witness.append((pi[outside],b+1))
  assert len(set(witness))==len(witness);normalizer_patterns+=1
 for _ in range(p['count']):
  for b,(o,w)in enumerate(zip(offsets,widths0)):
   r,t=next(queues[w]);assert(r,t)not in used;used.add((r,t));assign.extend(struct.pack('>6I',r,t,bank,o,w,b+1))
  for o,w in zip(offsets[len(widths0):],cw):completion.append([bank,o,w])
  bank+=1
assert len(used)==60*8221 and all(next(q,None)is None for q in queues.values());assert bank==85571 and completion==[[85570,80,20]]
allhash=hashlib.sha256()
for s in range(5):
 coverage=bytearray(bank*100)
 for r,t,b,o,w,sc in struct.iter_unpack('>6I',assign):
  z=b*100+o;assert not any(coverage[z:z+w]);coverage[z:z+w]=b'\1'*w
  family=230400+s*bank+b;assert 230400+s*bank<=family<230400+(s+1)*bank;allhash.update(struct.pack('>7I',s,r,t,family,o,w,sc))
 for b,o,w in completion:
  z=b*100+o;assert not any(coverage[z:z+w]);coverage[z:z+w]=b'\2'*w
 assert coverage.count(0)==0 and coverage.count(2)==20
(P/'new-bank-assignments.bin.gz').write_bytes(gzip.compress(assign,mtime=0))
# Full literal primitive allowance, using fresh scalar count and newfivechildren.
S=R['literal_stock'];E=R['literal_calls'];m=100;J=60*(24*960+10*8221)+2*5;K=2*5*60*((S-1)+8221*100*599)+2*5*((S-1)+100*599)
terms={'unit_expanded_additions':60*(5*R['scalar_forward']['unit_additions']+6*960),'high_affine_factors':J*16*10001**2,'low_transpositions':J*(S+20),'generic_wrappers':E*80008,'matrix_preparation':E*128*200**3,'global_matrix_preparation':16*100**3,'copy_erase_episodes':6000,'paid_child_overhead':E,'bank_selectors':K,'constant':1}
assert sum(terms.values())<2**80 and K<2**40 and S+20<2**80
out={'status':'PASS_NEW_ENDPOINT_CHARTS_AND_LITERAL_BANK_INVOICE','composition_result_sha256':hashlib.sha256((P/'RESULT.json').read_bytes()).hexdigest(),'changed_endpoint_charts':charts,'unchanged_charts_inherited_from_bound_paid892_packet':True,'assignment_count':len(used)*5,'assignment_sha256':hashlib.sha256(assign).hexdigest(),'five_stage_assignment_sha256':allhash.hexdigest(),'all_coordinate_coverage':True,'normalizer_pattern_checks':normalizer_patterns,'normalizer_bound':599,'completion_per_stage':{'offset':80,'rank':20,'one_exact_child':True},'route_families':J,'selector_calls':K,'terms':terms,'coefficient':sum(terms.values()),'max_child_rank':42,'halving_degree':1,'row_reserve_coefficient':10001,'literal_stock':S,'children':E,'scope':'All newly changed bank charts, literal assignment and fee arithmetic. Complete new global frame-IR binding and independently reviewed scalar composition remain next admission gates.'}
(P/'BANK-RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='changed_endpoint_charts'},indent=2))
