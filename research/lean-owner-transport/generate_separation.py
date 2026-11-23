#!/usr/bin/env python3
"""Project the selected source data-bank definition; all window avoidance is proved in Lean."""
from pathlib import Path
import argparse, gzip, hashlib, json
ROOT = Path(__file__).resolve().parent

def generate():
    pin=json.loads((ROOT/'SOURCE531-HOSTING.json').read_text())
    raw=(ROOT/'source531-hosting/GLOBAL-TEMPLATE.json.gz').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=pin['sha256']:raise ValueError('Changed hosting source')
    template=json.loads(gzip.decompress(raw))
    table_pin=json.loads((ROOT/'SOURCE531.json').read_text())
    for name,digest in table_pin['sha256'].items():
        if hashlib.sha256((ROOT/'source531'/name).read_bytes()).hexdigest()!=digest:
            raise ValueError('Changed table source: '+name)
    plan=json.loads((ROOT/'source531/PLAN.json').read_text())
    rows=json.loads(gzip.decompress((ROOT/'source531/OWNERS.json.gz').read_bytes()))
    pairs={e['stage']:e['pair'] for e in template['recipe'] if e['kind']=='local'}
    if sorted(pairs)!=list(range(len(pairs))):raise ValueError('Stage census')
    calls=len(plan['order']); helpers=len(plan['baseline_widths']); ports=plan['copies']
    lanes=max(2*plan['pairs'][k]+plan['sides'][k] for k in plan['pairs'])+1
    children=len(plan['pairs']); replicas=len(plan['windows'])//children
    lookup={(r['time'],r['helper']):r for r in rows}
    if len(template['calls'])!=calls:raise ValueError('Call census')
    for t,c in enumerate(template['calls']):
        if [c['stage'],c['replica']]!=plan['order'][t] or c['time']!=t:raise ValueError('Call order')
        if c['pair']!=pairs[c['stage']]:raise ValueError('Active pair')
        expected=[(c['replica']*lanes+2*c['pair'])*ports+j for j in range(2*ports)]
        if [x[0]for x in c['owners'][:2*ports]]!=expected:raise ValueError('Data-bank projection')
        if len(c['owners'])!=2*ports+helpers:raise ValueError('Register census')
        for helper,(f,route) in enumerate(c['owners'][2*ports:]):
            row=lookup[t,helper]
            if f!=row['family'] or route[1:3]!=[row['child'],row['offset']]:raise ValueError('Helper projection')
            width=9 if route[0]==3 else route[3] if route[0]==4 else None
            if width!=row['width']:raise ValueError('Helper route width')
    literals=', '.join(str(pairs[i])for i in range(len(pairs)))
    out=f'''/- Generated from the pinned PR531 complete hosted template.
Original construction: icekylinx and credited predecessors; Apache-2.0.
Projection/proofs: Rohan Arun with OpenAI Codex assistance. -/
import PR531TableData
import OwnerSeparation
namespace OwnerTransport.PR531DataWindows
open OwnerTable OwnerSeparation PR531Table
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def stagePair (s : Nat) : Nat := (#[{literals}][s]?).getD 0

def checkWindow (g : Nat) : Bool :=
  (witness.window g).times.all (fun t =>
    decide ((witness.call t).2 ≠ g / {children} ∨
      witness.lane (g % {children}) / 2 ≠ stagePair (witness.call t).1))

theorem all_windows_checked : checkRange checkWindow 0 {replicas*children} = true := by decide

theorem windows_avoid_data : WindowsAvoidData witness stagePair := by
  intro r child hr hc t ht
  change r < {replicas} at hr
  change child < {children} at hc
  have hg : r * {children} + child < {replicas*children} := by omega
  have h := range_sound checkWindow 0 {replicas*children} (r * {children} + child)
    all_windows_checked (by omega) (by omega)
  have hh := List.all_eq_true.mp h t ht
  have hdiv : (r * {children} + child) / {children} = r := div_tail _ _ _ hc
  have hmod : (r * {children} + child) % {children} = child := by omega
  simpa only [decide_eq_true_eq, hdiv, hmod] using hh

theorem all_active_pairs_fit :
    checkRange (fun t => decide (2 * stagePair (witness.call t).1 + 2 ≤ witness.lanes)) 0 {calls} = true := by decide

theorem active_pair_fits (t : Nat) (ht : t < witness.calls) :
    2 * stagePair (witness.call t).1 + 2 ≤ witness.lanes := by
  have h := range_sound _ 0 {calls} t all_active_pairs_fit (by omega) ht
  exact of_decide_eq_true h

theorem all_call_replicas_fit :
    checkRange (fun t => decide ((witness.call t).2 < witness.replicas)) 0 {calls} = true := by decide

theorem call_replica_fits (t : Nat) (ht : t < witness.calls) :
    (witness.call t).2 < witness.replicas := by
  exact of_decide_eq_true (range_sound _ 0 {calls} t all_call_replicas_fit (by omega) ht)

end OwnerTransport.PR531DataWindows
'''
    return out,{'calls':calls,'data_wires_per_call':2*ports,'helpers_per_call':helpers,'declared_windows':replicas*children}

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    s,counts=generate();target=ROOT/'PR531DataWindows.lean'
    if a.check:
        if target.read_text()!=s:raise ValueError('Window source differs from projection')
    else:target.write_text(s)
    print(json.dumps({'status':'PASS_HOSTING_PROJECTION',**counts}))
if __name__=='__main__':main()
