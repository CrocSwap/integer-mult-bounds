from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Original independent exact audit of the explicit 892 local/global frame word.
Reads all source programs and worker programs only as inert files. Apache-2.0.
Prepared with substantial OpenAI assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
from math import gcd,lcm
from collections import Counter,defaultdict
from functools import lru_cache
import gzip,hashlib,json
import numpy as np
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=support.AUDIT;LOCAL=support.FRAME;GLOBAL=support.OUTPUT/"full-frame";INC=support.LOWER;BASE=support.BASE_OUTPUT;AD=support.HERE/"admission"
hashes={}
def load(p):
 p=Path(p);b=p.read_bytes();hashes[str(p)]=hashlib.sha256(b).hexdigest();return json.loads(gzip.decompress(b)if p.name.endswith('.gz')else b)
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
result=load(LOCAL/'RESULT.json');globalresult=load(GLOBAL/'RESULT.json');manifest=load(support.INPUT_MANIFEST)
assert sha((support.HERE/'frame/build_local.py').read_bytes())==result['checker_sha256']
for name,value in result['artifacts'].items():assert sha((LOCAL/name).read_bytes())==value
assert result['candidate_sha256']==globalresult['candidate_sha256']=='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
def source(name):
 z=next(z for z in manifest['files']if z['path']==name);b=(support.INPUTS/z['local']).read_bytes()
 assert sha(b)==z['sha256']and len(b)==z['bytes']
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==z['git_blob']
 return json.loads(gzip.decompress(b)if name.endswith('.gz')else b)
word=load(support.WORD);oldword=source('bitword/selected/bit/word_p10.json.gz');sourceframes=source('bitword/selected/bit/frames_p10.json.gz')['frames'];graph=source('bitword/selected/bit/graph_p10.json');D=source('descent-selection.json')['entries'];R=source('restore-selection.json')['entries'];T=source('target-selection.json')['groups'];S=source('sink-selection.json')['sinks'];Z=source('reorder-selection.json');KS=source('kernel-selection.json')
kernels=[dict(pivot=e['a'],donors=[e['b']],basis=e['basis'],rank=e['rank'])for e in KS['pairs']]+KS['families']
frames0=load(LOCAL/'local-frames.json.gz');events=load(LOCAL/'local-events.json.gz');records=load(LOCAL/'local-records.json.gz');ends=load(LOCAL/'local-endpoints.json');paths=load(LOCAL/'local-paths.json.gz');moves=load(LOCAL/'reorder-receipts.json')
assert len(records)==389223 and len(events)==336293 and len(moves)==133 and len(frames0)==15034
# Normalize rows only by nonzero scalar, using exact rational arithmetic.
def introw(row):
 row=list(map(Q,row));den=lcm(*(x.denominator for x in row));v=[int(x*den)for x in row];g=gcd(*v)
 if g:v=[x//g for x in v]
 return tuple(v)
def mat(rows):return tuple(introw(row)for row in rows)
def rank_mod(rows,p):
 a=[[int(x)%p for x in row]for row in rows];r=0
 for j in range(len(a[0])if a else 0):
  pivot=next((i for i in range(r,len(a))if a[i][j]),None)
  if pivot is None:continue
  a[r],a[pivot]=a[pivot],a[r];v=pow(a[r][j],-1,p);a[r]=[(x*v)%p for x in a[r]]
  for i in range(r+1,len(a)):
   v=a[i][j]
   if v:a[i]=[(x-v*y)%p for x,y in zip(a[i],a[r])]
  r+=1
  if r==len(a):break
 return r
frames={};keys={};gram_witnesses=Counter()
for textid,z in frames0.items():
 i=int(textid);kind,k=z['key'];r=z['rank'];A=mat(z['annihilator']);B=mat(z['basis'])
 assert len(A)==20-r and len(B)==r and all(len(row)==20 for row in A+B)
 assert all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in B)
 assert any(rank_mod(A,p)==len(A)and rank_mod(B,p)==len(B)for p in (65521,65519,1000003))
 if kind=='frame':
  src=sourceframes[str(k)];assert src['dim']==r
  if 'a'in src:assert A==mat(src['a'])
  if 'b'in src:assert B==mat(src['b'])
 elif kind=='zero':assert r==0
 elif kind=='cap':assert r==19 and A==mat([[3*int(j in graph['labels'][k])-1 for j in range(20)]])
 else:
  expected={'descent':lambda:D[k]['new_basis'],'restore':lambda:R[k]['basis'],'target':lambda:T[k]['close_basis'],'sink':lambda:S[k]['root_frame_basis'],'kernel':lambda:kernels[k]['basis'],'reorder':lambda:Z['moves'][k]['frame_basis']}[kind]()
  assert B==mat(expected)
 # A full-rank reduction of rational Gram is an exact nonsingularity witness
 # over Q, not a claim of nondegeneracy at every eligible compiler prime.
 for p in (65521,65519,1000003):
  b=np.asarray([[x%p for x in row]for row in B],dtype=np.int64).reshape(r,20);sm=b.sum(axis=1)
  gram=(9*(b@b.T)-sm[:,None]*sm[None,:])%p
  if rank_mod(gram.tolist(),p)==r:gram_witnesses[p]+=1;break
 else:raise AssertionError(('Gram singular or witnesses inconclusive',i))
 frames[i]=(r,A,B);keys[kind,k]=i
