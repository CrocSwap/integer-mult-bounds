"""Source490 and85 target quotient groups: full F2 and both integer signs.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
All1760 sources, all16624 dirty registers, and all targets checked.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util,json,sys,time,gc,hashlib
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent/'extra'
sp=importlib.util.spec_from_file_location('source490setup',P/'setup.py');setup=importlib.util.module_from_spec(sp);sp.loader.exec_module(setup)
m=setup.m;extra=setup.extra;groups=json.loads((D/'selection.json').read_text())['groups']
agg=[];role_groups=defaultdict(list);target_group={};allowed_roles={r['role']for r in m.new_gauge_selection+extra};terminaltargets={t for e in m.terminal for t in e['targets']}
for k,row in enumerate(groups):
 ts=row['targets'];pivot=row['pivot'];roles=row['roles'];F=m.W.register(row['frame_basis']);assert len(ts)>=2 and pivot in ts and not(set(ts)&terminaltargets);assert m.C.nondeg(F)
 for t in ts:assert t not in target_group;target_group[t]=k
 for s in roles:
  assert s in m.W.gauge and set(ts)<=set(m.adj[s]);assert len({m.adj[s][t]for t in ts})==1
  assert m.C.sub(m.W.gauge[s]['frame'],F);role_groups[s].append(k)
 agg.append(dict(targets=ts,pivot=pivot,roles=roles,frame=F))
for s,ks in role_groups.items():assert {t for k in ks for t in agg[k]['targets']}<=set(m.adj[s])
assert len(agg)==85 and len(target_group)==316;m.agg=agg;m.role_groups=role_groups;m.target_group=target_group
generated=D/'word.py';exec(compile(generated.read_text(),str(generated),'exec'),m.__dict__)
start=time.monotonic();out=dict(status='PASS_SOURCE490_AND85_GENERAL_TARGET_GROUPS_SCALAR',scope='Actual490 source-backed physical roles, original frozen39 prefix groups plus46 new disjoint quartets, complete target/reflected ledgers and all formal columns. Full source/auxiliary geometry/profile independently checked; no kappa claim.',source_selection=extra,groups=groups)
out['F2']=m.replay();print('PASS F2', {k:v for k,v in out['F2'].items()if k!='aggregation_restores'},flush=True)
bound=m.replay('bound');bits=8*((bound.bit_length()+2+7)//8);assert 1<<bits>2*bound;out['majorant']=dict(residual_bound=bound,packing_bits=bits);print('BOUND',bound,bits,flush=True);out['integer']=[]
for direction in(1,-1):out['integer'].append(m.replay('Z',direction,bits));gc.collect();print('PASS integer',direction,'seconds',time.monotonic()-start,flush=True)
out['controls']={}
for mutation in ['omit_aggregation_setup','omit_aggregation_inverse','repeat_aggregation_read','omit_extra_mix','omit_extra_compensation','omit_early_mix','old_adjoint','undo_before_restore','omit_gauge_mix','omit_gauge_compensation','late_phase1_gauge']:
 try:m.replay(mutation=mutation)
 except AssertionError as e:out['controls'][mutation]=dict(status='REJECTED',error=str(e))
 else:raise AssertionError('Negative mutation accepted: '+mutation)
assert all(m.input_pins[str(p)]==hashlib.sha256(p.read_bytes()).hexdigest()for p in m.input_paths)
out['input_pins']=dict(m.input_pins);out['input_pins'].update({str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in[Path(__file__),P/'setup.py',P/'selection.json',D/'selection.json',generated]});out['seconds']=time.monotonic()-start
(D/'replay.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS source490 scalar word, target reflections, all11 controls',flush=True)
