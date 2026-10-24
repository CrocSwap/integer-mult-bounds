"""Read-only coherent-receipt and source-pin check; optional manifest freeze."""
from pathlib import Path
from hashlib import sha1,sha256
import argparse,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def need(ok,message):
    if not ok:raise ValueError(message)
def main():
    if not __debug__:raise ValueError('Run the frozen research checks with assertions enabled')
    ap=argparse.ArgumentParser();ap.add_argument('--write-manifest',action='store_true');args=ap.parse_args()
    sources=read(HERE/'SOURCES.json')
    for row in sources['sources']:
        p=ROOT/row['path'] if row['name']=='native-word' else HERE/'sources'/row['name']
        raw=p.read_bytes();need(sha256(raw).hexdigest()==row['sha256'],'Source SHA '+row['name'])
        if 'blob' in row:need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['blob'],'Original Git blob '+row['name'])
    owned=read(HERE/'OWNED-PHASE-GATE.json')
    need(owned['script_sha256']==digest(HERE/'owned_phase_probe.py'),'Owned probe source')
    need(owned['sources_sha256']==digest(HERE/'SOURCES.json'),'Owned source pins')
    need(owned['remaining_equations']==0 and not owned['useful_helper_queries'],'Owned relaxed helper gate')
    need(len(owned['free_forms_only_at_isolated_clear_nodes'])==8 and owned['nonzero_coordinates']==288,'Isolated clear forms')
    exact=read(HERE/'EXACT-DEFECT-RESULT.json')
    need(exact['script_sha256']==digest(HERE/'exact_defect_probe.py'),'Exact scan source')
    need(exact['source_graph_probe_sha256']==digest(HERE/'owned_phase_probe.py'),'Exact graph extraction')
    need(exact['sources_sha256']==digest(HERE/'SOURCES.json'),'Exact source pins')
    need(exact['complete_candidate_scan'] and exact['tested']==exact['proof_dependency_candidates']==2008,'Complete 2008 scan')
    need(exact['edge_count']==34638 and exact['equations']==559088 and exact['helper_queries']==80,'Complete declared graph')
    witnesses=read(HERE/'ONE-DEFECT-WITNESSES.json')
    need(exact['witnesses']==witnesses and len(witnesses)==100,'Final witness checkpoint')
    forms=read(HERE/'FORMS-WITNESSES.json')
    need(forms['source_witnesses_sha256']==digest(HERE/'ONE-DEFECT-WITNESSES.json'),'Forms input snapshot')
    need(forms['script_sha256']==digest(HERE/'materialize_forms.py'),'Whole-kernel source')
    need(forms['sources_sha256']==digest(HERE/'SOURCES.json'),'Whole-kernel source pins')
    need(len(forms['witnesses'])==100,'All feasible kernels materialized')
    boundaries=[]
    for w in forms['witnesses']:
        c=w['whole_kernel_classification']
        need(c['all_residual_equations_discharged'] and len(c['whole_kernel_incident_support_nodes'])==1,'Whole-kernel support')
        need(c.get('all_forms_are_one_helper_boundary_only') and c.get('all_rank_nonimprovement_by_strict_subadditivity'),'All-rank classification')
        need(c['zero_rank_edge'] and c['helper_form_is_restriction_of_paid_defect'] and c['old_helper_rank']>0,'Cost lemma premises')
        boundaries.append(c['boundary'])
    need(boundaries.count('entrance')==boundaries.count('exit')==50,'Boundary census')
    verified=read(HERE/'VERIFIED-FORMS.json')
    need(verified['forms_sha256']==digest(HERE/'FORMS-WITNESSES.json'),'Independent forms snapshot')
    need(verified['script_sha256']==digest(HERE/'verify_forms.py') and not verified['equality_solver_used'],'Independent evaluator source')
    need(len(verified['results'])==100 and len(verified['controls'])==3,'Independent matrix coverage')
    invoice=read(HERE/'INVOICE.json')
    need(invoice['script_sha256']==digest(HERE/'invoice.py'),'Invoice source')
    need(invoice['witnesses_sha256']==digest(HERE/'ONE-DEFECT-WITNESSES.json'),'Invoice witness snapshot')
    need(invoice['baseline_whole_arithmetic_sha256']==digest(ROOT/'research/kappa-round6-compiler-tightening-20261022/ARITHMETIC.json'),'Whole baseline')
    need(invoice['independent_interval_engine_sha256']==digest(ROOT/'research/kappa-rebuild/transfer-audit/outer_transfer_audit.py'),'Interval engine')
    need(invoice['witness_count']==invoice['all_t_negative_witnesses']==100 and invoice['positive_witnesses']==0,'Complete negative invoice')
    controls=read(HERE/'CONTROLS.json')
    for key,name in [('script_sha256','controls.py'),('proof_engine_sha256','exact_defect_probe.py'),('graph_probe_sha256','owned_phase_probe.py')]:
        need(controls[key]==digest(HERE/name),'Control source '+name)
    need(controls['query_proofs']==896 and controls['exact_gaussian_edge_deletion_counterfactuals']==5426,'Independent proof controls')
    lean=read(HERE/'LEAN-VERIFICATION.json')
    need(lean['status']=='PASS_SCOPED_PHASE_PREPROCESSING_INEQUALITY_LEAN' and lean['fresh_axiom_reports']==4,'Scoped fresh Lean')
    need(lean['script_sha256']==digest(HERE/'verify_lean.py'),'Lean wrapper source')
    need(lean['source_sha256']==digest(HERE/'Preprocessing.lean') and lean['log_sha256']==digest(HERE/'Preprocessing.log'),'Lean source/log')
    if (HERE/'Preprocessing.olean').exists():need(lean['olean_sha256']==digest(HERE/'Preprocessing.olean'),'Local Lean object')
    runtime=ROOT/'research/kappa-lean-verification-20261022'
    need(lean['auditor_sha256']==digest(runtime/'verify_lean.py')=='6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895','Pinned proof auditor')
    need(lean['runtime']['lean_executable_sha256']==digest(runtime/'.toolchain/lean-4.21.0-windows/bin/lean.exe'),'Compiler executable')
    spec=importlib.util.spec_from_file_location('phase_bundle_proof_auditor',runtime/'verify_lean.py')
    W=importlib.util.module_from_spec(spec);spec.loader.exec_module(W)
    need(W.parse_axioms(HERE/'Preprocessing.log',W.audit_source(HERE/'Preprocessing.lean'))==lean['axioms'],'Lean reports')
    result=dict(status='PASS_FROZEN_ONE_EDGE_PHASE_NONIMPROVEMENT',script_sha256=digest(__file__),
        physical_edges=34638,exact_candidate_deletions=2008,feasible_edges=100,
        full_kernel_single_helper_boundaries=100,entrance_cases=50,exit_cases=50,
        independent_matrix_witnesses=100,negative_complete_invoices=100,positive_invoices=0,
        fresh_Lean_modules=1,fresh_Lean_analytic_reports=4,
        receipt_sha256={n:digest(HERE/n) for n in ['SOURCES.json','OWNED-PHASE-GATE.json','EXACT-DEFECT-RESULT.json',
            'ONE-DEFECT-WITNESSES.json','FORMS-WITNESSES.json','VERIFIED-FORMS.json','INVOICE.json','CONTROLS.json','LEAN-VERIFICATION.json']},
        scope='Exact fixed-graph one-edge phase nonimprovement with owned contact phases relaxed; finite classification is Python, analytic implication is Lean. No joint-defect/global phase ceiling, native admission, new controller or kappa.')
    output=HERE/'BUNDLE-CHECK.json'
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if output.exists() and not args.write_manifest:need(output.read_text(encoding='utf-8')==encoded,'Frozen bundle receipt drift')
    else:output.write_text(encoded,encoding='utf-8',newline='\n')
    files={str(p.relative_to(HERE)).replace('\\','/'):digest(p) for p in HERE.rglob('*') if p.is_file() and
        p.name!='ARTIFACT-MANIFEST.json' and p.suffix!='.olean' and not any(x in ['.scratch','__pycache__'] for x in p.relative_to(HERE).parts)}
    manifest=dict(status='FROZEN_SOURCE_AND_RECEIPT_MANIFEST',files_sha256=files)
    target=HERE/'ARTIFACT-MANIFEST.json'
    if args.write_manifest:target.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:need(read(target)==manifest,'Frozen artifact hashes')
    print(result['status'],'edges=34638 exact=2008 feasible=100 positive=0 freshLeanReports=4')
if __name__=='__main__':main()
