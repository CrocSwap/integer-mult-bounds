#!/usr/bin/env python3
"""Join fresh #5387 physical/template gates to its independent funded arithmetic."""
from pathlib import Path
from hashlib import sha256
import json
from exact_engine import need,ASSUMPTIONS
from bind_and_check import checked_bytes
H=Path(__file__).resolve().parent;W=H.parent;ROOT=H.parents[2]
HEAD='b1ab650d36f59e5be682a813145b7c67e219e341';BASE='1ec1119972c9aefe42525172d07b332fcff81cb4'
CAP=W/'09-capsule-cold/capsule-5387-v1';MANIFEST='b0b7eaeef8895264f33e86d87c1bf63fba495d6ac2f50e1414ee3eae775a1594'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def bound(p,h):need(sha(p)==h,'dependency changed '+str(p));return json.loads(p.read_bytes())
def run():
    out=H/'5387-receipt-v2.json';need(not out.exists(),'immutable 5387 receipt-v2 exists')
    r=bound(H/'5387-receipt-v1.json','f077be8f5f4543f0677ecb9ce7a1d31370e2dc04d58744519720384e3bd54585')
    m=bound(CAP/'IMMUTABLE-MANIFEST.json',MANIFEST)
    for row in m['rows']:checked_bytes(row,(CAP/row['capsule_path']).read_bytes())
    need(sha(H/'exact_engine.py')==r['engine_sha256'] and sha(H/'bind_5387.py')==r['binding_runner_sha256'],'frozen independent arithmetic executable changed')
    ph=W/'01-physical/5387-fresh/PHYSICAL-RECEIPT.json';pr=bound(ph,'a0a76015ae99a4bbaaa188a718fac6ef2925aa19fa9224d9986a00bec27c16cd')
    cl=W/'03-precision-stock/CLOSURE-5387-v1.json';cr=bound(cl,'2e90da356fdf32ad35dfe9bd8f7c4567e12e4fdf4453595c09f6bc6370e6cee3')
    need(pr['status']=='PASS_BOUNDED_FRESH_INDEPENDENT_PHYSICAL_5387_EIGHT_RELATIONS' and pr['candidate_head']==HEAD and pr['manifest_sha256']==MANIFEST,'5387 fresh physical gate mismatch')
    need(cr['status']=='PASS_SAME_PREMISE_CONSTRUCTIVE_FINITE_TEMPLATE_SPECIALIZATION' and cr['candidate']['head']==HEAD and cr['candidate']['canonical_base']==BASE,'5387 fresh template gate mismatch')
    need(pr['word_sha256']==cr['candidate']['word_sha256'] and pr['word_sha256']=='6412632c28e265597fb088087048091d81c19500fb28a0c9c9d2a48f61b8665b','new physical/template word mismatch')
    need(cr['retained_assumptions']==ASSUMPTIONS and cr['new_candidate_specific_assumptions']==[],'5387 premise change')
    need(cr['expanded_constants']['N']==r['N'] and cr['expanded_constants']['C1']==1,'new compiler N/C1 mismatch')
    need(cr['expanded_constants']['old_raw_cap_used_as_expanded_cap'] is False and cr['stock']['simultaneous_rule']=='product' and cr['stock']['ordinary_BIT_atom']==r['ordinary_BIT']['atom'],'new expanded-cap/stock product mismatch')
    need(cr['approximation']['error_site_log_bound']=='(G+N+2*P+4)*d','leaf inclusive new-N error bound absent')
    need(cr['changed_physical_inventory']['owned_added']==['L',261] and cr['changed_physical_inventory']['owned_removed']==['L',288] and cr['preparation']['changed_last_snapshot']['source_role']==['L',256],'changed relation/owner inventory not covered')
    need(cr['ordinary']['local_upper']==r['invoice']['ordinary']['local_units_upper'] and cr['ordinary']['raw_global_upper']==r['invoice']['ordinary']['raw_nonrecursive_units_upper'],'ordinary tariff mismatch')
    for path,h in cr['dependencies_sha256'].items():need(sha(ROOT/path)==h,'5387 closure dependency changed '+path)
    generic=cr['base_generic_lemma'];need(sha(ROOT/generic['closure_5383_v2_path'])==generic['closure_5383_v2_sha256'],'base generic lemma changed')
    supp=W/'09-capsule-cold/supplement-03-v1';sm=json.loads((supp/'MANIFEST.json').read_bytes())
    for row in sm['rows']:checked_bytes(row,(supp/'snapshot'/row['path']).read_bytes());need(cr['source_proof_sha256'][row['path']]==row['sha256'],'canonical proof source changed')
    si=bound(H/'source-inventory-v1.json','fb5552da9096651bcf8cec614d6ef2c3c6429d33f089697eb9b57d3622b69aa4')
    need(set(r['outer']['strict_checks'])==set(si['direct_strict_names'])|set(si['margin_derived_strict_names']),'new54 inventory changed')
    need(set(r['outer']['functional_checks'])==set(si['source_functional_names'])|set(si['typed_interface_added_functional']),'new4 inventory changed')
    predecessor=bound(H/'receipt-v3.json','a5f48459f8500909a243462c2cd205c57f064fc76ef7082ba41c516fbd5a5794');need(predecessor['endpoint_funded'] is True,'strong precursor gate absent')
    r['same_profile_predecessor'].update(path=str(H/'receipt-v3.json'),sha256=sha(H/'receipt-v3.json'),credit='Ali Romman #5383 owns public eight-relation mechanism/P-T profile; Dugongue #5387 changes last relation/pivot/retained boundary and preparation and certifies the smaller-reserve funded compiler point')
    deps={str(p):sha(p) for p in [H/'5387-receipt-v1.json',ph,cl,H/'source-inventory-v1.json',supp/'MANIFEST.json',H/'receipt-v3.json']}
    r.update(status='FUNDED_CONDITIONAL_INDEPENDENT_STATIC_ADMISSION',endpoint_funded=True,finite_template_gate_bound=True,complete_bill_ready=True,arithmetic_receipt={'path':str(H/'5387-receipt-v1.json'),'sha256':sha(H/'5387-receipt-v1.json')},physical_gate={'path':str(ph),'sha256':sha(ph),'status':pr['status'],'fresh_all_column_review':True},precision_stock_gate={'path':str(cl),'sha256':sha(cl),'status':cr['status'],'new_candidate_specific_assumptions':[],'fresh_new_N_and_word':True},source_predicate_inventory={'path':str(H/'source-inventory-v1.json'),'sha256':sha(H/'source-inventory-v1.json'),'strict':54,'functional':4},closure_dependencies_sha256=deps,closure_runner_sha256=sha(Path(__file__)),funding_scope='Actual changed compiler point independently funded for the freshly validated changed physical word, complete invoice and new-N expanded template, under exactly five selected assumptions.',registered_cold_bound=False,public_reviewable=False,selected=False,external_gate_requirements=['role09 serial registered normal/optimized replay and final publication preflight'],scientific_scope='Fresh independent #5387 physical, complete-census, new-N precision/stock/tape applicability and exact compiler/outer gates pass for the same exact source-bound candidate. No physical endpoint transfers by histogram equality; exactly five source framework assumptions retained.')
    raw=(json.dumps(r,indent=2,sort_keys=True)+'\n').encode();out.write_bytes(raw);out.chmod(0o444);(H/'5387-receipt-v2.sha256').write_text(sha(out)+'  5387-receipt-v2.json\n')
    print(json.dumps({'status':r['status'],'receipt_sha256':sha(out),'endpoint_funded':True,'kappa':r['kappa']}))
if __name__=='__main__':run()
