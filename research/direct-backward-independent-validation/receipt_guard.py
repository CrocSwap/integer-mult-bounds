"""Validate complete fresh coverage and compare frozen semantic receipts."""
import copy
import hashlib
import json
from fractions import Fraction as Q

def require(ok,message):
    if not ok:raise ValueError(message)

def read(root,name):return json.loads((root/name).read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def stable(value):
    # These exact fields record execution time/resource samples, never science.
    if isinstance(value,dict):return {k:stable(v) for k,v in value.items() if k not in ('seconds','runtime','max_rss_kib')}
    if isinstance(value,list):return [stable(v) for v in value]
    return value

def caller_stable(value):
    value=copy.deepcopy(value)
    # Absolute locations of three already hash-authenticated old receipts move
    # to the private scratch tree. Every other field remains compared exactly.
    for row in value['supplier_reuse']['receipts'].values():
        row['path']=row['path'].replace('\\','/').split('/')[-1]
    return stable(value)

def validate(root,claims,binding):
    c=claims['candidates'][0];head=c['head'];k=Q(c['kappa'])
    a=read(root,'agents/caller/RESULT.json')
    require(a['status']=='PASS_SOURCE_BOUND_DIRECT_CALLER_WITH_RETAINED_SIGNED_HELPER_NORMALIZERS' and a['head']==head,'Incomplete caller/head')
    require(a['checker_sha256']==binding['digests']['capsule/agents/caller/check.py'],'Caller checker binding')
    require(a['controller_sha256']==binding['digests']['capsule/repository/research/kappa-backward-controller-20261023/CONTROLLER.json'],'Caller controller binding')
    require(a['full_laurent_replay']=={'rows':32,'formal_generators':34,'central_finite_order_used':False,'all_coefficients_exact':True,'signed_swaps_expanded_to_three_ADD':True},'Incomplete literal Laurent endpoint')
    require(a['wrapper_sites']==[{'source_index':0,'stage':0,'pair':0},{'source_index':99,'stage':32,'pair':15}],'Wrong physical wrapper sites')
    require(a['native']=={'dimension':265,'stages':[0,32],'ports':112,'contacts':896,'columns':114688,'new_positive_jobs':0},'Incomplete physical phase contacts')
    require(len(a['controls'])==9 and all(a['controls'].values()),'Missing caller/helper/phase controls')
    s=a['supplier_reuse'];require(s['word_payload_sha256']=='2aee5e997df99726fc763e510d9cb69fbe4f86114dc8d2cd33ad26c6c462a21d' and s['supplier_science_rerun'] is False,'Wrong supplier reuse')
    require(s['owned_arbitrary_inputs']==17 and s['persistent_independent_inputs']==624 and len(s['helpers'])==400,'Incomplete arbitrary supplier/helper scope')
    require(s['helper_profile']=={'9':318,'8':47,'7':7,'4':28},'Wrong positive helper profile')
    h=a['helper_normalization'];require(h['adapter_order_preserved'] and h['applied_only_after_autonomous_completed_endpoint'] and h['all_400_raw_helper_maps_unchanged_by_main_wrapper'] and h['no_helper_rank_only_shortcut'] and h['charged_in_invoice_review'],'Unproved helper normalization')
    require(h['two_sided_nine_axis_record_bound']==342 and h['retained_per_group_allowance']==1000 and h['existing_helper_route_groups_per_full']==816,'Helper normalizer funding mismatch')
    require(a['ownership']['distinct_helper_owners']==7200 and a['ownership']['distinct_owned_bank_positions']==306 and a['ownership']['full_calls']==18,'Incomplete caller ownership')
    require(caller_stable(a)==caller_stable(read(root,'expected/caller-RESULT.json')),'Fresh caller semantic output differs from frozen reviewed coverage')
    contacts=read(root,'agents/caller/PHYSICAL-CONTACTS.json');require(contacts==read(root,'expected/PHYSICAL-CONTACTS.json'),'Fresh phase contact records differ')
    inv=read(root,'agents/numeric/INVOICE-v2.json');f=read(root,'agents/numeric/FUNDING-v1.json')
    require(inv==read(root,'expected/INVOICE-v2.json'),'Fresh complete invoice differs from reviewed census')
    require(inv['candidate']['head']==head and inv['no_candidate_code_imported'] is True,'Invoice source identity')
    require(inv['totals']=={'paid':64116,'productive':10784,'paid_mass':237838,'productive_mass':238590,'rank_surplus':752},'Incomplete complete bill')
    require(len(inv['chronology'])==162 and len(inv['helper_normalizers'])==400 and len(inv['controls'])==10,'Incomplete invoice chronology/helpers/controls')
    require(inv['controller']['raw_owned']==306 and inv['local']['scalar_units']==158744,'Wrong raw controller/local specialization')
    ordinary=inv['ordinary'];require(ordinary['raw_upper']==181586816 and ordinary['raw_upper']<ordinary['raw_budget']==10**9 and ordinary['local_units_upper']<ordinary['local_budget']==10**7 and ordinary['wrapper_allowance']==459648,'Unfunded ordinary bill')
    require(ordinary['signed_swap_intermediate_norm_factor']==2 and ordinary['source_route_terms']['two_helper_wrappers']==816,'Uncharged helper/swap prefixes')
    require(f['status']=='PASS_INDEPENDENT_EXACT_ARITHMETIC_ONLY' and f['candidate']['head']==head and Q(f['kappa'])==k and Q(f['tested'])==Q('.00302728824'),'Wrong fresh funding target')
    require(f['invoice_sha256']==sha(root/'agents/numeric/INVOICE-v2.json'),'Fresh funding/invoice mismatch')
    require(f['engine_sha256']==binding['digests']['capsule/agents/numeric/exact_engine.py'] and f['reviewer_sha256']==binding['digests']['capsule/agents/numeric/review5398.py'],'Funding engine binding')
    require(Q(f['gain_over_selected'])==k-Q('.0030217758') and Q(f['gain_over_independent_5377'])==k-Q('.00302235') and Q(f['gain_over_5387'])==k-Q('.003026674765') and Q(f['gain_over_5392'])==k-Q('.00302725'),'Incorrect derived gain claim')
    require(f['endpoint_funded'] is False and f['no_candidate_code_imported'] and f['no_expanded_word_materialized'],'Arithmetic lane scope changed')
    require(Q(f['reserve'])==Q('1/1000000000000') and Q(f['reserve_strict_slack'])>0 and Q(f['normalized_paid_upper'])<1 and Q(f['completion_strict_slack'])>0,'Unfunded completion/reserve')
    require(Q(f['ratios']['alpha'][1])<1-Q(f['reserve']) and all(Q(f['ratios'][n][1])<Q(97,100) for n in ('gamma','delta')),'Moment/tail bound failed')
    require(all(f['capacity'].values()) and len(f['capacity'])==10 and f['j']==55099 and f['H']==38569300000000000,'Incomplete finite compiler/capacity')
    outer=f['outer'];require(len(outer['strict_checks'])==54 and len(outer['functional_checks'])==4 and all(Q(x)>0 for x in [*outer['strict_checks'].values(),*outer['functional_checks'].values()]),'Incomplete strict/functional outer ledger')
    require(set(outer['strict_checks'])==set(f['source_predicates']['strict']) and set(outer['functional_checks'])==set(f['source_predicates']['functional']),'Outer source predicate coverage mismatch')
    require(len(f['controls'])==11 and all(f['controls'].values()) and len(f['changed_profile_controls'])==5 and all(f['changed_profile_controls'].values()),'Missing funding controls')
    r=f['root'];require(Q(r['strict_signs'][0][0])>0>Q(r['strict_signs'][1][1]) and Q(r['derivative_upper'])<0 and Q(r['remaining_moment_upper'])<0,'Fixed-profile root ceiling incomplete')
    require(stable(f)==stable(read(root,'expected/FUNDING-v1.json')),'Fresh funding semantic output differs from reviewed coverage')
    p=read(root,'agents/precision/CHECK.json')
    require(p['status']=='PASS_SCOPED_DIRECT_CALLER_PRECISION_STOCK_COMPILER' and p['candidate_head']==head,'Incomplete precision/head')
    require(p['source_manifest_sha256']==binding['digests']['capsule/agents/precision/SOURCES.json'],'Precision source manifest binding')
    require(p['source_bindings']>=30 and p['raw_LOCAL_owned_banks']==306 and p['local_owned_banks']==17 and p['full_backward_calls']==18,'Incomplete fresh bank specialization')
    require(p['backward_scalar_allowance']==158744 and p['backward_scalar_height']==29183 and p['signed_swap_three_ADD_prefix_sup_norms']==[2,2,1],'Wrong transient scalar envelope')
    require(p['expanded']['unit_log_bound']==225309 and p['expanded']['numerical_majorant_materialized'] is False and p['expanded']['raw_cap_used_as_expanded_stock'] is False,'Wrong expanded all-n bound')
    require(p['precision']['C1']==1 and p['precision']['intermediate_swap_factor_paid'] is True and p['stock']['all_suspended_owners_distinct'] is True and p['stock']['owned_productive_credit'] is False,'Incomplete precision/stock applicability')
    require(p['compiler']['H']==f['H'] and p['compiler']['j']==f['j'] and Q(p['compiler']['gap'])==Q(f['gap']) and Q(p['compiler']['reserve'])==Q(f['reserve']),'Precision/compiler numerical mismatch')
    require(p['controls']['count']==7 and len(p['controls']['rejected'])==7 and len(set(p['controls']['rejected']))==7,'Missing precision controls')
    require(p['assumptions']==f['assumptions']==[x['id'] for x in claims['assumptions']],'Changed retained five-premise set')
    require(stable(p)==stable(read(root,'expected/precision-CHECK.json')),'Fresh precision semantic output differs from reviewed all-n coverage')
    return {'candidate_pr':5398,'candidate_head':head,'kappa':str(k),'paid':64116,'productive':10784,'retained_arbitrary_inputs':624,'local_arbitrary_owned_inputs':17,'raw_owned_bank_positions':306,'productive_helper_owners':7200,'outer_predicates':{'strict':54,'functional':4},'fresh_gates':['literal_caller_and_phase_helper_normalization','complete_invoice_and_exact_funding','fresh_all_n_precision_stock_compiler'],'reused_supplier_review':claims['reused_review'],'assumptions':claims['assumptions']}
