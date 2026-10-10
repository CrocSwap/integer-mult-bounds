#!/usr/bin/env python3
"""Bind immutable suppliers, actual p10b word, finite banks and exact outer assembly.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,hashlib,struct,gzip
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def census(path):
 H=Counter();adds=units=copies=records=0
 for op,a,b,c,f,z in struct.iter_unpack('<6i',Path(path).read_bytes()):
  records+=1
  if op==0 and f:H[f]+=1
  elif op==1:adds+=1;units+=abs(c)
  elif op==2:H[z]+=1;copies+=1
 return H,adds,units,copies,records


def verify_regenerated_files(src,work,files):
 # Gzip containers can differ across OS/zlib builds. Bind both containers and
 # compare the complete expanded bytes, without parsing or normalizing JSON.
 names={'graph_p10.json','kchron_p10.json','profile_p10.json','word_p10.json.gz','frames_p10.json.gz'}
 assert set(files)==names,'Exactly five regenerated source files required'
 for name,r in files.items():
  pinned=(src/'bitword/selected/bit'/name).read_bytes()
  rebuilt=(work/'final1'/name).read_bytes()
  assert hashlib.sha256(pinned).hexdigest()==r['pinned'],name+' pinned container hash'
  assert hashlib.sha256(rebuilt).hexdigest()==r['rebuilt'],name+' rebuilt container hash'
  if name.endswith('.gz'):
   pinned=gzip.decompress(pinned);rebuilt=gzip.decompress(rebuilt)
  assert pinned==rebuilt,name+' complete expanded bytes'
  assert hashlib.sha256(rebuilt).hexdigest()==r['expanded'],name+' expanded hash'

def finish(out):
 out=Path(out);pin=read(ROOT/'SOURCE.json');E=pin['expected'];src=ROOT/'vendor/predecessor';pred=out/'predecessor';base=out/'base';candidate=out/'candidate';mat=out/'materialized';ver=read(pred/'verification.json');oldcert=read(pred/'certificate.json');oldst=read(base/'249-states.json');st=read(candidate/'249-states.json')
 assert ver['status']=='PASS_IMMUTABLE_PARITY_FUSED_P10_FIVE_STAGE_BANKED_CONSTRUCTION' and ver['inputs_unchanged']
 assert ver['manifest_sha256']==sha(src/'MANIFEST.json')==pin['predecessor']['manifest_sha256']
 assert Q(ver['kappa'])==Q(oldcert['kappa'])==Q(pin['base_kappa'])<Q(pin['kappa'])
 required={'virtual','raw','bit','scalar','primes','banks','complex','math','finite'}
 assert set(ver['fresh_stages'])==required and len(ver['negative_controls'])==len(required)
 assert read(pred/'complex.json')['status']=='PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION' and read(pred/'complex.json')['precision_guard']['retained_row_coefficient']==20161
 assert read(pred/'primes.json')['all_remaining_factors_below_2_power_80']
 assert sha(base/'COHORT249-RECORDS.bin')==oldst['record_sha256']==pin['source_parity_sha256']
 assert (base/'COHORT249-RECORDS.bin').read_bytes()==gzip.decompress((pred/'records.bin.gz').read_bytes())
 assert sha(candidate/'COHORT249-RECORDS.bin')==st['record_sha256']==pin['final_word_sha256']
 ex=read(out/'EXPORT.json');assert ex['base_n']==10020 and ex['candidate_n']==E['n'] and ex['R']==E['R'] and len(ex['removed_physical_registers'])==pin['stage_bindings']['sink']['selected']
 assert ex['all_used_frames']==E['frames'] and ex['new_used_frames']==E['new_charts']
 for path,d in ex['input_hashes'].items():assert sha(path)==d
 regen=read(out/'source-regeneration/REGENERATION.json');assert regen['status']=='PASS_STRUCTURAL_PRODUCER_REGENERATION_ALL_FIVE_FILES' and regen['rounds']==2 and regen['source_unchanged'] and regen['source_manifest_sha256']==pin['predecessor']['manifest_sha256'] and regen['checker_sha256']==sha(src/'bitword/producer/regenerate_structural.py')
 verify_regenerated_files(src,out/'source-regeneration',regen['files'])
 controls=read(out/'PRODUCER-BINDING-CONTROLS.json')
 expected_controls={'forged-pinned','forged-rebuilt','forged-expanded','missing-file','extra-file'}|{'changed-complete-bytes-'+name for name in regen['files']}
 assert controls['status']=='PASS_EXACT_PRODUCER_CONTENT_BINDING_CONTROLS' and len(controls['negative_controls'])==len(expected_controls) and set(controls['negative_controls'])==expected_controls

 receipts=['PRODUCER-BINDING-CONTROLS.json','source-regeneration/REGENERATION.json','predecessor/verification.json','predecessor/certificate.json','predecessor/complex.json','predecessor/primes.json','predecessor/banks.json','EXPORT.json','ROLE-MAP.json']
 stages={}
 previous=pin['source_parity_sha256']
 for name in ('descent','target','kernel','restore','sink','reorder','descent2'):
  binding=pin['stage_bindings'][name]
  r=read(mat/name/(('descent' if name=='descent2' else name)+'.json'));stages[name]=r
  assert all(r[k]==v for k,v in binding.items()),name
  assert r['selection_sha256']==sha(ROOT/'stages'/(name+'-selection.json'))==sha(mat/(name+'-selection.json'))
  assert r['transform_sha256']==sha(ROOT/'engines'/(name+'_transform.py'))
  assert r['both_reflected_ledgers'] and r['unchanged_copy_lifetimes']
  raw=gzip.decompress((mat/name/('records.bin.gz' if name in ('descent','target','descent2') else name+'-records.bin.gz')).read_bytes());digest=hashlib.sha256(raw).hexdigest();assert digest==pin['stage_word_sha256'][name]
  if 'input_raw_sha256'in r:assert r['input_raw_sha256']==previous
  if 'output_raw_sha256'in r:assert r['output_raw_sha256']==digest
  previous=digest
  if 'scalar'in r:
   assert all(r['scalar'][k]['all_sources_and_dirty_restored'] and r['scalar'][k]['wrong_rows']==0 for k in ('forward','inverse'))
   assert r['scalar']['controls'] and all(not c['all_sources_and_dirty_restored'] and c['wrong_rows']>0 for c in r['scalar']['controls'])
  receipts.append('materialized/'+name+'/'+('descent' if name=='descent2' else name)+'.json')
 assert stages['descent']['selected_gate_count']==480 and stages['target']['selected_groups']==120 and stages['target']['negative_control']
 assert stages['target']['literal_prefix_dependencies_checked'] and stages['target']['producer_context_unchanged']
 assert all(stages['target'][k]['all_source_and_dirty_restored'] and stages['target'][k]['arbitrary_target_contents_preserved'] and stages['target'][k]['all_formal_columns']==10020 for k in ('forward','inverse'))
 assert stages['kernel']['selected_entries']==pin['stage_bindings']['kernel']['selected_entries'] and stages['kernel']['rank_drop']==pin['stage_bindings']['kernel']['rank_drop']
 assert stages['descent2']['selected_gate_count']==pin['stage_bindings']['descent2']['selected_gate_count'] and stages['descent2']['operand_source_spans_contained'] and stages['descent2']['unchanged_all_input_output_frames']
 assert stages['restore']['selected']==stages['restore']['endpoint_rank_saving']==240
 assert stages['sink']['selected']==pin['stage_bindings']['sink']['selected'] and stages['sink']['physical_R']==E['R'] and stages['reorder']['selected']==pin['stage_bindings']['reorder']['selected']
 assert stages['reorder']['integer_replay']['identical'] and stages['reorder']['all_gate_frames_contain_operand_source_spans']
 assert st['n']==oldst['n']==E['n'] and st['v']==oldst['v']==960 and st['h']==20 and st['regs']==oldst['regs'] and len(set(st['regs']))==E['R']
 H,adds,units,copies,records=census(candidate/'COHORT249-RECORDS.bin')
 assert adds==E['adds'] and units==E['units'] and copies==20 and records==E['records'] and sum(H.values())==E['paid_calls'] and sum(r*n for r,n in H.items())==E['rank_mass']
 legal=read(out/'LEGALITY.json');cols=read(out/'COLUMNS.json');bank=read(out/'BANK.json');price=read(out/'PRICE.json');inv=read(out/'INVOICE.json');tiling=read(out/'TILING.json');prime=read(out/'FRAME-PRIMES.json');fs=read(candidate/'frames.json')['frames']
 assert legal['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and legal['all_final_frames_pass'] and legal['copies']==legal['erasures']==20 and legal['common_frame_ADDs']==adds and legal['rank_mass']==E['rank_mass'] and {int(r):n for r,n in legal['paid_histogram']}==H
 assert cols['status']=='PASS_GENERIC_FIVE_STAGE_FORMAL_COLUMNS_AND_COMPUTED_PREFIX' and cols['formal_columns_checked']==4*960+E['R'] and cols['independent_dirty_registers']==E['R'] and cols['local_scalar_additions']==adds and cols['fresh_center_copies']==100 and cols['copied_center_original_source_immutable']
 assert len(cols['negative_controls'])==6 and all(c['rejected']for c in cols['negative_controls'])
 assert H=={int(r):n for r,n in cols['local_raw_H']}=={int(r):n for r,n in price['local_histogram'].items()}
 assert prime['status']=='PASS_EXACT_FRAME_AND_ANNIHILATOR_MINORS_FOR_ALL_PRIMES_ABOVE_2_POWER_80' and prime['input_sha256']==sha(candidate/'frames.json') and prime['zero_row_control_rejected']
 assert prime['frames']==len(fs)==E['frames'] and prime['basis_witnesses']==2*len(fs) and int(prime['max_abs_minor'])==E['max_abs_minor']<2**80 and prime['max_minor_bits']==E['max_minor_bits']
 assert bank['status']=='PASS_GENERIC_EXACT_CHARTS_ACTUAL_BANK_ALLOCATION' and bank['all_new_ordinary_annihilators_full_rank'] and 'saved_literal_banks'not in bank
 assert bank['new_exact_charts']==E['new_charts'] and bank['changed_projector_charts']==E['changed_projectors'] and bank['max_new_chart_factors']==E['max_chart_factors'] and bank['changed_helper_endpoints']==E['changed_helper_endpoints'] and bank['actual_helper_roles']==E['R'] and bank['deleted_inert_roles']==0
 assert bank['physical_replicas']==tiling['physical_replicas']==inv['physical_replicas']==pin['physical_replicas']==300
 assert bank['literal_stock']==E['literal_stock'] and bank['normalized_stock']==E['normalized_stock'] and bank['banks_per_stage']==E['banks_per_stage'] and bank['actual_role_replica_stage_assignments']==5*300*E['R'] and bank['new_endpoint_saved_rank']==E['endpoint_saved_rank']
 expected={int(r):n for r,n in E['residual_families'].items()};assert {int(r):n for r,n in bank['residual_families'].items()}==expected=={int(r):n for r,n in tiling['census'].items()}
 used=Counter()
 for pattern in bank['bank_patterns']:
  assert sum(pattern['widths'])==100
  for r in pattern['widths']:used[r]+=pattern['count']
 assert used=={r:300*n for r,n in expected.items()} and len(bank['bank_patterns'])==E['bank_patterns'] and sum(p['count']for p in bank['bank_patterns'])==E['banks_per_stage']
 assert bank['endpoint_address_columns']==E['endpoint_columns'] and bank['nonzero_omission_repeat_control_columns']==E['endpoint_columns'] and bank['normalizer_factor_ceiling']==787
 oldbank=read(pred/'banks.json')['banks'];assert oldbank['normalizer_factor_bound']==349 and oldbank['max_chart_factors']==150 and max(oldbank['max_chart_factors'],bank['max_new_chart_factors'])+99+100<=787
 literal={r:1500*n for r,n in H.items()}
 for r in (4,19,38,42):literal[r]=literal.get(r,0)+576000
 assert literal=={int(r):int(n)for r,n in inv['literal_histogram'].items()}=={int(r):5*n for r,n in price['cohort_candidate']['histogram'].items()}
 mass=sum(r*n for r,n in literal.items());calls=sum(literal.values());stock=bank['literal_stock'];assert mass==E['literal_mass'] and calls==E['literal_calls'] and stock*100-mass==612000
 J=300*(24*960+10*E['R']);K=2*5*300*((stock-1)+E['R']*100*787);coeff=300*(5*units+6*960)+J*16*(10000+1)**2+J*(stock+20)+calls*(8*10000+8)+calls*128*200**3+16*100**3+100*300+calls+K+1
 assert inv['status']=='PASS_COHORT_LITERAL_FIVE_STAGE_FINITE_INVOICE_AND_POSITIVE_CUTOFFS' and coeff==E['coefficient']==int(inv['full_counted_primitive_coefficient']) and K==E['selector']==int(inv['extra_selector_calls'])==bank['selector_charge']
 assert coeff<2**80 and K<2**41 and inv['payload_bits']==cols['payload_prefix_bits']==E['payload_bits']<104
 assert price['status']=='PASS_ACTUAL_P10_COMPOSED_WORD_TWO_MOMENTS_AND_47_CONSTRAINTS' and Q(price['kappa'])==Q(pin['native_kappa']) and price['source_word_sha256']==pin['final_word_sha256'] and price['local_rank_mass']==E['rank_mass'] and price['residual']==E['residual']
 assert all(Q(price[k][1])<1 for k in ('first_interval','second_interval')) and all(Q(price[k][0])>1 for k in ('first_next','second_next'))
 assert len(price['ordinary_gaps'])==3 and all(min(map(Q,g.values()))>0 for g in price['ordinary_gaps']) and len(price['assembly']['strict_constraints'])==47 and min(map(Q,price['assembly']['strict_constraints'].values()))>0 and price['adjacent_rejected'] and price['full_fallback_retained'] and price['complex_binds']==E['complex_binds']
 reserve=price['complex_reserve'];cv=read(out/'complex-reserve/VERIFICATION.json');supplier=price['complex_supplier'];binding=supplier['source_binding']
 assert Path(reserve['package'])==(ROOT/'vendor/complex-reserve').resolve() and Path(reserve['proof'])==(out/'complex-reserve').resolve()
 assert reserve['binding']==binding and binding['manifest_sha256']==sha(ROOT/'vendor/complex-reserve/MANIFEST.json')==pin['complex_reserve']['manifest_sha256']
 assert cv['status']=='PASS_PORTABLE_PUBLIC_PR327_P10_COMPLEX_SUPPLIER_TRANSFER' and cv['inputs_unchanged'] and cv['candidate_sha256']==pin['complex_reserve']['candidate_sha256'] and len(cv['fresh_stages'])==2
 assert Q(price['complex_saving'])==Q(cv['complex_coarse'])==Q(pin['complex_reserve']['coarse'])
 assert supplier['finite_guard']['retained_row_coefficient']==20161 and binding['inputs_unchanged'] and binding['all_supplier_stages_fresh'] and binding['adapter_sha256']==sha(ROOT/'code/future_supplier.py')
 for name,digest in binding['receipt_hashes'].items():assert sha(out/'complex-reserve'/name)==digest;receipts.append('complex-reserve/'+name)
 refine=read(out/'REFINEMENT.json')
 assert refine['status']=='PASS_P10_PRIME_THRESHOLD_FULL_INVOICE_TWO_MOMENTS_FINITE_BOOTSTRAP_OUTER47'
 assert Q(refine['native_kappa'])==Q(price['kappa'])==Q(pin['native_kappa'])<Q(refine['kappa'])==Q(pin['kappa'])
 assert refine['source']['word_sha256']==pin['final_word_sha256'] and refine['source']['arithmetic_source_head']==pin['arithmetic_source']['head']
 for name,digest in refine['source']['receipt_hashes'].items():assert sha(out/name)==digest
 for name,digest in refine['source']['external_receipt_hashes'].items():assert sha(name)==digest
 for name,digest in refine['source']['engine_hashes'].items():assert sha((src if name in ('moment.py','base_two_moment.py','outer.py') else ROOT/'code')/name)==digest
 assert 'FRAME-PRIMES.json'in refine['source']['receipt_hashes']
 assert refine['prime_threshold']['Q']==2**127-1 and refine['prime_threshold']['lucas_lehmer_residue']==0 and refine['prime_threshold']['growing_prime_regime_retained'] and refine['prime_threshold']['all_permitted_primes_q_at_least_Q']
 ordinary=refine['ordinary_saving'];assert ordinary['complex_binds']==E['complex_binds'] and Q(ordinary['value'])==min(Q(refine['root']['lower']),Q(ordinary['strict_complex_cap']))<Q(ordinary['complex_limit'])==(1-Q(1,10**9))*Q(price['complex_saving'])
 assert all(Q(ordinary[k][1])<1 for k in ('first_interval','second_interval')) and Q(refine['root']['lower'])>=Q(ordinary['value'])
 assert refine['bootstrap']['levels']==E['bootstrap_levels'] and len(refine['bootstrap']['gaps'])==E['bootstrap_levels'] and all(min(map(Q,g['gaps'].values()))>0 for g in refine['bootstrap']['gaps'])
 assert len(refine['assembly']['strict_constraints'])==47 and min(map(Q,refine['assembly']['strict_constraints'].values()))>0 and len(refine['negative_controls'])==12
 assert refine['complete_literal_invoice']['coefficient']==coeff and refine['complete_literal_invoice']['rank_mass']==mass and refine['complete_literal_invoice']['positive_rank_children']==calls
 result=dict(status='PASS_SOURCE_BOUND_P10B_FLOW016_PR327_T300_CONDITIONAL_CONSTRUCTION',kappa=refine['kappa'],native_kappa=price['kappa'],predecessor_kappa=pin['base_kappa'],kappa_gain=str(Q(refine['kappa'])-Q(pin['base_kappa'])),word_sha256=pin['final_word_sha256'],source_regenerated=True,entrance_families=pin['stage_bindings']['kernel']['selected_entries'],entrance_rank=pin['stage_bindings']['kernel']['rank_drop'],final_descent_gates=pin['stage_bindings']['descent2']['selected_gate_count'],restored_helpers=240,terminal_sinks=pin['stage_bindings']['sink']['selected'],reordered_gates=pin['stage_bindings']['reorder']['selected'],physical_replicas=300,literal_stock=stock,normalized_stock=E['normalized_stock'],helper_assignments=5*300*E['R'],new_frame_charts=E['new_charts'],changed_projector_charts=E['changed_projectors'],new_chart_factor_max=E['max_chart_factors'],normalizer=787,finite_coefficient=coeff,selector_charge=K,payload_bits=E['payload_bits'],complex_reserve={k:v for k,v in binding.items()if k!='receipt_hashes'},scope=refine['scope'])
 receipts+=['LEGALITY.json','COLUMNS.json','BANK.json','PRICE.json','INVOICE.json','TILING.json','FRAME-PRIMES.json','REFINEMENT.json']
 result['fresh_receipt_hashes']={n:sha(out/n)for n in receipts};(out/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS integrated p10b structural PR327 T300 '+refine['kappa'],flush=True)
if __name__=='__main__':finish(sys.argv[1])
