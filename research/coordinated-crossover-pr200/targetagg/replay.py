"""Complete493+82+7+4 scalar word: all20141 formal columns and both integer signs.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Integer execution checks the defining decoder; its F2 reduction is identity.
"""
from pathlib import Path
import importlib.util,json,hashlib,sys,time,gc
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent
sp=importlib.util.spec_from_file_location('complete493_setup',D/'setup.py');setup=importlib.util.module_from_spec(sp);sp.loader.exec_module(setup);m=setup.m
word=D/'word.py';exec(compile(word.read_text(),str(word),'exec'),m.__dict__)
start=time.monotonic();out=dict(status='PASS_SOURCE493_82_EQUAL7_RANK4_ECHELON_PR230',source_selection=setup.extra,groups=setup.groups,rank_groups=setup.rankselection['groups'],echelon_groups=setup.echelonselection['groups'])
out['F2']=m.replay();print('PASS F2 all20141columns/source/dirty restoration and both source/target ledgers',flush=True)
bound=m.replay('bound');bits=8*((bound.bit_length()+2+7)//8);assert 1<<bits>2*bound;out['majorant']=dict(residual_bound=bound,packing_bits=bits);print('BOUND',bound,bits,flush=True);out['integer']=[]
for direction in(1,-1):out['integer'].append(m.replay('Z',direction,bits));gc.collect();print('PASS defining integer',direction,'seconds',time.monotonic()-start,flush=True)
out['controls']={}
for mutation in['omit_echelon_setup','omit_echelon_inverse','flip_echelon_sign','omit_rank_setup','omit_rank_inverse','repeat_rank_read','omit_aggregation_setup','omit_aggregation_inverse','repeat_aggregation_read','omit_extra_mix','omit_extra_compensation','omit_early_mix','old_adjoint','undo_before_restore','omit_gauge_mix','omit_gauge_compensation','late_phase1_gauge']:
 try:m.replay('Z'if mutation=='flip_echelon_sign'else'F2',bits=bits,mutation=mutation)
 except AssertionError as e:out['controls'][mutation]=dict(status='REJECTED',error=str(e))
 else:raise AssertionError('Corruption accepted: '+mutation)
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in m.input_pins.items())
out['input_pins']=dict(m.input_pins);out['input_pins'].update({str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in(Path(__file__),word,D/'setup.py',D/'selection.json',P/'extra/setup.py',P/'extra/selection.json',P/'rank/selection.json',P/'echelon/selection.json')});out['seconds']=time.monotonic()-start
(D/'replay.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS complete493+82+7+4 actual scalar word and17controls',flush=True)
