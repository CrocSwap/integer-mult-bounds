from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import packet325 as contract
contract.require_assertions()
contract.verify_inputs()
contract.verify_source()
"""Independent source-bound event/retiming/COPY audit; upstream stays inert."""
from pathlib import Path
from collections import Counter,defaultdict
import gzip,json,hashlib
if not __debug__:raise RuntimeError('Assertions must be enabled')
HERE=contract.AUDIT
P=contract.SOURCE;I=P/'inputs'
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
w=read(I/'bitword__selected__bit__word_p10.json.gz');g=read(I/'bitword__selected__bit__graph_p10.json')
F=read(I/'bitword__selected__bit__frames_p10.json.gz')['frames'];K=read(I/'bitword__selected__bit__kchron_p10.json')['entries']
events=read(P/'scalar-events.json.gz');selection=read(P/'retiming-selection.json')['entries'];projection=read(P/'source-events.json.gz')
assert len(events)==350680 and len(selection)==480
alias={b:a for a,b in w['pairs']};rmax=1+max(max(e[:2])for e in w['ops']);roles=sorted(set(range(rmax))-set(alias))
physical={r:1920+j for j,r in enumerate(roles)}
def phys(r):return physical[alias.get(r,r)]
assert rmax==9060 and len(roles)==8100
n=10020;source={int(k):v for k,v in w['sources'].items()}
assert read(P/'physical-source-map.json')=={str(q):{'virtual':r,'physical':phys(r)}for q,r in source.items()}
first=sorted(w['phase1']);marked=set(first);later=[i for i in range(len(w['ops']))if i not in marked];order=first+later
adj=[Counter()for _ in range(rmax)]
for root,r in zip(g['roots'],w['rootroles']):
 assert root['coefficient']==1
 adj[r].update(root['targets'])
for i in reversed(order):
 a,b,node=w['ops'][i];adj[b].update(adj[a])
gauges={e['role']:e for e in w['gauges']};cursor=0;even=0;changed=[];copy_events=[]
def emit(op,a,b,c,frame,semantic):
 global cursor,even
 if op==1 and c%2==0:even+=1;return
 expected={'op':op,'a':a,'b':b,'c':c,'frame':frame,'semantic':semantic}
 if semantic[0]=='partner_setup':
  pair=semantic[1];assert frame==K[pair]['mix_frame'];expected['frame']=K[pair]['deliver_frame'];changed.append(cursor)
 assert events[cursor]==expected,(cursor,events[cursor],expected)
 if op in(2,3):copy_events.append([cursor,expected])
 cursor+=1
def compensate(r):
 frame=gauges[r]['frame']if r in gauges else-1
 for t,c in sorted(adj[r].items()):emit(1,960+t,phys(r),-c,frame,['gauge'if r in gauges else'plain',r,t])
def gate(i,c):
 a,b,_=w['ops'][i];emit(1,phys(a),phys(b),c,w['op_frame'][i]if c==1 else w['full_frame'],['forward'if c==1 else'inverse',i])
for r in range(rmax):
 if r not in gauges:compensate(r)
for q in range(960):emit(1,phys(source[q]),q,1,w['source_frame'][q],['inject',q])
for i in first:gate(i,1)
for j,(root,r)in enumerate(zip(g['roots'],w['rootroles'])):
 if root['kind']=='center':
  emit(2,phys(r),n,0,w['root_frame'][j],['copy',j])
  for t in root['targets']:emit(1,960+t,n,1,-1,['center_read',j,t])
  emit(3,phys(r),n,0,w['root_frame'][j],['erase',j])
readtimes=defaultdict(list)
for z in reversed(w['gauges']):readtimes[w['reads'].get(str(z['role']),len(first))-len(first)].append(z['role'])
assert set(readtimes)<=set(range(len(later)+1))
for j,i in enumerate(later):
 for r in readtimes[j]:compensate(r)
 gate(i,1)
for r in readtimes[len(later)]:compensate(r)
delivery=defaultdict(list)
for pair,z in enumerate(K):delivery[z['deliver_after_root']].append(pair)
for j,(root,r)in enumerate(zip(g['roots'],w['rootroles'])):
 if root['kind']=='side':
  for t in root['targets']:emit(1,960+t,phys(r),1,w['root_frame'][j],['root',j,t])
 for pair in delivery[j]:
  z=K[pair];a,b=z['carrier'],z['passive'];emit(1,a,b,1,z['mix_frame'],['partner_setup',pair,j])
  for t in z['receivers']:emit(1,960+t,a,1,z['deliver_frame'],['partner_delivery',pair,j,t])
for pair,z in enumerate(K):emit(1,z['carrier'],z['passive'],-1,w['full_frame'],['partner_cleanup',pair])
for i in reversed(order):gate(i,-1)
for q in range(960):emit(1,phys(source[q]),q,-1,w['full_frame'],['uninject',q])
assert cursor==len(events)and even==578560
assert set(changed)=={z['setup_event']for z in selection}
assert len(copy_events)==40 and not(set(changed)&{i for i,e in copy_events})
actual_projection=[{'event':i,**e}for i,e in enumerate(events)if e['op']==1 and min(e['a'],e['b'])<960]
assert actual_projection==projection and len(projection)==3840
uses=defaultdict(list)
for e in projection:
 for q in (e['a'],e['b']):
  if q<960:uses[q].append(e)
