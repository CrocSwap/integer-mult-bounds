"""Bounded PR122-style terminal inventory on our shrunk+birth composition.

PR122 terminal identity: SovereignSteak; PR125 frames: Joel Pulikkan;
PR124 birth reuse: James Chang; PR117 DAG: eumemic. This compatibility
inventory and conservative disjoint selection are new composition work.
"""
from pathlib import Path
from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
import argparse, gzip, json, pickle

W=Path(__file__).resolve().parent
B=W/'baseline'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--frames',type=Path,required=True)
p.add_argument('--matches',type=Path,required=True)
p.add_argument('--readouts',type=Path,required=True)
p.add_argument('--out',type=Path,default=W/'inventory.json')
p.add_argument('--include-birth-recipients',action='store_true',help='Expose virtual terminal options for joint optimization; these options are not a simultaneous legal elimination selection.')
p.add_argument('--terminal-roles',type=Path,help='JSON list of exact terminal role IDs to eliminate; requires ordinary disjoint eligibility.')
a=p.parse_args()
assert not (a.include_birth_recipients and a.terminal_roles), 'Joint options and a validated physical selection are distinct modes'
g=pickle.loads(a.frames.read_bytes())
readouts=pickle.loads(a.readouts.read_bytes())
choice=json.loads(gzip.decompress(a.matches.read_bytes()))
assert choice['source_frame_checkpoint_sha256']==sha256(a.frames.read_bytes()).hexdigest()
R=len(g['first']);v=g['v'];h=g['h'];m=h*h
merge={r['recipient']:r['donor'] for r in choice['pairs']}

@lru_cache(None)
def contains(A,B):
    for x in A:
        for r in B:
            if x>>(r.bit_length()-1)&1:x^=r
        if x:return False
    return True

incoming=defaultdict(list);outgoing=Counter()
for i,(op,s,t,x) in enumerate(g['ops']):
    if op==1:dst,src=s,t
    elif op==2:dst,src=t,s
    else:continue
    incoming[dst].append((i,src,x));outgoing[src]+=1

target_front=[() for _ in range(v)]
for s,F in sorted(g['placed'].items(),key=lambda z:(len(z[1]),z[0])):
    targets=g['reach'][s]
    while targets:
        b=targets&-targets;targets-=b;t=b.bit_length()-1
        assert contains(target_front[t],F)
        target_front[t]=F

def scaled(mask,n):return tuple(mask if n>>i&1 else 0 for i in range(n.bit_length()))

blocked=Counter();eligible=[]
for s,j in sorted(g['terminal'].items()):
    if j>=len(g['roots'])-h:blocked['center_root']+=1;continue
    if outgoing[s]:blocked['controls_auxiliary']+=1;continue
    if s in merge and not a.include_birth_recipients:blocked['physical_slot_shared_as_birth_recipient']+=1;continue
    assert s not in set(merge.values())
    if s not in g['placed']:blocked['not_deferred']+=1;continue
    if g['first'][s]<=v:blocked['source_injection_excluded_from_this_bounded_pass']+=1;continue
    if not incoming[s]:blocked['no_incoming_update']+=1;continue
    if any(i in g['phase'] for i,_,_ in incoming[s]):blocked['early_update']+=1;continue
    assert s not in g['touched']
    t=g['targets'][j];sign=1 if j<v else -1
    expected=scaled(1<<t,21)
    assert readouts['positive'][s]==(expected if sign>0 else ())
    assert readouts['negative'][s]==(expected if sign<0 else ())
    F0=g['U'][incoming[s][0][2]];M=target_front[t];sigma=g['placed'][s]
    if not contains(M,F0):blocked['target_front_past_first_update']+=1;continue
    fs=[M]+[g['U'][x] for _,_,x in incoming[s]]
    assert all(contains(a,b) for a,b in zip(fs,fs[1:])),s
    assert contains(sigma,M) and len(fs[-1])<=h-1
    if a.include_birth_recipients and not len(sigma)==len(M)==len(F0):blocked['unequal_packet_dimensions_excluded_from_joint_options']+=1;continue
    eligible.append({'role':s,'target':t,'root_index':j,'coefficient_numerator':21*sign,'sigma':len(sigma),'M':len(M),'F0':len(F0),'incoming_operations':[i for i,_,_ in incoming[s]],'incoming_count':len(incoming[s]),'frames':[list(F) for F in fs],'current_birth_donor':merge.get(s),'terminal_local_scalar_charge':29*len(incoming[s]),'packet_replication':2*v,'old_packet':[m-h+len(sigma),1,len(F0)-len(sigma),h-1-len(M)],'padded_new_packet':[m,len(F0)-len(M),0,0]})

# One terminal per target gives disjoint target-front packets; this avoids
# treating individually legal but interleaved output paths as simultaneous.
bytarget=defaultdict(list)
for row in eligible:bytarget[row['target']].append(row)
selected=[min(group,key=lambda x:x['role']) for _,group in sorted(bytarget.items())]
if a.terminal_roles:
    requested=json.loads(a.terminal_roles.read_text())
    assert isinstance(requested,list) and all(type(s) is int for s in requested), 'Selection must be a JSON list of integer role IDs'
    assert len(requested)==len(set(requested)), 'Duplicate terminal role ID'
    rows={row['role']:row for row in eligible}
    assert set(requested)<=rows.keys(), f'Ineligible requested terminal roles: {sorted(set(requested)-rows.keys())}'
    selected=[rows[s] for s in sorted(requested)]
    assert len({row['target'] for row in selected})==len(selected), 'Selected terminals must have distinct targets'
    assert not set(requested)&(set(merge)|set(merge.values())), 'Selected terminals must have no birth aliases'
record={'status':'PASS exact local eligibility and disjoint-target selection on new composition inputs','base_virtual_roles':R,'base_physical_roles':choice['R'],'birth_merges_preserved':len(merge),'eligible_unshared_terminal_roles':len(eligible),'selected_terminal_roles':len(selected),'selected_targets':len(bytarget),'blocked':dict(blocked),'selection_rule':'Lowest eligible role id per target; no frame, deferral or birth matching changes.','selected':selected,'eligible':eligible,'expected_physical_roles':choice['R']-len(selected),'input_sha256':{str(p):sha256(p.read_bytes()).hexdigest() for p in [a.frames,a.readouts,a.matches]}}
if a.terminal_roles:
    record.update(selection_rule='Exact requested role-ID subset, validated against ordinary unshared eligibility and distinct targets',selected_targets=len(selected),selection_sha256=sha256(a.terminal_roles.read_bytes()).hexdigest())
if a.include_birth_recipients:
    record.update(status='PASS virtual eligibility options for joint birth/terminal optimization; not a legal simultaneous elimination selection',joint_optimization_options=True,eligible_virtual_terminal_roles=len(eligible),currently_birth_matched_options=sum(row['current_birth_donor'] is not None for row in eligible),selection_rule='All eligible options retained in eligible; selected is only the lowest role per target and may conflict with existing births. Choose at most one option per target and never choose both a terminal edge and a birth donor edge for the same role. After changing the birth matching, rerun the default inventory and full builder.')
    record.pop('eligible_unshared_terminal_roles');record.pop('expected_physical_roles')
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ['selected','eligible','input_sha256']},indent=2))
