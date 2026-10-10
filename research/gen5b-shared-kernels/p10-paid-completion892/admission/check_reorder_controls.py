"""Independent injected-event controls for each of133 transported reorders."""
from pathlib import Path
from collections import defaultdict
import json,hashlib
from weighted_source_data import verify,HEAD,OUTPUT
from admission_config import OVER,OVER_SHA
from check_scalar_recurrence import scalar_word
P=Path(__file__).resolve().parent

def run():
 verify();assert hashlib.sha256(OVER.read_bytes()).hexdigest()==OVER_SHA
 B,n,*_=scalar_word(json.loads(OVER.read_text()),[])
 proof=json.loads((OUTPUT/'reorder-transport-result.json').read_text());assert proof['overlay_sha256']==OVER_SHA
 incidence=defaultdict(list);lastplain=max(i for i,r in enumerate(B)if r[-1][0]=='plain')
 for i,r in enumerate(B):
  op,a,b,c,sem=r;incidence[a].append(i)
  if op==1:incidence[b].append(i)
 controls=[]
 def screen(a,b,at,rows):
  bad=[];anchors=[]
  for i,r in sorted(rows,key=lambda x:x[0]):
   op,x,y,c,sem=r
   if(op==1 and(y==a or x==b))or(op in(2,3)and x==a):bad.append((op,sem,i<at))
   if i>lastplain and(x in(a,b)or(op==1 and y in(a,b))):anchors.append((op,sem,x==a,x==b,y==a,y==b,i<at))
  return bad,anchors
 for e in proof['receipts']:
  a,b,c=e['new_precompact_incidence'];at=e['new_scalar_event_index'];assert B[at][1:4]==(a,b,c)
  rows=[(i,B[i])for i in sorted(set(incidence[a]+incidence[b]))];good=screen(a,b,at,rows)
  assert len(good[0])==e['noncommuting_event_count']and len(good[1])==e['postprefix_anchor_incidence_count']
  spare=next(s for s in range(n)if s not in(a,b));spare2=next(s for s in range(n)if s not in(a,b,spare))
  # Writing b cannot commute past E_ab. The complete bad trace must change.
  bad=(1,b,spare,1,('negative_write_moved_source',e['old_record']))
  assert screen(a,b,at,rows+[(at+0.5,bad)])[0]!=good[0]
  # A same-target ADD commutes, but creates a new possible anchor incidence.
  anchor=(1,a,spare,1,('negative_extra_anchor',e['old_record']))
  changed=screen(a,b,at,rows+[(at+0.5,anchor)])
  assert changed[0]==good[0]and changed[1]!=good[1]
  # A fully disjoint ADD is accepted by both screens.
  disjoint=(1,spare,spare2,1,('positive_disjoint',e['old_record']))
  assert screen(a,b,at,rows+[(at+0.5,disjoint)])==good
  controls.append(e['old_record'])
 assert len(controls)==133
 out=dict(status='PASS_ALL133_REORDER_TRACE_MUTATION_CONTROLS',head=HEAD,overlay_sha256=OVER_SHA,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),moves_checked=len(controls),noncommuting_insertions_rejected=133,commuting_extra_anchor_insertions_rejected=133,disjoint_positive_controls_accepted=133,records=controls,dependency_sha256={name:hashlib.sha256((P/name).read_bytes()).hexdigest()for name in ['weighted_source_data.py','admission_config.py','check_scalar_recurrence.py']},reorder_receipt_sha256=hashlib.sha256((OUTPUT/'reorder-transport-result.json').read_bytes()).hexdigest())
 (OUTPUT/'reorder-controls-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='records'},indent=2))
if __name__=='__main__':run()
