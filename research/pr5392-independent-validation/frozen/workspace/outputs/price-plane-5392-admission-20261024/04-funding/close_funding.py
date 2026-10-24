#!/usr/bin/env python3
"""Immutable join of independent5392physical, phase, invoice and precision gates."""
from pathlib import Path
import json
from exact_engine import need,ASSUMPTIONS
from invoice import H,W,ROOT,CAP,PKG,HEAD,BASE,read,sha,checked

def bound(p,h):need(sha(p)==h,'dependency changed '+str(p));return read(p)
def run():
 outp=H/'FUNDING-v2.json';need(not outp.exists(),'immutable final funding receipt exists')
 r=bound(H/'FUNDING-v1.json','bf473e85e61d957ccbe984a2ffc55c2312db0c7b1fbf2fc7a4529f3b91b680a9')
 inv=bound(H/'INVOICE-v1.json',r['invoice']['sha256'])
 cp=W/'03-closure/CLOSURE-v1.json';cr=bound(cp,'4959ea0a58ac51cd6fea46ce0123bcbf74135b716593607031621fcd6bf2471f')
 wp=W/'01-physical/WORD-RECEIPT.json';wr=bound(wp,'0fc8aa60ab9ec712bb90d649e8bd863d6a3869b1efd99eecf45d1c3681070717')
 pp=W/'01-physical/PHASE-RECEIPT.json';pr=bound(pp,'938e5944f46168ef31ac4810269507fc8ec794e791377f504d695a22c2ef8d5a')
 gp=W/'01-physical/PHASE-GUARD-RECEIPT.json';gr=bound(gp,'56a9cd98fbc6f2c2146ca9d7cde7467a5d687dd029969f6178125b803b73789f')
 need(cr['status']=='PASS_SAME_PREMISE_CONSTRUCTIVE_FINITE_TEMPLATE_SPECIALIZATION' and cr['candidate']['head']==HEAD and cr['candidate']['canonical_base']==BASE,'fresh precision candidate/status mismatch')
 need(cr['retained_assumptions']==ASSUMPTIONS and cr['new_candidate_specific_assumptions']==[],'extra premise introduced')
 need(cr['candidate']['word_sha256']==inv['word_sha256']==wr['word_sha256'],'word/source gate mismatch')
 need(wr['status']=='PASS_INDEPENDENT_LITERAL_TRANSPOSE_AND_UNIVERSAL_ENDPOINT' and wr['head']==HEAD and wr['manifest_sha256']==inv['authentication']['root_manifest_sha256'],'physical gate mismatch')
 ep=wr['entry_endpoint'];need(ep['entry_columns']==641 and ep['retained']==624 and ep['arbitrary_owned']==17 and ep['owned_returned_zero'] is True and ep['all_ghost_terms_cancel'] is True,'all641 boundary incomplete')
 need(pr['status']=='PASS_INDEPENDENT_EXACT_TRANSPOSE_PHASES' and pr['head']==HEAD and (pr['paid_classes'],pr['native_warp_classes'],pr['literal_native_columns'],pr['Q_squared_ports'])==(2847,180,92160,112),'fresh phase inventory incomplete')
 need(gr['exit_code']==0 and gr['resource_stop'] is None and gr['source_immutability'] is True,'phase execution guard did not pass')
 need(sha(W/'01-physical/check_phases.py')==pr['code_sha256']==gr['code_sha256'],'phase code drift')
 need(cr['expanded_constants']['N']==r['N'] and cr['expanded_constants']['C1']==1 and cr['expanded_constants']['old_equal_N_implies_old_constants'] is False,'new expanded constants mismatch')
 need(cr['ordinary']['raw_local_owned_banks']==inv['controller']['raw_owned_banks']==306,'suspended owner allocation mismatch')
 need(cr['ordinary']['independent_route_upper']==inv['ordinary']['route_units_upper'] and cr['ordinary']['local_scalar_route_upper']==inv['ordinary']['local_units_upper'] and cr['ordinary']['raw_global_upper']==inv['ordinary']['raw_units_upper'],'fresh ordinary tariff mismatch')
 need(cr['ordinary']['two_sided_nine_axis_factor_recipe_upper']<cr['ordinary']['common_route_group_multiplier'],'route recipe outside bound')
 need(cr['stocks']['ordinary_BIT_atom']==r['ordinary_BIT']['atom'] and cr['stocks']['simultaneous_rule']=='PRODUCT, never maximum','stronger BIT/complex product missing')
 need(cr['actual_word_error_proof']['runtime_zero_test'] is False and cr['actual_word_error_proof']['independent_errors_assumed_cancel'] is False and cr['actual_word_error_proof']['error_site_count']=='(G+N+1)*e*(P+1)^(D+1)','actual changed-word error proof uncovered')
 for p,h in cr['dependencies_sha256'].items():need(sha(ROOT/p)==h,'precision dependency drift '+p)
 for file,key in [('exact_engine.py','engine_sha256'),('invoice.py','invoice_runner_sha256'),('funding.py','funding_runner_sha256')]:need(sha(H/file)==r[key],'independent code drift '+file)
 manifest=read(CAP/'ROOT-MANIFEST.json');need(sha(CAP/'ROOT-MANIFEST.json')==r['source']['root_manifest_sha256'],'root source capsule drift')
 for row in manifest['rows']:checked(row,(CAP/row['path']).read_bytes())
 r.update(status='FUNDED_CONDITIONAL_INDEPENDENT_STATIC_ADMISSION',endpoint_funded=True,finite_template_gate_bound=True,complete_bill_ready=True,physical_gate={'word_receipt':str(wp),'word_sha256':sha(wp),'phase_receipt':str(pp),'phase_sha256':sha(pp),'guard_receipt':str(gp),'guard_sha256':sha(gp)},precision_stock_gate={'path':str(cp),'sha256':sha(cp),'status':cr['status'],'new_candidate_specific_assumptions':[]},arithmetic_receipt={'path':str(H/'FUNDING-v1.json'),'sha256':sha(H/'FUNDING-v1.json')},closure_dependencies_sha256={str(p):sha(p) for p in [H/'FUNDING-v1.json',H/'INVOICE-v1.json',cp,wp,pp,gp]},closure_runner_sha256=sha(Path(__file__)),registered_cold_bound=False,public_reviewable=False,selected=False,scientific_scope='Independent5392literal invoice, full641-entry endpoint/owned transpose, fresh native absolute phases, new expanded precision/stock/tape applicability and exact funded compiler/outer point all pass at the same source head under exactly the five selected framework assumptions. No unconditional theorem, author cold replay or selected promotion.',external_gate_requirements=['root publication decision','09 final raw source-history/export preflight and any authorized registered cold replay'])
 outp.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');outp.chmod(0o444);(H/'FUNDING-v2.sha256').write_text(sha(outp)+'  FUNDING-v2.json\n')
 print(json.dumps({'status':r['status'],'sha256':sha(outp),'kappa':r['kappa'],'endpoint_funded':True}))
if __name__=='__main__':run()
