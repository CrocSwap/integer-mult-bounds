"""Source-specific receipt consumer only; no scientific engine imports.

The new reviewer-policy proposal is frozen for root/auditor review. This tool
cannot grant public or selected authority. Original #5391 library unchanged.
"""
from pathlib import Path
import json
import oracle as o

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
WORK=BASE.parents[1]
LIB_SHA='51a9d378c36ad9cb3f7f0cd9db48cae7d43d971bbd6cb028dd9bf6aa60cd8468'
HEAD='329b2ff35d2994b11abbb59f770d12da75c494ac'
CANON='1ec1119972c9aefe42525172d07b332fcff81cb4'
PINS={
 'physical':('01-physical/PHYSICAL-RECEIPT.json','d5a561a8d7aab680f469e7929622d882bcd1a05179feb584a588cba80577ea4b'),
 'erratum':('01-physical/SCOPE-ERRATUM-RECEIPT.json','25ad329e4ed0be000e431216f0c55d04a69068c9803010031a0a5f6637cb6bf4'),
 'invoice':('04-funding/INVOICE-v1.json','5263880a5a88ec356879aba7452f13be817ee82469bd00166b28d35e82233016'),
 'closure':('03-closure/CLOSURE-v1.json','4959ea0a58ac51cd6fea46ce0123bcbf74135b716593607031621fcd6bf2471f'),
 'funding':('04-funding/FUNDING-v2.json','5173909380120154069f14518aa8d56e88823183d8e2dca864f48d30d1fbd5dc'),
 'cold':('09-cold/VALIDATION.json','5460f7652a34a369d65a3ddaea51745d1f59ecdec41c1866afd3d7f20fbddfc2'),
 'cold_correction':('09-cold/BOUNDED-REGISTERED-RUN-CORRECTION.json','412e83fef8c56f8bc8349e5525fd7bfe0c6958690c224fbed6d114804691af10'),
}

