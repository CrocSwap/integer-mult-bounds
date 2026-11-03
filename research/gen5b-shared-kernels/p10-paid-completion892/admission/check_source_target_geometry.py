"""New exact source and target required-frame audit on the final scalar word.
This includes target compression and sink edits, and never runs upstream code.
Fixed frame admissibility is inherited from pinned definitions; all containment
relations, source line identities, and terminal target caps are checked here.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import hashlib,json
from weighted_source_data import read,verify,HEAD,OUTPUT
from admission_config import OVER,OVER_SHA
from check_transport import rr,null,included
from check_scalar_recurrence import scalar_word,replay
P=Path(__file__).resolve().parent

def run():
 verify();assert hashlib.sha256(OVER.read_bytes()).hexdigest()==OVER_SHA
 w=json.loads(OVER.read_text());g=read('graph.json');F={int(k):v for k,v in read('frames.json')['frames'].items()};ga={e['role']:e for e in w['gauges']};tg=read('target-selection.json')['groups'];ks=read('kchron.json')['entries'];sn=read('sink-selection.json')['sinks']
 groups={int(q):j for j,e in enumerate(tg)for q in e['dependent']};partners={e['carrier']:e for e in ks};sinks={e['stream']:e for e in sn}
 ev,n,*_=scalar_word(w,[])
 @lru_cache(None)
 def info(key):
  kind,x=key
  if kind=='zero':return 0,[]
  if kind=='frame':return F[x]['dim'],F[x]['a']if'a'in F[x]else null(F[x]['b'])
  if kind=='close':return len(tg[x]['close_basis']),null(tg[x]['close_basis'])
  if kind=='sink':return len(sinks[x]['root_frame_basis']),null(sinks[x]['root_frame_basis'])
  if kind=='cap':return 19,[[3*int(j in g['labels'][x])-1 for j in range(20)]]
  raise AssertionError(key)
 def frame(sem):
  k=sem[0]
  if k in('plain','center_read','target_setup','sink_setup'):return ('zero',0)
  if k=='inject':return ('frame',w['source_frame'][sem[1]])
  if k in('uninject','partner_cleanup'):return ('frame',w['full_frame'])
  if k=='gauge':return ('frame',ga[sem[1]]['frame'])
  if k=='target_restore':return ('close',groups[sem[1]])
  if k=='root':return ('frame',w['root_frame'][sem[1]])
  if k=='partner_setup':return ('frame',partners[sem[1]]['mix_frame'])
  if k=='partner_delivery':return ('frame',partners[sem[1]]['deliver_frame'])
  if k=='sink_redirect':return ('frame',w['op_frame'][sem[2]])
  if k=='sink_restore':return ('sink',sem[1])
  raise AssertionError(('unmapped external frame',sem))
 checks=set();events=Counter();paths={q:[('frame',w['source_frame'][q])]if q<960 else[('zero',0)]for q in range(1920)}
 def append(q,f):
  p=paths[q][-1]
  if p==f:return
  if(p,f)not in checks:
   if p[0]=='zero':d=0
   else:
    d,A=info(p);e,B=info(f);assert d<=e and included(B,A),('external nonnesting',q,p,f)
   checks.add((p,f))
  paths[q].append(f)
 for op,a,b,c,sem in ev:
  if op!=1:continue
  ext=[s for s in(a,b)if s<1920]
  if not ext:continue
  f=frame(sem)
  for s in ext:append(s,f);events['source'if s<960 else'target']+=1
 for q in range(960):
  d,A=info(('frame',w['source_frame'][q]));chi=[int(j in g['labels'][q])for j in range(20)]
  assert d==1 and len(rr(A)[0])==19 and all(sum(a*b for a,b in zip(chi,row))==0 for row in A)
  append(q,('frame',w['full_frame']));append(960+q,('cap',q))
 # All960 source partner chains are read from the immutable definitions and
 # must match the exact stage needs. No source participates in a reuse pair.
 members=Counter()
 for e in ks:
  a,b=e['carrier'],e['passive'];members.update([a,b]);assert len(set(g['labels'][a])&set(g['labels'][b]))==1
  expected_a=[w['source_frame'][a],e['mix_frame'],e['deliver_frame'],w['full_frame']];expected_b=[w['source_frame'][b],e['mix_frame'],w['full_frame']]
  assert e['carrier_chain']==expected_a and e['passive_chain']==expected_b
  assert paths[a]==[('frame',f)for f in expected_a]and paths[b]==[('frame',f)for f in expected_b]
 assert members==Counter({q:1 for q in range(960)})
 assert not({r for p in w['pairs']for r in p}&set(w['sources'].values()))
 # Independent omission checks for each newly delayed compensation are made
 # on the whole final scalar/COPY stream without changing the replay program.
 controls=[]
 for role in(9118,9119):
  mutated=[r for r in ev if not(r[0]==1 and r[-1][0]=='gauge'and r[-1][1]==role)]
  assert len(ev)-len(mutated)==1
  try:replay(mutated,n)
  except AssertionError:controls.append(role)
  else:raise AssertionError(('omitted late gauge admitted',role))
 out=dict(status='PASS_ORIGINAL_SOURCE_AND_FINAL_TARGET_SCALAR_FRAME_CHAINS',head=HEAD,overlay_sha256=OVER_SHA,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_columns=960,target_columns=960,partner_pairs=len(ks),external_event_incidences=dict(events),unique_containment_pairs=len(checks),source_line_identities_and_partner_chains_exact=True,all_terminal_targets_in_declared_cap=True,new_gauge_omission_controls_rejected=controls,source_path_changes=0,paths={str(k):v for k,v in paths.items()},scope='Original pre-descent source chronology and final target chronology. Actual rank18 source setups and final source chains are verified separately by the mandatory source correction. Existing rational frame nondegeneracy, raw-record reorder admission, compiler, prime and all-size hypotheses remain inherited. No complete final raw frame word is emitted.',dependency_sha256={name:hashlib.sha256((P/name).read_bytes()).hexdigest()for name in ['weighted_source_data.py','admission_config.py','check_transport.py','check_target_chronology.py','check_scalar_recurrence.py']})
 (OUTPUT/'source-target-geometry-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='paths'},indent=2))
if __name__=='__main__':run()
