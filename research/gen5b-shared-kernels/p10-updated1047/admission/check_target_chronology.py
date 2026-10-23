"""Fresh partial raw-prefix regeneration; no upstream executable imported.
Rebuilds original pre-descent prefix boundaries, then binds them to semantic
ADD identities on the actual matching overlay, and checks target chains.
"""
from pathlib import Path
from collections import defaultdict,Counter
import hashlib,json,time
from weighted_source_data import read,verify,HEAD
from check_transport import OVER,OVER_SHA,rr,null,included
CODE=Path(__file__).resolve().parent
from weighted_source_data import OUTPUT,PACKAGE_OUTPUT,PACKAGE_ROOT
HERE=OUTPUT

def build(w):
 g=read('graph.json');F={int(k):v for k,v in read('frames.json')['frames'].items()};ga={e['role']:e for e in w['gauges']};alias={b:a for a,b in w['pairs']};regs=sorted(set(range(9120))-set(alias));sid0={r:1920+i for i,r in enumerate(regs)};sid=lambda r:sid0[alias.get(r,r)];n=1920+len(regs)
 phase=sorted(w['phase1']);ps=set(phase);rest=[i for i in range(len(w['ops']))if i not in ps];order=phase+rest
 adj=[{}for _ in range(9120)]
 for root,r in zip(g['roots'],w['rootroles']):
  for t in root['targets']:adj[r][t]=adj[r].get(t,0)+1
 for i in reversed(order):
  a,b,_=w['ops'][i]
  for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
 state={i:w['source_frame'][i]for i in range(960)}|{960+t:'ZERO'for t in range(960)}|{sid(r):ga[r]['frame']if r in ga else'ZERO'for r in regs};initial=dict(state);rows=[]
 def move(s,f,sem):
  if state[s]!=f:rows.append((0,s,state[s],f,sem));state[s]=f
 def add(a,b,c,f,sem,copy=False):
  move(a,f,sem)
  if not copy:move(b,f,sem)
  rows.append((1,a,b,c,f,sem))
 for r in range(9120):
  if r in ga:continue
  for t,c in adj[r].items():add(960+t,sid(r),-c,'ZERO',('plain',r,t))
 for source,r in w['sources'].items():add(sid(r),int(source),1,w['source_frame'][int(source)],('inject',int(source),r))
 for i in phase:
  a,b,_=w['ops'][i];add(sid(a),sid(b),1,w['op_frame'][i],('forward',i,a,b))
 for j,(r,s)in enumerate(zip(g['roots'],w['rootroles'])):
  if r['kind']!='center':continue
  f=w['root_frame'][j];sem=('center',j,s);move(sid(s),f,sem);rows.append((2,sid(s),n,f,'ZERO',sem));state[n]='ZERO'
  for t in r['targets']:add(960+t,n,1,'ZERO',('center_read',j,s,t),copy=True)
  rows.append((3,sid(s),n,f,'ZERO',sem));del state[n]
 at=defaultdict(list)
 for e in reversed(w['gauges']):at[w['reads'].get(str(e['role']),len(phase))-len(phase)].append(e['role'])
 for j,i in enumerate(rest+[None]):
  for r in at[j]:
   for t,c in adj[r].items():
    sem=('gauge',r,t);move(sid(r),ga[r]['frame'],sem);move(960+t,ga[r]['frame'],sem);add(960+t,sid(r),-c,ga[r]['frame'],sem)
  if i is not None:
   a,b,_=w['ops'][i];add(sid(a),sid(b),1,w['op_frame'][i],('forward',i,a,b))
 # parity-fuse pending moves exactly as a mathematically independent stream
 # normalizer, using event identities carried through each move/ADD.
 out=[];pending={}
 def flush(a):
  if a in pending:out.append(pending.pop(a))
 for row in rows:
  op,a,b,*_=row
  if op==0:
   if a in pending:row=(0,a,pending[a][2],row[3],row[4])
   pending[a]=row;continue
  if op==1 and row[3]%2==0:continue
  flush(a);flush(b);out.append(row)
 # Stop at last forward op, retaining deferred endpoint-only moves outside
 # this partial prefix. Every queried boundary is strictly before that point.
 # The descent pass discards input MOVE records and regenerates each ADD
 # need in destination/source order. Its selected retimings are all later.
 desc=[];state=dict(initial)
 def dmove(a,f,sem):
  if state[a]!=f:desc.append((0,a,state[a],f,sem));state[a]=f
 for row in out:
  if row[0]==0:continue
  if row[0]==1:
   _,a,b,c,f,sem=row;dmove(a,f,sem)
   if b!=n:dmove(b,f,sem)
  elif row[0]==2:
   _,a,b,f,zero,sem=row;dmove(a,f,sem);state[b]=zero
  else:del state[row[2]]
  desc.append(row)
 return desc,adj,sid,n,F

