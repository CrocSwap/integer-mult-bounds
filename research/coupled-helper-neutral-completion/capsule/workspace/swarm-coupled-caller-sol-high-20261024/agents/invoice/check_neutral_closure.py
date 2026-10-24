#!/usr/bin/env python3
"""Hash-bound conditional mathematical conjunction; preserves scoped receipts.

The package master freshly reproduces component semantics first. This checker
then joins the immutable accepted inputs at their original relative paths.
No native, oracle or candidate evaluator is imported or rerun here.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import argparse,json


def need(v,why):
    if not v:raise ValueError(why)


def hist(x):return {int(k):v for k,v in x.items()if v}


def enc(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):enc(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [enc(v)for v in x]
    return x


def conjunction(root,manifest):
    need(manifest['schema']=='neutral-v16c-closure-inputs/1','closure manifest schema')
    rows={r['id']:r for r in manifest['rows']}
    need(len(rows)==len(manifest['rows']),'unique closure input identities')
    paths={};data={}
    for key,row in rows.items():
        p=(root/row['path']).resolve()
        need(p.is_relative_to(root)and p.is_file(),'relative regular closure input '+key)
        b=p.read_bytes();need(sha256(b).hexdigest()==row['sha256'],'changed closure input '+key)
        paths[key]=p
        if p.suffix=='.json':data[key]=json.loads(b)
    def digest(key):return rows[key]['sha256']
    L,W,J,P,F,I=(data[k]for k in ['local','whole','join','precision','funding','invoice'])
    B,FW=data['backward'],data['forward'];provider=data['provider_acceptance']
    predicates={}
    def gate(name,value):
        need(value,'closure premise failed: '+name);predicates[name]=True
    gate('exact_frozen_v16c_B_F',L['packet_sha256']=={
         'backward':digest('backward'),'forward':digest('forward')}
         and FW['backward_candidate_sha256']==digest('backward'))
    gate('accepted_local_all649_and11controls',
         L['status']=='PASS_COMPLETE_LOCAL_STANDARD_B_AND_F_WITH408POSITIVE_HELPERS'
         and len(L['controls'])==11 and all(c['rejected']for c in L['controls'])
         and all(x['independent_original_columns']==632 and x['arbitrary_owned_columns']==17
                 and x['owned_zero_outputs']==17 and x['positive_helpers']==408
                 for x in L['results'].values()))
    route=L['child_route_proof']
    gate('actual_paid_C8_and_new_positive_C8_routes',
         route['paid_D8_route_maps']==16 and route['newmode_target_alias_maps']==16
         and route['R_intertwining_of_coordinate_swap']is True
         and I['explicit_paid_child_axis_route_maps']==16
         and I['explicit_new_helper_axis_alias_maps']==16
         and I['paid_child_standard_axes']==list(range(8))
         and I['new_helper_canonical_axes']==list(range(8)))
    gate('same_accepted400_forward_aliases',L['aliases_sha256']==digest('aliases')
         and B['aliases_sha256']==digest('aliases'))
    consumed=provider['consumed_sha256']
    gate('reused_provider_exact_actual_bytes',
         provider['status']=='PASS_INDEPENDENT_COUPLED_PROVIDER_COMPONENT'
         and provider['candidate_head']=='3348fccea855082786d5f0fc5558b73d4974e745'
         and provider['all_original_inputs']==632 and provider['arbitrary_owned_inputs']==9
         and consumed['research/native-rank8-helper-provider/PROVIDER.json']==digest('provider')
         and consumed['research/native-rank8-helper-provider/WORD.json.gz']==digest('provider_word')
         and consumed['research/native-center-free-code/SOURCE-WORD.json.gz']==digest('source_word'))
    gate('all18_B_old_controller_exact',W['controller_sha256']==digest('controller')
         and W['physical_events_executed']=={'LOCAL':18,'QUERY_SHEAR':15,'IDLE':15,
             'ADD':90,'SIGNED_SWAP':20,'Q_POWER':4}
         and W['local_receipt_sha256']==digest('local')
         and W['plan_sha256']==digest('plan'))
    gate('whole_main_Laurent_and_eight_controls',
         W['status']=='PASS_EXACT_WHOLECALLER_AND_ALL10928_CANONICAL_TARGET_ROUTES'
         and W['laurent_rows']==32 and W['independent_ports_per_row']==112
         and W['finite_order_used_in_main_Laurent']is False
         and len(W['controls'])==8 and all(c['rejected']for c in W['controls']))
    gate('all30368_canonical_layout_maps',
         W['layout_fieldmaps']=={'main':7168,'helpers':14688,'idle':6720}
         and W['negativeQ_Xcentral_maps']==1792
         and W['total_new_normalizer_fieldmaps_including_X']==30368
         and P['global_target_layout_fieldmaps']==W['layout_fieldmaps']
         and P['total_new_normalizer_fieldmaps']==30368)
    gate('actual_global_integer_ID_join',
         J['status']=='PASS_ACTUAL_GLOBAL649_FIELD_ALPHA_RENAMING_AND418_OWNED'
         and J['global_packet_sha256']==digest('global_packet')
         and J['canonical_route_plan_sha256']==digest('plan')
         and J['wholecaller_receipt_sha256']==digest('whole')
         and J['actual_fields']==11346 and J['persistent_targets']==10928
         and J['private_fields']==418 and len(J['controls'])==3
         and all(c['rejected']for c in J['controls']))
    gate('owned418_and_distinct7344_helpers',
         W['ownership']['local_owned_fields']==306
         and W['ownership']['query_owned_fields']==112
         and W['ownership']['persistent_helper_fields']==7344
         and W['ownership']['all_helper_namespace_keys_distinct']is True
         and P['raw_total_private_reservation']==418)
    gate('actual_preRIGHT_events_LEFT_post_order',P['execution_order']==W['ordered_execution']
         and W['ordered_execution']==['all_main_preJ','RIGHT_program',
          'physical_events_with_helper_preJ_LOCAL_postJinverse_and_IDLEROUTES',
          'LEFT_program','negative_q_main_Xcentral','all_main_postJinverse'])
    paid,target=hist(I['histograms']['paid']),hist(I['histograms']['productive'])
    gate('all_four_complete_profiles_identical',paid==hist(F['paid'])==hist(W['complete_paid_profile'])==hist(P['paid'])
         and target==hist(F['targets'])==hist(W['productive_profile'])==hist(P['targets'])
         and sum(paid.values())==64260 and sum(target.values())==10928)
    gate('zero_economic_gain_exact_neutral_profile',I['signed_profile_identical_to_5398']is True
         and I['economic_profile_gain']==0 and F['economic_profile_gain']==0
         and I['raw_moment_delta_all_exponents']==0 and I['raw_ceiling_changed']is False)
    k,c,gap=map(Q,(F['kappa'],F['tested'],F['gap']))
    gate('exact_new_positive_endpoint_gap',k==Q('.003027288235')
         and c==Q('.003027288245') and gap==(c-k)/7==Q(1,700000000000)
         and k-Q('.00302728823')==Q(1,200000000000))
    gate('fresh_alpha_both_tails_completion_eta',
         all(F['predicates'].values()) and Q(F['alpha_upper'])<1-Q(F['reserve'])
         and Q(F['gamma_upper'])<Q(97,100) and Q(F['delta_upper'])<Q(97,100)
         and Q(F['reserve_slack'])>0 and Q(F['completion_slack'])>0)
    gate('strict_minimum_rounding_reserve',Q(F['strict_minimum_rounding_reserve'])==Q(1,1099511626752)
         and Q(F['reserve'])>Q(F['strict_minimum_rounding_reserve']))
    H,j=F['H'],F['j']
    gate('fresh_height_and_preceding_height_grid',H==38569300000000000 and j==55099
         and H==j*gap.denominator and (H+1)**1000<2**j
         and (gap.denominator*(j-1)+1)**1000>=2**(j-1))
    outer=F['outer'];strict=outer['strict'];functional=outer['functional']
    gate('all54_strict_and4_functional_outer_rows',len(strict)==54 and len(functional)==4
         and all(Q(x)>0 for x in strict.values())and all(Q(x)>0 for x in functional.values())
         and set(strict)==set(F['source_predicates']['strict'])
         and set(functional)==set(F['source_predicates']['functional']))
    be=Q(outer['parameters']['beta']);atom=Q(F['ordinary_BIT']['atom'])
    stock_gap=be-Q(functional['actual_new_BIT_stock_sublinear'])
    gate('ordinary_BIT_and_product_stock_spare_power',Q(F['ordinary_BIT']['admitted'])==Q('.0034')
         and Q(F['ordinary_BIT']['actual'])>Q('.0034')>c
         and stock_gap==be*atom>0 and be-2*atom>0)
    gate('precision_v3_exact_same_carrier_and_sources',
         P['status']=='PASS_SCOPED_V16C_PRECISION_STOCK_AND_FRESH_RAW_MAJORANTS'
         and P['input_manifest_sha256']==digest('precision_manifest')
         and P['carrier_H']==H and P['carrier_j']==j and Q(P['carrier_gap'])==gap
         and P['mathematical_application']['proof_sha256']==digest('precision_proof')
         and P['mathematical_application']['retained_five_assumptions_only']is True)
    for row in data['precision_manifest']['rows']:
        path=(root/row['path']).resolve()
        need(path.is_relative_to(root)and sha256(path.read_bytes()).hexdigest()==row['sha256'],
             'precision manifest input changed '+row['id'])
    pg={row['id']:row for row in data['precision_manifest']['rows']}
    gate('precision_and_join_use_exact_final_B_F_plan',
         pg['B']['sha256']==digest('backward') and pg['F']['sha256']==digest('forward')
         and pg['plan']['sha256']==digest('plan') and pg['funding']['sha256']==digest('funding'))
    raw=P['raw_global'];Iraw=sum(raw['operations'].values())+418+64260+10928+1
    R=64*146**3*Iraw**3+raw['scalar_tariff'];G=raw['scalar_tariff']+8*R
    gate('fresh_ordinary_physical_majorants_not_old_caps',
         raw['scalar_tariff']==3634556 and R==P['raw_physical_value_upper']
         and G==P['raw_G_upper'] and max(R,G,raw['dyadic_coefficient_height'])<2**128
         and P['expanded']['no_old_raw_or_expanded_caps_reused']is True)
    expanded=P['expanded']
    gate('fresh_constructive_F16_semantic_stock_bound',
         expanded['strictified_log_upper']==585757<1048576
         and expanded['D0']=='2^1048576' and expanded['M']==f'F16(2^{H})'
         and expanded['N']==f'2^{H}' and expanded['actual_counts_bound']=='W,P,U,O,R,G <= M'
         and expanded['recursion']=='F16(0)=D0; X_n=(n+1)*(D0+1)*(F16(n-1)+1); F16(n)=X_n^(16*(n+1)^2)')
    gate('accepted_written_source_specialization',
         digest('precision_proof')=='cda8f596f7854f42a228f757d5f8e68f6b2256a19c5ae3771fb40753cedc5b39'
         and all(P['mathematical_application'][name].startswith('PROVED')for name in
           ['ordinary_class_specialization','expanded_construction','precision_stock_tape','recovery_class']))
    gate('narrow_component_false_flags_preserved',L['complete_caller']is False
         and W['compiler_or_funding_admission']is False and J['funding_admitted']is False
         and P['complete_admission']is False and F['whole_scientific_admission']is False)
    return {'schema':'neutral-v16c-conditional-mathematical-conjunction/1',
            'status':'PASS_CONDITIONAL_MATHEMATICAL_KAPPA_CONJUNCTION',
            'premises':predicates,'premise_count':len(predicates),
            'input_bindings':manifest['rows'],'kappa':k,'tested':c,
            'gain_over_prior_comparison':k-Q('.00302728823'),
            'gain_type':'tiny compiler/outer headroom; zero recursive economic gain',
            'economic_profile_gain':0,'raw_ceiling_changed':False,
            'paid':paid,'targets':target,'paid_calls':64260,'productive_fields':10928,
            'H':H,'height_grid_j':j,'height_grid_preceding_fails':True,
            'kappa_grid_maximality_claimed':False,'kappa_next_grid_rejection_claimed':False,
            'ordinary_class_source_application':True,'fresh_precision_stock_source_application':True,
            'conditional_mathematical_application':True,
            'assumptions':['native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'],
            'carrier_vs_outer_growth':'N=2^H fixed before outer growth; D0 and F16(N) enter new finite constants/outer thresholds, never assumed below N^gap',
            'stock_spare_power':stock_gap,'component_flags_unchanged':True,
            'formal_kernel_acceptance':False,'independent_human_approval':False,
            'physical_Turing_tape_executed':False,'unconditional_multiplication_claim':False,
            'selected_record_changed':False,'final_registered_package_replay_still_required':True,
            'scope':'Exact frozen source/physical/wholecaller/invoice/numerical/ordinary/precision/stock conjunction '
                    'under exactly the five retained selected premises. See both bound written proofs. '
                    'Master must freshly reproduce component semantics before replaying this accepted-input conjunction.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();need(not a.output.exists(),'immutable aggregate output exists')
    result=conjunction(a.root.resolve(),json.loads(a.manifest.read_bytes()))
    a.output.write_text(json.dumps(enc(result),indent=2,sort_keys=True)+'\n')
    print(json.dumps(enc({k:result[k]for k in ['status','premise_count','kappa',
          'gain_over_prior_comparison','economic_profile_gain','conditional_mathematical_application']})))
