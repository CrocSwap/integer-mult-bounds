#!/usr/bin/env python3
"""Cross-bind fresh frozen PR317, shared kernels, actual word, banks and exact invoice.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
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
def census(path):
 hist=Counter();adds=units=copies=records=0
 for op,a,b,c,f,z in struct.iter_unpack('<6i',Path(path).read_bytes()):
  records+=1
  if op==0 and f:hist[f]+=1
  elif op==1:adds+=1;units+=abs(c)
  elif op==2:hist[z]+=1;copies+=1
 return hist,adds,units,copies,records
def finish(out):
 out=Path(out);pin=read(ROOT/'SOURCE.json');pred=out/'predecessor';src=ROOT/'vendor/pr317';base=read(pred/'VERIFICATION.json');oldcert=read(pred/'CERTIFICATE.json');candidate=out/'candidate';old=pred/'candidate'
 bank=read(out/'BANK.json');price=read(out/'PRICE.json');inv=read(out/'INVOICE.json');cols=read(out/'COLUMNS.json');legal=read(out/'LEGALITY.json');st=read(candidate/'249-states.json');oldst=read(old/'249-states.json');higher=read(candidate/'HIGHER-KERNEL-STAGE.json');selection=read(ROOT/'stages/shared-kernel-selection.json')
 assert base['status']==oldcert['status']=='PASS_SOURCE_BOUND_P10_KERNEL_TARGET_PLATEAU_RESTORE_REORDER_CONDITIONAL_CONSTRUCTION' and base['inputs_unchanged'] and oldcert['source_regenerated']
 assert base['manifest_sha256']==sha(src/'MANIFEST.json')==pin['pr317']['manifest_sha256']
 assert base['word_sha256']==oldcert['word_sha256']==sha(old/'COHORT249-RECORDS.bin')==pin['base_word_sha256']
 assert Q(base['kappa'])==Q(oldcert['kappa'])==Q(pin['base_kappa'])<Q(pin['kappa'])
 for name,digest in oldcert['fresh_receipt_hashes'].items():assert sha(pred/name)==digest
 expected_stages={'immutable-pr315-source','export-source','kernel-stage','target-prefix-stage','plateau-ascent-stage','early-restoration-stage','reorder-stage','compile-legality','compile-columns','compile-banks','compile-changed-charts','compile-invoice','legality','columns','tiling','bank-frames-and-assignment','changed-charts','geometry-admission','price','finite-invoice','complete-admission'}
 assert {row['stage']for row in base['fresh_stages']}==expected_stages
 # Original source construction and its complete complex supplier are regenerated.
 original=read(pred/'baseline/verification.json');complex=read(pred/'baseline/complex.json')
 assert original['status']=='PASS_IMMUTABLE_PARITY_FUSED_P10_FIVE_STAGE_BANKED_CONSTRUCTION' and original['inputs_unchanged'] and len(original['negative_controls'])==9
 assert complex['status']=='PASS_FRESH_COMPLEX_LABEL_SCALAR_SPLICE_PRECISION' and complex['precision_guard']['retained_row_coefficient']==20161
 assert read(pred/'baseline/primes.json')['all_remaining_factors_below_2_power_80']
 # The new stage is appended to the complete predecessor; its receipts stay intact.
 inherited=['EXTRA-TARGET-STAGE.json','PLATEAU-STAGE.json','restore.json','REORDER-STAGE.json']+[p.name for p in old.iterdir()if p.name.startswith('kernel') and p.is_file()]
 for name in inherited:assert sha(old/name)==sha(candidate/name)
 assert sha(old/'COHORT249-FRAMES.json')==sha(candidate/'COHORT249-FRAMES.json')
 assert st['final']==oldst['final'] and st['regs']==oldst['regs'] and st['n']==10150 and st['v']==960 and st['h']==20
 changed={int(r)for r in st['initial']if st['initial'][r]!=oldst['initial'][r]}
 assert changed=={f['pivot']for f in selection['families']} and len(changed)==90
 assert higher['status']=='PASS_GEN4_PER_ENTRY_CUT_KERNEL_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS'
 assert higher['selected_entries']==higher['rank_drop']==pin['new_kernel_entries']==90
 assert higher['input_raw_sha256']==pin['base_word_sha256']==selection['input_raw_sha256']
 assert higher['selection_sha256']==sha(ROOT/'stages/shared-kernel-selection.json')==sha(candidate/'HIGHER-KERNEL-SELECTION.json')
 assert higher['transform_sha256']==sha(ROOT/'code/higher_kernel_transform.py') and higher['wrapper_sha256']==sha(ROOT/'code/shared_kernel_stage.py')
 assert higher['exact_checker_sha256']==sha(src/'vendor/pr315/bitword/references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py')
 assert higher['both_reflected_ledgers'] and higher['unchanged_copy_lifetimes'] and higher['unchanged_data_input_output_and_dirty_output_frames']
 proof=higher['proof'];assert proof['selected_helpers']==196 and proof['prefix_relations_checked']==90 and proof['prefix_target_comparisons']==86400 and proof['total_entrance_rank']==90
 assert proof['selected_helpers_untouched_before_own_cut'] and proof['no_prefix_response_outside_targets_and_own_helper'] and proof['all_old_surviving_scalar_and_copy_events_in_order'] and proof['source_context_preserved']
 for k in ('forward','inverse'):assert higher['scalar'][k]['all_sources_and_dirty_restored'] and higher['scalar'][k]['formal_columns']==10150
 assert len(higher['scalar']['controls'])==2 and all(not c['all_sources_and_dirty_restored']for c in higher['scalar']['controls'])
 assert higher['source_span_checked']==376244 and higher['source_span_violations']==0
 digest=sha(candidate/'COHORT249-RECORDS.bin');assert digest==pin['final_word_sha256']==st['record_sha256']==higher['output_raw_sha256']==higher['standalone_final_raw_sha256']==price['source_word_sha256']
 assert Q(price['kappa'])==Q(pin['kappa']) and price['status']=='PASS_ACTUAL_P10_COMPOSED_WORD_TWO_MOMENTS_AND_47_CONSTRAINTS'
 assert cols['formal_columns_checked']==12070 and cols['independent_dirty_registers']==8230 and cols['fresh_center_copies']==100 and cols['copied_center_original_source_immutable']
 assert len(cols['negative_controls'])==6 and all(c['rejected']for c in cols['negative_controls'])
 assert legal['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and legal['all_final_frames_pass'] and legal['restored_helper_endpoints']==240 and legal['selected_helpers']==630 and legal['copies']==legal['erasures']==20
 assert bank['status']=='PASS_GENERIC_EXACT_CHARTS_ACTUAL_BANK_ALLOCATION' and bank['all_new_ordinary_annihilators_full_rank']
 assert bank['new_exact_charts']==390 and bank['changed_projector_charts']==3937 and bank['max_new_chart_factors']==139 and bank['changed_helper_endpoints']==870 and bank['actual_helper_roles']==8230 and bank['actual_role_replica_stage_assignments']==2469000
 assert bank['normalized_stock']==132084 and bank['literal_stock']==660420 and bank['banks_per_stage']==86004 and bank['new_endpoint_saved_rank']==870
 assert bank['residual_families']=={'3':310,'4':960,'19':630,'20':6330}
 hist,adds,units,copies,records=census(candidate/'COHORT249-RECORDS.bin');oldhist,oldadds,oldunits,oldcopies,oldrecords=census(old/'COHORT249-RECORDS.bin')
 assert records==384591 and copies==20 and adds==335264==cols['local_scalar_additions']==legal['common_frame_ADDs']==price['adds'] and units==337184==price['unit_adds']
 assert dict(hist)==dict((int(r),n)for r,n in cols['local_raw_H'])=={int(r):n for r,n in price['local_histogram'].items()}
 delta={r:hist[r]-oldhist[r]for r in hist.keys()|oldhist.keys()if hist[r]!=oldhist[r]}
 assert delta=={int(r):n for r,n in selection['expected_local_delta'].items()}=={int(r):n for r,n in higher['local_histogram_delta'].items()}
 assert sum(hist.values())==48138 and sum(r*n for r,n in hist.items())==180180==legal['rank_mass']==price['local_rank_mass']
 assert sum(r*n for r,n in oldhist.items())-sum(r*n for r,n in hist.items())==90 and adds-oldadds==units-oldunits==24
 literal={r:300*n for r,n in hist.items()}
 for r in (4,19,38,42):literal[r]=literal.get(r,0)+115200
 assert literal=={int(r):int(n)for r,n in inv['literal_histogram'].items()}=={int(r):5*n for r,n in price['cohort_candidate']['histogram'].items()}
 mass=sum(r*n for r,n in literal.items());calls=sum(literal.values());stock=bank['literal_stock'];assert mass==65919600 and calls==14902200 and 100*stock-mass==122400
 J=60*(24*960+10*8230);K=2*5*60*((stock-1)+8230*100*787)
 coeff=60*(5*units+6*960)+J*16*(10000+1)**2+J*(stock+20)+calls*(8*10000+8)+calls*128*200**3+16*100**3+100*60+calls+K+1
 assert inv['status']=='PASS_COHORT_LITERAL_FIVE_STAGE_FINITE_INVOICE_AND_POSITIVE_CUTOFFS' and coeff==25380271118580401==int(inv['full_counted_primitive_coefficient']) and K==389016851400==int(inv['extra_selector_calls'])==bank['selector_charge']
 assert coeff<2**80 and K<2**40 and inv['payload_bits']==cols['payload_prefix_bits']==94<104
 assert all(Q(price[k][1])<1 for k in ('first_interval','second_interval')) and all(Q(price[k][0])>1 for k in ('first_next','second_next'))
 assert len(price['ordinary_gaps'])==3 and all(min(map(Q,g.values()))>0 for g in price['ordinary_gaps']) and len(price['assembly']['strict_constraints'])==47 and min(map(Q,price['assembly']['strict_constraints'].values()))>0 and price['adjacent_rejected'] and price['full_fallback_retained']
 result=dict(status='PASS_SOURCE_BOUND_P10_SHARED90_CONDITIONAL_CONSTRUCTION',kappa=price['kappa'],predecessor_kappa=pin['base_kappa'],kappa_gain=str(Q(price['kappa'])-Q(pin['base_kappa'])),word_sha256=digest,predecessor_word_sha256=pin['base_word_sha256'],source_regenerated=True,new_kernel_entries=90,total_kernel_entries=630,literal_stock=stock,normalized_stock=132084,helper_assignments=2469000,new_frame_charts=390,changed_projector_charts=3937,new_chart_factor_max=139,normalizer=787,finite_coefficient=coeff,selector_charge=K,payload_bits=94,scope=oldcert['scope'])
 receipts=['predecessor/VERIFICATION.json','predecessor/CERTIFICATE.json','predecessor/baseline/complex.json','LEGALITY.json','COLUMNS.json','BANK.json','PRICE.json','INVOICE.json','TILING.json','candidate/HIGHER-KERNEL-STAGE.json']
 result['fresh_receipt_hashes']={n:sha(out/n)for n in receipts};(out/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS integrated shared90',price['kappa'],flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('output');a=ap.parse_args();finish(a.output)
