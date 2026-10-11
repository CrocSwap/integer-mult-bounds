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
    comp=read(out/'COMPACTION.json');assert len(comp['deleted_dormant_staged'])==480 and comp['active_helpers']==7610 and comp['inverse_event_relabeling_byte_exact']
    assert comp['source_word_sha256']==pin['upstream_final_word_sha256'] and comp['compacted_word_sha256']==pin['source_compacted_word_sha256']
    assert comp['copy_slots']==[10020,10010,9530] and len(comp['sink_roles_original'])==10
    for p,h in comp['source_hashes'].items():assert sha(p)==h
    sr=read(out/'staged-regeneration/REGENERATION.json');ss=pin['staged_source']
    assert sr['status']=='PASS_REGENERATED_PR329_FOUR_STAGES_MATCH_PR354_EXACT_BYTES' and sr['stages']==ss['stages']
    assert sr['source329_manifest_sha256']==ss['pr329_manifest'] and sr['source354_manifest_sha256']==ss['pr354_manifest'] and sr['exporter_sha256']==sha(ROOT/'code/staged_export.py')
    assert set(sr['files'])=={tag+'/'+name for tag in ('parity','staged') for name in ('249-records.bin','249-states.json','frames.json')}
    for tag,snapshot in [('parity','00-parity'),('staged','04-sink')]:
        for name in ('249-records.bin','249-states.json','frames.json'):
            old=ROOT/'vendor/pr354/data'/tag/(name+'.gz');new=out/'staged-regeneration'/snapshot/name;row=sr['files'][tag+'/'+name]
            assert sha(old)==row['pinned_compressed_sha256'] and sha(new)==row['expanded_sha256']==row['regenerated_sha256'] and new.read_bytes()==gzip.decompress(old.read_bytes())
            if tag=='parity':assert new.read_bytes()==(out/'source-regeneration/round1'/name).read_bytes()
    role=read(out/'staged-regeneration/SOURCE-ROLE-MAP.json');assert sr['source_role_map_sha256']==sha(out/'staged-regeneration/SOURCE-ROLE-MAP.json')
    assert role['removed_original_positions']==comp['sink_roles_original'] and role['stages']==ss['stages']
    assert {k:v for k,v in comp['original_to_compact'].items() if int(k)!=10020}==read(out/'ROLE-MAP.json')
    assert read(out/'PARITY-CONTROL.json')['word_sha256']==ss['parity_control_word'] and sha(out/'design/TT-control/249-records.bin')==ss['parity_control_word']
    ds=read(out/'DESIGN-SCALAR.json');assert ds['status']=='PASS_STRICT_PR354_SCALAR_REPLAY' and ds['word_sha256']==pin['upstream_final_word_sha256']
    assert E['candidate_files']=={name:sha(c/name) for name in E['candidate_files']}
    st=read(c/'249-states.json');ex=read(out/'ORIGINAL-EXPORT.json');tp=pin['signed_twin_transform']
    assert st['n']==9530 and st['R']==7610 and st['v']==960 and st['h']==20
    assert sha(c/'COHORT249-RECORDS.bin')==st['record_sha256']==pin['final_word_sha256']
    assert ex['base_n']==10020 and ex['candidate_n']==9530 and ex['R']==7610 and len(ex['removed_physical_registers'])==490
    assert ex['all_used_frames']==tp['source_frames']==13885 and ex['new_used_frames']==tp['source_new_frames']==1000
    assert ex['candidate_word_sha256']==pin['source_compacted_word_sha256']==sha(out/'candidate-source/COHORT249-RECORDS.bin')
    for p,h in ex['input_hashes'].items():assert sha(p)==h
    assert set(tp['files'])=={'source','intermediate','final'}
    for folder,key in [('candidate-source','source'),('candidate-signed18','intermediate'),('candidate','final')]:
        paths=list((out/folder).rglob('*'));assert all(not p.is_symlink()for p in paths)
        actual={p.relative_to(out/folder).as_posix():sha(p)for p in paths if p.is_file()}
        assert actual==tp['files'][key] and len(actual)==7,folder
    for name,h in tp['code_sha256'].items():assert sha(ROOT/'code'/name)==h
    tr=read(out/'candidate-signed18-REGENERATION.json');tr2=read(out/'candidate-REGENERATION.json')
    assert tr['status']=='PASS_EXACT_GENERALIZED_TWIN_REGENERATION_NOT_FULL_ADMISSION'
    assert tr['source_word_sha256']==pin['source_compacted_word_sha256'] and tr['candidate_word_sha256']==pin['intermediate_word_sha256']
    assert tr['source_state_sha256']==sha(out/'candidate-source/249-states.json') and tr['source_frames_sha256']==sha(out/'candidate-source/frames.json') and tr['source_base_frames_sha256']==sha(b/'frames.json')
    assert len(tr['chosen'])==18 and len(tr['removed_zero_frame_additions'])==72 and len(set(tr['removed_zero_frame_additions']))==72
    assert tr['records_before']==tp['source_records']==406312 and tr['records_after']==tp['intermediate_records']==406294 and tr['new_frames']==2 and tr['entrance_rank_saved']==18
    assert tr2['status']=='PASS_EXACT_TWO_FURTHER_SIGNED_TWINS_REGENERATION_NOT_FULL_ADMISSION'
    assert tr2['source_word_sha256']==pin['intermediate_word_sha256'] and tr2['candidate_word_sha256']==pin['final_word_sha256']
    assert tr2['source_files']==tp['files']['intermediate'] and tr2['candidate_files']==tp['files']['final']
    assert len(tr2['chosen'])==2 and len(tr2['removed_zero_frame_additions'])==8 and len(set(tr2['removed_zero_frame_additions']))==8
    assert tr2['records_before']==tp['intermediate_records'] and tr2['records_after']==E['records']==406292 and tr2['new_frames']==0 and tr2['entrance_rank_saved']==2
    chosen=tr['chosen']+tr2['chosen']
    assert len(chosen)==tp['selected_twins']==20 and len({r['a']for r in chosen}|{r['b']for r in chosen})==40
    assert tr['new_frames']+tr2['new_frames']==tp['new_frames']==2
    assert len(tr['removed_zero_frame_additions'])+len(tr2['removed_zero_frame_additions'])==tp['removed_zero_frame_additions']==80
    zi=read(out/'INTEGER-AUDIT.json')
    assert zi['status']=='PASS_EXACT_INTEGER_PR354_SIGNED_TWENTY_TWIN_OPERATOR_EQUIVALENCE' and zi['all_output_rows_equal'] is True
    assert zi['source_sha256']==pin['source_compacted_word_sha256'] and zi['candidate_sha256']==pin['final_word_sha256']
    assert zi['independent_integer_input_columns']==9530 and zi['output_rows_compared']==9531
    assert {(x['entry_category'],x['name'])for x in zi['mutation_controls']}=={(cat,name)for cat in (44,46)for name in ('missing_entry','missing_exit','wrong_entry_sign')} and len(zi['mutation_controls'])==6
    assert all(x['rejected'] is True and x['changed_rows']>0 for x in zi['mutation_controls'])
    assert len(read(c/'frames.json')['frames'])==E['frames'] and len(read(c/'COHORT249-FRAMES.json'))==E['new_frame_charts']
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
    assert cols['status']=='PASS_GENERIC_FIVE_STAGE_FORMAL_COLUMNS_AND_COMPUTED_PREFIX' and cols['formal_columns_checked']==11450 and cols['independent_dirty_registers']==7610
    assert cols['local_scalar_additions']==adds and cols['fresh_center_copies']==100 and cols['copied_center_original_source_immutable']
    assert len(cols['negative_controls'])==6 and all(x['rejected']for x in cols['negative_controls'])
    assert H==Counter({int(k):v for k,v in cols['local_raw_H']})==Counter({int(k):v for k,v in price['local_histogram'].items()})
    assert refl['status']=='PASS_BOTH_CHRONOLOGICAL_REFLECTED_FRAME_LEDGERS_AND_PAID_HISTOGRAMS' and refl['non_nested_control_rejected']
    assert refl['source_word_sha256']==pin['final_word_sha256'] and refl['frame_sha256']==sha(c/'frames.json') and refl['state_sha256']==sha(c/'249-states.json')
    assert len(refl['ledgers'])==2 and {q['reverse_complement'] for q in refl['ledgers']}=={False,True}
    for q in refl['ledgers']:
        assert q['records']==records and q['rank_mass']==E['rank_mass'] and q['copies']==20 and q['all_endpoints_exact'] and q['common_frame_adds'] and q['copy_original_source_immutable']
        assert Counter({int(k):v for k,v in q['paid_histogram'].items()})==H and q['operations']['1']==adds
    assert bank['status']=='PASS_GENERIC_EXACT_CHARTS_ACTUAL_BANK_ALLOCATION' and bank['all_new_ordinary_annihilators_full_rank'] and bank['deleted_inert_roles']==0
    assert bank['actual_helper_roles']==7610 and bank['actual_role_replica_stage_assignments']==11415000 and bank['physical_replicas']==300
    for key in ('literal_stock','normalized_stock','banks_per_stage','changed_projector_charts','max_new_chart_factors','selector_charge','normalizer_factor_ceiling'):
        assert bank[key]==E[key],key
    assert bank['new_exact_charts']==E['new_frame_charts']==1002 and bank['changed_helper_endpoints']==E['changed_helper_endpoints']==740
    geometry_files=['candidate/COHORT249-RECORDS.bin','candidate/COHORT249-FRAMES.json','charts/COMBINED-CHART-AUDIT.json','charts/COMBINED-CHARTS.json','bank/BANK-REVIEW.json','bank/BANK-CHARTS.json']
    assert bank['geometry_input_hashes']=={str((out/n).resolve()):sha(out/n)for n in geometry_files}
    assert fp['input_sha256']==sha(c/'frames.json') and fp['zero_row_control_rejected'] and fp['frames']==E['frames'] and fp['basis_witnesses']==2*E['frames']
    assert fp['status']=='PASS_EXACT_FRAME_AND_ANNIHILATOR_MINORS_FOR_ALL_PRIMES_ABOVE_2_POWER_80' and 0<int(fp['max_abs_minor'])<2**80
    assert price['source_word_sha256']==pin['final_word_sha256'] and Q(price['kappa'])==Q(pin['native_kappa']) and Q(price['bit_root'])==Q(E['bit_coarse'])
    assert price['complex_binds'] is pin['complex_binds'] is False and price['adjacent_rejected'] and price['full_fallback_retained']
    assert all(Q(price[k][1])<1 for k in ('first_interval','second_interval')) and all(Q(price[k][0])>1 for k in ('first_next','second_next'))
    assert len(price['assembly']['strict_constraints'])==47 and min(map(Q,price['assembly']['strict_constraints'].values()))>0
    cv=read(out/'complex-reserve/VERIFICATION.json');binding=price['complex_supplier']['source_binding']
    assert cv['status']==pin['complex_reserve']['verification_status'] and cv['inputs_unchanged'] and cv['producer_regeneration_claim'] is False
    assert cv['candidate_sha256']==pin['complex_reserve']['candidate_sha256']
    assert cv['lean_data_regeneration_claim'] is True and cv['upstream_lean_rebuilt'] is False and cv['parity_corrected_complete_invoice'] is True
    assert cv['manifest_sha256']==binding['manifest_sha256']==pin['complex_reserve']['manifest_sha256']==sha(ROOT/'vendor/complex-reserve/MANIFEST.json')
    assert Q(cv['complex_coarse'])==Q(price['complex_saving'])==Q(pin['complex_reserve']['coarse'])
    assert binding['adapter_sha256']==sha(ROOT/'code/future_supplier.py') and binding['all_supplier_stages_fresh'] and binding['declarative_source'] and binding['producer_regeneration_claim'] is False
    assert binding['lean_data_regeneration_claim'] is True and binding['upstream_lean_rebuilt'] is False and binding['parity_corrected_complete_invoice'] is True
    for name,h in binding['receipt_hashes'].items():assert sha(out/'complex-reserve'/name)==h
    ref=read(out/'REFINEMENT.json');assert ref['status']=='PASS_P10_PRIME_THRESHOLD_FULL_INVOICE_TWO_MOMENTS_FINITE_BOOTSTRAP_OUTER47'
    assert Q(ref['native_kappa'])==Q(price['kappa'])<Q(ref['kappa'])==Q(pin['kappa'])
    assert ref['source']['word_sha256']==pin['final_word_sha256'] and len(ref['negative_controls'])==12
    for name,h in ref['source']['receipt_hashes'].items():assert sha(out/name)==h
    for name,h in ref['source']['external_receipt_hashes'].items():assert sha(name)==h
    for name,h in ref['source']['engine_hashes'].items():assert sha((src if name in ('moment.py','base_two_moment.py','outer.py')else ROOT/'code')/name)==h
    assert ref['prime_threshold']['Q']==2**127-1 and ref['prime_threshold']['lucas_lehmer_residue']==0 and ref['prime_threshold']['growing_prime_regime_retained']
    assert ref['bootstrap']['levels']==E['bootstrap_levels'] and ref['ordinary_saving']['complex_binds'] is pin['complex_binds'] is False
    assert len(ref['assembly']['strict_constraints'])==47 and min(map(Q,ref['assembly']['strict_constraints'].values()))>0
    assert int(inv['full_counted_primitive_coefficient'])==ref['complete_literal_invoice']['coefficient']==E['coefficient'] and inv['payload_bits']==88
    names=['source-regeneration/REGENERATION.json','COMPACTION.json','ORIGINAL-EXPORT.json','candidate-signed18-REGENERATION.json','candidate-REGENERATION.json','INTEGER-AUDIT.json','ROLE-MAP.json','LEGALITY.json','COLUMNS.json','REFLECTED-LEDGERS.json','TILING.json','BANK.json','FRAME-PRIMES.json','PRICE.json','INVOICE.json','REFINEMENT.json']
    names+=['predecessor/'+n for n in ('verification.json','certificate.json','complex.json','primes.json','banks.json','math.json')]
    names+=['complex-reserve/'+n for n in binding['receipt_hashes']]
    names+=geometry_files
    names+=[folder+'/'+name for folder,key in [('candidate-source','source'),('candidate-signed18','intermediate'),('candidate','final')]for name in tp['files'][key]]
    names+=['staged-regeneration/REGENERATION.json','staged-regeneration/SOURCE-ROLE-MAP.json','DESIGN-SCALAR.json','PARITY-CONTROL.json']
    result=dict(status='PASS_SOURCE_BOUND_W3_STAGED354_E8_SIGNED20_COMPLETE_NATIVE_CONDITIONAL_CONSTRUCTION',kappa=pin['kappa'],native_kappa=pin['native_kappa'],word_sha256=pin['final_word_sha256'],source_regenerated=True,source_compacted_word_sha256=pin['source_compacted_word_sha256'],intermediate_word_sha256=pin['intermediate_word_sha256'],signed_twin_source_regenerated=True,integer_local_scalar_operator_preserved=True,integer_comparison_ignores_moves=True,integer_input_columns=9530,integer_output_rows=9531,signed_twin_count=20,complex_declarative_source=True,complex_producer_regeneration_claim=False,complex_lean_data_regeneration_claim=True,complex_upstream_lean_rebuilt=False,complex_parity_corrected_invoice=True,physical_replicas=300,literal_stock=bank['literal_stock'],normalized_stock=bank['normalized_stock'],helper_assignments=bank['actual_role_replica_stage_assignments'],new_frame_charts=E['new_frame_charts'],changed_projector_charts=E['changed_projector_charts'],new_chart_factor_max=bank['max_new_chart_factors'],normalizer=787,finite_coefficient=E['coefficient'],selector_charge=bank['selector_charge'],payload_bits=88,bootstrap_levels=E['bootstrap_levels'],scope=ref['scope'],fresh_receipt_hashes={n:sha(out/n)for n in names})
    (out/'CERTIFICATE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS integrated source-bound Design T/twins '+pin['kappa'],flush=True)

if __name__=='__main__':finish(sys.argv[1])
