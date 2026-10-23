"""Fresh complete scalar-only actual-overlay recurrence, newly authored.
All installed scalar edits are reconstructed from content-bound selections;
frame/raw-record output is intentionally not claimed. Reorder commutations
are transported using independently checked unchanged operand classes.
"""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,time
from weighted_source_data import read,verify,HEAD
from check_transport import OVER,OVER_SHA,CAND,CAND_SHA
from check_target_chronology import build
CODE=Path(__file__).resolve().parent
from weighted_source_data import OUTPUT,PACKAGE_OUTPUT,PACKAGE_ROOT
HERE=OUTPUT

def scalar_word(w,extra):
 raw,adj,sid,n,F=build(w);g=read('graph.json');K=read('kchron.json')['entries'];ks=read('kernel-selection.json');sinks=read('sink-selection.json')['sinks'];restore=read('restore-selection.json')['entries'];target=read('target-selection.json')['groups'];tc=json.loads((HERE/'target-chronology-result.json').read_text())
 assert w['pairs']==read('bitword/selected/bit/word_p10.json.gz')['pairs']or hashlib.sha256(OVER.read_bytes()).hexdigest()==OVER_SHA
 baseline=w['pairs']==read('bitword/selected/bit/word_p10.json.gz')['pairs']
 which='old_'if baseline else'new_'
 cut=tc['groups'][0][which+'cut'];close={e[which+'close']:target[e['group']]for e in tc['groups']};deps={960+int(q):e[which+'close']for e in tc['groups']for q in target[e['group']]['dependent']}
 assert hashlib.sha256((CODE/'check_target_chronology.py').read_bytes()).hexdigest()==tc['checker_sha256']
 # Target compression; retain semantic identities through scalar-only edits.
 events=[]
 for i,r in enumerate(raw):
  if r[0]==1:
   _,a,b,c,f,sem=r
   if a not in deps or not cut<i<=deps[a]:events.append((1,a,b,c,sem))
  elif r[0]in(2,3):events.append((r[0],r[1],r[2],0,r[-1]))
  if i==cut:
   for e in target:
    for q,ps in e['dependent'].items():
     for p in ps:events.append((1,960+int(q),960+p,-1,('target_setup',int(q),p)))
  if i in close:
   e=close[i]
   for q,ps in e['dependent'].items():
    for p in ps:events.append((1,960+int(q),960+p,1,('target_restore',int(q),p)))
 byroot=defaultdict(list)
 for e in K:byroot[e['deliver_after_root']].append(e)
 for j,(root,r)in enumerate(zip(g['roots'],w['rootroles'])):
  if root['kind']=='side':
   for q in root['targets']:events.append((1,960+q,sid(r),1,('root',j,r,q)))
  for e in byroot[j]:
   a,b=e['carrier'],e['passive'];events.append((1,a,b,1,('partner_setup',a,b)))
   for q in e['receivers']:events.append((1,960+q,a,1,('partner_delivery',a,q)))
 for e in K:events.append((1,e['carrier'],e['passive'],-1,('partner_cleanup',e['carrier'],e['passive'])))
 # Early restoration is inserted immediately before the first cleanup ADD.
 moved={(e['helper'],e['donor']):e for e in restore};movedhits=Counter()
 for e in sorted(restore,key=lambda e:e['helper']):events.append((1,e['helper'],e['donor'],e['coefficient'],('early_restore',e['helper'],e['donor'])))
 phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase]
 for i in reversed(order):
  a,b,_=w['ops'][i];a,b=sid(a),sid(b)
  if(a,b)in moved:movedhits[a,b]+=1;continue
  events.append((1,a,b,-1,('cleanup',i)))
 assert set(movedhits)==set(moved)and set(movedhits.values())=={1}
 for source,r in w['sources'].items():events.append((1,sid(r),int(source),-1,('uninject',int(source),r)))
 # Kernel literal cuts are invariant because the complete initial plain
 # prefix and retained physical IDs are unchanged under this matching.
 kernels=[dict(pivot=e['a'],donors=[e['b']],rank=e['rank'],cut_read=e['cut_read'])for e in ks['pairs']]+[dict(pivot=e['pivot'],donors=e['donors'],rank=e['rank'],cut_read=e['cut_read'])for e in ks['families']]
 oldp={e['pivot']for e in kernels};newp={e['pivot']for e in extra};at=defaultdict(list)
 for e in kernels:at[tuple(e['cut_read'])].append(e)
 plainends=[i for i,r in enumerate(events)if r[0]==1 and r[-1][0]=='plain'];lastplain=max(plainends)
 out=[];hits=set();removed=Counter();added=Counter()
 for i,r in enumerate(events):
  op,a,b,c,sem=r;plain=op==1 and sem[0]=='plain'
  if plain and b in oldp|newp:removed['old'if b in oldp else'new']+=1;removed['old_units'if b in oldp else'new_units']+=abs(c)
  else:out.append(r)
  if plain:
   for e in sorted(at.get((a,b,c),[]),key=lambda e:(e['rank'],e['pivot'])):
    hits.add(e['pivot'])
    for d in e['donors']:out.append((1,d,e['pivot'],1,('kernel_setup',e['pivot'],d)));added['old']+=1
  if i==lastplain:
   for e in extra:
    for d in e['donors']:out.append((1,d,e['pivot'],1,('new_setup',e['pivot'],d)));added['new']+=1
 assert len(hits)==775
 for e in kernels:
  for d in e['donors']:out.append((1,d,e['pivot'],-1,('kernel_restore',e['pivot'],d)))
 for e in reversed(extra):
  for d in reversed(e['donors']):out.append((1,d,e['pivot'],-1,('new_restore',e['pivot'],d)))
 # Sink edits are bound by exact virtual operation identities and literal
 # coefficient/target patterns, independently of raw record-number shifts.
 sink={sid(e['role']):e for e in sinks};endcopy=max(i for i,r in enumerate(out)if r[0]==3);lastwrites={};writes=Counter()
 for i,r in enumerate(out):
  if r[0]==1 and r[1]in sink and r[-1][0]=='forward':lastwrites[r[1]]=i;writes[r[1]]+=1
 assert all(writes[s]==e['forward_writes']for s,e in sink.items())
 final=[];skipped=Counter();redirected=0
 for i,r in enumerate(out):
  op,a,b,c,sem=r
  if op==1 and b in sink:
   assert sem[0]in('plain','root');skipped[sem[0]]+=1
  elif op==1 and a in sink:
   if sem[0]=='forward':final.append((1,sink[a]['pivot'],b,c,('sink_redirect',a,*sem[1:])));redirected+=1
   else:assert sem[0]=='cleanup';skipped['cleanup']+=1
  else:final.append(r)
  if i==endcopy:
   for s,e in sorted(sink.items()):
    for q in e['targets']:
     if q!=e['pivot']:final.append((1,q,e['pivot'],-1,('sink_setup',s,q)))
  if op==1 and a in lastwrites and lastwrites[a]==i:
   e=sink[a]
   for q in e['targets']:
    if q!=e['pivot']:final.append((1,q,e['pivot'],1,('sink_restore',a,q)))
 assert redirected==sum(e['forward_writes']for e in sinks)
 assert not any(r[0]==1 and(r[1]in sink or r[2]in sink)for r in final)
 return final,n,dict(removed),dict(added),dict(skipped)