print('All15034 exact source-bound frames and rational Gram witnesses pass',flush=True)
@lru_cache(None)
def sub(a,b):
 ra,Aa,Ba=frames[a];rb,Ab,Bb=frames[b]
 return ra<=rb and all(sum(x*y for x,y in zip(row,v))==0 for row in Ab for v in Ba)
def equal(a,b):return frames[a][0]==frames[b][0]and sub(a,b)
# Rebind every selected original physical port through virtual representatives.
oldregs=sorted(set(range(9120))-{b for a,b in oldword['pairs']});newregs=sorted(set(range(9120))-{b for a,b in word['pairs']});alias={b:a for a,b in word['pairs']};oldinv={1920+i:r for i,r in enumerate(oldregs)};newid={r:1920+i for i,r in enumerate(newregs)}
def xlat(s):return newid[alias.get(oldinv[s],oldinv[s])]if s>=1920 else s
assert set(oldregs)-set(newregs)=={9118,9119} and all(newid[r]==i for i,r in oldinv.items()if r in newid)
selected={s for z in kernels for s in [z['pivot']]+z['donors']}|{z[k]for z in R for k in('helper','donor')}|{z['stream']for z in S}
assert len(selected)==2433 and all(xlat(s)==s for s in selected)
removed=sorted(z['stream']for z in S)
def lift(s):
 for r in removed:
  if r<=s:s+=1
 return s
assert all(xlat(lift(s))==lift(s)for z in Z['moves']for s in z['incidence'][:2])
# Reconstruct original order, source-bind all unmoved semantic frames.
original=sorted(events,key=lambda e:e['original_index']);assert [e['original_index']for e in original]==list(range(len(events)))
original=[dict(e)for e in original]
for e in original:
 if e.get('moved'):
  sem=e['semantic'];frame_id=word['op_frame'][sem[1]]if sem[0]=='forward'else word['root_frame'][sem[1]]
  e['frame']=keys['frame',frame_id];e.pop('moved',None)
# Bind the reordered word back to the already audited full scalar projection,
# and check every original event's frame against its source semantic meaning.
scalar_rows=np.frombuffer(gzip.decompress((INC/'local-scalar-operands.i32.gz').read_bytes()),dtype='<i4').reshape(-1,5)
scalar_semantics=[json.loads(line)for line in gzip.decompress((INC/'local-semantic-events.jsonl.gz').read_bytes()).splitlines()]
chron=source('bitword/selected/bit/kchron_p10.json')['entries'];partner={e['carrier']:e for e in chron}
ga={e['role']:e for e in word['gauges']};targets={int(q):j for j,e in enumerate(T)for q in e['dependent']};restores={(e['helper'],e['donor']):j for j,e in enumerate(R)};kernel_ids={e['pivot']:j for j,e in enumerate(kernels)};sink_ids={e['stream']:j for j,e in enumerate(S)};descs={(e['scalar'][0],e['scalar'][1]):j for j,e in enumerate(D)}
for i,e in enumerate(original):
 assert [e[k]for k in ('op','a','b','c')]==scalar_rows[i,:4].tolist()and int(scalar_rows[i,4])==i
 assert scalar_semantics[i]==[i,e['semantic']]
 sem=e['semantic'];kind=sem[0]
 if kind in('plain','center_read','target_setup','sink_setup'):key=('zero',0)
 elif kind in('cleanup','uninject','partner_cleanup','kernel_restore'):key=('frame',word['full_frame'])
 elif kind=='inject':key=('frame',word['source_frame'][sem[1]])
 elif kind in('forward','sink_redirect'):key=('frame',word['op_frame'][sem[1]if kind=='forward'else sem[2]])
 elif kind=='gauge':key=('frame',ga[sem[1]]['frame'])
 elif kind in('root','center'):key=('frame',word['root_frame'][sem[1]])
 elif kind=='target_restore':key=('target',targets[sem[1]])
 elif kind=='partner_setup':key=('descent',descs[sem[1],sem[2]])
 elif kind=='partner_delivery':key=('frame',partner[sem[1]]['deliver_frame'])
 elif kind=='early_restore':key=('restore',restores[sem[1],sem[2]])
 elif kind=='kernel_setup':key=('kernel',kernel_ids[sem[1]])
 elif kind=='sink_restore':key=('sink',sink_ids[sem[1]])
 else:raise AssertionError(kind)
 assert e['frame']==keys[key],(i,sem,e['frame'],key)
