"""Actual scalar word for new-source-gauge target conjugation.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Retains source471 physical source/auxiliary word; no standalone kappa claim.
"""
from pathlib import Path
from collections import Counter
import importlib.util,json,sys,time,gc,hashlib
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent/'newg'
sp=importlib.util.spec_from_file_location('scalar471copy',P/'replay.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
selection_path=D/'selection.json';groups=json.loads(selection_path.read_text())['groups']
agg=[];role_group={};target_group={};newroles={r['role']for r in m.new_gauge_selection};terminaltargets={t for e in m.terminal for t in e['targets']}
for i,row in enumerate(groups):
 ts=row['targets'];pivot=row.get('pivot',min(ts));roles=row['roles'];F=m.W.register(row['frame_basis'])
 assert len(set(ts))==len(ts)and pivot in ts and not(set(ts)&terminaltargets)
 assert m.C.nondeg(F)
 for t in ts:assert t not in target_group;target_group[t]=i
 for s in roles:
  assert s in newroles and s not in role_group;role_group[s]=i
  assert set(m.adj[s])==set(ts)and len(set(m.adj[s].values()))==1
  assert m.C.sub(m.W.gauge[s]['frame'],F)
 agg.append(dict(targets=ts,pivot=pivot,roles=roles,frame=F))
assert agg
m.agg=agg;m.role_group=role_group;m.target_group=target_group
generated=D/'word.py';exec(compile(generated.read_text(),str(generated),'exec'),m.__dict__)
start=time.monotonic();out=dict(status='PASS_SOURCE471_TARGET_AGGREGATION_SCALAR_PROTOTYPE',scope='Actual F2 and defining-integer words with D0 target setup, only pivot early compensation reads, actual inverse before original read, complete target and reflected frame histograms, all-source/dirty restoration. Source/auxiliary frames remain unchanged by target-only conjugation. No entrance-bank or assembly/kappa admission.',groups=groups)
out['F2']=m.replay();print('PASS F2',out['F2'],flush=True)
bound=m.replay('bound');bits=8*((bound.bit_length()+2+7)//8);assert 1<<bits>2*bound;out['majorant']=dict(residual_bound=bound,packing_bits=bits);print('BOUND',bound,bits,flush=True)
out['integer']=[]
for direction in(1,-1):out['integer'].append(m.replay('Z',direction,bits));gc.collect();print('PASS integer',direction,'seconds',time.monotonic()-start,flush=True)
out['controls']={}
for mutation in ['omit_aggregation_setup','omit_aggregation_inverse','repeat_aggregation_read','omit_early_mix','old_adjoint','undo_before_restore','omit_gauge_mix','omit_gauge_compensation','late_phase1_gauge']:
 try:m.replay(mutation=mutation)
 except AssertionError as e:out['controls'][mutation]=dict(status='REJECTED',error=str(e))
 else:raise AssertionError('Negative mutation accepted: '+mutation)
assert all(m.input_pins[str(p)]==hashlib.sha256(p.read_bytes()).hexdigest()for p in m.input_paths)
out['input_pins']=dict(m.input_pins);out['input_pins'].update({str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),selection_path,generated]});out['seconds']=time.monotonic()-start
(D/'replay.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS exact target aggregation scalar, reflected target ledger and all nine controls',flush=True)
