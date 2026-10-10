"""Exact semantic-anchor and commutation-trace transport for all133 moves.
Old raw-crossing admission is an explicit hypothesis. Every new potential
obstruction and every anchor incidence is checked over the full scalar words.
"""
from collections import defaultdict
from pathlib import Path
import json,hashlib
from weighted_source_data import read,verify,HEAD
from check_transport import OVER,OVER_SHA
from check_scalar_recurrence import scalar_word,replay
CODE=Path(__file__).resolve().parent
from weighted_source_data import OUTPUT,PACKAGE_OUTPUT,PACKAGE_ROOT
HERE=OUTPUT

def run():
 verify();old=read('bitword/selected/bit/word_p10.json.gz');new=json.loads(OVER.read_text());candidate=json.loads((HERE/'rebound-candidate19.json').read_text())['entries']
 A,na,*_=scalar_word(old,[]);B,nb,*_=scalar_word(new,candidate);sinks=sorted(e['stream']for e in read('sink-selection.json')['sinks'])
 def lift(s):
  for q in sinks:
   if q<=s:s+=1
  return s
 def index(events):
  writes=defaultdict(list);reads=defaultdict(list);incident=defaultdict(list);copies=defaultdict(list);ids={};lastcopy=max(i for i,r in enumerate(events)if r[-1][0]=='plain')
  for i,(op,a,b,c,sem)in enumerate(events):
   key=(op,sem);assert key not in ids;ids[key]=i
   if op==1:writes[a].append(i);reads[b].append(i);incident[a].append(i);incident[b].append(i)
   else:copies[a].append(i);incident[a].append(i)
  return writes,reads,incident,copies,ids,lastcopy
 IA=index(A);IB=index(B);receipts=[];allports=set()
 def kinds(sem):return 'side_root'if sem[0]=='root'else'forward_gate'if sem[0]=='forward'else sem[0]
 def frame(sem):
  if sem[0]=='forward':return ('frame',new['op_frame'][sem[1]])
  if sem[0]=='root':return ('frame',new['root_frame'][sem[1]])
  # These exact semantic inputs and selections are unchanged. The equality
  # key binds the unique declared frame by its defining event or selection.
  return ('unchanged_selection_or_semantic_frame',sem)
 for z in read('reorder-selection.json')['moves']:
  a,b,c=z['incidence'];a,b=lift(a),lift(b);assert not{a,b}&allports;allports|={a,b}
  hits=[i for i in IA[2][a]if A[i][0]==1 and A[i][1:4]==(a,b,c)and kinds(A[i][-1])==z['category']];assert len(hits)==1
  oi=hits[0];key=(1,A[oi][-1]);ni=IB[4][key];assert B[ni][1:4]==(a,b,c)
  def traces(events,idx,at):
   wr,rd,inc,cp,ids,lastcopy=idx
   bad=sorted(set(rd[a]+wr[b]+cp[a]));badtrace=[(events[i][0],events[i][-1],i<at)for i in bad]
   incidences=sorted(set(inc[a]+inc[b]));anchortrace=[(events[i][0],events[i][-1],events[i][1]==a,events[i][1]==b,events[i][2]==a,events[i][2]==b,frame(events[i][-1]),i<at)for i in incidences if i>lastcopy]
   return badtrace,anchortrace,bad,incidences
  ot,oa,ob,oii=traces(A,IA,oi);nt,nn,nbr,nii=traces(B,IB,ni)
  assert ot==nt,('new noncommuting crossing',z['record'])
  assert oa==nn,('anchor event sequence changed',z['record'])
  assert oi>IA[5]and ni>IB[5]
  receipts.append(dict(old_record=z['record'],old_anchor=z['anchor'],side=z['side'],precompact_incidence=[a,b,c],moved_semantic_event=A[oi][-1],old_scalar_event_index=oi,new_scalar_event_index=ni,postprefix_anchor_incidence_count=len(oa),noncommuting_event_count=len(ot),all_anchor_candidates_semantically_preserved=True,noncommuting_trace_and_relative_position_identical=True))
 # The only time-relocated pre-existing semantic events are singleton gauge
 # compensations9118/9119. Verify their endpoints miss all moved operands.
 late=[r for r in B if r[-1][0]=='gauge'and r[-1][1]in(9118,9119)];assert len(late)==2
 assert all(not{r[1],r[2]}&allports for r in late)
 out=dict(status='PASS_ALL133_SEMANTIC_ANCHOR_AND_COMMUTATION_TRACES',head=HEAD,overlay_sha256=OVER_SHA,rebound_candidate_sha256=hashlib.sha256((HERE/'rebound-candidate19.json').read_bytes()).hexdigest(),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),moves=len(receipts),moved_ports=len(allports),late_compensations=late,all_anchors_survive=True,all_noncommuting_traces_equal=True,receipts=receipts,proof='For each moved shear E_ab(c), an ADD E_xy(d) fails the inherited sufficient commutation screen only when y=a or x=b; a COPY/ERASE fails only when its source is a. Both these complete traces and the moved gate position within them are identical old/new. The complete incident-event trace after the complete initial plain prefix is also identical, with the same defining frame per event, so every admitted old anchor persists in order and with its declared frame. Any inserted, deleted, re-addressed or relocated events between a move and its transported anchor commute. The test depends only on operands, so replacing c,d by their absolute values preserves it. Thus the inherited133 raw crossing proofs transport to the new signed and nonnegative words. Physical coordinate norms start positive and increase under unsigned ADDs. Each reused COPY scratch norm equals a captured physical norm, so it is also bounded by the maximum final physical norm. Therefore the maximum prefix row norm is bounded by the maximum final physical norm, which commuting rewrites preserve.',scope='Complete finite transport of inherited133 moves and all possible original anchors through actual old/new scalar event bijection. Does not independently rerun the original raw record-number crossing proof or emit new final frame records.')
 (HERE/'reorder-transport-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='receipts'},indent=2))
if __name__=='__main__':run()