def main():
 o._require(o.digest((HERE/'oracle.py').read_bytes())==LIB_SHA,'PUBLISHED_LIBRARY_CHANGED')
 dest=HERE/'case-v1';o._require(not dest.exists(),'IMMUTABLE_CASE_EXISTS')
 artifacts={};origins={};deps={};data={}
 def add(path,expected=None):
  path=Path(path);raw=path.read_bytes();sha=o.digest(raw)
  o._require(not expected or sha==expected,'PRODUCER_PIN_MISMATCH:'+str(path))
  artifacts[sha]=raw;origins[sha]=str(path);return sha
 for name,(relative,sha) in PINS.items():
  deps[name]=add(BASE/relative,sha);data[name]=json.loads(artifacts[sha])
 p,e,i,c,f,v,x=(data[k] for k in ['physical','erratum','invoice','closure','funding','cold','cold_correction'])
 o._require(p['head']==i['candidate']['head']==c['candidate']['head']==f['candidate']['head']==v['candidate']['head']==HEAD,'HEAD_MISMATCH')
 o._require(e['original_joint_receipt_sha256']==deps['physical'] and e['positive_universal_endpoint_gate_unchanged'] is True and e['actual_specialization_nonzero_claim_established'] is False and e['surjectivity_claim_established'] is False and e['reverse_zero_premise_required'] is False,'ERRATUM_SCOPE_MISSING')
 cov=p['coverage'];o._require(cov['all_entry_columns']==641 and cov['independent_retained']==624 and cov['arbitrary_owned']==17 and cov['all_owned_return_zero'] is True and cov['paid_transpose_classes']==2847 and cov['native_transpose_classes']==180,'PHYSICAL_COVERAGE_GAP')
 o._require(c['ordinary']['raw_local_owned_banks']==i['controller']['raw_owned_banks']==306 and c['ordinary']['raw_global_upper']==i['ordinary']['raw_units_upper']==361098496,'STALE_STOCK_OR_CHARGE')
 o._require(c['new_candidate_specific_assumptions']==[] and c['retained_assumptions']==list(o.ASSUMPTIONS) and c['expanded_constants']['old_equal_N_implies_old_constants'] is False,'CLOSURE_DOMAIN_GAP')
 o._require(c['actual_word_error_proof']['runtime_zero_test'] is False and c['tape_and_eventual_threshold']['old_C0_or_p0_reused'] is False,'PRECISION_TAPE_GAP')
 o._require(f['invoice']['sha256']==deps['invoice'] and f['precision_stock_gate']['sha256']==deps['closure'] and f['endpoint_funded'] is True and f['complete_bill_ready'] is True,'FUNDING_NOT_BOUND')
 o._require(f['paid']==i['histograms']['paid'] and f['targets']==i['histograms']['productive'] and f['N']==c['expanded_constants']['N'],'FUNDING_PROFILE_HEIGHT_MISMATCH')
 inventory=f['source_predicate_inventory'];o._require(set(inventory['strict_keys'])==set(f['outer']['strict_checks']) and set(inventory['functional_keys'])==set(f['outer']['functional_checks']),'PREDICATE_DOMAIN_MISMATCH')
 for name,sha in p['receipts'].items():add(BASE/'01-physical'/name,sha)
 for relative,sha in c['dependencies_sha256'].items():add(WORK/relative,sha)
 for path,sha in f['closure_dependencies_sha256'].items():add(path,sha)
 for name,sha in e['bound_original_files'].items():add(BASE/'01-physical'/name,sha)
 add(BASE/'01-physical/SCOPE-ERRATUM.md',e['erratum_markdown_sha256'])
 rawsha=add(BASE/'09-cold'/x['raw_receipt_path'],x['raw_receipt_sha256']);raw=json.loads(artifacts[rawsha])
 o._require(raw['capsule_manifest_sha256']==x['incorrect_recorded_value']==deps['invoice'] and x['correct_effective_value']==x['capsule_manifest_pre_sha256']==x['capsule_manifest_post_sha256']==v['source_provenance']['closed_manifest_sha256'],'COLD_CORRECTION_NOT_EXPLICIT')
 o._require(x['source_changed'] is False and x['execution_repeated'] is False and raw['exit']==0 and raw['resource_stop'] is None,'COLD_EXECUTION_GAP')
 deps['raw_cold']=rawsha
 manifest=BASE/'09-cold/capsule-5392-v2/IMMUTABLE-MANIFEST.json'
 if not manifest.exists():manifest=BASE/'09-cold/capsule-5392-v2/MANIFEST.json'
 deps['effective_cold_manifest']=add(manifest,x['correct_effective_value'])
 sidecar={'schema':'explicit-effective-cold-binding/v1','raw_receipt_sha256':rawsha,'correction_sha256':deps['cold_correction'],'raw_field':'capsule_manifest_sha256','unchanged_raw_wrong_value':raw['capsule_manifest_sha256'],'effective_value':x['correct_effective_value'],'validation_sha256':deps['cold'],'raw_receipt_modified':False}
 sr=o.encode(sidecar);deps['cold_sidecar']=o.digest(sr);artifacts[deps['cold_sidecar']]=sr;origins[deps['cold_sidecar']]='explicit derived sidecar, preserves raw receipt'
 wordsha=add(BASE/'source-capsule/research/native-transpose-owned/WORD.json.gz',p['word_sha256']);deps['word']=wordsha
 deps['root_manifest']=add(BASE/'source-capsule/ROOT-MANIFEST.json',p['root_manifest_sha256'])
 deps['controller']=add(i['authentication']['canonical']['research/joint-helper-lattice/CONTROLLER.json']['path'],i['authentication']['canonical']['research/joint-helper-lattice/CONTROLLER.json']['sha256'])
 profile={'paid':i['histograms']['paid'],'productive':i['histograms']['productive'],'paid_jobs':i['totals']['paid'],'productive_jobs':i['totals']['productive'],'excluded_productive_credit':{'aliases':0,'copies':0,'surrendered':0}}
 o._require(profile['paid_jobs']==64116 and profile['productive_jobs']==10784,'PROFILE_COUNTS')
 model={'id':f['model'],'parameters':f['config']['tuple'],'theorem_evidence_sha256':deps['closure']}
 candidate={'schema':'source-bound-price-candidate/v1','candidate_id':'aliromman-pr5392-329b2ff-actual-complete-case-v1','scientific_head':HEAD,'canonical_comparison_base':CANON,'attribution':[v['credit'],'Unmodified oracle #5391 by Chris R / Clear1nsight with substantial OpenAI Codex assistance'],'assumptions':list(o.ASSUMPTIONS),'source_dependencies':deps,'literal_witness_sha256':wordsha,'model':model,'profile':profile,'planes':{},'receipts':{},'requested_label':'FUNDED_CONDITIONAL'}
 entries={
 'paid_productive':[('complete_paid',profile['paid'],'proved',deps['invoice']),('independent_productive',profile['productive'],'proved',deps['invoice'])],
 'ordinary':[('scalar',159320,'constructively_upper_bounded',deps['invoice']),('route',10312000,'constructively_upper_bounded',deps['invoice']),('raw_controller',361098496,'constructively_upper_bounded',deps['invoice'])],
 'ownership_stock':[('fresh_banks',306,'constructively_upper_bounded',deps['closure']),('stock_product',c['stocks'],'constructively_upper_bounded',deps['closure']),('scope_corrected_endpoint',{'physical':deps['physical'],'required_erratum':deps['erratum'],'physical_reverse_nonzero_claim':False},'proved',deps['erratum'])],
 'precision_tape':[('expanded_constants',c['expanded_constants'],'constructively_upper_bounded',deps['closure']),('actual_error',c['actual_word_error_proof'],'constructively_upper_bounded',deps['closure']),('fresh_tapes_threshold',c['tape_and_eventual_threshold'],'constructively_upper_bounded',deps['closure'])],
 'compiler_reserves':[('funded_tuple',f['config'],'proved',deps['funding']),('completion_capacity',f['capacity'],'proved',deps['funding'])],
 'bit_outer':[('strong_bit_stock',c['stocks'],'constructively_upper_bounded',deps['closure']),('exact_outer',f['outer'],'proved',deps['funding'])]}
 for plane,rows in entries.items():
  candidate['planes'][plane]=[{'id':name,'value_or_symbol':value,'unit':'source elementary scalar/route units' if plane=='ordinary' else 'source finite-template obligation','state':state,'evidence_sha256':[evidence],'dependency_hashes':[deps['invoice'],deps['physical'],deps['erratum'],deps['closure'],deps['funding']],'invalidation_conditions':['changed exact head, word, phase, invoice, scope correction, 306-bank allocation, compiler tuple or source domain']} for name,value,state,evidence in rows]
 payload=o.digest(o.encode(o.scientific_payload(candidate)))
 policy={'candidate_id':candidate['candidate_id'],'scientific_payload_sha256':payload,'scientific_head':HEAD,'canonical_comparison_base':CANON,'source_dependencies':deps,'model_id':model['id'],'parameter_domain':[model['parameters']],'charge_inventory':{plane:[r[0] for r in rows] for plane,rows in entries.items()},'receipt_sha256':{},'outer_predicate_ids':{'strict':inventory['strict_keys'],'functional':inventory['functional_keys']},'arithmetic_check_ids':list(f['capacity']),'optimization_scope':'One exact independently reviewed #5392 word/profile and certified compiler point; no global optimum.','review_status':'PROPOSED_FOR_ROOT_AUDITOR_REVIEW_NOT_PUBLIC_AUTHORITY','authority_basis':'Root instruction pins independent01+erratum/04invoice/03closure/04funding/09cold+correction. No candidate-authored PASS authority.'}
 for role,evidence in [('physical',[deps['physical'],deps['erratum']]),('census',[deps['invoice']]),('closure',[deps['closure']]),('arithmetic',[deps['funding']])]:
  receipt={'schema':'source-bound-price-receipt/v1','role':role,'independent':True,'scientific_payload_sha256':payload,'scientific_head':HEAD,'profile_sha256':o.profile_hash(profile),'source_dependencies':deps,'coverage':list(o.COVERAGE[role]),'open_obligations':[],'evidence_sha256':evidence}
  if role=='physical':receipt['scope_correction']={'required_sha256':deps['erratum'],'formal_nonempty_rows_are_not_physical_nonzero_or_surjectivity':True,'positive_universal_endpoint_unchanged':True}
  if role=='arithmetic':receipt.update({'invoice_receipt_sha256':candidate['receipts']['census'],'closure_receipt_sha256':candidate['receipts']['closure'],'model':model,'endpoint_funded':True,'funded_kappa':f['kappa'],'tested_saving':f['tested'],'raw_root_interval':f['root']['bracket'],'root_sign_intervals':f['root']['strict_signs'],'compiler_domain':model['parameters'],'strict_slacks':f['outer']['strict_checks'],'functional_slacks':f['outer']['functional_checks'],'checks':f['capacity'],'same_five_assumptions':f['assumptions']==list(o.ASSUMPTIONS)})
  rr=o.encode(receipt);sha=o.digest(rr);artifacts[sha]=rr;origins[sha]='normalized consumer receipt; raw evidence pinned separately';candidate['receipts'][role]=policy['receipt_sha256'][role]=sha
 result=o.evaluate(o.encode(candidate),artifacts,policy)
 dest.mkdir();(dest/'artifacts').mkdir()
 for sha,rawbytes in artifacts.items():(dest/'artifacts'/sha).write_bytes(rawbytes)
 for name,obj in [('candidate',candidate),('policy',policy),('result',result),('origins',origins),('cold-sidecar',sidecar)]: (dest/(name+'.json')).write_bytes(o.encode(obj))
 print(json.dumps({'label':result['label'],'kappa':result['funded_kappa'],'artifacts':len(artifacts),'policy_public_authority':False},indent=2))

if __name__=='__main__':main()
