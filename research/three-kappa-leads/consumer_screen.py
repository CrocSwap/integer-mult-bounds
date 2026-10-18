#!/usr/bin/env python3
"""Exact boundary test for a shared five-plane scratch with native consumers."""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,tarfile,hashlib,importlib.util,argparse
from check_inputs import authenticate
authenticate()
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
ARCHIVE=ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz'
BASE='candidate/strict/global/base/split-centres/'
def need(x,m):
 if not x:raise ValueError(m)
def translate(v,delta):return {x^delta:y for x,y in v.items()}
def add(dst,src,c):
 out=dst.copy()
 for x,y in src.items():out[x]=out.get(x,Q(0))+c*y
 return {x:y for x,y in out.items()if y}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',type=Path);a=ap.parse_args()
 path=ROOT/'research/five-plane-port-p112-seed1f7fdfe4/core.py'
 spec=importlib.util.spec_from_file_location('five_source',path);core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
 labels,_=core.load_sources();candidate=json.loads((path.parent/'CANDIDATE.json').read_text())['candidate'];blocks=candidate['blocks']
 hashes={}
 with tarfile.open(ARCHIVE)as t:
  data={}
  for name in ['CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz']:
   raw=gzip.decompress(t.extractfile(BASE+name).read());hashes[BASE+name]=hashlib.sha256(raw).hexdigest();data[name]=json.loads(raw)
 canonical=data['CANONICAL-WORD.json.gz'];events=data['LOCAL-PROGRAMS.json.gz']['forward'];deltas=[];consumers=[]
 for group in blocks:
  delta=0
  for port in group:delta^=labels[port]
  deltas.append(delta)
  # Bind a real native scalar ADD to a target in this block. The proposed five-plane
  # producer is hypothetical; this tests the exact ZERO-frame consumer interface.
  target=112+group[0]
  index,event=next((i,e)for i,e in enumerate(events)if e[0]=='scalar'and e[1][0]=='add'and e[1][1]==['L',target]and e[1][2][0]=='C')
  need(event[2]==0,'consumer ZERO frame');need(event[1][3]!=0,'nonzero consumer')
  consumers.append({'port':group[0],'event_index':index,'event':event})
 need(len(blocks)==23 and len({r['port']for r in consumers})==23,'distinct native target streams')
 total=0
 for delta in deltas:total^=delta
 need(total==0,'global cancellation premise')
 cumulative=0;pending=[]
 for delta in deltas:cumulative^=delta;pending.append(cumulative)
 # Source scratch h is optimistically identical through all lifts; each native
 # consumer writes an independent target. Even this extra sharing is insufficient.
 cases=0
 for address in range(512):
  h={address:Q(1)};initial=h.copy();outputs=[]
  for delta,row in zip(deltas,consumers):
   h=translate(h,delta);e=row['event'];c=Q(e[1][3],e[1][4]);dirty={address^511:Q(7)}
   actual=add(dirty,h,c);expected=add(dirty,initial,c);outputs.append(actual==expected)
  need(h==initial,'optimistic shared scratch endpoint')
  need(not outputs[0],'first actual consumer must expose pending translation')
  cases+=1
 # Correct positive control: translate each target with its source and undo it
 # after the ADD. X_delta^-1 ADD X_delta on both roles equals the original ADD,
 # including arbitrary target dirt. Those target corrections are not free.
 c=Q(consumers[0]['event'][1][3],consumers[0]['event'][1][4]);delta=deltas[0]
 for address in range(512):
  h={address:Q(3)};d={address^1:Q(5)}
  got=translate(add(translate(d,delta),translate(h,delta),c),delta)
  need(got==add(d,h,c),'joint source/target translation control')
  # Reusing a pointer after CLEAR/COPY does not compose translations on the same value.
  fresh={address^2:Q(1)};need(translate(translate(fresh,deltas[1]),deltas[0])!=fresh,'reload counterexample')
 # Bind actual wrapper endpoint/next centre: scratch cleanup and a separately copied input.
 source=consumers[0]['event'][1][2];consumer_i=consumers[0]['event_index']
 clear_i,clear=next((i,e)for i,e in enumerate(events[consumer_i+1:],consumer_i+1)if e[0]=='scalar'and e[1]==['clear',source])
 next_copy_i,next_copy=next((i,e)for i,e in enumerate(events[clear_i+1:],clear_i+1)if e[0]=='scalar'and e[1][0]=='copy'and e[1][1][0]=='C')
 need(next_copy[1][1]!=source,'selected next wrapper uses distinct scratch role')
 out={'status':'SCOPED_NEGATIVE_UNCHANGED_ZERO_FRAME_CONSUMERS','producer_status':'Five-plane native producer/owner route absent; this is a conditional consumer-boundary obstruction, not a replay of a nonexistent lift.','blocks':23,'deltas':deltas,'pending_prefix_translations':pending,'native_consumer_witnesses':consumers,'selected_wrapper_clear':[clear_i,clear],'selected_next_wrapper_copy':[next_copy_i,next_copy],'consumed_member_sha256':hashes,'basis_addresses':cases,'shared_scratch_final_translation':0,'first_consumer_mismatches':512,'positive_controls':['joint source-target translation with target restoration','shared scratch final endpoint restores'],'cost_ledger':{'local_copy_charge':118,'provisional_cleanup_units':23,'optimistic_extra_work_allowance':157,'with_local_cleanups_allowance':134,'native_shared_producer':'UNKNOWN','target_translation_routing_restoration':'UNKNOWN','hosting_precision_outer':'UNKNOWN','both_supplier_caps':'No changed complete supplier; no new kappa'},'remaining_domain':'Changed consumers/target frames or retained output compensation and complete physical owner schedule.'}
 if a.write:a.write.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(out==json.loads((P/'CONSUMER-RESULT.json').read_text()),'receipt differs')
 print('PASS_SHARED_ADDRESS_CONSUMER_SCREEN blocks=23 final_scratch_shift=0 first_output_defects=512 actual_consumer_direction=target_from_scratch changed_consumer_route=OPEN')
if __name__=='__main__':main()
