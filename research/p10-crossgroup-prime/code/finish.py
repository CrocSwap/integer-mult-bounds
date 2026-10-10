#!/usr/bin/env python3
"""Bind the immutable source, actual cross-group word, finite banks and exact assembly.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,hashlib,struct
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

def finish(out):
 out=Path(out);pin=read(ROOT/'SOURCE.json');src=ROOT/'vendor/predecessor';pred=out/'predecessor';base=out/'base';candidate=out/'candidate';mat=out/'materialized';ver=read(pred/'verification.json');oldcert=read(pred/'certificate.json');oldst=read(base/'249-states.json');st=read(candidate/'249-states.json')
 assert ver['status']=='PASS_IMMUTABLE_P10_PRESINK_RETIMING_FIVE_STAGE_BANKED_CONSTRUCTION' and ver['inputs_unchanged']
 assert ver['manifest_sha256']==sha(src/'MANIFEST.json')==pin['predecessor']['manifest_sha256']
 dep=ver['source_dependency'];assert dep['status']=='PASS_IMMUTABLE_PR320_SOURCE_AND_EXACT_CHANGE_SET' and dep['commit']==pin['pr320']['head'] and dep['upstream_manifest_sha256']==pin['pr320']['manifest_sha256']
 assert Q(ver['kappa'])==Q(oldcert['kappa'])==Q(pin['base_kappa'])<Q(pin['comparison_kappa'])<Q(pin['kappa'])
 required={'virtual','raw','bit','scalar','primes','banks','complex','math','finite','descent','target','kernel','restore','presink','sink','reorder'}
 assert set(ver['fresh_stages'])==required and len(ver['negative_controls'])==len(required)
 assert read(pred/'complex.json')['status']=='PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION' and read(pred/'complex.json')['precision_guard']['retained_row_coefficient']==20161
 assert read(pred/'primes.json')['all_remaining_factors_below_2_power_80']
 assert sha(base/'COHORT249-RECORDS.bin')==oldst['record_sha256']==pin['target_prefix_sha256']==read(pred/'kernel.json')['input_raw_sha256']
 assert sha(candidate/'COHORT249-RECORDS.bin')==st['record_sha256']==pin['final_word_sha256']
 receipts=['predecessor/verification.json','predecessor/certificate.json','predecessor/complex.json','predecessor/banks.json','EXPORT.json']
 stages={}
 for name,binding in pin['stage_bindings'].items():
  r=read(mat/name/(name+'.json'));stages[name]=r
  assert all(r[k]==v for k,v in binding.items()),name
  assert r['selection_sha256']==sha(ROOT/'stages'/(name+'-selection.json'))==sha(mat/(name+'-selection.json'))
  transform='kernel' if name=='kernel2' else name
  assert r['transform_sha256']==sha(src/(transform+'_transform.py'))
  assert r['both_reflected_ledgers'] and r['unchanged_copy_lifetimes']
  if 'scalar' in r:
   assert all(r['scalar'][k]['all_sources_and_dirty_restored'] and r['scalar'][k]['wrong_rows']==0 for k in ('forward','inverse'))
   assert r['scalar']['controls'] and all(not c['all_sources_and_dirty_restored'] and c['wrong_rows']>0 for c in r['scalar']['controls'])
  receipts.append('materialized/'+name+'/'+name+'.json')
 assert stages['kernel']['selected_entries']==1043 and stages['kernel']['rank_drop']==1195
 assert stages['restore']['selected']==240 and stages['restore']['endpoint_rank_saving']==240
 assert stages['presink']['selected_gate_count']==4 and stages['presink']['unchanged_all_input_output_frames']
 assert stages['sink']['selected']==7 and stages['sink']['physical_R']==8223 and stages['reorder']['selected']==133
 assert stages['kernel2']['selected_entries']==3 and stages['kernel2']['rank_drop']==6 and stages['kernel2']['output_raw_sha256']==pin['final_word_sha256']
 assert st['n']==oldst['n']==10143 and st['v']==oldst['v']==960 and st['h']==20 and st['regs']==oldst['regs'] and len(set(st['regs']))==8223
 H,adds,units,copies,records=census(candidate/'COHORT249-RECORDS.bin')
 assert adds==336227 and units==338147 and copies==20 and records==386883
 assert sum(H.values())==48507 and sum(r*n for r,n in H.items())==179469
 legal=read(out/'LEGALITY.json');cols=read(out/'COLUMNS.json');bank=read(out/'BANK.json');price=read(out/'PRICE.json');inv=read(out/'INVOICE.json');tiling=read(out/'TILING.json');prime=read(out/'FRAME-PRIMES.json');fs=read(candidate/'frames.json')['frames']
 assert legal['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and legal['all_final_frames_pass'] and legal['copies']==legal['erasures']==20 and legal['common_frame_ADDs']==adds and legal['rank_mass']==179469 and {int(r):n for r,n in legal['paid_histogram']}==H
 assert cols['status']=='PASS_GENERIC_FIVE_STAGE_FORMAL_COLUMNS_AND_COMPUTED_PREFIX' and cols['formal_columns_checked']==12063 and cols['independent_dirty_registers']==8223 and cols['local_scalar_additions']==adds and cols['fresh_center_copies']==100 and cols['copied_center_original_source_immutable']
 assert len(cols['negative_controls'])==6 and all(c['rejected']for c in cols['negative_controls'])
 assert H=={int(r):n for r,n in cols['local_raw_H']}=={int(r):n for r,n in price['local_histogram'].items()}
 assert prime['status']=='PASS_EXACT_FRAME_AND_ANNIHILATOR_MINORS_FOR_ALL_PRIMES_ABOVE_2_POWER_80' and prime['input_sha256']==sha(candidate/'frames.json') and prime['zero_row_control_rejected']
 assert prime['frames']==len(fs)==14038 and prime['basis_witnesses']==2*len(fs) and int(prime['max_abs_minor'])<2**80 and prime['max_minor_bits']==21
 assert bank['status']=='PASS_GENERIC_EXACT_CHARTS_ACTUAL_BANK_ALLOCATION' and bank['all_new_ordinary_annihilators_full_rank'] and 'saved_literal_banks' not in bank
 assert bank['new_exact_charts']==431 and bank['changed_projector_charts']==3658 and bank['max_new_chart_factors']==240 and bank['changed_helper_endpoints']==1286 and bank['actual_helper_roles']==8223 and bank['deleted_inert_roles']==0
 assert bank['physical_replicas']==tiling['physical_replicas']==inv['physical_replicas']==pin['physical_replicas']==300
 assert bank['literal_stock']==3291435 and bank['normalized_stock']==658287 and bank['banks_per_stage']==427887 and bank['actual_role_replica_stage_assignments']==12334500 and bank['new_endpoint_saved_rank']==1441
 expected={3:310,4:960,6:1,7:1,10:6,12:3,13:1,15:3,16:5,18:22,19:1004,20:5907};assert {int(r):n for r,n in bank['residual_families'].items()}==expected=={int(r):n for r,n in tiling['census'].items()}
 used=Counter()
 for pattern in bank['bank_patterns']:
  assert sum(pattern['widths'])==100
  for r in pattern['widths']:used[r]+=pattern['count']
 assert used=={r:300*n for r,n in expected.items()} and len(bank['bank_patterns'])==14 and sum(p['count']for p in bank['bank_patterns'])==427887
 assert bank['endpoint_address_columns']==5600 and bank['nonzero_omission_repeat_control_columns']==5600 and bank['normalizer_factor_ceiling']==787
 oldbank=read(pred/'banks.json')['banks'];assert oldbank['normalizer_factor_bound']==599 and oldbank['max_chart_factors']<=400 and max(400,bank['max_new_chart_factors'])+99+100<=787
 literal={r:1500*n for r,n in H.items()}
 for r in (4,19,38,42):literal[r]=literal.get(r,0)+576000
 assert literal=={int(r):int(n)for r,n in inv['literal_histogram'].items()}=={int(r):5*n for r,n in price['cohort_candidate']['histogram'].items()}
 mass=sum(r*n for r,n in literal.items());calls=sum(literal.values());stock=bank['literal_stock'];assert mass==328531500 and calls==75064500 and stock*100-mass==612000
 J=300*(24*960+10*8223);K=2*5*300*((stock-1)+8223*100*787);coeff=300*(5*units+6*960)+J*16*(10000+1)**2+J*(stock+20)+calls*(8*10000+8)+calls*128*200**3+16*100**3+100*300+calls+K+1
 assert inv['status']=='PASS_COHORT_LITERAL_FIVE_STAGE_FINITE_INVOICE_AND_POSITIVE_CUTOFFS' and coeff==127517659550812001==int(inv['full_counted_primitive_coefficient']) and K==1951324602000==int(inv['extra_selector_calls'])==bank['selector_charge']
 assert coeff<2**80 and K<2**41 and inv['payload_bits']==cols['payload_prefix_bits']==98<104
 assert price['status']=='PASS_ACTUAL_P10_COMPOSED_WORD_TWO_MOMENTS_AND_47_CONSTRAINTS' and Q(price['kappa'])==Q(pin['native_kappa']) and price['source_word_sha256']==pin['final_word_sha256'] and price['local_rank_mass']==179469 and price['residual']==142629
 assert all(Q(price[k][1])<1 for k in ('first_interval','second_interval')) and all(Q(price[k][0])>1 for k in ('first_next','second_next'))
 assert len(price['ordinary_gaps'])==3 and all(min(map(Q,g.values()))>0 for g in price['ordinary_gaps']) and len(price['assembly']['strict_constraints'])==47 and min(map(Q,price['assembly']['strict_constraints'].values()))>0 and price['adjacent_rejected'] and price['full_fallback_retained']
 refine=read(out/'REFINEMENT.json')
 assert refine['status']=='PASS_P10_PRIME_THRESHOLD_FULL_INVOICE_TWO_MOMENTS_FINITE_BOOTSTRAP_OUTER47'
 assert Q(refine['native_kappa'])==Q(price['kappa'])==Q(pin['native_kappa'])<Q(refine['kappa'])==Q(pin['kappa'])
 assert refine['source']['word_sha256']==pin['final_word_sha256'] and refine['source']['arithmetic_source_head']==pin['arithmetic_source']['head']
 for name,digest in refine['source']['receipt_hashes'].items():assert sha(out/name)==digest
 for name,digest in refine['source']['engine_hashes'].items():assert sha((src if name in ('moment.py','base_two_moment.py','outer.py') else ROOT/'code')/name)==digest
 assert 'FRAME-PRIMES.json' in refine['source']['receipt_hashes']
 assert refine['prime_threshold']['Q']==2**127-1 and refine['prime_threshold']['lucas_lehmer_residue']==0 and refine['prime_threshold']['growing_prime_regime_retained'] and refine['prime_threshold']['all_permitted_primes_q_at_least_Q']
 assert refine['bootstrap']['levels']==8 and len(refine['bootstrap']['gaps'])==8 and all(min(map(Q,g['gaps'].values()))>0 for g in refine['bootstrap']['gaps'])
 assert len(refine['assembly']['strict_constraints'])==47 and min(map(Q,refine['assembly']['strict_constraints'].values()))>0 and len(refine['negative_controls'])==12
 assert refine['complete_literal_invoice']['coefficient']==coeff and refine['complete_literal_invoice']['rank_mass']==mass and refine['complete_literal_invoice']['positive_rank_children']==calls
 result=dict(status='PASS_SOURCE_BOUND_P10_CROSSGROUP_T300_PRIME_THRESHOLD_BOOTSTRAP_CONDITIONAL_CONSTRUCTION',kappa=refine['kappa'],native_kappa=price['kappa'],predecessor_kappa=pin['base_kappa'],comparison_kappa=pin['comparison_kappa'],kappa_gain=str(Q(refine['kappa'])-Q(pin['comparison_kappa'])),word_sha256=pin['final_word_sha256'],source_regenerated=True,early_kernel_entries=1043,early_entrance_rank=1195,late_kernel_entries=3,late_entrance_rank=6,physical_replicas=300,literal_stock=stock,normalized_stock=658287,helper_assignments=12334500,new_frame_charts=431,changed_projector_charts=3658,new_chart_factor_max=240,normalizer=787,finite_coefficient=coeff,selector_charge=K,payload_bits=98,scope=refine['scope'])
 receipts+=['LEGALITY.json','COLUMNS.json','BANK.json','PRICE.json','INVOICE.json','TILING.json','FRAME-PRIMES.json','REFINEMENT.json']
 result['fresh_receipt_hashes']={n:sha(out/n)for n in receipts};(out/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS integrated crossgroup T300 '+refine['kappa'],flush=True)
if __name__=='__main__':finish(sys.argv[1])