# Explicitly bind every descended partner_setup to its actual selected basis.
desc={(z['scalar'][0],z['scalar'][1]):i for i,z in enumerate(D)};descents=[]
for e in original:
 if e['semantic'][0]=='partner_setup':
  _,a,b=e['semantic'];j=desc[a,b]
  assert e['frame']==keys['descent',j]and frames[e['frame']][0]==18
  assert e['a']==a and e['b']==b and e['c']==1;descents.append(j)
assert sorted(descents)==list(range(480))
# Every actual chosen anchor is checked, with exact commuting crossings.
before=defaultdict(list);after=defaultdict(list);moved={};ports=set();delta=Counter();crossings=0
incidence=defaultdict(list)
for i,e in enumerate(original):
 incidence[e['a']].append(i)
 if e['op']==1:incidence[e['b']].append(i)
initial={int(k):v for k,v in ends['initial'].items()};final={int(k):v for k,v in ends['final'].items()}
def chain_hist(port,chain):
 chain=[initial[port]]+[f for i,f in chain]+[final[port]];h=Counter()
 for a,b in zip(chain,chain[1:]):
  assert sub(a,b)
  if frames[b][0]>frames[a][0]:h[frames[b][0]-frames[a][0]]+=1
 return h
for j,receipt in enumerate(moves):
 z=Z['moves'][j];assert receipt['selection_index']==j;at=receipt['moved_event_index'];anchor=receipt['new_anchor_event_index'];e=original[at];nf=keys['reorder',j];a,b,c=z['incidence']
 assert(e['a'],e['b'],e['c'])==(a,b,c)and e['op']==1 and not {a,b}&ports;ports|={a,b}
 assert ('forward_gate'if e['semantic'][0]=='forward'else'side_root')==z['category']
 assert frames[e['frame']][0]==z['old_frame_rank']and frames[nf][0]==z['frame_rank']
 assert equal(original[anchor]['frame'],nf) and original[anchor]['op']==1
 assert {a,b}&{original[anchor]['a'],original[anchor]['b']}
 assert original[anchor]['semantic']==receipt['new_anchor_semantic']and z['side']==receipt['side']
 assert (at<anchor)if z['side']=='before'else(anchor<at)
 lo,hi=(at+1,anchor)if z['side']=='before'else(anchor+1,at)
 for crossed in original[lo:hi]:
  if crossed['op']==1:assert crossed['b']!=a and crossed['a']!=b
  else:assert crossed['a']!=a
  crossings+=1
 position=Q(2*anchor+(-1 if z['side']=='before'else 1),2);ld=Counter()
 for port in(a,b):
  path=[(i,original[i]['frame'])for i in incidence[port]];newpath=sorted([(i,f)for i,f in path if i!=at]+[(position,nf)])
  ld.update(chain_hist(port,newpath));ld.subtract(chain_hist(port,path))
 assert {str(k):v for k,v in ld.items()if v}==receipt['local_delta'];delta.update(ld)
 moved[at]=dict(e,frame=nf,moved=True);(before if z['side']=='before'else after)[anchor].append(at)
