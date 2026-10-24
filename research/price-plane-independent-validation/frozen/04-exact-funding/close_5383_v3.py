#!/usr/bin/env python3
"""Close peer physical/template gates without rerunning numerical arithmetic."""
from pathlib import Path
import json,hashlib
from exact_engine import need,ASSUMPTIONS
from bind_and_check import authenticate_capsule,checked_bytes,HEAD,CANONICAL,MANIFEST_SHA
H=Path(__file__).resolve().parent;W=H.parent;ROOT=H.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bound(p,expected):need(sha(p)==expected,'changed dependency '+str(p));return json.loads(p.read_bytes())
def run():
    need(not (H/'receipt-v3.json').exists(),'immutable receipt-v3 already exists')
    r=bound(H/'receipt-v1.json','fd195f406b6e8e11e29cad1a8d7c4ecf264ea5b968d19472a1ff4a2db0f4b112')
    authenticate_capsule()
    for file,key in [('exact_engine.py','engine_sha256'),('bind_and_check.py','binding_runner_sha256')]:need(sha(H/file)==r[key],'independent executable changed')
    ph=W/'01-physical/PHYSICAL-RECEIPT.json';pr=bound(ph,'c8221df752b6a8ffb7b0a9a98c4c0c034310ef70a81db4c195624bdf5480a786')
    cl=W/'03-precision-stock/CLOSURE-v2.json';cr=bound(cl,'0a171a3153304c1cf3bc2576ecf67e9489164401891723c4aa9865b770391e6b')
    need(pr['status']=='PASS_BOUNDED_INDEPENDENT_PHYSICAL_EIGHT_RELATIONS' and pr['candidate_head']==HEAD and pr['manifest_sha256']==MANIFEST_SHA,'physical gate mismatch')
    need(cr['status']=='PASS_SAME_PREMISE_CONSTRUCTIVE_FINITE_TEMPLATE_SPECIALIZATION','precision gate not complete')
    need(cr['candidate']['head']==HEAD and cr['candidate']['canonical_base']==CANONICAL,'precision pin mismatch')
    need(cr['candidate']['word_sha256']==pr['word_sha256'],'physical/template word mismatch')
    need(cr['retained_assumptions']==ASSUMPTIONS and cr['new_candidate_specific_assumptions']==[],'premise change')
    need(cr['expanded_constants']['N']==r['N'] and cr['expanded_constants']['C1']==1,'compiler/template constants mismatch')
    need(cr['stock']['simultaneous_rule']=='product' and cr['stock']['ordinary_BIT_atom']==r['ordinary_BIT']['atom'],'strong BIT stock mismatch')
    need(cr['expanded_constants']['old_raw_cap_used_as_expanded_cap'] is False,'old raw cap reused')
    need(cr['approximation']['error_site_log_bound']=='(G+N+2*P+4)*d','leaf-inclusive error bound missing')
    for path,expected in cr['dependencies_sha256'].items():need(sha(ROOT/path)==expected,'precision dependency changed '+path)
    supplement=W/'09-capsule-cold/supplement-03-v1';sm=json.loads((supplement/'MANIFEST.json').read_bytes())
    for row in sm['rows']:
        need(row['commit']==CANONICAL,'proof supplement floating pin');checked_bytes(row,(supplement/'snapshot'/row['path']).read_bytes())
        need(cr['source_proof_sha256'][row['path']]==row['sha256'],'proof dependency mismatch')
    si=bound(H/'source-inventory-v1.json','fb5552da9096651bcf8cec614d6ef2c3c6429d33f089697eb9b57d3622b69aa4')
    need(si['strict_count']==54 and si['functional_count']==4,'current inventory coverage mismatch')
    dependencies={str(p):sha(p) for p in [H/'receipt-v1.json',ph,cl,H/'source-inventory-v1.json',supplement/'MANIFEST.json']}
    r.update(status='FUNDED_CONDITIONAL_INDEPENDENT_STATIC_ADMISSION',endpoint_funded=True,finite_template_gate_bound=True,complete_bill_ready=True,arithmetic_receipt={'path':str(H/'receipt-v1.json'),'sha256':sha(H/'receipt-v1.json')},physical_gate={'path':str(ph),'sha256':sha(ph),'status':pr['status']},precision_stock_gate={'path':str(cl),'sha256':sha(cl),'status':cr['status'],'new_candidate_specific_assumptions':[]},source_predicate_inventory={'path':str(H/'source-inventory-v1.json'),'sha256':sha(H/'source-inventory-v1.json'),'strict':54,'functional':4},closure_dependencies_sha256=dependencies,closure_runner_sha256=sha(Path(__file__)),supersedes={'path':str(H/'receipt-v2.json'),'sha256':sha(H/'receipt-v2.json'),'reason':'Strengthened role03 leaf-inclusive error-site count; same word/P/T/N/C0/funded endpoint, no new assumptions.'},funding_scope='Independent static conditional admission of exact candidate and final rational endpoint, under exactly the five selected assumptions. Full registered cold/publication/source-history assembly remain separate.',registered_cold_bound=False,public_reviewable=False,selected=False,external_gate_requirements=['role09 serial registered normal/optimized replay and final publication preflight'],scientific_scope='The independent physical, complete-census, fresh expanded precision/stock/tape applicability and exact compiler/outer gates all pass for the same source-bound candidate. Retains exactly five source framework assumptions; no unconditional theorem or selected-record promotion.')
    raw=(json.dumps(r,indent=2,sort_keys=True)+'\n').encode();out=H/'receipt-v3.json';out.write_bytes(raw);out.chmod(0o444)
    (H/'receipt-v3.sha256').write_text(hashlib.sha256(raw).hexdigest()+'  receipt-v3.json\n')
    print(json.dumps({'status':r['status'],'receipt_sha256':sha(out),'endpoint_funded':True,'kappa':r['kappa']}))
if __name__=='__main__':run()
