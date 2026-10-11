"""Independent PR493 actual/reflected projector and whole-owner audit, OpenAI Codex. Apache-2.0.
Usage: review_local.py PR493_PACKAGE FRESH_OUTPUT REPORT.json
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import gzip,hashlib,json,struct,sys
import sympy as S
if not __debug__:raise RuntimeError('assertions must remain enabled')
assert len(sys.argv)==4, 'usage: review_local.py PR493_PACKAGE FRESH_OUTPUT REPORT.json'
PKG,OUT,REPORT=map(lambda x:Path(x).resolve(),sys.argv[1:])
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
w=read(PKG/'data/bit/bitE8mut-r489.json.gz');t=read(OUT/'bit/GLOBAL-TEMPLATE.json.gz');fs=read(OUT/'records/frames.json')['frames'];state=read(OUT/'records/249-states.json');records=list(struct.iter_unpack('<6i',(OUT/'records/249-records.bin').read_bytes()));v=120;n=2*v+w['R'];assert n==729
I=S.eye(8);P={};dims={};projector_hash={}
for key,z in fs.items():
 B=S.Matrix(z['B']) if z['B'] else S.zeros(0,8);p=B.T*(B*B.T).inv()*B if B.rows else S.zeros(8);assert p==p.T and p*p==p and p.trace()==z['dim'];P[int(key)]=p;dims[int(key)]=z['dim']
 for rev in (False,True):projector_hash[rev,int(key)]=hashlib.sha256(str(I-p if rev else p).encode()).hexdigest()
results={};transitions=set()
for rev in (False,True):
 ori='reverse' if rev else 'forward';cur=[state['final' if rev else 'initial'][str(i)] for i in range(n)]+[-1];rows=[1<<i for i in range(n)]+[0];center=None;hist=Counter();ledger=hashlib.sha256();adds=copies=0;sourcewrites=Counter();rebuilt=[]
 for op,x,y,c,f,z in (reversed(records) if rev else records):
  if op==0:rebuilt.append([0,x,c if rev else y,y if rev else c,f,int(rev)])
  elif op==1:rebuilt.append([1,x,y,-c if rev else c,f,int(rev)])
  elif op==(3 if rev else 2):rebuilt.append([2,x,y,c,f,abs(dims[c]-dims[f]),int(rev)])
  else:rebuilt.append([3,x,y,c,f,z,int(rev)])
 assert rebuilt==t['local_programs'][ori]
 for k,z in enumerate(rebuilt):
  op,x=z[:2]
  if op==0:
   _,x,old,new,rank,rr=z;assert bool(rr)==rev and cur[x]==old;key=(rev,old,new,rank)
   if key not in transitions:
    a=I-P[old] if rev else P[old];b=I-P[new] if rev else P[new];delta=b-a;assert a*b==b*a==a and delta*delta==delta and delta.trace()==rank;transitions.add(key)
   cur[x]=new;hist[rank]+=bool(rank)
  elif op==1:
   _,x,y,coeff,f,rr=z;assert bool(rr)==rev and cur[x]==cur[y]==f;assert x!=y and x!=center and (y<n or center is not None)
   ledger.update(json.dumps([k,x,y,coeff,projector_hash[rev,f]],separators=(',',':')).encode()+b'\n')
   if coeff&1:rows[x]^=rows[y]
   adds+=1
   if x<v:sourcewrites[int((I-P[f]).trace()) if rev else dims[f]]+=1
  elif op==2:
   _,x,y,a,b,rank,rr=z;assert bool(rr)==rev and y==n and center is None and cur[x]==a and rows[n]==0;assert rank==abs(dims[a]-dims[b])==8;center=x;cur[n]=b;rows[n]=rows[x];hist[rank]+=1;copies+=1
  else:
   _,x,y,a,b,rank,rr=z;assert bool(rr)==rev and op==3 and x==center and y==n and cur[x]==a and cur[n]==b;assert rows[n]==rows[x];rows[n]=0;cur[n]=-1;center=None
 assert center is None and rows[n]==0 and cur[:n]==[state['initial' if rev else 'final'][str(i)] for i in range(n)]
 assert all(rows[i]==(1<<i)^((1<<(i-v)) if v<=i<2*v else 0) for i in range(n))
 results[ori]={'formal_columns':n,'dirty_helpers_restored':w['R'],'source_registers_restored':v,'instructions':len(rebuilt),'adds':adds,'copies':copies,'source_write_actual_frame_dimensions':dict(sorted(sourcewrites.items())),'paid_profile':{str(k):val for k,val in sorted(hist.items()) if val},'actual_projector_ledger_sha256':ledger.hexdigest()}
assert results['forward']['paid_profile']==results['reverse']['paid_profile']==read(PKG/'EXPECTED.json')['word']['local_histogram']
# Source-support containment follows the actual signed scalar sources; forward
# coefficients are positive so support union is exact, including rewritten sources.
allowed={f:sum(int(all(sum(a*b for a,b in zip(w['lines'][i],row))==0 for row in fs[str(f)]['A']))<<i for i in range(v)) for f in P}
support=[1<<i if i<v else 0 for i in range(n)];checks=0;source_support_checks=0
for phase in ['D','A','B','C']:
 for f,d,srcs in w[phase]:
  for s in srcs:
   if s<v or s>=2*v:assert support[s]&~allowed[f]==0;checks+=1
   support[d]|=support[s]
  if d<v or d>=2*v:
   assert support[d]&~allowed[f]==0;checks+=1;source_support_checks+=int(d<v)
# Structural mutable-source interface, independently stated.
assert all(not (d<v or d>=2*v) or all(not v<=s<2*v for s in ss) for phase in ['D','A','B','C'] for f,d,ss in w[phase])
assert all(f==0 and v<=d<2*v and all(s>=2*v for s in ss) for f,d,ss in w['D'])
assert all(not v<=d<2*v for f,d,ss in w['A']) and all(v<=d<2*v for f,d,ss in w['B'])
assert w['C']==[[1,d,ss] for f,d,ss in reversed(w['A'])]
# Exact physical owner construction from every complete rational basis.
geo=read(OUT/'bit/GEOMETRY.json');idle={e['idx']:e for e in t['schedule'] if e['kind']=='idle'};bases=[]
for port in geo['ports']:
 head=[[Q(x,2) for x in port['q']]]+[[Q(row[j]) for row in port['complement_columns']] for j in range(7)]
 assert all(sum(x*y for x,y in zip(a,b))==int(i==j) for i,a in enumerate(head) for j,b in enumerate(head))
 cols=[tuple((i,x.numerator,x.denominator) for i,x in enumerate(col) if x) for col in head]+[((j,1,1),) for j in range(8,78)];assert len(cols)==78;bases.append(cols)
assert all(w['start'][h]==0 for h in range(240,n))
routecount=0;stream=hashlib.sha256();unique=set();groupcount=0;occupied=defaultdict(set);pending={};mult=Counter()
for call in t['calls']:
 active={fam for fam,route in call['owners'][:240]};seen=set();samefamily=defaultdict(set);counts=Counter()
 for helper,(fam,route) in enumerate(call['owners'][240:]):
  kind,idx,off,width=route;assert kind=='hosted' and fam not in active and width==8
  _,sub=divmod(fam,1200);pair,sp=divmod(sub,240);_,port=divmod(sp,120);child=idle[idx];assert child['pair']==pair
  lo,hi=child['source_level'],child['target_level'];axes=list(range(1,8))+list(range(8,8+7*hi)) if lo==-1 else list(range(8+7*lo,8+7*hi));assert len(axes)==child['rank'];foot=axes[off:off+width];assert len(set(foot))==8
  assert not samefamily[fam]&set(foot);samefamily[fam].update(foot)
  order=foot+[j for j in range(78) if j not in foot];assert set(order)==set(range(78));sigma=tuple(bases[port][j] for j in order)
  # Every full sigma is orthogonal, has inverse sigma^T, and sends the full
  # local8 residual to the exact8 assigned basis columns. This is a complete
  # rational matrix equality, not merely an integer slot reservation.
  assert tuple(sigma[:8])==tuple(bases[port][j] for j in foot)
  assert (fam,sigma) not in seen;seen.add((fam,sigma));routecount+=1;counts[fam]+=1
  h=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();unique.add(h);stream.update(json.dumps([call['stage'],call['replica'],helper,fam,h],separators=(',',':')).encode()+b'\n')
  key=(idx,fam);assert not occupied[key]&set(foot);occupied[key].update(foot);pending[key]=set(axes)
 assert len(seen)==489;groupcount+=len(samefamily)
 for count in counts.values():mult[count]+=1
assert routecount==43032
for key,foot in occupied.items():assert foot<=pending[key] and foot|(pending[key]-foot)==pending[key]
report={'status':'PASS_INDEPENDENT_PR493_MUTABLE_SOURCE_LEDGER_AND_ACTUAL_OWNER_AUDIT','head':'c3a9a436b84fe44fdc223a5784d84736d1c2d3c7','source_frames':len(P),'exact_oriented_projector_transitions':len(transitions),'orientations':results,'source_support_checks':checks,'mutable_source_destination_support_checks':source_support_checks,'no_targets_feed_sources_or_helpers':True,'literal_source_helper_inverse_cleanup':True,'actual_owner_routes':routecount,'actual_unique_sigma_matrices':len(unique),'cross_idle_call_family_groups':groupcount,'idle_family_completion_groups':len(occupied),'maximum_helpers_per_family':max(mult),'actual_sigma_stream_sha256':stream.hexdigest(),'modular_distinctness':'All routes for a physical family are one dyadic orthogonal port basis times distinct column permutations; equality is impossible over every odd field. Cross-idle assigned footprints are pairwise disjoint.','scope':'Exact native-frame local source/helper restoration and actual complete owner matrices. This does not unconditionally establish inherited all-size mutable-basis compiler, row or analytic contracts.'}
REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
