#!/usr/bin/env python3
"""Cross-bind fresh PR315 source, all transformed words, native charts, invoices and exact assembly."""
import sys
if not __debug__:raise SystemExit('assertions required')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,json,hashlib,struct
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(Path(p).read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def finish(out):
 out=Path(out);pin=read(ROOT/'SOURCE.json');base=read(out/'baseline/verification.json');complex=read(out/'baseline/complex.json');bank=read(out/'BANK.json');price=read(out/'PRICE.json');inv=read(out/'INVOICE.json');cols=read(out/'COLUMNS.json');legal=read(out/'LEGALITY.json');candidate=out/'candidate';st=read(candidate/'249-states.json')
 assert base['status']=='PASS_IMMUTABLE_PARITY_FUSED_P10_FIVE_STAGE_BANKED_CONSTRUCTION' and base['inputs_unchanged']
 assert base['manifest_sha256']==sha(ROOT/'vendor/pr315/MANIFEST.json')==pin['pr315']['manifest_sha256']
 assert set(base['fresh_stages'])=={'virtual','raw','bit','scalar','primes','banks','complex','math','finite'} and len(base['negative_controls'])==9
 assert complex['status']=='PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION' and complex['precision_guard']['retained_row_coefficient']==20161
 assert read(out/'baseline/primes.json')['all_remaining_factors_below_2_power_80']
 kernel=read(candidate/'kernel.json');target=read(candidate/'EXTRA-TARGET-STAGE.json');plateau=read(candidate/'PLATEAU-STAGE.json');restore=read(candidate/'restore.json');reorder=read(candidate/'REORDER-STAGE.json')
 assert kernel['status']=='PASS_GEN4_PER_ENTRY_CUT_KERNEL_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS' and kernel['selected_entries']==kernel['rank_drop']==540
 assert kernel['both_reflected_ledgers'] and kernel['unchanged_copy_lifetimes']
 assert kernel['input_raw_sha256']==pin['base_word_sha256'] and kernel['output_raw_sha256']==target['input_record_sha256']
 assert target['status']=='PASS_LITERAL_F2_TARGET_PREFIX_STAGE' and target['groups']==target['dependents']==120
 assert target['forward'] and target['inverse'] and target['dirty_restoration'] and target['omitted_setup_rejected'] and target['both_reflected_local_ledgers']
 assert target['output_record_sha256']==plateau['input_record_sha256']
 assert plateau['status']=='PASS_ACTUAL_SIGNED_WORD_PRESERVING_PLATEAU_ASCENT' and plateau['retimed_adds']==480 and plateau['signed_scalar_and_copy_word_unchanged'] and plateau['forward'] and plateau['inverse'] and plateau['both_reflected_local_ledgers']
 assert plateau['output_record_sha256']==restore['input_raw_sha256']
 assert restore['status']=='PASS_GEN5_EARLY_RESTORATION_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS' and restore['selected']==restore['changed_helper_endpoints']==restore['endpoint_rank_saving']==240 and restore['both_reflected_ledgers'] and restore['unchanged_copy_lifetimes']
 for row in (kernel,restore):
  for k in ('forward','inverse'):assert row['scalar'][k]['all_sources_and_dirty_restored'] and row['scalar'][k]['formal_columns']==10150
  assert all(not c['all_sources_and_dirty_restored'] for c in row['scalar']['controls'])
 assert restore['output_raw_sha256']==reorder['input_word_sha256']
 assert reorder['status']=='PASS_REORDER_STAGE_REDERIVED_COMMUTING_RELOCATIONS' and reorder['exact_rank_product_screen'] and reorder['integer_replay_identical'] and reorder['omission_control_rejected'] and reorder['fixed_point'] and reorder['output_word_sha256']==pin['final_word_sha256']
 digest=sha(candidate/'COHORT249-RECORDS.bin');assert digest==pin['final_word_sha256']==st['record_sha256']==price['source_word_sha256']
 assert Q(price['kappa'])==Q(pin['kappa']) and price['status']=='PASS_ACTUAL_P10_COMPOSED_WORD_TWO_MOMENTS_AND_47_CONSTRAINTS'
 assert cols['formal_columns_checked']==12070 and cols['independent_dirty_registers']==8230 and cols['fresh_center_copies']==100 and cols['copied_center_original_source_immutable']
 assert len(cols['negative_controls'])==6 and all(c['rejected']for c in cols['negative_controls'])
 assert legal['all_final_frames_pass'] and legal['restored_helper_endpoints']==240 and legal['copies']==legal['erasures']==20
 assert bank['new_exact_charts']==390 and bank['changed_helper_endpoints']==780 and bank['actual_helper_roles']==8230 and bank['actual_role_replica_stage_assignments']==2469000
 assert bank['normalized_stock']==132138 and bank['literal_stock']==660690 and bank['banks_per_stage']==86058 and bank['new_endpoint_saved_rank']==780
 hist=Counter();adds=units=copies=0
 for op,a,b,c,f,z in struct.iter_unpack('<6i',(candidate/'COHORT249-RECORDS.bin').read_bytes()):
  if op==0 and f:hist[f]+=1
  elif op==1:adds+=1;units+=abs(c)
  elif op==2:hist[z]+=1;copies+=1
 assert copies==20 and adds==cols['local_scalar_additions']==legal['common_frame_ADDs']==price['adds'] and units==price['unit_adds']
 assert dict(hist)==dict((int(r),n)for r,n in cols['local_raw_H'])=={int(r):n for r,n in price['local_histogram'].items()}
 assert sum(r*n for r,n in hist.items())==legal['rank_mass']==price['local_rank_mass']
 literal={r:300*n for r,n in hist.items()}
 for r in (4,19,38,42):literal[r]=literal.get(r,0)+115200
 assert literal=={int(r):int(n)for r,n in inv['literal_histogram'].items()}=={int(r):5*n for r,n in price['cohort_candidate']['histogram'].items()}
 mass=sum(r*n for r,n in literal.items());calls=sum(literal.values());stock=bank['literal_stock'];assert 100*stock-mass==122400
 J=60*(24*960+10*8230);K=2*5*60*((stock-1)+8230*100*787)
 coeff=60*(5*units+6*960)+J*16*(10000+1)**2+J*(stock+20)+calls*(8*10000+8)+calls*128*200**3+16*100**3+100*60+calls+K+1
 assert inv['status']=='PASS_COHORT_LITERAL_FIVE_STAGE_FINITE_INVOICE_AND_POSITIVE_CUTOFFS' and coeff==int(inv['full_counted_primitive_coefficient']) and K==int(inv['extra_selector_calls'])==bank['selector_charge']
 assert coeff<2**80 and K<2**40 and inv['payload_bits']==cols['payload_prefix_bits']<104
 assert all(Q(price[k][1])<1 for k in ('first_interval','second_interval')) and all(Q(price[k][0])>1 for k in ('first_next','second_next'))
 assert len(price['ordinary_gaps'])==3 and all(min(map(Q,g.values()))>0 for g in price['ordinary_gaps']) and len(price['assembly']['strict_constraints'])==47 and min(map(Q,price['assembly']['strict_constraints'].values()))>0 and price['adjacent_rejected'] and price['full_fallback_retained']
 result=dict(status='PASS_SOURCE_BOUND_P10_KERNEL_TARGET_PLATEAU_RESTORE_REORDER_CONDITIONAL_CONSTRUCTION',kappa=price['kappa'],word_sha256=digest,source_regenerated=True,kernels=540,target_groups=120,plateau_adds=480,restored_endpoints=240,reorder_relocations=reorder['relocated_adds'],literal_stock=stock,normalized_stock=132138,helper_assignments=2469000,new_frame_charts=390,changed_projector_charts=bank['changed_projector_charts'],new_chart_factor_max=bank['max_new_chart_factors'],normalizer=787,finite_coefficient=coeff,selector_charge=K,payload_bits=cols['payload_prefix_bits'],scope='Conditional on inherited all-size compiler, weighted charts, restored rows, selectors, routing, prime supply, complex dirty lifting, precision/recovery and analytic interfaces. Characteristic-two transforms preserve parity words; actual signed coefficients and finite prefix bounds are recomputed. No unconditional multiplication theorem, new Lean build or runtime benchmark is claimed.')
 receipts=['baseline/verification.json','baseline/complex.json','baseline/primes.json','baseline/finite.json','LEGALITY.json','COLUMNS.json','BANK.json','PRICE.json','INVOICE.json','TILING.json','candidate/kernel.json','candidate/EXTRA-TARGET-STAGE.json','candidate/PLATEAU-STAGE.json','candidate/restore.json','candidate/REORDER-STAGE.json']
 result['fresh_receipt_hashes']={n:sha(out/n)for n in receipts};(out/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS integrated p10',price['kappa'],flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('output');a=ap.parse_args();finish(a.output)
