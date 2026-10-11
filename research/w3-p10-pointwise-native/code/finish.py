#!/usr/bin/env python3
"""Bind regenerated Design T/twins to complete native and complex receipts.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions must remain enabled; refusing optimization')
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,hashlib,json,struct
from materialize import check_bytes
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())

def finish(out):
    out=Path(out);pin=read(ROOT/'SOURCE.json');E=pin['expected'];src=ROOT/'vendor/predecessor';c=out/'candidate';b=out/'base'
    pv=read(out/'predecessor/verification.json');assert pv['inputs_unchanged'] and pv['manifest_sha256']==pin['predecessor']['manifest_sha256']==sha(src/'MANIFEST.json')
    required={'virtual','raw','bit','scalar','primes','banks','complex','math','finite'}
    assert set(pv['fresh_stages'])==required and len(pv['negative_controls'])==9
    assert Q(pv['kappa'])==Q(pin['base_kappa'])
    r=read(out/'source-regeneration/REGENERATION.json');assert r['status']=='PASS_TWO_BYTE_EXACT_PR325_BASE_REGENERATIONS' and r['rounds']==2 and len(r['negative_controls'])==11
    assert r['source_manifest_sha256']==pv['manifest_sha256'] and r['exporter_sha256']==sha(ROOT/'vendor/pr346/code/export_p10.py')
    for k in range(2):check_bytes(ROOT/'vendor/pr346/data/bit',out/'source-regeneration'/f'round{k}',r['files'])
    assert sha(b/'COHORT249-RECORDS.bin')==pin['source_parity_sha256']==sha(out/'source-regeneration/round1/249-records.bin')
    assert (b/'COHORT249-RECORDS.bin').read_bytes()==gzip.decompress((out/'predecessor/records.bin.gz').read_bytes())
    comp=read(out/'COMPACTION.json');assert comp['deleted_count']==480 and comp['active_helpers']==7620 and comp['inverse_event_relabeling_byte_exact']
    assert comp['original_final_word_sha256']==pin['upstream_final_word_sha256'] and comp['compacted_word_sha256']==pin['final_word_sha256']
    assert comp['copy_slot_before']==10020 and comp['copy_slot_after']==9540
    for p,h in comp['source_hashes'].items():assert sha(p)==h
    st=read(c/'249-states.json');ex=read(out/'EXPORT.json')
    assert st['n']==9540 and st['R']==7620 and st['v']==960 and st['h']==20
    assert sha(c/'COHORT249-RECORDS.bin')==st['record_sha256']==pin['final_word_sha256']
    assert ex['base_n']==10020 and ex['candidate_n']==9540 and ex['R']==7620 and len(ex['removed_physical_registers'])==480
    assert ex['all_used_frames']==E['frames'] and ex['new_used_frames']==320
    for p,h in ex['input_hashes'].items():assert sha(p)==h
    H=Counter();adds=units=copies=erases=records=0
    for op,a,bb,cc,f,z in struct.iter_unpack('<6i',(c/'COHORT249-RECORDS.bin').read_bytes()):
        records+=1
        if op==0 and f:H[f]+=1
        elif op==1:adds+=1;units+=abs(cc)
        elif op==2:H[z]+=1;copies+=1
        elif op==3:erases+=1
    assert adds==E['adds'] and units==E['units'] and records==E['records'] and copies==erases==20
    assert sum(H.values())==E['paid_calls'] and sum(r*n for r,n in H.items())==E['rank_mass']
    legal=read(out/'LEGALITY.json');cols=read(out/'COLUMNS.json');bank=read(out/'BANK.json');price=read(out/'PRICE.json');inv=read(out/'INVOICE.json');fp=read(out/'FRAME-PRIMES.json');refl=read(out/'REFLECTED-LEDGERS.json')
    assert legal['status']=='PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and legal['all_final_frames_pass'] and legal['copies']==legal['erasures']==20
    assert legal['common_frame_ADDs']==adds and legal['rank_mass']==E['rank_mass'] and Counter(dict(legal['paid_histogram']))==H
    assert cols['status']=='PASS_GENERIC_FIVE_STAGE_FORMAL_COLUMNS_AND_COMPUTED_PREFIX' and cols['formal_columns_checked']==11460 and cols['independent_dirty_registers']==7620
    assert cols['local_scalar_additions']==adds and cols['fresh_center_copies']==100 and cols['copied_center_original_source_immutable']
    assert len(cols['negative_controls'])==6 and all(x['rejected']for x in cols['negative_controls'])
    assert H==Counter({int(k):v for k,v in cols['local_raw_H']})==Counter({int(k):v for k,v in price['local_histogram'].items()})
    assert refl['status']=='PASS_BOTH_CHRONOLOGICAL_REFLECTED_FRAME_LEDGERS_AND_PAID_HISTOGRAMS' and refl['non_nested_control_rejected']
    assert refl['source_word_sha256']==pin['final_word_sha256'] and refl['frame_sha256']==sha(c/'frames.json') and refl['state_sha256']==sha(c/'249-states.json')
    assert bank['status']=='PASS_GENERIC_EXACT_CHARTS_ACTUAL_BANK_ALLOCATION' and bank['all_new_ordinary_annihilators_full_rank'] and bank['deleted_inert_roles']==0
    assert bank['actual_helper_roles']==7620 and bank['actual_role_replica_stage_assignments']==11430000 and bank['physical_replicas']==300
    for key in ('literal_stock','normalized_stock','banks_per_stage','changed_projector_charts','max_new_chart_factors','selector_charge','normalizer_factor_ceiling'):
        assert bank[key]==E[key],key
    assert bank['new_exact_charts']==320 and bank['changed_helper_endpoints']==480
    geometry_files=['candidate/COHORT249-RECORDS.bin','candidate/COHORT249-FRAMES.json','charts/COMBINED-CHART-AUDIT.json','charts/COMBINED-CHARTS.json','bank/BANK-REVIEW.json','bank/BANK-CHARTS.json']
    assert bank['geometry_input_hashes']=={str((out/n).resolve()):sha(out/n)for n in geometry_files}
    assert fp['input_sha256']==sha(c/'frames.json') and fp['zero_row_control_rejected'] and fp['frames']==E['frames'] and fp['basis_witnesses']==2*E['frames']
    assert fp['status']=='PASS_EXACT_FRAME_AND_ANNIHILATOR_MINORS_FOR_ALL_PRIMES_ABOVE_2_POWER_80' and 0<int(fp['max_abs_minor'])<2**80
    assert price['source_word_sha256']==pin['final_word_sha256'] and Q(price['kappa'])==Q(pin['native_kappa'])
    assert price['complex_binds'] and price['adjacent_rejected'] and price['full_fallback_retained']
    assert all(Q(price[k][1])<1 for k in ('first_interval','second_interval')) and all(Q(price[k][0])>1 for k in ('first_next','second_next'))
    assert len(price['assembly']['strict_constraints'])==47 and min(map(Q,price['assembly']['strict_constraints'].values()))>0
    cv=read(out/'complex-reserve/VERIFICATION.json');binding=price['complex_supplier']['source_binding']
    assert cv['status']=='PASS_PORTABLE_REGENERATED_PR348_P10_COMPLEX_SUPPLIER' and cv['inputs_unchanged'] and cv['producer_regeneration_claim'] is True
    assert cv['manifest_sha256']==binding['manifest_sha256']==pin['complex_reserve']['manifest_sha256']==sha(ROOT/'vendor/complex-reserve/MANIFEST.json')
    assert Q(cv['complex_coarse'])==Q(price['complex_saving'])==Q(pin['complex_reserve']['coarse'])
    assert binding['adapter_sha256']==sha(ROOT/'code/future_supplier.py') and binding['all_supplier_stages_fresh'] and binding['declarative_source'] and binding['producer_regeneration_claim']
    for name,h in binding['receipt_hashes'].items():assert sha(out/'complex-reserve'/name)==h
    ref=read(out/'REFINEMENT.json');assert ref['status']=='PASS_P10_PRIME_THRESHOLD_FULL_INVOICE_TWO_MOMENTS_FINITE_BOOTSTRAP_OUTER47'
    assert Q(ref['native_kappa'])==Q(price['kappa'])<Q(ref['kappa'])==Q(pin['kappa'])
    assert ref['source']['word_sha256']==pin['final_word_sha256'] and len(ref['negative_controls'])==12
    for name,h in ref['source']['receipt_hashes'].items():assert sha(out/name)==h
    for name,h in ref['source']['external_receipt_hashes'].items():assert sha(name)==h
    for name,h in ref['source']['engine_hashes'].items():assert sha((src if name in ('moment.py','base_two_moment.py','outer.py')else ROOT/'code')/name)==h
    assert ref['prime_threshold']['Q']==2**127-1 and ref['prime_threshold']['lucas_lehmer_residue']==0 and ref['prime_threshold']['growing_prime_regime_retained']
    assert ref['bootstrap']['levels']==E['bootstrap_levels'] and ref['ordinary_saving']['complex_binds']
    assert len(ref['assembly']['strict_constraints'])==47 and min(map(Q,ref['assembly']['strict_constraints'].values()))>0
    assert int(inv['full_counted_primitive_coefficient'])==ref['complete_literal_invoice']['coefficient']==E['coefficient'] and inv['payload_bits']==88
    names=['source-regeneration/REGENERATION.json','COMPACTION.json','EXPORT.json','ROLE-MAP.json','LEGALITY.json','COLUMNS.json','REFLECTED-LEDGERS.json','TILING.json','BANK.json','FRAME-PRIMES.json','PRICE.json','INVOICE.json','REFINEMENT.json']
    names+=['predecessor/'+n for n in ('verification.json','certificate.json','complex.json','primes.json','banks.json','math.json')]
    names+=['complex-reserve/'+n for n in binding['receipt_hashes']]
    names+=geometry_files
    result=dict(status='PASS_SOURCE_BOUND_W3_P10_COMPLETE_NATIVE_CONDITIONAL_CONSTRUCTION',kappa=pin['kappa'],native_kappa=pin['native_kappa'],word_sha256=pin['final_word_sha256'],source_regenerated=True,complex_declarative_source=True,complex_producer_regeneration_claim=True,physical_replicas=300,literal_stock=bank['literal_stock'],normalized_stock=bank['normalized_stock'],helper_assignments=bank['actual_role_replica_stage_assignments'],new_frame_charts=320,changed_projector_charts=1776,new_chart_factor_max=bank['max_new_chart_factors'],normalizer=787,finite_coefficient=E['coefficient'],selector_charge=bank['selector_charge'],payload_bits=88,bootstrap_levels=E['bootstrap_levels'],scope=ref['scope'],fresh_receipt_hashes={n:sha(out/n)for n in names})
    (out/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS integrated source-bound Design T/twins '+pin['kappa'],flush=True)

if __name__=='__main__':finish(sys.argv[1])