def replay(events,n,reverse=False,omit=None):
 cols=[1<<i for i in range(n+1)];norm=[1]*(n+1);center=None;digest=hashlib.sha256();count=0;coeff=Counter()
 for index in(range(len(events)-1,-1,-1)if reverse else range(len(events))):
  op,a,b,c,sem=events[index]
  if op==1:
   if sem[0]==omit:continue
   assert a!=b and c%2;cols[a]^=cols[b];norm[a]+=abs(c)*norm[b];count+=1;coeff[abs(c)]+=1
   source=center if b==n else b
   digest.update((json.dumps([a,source,-c if reverse else c],separators=(',',':'))+'\n').encode())
  elif op==(3 if reverse else 2):assert center is None;center=a;cols[b]=cols[a];norm[b]=norm[a]
  else:assert center==a and cols[b]==cols[a];center=None
 assert center is None
 wrong=[i for i in range(n)if cols[i]!=((1<<i)^((1<<(i-960))if 960<=i<1920 else 0))]
 if omit:assert wrong
 else:assert not wrong,wrong[:20]
 return dict(all_columns=not wrong,columns=n,weighted_additions=count,literal_unit_additions=sum(k*v for k,v in coeff.items()),coefficient_histogram=dict(coeff),max_row_l1=max(norm),max_source=max(norm[:960]),max_target=max(norm[960:1920]),max_helper=max(norm[1920:n]),event_sha256=digest.hexdigest(),reverse=reverse)

def run():
 t=time.monotonic();verify();w=json.loads(OVER.read_text());extra=json.loads((HERE/'rebound-candidate19.json').read_text())['entries'];assert hashlib.sha256(OVER.read_bytes()).hexdigest()==OVER_SHA
 baseline,n,old_removed,old_added,old_skipped=scalar_word(read('bitword/selected/bit/word_p10.json.gz'),[]);baselineF=replay(baseline,n);baselineB=replay(baseline,n,True);pins=read('word-pins.json')
 assert baselineF['weighted_additions']==pins['weighted_scalar_events']and baselineF['literal_unit_additions']==pins['literal_unit_additions']
 assert baselineF['max_row_l1']==pins['forward_max_row_l1']and baselineB['max_row_l1']==pins['inverse_max_row_l1'],('baseline norm differs',baselineF,baselineB)
 events,n,removed,added,skipped=scalar_word(w,extra);F=replay(events,n);B=replay(events,n,True);replay(events,n,omit='new_setup');replay(events,n,omit='new_restore')
 assert removed['old']==old_removed['old']and removed['old_units']==old_removed['old_units']
 payload=64*F['max_row_l1']**3*B['max_row_l1']**2
 out=dict(status='PASS_FRESH_WEIGHTED892_PLUS19_SCALAR_RECURRENCE',head=HEAD,overlay_sha256=OVER_SHA,original_candidate_sha256=CAND_SHA,rebound_candidate_sha256=hashlib.sha256((HERE/'rebound-candidate19.json').read_bytes()).hexdigest(),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),baseline_forward=baselineF,baseline_inverse=baselineB,forward=F,inverse=B,final_compact_columns=n-7,retained_sink_spectator_columns=7,removed_initial_reads=removed,setup_counts=added,sink_deletions=skipped,payload_bound=payload,payload_bits=payload.bit_length(),retained_payload_cap_2_to104=payload<2**104,all_setup_and_restore_omission_controls_rejected=True,scope='Fresh complete scalar/COPY event recurrence before the133 inherited commutative reorder moves; matches original baseline ADD/unit counts and forward/inverse norms exactly. New matching,775 kernels,120 target groups,240 early restorations,7 sinks and fixed19 are replayed on actual new physical columns. Frame/raw-record/hash regeneration of the final pipeline and the original raw-crossing verification remain separate.',dependency_sha256={name:hashlib.sha256(((CODE if name.endswith('.py')else HERE)/name).read_bytes()).hexdigest()for name in['weighted_source_data.py','check_transport.py','check_target_chronology.py','target-chronology-result.json','rebound-candidate19.json']})
 (HERE/'scalar-recurrence-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':run()
