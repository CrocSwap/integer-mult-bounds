"""Fresh exact17-stage application of the changed485/1455 producer.

Retained source checks and attribution come from the authenticated #7480
closure. All adaptations are counted and recorded. No selected frontier is
modified. Apache-2.0, following the retained source notices.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util,json,gzip,shutil,subprocess,sys,time,os
CHILD_ENV=dict(os.environ);CHILD_ENV.pop('PYTHONOPTIMIZE',None)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'inputs/pr7480'
CANDIDATE=ROOT/'producer54/reroute'
NATIVE=ROOT/'producer54/validation_native/NATIVE-RESULT.json'
OUT=HERE/'RESULT.json'
ROUND_ROOT=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/kappa-research-20261116b')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
def read(path):
 raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw)if raw[:2]==b'\x1f\x8b'else raw)
def normal(x):return json.loads(json.dumps(x,default=str))
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
if not __debug__: raise RuntimeError('Optimized Python is prohibited for signed qualification')
binding_path=ROOT/'E4-SIGNED-BINDING.json'
assert sha256(binding_path.read_bytes()).hexdigest()==os.environ['E4_SIGNED_BINDING_SHA256'], 'Execution binding digest'
cfg=read(binding_path)
def check_closure():
 rows=cfg['closure']; assert isinstance(rows,dict) and rows
 for name,digest in rows.items():
  path=Path(name); assert path.is_absolute() and path.is_file() and not path.is_symlink() and sha256(path.read_bytes()).hexdigest()==digest, 'Closure mismatch '+name
 for path in (Path(__file__),SOURCE/'source.py',HERE/'w2_adapt.py',CANDIDATE/'WORD.json.gz',ROOT/'native.receipt.json',NATIVE,*(ROOT/'frozen-composition'/n for n in ('7546-WORD.json.gz','7546-NATIVE.json','7546-SIGNED.json','7604-WORD.json.gz','7604-INVOICE.json','7627-WORD.json.gz','CANDIDATE-WORD.json.gz'))):
  assert str(path.resolve()) in rows, 'Required input absent from closure'
check_closure()
src=load('producer_source',SOURCE/'source.py')
assert sha256((HERE/'w2_adapt.py').read_bytes()).hexdigest()=='85b8e86c1e5e4a2dbc2feb98d41b95bdd3c38a35842ff4bd97a0402d6e4f7119', 'Prepared helper hash mismatch'
adapter=load('producer_adapter',HERE/'w2_adapt.py')
FROZEN=ROOT/'frozen-composition'
old_word=read(FROZEN/'7546-WORD.json.gz');new_word=read(CANDIDATE/'WORD.json.gz')
assert new_word==read(FROZEN/'CANDIDATE-WORD.json.gz'),'Pinned literal helper757 word'
assert sha256(canonical(new_word)).hexdigest()=='1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e'
assert {k:v for k,v in old_word.items()if k!='program'}=={k:v for k,v in new_word.items()if k!='program'},'Exact native interface metadata'
old_result=read(FROZEN/'7546-NATIVE.json')
assert old_result['word_canonical_sha256']=='bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745'
# All paths/hashes are supplied by an independently reviewed execution freeze.
# Schema e4-signed-binding/v1 and e4-native-paired/v1 are provisional.
assert cfg['native_freeze_sha256']=='3328d0b08145bf8a6fa08e0a075d0dc77a24b3c7d6ae31d5eb298fe91db0be0f'
assert cfg['supervisor_freeze_sha256']=='7ffeaf1db1ead880401fe4f35f9495e88dfe4e0ad7de0454f639af8ef2630cc8'
assert cfg['supervisor_finalizer_sha256']=='3e76f10e5458578c7791c56d914f3d29150db000c6c2a9af61249977f67f58a9'
assert cfg['common_u_sha256']=='734403f0278609a6dfbeb962556fbf0f3bb66e95e7553302b5ddb10f7b579947'
for key in ('native_freeze','supervisor_freeze','supervisor_finalizer','common_u'):
 p=Path(cfg[key+'_path']); assert p.is_absolute() and p.is_file() and not p.is_symlink()
 assert sha256(p.read_bytes()).hexdigest()==cfg[key+'_sha256'] and cfg['closure'].get(str(p.resolve()))==cfg[key+'_sha256'],key+' closure pin'
assert cfg['provisional_sha256']=='a5cf1dd107e2cd1ded105aee741d72f2ce3ded433c9faf52cba25107f0adaa0f'
assert cfg['firstgate_sha256']=='11016b0db3aa46b16e36e6cfe9b4914d4d49bb4c77c1f4e6d2403f9e2d3783c7'
assert cfg['certificates_sha256']=='e6faf6fe56172f31c76cb3300055ba27f786f7e67a1f8e8e64ba446511b2b41e'
assert cfg['certificate_receipt_sha256']=='c67b225097edf653c3880ed0ef3a55cd0959bb112c0646cac2be812a6faba49f'
assert cfg['schema']=='e4-signed-binding/v1' and cfg['run_id']
assert cfg['source_canonical_sha256']=='b80b6e74bff87c8d8160c5e121dac7c68df0827a7061847b896075417a346238'
assert cfg['candidate_canonical_sha256']=='1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e'
assert cfg['candidate_gzip_sha256']=='736d475843e2ca53cad8a193ed582926e2659abaec40895a41d55efd4fca532f'
assert sha256((CANDIDATE/'WORD.json.gz').read_bytes()).hexdigest()==cfg['candidate_gzip_sha256']
assert sha256(canonical(new_word)).hexdigest()==cfg['candidate_canonical_sha256']
def bound(name):
 p=Path(cfg[name+'_path']); assert p.is_absolute() and p.is_file() and not p.is_symlink()
 assert cfg['closure'].get(str(p.resolve()))==cfg[name+'_sha256'] and sha256(p.read_bytes()).hexdigest()==cfg[name+'_sha256'],name+' byte binding'
 return read(p)
exact=bound('exact'); provisional=bound('provisional'); firstgate=bound('firstgate')
cert=bound('certificates'); cert_receipt=bound('certificate_receipt')
native=bound('native'); receipt=bound('native_receipt'); native_supervisor=bound('native_supervisor')
assert sha256(NATIVE.read_bytes()).hexdigest()==cfg['native_sha256']
assert sha256((ROOT/'native.receipt.json').read_bytes()).hexdigest()==cfg['native_receipt_sha256']
assert all(not (HERE/name).exists() for name in ('RESULT.json','GENERATOR-PREPARED.json','PRICE.json','MATCHED-ORDINARY.json','SOURCE-RESOURCE.json','source-checks','candidate-checks','adapted','assemble_odd_application.py.log')), 'exclusive fresh output required'
assert not list(HERE.glob('*.log')), 'existing log prevents fresh run'
assert exact['status']=='PASS_LITERAL_EXACT_ONLY' and exact['candidate_canonical_sha256']==cfg['candidate_canonical_sha256']
assert firstgate['candidate_canonical_sha256']==cfg['candidate_canonical_sha256'] and firstgate['exact_sha256']==cfg['exact_sha256'] and firstgate['price_sha256']==cfg['provisional_sha256']
assert firstgate['status']=='PROVISIONAL_EXACT_AND_DECLARED_PRICE_ONLY' and firstgate['qualified_kappa'] is False
assert provisional['status']=='PROVISIONAL_DECLARED_INVOICE_ONLY' and provisional['schema']=='e4-provisional-fixed-caller-price/v1' and provisional['qualified_kappa'] is False
assert firstgate['source_canonical_sha256']==cfg['source_canonical_sha256']==provisional['source']['canonical_sha256']
assert provisional['candidate']['canonical_sha256']==cfg['candidate_canonical_sha256'] and provisional['candidate']['gzip_sha256']==cfg['candidate_gzip_sha256']
assert firstgate['candidate_bracket']==provisional['candidate_bracket'] and firstgate['claim']==provisional['claim'] and firstgate['tested']==provisional['tested'] and firstgate['full_upper']==provisional['full_upper']
assert receipt['run_id']==native['run_id']==cfg['native_run_id'] and native_supervisor['run_id']==cfg['native_run_id']
assert type(cert_receipt['exit_code']) is int and cert_receipt['exit_code']==0 and cert_receipt['result_sha256']==cfg['certificates_sha256']
assert cert_receipt['status']==cert['status'] and cert_receipt['wall_killed'] is False
assert cert_receipt['candidate_canonical_sha256']==cfg['candidate_canonical_sha256']
assert cert_receipt['post_authentication_pass'] is True and cert_receipt['readback_limits_pass'] is True and cert_receipt['process_group_empty'] is True
assert cert_receipt['raw_hashes']['RESULT.json']==cfg['certificates_sha256']
assert cert['status']=='PASS_INDEPENDENT_CERTIFICATE_AND_REMAINING_LIVE_RANK_204' and cert['candidate_canonical_sha256']==cfg['candidate_canonical_sha256']
assert cert['source_records']==cert['candidate_records']==204 and cert['zero_records']==7 and cert['peak']==50
assert cert['actual_witness_rejections']==['old','wrong'] and cert['verifier_sha256']==cfg['certificate_adapter_sha256']
assert cert['input_sha256']['outputs/kappa-target368-20261116/agents/e4-direct-204/candidate-word.json.gz']==cfg['candidate_gzip_sha256']
assert cert['input_sha256']['outputs/kappa-target368-20261116/agents/e4-direct-204/candidate-certificates.json']==cfg['candidate_certificates_sha256']
assert receipt['status']=='SCOPED_GATE_RETURNED' and receipt['result_sha256']==cfg['native_sha256']
assert receipt['result_status']==native['status']=='PASS_E4_INGREDIENT_NATIVE_ONLY'
assert receipt['freeze_sha256']==native['freeze_sha256']==cfg['native_freeze_sha256']
assert native_supervisor['schema']=='e4-native-recovery/v1' and native_supervisor['status']=='PASS_RECOVERED_INGREDIENT_NATIVE' and native_supervisor['original_finalizer_core_status']=='PASS_SUPERVISED_INGREDIENT_NATIVE' and native_supervisor['result_status']==native['status']
assert type(native_supervisor['exit_code']) is int and native_supervisor['exit_code']==0 and native_supervisor['result_sha256']==cfg['native_sha256']
assert native_supervisor['freeze_sha256']==cfg['native_freeze_sha256'] and native_supervisor['driver_terminal_sha256']==cfg['native_receipt_sha256']
assert native_supervisor['started_sha256']==cfg['native_started_sha256'] and sha256(Path(cfg['native_started_path']).read_bytes()).hexdigest()==cfg['native_started_sha256']
assert cfg['closure'].get(str(Path(cfg['native_started_path']).resolve()))==cfg['native_started_sha256']
native_started=read(cfg['native_started_path'])
assert native_started['status']=='STARTED' and native_started['run_id']==cfg['native_run_id'] and native_started['freeze_sha256']==cfg['native_freeze_sha256']
assert native_supervisor['measured_within_limits'] is True and not native_supervisor['secondary_errors'] and not native_supervisor.get('error')
assert cfg['native_supervisor_provenance']=='RECOVERED_ORIGINAL_UNIT_NOT_ORIGINAL_TERMINAL'
assert cfg['recovery_receipt_sha256']==cfg['native_supervisor_sha256']
assert cfg['recovery_host_sha256']=='4bb1de52405b3a465461767b4b79599faa935f1ffa46092670ce56229e38a269'
host=Path(cfg['recovery_host_path']); assert host.is_absolute() and host.is_file() and not host.is_symlink() and sha256(host.read_bytes()).hexdigest()==cfg['recovery_host_sha256'] and cfg['closure'].get(str(host.resolve()))==cfg['recovery_host_sha256']
assert native_supervisor['recovery_provenance']=={'origin':'retained original unit','observer_exit_code':143,'host_readback_sha256':cfg['recovery_host_sha256'],'original_supervisor_terminal_present':False,'original_unit':'<REDACTED-UNIT-IDENTIFIER>'}
assert type(native_supervisor['execution_wall_seconds']) in (int,float) and 0<=native_supervisor['execution_wall_seconds']<=4200
assert type(native_supervisor['aggregate_cpu_usec']) is int and 0<native_supervisor['aggregate_cpu_usec']<=3600*1000000
assert type(native_supervisor['peak_memory_bytes']) is int and 0<native_supervisor['peak_memory_bytes']<=2*1024**3
assert native_supervisor['post_authentication_pass'] is True and native_supervisor['readback_limits_pass'] is True and native_supervisor['process_group_empty'] is True
assert native['schema']=='e4-native-paired/v1'
assert native['source_word']['canonical_sha256']==cfg['source_canonical_sha256'] and native['candidate_word']['canonical_sha256']==cfg['candidate_canonical_sha256']
assert native['source_word']['gzip_sha256']==cfg['source_gzip_sha256'] and native['candidate_word']['gzip_sha256']==cfg['candidate_gzip_sha256']
assert native['economics']['status']=='PASS_E4_18_CALL_INGREDIENT_ECONOMICS_ONLY' and native['economics']['calls']==18
assert all(native['physical'][x]['status']=='PASS_FINITE_PHYSICAL_ONLY' and native['physical'][x]['word_canonical_sha256']==cfg[x+'_canonical_sha256'] for x in ('source','candidate'))
# Directly bind retained checker inputs to the fresh paired ingredient result.
econ=native['economics']; grids=native['grids']
new_result=dict(word_canonical_sha256=cfg['candidate_canonical_sha256'],native=native['native']['candidate'],invoice=econ['candidate_invoice'],precision=econ['candidate_precision'],gate=econ['candidate_gate'],price=econ['candidate_price'],ordinary=econ['candidate_ordinary'],derived_grid=grids['candidate']['derived_grid'])
paired=dict(source=econ['source_precision'],source_gate=econ['source_gate'],source_price=econ['source_price'])
paired_ordinary=dict(source=econ['source_ordinary'])
commands=('emit_odd_type_b.py','emit_odd_type_ab.py','check_odd_caller_exact_grid.py',
          'check_odd_physical_binding.py','check_odd_precision.py','check_odd_partial_admission.py',
          'check_odd_fixed_tape_counts.py')
log=[];started=time.time()
with src.sources()as(vendor,archive,rank9,bundle,parent,unused_old):
 with src.bundles()as(parts,unused_previous,temp):
  working=temp/'producer54-signed-working';shutil.copytree(parts[7113]/'replay',working)
  folder=working/'supplier7112/short-caller'
  (folder.parent/'WORD.json.gz').write_bytes((CANDIDATE/'WORD.json.gz').read_bytes())
  (folder.parent/'RESULT.json').write_text(json.dumps(new_result,sort_keys=True,indent=2)+'\n')
  for path in folder.glob('SHORT-CATALOGUE-*-*.log'):path.unlink()
  sys.path.insert(0,str(folder))
  model=load('producer_signed_model',folder/'signed_model.py');ind=model.signed_model()
  code=(folder/'independent.py').read_text();part=code[code.index('def invoices('):code.index('def ordinary(')]
  assert part.count('assert calls==18')==1
  part=part.replace('assert calls==18',"assert calls==C['stages']")
  old="elif e[1]=='IDLE_ONE':P[8*len(e[3])]+=ports";assert part.count(old)==1
  part=part.replace(old,"elif e[1] in ('IDLE_ONE','IDLE_ODD'):P[8*len(e[3])+(e[1]=='IDLE_ODD')]+=ports")
  exec(compile(part,str(folder/'independent.py'),'exec'),ind.__dict__)
  C=read(parts[7113]/'expected/ODD-TYPE-AB-CALLER.json')
  assert sha256((parts[7113]/'expected/ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest()=='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
  inventories=[ind.native(w)for w in(old_word,new_word)]
  for n,r,w in zip(inventories,(old_result,new_result),(old_word,new_word)):
   assert normal(n)==r['native']and not n['bad_inputs']
   assert sha256(canonical(w)).hexdigest()==r['word_canonical_sha256']
  before,after=[ind.invoices(w,C,n)for w,n in zip((old_word,new_word),inventories)]
  previous=read(FROZEN/'7546-SIGNED.json')['price']
  assert Q(previous['gate']['claim'])==Q('0.003648411294790')
  ranks=set(before['P'])|set(after['P'])
  delta={r:after['P'].get(r,0)-before['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=before['P'].get(r,0)}
  assert after['T']==before['T']
  assert before['S']==after['S']==1424 and not before['empty_root_credits'] and not after['empty_root_credits']
  assert sum(after['T'].values())==22461 and after['S']==1424
  assert normal(before)==previous['after'],'Whole reconstructed #7546 invoice'
  peer_word=read(FROZEN/'7604-WORD.json.gz')
  peer_native=ind.native(peer_word);assert not peer_native['bad_inputs']
  peer_invoice=ind.invoices(peer_word,C,peer_native)
  frozen_peer=read(FROZEN/'7604-INVOICE.json')
  assert normal(peer_invoice['P'])==frozen_peer['paid'] and normal(peer_invoice['T'])==frozen_peer['targets']
  assert peer_invoice['S']==1424 and not peer_invoice['empty_root_credits']
  ranks=set(peer_invoice['P'])|set(after['P'])
  peer_delta={r:after['P'].get(r,0)-peer_invoice['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=peer_invoice['P'].get(r,0)}
  baseline_word=read(FROZEN/'7627-WORD.json.gz')
  assert sha256(canonical(baseline_word)).hexdigest()==cfg['source_canonical_sha256']
  assert sha256((FROZEN/'7627-WORD.json.gz').read_bytes()).hexdigest()==cfg['source_gzip_sha256']
  baseline_native=ind.native(baseline_word);assert not baseline_native['bad_inputs']
  assert normal(baseline_native)==normal(native['native']['source'])
  baseline_invoice=ind.invoices(baseline_word,C,baseline_native)
  assert after['T']==baseline_invoice['T'] and after['S']==baseline_invoice['S']
  assert not baseline_invoice['empty_root_credits'] and not after['empty_root_credits']
  G=load('producer_signed_price_engine',bundle/'gate.py')
  gate,price=G.exact_price(vendor,archive,before,after,{'gate':previous['gate']})
  directed=G.module('producer_native_comparator',vendor/'interval_gate.py')
  old_upper=Q(36657312773679346788340108614613,10**34)
  first_claim=Q(firstgate['claim']);first_probe=Q(firstgate['tested'])
  assert Q(firstgate['full_upper'])==old_upper
  assert old_upper<first_claim<first_probe<Q(gate['raw_bracket'][0])
  assert directed.moment(G.signed(baseline_invoice),old_upper)[1]<0
  assert directed.moment(G.signed(baseline_invoice),first_claim)[1]<0
  assert normal(after['P'])==provisional['candidate_invoice']['paid'] and normal(after['T'])==provisional['candidate_invoice']['targets']
  assert normal(baseline_invoice['P'])==provisional['source_invoice']['paid'] and normal(baseline_invoice['T'])==provisional['source_invoice']['targets']
  public_gate=directed.gate(after,first_claim,first_probe,*map(Q,gate['raw_bracket']),Q(gate['BIT_pin']))
  price_record=normal(dict(public_claim_gate=public_gate,before=before,after=after,gate=gate,price=price,
    baseline_7627=baseline_invoice,baseline_7627_rejects_claim=True,baseline_7627_rejects_raw_upper=True,
    first_gate_claim=first_claim,first_gate_probe=first_probe,first_gate_old_upper=old_upper,
    old_native=old_result['word_canonical_sha256'],new_native=new_result['word_canonical_sha256']))
  (folder/'CURRENT-PRICE.json').write_text(json.dumps(price_record,indent=2)+'\n')
  (folder/'COHORT-PRICE.json').write_text(json.dumps(normal(dict(target=after['T'],paid=after['P'],bracket=gate['raw_bracket'])),indent=2)+'\n')
  (HERE/'PRICE.json').write_text(json.dumps(price_record,indent=2)+'\n')
  print('PASS two complete literal invoices and both directed prices',price['claim_decimal'],flush=True)
  changes=adapter.adapt(folder,price['claim_decimal'],new_result['derived_grid']['fractional_bits'])
  for name in commands:
   print('RUN',name,flush=True);tick=time.time()
   with (HERE/(name+'.log')).open('x')as stream:
    subprocess.run([sys.executable,'-B',str(folder/name)],cwd=folder,stdout=stream,stderr=subprocess.STDOUT,check=True,env=CHILD_ENV)
   log.append({'check':name,'seconds':time.time()-tick})
   print((HERE/(name+'.log')).read_text(),end='',flush=True)
  assert(folder/'ODD-TYPE-AB-CALLER.json').read_bytes()==(parts[7113]/'expected/ODD-TYPE-AB-CALLER.json').read_bytes()
  fresh_price=read(folder/'CURRENT-PRICE.json');partial=read(folder/'ODD-ADMISSION-PARTIAL.json')
  assert fresh_price['after']==partial['invoice']
  assert fresh_price['gate']==partial['compiler_outer']
  # Same actual caller and same independent ordinary model for both words.
  # Mirror the seven-check partial admission's exact, counted ordinary patches.
  ordinary_code=code[code.index('def ordinary('):code.index('def main(')]
  ordinary_patches=(('calls=18;',"calls=C['stages'];"),
      ("queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)","queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)\n  fusedroute=sum(36500*p for e in C['events'] if e[:2]==[ty,'IDLE_ODD'])"),
      ('idle_routes=idleroute,query_routes=queryroute)','idle_routes=idleroute,query_routes=queryroute,fused_routes=fusedroute)'))
  for find,replacement in ordinary_patches:
   assert ordinary_code.count(find)==1, 'Exact ordinary patch count'
   ordinary_code=ordinary_code.replace(find,replacement,1)
  exec(compile(ordinary_code,str(folder/'independent.py'),'exec'),ind.__dict__)
  ordinary_base=normal(ind.ordinary(baseline_word,C,baseline_native))
  ordinary_candidate=normal(ind.ordinary(new_word,C,inventories[1]))
  charged=partial['ordinary'];caller_surcharge=charged['all_caller_scalar_surcharge'];conversions=charged['charged_caller_odd_conversions']
  for key in ('scalar_upper','init_clear_allowance','route_items','routing','caller_items','caller_total','raw_upper','per_input_conversion','lambda_second_charge','odd_divisions','lambda_paid_rank1_would_reduce_S_by'):
   assert ordinary_candidate[key]==charged[key], 'Fresh partial ordinary mismatch '+key
  assert ordinary_candidate['conservative_total']+caller_surcharge+conversions==charged['conservative_total'], 'Fresh complete ordinary bill mismatch'
  matched_base=ordinary_base['conservative_total']+caller_surcharge+conversions
  matched_candidate=charged['conservative_total']
  assert matched_base<10**9 and matched_candidate<10**9, 'Matched ordinary bound'
  matched_ordinary=dict(model='same actual signed caller and independent ordinary model; same caller surcharge and conversion',
    source=ordinary_base,candidate=ordinary_candidate,caller_scalar_surcharge=caller_surcharge,
    caller_odd_conversions=conversions,source_total=matched_base,candidate_total=matched_candidate,
    candidate_partial_ordinary=charged,complete_U_tariff='unknown; separate qualification required')
  (HERE/'MATCHED-ORDINARY.json').write_text(json.dumps(matched_ordinary,sort_keys=True,indent=2)+'\n')
  # A separate pristine source replay: the source record below is derived from
  # THIS fresh candidate native run; it is not a fresh standalone native pass.
  assert normal(baseline_native)==normal(native['native']['source']), 'Fresh source native inventory binding'
  source_signed_gate,source_signed_price=G.exact_price(vendor,archive,before,baseline_invoice,{'gate':previous['gate']})
  source_work=temp/'producer54-source-working';shutil.copytree(parts[7113]/'replay',source_work)
  source_folder=source_work/'supplier7112/short-caller'
  source_word_bytes=(FROZEN/'7627-WORD.json.gz').read_bytes()
  (source_folder.parent/'WORD.json.gz').write_bytes(source_word_bytes)
  source_result=normal(dict(status='DERIVED_FRESH_SOURCE_RESOURCE_ONLY',word_canonical_sha256=cfg['source_canonical_sha256'],
      native=native['native']['source'],invoice=econ['source_invoice'],
      precision=paired['source'],gate=paired['source_gate'],price=paired['source_price'],
      ordinary=paired_ordinary['source'],candidate_native_result_sha256=sha256(NATIVE.read_bytes()).hexdigest(),
      scope='Derived from fresh candidate-bound native paired source calculations; not a standalone source native pass.'))
  (source_folder.parent/'RESULT.json').write_text(json.dumps(source_result,sort_keys=True,indent=2)+'\n')
  source_cohort=normal(dict(target=baseline_invoice['T'],paid=baseline_invoice['P'],bracket=source_signed_gate['raw_bracket']))
  source_current=normal(dict(before=before,after=baseline_invoice,gate=source_signed_gate,price=source_signed_price,
      source_native_result_sha256=sha256((source_folder.parent/'RESULT.json').read_bytes()).hexdigest()))
  (source_folder/'COHORT-PRICE.json').write_text(json.dumps(source_cohort,sort_keys=True,indent=2)+'\n')
  (source_folder/'CURRENT-PRICE.json').write_text(json.dumps(source_current,sort_keys=True,indent=2)+'\n')
  source_changes=adapter.adapt(source_folder,source_signed_price['claim_decimal'],int(paired['source']['word']['dyadic_height']))
  source_logs=[]
  for name in commands:
   tick=time.time();log_path=HERE/('SOURCE-'+name+'.log')
   with log_path.open('x') as stream:
    subprocess.run([sys.executable,'-B',str(source_folder/name)],cwd=source_folder,stdout=stream,stderr=subprocess.STDOUT,check=True,env=CHILD_ENV)
   source_logs.append(dict(check=name,seconds=time.time()-tick,sha256=sha256(log_path.read_bytes()).hexdigest()))
  source_names=('ODD-TYPE-B-REPLAY.json','ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json',
      'ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json')
  source_checks={name:read(source_folder/name) for name in source_names}
  # Preserve the exact seven raw source outputs before temporary cleanup.
  source_check_dir=HERE/'source-checks';source_check_dir.mkdir(exist_ok=False)
  for name in source_names:
   data=(source_folder/name).read_bytes()
   with (source_check_dir/name).open('xb') as out: out.write(data)
   assert sha256((source_check_dir/name).read_bytes()).hexdigest()==sha256(data).hexdigest()

  source_partial=source_checks['ODD-ADMISSION-PARTIAL.json']
  assert source_partial['invoice']==source_current['after'] and source_partial['compiler_outer']==source_current['gate'], 'Fresh source 17-call invoice and gate'
  assert source_partial['ordinary']['conservative_total']==matched_base, 'Fresh source matched ordinary bill'
  assert (source_folder/'ODD-TYPE-AB-CALLER.json').read_bytes()==(parts[7113]/'expected/ODD-TYPE-AB-CALLER.json').read_bytes(), 'Fresh source caller pin'
  candidate_precision=read(folder/'ODD-PRECISION.json');candidate_tape=read(folder/'ODD-FIXED-TAPE-COUNTS.json')
  precision_keys=('context_height','context_mass_bits','context_c','native_grid','rounded_native','rounded_caller')
  tape_keys=('H','context_c','context_bound_bits','native_invocations','owned_banks_per_raw_occurrence',
      'scalar_macro_inputs','scalar_services_upper','monomial_map_slots','elementary_records_upper','max_scalar_numerator_bits','common_grid')
  paired_resources=dict(precision={key:{'source':source_checks['ODD-PRECISION.json'][key],
      'candidate':candidate_precision[key]} for key in precision_keys},
      tape={key:{'source':source_checks['ODD-FIXED-TAPE-COUNTS.json'][key],
      'candidate':candidate_tape[key]} for key in tape_keys})
  # A ceiling is not a precision proof: absent a charged common context,
  # stop if either independently recomputed signed context differs.
  for key in ('context_height','context_mass_bits','context_c'):
   assert source_checks['ODD-PRECISION.json'][key]==candidate_precision[key], 'Common charged precision required: '+key
  assert Q(candidate_precision['context_c'])<=4096, 'Precision exceeds stated common U domain'
  source_resource=normal(dict(status='DERIVED_FRESH_SOURCE_RESOURCE_ONLY',native_word_sha256=cfg['source_canonical_sha256'],
      candidate_native_receipt_sha256=sha256(NATIVE.read_bytes()).hexdigest(),
      source_native_derived_sha256=sha256((source_folder.parent/'RESULT.json').read_bytes()).hexdigest(),
      source_word_gzip_sha256=sha256(source_word_bytes).hexdigest(),
      caller_sha256=sha256((source_folder/'ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest(),
      source_current_price_sha256=sha256((source_folder/'CURRENT-PRICE.json').read_bytes()).hexdigest(),
      source_cohort_price_sha256=sha256((source_folder/'COHORT-PRICE.json').read_bytes()).hexdigest(),
      source_17_gate_sha256=sha256(canonical(normal(source_signed_gate))).hexdigest(),
      source_18_gate_sha256=sha256(canonical(normal(paired['source_gate']))).hexdigest(),
      check_sha256={name:sha256((source_folder/name).read_bytes()).hexdigest() for name in source_names},
      derived_result=source_result,source_17_gate=source_signed_gate,source_17_price=source_signed_price,
      source_18_gate=paired['source_gate'],source_18_price=paired['source_price'],adapter=source_changes,
      checks=source_checks,logs=source_logs,paired_resource_comparison=paired_resources,source_catalogue_rerun=False,
      common_U_tariff='unknown; separate qualification required'))
  assert all(sha256((source_check_dir/name).read_bytes()).hexdigest()==source_resource['check_sha256'][name] for name in source_names)
  (HERE/'SOURCE-RESOURCE.json').write_text(json.dumps(source_resource,sort_keys=True,indent=2)+'\n')
  # Record actual protected generator before invoking --size or any slice.
  generator_path=folder/'short_native_catalogue.py'
  assert generator_path.is_file() and not generator_path.is_symlink()
  prepared_generator=dict(schema='swarm30-generator-prepared/v1',generator_sha256=sha256(generator_path.read_bytes()).hexdigest(),
    candidate_gzip_sha256=cfg['candidate_gzip_sha256'],candidate_canonical_sha256=cfg['candidate_canonical_sha256'],
    firstgate_result_sha256=cfg['firstgate_sha256'],native_result_sha256=sha256(NATIVE.read_bytes()).hexdigest(),
    native_receipt_sha256=sha256((ROOT/'native.receipt.json').read_bytes()).hexdigest(),run_id=receipt['run_id'])
  with (HERE/'GENERATOR-PREPARED.json').open('x') as out: json.dump(prepared_generator,out,sort_keys=True,indent=2);out.write('\n')
  catalogue=[]
  size=int(subprocess.check_output([sys.executable,'-B',str(folder/'short_native_catalogue.py'),'--size'],cwd=folder,text=True,env=CHILD_ENV))
  assert size>0, 'Fresh compiler catalogue must be nonempty'
  for start in range(0,size,1000):
   stop=min(start+1000,size);print('RUN complete catalogue',start,stop,flush=True)
   path=folder/f'SHORT-CATALOGUE-{start}-{stop}.log'
   with path.open('x')as stream:subprocess.run([sys.executable,'-B',str(folder/'short_native_catalogue.py'),'--start',str(start),'--stop',str(stop)],cwd=folder,stdout=stream,check=True,env=CHILD_ENV)
   text=path.read_text();catalogue.append(json.loads(text[text.index('\n{'):]))
   shutil.copy2(path,HERE/path.name)
  # Closed coverage of the unchanged protected catalogue and caller.
  assert type(size) is int and size>0 and catalogue
  cursor=0
  for item in catalogue:
   assert all(type(item[k]) is int for k in ('catalogue_size','slice_start','slice_stop','checked_maps','main_boundary_pairs'))
   assert item['catalogue_size']==size and item['slice_start']==cursor and item['slice_stop']>cursor
   assert item['slice_stop']-cursor==item['checked_maps'] and item['checked_maps']<=1000 and item['word_sha256']==cfg['candidate_gzip_sha256']
   assert item['phase_control_rejected'] is True
   cursor=item['slice_stop']
  assert cursor==size and sum(x['checked_maps'] for x in catalogue)==size
  assert sum(x['main_boundary_pairs'] for x in catalogue)==104
  assert public_gate['outer']['strict_count']==54 and public_gate['outer']['functional_count']==4
  with(HERE/'assemble_odd_application.py.log').open('x')as stream:
   subprocess.run([sys.executable,'-B',str(folder/'assemble_odd_application.py')],cwd=folder,stdout=stream,stderr=subprocess.STDOUT,check=True,env=CHILD_ENV)
  print((HERE/'assemble_odd_application.py.log').read_text(),end='',flush=True)
  files=('ODD-TYPE-B-REPLAY.json','ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json',
         'ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json','ODD-8X9-APPLICATION-CHECKS.json')
  candidate_check_dir=HERE/'candidate-checks';candidate_check_dir.mkdir(exist_ok=False)
  for name in files:
   data=(folder/name).read_bytes()
   with (candidate_check_dir/name).open('xb') as out: out.write(data)
   assert sha256((candidate_check_dir/name).read_bytes()).hexdigest()==sha256(data).hexdigest()
  result=normal(dict(status='PASS_E4_COMPLETE_SIGNED_APPLICATION',candidate_check_sha256={name:sha256((candidate_check_dir/name).read_bytes()).hexdigest() for name in files},
    claim=fresh_price['gate']['claim'],price=fresh_price,caller_sha256=sha256((folder/'ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest(),
    adapter=changes,matched_ordinary=matched_ordinary,source_resource=source_resource,catalogue_size=size,catalogue_generator_sha256=sha256((folder/'short_native_catalogue.py').read_bytes()).hexdigest(),catalogue=catalogue,checks={name:read(folder/name)for name in files},
    source_head='99438c43df7aac1e5dbcc43c1578fcd886c119ec',peer_head='ba2638c5a6e2b9a1c0c559a41811e5d41a591f41',
    component_head='71f5acb0409daf208a865482f3349049dbd3251c',timings=log,elapsed_seconds=time.time()-started,
    assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']))
  # Retain the precisely adapted checker text and its generated essential inputs.
  keep=HERE/'adapted';keep.mkdir(exist_ok=True)
  for name in set(commands)|{'short_native_catalogue.py','assemble_odd_application.py','CURRENT-PRICE.json','COHORT-PRICE.json'}:
   shutil.copy2(folder/name,keep/name)
  assert sha256((keep/'short_native_catalogue.py').read_bytes()).hexdigest()==prepared_generator['generator_sha256']==result['catalogue_generator_sha256']
  check_closure()
  with OUT.open('x') as out: out.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
  print(result['status'],price['claim_decimal'],flush=True)