def run():
 verify();t=time.monotonic();old=read('bitword/selected/bit/word_p10.json.gz');new=json.loads(OVER.read_text());assert hashlib.sha256(OVER.read_bytes()).hexdigest()==OVER_SHA
 A,adj,os,on,F=build(old);B,_,ns,nn,_=build(new);target=read('target-selection.json');cut=target['cut_record'];minimum_descent=min(e['record']for e in read('descent-selection.json')['entries']);assert max(e['close_after_record']for e in target['groups'])<minimum_descent
 assert A[cut][0]==0 and A[cut][1]in range(960,1920) and A[cut][2]=='ZERO',('cut not first pending target MOVE',cut,A[cut])
 assert max(i for i,r in enumerate(A)if r[0]==3)<cut
 # Descents rebuild MOVE instructions but have no retimed event in this prefix;
 # its canonical pending-MOVE form is therefore unchanged.
 assert all(A[e['close_after_record']][0]==1 for e in target['groups'])
 lookup={r[-1]:i for i,r in enumerate(B)if r[0]in(1,3)};assert len(lookup)==sum(r[0]in(1,3)for r in B)
 reboundcut=next(i for i,r in enumerate(B)if r==A[cut]);assert reboundcut<lookup[A[cut][-1]]
 receipts=[];relations=0
 # F2 columns for whole prefix, tracking fresh relation responses after cut.
 columns=[1<<i for i in range(nn+1)];responses={t:0 for e in target['groups']for t in e['targets']};owner={t:j for j,e in enumerate(target['groups'])for t in e['targets']};closes={};targetpaths=defaultdict(list)
 for j,e in enumerate(target['groups']):
  oldclose=e['close_after_record'];sem=A[oldclose][-1];newclose=lookup[sem];assert oldclose>cut and newclose>reboundcut;closes[newclose]=j
  receipts.append(dict(group=j,old_cut=cut,new_cut=reboundcut,old_close=oldclose,new_close=newclose,close_semantic_event=sem,old_close_event=A[oldclose],new_close_event=B[newclose]))
 assert len(closes)==120
 center=None;close_source_columns={};negative=[]
 for i,row in enumerate(B):
  op,a,b,*_=row
  if op==2:assert center is None;center=a;columns[b]=columns[a]
  if op==3:assert center==a;center=None
  if op==1:
   _,a,b,c,f,sem=row
   if i>reboundcut:
    if 960<=b<1920:assert b-960 not in owner or i>receipts[owner[b-960]]['new_close']
    if a-960 in owner and i<=receipts[owner[a-960]]['new_close']:responses[a-960]^=columns[b]
   if i in closes:close_source_columns[i]=columns[b]
   columns[a]^=columns[b]
   if 960<=a<1920 and f!='ZERO':
    if not targetpaths[a-960]or targetpaths[a-960][-1]!=f:targetpaths[a-960].append(f)
  if i in closes:
   j=closes[i];e=target['groups'][j]
   for q,ps in e['dependent'].items():
    z=responses[int(q)]
    for p in ps:z^=responses[p]
    assert z==0,('literal target relation',j)
    relations+=1
    if j==119:
     assert B[i][1]-960 in ps and z^close_source_columns[i]
     negative.append('Omitting group119 closing retained read makes its literal dependency nonzero')
 # All new target read chains exact subspace nesting, and compressed group
 # close frame included before every later target read.
 cache={}
 def ann(f):
  if f not in cache:cache[f]=F[f]['a']if'a'in F[f]else null(F[f]['b'])
  return cache[f]
 checks=set()
 for q,path in targetpaths.items():
  for x,y in zip(path,path[1:]):
   if(x,y)not in checks:assert included(ann(y),ann(x));checks.add((x,y))
 for j,e in enumerate(target['groups']):
  remaining=set(e['targets'])
  for row in B[receipts[j]['new_close']+1:]:
   if row[0]==1 and row[1]-960 in remaining and row[4]!='ZERO':
    assert all(sum(x*y for x,y in zip(a,b))==0 for a in ann(row[4])for b in e['close_basis'])
    remaining.remove(row[1]-960)
    # Earliest later event per target suffices by established nesting.
    if not remaining:break
  # A target with no remaining forward-prefix read is a terminal spectator
  # here; its later side/partner frame contract is inherited unchanged.
 # Fresh compressed target state at every close: check every member's
 # incoming frame against the close span, then every later required frame.
 targetstate={q:[]for q in owner};state_checks=0
 def basis(fid):return F[fid]['b']if'b'in F[fid]else null(F[fid]['a'])
 def append_need(q,B):
  nonlocal state_checks
  assert included(targetstate[q],B),('compressed target nonnesting',q)
  targetstate[q]=B;state_checks+=1
 for i,row in enumerate(B):
  if row[0]==1:
   _,a,b,c,f,sem=row;q=a-960
   if q in owner and f!='ZERO':
    e=target['groups'][owner[q]]
    dropped=str(q)in e['dependent']and reboundcut<i<=receipts[owner[q]]['new_close']
    if not dropped:append_need(q,basis(f))
  if i in closes:
   j=closes[i];e=target['groups'][j]
   for q in e['targets']:append_need(q,e['close_basis'])
 # Continue all target paths through side and partner deliveries, unchanged
 # as semantic events by the rematching.
 g=read('graph.json');K=read('kchron.json')['entries'];deliveries=defaultdict(list)
 for e in K:deliveries[e['deliver_after_root']].append(e)
 for j,root in enumerate(g['roots']):
  if root['kind']=='side':
   for q in root['targets']:
    if q in targetstate:append_need(q,basis(new['root_frame'][j]))
  for e in deliveries[j]:
   for q in e['receivers']:
    if q in targetstate:append_need(q,basis(e['deliver_frame']))
 gauges={r[-1][1]:i for i,r in enumerate(B)if r[0]==1 and r[-1][0]=='gauge'and r[-1][1]in(9118,9119)}
 oldgauges={r[-1][1]:i for i,r in enumerate(A)if r[0]==1 and r[-1][0]=='gauge'and r[-1][1]in(9118,9119)}
 special=receipts[119];assert all(i>special['new_close']for i in gauges.values());assert all(i>special['old_close']for i in oldgauges.values())
 out=dict(status='PASS_FRESH_PARTIAL_RAW_PREFIX_AND_ALL120_TARGET_CUTS',head=HEAD,overlay_sha256=OVER_SHA,old_physical_columns=on,new_physical_columns=nn,global_cut_semantic_event=A[cut],all120_literal_target_relations=relations,minimum_descent_record=minimum_descent,max_original_close=max(e['close_after_record']for e in target['groups']),group119=special,old_late_gauge_records=oldgauges,new_late_gauge_records=gauges,new_late_gauge_event_details=[B[i]for i in gauges.values()],all_gauge_target_paths_nested=True,all480_group_members_checked_at_close=True,compressed_target_state_containment_checks=state_checks,negative_controls=negative,unique_target_containment_pairs=len(checks),groups=receipts,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Fresh original and new raw prefix regenerated through last forward gate, stopping before side-root/partner/kernel/restore/sink/reorder tail. Target cuts rebound by unique semantic event identity; all120 literal relations checked on the actual new physical columns. This does not emit the complete final pipeline.',dependency_sha256={'weighted_source_data.py':hashlib.sha256((CODE/'weighted_source_data.py').read_bytes()).hexdigest(),'check_transport.py':hashlib.sha256((CODE/'check_transport.py').read_bytes()).hexdigest()})
 (HERE/'target-chronology-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
