from pathlib import Path
from collections import Counter,defaultdict
import sys,json,gzip,hashlib,copy,math
sys.dont_write_bytecode=True
OUT=Path(sys.argv[1]);CP=Path(sys.argv[2]);PHASE=Path(sys.argv[3]);LOCAL=Path(sys.argv[4]);PRIOR=Path(sys.argv[5])
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();raw=gzip.decompress((OUT/'TEMPLATE.json.gz').read_bytes());ir=json.loads(raw);rr=gzip.decompress((OUT/'ROUTES.json.gz').read_bytes());routes=json.loads(rr);receipt=read(OUT/'ADMISSION.json');phase=read(PHASE);local=json.loads(gzip.decompress(LOCAL.read_bytes()));prior=json.loads(gzip.decompress(PRIOR.read_bytes()));c=read(CP);ext=dict(c['ext']);n=2*c['v']+c['R'];m=73;bank=ir['banks_per_stage'];phaseby={p['frame']:p for p in phase['frames']}
assert hashlib.sha256(raw).hexdigest()==receipt['template_sha256'];assert hashlib.sha256(rr).hexdigest()==receipt['route_table_sha256']==ir['route_table_sha256'];assert sha(CP)==receipt['candidate_sha256']==phase['candidate_sha256'];assert phase['fresh_frames']==len(set(ext.values())) and phase['fresh_address_columns']==512*phase['fresh_frames'];assert all(sha(p)==h for p,h in receipt['source_hashes'].items())
# Independent integer-permutation decoder, not the emitter's matrix arithmetic.
def permutation(rows):
 assert len(rows)==m and all(x>0 and not(x&(x-1)) for x in rows)
 ids=[x.bit_length()-1 for x in rows];assert set(ids)==set(range(m));return ids
