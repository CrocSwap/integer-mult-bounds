#!/usr/bin/env python3
"""Cross-bind strict PR320 provenance, actual kernel word, complete T300 banks and both engines.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,hashlib,json,struct
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
 out=Path(out);pin=read(ROOT/'SOURCE.json');src=ROOT/'vendor/predecessor';pred=out/'predecessor';base=out/'base';candidate=out/'candidate';ver=read(pred/'verification.json');oldcert=read(pred/'certificate.json');oldst=read(base/'249-states.json');st=read(candidate/'249-states.json');sel=read(ROOT/'stages/kernel2-selection.json');stage=read(out/'kernel2/kernel2.json')
 assert ver['status']=='PASS_IMMUTABLE_P10_PRESINK_RETIMING_FIVE_STAGE_BANKED_CONSTRUCTION' and ver['inputs_unchanged']
 assert ver['manifest_sha256']==sha(src/'MANIFEST.json')==pin['predecessor']['manifest_sha256']
 assert ver['source_dependency']['status']=='PASS_IMMUTABLE_PR320_SOURCE_AND_EXACT_CHANGE_SET' and ver['source_dependency']['commit']==pin['pr320']['head'] and ver['source_dependency']['upstream_manifest_sha256']==pin['pr320']['manifest_sha256']
 assert Q(ver['kappa'])==Q(oldcert['kappa'])==Q(pin['base_kappa'])<Q(pin['kappa'])
 required={'virtual','raw','bit','scalar','primes','banks','complex','math','finite','descent','target','kernel','restore','presink','sink','reorder'}
 assert set(ver['fresh_stages'])==required and len(ver['negative_controls'])==len(required)
 assert read(pred/'complex.json')['status']=='PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION'
 assert read(pred/'complex.json')['precision_guard']['retained_row_coefficient']==20161
 assert read(pred/'primes.json')['all_remaining_factors_below_2_power_80']
 assert sha(base/'COHORT249-RECORDS.bin')==oldst['record_sha256']==pin['base_word_sha256']==stage['input_raw_sha256']==sel['input_raw_sha256']
 assert sha(candidate/'COHORT249-RECORDS.bin')==st['record_sha256']==pin['final_word_sha256']==stage['output_raw_sha256']
 assert stage['selection_sha256']==sha(ROOT/'stages/kernel2-selection.json') and stage['transform_sha256']==sha(src/'kernel_transform.py')
 assert stage['status']=='PASS_GEN4_PER_ENTRY_CUT_KERNEL_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS'
 assert stage['selected_entries']==3 and stage['rank_drop']==6 and stage['both_reflected_ledgers'] and stage['unchanged_copy_lifetimes'] and stage['unchanged_data_input_output_and_dirty_output_frames']
 assert st['n']==oldst['n']==10143 and st['v']==oldst['v']==960 and st['h']==20 and st['regs']==oldst['regs'] and len(set(st['regs']))==8223 and st['final']==oldst['final']
 changed={int(k)for k in st['initial']if st['initial'][k]!=oldst['initial'][k]};assert changed=={7000,7234,7349}=={f['pivot']for f in sel['families']}
 proof=stage['proof'];assert proof['selected_helpers']==12 and proof['total_entrance_rank']==6 and proof['prefix_relations_checked']==3 and proof['prefix_target_comparisons']==2880 and proof['removed_initial_reads']==32 and proof['added_setup_and_restores']==18
 for k in ('selected_helpers_untouched_before_own_cut','no_prefix_response_outside_targets_and_own_helper','all_old_surviving_scalar_and_copy_events_in_order','source_context_preserved'):assert proof[k]
 for k in ('forward','inverse'):assert stage['scalar'][k]['all_sources_and_dirty_restored'] and stage['scalar'][k]['formal_columns']==10143
 assert len(stage['scalar']['controls'])==2 and all(not c['all_sources_and_dirty_restored']for c in stage['scalar']['controls'])
 H,adds,units,copies,records=census(candidate/'COHORT249-RECORDS.bin');oldH,oldadds,oldunits,oldcopies,oldrecords=census(base/'COHORT249-RECORDS.bin')
 delta={r:H[r]-oldH[r]for r in H.keys()|oldH.keys()if H[r]!=oldH[r]};assert delta=={1:12,2:9,3:-12}=={int(r):n for r,n in stage['local_histogram_delta'].items()}=={int(r):n for r,n in sel['expected_local_delta'].items()}
 assert adds==336239 and units==338159 and copies==oldcopies==20 and records==386904 and adds-oldadds==units-oldunits==-14 and records-oldrecords==-5
 assert sum(H.values())==48516 and sum(r*n for r,n in H.items())==179464 and sum(r*(H[r]-oldH[r])for r in H.keys()|oldH.keys())==-6
 legal=read(out/'LEGALITY.json');cols=read(out/'COLUMNS.json');bank=read(out/'BANK.json');price=read(out/'PRICE.json');inv=read(out/'INVOICE.json');tiling=read(out/'TILING.json')
 assert legal['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and legal['all_final_frames_pass'] and legal['selected_helpers']==3 and legal['restored_helper_endpoints']==0 and legal['copies']==legal['erasures']==20 and legal['common_frame_ADDs']==adds and legal['rank_mass']==179464
 assert cols['status']=='PASS_GENERIC_FIVE_STAGE_FORMAL_COLUMNS_AND_COMPUTED_PREFIX' and cols['formal_columns_checked']==12063 and cols['independent_dirty_registers']==8223 and cols['local_scalar_additions']==adds and cols['fresh_center_copies']==100 and cols['copied_center_original_source_immutable']
 assert len(cols['negative_controls'])==6 and all(c['rejected']for c in cols['negative_controls'])
 assert H=={int(r):n for r,n in cols['local_raw_H']}=={int(r):n for r,n in price['local_histogram'].items()}
 assert bank['status']=='PASS_GENERIC_EXACT_CHARTS_ACTUAL_BANK_ALLOCATION' and bank['all_new_ordinary_annihilators_full_rank']
 assert bank['new_exact_charts']==1 and bank['changed_projector_charts']==15 and bank['max_new_chart_factors']==115 and bank['changed_helper_endpoints']==3 and bank['actual_helper_roles']==8223 and bank['deleted_inert_roles']==0
 assert bank['physical_replicas']==tiling['physical_replicas']==inv['physical_replicas']==pin['physical_replicas']==300
 assert bank['literal_stock']==3291360 and bank['normalized_stock']==658272 and bank['banks_per_stage']==427872 and bank['actual_role_replica_stage_assignments']==12334500 and bank['new_endpoint_saved_rank']==6
 expected={3:310,4:960,6:1,7:1,10:6,12:3,13:1,15:3,16:5,18:23,19:1007,20:5903};assert {int(r):n for r,n in bank['residual_families'].items()}==expected=={int(r):n for r,n in tiling['census'].items()}
 used=Counter()
 for pattern in bank['bank_patterns']:
  assert sum(pattern['widths'])==100
  for r in pattern['widths']:used[r]+=pattern['count']
 assert used=={r:300*n for r,n in expected.items()} and len(bank['bank_patterns'])==14 and sum(p['count']for p in bank['bank_patterns'])==427872
 assert bank['endpoint_address_columns']==5600 and bank['nonzero_omission_repeat_control_columns']==5600 and bank['normalizer_factor_ceiling']==787
 oldbank=read(pred/'banks.json')['banks'];assert oldbank['normalizer_factor_bound']==599 and oldbank['max_chart_factors']<=400 and max(400,bank['max_new_chart_factors'])+99+100<=787
 literal={r:1500*n for r,n in H.items()}
 for r in (4,19,38,42):literal[r]=literal.get(r,0)+576000
 assert literal=={int(r):int(n)for r,n in inv['literal_histogram'].items()}=={int(r):5*n for r,n in price['cohort_candidate']['histogram'].items()}
 mass=sum(r*n for r,n in literal.items());calls=sum(literal.values());stock=bank['literal_stock'];assert mass==328524000 and calls==75078000 and stock*100-mass==612000
 J=300*(24*960+10*8223);K=2*5*300*((stock-1)+8223*100*787);coeff=300*(5*units+6*960)+J*16*(10000+1)**2+J*(stock+20)+calls*(8*10000+8)+calls*128*200**3+16*100**3+100*300+calls+K+1
 assert inv['status']=='PASS_COHORT_LITERAL_FIVE_STAGE_FINITE_INVOICE_AND_POSITIVE_CUTOFFS' and coeff==127531482262151501==int(inv['full_counted_primitive_coefficient']) and K==1951324377000==int(inv['extra_selector_calls'])==bank['selector_charge']
 assert coeff<2**80 and K<2**41 and inv['payload_bits']==cols['payload_prefix_bits']==98<104
 assert price['status']=='PASS_ACTUAL_P10_COMPOSED_WORD_TWO_MOMENTS_AND_47_CONSTRAINTS' and Q(price['kappa'])==Q(pin['kappa']) and price['source_word_sha256']==pin['final_word_sha256'] and price['local_rank_mass']==179464 and price['residual']==142624
 assert all(Q(price[k][1])<1 for k in ('first_interval','second_interval')) and all(Q(price[k][0])>1 for k in ('first_next','second_next'))
 assert len(price['ordinary_gaps'])==3 and all(min(map(Q,g.values()))>0 for g in price['ordinary_gaps']) and len(price['assembly']['strict_constraints'])==47 and min(map(Q,price['assembly']['strict_constraints'].values()))>0 and price['adjacent_rejected'] and price['full_fallback_retained']
 result=dict(status='PASS_SOURCE_BOUND_P10_PR320_PRESINK_THREE_QUADS_T300_CONDITIONAL_CONSTRUCTION',kappa=price['kappa'],predecessor_kappa=pin['base_kappa'],kappa_gain=str(Q(price['kappa'])-Q(pin['base_kappa'])),word_sha256=pin['final_word_sha256'],predecessor_word_sha256=pin['base_word_sha256'],source_regenerated=True,new_kernel_entries=3,new_entrance_rank=6,physical_replicas=300,literal_stock=stock,normalized_stock=658272,helper_assignments=12334500,new_frame_charts=1,changed_projector_charts=15,new_chart_factor_max=115,normalizer=787,finite_coefficient=coeff,selector_charge=K,payload_bits=98,scope=oldcert['scope'])
 receipts=['predecessor/verification.json','predecessor/certificate.json','predecessor/complex.json','predecessor/banks.json','kernel2/kernel2.json','LEGALITY.json','COLUMNS.json','BANK.json','PRICE.json','INVOICE.json','TILING.json']
 result['fresh_receipt_hashes']={n:sha(out/n)for n in receipts};(out/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS integrated PR320 presink three quads T300 '+price['kappa'],flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('output');finish(ap.parse_args().output)
