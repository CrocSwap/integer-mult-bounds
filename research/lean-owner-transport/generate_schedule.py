#!/usr/bin/env python3
"""Emit the controller trace and its finite window certificate from pinned source."""
from pathlib import Path
import argparse,gzip,hashlib,json
from generate_separation import generate as check_hosting_projection
ROOT=Path(__file__).resolve().parent

def access(name,ty,items):
    size=32;chunks=[items[i:i+size]for i in range(0,len(items),size)];out=''
    for n,chunk in enumerate(chunks):out+=f'def {name}Part{n} : Array ({ty}) := #[\n  '+',\n  '.join(chunk)+']\n\n'
    def choose(lo,hi):
        if hi-lo==1:return f'{name}Part{lo}'
        mid=(lo+hi)//2
        return f'(if block < {mid} then {choose(lo,mid)} else {choose(mid,hi)})'
    arg='block' if len(chunks)>1 else '_block'
    out+=f'def {name}Block ({arg} : Nat) : Array ({ty}) := {choose(0,len(chunks))}\n\n'
    return out+f'def {name} (i : Nat) : {ty} := (({name}Block (i / {size}))[i % {size}]?).getD default\n\n'

def generate():
    check_hosting_projection()
    p=json.loads(gzip.decompress((ROOT/'source531-hosting/GLOBAL-TEMPLATE.json.gz').read_bytes()))
    plan=json.loads((ROOT/'source531/PLAN.json').read_text())
    stagepair={e['stage']:e['pair']for e in p['recipe']if e['kind']=='local'}
    last={};bounds={};positions={};events=[]
    for pos,e in enumerate(p['execution_schedule'],1):
        kind=e['kind'];rep=e.get('replica');touch=[];idle=[];call='none';unknown=False
        if kind=='local_cover_sweep':
            touch=[stagepair[e['stage']]];call=f"some ({e['stage']}, {e['time']})"
            if e['time']in positions:raise ValueError('Repeated call')
            positions[e['time']]=pos;last[rep,touch[0]]=pos
        elif kind=='bridge':
            touch=[e['src'],e['dst']]
            for pair in touch:last[rep,pair]=pos
        elif kind=='idle_cover_sweep':
            touch=[e['pair']];idle=e['child_indices']
            for child in idle:
                if (rep,child)in bounds:raise ValueError('Repeated child deadline')
                bounds[rep,child]=(last.get((rep,e['pair']),0),pos)
        else:unknown=True
        replica='none' if rep is None else f'some {rep}'
        events.append(f'⟨{replica}, {touch}, {idle}, {call}, {str(unknown).lower()}⟩')
    calls=len(plan['order']);children=len(plan['pairs']);replicas=len(plan['windows'])//children;windows=replicas*children
    if set(positions)!=set(range(calls)):raise ValueError('Incomplete call positions')
    bounds_items=[str(bounds[r,child])for r in range(replicas)for child in range(children)]
    out='''/- Generated projection of the pinned PR531 hosted controller.
Original construction: icekylinx and credited predecessors; Apache-2.0.
Projection/proofs: Rohan Arun with OpenAI Codex assistance. -/
import PR531DataWindows
import BorrowSchedule
namespace OwnerTransport.PR531Controller
open OwnerTable OwnerSeparation PR531Table PR531DataWindows
set_option maxRecDepth 100000
set_option maxHeartbeats 0

'''
    out+=access('events','BorrowSchedule.Event',events)
    out+=access('positions','Nat',[str(positions[t])for t in range(calls)])
    out+=access('bounds','Nat × Nat',bounds_items)
    out+=f'''def trace : BorrowSchedule.Trace where
  count := {len(events)}
  event := fun p => events (p - 1)
  callPosition := positions
  bounds := bounds

theorem call_certificate :
    checkRange (BorrowSchedule.checkCall witness trace stagePair) 0 {calls} = true := by decide

'''
    for label,check in [('window','BorrowSchedule.checkWindow witness trace'),('separation','BorrowSchedule.checkSeparations witness trace')]:
        for r in range(replicas):
            out+=f'theorem {label}_chunk_{r} : checkRange ({check}) {r*children} {children} = true := by decide\n'
        out+=f'\ntheorem {label}_chunks (r : Nat) (h : r < {replicas}) :\n    checkRange ({check}) (r * {children}) {children} = true := by\n  match r with\n'
        for r in range(replicas):out+=f'  | {r} => exact {label}_chunk_{r}\n'
        out+=f'  | n + {replicas} => omega\n\n'
    out+=f'''/-- Calls, exact borrowing windows, and same-lane window separation are certified. -/
theorem accepted : BorrowSchedule.Accepted witness trace stagePair := by
  refine ⟨?_, ?_, ?_⟩
  · intro t ht
    exact range_sound _ 0 {calls} t call_certificate (by omega) ht
  · intro g hg
    exact chunks_sound (BorrowSchedule.checkWindow witness trace) {children} {replicas}
      (by decide) window_chunks g hg
  · intro g hg
    exact chunks_sound (BorrowSchedule.checkSeparations witness trace) {children} {replicas}
      (by decide) separation_chunks g hg

/-- The controller establishes the declared exclusion from active data. -/
theorem controller_windows_avoid_data : WindowsAvoidData witness stagePair :=
  BorrowSchedule.windows_avoid_data witness trace stagePair accepted

/-- Each selected window has its traced deadline, untouched interior and exact call set. -/
theorem every_window_realized (g : Nat) (hg : g < BorrowSchedule.windowCount witness) :
    BorrowSchedule.WindowFacts witness trace g :=
  BorrowSchedule.accepted_window witness trace stagePair accepted g hg

/-- Two pending children of the same physical lane have separated windows. -/
theorem same_lane_windows_separated (g h : Nat)
    (hg : g < BorrowSchedule.windowCount witness) (hh : h < BorrowSchedule.windowCount witness) :
    BorrowSchedule.Separate witness trace g h :=
  BorrowSchedule.accepted_separation witness trace stagePair accepted g h hg hh

end OwnerTransport.PR531Controller
'''
    return out,{'events':len(events),'calls':calls,'selected_windows':windows,'all_child_deadlines':len(bounds),'unmodeled_event_policy':'conservatively blocks affected replica or all replicas'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    s,counts=generate();target=ROOT/'PR531Controller.lean'
    if a.check:
        if target.read_text()!=s:raise ValueError('Controller source differs from projection')
    else:target.write_text(s)
    print(json.dumps({'status':'PASS_CONTROLLER_PROJECTION',**counts}))
if __name__=='__main__':main()