def audit(t,rs):
 lookup={};used=defaultdict(set);nonsymmetric=0
 for a in rs:
  key=a['replica'],a['helper'];assert key not in lookup;lookup[key]=a;f=permutation(a['map_local_to_bank_rows']);z=permutation(a['owner_right_factor_rows']);assert all(z[f[i]]==i and f[z[i]]==i for i in range(m))
  columns=[f.index(i) for i in range(m)];expectedrank=9-len(c['frames'][ext[a['helper']]]) if a['helper'] in ext else 9;assert a['rank']==expectedrank and a['residual_axes']==columns[:expectedrank]
  assert not used[a['bank']]&set(a['residual_axes']);used[a['bank']].update(a['residual_axes']);nonsymmetric+=f!=z
 assert len(lookup)==8*c['R'] and len(used)==bank
 for b in range(bank):
  original=used[b];missing=set(range(m))-original
  for s in range(9):
   ps=[p for p in t['bank_padding'] if p['family']==7680+s*bank+b];assert len(ps)==bool(missing)
   if ps:assert set(ps[0]['axes'])==missing and ps[0]['rank']==len(missing)
 assert t['live']==7680+9*bank and t['physical']==t['live']+c['R']+10
 assert t['private_namespace']==dict(centers=[t['live'],t['live']+9],tableau=[t['live']+9,t['live']+9+c['R']],coefficient=[t['physical']-1,t['physical']])
 H=Counter();programsha={}
 for ori,program in t['local_programs'].items():
  assert program[0]==['phase','bank_pre_adapters'] and program[-1]==['phase','done'];first=next(i for i,e in enumerate(program) if e==['phase','old_response']);last=next(i for i,e in enumerate(program) if e==['phase','bank_post_adapters']);assert first==len(ext)+1
  pre=program[1:first];post=program[last+1:-1];assert [e[2] for e in pre]==sorted(ext)==[e[2] for e in post]
  for e in pre+post:
   _,which,r,f,rec=e;assert ext[r]==f and rec['rank']==0;expected=phaseby[f]['pre_adapter' if which=='right_inverse_before_old_response' else 'post_adapter'];assert rec==expected
  assert all(e[1]=='right_inverse_before_old_response' for e in pre) and all(e[1]=='left_inverse_after_cleanup' for e in post)
  assert program[first:last]==local['local_programs'][ori][:-1]
  for r,f in ext.items():assert t['entry_charts'][str(f)]['physical_initial_chart']==f'T_{f}' and t['entry_charts'][str(f)]['formal_normalized_input_token']==f'T_{f}_inverse' and t['entry_charts'][str(f)]['entry_adapter_rank']==0
  hh=Counter(e[5] for e in program if e[0]=='climb');hh.update(e[4] for e in program if e[0]=='center');assert hh=={int(r):num for r,num in receipt['local_profile'].items()}
  programsha[ori]=hashlib.sha256(json.dumps(program,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for call,oldcall in zip(t['calls'],prior['calls']):
  assert all(call[k]==oldcall[k] for k in ['stage','replica','pair','orientation','window']);assert call['owners'][:240]==oldcall['owners'][:240];s,r=call['stage'],call['replica'];assert call['local_program_sha256']==programsha[call['orientation']]
  for helper in range(240,n):assert call['owners'][helper]==[7680+s*bank+lookup[r,helper]['bank'],['explicit_inverse_route',r,helper]]
  assert len({json.dumps(o) for o in call['owners']})==n;assert len({(lookup[r,helper]['bank'],tuple(lookup[r,helper]['owner_right_factor_rows'])) for helper in range(240,n)})==c['R']
  program=t['local_programs'][call['orientation']];H.update(e[5] for e in program if e[0]=='climb');H.update(e[4] for e in program if e[0]=='center')
 assert len(t['calls'])==72 and t['recipe']==prior['recipe'] and t['idle_children']==prior['idle_children']
 for ch in t['idle_children']:H[ch['rank']]+=ch['replicas']
 for p in t['bank_padding']:H[p['rank']]+=1
 assert H=={int(r):num for r,num in receipt['profile'].items()};mass=sum(r*num for r,num in H.items());assert mass==receipt['rank_mass'] and 73*t['live']-mass==2496
 assert t['cover']==prior['cover'] and t['loop_order']==prior['loop_order'];assert t['route_semantics']['data']==prior['route_semantics']['data'] and t['route_semantics']['work']==prior['route_semantics']['work'];assert t['exact_data_phase_recipe_sha256']==prior['exact_data_phase_recipe_sha256']
 originalschedule=[e for e in prior['execution_schedule'] if e['kind'] not in ('bank_padding_cover_sweep','translate_every_live_family')];assert t['execution_schedule'][:-2]==originalschedule
 assert t['execution_schedule'][-2]==dict(kind='heterogeneous_bank_padding_cover_sweep',padding=t['bank_padding']);assert t['execution_schedule'][-1]==t['cover_final_correction'] and t['cover_final_correction']['families']==[0,t['live']] and t['cover_final_correction']['formula']==prior['cover_final_correction']['formula']
 return nonsymmetric
nonsymmetric=audit(ir,routes);controls=[]
mutants=[('omit_pre',lambda t,r:t['local_programs']['forward'].pop(1)),('omit_post',lambda t,r:t['local_programs']['backward'].pop(-2)),('wrong_inverse',lambda t,r:next(a for a in r if a['map_local_to_bank_rows']!=a['owner_right_factor_rows']).__setitem__('owner_right_factor_rows',next(a for a in r if a['map_local_to_bank_rows']!=a['owner_right_factor_rows'])['map_local_to_bank_rows'])),('duplicate_padding',lambda t,r:t['bank_padding'].append(copy.deepcopy(t['bank_padding'][0]))),('underpriced_padding',lambda t,r:t['bank_padding'][0].__setitem__('rank',0)),('omit_final_cover_family',lambda t,r:t['cover_final_correction']['families'].__setitem__(1,t['live']-1)),('wrong_chart_I',lambda t,r:t['entry_charts'][str(next(iter(ext.values())))].__setitem__('physical_initial_chart','I')),('aliased_owner',lambda t,r:t['calls'][0]['owners'].__setitem__(241,t['calls'][0]['owners'][240]))]
for name,mut in mutants:
 t,r=copy.deepcopy(ir),copy.deepcopy(routes);mut(t,r)
 try:audit(t,r)
 except (AssertionError,KeyError,StopIteration):controls.append(name)
 else:raise AssertionError('accepted mutant '+name)
# Independently recompute source-counted invoice from decoded programs and bills.
bills=local['bills'];prim=sum(bills[c['orientation']]['totals']['real_component_primitive_steps'] for c in ir['calls']);lc=sum(int(v) for v in receipt['local_profile'].values());macros=max(bills[o]['totals']['scalar_macros'] for o in bills);comp=64*74**3;adapters=16*(macros+lc+n+9)+64*73+8*len(ext);bridges=sum(e['kind']=='bridge' for e in ir['recipe']);ba=2*120*8*bridges;ts=4*120*8;tm=7680
items=6*120*8*9+2*9*8*c['R']+len(ir['idle_children'])*8+len(ir['bank_padding'])+ba+ts+tm+ir['live']+ir['physical']+4*72*len(ext);outside=8*items+64*73;pv=prim+ba+ts+tm+ir['live']+(72*adapters+outside)*comp+64*ir['physical'];inv=receipt['invoice'];assert inv['real_primitives_all_calls']==prim and inv['adapter_groups']==adapters and inv['outside_groups']==outside and inv['pervertex']==pv and inv['explicit_bank_boundary_adapters']==2*72*len(ext)
result=dict(status='PASS_INDEPENDENT_DECODED_TWO_SIDED_BANKS_SCHEDULE_PROFILE_AND_INVOICE',candidate_sha256=sha(CP),template_sha256=receipt['template_sha256'],route_table_sha256=receipt['route_table_sha256'],banks_per_stage=bank,stage_bank_products=9*bank,owner_routes=8*c['R'],nonsymmetric_routes=nonsymmetric,all_size_claim=False,structural_controls_rejected=controls,source_hashes={str(p):sha(p) for p in [CP,PHASE,LOCAL,PRIOR,OUT/'ADMISSION.json',Path(__file__)]},scope='Independent integer-permutation readback plus complete scalar/local source equality, literal bank pre/post locations, current paid child profile, private namespace, retained interleaved schedule and counted finite invoice. Exact monomial identities and arbitrary-dirty block diagonal endpoints are separately source-bound. Conditional all-size interfaces remain inherited.')
(OUT/'INDEPENDENT-ADMISSION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