reordered=[]
for i,e in enumerate(original):
 reordered.extend(moved[j]for j in sorted(before[i]))
 if i not in moved:reordered.append(e)
 reordered.extend(moved[j]for j in sorted(after[i]))
assert reordered==events and {str(k):v for k,v in delta.items()if v}==result['reorder_delta']==Z['expected_local_delta']
print('All133 actual equivalent-frame anchors and every crossed event pass',flush=True)
# Derive all389223 records afresh from actual events and source endpoints.
state=dict(initial);out=[];hist=Counter();pathout=defaultdict(list);work=None;cats={s:i for i,s in enumerate(ends['categories'])};n=10141
assert set(initial)==set(final)==set(range(n))
def need(s,f):
 old=state[s]
 if old==f:return
 assert sub(old,f);gap=frames[f][0]-frames[old][0]
 out.append([0,s,old,f,gap,0]);state[s]=f;pathout[s].append([old,f,gap])
 if gap:hist[gap]+=1
for e in events:
 op,a,b,c,f=e['op'],e['a'],e['b'],e['c'],e['frame']
 if op==1:
  need(a,f)
  if b!=n:need(b,f)
  else:assert work is not None and frames[f][0]==0
  out.append([1,a,b,c,f,cats['reorder_moved'if e.get('moved')else e['semantic'][0]]])
 elif op==2:
  assert work is None and b==n;need(a,f);state[b]=keys['zero',0];work=(a,b,f);hist[frames[f][0]]+=1
  out.append([2,a,b,f,keys['zero',0],frames[f][0]])
 else:
  assert op==3 and work==(a,b,f)and state[a]==f and state[b]==keys['zero',0]
  out.append([3,a,b,f,keys['zero',0],frames[f][0]]);del state[b];work=None
for s,f in sorted(final.items()):need(s,f)
assert out==records and state==final and work is None
assert {str(k):v for k,v in pathout.items()}==paths
assert hist==Counter({int(k):v for k,v in result['one_stage_paid_histogram'].items()})
assert(sum(hist.values()),sum(k*v for k,v in hist.items()))==(48473,179464)
# Integer source containment on the actual reordered execution. Check both
# pre- and post-addition operands; no probabilistic or F2 cancellation shortcut.
cols=[{i:1}if i<960 else{}for i in range(n+1)];checked=set();copy=None
labels=graph['labels']
def check_support(f,support):
 for q in support:
  if (f,q)in checked:continue
  assert all(sum(row[j]for j in labels[q])==0 for row in frames[f][1]);checked.add((f,q))
for e in events:
 op,a,b,c,f=e['op'],e['a'],e['b'],e['c'],e['frame']
 if op==2:assert copy is None;check_support(f,cols[a]);cols[b]=dict(cols[a]);copy=a;continue
 if op==3:assert copy==a;copy=None;continue
 if not 960<=a<1920:check_support(f,cols[a])
 if b!=n and not 960<=b<1920:check_support(f,cols[b])
 if not 960<=a<1920:
  assert not 960<=b<1920
  for q,x in cols[b].items():
   y=cols[a].get(q,0)+c*x
   if y:cols[a][q]=y
   else:cols[a].pop(q,None)
  check_support(f,cols[a])
assert copy is None
print('Integer source containment passes',len(checked),'distinct checks',flush=True)
local_audit={'status':'PASS_INDEPENDENT_COMPLETE_LOCAL_FRAME_AUDIT','input_hashes':hashes,'records':len(records),'frames':len(frames),'rational_gram_witness_primes':dict(gram_witnesses),'source_bound_descents':len(descents),'actual_reorder_anchors':len(moves),'literal_crossed_events':crossings,'selected_physical_ports_rebound':len(selected),'reorder_ports_rebound':len(ports),'integer_source_containment_checks':len(checked),'local_paid_calls':sum(hist.values()),'local_rank_mass':sum(k*v for k,v in hist.items()),'scope':'Explicit local records, actual newly selected equivalent-frame anchors, source-bound frames, rational nondegeneracy, physical rebinding and integer source containment. Does not claim identical historical raw anchor IDs or uniform prime/all-size compilation.','checker_sha256':sha(Path(__file__).read_bytes())}
(HERE/'LOCAL-AUDIT.json').write_text(json.dumps(support.portable(local_audit),indent=2)+'\n')
print(json.dumps({k:v for k,v in local_audit.items()if k!='input_hashes'},indent=2))
