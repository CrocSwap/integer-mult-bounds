"""Fresh exact17-stage application of the changed485/1455 producer.

Retained source checks and attribution come from the authenticated #7480
closure. All adaptations are counted and recorded. No selected frontier is
modified. Apache-2.0, following the retained source notices.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util,json,gzip,shutil,subprocess,sys,time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'inputs/pr7480'
CANDIDATE=ROOT/'producer54/reroute'
NATIVE=ROOT/'producer54/validation_native/NATIVE-RESULT.json'
OUT=HERE/'RESULT.json'
ROUND_ROOT=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/kappa-research-20261116')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj);return obj
def read(path):
 raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw)if raw[:2]==b'\x1f\x8b'else raw)
def normal(x):return json.loads(json.dumps(x,default=str))
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
assert __debug__
src=load('producer_source',SOURCE/'source.py')
assert sha256((HERE/'w2_adapt.py').read_bytes()).hexdigest()=='06e9ff2b6d73275b87d1d710d32edf7b3028264e7bde858012a28896eadc6136', 'Prepared helper hash mismatch'
adapter=load('producer_adapter',HERE/'w2_adapt.py')
FROZEN=ROOT/'frozen-composition'
old_word=read(FROZEN/'7546-WORD.json.gz');new_word=read(CANDIDATE/'WORD.json.gz')
assert new_word==read(FROZEN/'CANDIDATE-WORD.json.gz'),'Pinned literal helper757 word'
assert sha256(canonical(new_word)).hexdigest()=='fd8aa08c7654791f9f6255898a83c06c8d114f22ab7bc7e6763c4fff2c015277'
assert {k:v for k,v in old_word.items()if k!='program'}=={k:v for k,v in new_word.items()if k!='program'},'Exact native interface metadata'
old_result=read(FROZEN/'7546-NATIVE.json');new_result=read(NATIVE)
assert new_result['status']=='PASS_CONTACT7623_COMPLETE_NATIVE'
assert old_result['word_canonical_sha256']=='bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745'
assert sha256(canonical(new_word)).hexdigest()==new_result['word_canonical_sha256']
receipt=read(ROOT/'native.receipt.json')
assert receipt['stage']=='native' and receipt['exit']==0 and isinstance(receipt['run_id'],str) and receipt['run_id']
assert receipt['run_id']==read(ROOT/'QUALIFICATION-ID.json')['run_id'], 'Fresh qualification run ID'
assert receipt['candidate_canonical_sha256']==sha256(canonical(new_word)).hexdigest()
assert receipt['native_result_sha256']==sha256(NATIVE.read_bytes()).hexdigest()
assert receipt['adapter_sha256']==sha256((ROOT/'CONTACT7623-ADAPTERS.json').read_bytes()).hexdigest()
assert receipt['launcher_sha256']==sha256((ROOT/'CONTACT7623-LAUNCHER.py').read_bytes()).hexdigest()
commands=('emit_odd_type_b.py','emit_odd_type_ab.py','check_odd_caller_exact_grid.py',
          'check_odd_physical_binding.py','check_odd_precision.py','check_odd_partial_admission.py',
          'check_odd_fixed_tape_counts.py')
log=[];started=time.time()
with src.sources()as(vendor,archive,rank9,bundle,parent,unused_old):
 with src.bundles()as(parts,unused_previous,temp):
  working=temp/'producer54-signed-working';shutil.copytree(parts[7113]/'replay',working)
  folder=working/'supplier7112/short-caller'
  (folder.parent/'WORD.json.gz').write_bytes((CANDIDATE/'WORD.json.gz').read_bytes())
  (folder.parent/'RESULT.json').write_bytes(NATIVE.read_bytes())
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
  assert sum(after['P'].values())==110111 and sum(after['T'].values())==22461
  assert normal(before)==previous['after'],'Whole reconstructed #7546 invoice'
  peer_word=read(FROZEN/'7604-WORD.json.gz')
  peer_native=ind.native(peer_word);assert not peer_native['bad_inputs']
  peer_invoice=ind.invoices(peer_word,C,peer_native)
  frozen_peer=read(FROZEN/'7604-INVOICE.json')
  assert normal(peer_invoice['P'])==frozen_peer['paid'] and normal(peer_invoice['T'])==frozen_peer['targets']
  assert peer_invoice['S']==1424 and not peer_invoice['empty_root_credits']
  ranks=set(peer_invoice['P'])|set(after['P'])
  peer_delta={r:after['P'].get(r,0)-peer_invoice['P'].get(r,0)for r in ranks if after['P'].get(r,0)!=peer_invoice['P'].get(r,0)}
  # Reconstruct the current #7623 baseline with this actual native inventory
  # and the very same signed caller, not from a projected raw delta.
  baseline_word=read(FROZEN/'7623-WORD.json.gz')
  assert sha256(canonical(baseline_word)).hexdigest()=='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c'
  baseline_native=ind.native(baseline_word);assert not baseline_native['bad_inputs']
  baseline_invoice=ind.invoices(baseline_word,C,baseline_native)
  source_invoice_path=FROZEN/'7623-INVOICE.json'
  assert sha256(source_invoice_path.read_bytes()).hexdigest()=='5be4724fde8264b8b1b4a565ea2eb1a56339f29528db40728b3fab210c44208d'
  source_invoice=read(source_invoice_path)
  assert normal(baseline_invoice['P'])==source_invoice['paid'] and normal(baseline_invoice['T'])==source_invoice['targets'], 'Fresh signed #7623 baseline invoice'
  assert baseline_invoice['S']==1424 and not baseline_invoice['empty_root_credits']
  assert sum(baseline_invoice['P'].values())==110145 and sum(baseline_invoice['T'].values())==22461
  actual_delta={r:after['P'].get(r,0)-baseline_invoice['P'].get(r,0) for r in set(after['P'])|set(baseline_invoice['P']) if after['P'].get(r,0)!=baseline_invoice['P'].get(r,0)}
  expected_delta={1:-51,2:17,4:-17,5:17}
  assert actual_delta==expected_delta and after['T']==baseline_invoice['T'], 'Fresh complete signed #7623 comparison'
  def delta_from_source(prior):
   ranks=set(baseline_invoice['P'])|set(prior['P'])|set(expected_delta)
   return {r:baseline_invoice['P'].get(r,0)-prior['P'].get(r,0)+expected_delta.get(r,0) for r in ranks if baseline_invoice['P'].get(r,0)-prior['P'].get(r,0)+expected_delta.get(r,0)}
  assert delta==delta_from_source(before) and peer_delta==delta_from_source(peer_invoice), 'Derived baseline comparisons'
  candidate_invoice=read(FROZEN/'CANDIDATE-INVOICE.json')
  assert normal(after['P'])==candidate_invoice['paid'] and normal(after['T'])==candidate_invoice['targets']
  gate_path=FROZEN/'CONTACT7623-PRICE.json'
  assert sha256(gate_path.read_bytes()).hexdigest()=='7176024971cb38065f3403335e9ab27e9a8902034fa38e4a252c970b58603233'
  first_gate=read(gate_path)
  assert first_gate['status']=='PROVISIONAL_UNDER_COMMON_U' and first_gate['bindings']['candidate_canonical_sha256']=='fd8aa08c7654791f9f6255898a83c06c8d114f22ab7bc7e6763c4fff2c015277'
  assert first_gate['bindings']['original_word_canonical_sha256']=='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c' and first_gate['bindings']['old_invoice_sha256']=='5be4724fde8264b8b1b4a565ea2eb1a56339f29528db40728b3fab210c44208d'
  assert sha256((FROZEN/'CANDIDATE-INVOICE.json').read_bytes()).hexdigest()==first_gate['candidate_invoice']['sha256'], 'First-gate candidate invoice bytes'
  first_claim=Q(first_gate['claim']);first_probe=Q(first_gate['tested']);old_upper=Q(first_gate['old_published_raw_upper'])
  assert old_upper==Q('0.0036624027916') and old_upper<first_claim<first_probe
  G=load('producer_signed_price_engine',bundle/'gate.py')
  gate,price=G.exact_price(vendor,archive,before,after,{'gate':previous['gate']})
  assert Q(gate['claim'])>Q(previous['gate']['raw_bracket'][1]),'Strictly higher than #7546 raw crossing'
  assert Q(gate['claim'])>Q('0.0036475398278'),'Strictly higher than upper endpoint of #7542 price enclosure'
  assert Q(gate['claim'])>Q(new_result['gate']['claim'])
  native_invoice={k:({int(r):v for r,v in value.items()}if k in('T','P')else value)for k,value in new_result['invoice'].items()}
  directed=G.module('producer_native_comparator',vendor/'interval_gate.py')
  assert directed.moment(G.signed(before),Q(gate['claim']))[1]<0,'Exact #7546 invoice rejects the new signed claim'
  assert directed.moment(G.signed(native_invoice),Q(gate['claim']))[1]<0
  assert directed.moment(G.signed(peer_invoice),Q(gate['claim']))[1]<0,'Exact open #7604 invoice rejects the new signed claim'
  assert Q(gate['claim'])>Q('0.0036502223358273'),'Strict improvement over latest #7604 crossing'
  assert directed.moment(G.signed(baseline_invoice),old_upper)[1]<0, 'Current #7623 invoice rejects its certified upper bound'
  assert directed.moment(G.signed(baseline_invoice),first_claim)[1]<0, 'Current #7623 rejects candidate claim'
  assert Q(gate['claim'])>=first_claim and first_probe<Q(gate['raw_bracket'][0]), 'First gate claim and probe within fresh signed bracket'
  public_claim=first_claim
  public_gate=directed.gate(after,public_claim,first_probe,*map(Q,gate['raw_bracket']),Q(gate['BIT_pin']))
  price_record=normal(dict(public_claim_gate=public_gate,before=before,after=after,gate=gate,price=price,
    native_baseline_rejects_new_claim=True,signed_incumbent_rejects_new_claim=True,
    baseline_7623=baseline_invoice,baseline_7623_rejects_claim=True,baseline_7623_rejects_raw_upper=True,
    first_gate_claim=first_claim,first_gate_probe=first_probe,first_gate_old_upper=old_upper,
    old_native=old_result['word_canonical_sha256'],new_native=new_result['word_canonical_sha256']))
  (folder/'CURRENT-PRICE.json').write_text(json.dumps(price_record,indent=2)+'\n')
  (folder/'COHORT-PRICE.json').write_text(json.dumps(normal(dict(target=after['T'],paid=after['P'],bracket=gate['raw_bracket'])),indent=2)+'\n')
  (HERE/'PRICE.json').write_text(json.dumps(price_record,indent=2)+'\n')
  print('PASS two complete literal invoices and both directed prices',price['claim_decimal'],flush=True)
  changes=adapter.adapt(folder,price['claim_decimal'],new_result['derived_grid']['fractional_bits'])
  for name in commands:
   print('RUN',name,flush=True);tick=time.time()
   with (HERE/(name+'.log')).open('w')as stream:
    subprocess.run([sys.executable,'-B',str(folder/name)],cwd=folder,stdout=stream,stderr=subprocess.STDOUT,check=True)
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
  assert normal(baseline_native)==new_result['source_native'], 'Fresh source native inventory binding'
  paired=new_result['paired_precision'];paired_ordinary=new_result['paired_ordinary']
  source_signed_gate,source_signed_price=G.exact_price(vendor,archive,before,baseline_invoice,{'gate':previous['gate']})
  source_work=temp/'producer54-source-working';shutil.copytree(parts[7113]/'replay',source_work)
  source_folder=source_work/'supplier7112/short-caller'
  source_word_bytes=(FROZEN/'7623-WORD.json.gz').read_bytes()
  (source_folder.parent/'WORD.json.gz').write_bytes(source_word_bytes)
  source_result=normal(dict(status='DERIVED_FRESH_SOURCE_RESOURCE_ONLY',word_canonical_sha256='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c',
      native=new_result['source_native'],invoice=new_result['source_invoice'],
      precision=paired['source_7623'],gate=paired['source_gate'],price=paired['source_price'],
      ordinary=paired_ordinary['source_7623'],candidate_native_result_sha256=sha256(NATIVE.read_bytes()).hexdigest(),
      scope='Derived from fresh candidate-bound native paired source calculations; not a standalone source native pass.'))
  (source_folder.parent/'RESULT.json').write_text(json.dumps(source_result,sort_keys=True,indent=2)+'\n')
  source_cohort=normal(dict(target=baseline_invoice['T'],paid=baseline_invoice['P'],bracket=source_signed_gate['raw_bracket']))
  source_current=normal(dict(before=before,after=baseline_invoice,gate=source_signed_gate,price=source_signed_price,
      source_native_result_sha256=sha256((source_folder.parent/'RESULT.json').read_bytes()).hexdigest()))
  (source_folder/'COHORT-PRICE.json').write_text(json.dumps(source_cohort,sort_keys=True,indent=2)+'\n')
  (source_folder/'CURRENT-PRICE.json').write_text(json.dumps(source_current,sort_keys=True,indent=2)+'\n')
  source_changes=adapter.adapt(source_folder,source_signed_price['claim_decimal'],int(paired['source_7623']['word']['dyadic_height']))
  source_logs=[]
  for name in commands:
   tick=time.time();log_path=HERE/('SOURCE-'+name+'.log')
   with log_path.open('x') as stream:
    subprocess.run([sys.executable,'-B',str(source_folder/name)],cwd=source_folder,stdout=stream,stderr=subprocess.STDOUT,check=True)
   source_logs.append(dict(check=name,seconds=time.time()-tick,sha256=sha256(log_path.read_bytes()).hexdigest()))
  source_names=('ODD-TYPE-B-REPLAY.json','ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json',
      'ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json')
  source_checks={name:read(source_folder/name) for name in source_names}
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
  source_resource=normal(dict(status='DERIVED_FRESH_SOURCE_RESOURCE_ONLY',native_word_sha256='48e1845e6b24832731705a3ff096b22d2b807428f7d625d06b45adfe3b5a738c',
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
  (HERE/'SOURCE-RESOURCE.json').write_text(json.dumps(source_resource,sort_keys=True,indent=2)+'\n')
  catalogue=[]
  size=int(subprocess.check_output([sys.executable,'-B',str(folder/'short_native_catalogue.py'),'--size'],cwd=folder,text=True))
  for start in range(0,size,1000):
   stop=min(start+1000,size);print('RUN complete catalogue',start,stop,flush=True)
   path=folder/f'SHORT-CATALOGUE-{start}-{stop}.log'
   with path.open('x')as stream:subprocess.run([sys.executable,'-B',str(folder/'short_native_catalogue.py'),'--start',str(start),'--stop',str(stop)],cwd=folder,stdout=stream,check=True)
   text=path.read_text();catalogue.append(json.loads(text[text.index('\n{'):]))
   shutil.copy2(path,HERE/path.name)
  with(HERE/'assemble_odd_application.py.log').open('w')as stream:
   subprocess.run([sys.executable,'-B',str(folder/'assemble_odd_application.py')],cwd=folder,stdout=stream,stderr=subprocess.STDOUT,check=True)
  print((HERE/'assemble_odd_application.py.log').read_text(),end='',flush=True)
  files=('ODD-TYPE-AB-REPLAY.json','ODD-CALLER-EXACT-GRID.json','ODD-PHYSICAL-BINDING.json',
         'ODD-PRECISION.json','ODD-ADMISSION-PARTIAL.json','ODD-FIXED-TAPE-COUNTS.json','ODD-8X9-APPLICATION-CHECKS.json')
  result=normal(dict(status='PASS_CONTACT7623_COMPLETE_SIGNED_APPLICATION',
    claim=fresh_price['gate']['claim'],price=fresh_price,caller_sha256=sha256((folder/'ODD-TYPE-AB-CALLER.json').read_bytes()).hexdigest(),
    adapter=changes,matched_ordinary=matched_ordinary,source_resource=source_resource,catalogue=catalogue,checks={name:read(folder/name)for name in files},
    source_head='99438c43df7aac1e5dbcc43c1578fcd886c119ec',peer_head='ba2638c5a6e2b9a1c0c559a41811e5d41a591f41',
    component_head='71f5acb0409daf208a865482f3349049dbd3251c',timings=log,elapsed_seconds=time.time()-started,
    assumptions=['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery']))
  OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
  # Retain the precisely adapted checker text and its generated essential inputs.
  keep=HERE/'adapted';keep.mkdir(exist_ok=True)
  for name in set(commands)|{'short_native_catalogue.py','assemble_odd_application.py','CURRENT-PRICE.json','COHORT-PRICE.json'}:
   shutil.copy2(folder/name,keep/name)
  print(result['status'],price['claim_decimal'],flush=True)
