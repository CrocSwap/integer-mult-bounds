"""Consume a freshly admitted E8 supplier with corrected odd-dimensional cover charges.
OpenAI Codex-assisted; Apache-2.0. Explicit gcert and regenerated Lean data are
bound separately; no certificate-producer regeneration or Lean kernel rebuild.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip,hashlib,importlib.util,json
MANIFEST='3d0d867b84b86dd9f0850cedce9a6de83f2313a604bdef58f7235af30f94bcbd'
CANDIDATE='3594f19c4d01cf11fb930c5c61baeed399620acbc5b94096b16bcacb23997dd3'
COARSE=Q(876248285600677,10**18)
HEAD='04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2'
E8_HEAD='9c94857bbaee886f8649edee0bc2d3c738f9555e'
STAGES=['complete-e8-scalar-splice-dirty-parity-guard','e8-lean-data-regeneration','e8-independent-replay','complete-e8-two-moment-pricing']
RECEIPTS=('candidate.json','admission/UPSTREAM-GUARD.json','admission/INDEPENDENT-AUDIT.json','LEAN-DATA.json','INDEPENDENT-REPLAY.json','SUPPLIER-CHECK.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def supplier(cost,other,package,proof):
 package=Path(package).resolve();proof=Path(proof).resolve();assert not proof.is_relative_to(package) and not(proof/'FAILURE.json').exists()
 assert sha(package/'MANIFEST.json')==MANIFEST
 files={}
 for p in package.rglob('*'):
  assert not p.is_symlink(),'Symlink in supplier package'
  if p.is_file() and p!=package/'MANIFEST.json':files[p.relative_to(package).as_posix()]=sha(p)
 assert files==read(package/'MANIFEST.json')['files'],'Changed, missing or unpinned supplier file'
 pins=read(package/'SOURCE.json');v=read(proof/'VERIFICATION.json');a=read(proof/'admission/INDEPENDENT-AUDIT.json');g=read(proof/'admission/UPSTREAM-GUARD.json');c=read(proof/'SUPPLIER-CHECK.json')
 assert v['status']=='PASS_PORTABLE_E8_CORRECTED_COMPLEX_SUPPLIER' and v['manifest_sha256']==MANIFEST and v['inputs_unchanged'] is True and v['kappa_claim'] is False
 for k,value in [('producer_regeneration_claim',False),('lean_data_regeneration_claim',True),('upstream_lean_rebuilt',False),('declarative_source',True),('parity_corrected_complete_invoice',True)]:assert v[k] is value and pins[k] is value
 assert v['public_head']==pins['public_head']==HEAD and v['e8_source_head']==pins['e8_source_head']==E8_HEAD
 assert [s['stage']for s in v['fresh_stages']]==STAGES
 for stage in v['fresh_stages']:assert stage['returncode']==0 and sha(proof/'logs'/(stage['stage']+'.log'))==stage['log_sha256']
 assert set(v['receipt_hashes'])==set(RECEIPTS)
 for name,digest in v['receipt_hashes'].items():assert sha(proof/name)==digest
 assert v['candidate_sha256']==pins['candidate_sha256']==CANDIDATE==sha(proof/'candidate.json')
 assert sha(package/pins['certificate_gzip_path'])==pins['certificate_gzip_sha256'] and gzip.decompress((package/pins['certificate_gzip_path']).read_bytes())==(proof/'candidate.json').read_bytes()
 assert Q(v['complex_coarse'])==Q(pins['complex_coarse'])==COARSE
 assert a['status']=='PASS_E8_INDEPENDENT_DIRTY_SCALARS_AND_CORRECTED_FINITE_GUARD' and a['certificate_sha256']==CANDIDATE and a['guard_receipt_sha256']==sha(proof/'admission/UPSTREAM-GUARD.json')
 assert set(a['scalar_words'])=={'forward','backward'}
 for ori in ['forward','backward']:
  x=a['scalar_words'][ori];assert x['status']=='PASS_FULL_ACTUAL_DIRTY_SCALAR_WORD' and x['independent_live_columns']==1023 and x['source_columns']==120 and x['target_columns']==120 and x['helper_columns']==783 and x['all_live_rows_correct'] is True and x['all_private_work_restored_zero'] is True
 assert g['status']=='PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION' and g['program_check']['certificate_sha256']==CANDIDATE
 assert g['program_check']['status']=='PASS_COMPLEX_PROGRAM_GX_CHECK1_SCALAR_AND_GXCORE_MIRROR' and len(g['program_check']['controls'])==2
 assert len(g['splice']['controls'])==20 and all(x['rejected']for x in g['splice']['controls']) and set(g['splice']['program'])=={'forward','backward'}
 assert [g['scalar_bill'][ori]['totals']['real_component_primitive_steps']for ori in ['forward','backward']]==[68158,72856]
 for splice in g['splice']['program'].values():assert splice['final_climbs_before_cleanup'] is True and splice['old_response_erased_before_all_children'] is True and splice['paid_children']==3974
 complex_root=package/'upstream/pr352/code/complex'
 for name,digest in g['input_pins'].items():assert sha(complex_root/name)==digest
 spec=importlib.util.spec_from_file_location('native_e8_corrected_guard',package/'finite_guard.py');correction=importlib.util.module_from_spec(spec);spec.loader.exec_module(correction)
 word=read(proof/'candidate.json');guard=correction.finite_guard(g,word);assert json.loads(json.dumps(guard))==a['finite_guard']
 assert guard['status']=='PASS_CORRECTED_ODD_DIMENSION_COMPLETE_FINITE_INVOICE' and guard['all_retained_guards_pass'] is True
 assert(guard['group_bits'],guard['live_stock_bits'],guard['physical_stock_bits'],guard['physical_row_overcharge_coefficient'],guard['retained_row_coefficient'],guard['induction_gap_multiple_of_B'])==(990,1000,1001,11162,20161,49)
 # JSON receipt keys stringify integer dimensions; compare normalized values explicitly.
 assert {int(k):n for k,n in guard['small_dimension_complete_orthogonal_basis_enumeration'].items()}=={1:1,2:2,3:6,4:48,5:720}
 assert len(guard['controls'])==6 and all(guard['controls'].values())
 lean=read(proof/'LEAN-DATA.json');assert lean['status']=='PASS_EXACT_E8_LEAN_DATA_REGENERATION' and lean['source_head']==E8_HEAD and lean['certificate_sha256']==CANDIDATE and lean['upstream_lean_rebuilt'] is False and lean['producer_regeneration_claim'] is False
 assert len(lean['matched_files'])==25 and len(lean['unmatched_generated_files'])==3
 e8=complex_root/'inputs/e8'
 for name,digest in lean['matched_files'].items():
  actual='cmp/'+name[len('comparator/'):]if name.startswith('comparator/')else name
  assert sha(e8/name)==digest==sha(proof/'lean-data'/actual)
 for name,digest in lean['unmatched_generated_files'].items():assert sha(proof/'lean-data'/name)==digest
 for name,digest in lean['generator_log_hashes'].items():assert sha(proof/'lean-data'/name)==digest
 replay=read(proof/'INDEPENDENT-REPLAY.json');assert replay['status']=='PASS_UPSTREAM_STANDALONE_E8_REPLAY' and replay['certificate_sha256']==CANDIDATE and replay['script_sha256']==sha(e8/'tools/e8/replay.py') and replay['stdout_sha256']==sha(proof/'logs/e8-independent-replay.log')
 assert replay['summary'].startswith('REPLAY ACCEPTED: R=783 W=1263 D=120 cst=72 N=9039 figure=8762479') and 'E8 family: True' in replay['summary']
 assert c['status']=='PASS_E8_FULL_PAID_PROFILE_TWO_EXACT_MOMENTS' and c['candidate_sha256']==CANDIDATE and c['kappa_claim'] is False and c['guard_sha256']==sha(proof/'admission/UPSTREAM-GUARD.json')
 for name,digest in c['engine_pins'].items():assert sha(package/'upstream/pr352/code/pricing'/name)==digest
 CH=Counter()
 for block in word['blocks'].values():CH.update({int(r):5*n for r,n in block.items()})
 h,vv,R=word['h'],word['v'],word['R'];m,W=5*h,4*vv+R
 for r in(2*h-2,h-1,2*h+2,4):CH[r]+=2*vv
 assert(m,W,h,vv,R)==(45,1263,9,120,783) and CH==Counter({int(r):n for r,n in g['ledger']['histogram'].items()})
 assert(sum(CH.values()),sum(r*n for r,n in CH.items()),g['ledger']['copy_calls'],g['ledger']['idle_calls'],g['ledger']['centres'])==(20830,56715,40,960,8)
 profile=dict(m=m,W=W,histogram=dict(CH),calls=sum(CH.values()),rank_mass=sum(r*n for r,n in CH.items()),deficit=m*W-sum(r*n for r,n in CH.items()),maxchild=max(CH));assert profile['deficit']==120 and profile['maxchild']==20
 assert {**c['profile'],'histogram':{int(k):n for k,n in c['profile']['histogram'].items()}}==profile
 result={};grid=Q(1,10**18)
 for fallback in [True,False]:
  label='with_fallback'if fallback else'without_fallback';b=Q(c['roots'][label]['b']);root=cost.certify(dict(CH),m,W,fallback);assert Q(int(Q(root['lower'])*10**18),10**18)==b
  cm=cost.moment(dict(CH),m,W,b,fallback);nextcm=cost.moment(dict(CH),m,W,b+grid,fallback);assert cm[1]<1<nextcm[0]
  lower,upper=other.moment(m,W,list(CH.items()),b);nlower,nupper=other.moment(m,W,list(CH.items()),b+grid)
  if fallback:
   total=32*m*m*sum(CH.values());bl,bu=other.moment(m,W,[(1,total)],b);nbl,nbu=other.moment(m,W,[(1,total)],b+grid);lower+=Q(1,10**16)*bl;upper+=Q(1,10**16)*bu;nlower+=Q(1,10**16)*nbl;nupper+=Q(1,10**16)*nbu
  assert upper<1<nlower;result[label]=dict(b=b,moment_interval=cm,next_grid_excluded=nextcm,independent_moment_interval=(lower,upper),independent_next_grid=(nlower,nupper))
 b=result['with_fallback'];b0=result['without_fallback'];assert b['b']==COARSE<b0['b']
 binding=dict(manifest_sha256=MANIFEST,public_head=HEAD,e8_source_head=E8_HEAD,candidate_sha256=CANDIDATE,receipt_hashes={n:sha(proof/n)for n in('VERIFICATION.json',)+RECEIPTS},adapter_sha256=sha(__file__),inputs_unchanged=True,all_supplier_stages_fresh=True,declarative_source=True,declarative_source_scope=pins['declarative_source_scope'],producer_regeneration_claim=False,lean_data_regeneration_claim=True,upstream_lean_rebuilt=False,parity_corrected_complete_invoice=True)
 return dict(profile=profile,coarse=b['b'],moment_interval=b['moment_interval'],next_grid_excluded=b['next_grid_excluded'],coarse_without_fallback=b0['b'],moment_interval_without_fallback=b0['moment_interval'],source_program_sha256=CANDIDATE,finite_guard=guard,roots=result,source_binding=binding,scope=pins['scope'])
