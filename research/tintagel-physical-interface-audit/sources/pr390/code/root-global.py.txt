"""Bind the heterogeneous local program, exact endpoint phases and bank owner routes."""
from pathlib import Path
import os,json,gzip,hashlib,copy
P=Path(os.environ['COMPLEX_PUBLIC']);B=P/'381/source/research/e8-nine-stage-kappa/complex377/work/odd-stages';O=Path(os.environ['COMPLEX_OUTPUT']);K=Path(os.environ['HETEROBANKS']);PH=Path(os.environ['BANK_PHASE']);REVIEW=Path(os.environ['BANK_REVIEW']);raw=(O/'HETEROGENEOUS-TEMPLATE.json.gz').read_bytes();local=json.loads(gzip.decompress(raw));bill=json.loads((O/'RESULT.json').read_text());banks=json.loads(K.read_text());ph=json.loads(PH.read_text());rv=json.loads(REVIEW.read_text());recipe=json.loads((B/'RECIPE-9.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert banks['live']==bill['live']==58899 and banks['banks_per_stage']==3131 and banks['replicas']==32
assert ph['status']=='PASS_EXACT_RANK_EIGHT_BANK_ENDPOINT_PHASE_ADAPTERS' and len(ph['endpoints'])==2
assert rv['status']=='PASS_PROPOSED_BANK_SUBSPACES_INVERSES_AND_ALL_SINK_MAIN_FRAMES'
assert rv['source_hashes'][str(K.resolve())]==sha(K)
byframe={e['frame']:e['canonical_to_orthogonal_coordinate_adapter'] for e in ph['endpoints']}
# Relative adapter R = (A^-1 C_block A) T_E^-1 follows the canonical E frame.
# It is emitted in full, including affine permutation, translation and Z4 phase.
for ori,prog in local['local_programs'].items():
 count=0
 for i,e in enumerate(prog):
  if e[:2]==['adapter','canonical_to_bank_residual']:
   _,_,r,f=e;assert (r,f) in [(355,206),(403,221)]
   prog[i]=['rankzero_endpoint_adapter',r,f,copy.deepcopy(byframe[f])];count+=1
 assert count==2
assign={(a['replica'],a['helper']):a for a in banks['assignments']};routes=[[int(x,2)for x in A]for A in banks['route_recipes']]
def transpose(A):return [sum(((row>>i)&1)<<j for j,row in enumerate(A))for i in range(73)]
inverses=[transpose(A)for A in routes]
calls=[]
for e in recipe:
 if e['kind']!='local':continue
 s,p=e['stage'],e['pair'];ori='backward' if e['reverse'] else 'forward'
 for rep in range(32):
  owners=[]
  for r in range(240):owners.append([rep*960+(2*p+r//120)*120+r%120,['data',s,r%120]])
  for h in range(240,1023):
   a=assign[rep,h];owners.append([30720+s*3131+a['bank'],['helper',a['orthogonal_route_id']]])
  assert len({(fam,tuple(route))for fam,route in owners})==1023 and all(0<=fam<58899 for fam,route in owners)
  calls.append(dict(stage=s,replica=rep,pair=p,orientation=ori,owners=owners))
assert len(calls)==288
assert len([e for e in recipe if e['kind']=='bridge'])==9
source_hashes={str(p):sha(p)for p in [K,PH,REVIEW,O/'HETEROGENEOUS-TEMPLATE.json.gz',O/'RESULT.json',B/'RECIPE-9.json',B/'data_phases.py']}
template=dict(recipe=recipe,local=local,calls=calls,bank_placement_matrices=routes,bank_owner_right_factors=inverses,bank_owner_formula='g=d*A^-1; A maps the local residual subspace onto its disjoint bank block; explicit A^-1=A^T, without an A=A^-1 assumption.',banks=banks['assignments'],bank_padding=[dict(stage=s,bank=b,axis=72,rank=1)for s in range(9)for b in range(8,3131)],data_phase_source=sha(B/'data_phases.py'),terminal_data_rule='Exact unchanged nine-stage DATA-PHASES X_q correction and signed exchange, then bank padding, then X_delta(g) on every live family.',cover_final_correction=dict(families=[0,58899],formula='delta_i=(weight(row_i(g))-1)/2 mod 2',charged_calls=58899),private=dict(start=58899,physical=59692,centres=9,tableau=783,coefficient=1),source_hashes=source_hashes)
assert len(template['bank_padding'])==28107
# Negative controls on genuinely required full affine/phase and inverse fields.
def validate(t):
 assert t['bank_owner_right_factors']==[transpose(A)for A in t['bank_placement_matrices']]
 assert len(t['bank_padding'])==28107 and t['cover_final_correction']['charged_calls']==58899
 for ori in ['forward','backward']:
  got=[e for e in t['local']['local_programs'][ori]if e[0]=='rankzero_endpoint_adapter']
  assert {e[2]for e in got}=={206,221}
  for e in got:assert e[3]==byframe[e[2]]
validate(template);controls=[]
for name in ['omit_endpoint_adapter','wrong_owner_inverse','omit_bank_padding','omit_cover_phase']:
 t=copy.deepcopy(template)
 if name=='omit_endpoint_adapter':t['local']['local_programs']['forward']=[e for e in t['local']['local_programs']['forward']if not(e[0]=='rankzero_endpoint_adapter'and e[1]==355)]
 elif name=='wrong_owner_inverse':i=next(i for i,A in enumerate(routes)if A!=inverses[i]);t['bank_owner_right_factors'][i]=routes[i]
 elif name=='omit_bank_padding':t['bank_padding'].pop()
 else:t['cover_final_correction']['charged_calls']-=1
 try:validate(t)
 except AssertionError:controls.append(name)
 else:raise AssertionError('control accepted '+name)
blob=json.dumps(template,sort_keys=True,separators=(',',':')).encode();(O/'GLOBAL-HETEROGENEOUS-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))
result=dict(status='PASS_EMITTED_HETEROGENEOUS_OWNERS_FULL_ENDPOINT_PHASES_AND_TEMPLATE_BINDING',template_sha256=hashlib.sha256(blob).hexdigest(),local_invocations=288,independent_owner_checks=288,bank_count_per_stage=3131,padding_calls=28107,endpoint_adapters=576,physical=59692,live=58899,controls_rejected=controls,source_hashes=source_hashes,scope='Finite template composition under the explicitly inherited compressed-window, arbitrary-dirty bank, Clifford/compiler, row and analytic interfaces. No astronomical cover enumeration or new Lean theorem.')
(O/'GLOBAL-HETEROGENEOUS-RECEIPT.json').write_text(json.dumps(result,indent=2));print(result['status'],flush=True)