source_values=[Counter({q:1})for q in range(960)];checks=0;mutants=[]
for e in projection:
 f=F[str(e['frame'])]
 # Every source-incident retimed frame is rank1, rank18, or full. A basis
 # source frame is the exact chi line; cap annihilators are read directly.
 for q in [q for q in (e['a'],e['b'])if q<960]:
  for s,c in source_values[q].items():
   assert c
   if f['dim']==1:
    assert e['frame']==w['source_frame'][s]
   elif f['dim']==18:
    assert all(sum(row[j]for j in g['labels'][s])==0 for row in f['a'])
   else:assert f['dim']==20
   checks+=1
 if e['a']<960:
  a,b,c=e['a'],e['b'],e['c'];assert b<960
  for q,x in source_values[b].items():
   source_values[a][q]+=c*x
   if not source_values[a][q]:del source_values[a][q]
assert source_values==[Counter({q:1})for q in range(960)]and checks==6240
for pair,z in enumerate(selection):
 old=K[pair];a,b=z['carrier'],z['passive'];assert(a,b)==(old['carrier'],old['passive'])
 assert z['new_frame']==old['deliver_frame']and z['old_frame']==old['mix_frame']
 assert z['new_annihilator']==F[str(old['deliver_frame'])]['a']
 assert len(z['new_basis'])==18
 assert all(sum(x*y for x,y in zip(row,basis))==0 for row in z['new_annihilator']for basis in z['new_basis'])
 assert [e['event']for e in uses[a]]==z['carrier_uses']and [e['event']for e in uses[b]]==z['passive_uses']
 assert [e['semantic'][0]for e in uses[a]]==['inject','partner_setup','partner_delivery','partner_delivery','partner_cleanup','uninject']
 assert [e['semantic'][0]for e in uses[b]]==['inject','partner_setup','partner_cleanup','uninject']
 assert z['delivery_events']==[z['setup_event']+1,z['setup_event']+2]
 assert z['carrier_uses'][1]==z['passive_uses'][1]==z['setup_event']
 assert z['carrier_uses'][-2]==z['passive_uses'][-2]==z['cleanup_event']
 # Execute the actual source-mutating subsequence after deleting either
 # recorded operation, rather than only asserting a symbolic inequality.
 for omitted in (z['setup_event'],z['cleanup_event']):
  ca,cb={a:1},{b:1}
  for e in uses[a]:
   if e['event']==omitted or e['a']!=a:continue
   assert e['b']==b
   for q,x in cb.items():ca[q]=ca.get(q,0)+e['c']*x
   ca={q:x for q,x in ca.items()if x}
  assert ca!={a:1};mutants.append([pair,omitted,ca])
def replay(backward):
 cols=[1<<i for i in range(n+1)];norm=[1]*(n+1);live=None;reads=0;copy_lives=0;peak=1
 for e in reversed(events)if backward else events:
  op,a,b,c=e['op'],e['a'],e['b'],e['c']
  if backward and op in(2,3):op=5-op
  if op==1:
   assert c%2;cols[a]^=cols[b];norm[a]+=abs(c)*norm[b];peak=max(peak,norm[a])
   if b==n:assert live is not None;reads+=1
  elif op==2:
   assert live is None and b==n;live=(a,b,e['frame']);cols[b]=cols[a];norm[b]=norm[a];reads=0
  else:
   assert op==3 and live==(a,b,e['frame'])and reads==144 and cols[b]==cols[a]
   live=None;cols[b]=0;norm[b]=0;copy_lives+=1
 assert live is None and copy_lives==20
 for q in range(n):assert cols[q]==((1<<q)^(1<<(q-960))if 960<=q<1920 else 1<<q)
 return peak
assert(replay(False),replay(True))==(22071,959838)
counts=Counter(e['c']for e in events if e['op']==1)
assert sum(counts.values())==350640 and sum(abs(k)*v for k,v in counts.items())==352560
out={'status':'PASS_INDEPENDENT_PR325_RETIMED_EVENT_AND_COPY_AUDIT','head':'0eca9340a3df6141b8e71a41638c3937b3522888',
 'events_reconstructed':len(events),'changed_setup_frames':480,'scalar_projection_unchanged':True,
 'source_incidence_events':len(projection),'integer_source_incidence_checks':checks,
 'omission_controls_rejected':len(mutants),'copied_lifetimes':20,'copy_reads_each':144,
 'all_formal_F2_columns_both_directions':10020,'forward_norm':22071,'inverse_norm':959838,
 'weighted_additions':350640,'literal_unit_additions':352560,
 'inputs':{name:sha(P/name)for name in ['SOURCES.json','retiming-selection.json','scalar-events.json.gz','source-events.json.gz','physical-source-map.json']},
 'checker_sha256':sha(__file__),
 'scope':'Independently reconstructed complete scalar/COPY projection and all new source retiming incidences. Exact endpoint geometry is separate. A complete helper/target local-frame admission and retained interleaved framed-word realization contract remain necessary before a full global matrix claim.'}
(HERE/'EVENT-AUDIT.json').write_text(json.dumps(contract.portable(out),indent=2)+'\n');print(json.dumps(contract.portable(out),indent=2))
