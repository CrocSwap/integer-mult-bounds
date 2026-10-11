#!/usr/bin/env python3
"""One-command independent exact replay; only this packet's audit code runs.
Reference source programs are never imported or executed. Python standard library.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import shutil
from collections import Counter
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parent
if sys.flags.optimize:
    raise SystemExit('FAIL: assertions are required; remove -O/PYTHONOPTIMIZE')

def integrity(root=ROOT):
    manifest=json.loads((root/'SHA256SUMS.json').read_text())
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    require(actual==set(manifest)|{'SHA256SUMS.json'},'unlisted or missing packet files: '+str(sorted(actual ^ (set(manifest)|{'SHA256SUMS.json'}))))
    require(not any(p.is_symlink() for p in root.rglob('*')),'symlinks are not packet files')
    for name,r in manifest.items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'unsafe manifest path')
        path=root/name
        if not path.is_file():raise ValueError('missing packet file: '+name)
        b=path.read_bytes()
        if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:
            raise ValueError('packet integrity mismatch: '+name)
    return len(manifest)

def load_checker():
    spec=importlib.util.spec_from_file_location('independent_packet_checker',ROOT/'exact_checker.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def require(condition,message):
    if not condition:raise ValueError(message)

def source_text(path):
    records=json.loads((ROOT/'PROVENANCE.json').read_text())['sources']
    r=next(r for r in records if r['source_path']==path)
    return (ROOT/r['packet_path']).read_text()

def statement_fidelity(s):
    b=s['B3'];e=s['endpoint']
    require(b['kind']=='conditional_block_route_provider','B3 must remain conditional')
    require(b['h_min']==2 and b['dimension']=='7*h','B3 dimension/hypothesis drift')
    require(b['stages']==['F1','B1','F1','B2','F2','B3','F3'],'B3 schedule drift')
    require(b['port_conditions']==['u dot u = 1 over F2','u is not the all-ones vector'],'port assumptions omitted')
    require(b['local_hypotheses']==['physical Inv or GInv route package','both chronological orientations','full joint live-state identity for arbitrary helper values','common helper multiplier W','declared scratch action and no other live effects','exact local paid-block price'],'local physical hypotheses omitted or changed')
    require(b['owner_rule']=='d=g*rho_kt; gamma=d*tau_k; right actions, not cumulative','B3 owner drift')
    require(b['live_roles_per_owner']=='6*v+R','B3 stock drift')
    require(b['terminal_rule']=='translate Y by u, then simultaneously (X,Y)<-(Y,-X)','terminal correction drift')
    require(b['paid_price_per_owner']=='7*C_inv+2*v*(2*b(h-1)+b(2*h-2)+b(4*h-4)+b(4*h+2)+b(2*h+4)+b(6))','block price drift')
    require(b['actual_PR390_instance_certified'] is False,'unjustified PR390 instance claim')
    require(e['kind']=='conditional_bank_completion_and_specific_interface_obstruction','endpoint scope drift')
    require(e['hypotheses']==['completed local macro with independent helper endpoints and no residual cross terms','distinct physical roles and restored private workspace','exact signed adapters','each cover owner called once per selected role','once-only bank coverage including paid padding','serial complete macros'],'bank theorem premises omitted')
    require(e['owner_rule']=='g=d*A^-1','owner inverse omitted')
    require(e['completion_criterion']=='sum epsilon*v*v^T = I over F2','completion field/criterion drift')
    require(e['translation']=='delta_i=(sum epsilon*v_i-1)/2 mod 2','cover phase drift')
    require(e['normals']==[508,499] and e['character_eigenvalues']=={'rank8':[1,0],'common_rank9':[0,-1]},'counterexample drift')
    require(e['claim_existing_PR390_adapters_are_wrong'] is False,'adapters agree with source; do not claim a source bug')
    require(s['not_certified']==['optimized local physical package','nine-stage PR390 data endpoint','all-size compressed windows','recursive compiler','bit/row/precision/router bounds','multiplication exponent','novel general normalization mechanism'],'scope boundary changed')
    require(s['formalization']=='partial structural core and concrete arithmetic obstruction only','Lean scope overstated')
    for path,tokens in {
        'Work/Bridge/Inv.lean':['structure Inv','iout Xm tv (fun q => Wn * Z q)','fwd :','bwd :'],
        'Work/GCert/Chain/Inv.lean':['structure GInv','iout W.Xm tv (fun q => Wn * Z q)','hgap :'],
        'Work/GCert/Chain/WinB.lean':['def gwinB','Fintype.card B','GWin H (LB B H)'],
        'Work/Block/Word.lean':['| localM (g : Matrix ρ ρ ℚ)','1 ≤ rk ∧ rk < u'],
        'Work/BlockApply/Exact.lean':['def XRoute','∀ (f : ℕ) (x : Data α ρ f)'],
        'research/e8-prefix-restoration/code/root-global.py':['g=d*A^-1','delta_i=(weight(row_i(g))-1)/2 mod 2'],
        'research/e8-prefix-restoration/code/complex-bank-phase.py':['relative=canonical.adjoint().then(routed)',"assert rec['rank']==0"],
        'research/e8-prefix-restoration/code/complex-hetero-compose.py':["for r,a in sinks.items():final[r]=a['frame']"],
        'research/e8-prefix-restoration/research-notes/complex-hetero-note.md':['Physical stock59692'],
    }.items():
        text=source_text(path)
        require(all(t in text for t in tokens),'source statement mismatch: '+path)
    return 'PASS: authored statement drift guards and pinned source substring checks; not semantic source verification'

def negative_controls(C,results,statements,columns):
    out=[]
    def rejected(name,fn,category="algebra_or_coverage_witness"):
        try:fn()
        except (AssertionError,ValueError) as e:out.append({"control":name,"category":category,"rejected":True,"evidence":str(e) or "expected assertion failed"})
        else:raise AssertionError('negative control accepted: '+name)
    rejected('omit first B3 twin alignment',lambda:C.b3_schedule(9,omit_first_alignment=True),'schedule_pipeline_mutation')
    # These controls compute the altered operators' exact character multipliers.
    a=14;z=2
    signed=(a.bit_count()*C.parity(a&z))%4;unsigned=C.parity(a&z)
    require((signed,unsigned)==(3,1),'unsigned-control witness drift')
    rejected('ignore rank-one signed phase',lambda:require(signed==unsigned,'-i differs from i'))
    line=C.projector(C.eye(2),{0});rest=tuple(x^y for x,y in zip(C.eye(2),line))
    required=C.phase_value(C.padd(C.phase_of_matrix(C.eye(2)),C.phase_of_matrix(line)),1,2)
    uncorrected=C.phase_value(C.phase_of_matrix(rest),1,2)
    require((required,uncorrected)==(2,0),'terminal-control witness drift')
    rejected('omit terminal Y translation',lambda:require(required==uncorrected,'translation character sign is missing'))
    prefix=C.projector(C.eye(63),set(range(54)))
    rejected('omit seventh helper window',lambda:require(C.mv(prefix,1<<62)==1<<62,'last window is missing'))
    bad=results['endpoint_banks']['wrong_inverse']
    require((bad['character'],bad['correct_phase'],bad['wrong_phase'])==(4,1,0),'wrong-inverse semantic witness drift')
    rejected('replace nonsymmetric A^-1 owner factor by A',lambda:require(bad['correct_phase']==bad['wrong_phase'],'i differs from 1'),'computed_route_mutation_witness')
    # Standard bank with only eight full-nine blocks misses axis 72.
    missing=[1<<i for i in range(72)];z=1<<72
    rejected('omit paid bank padding',lambda:require(sum(C.parity(v&z) for v in missing)%4==1,'missing axis has eigenvalue 1 instead of i'))
    g=C.transvection(4,15)
    phase=sum(C.parity(v&1) for v in g)%4
    require(phase==3,'nontrivial cover correction witness drift')
    rejected('omit final cover translation',lambda:require(phase==1,'uncorrected -i differs from i'))
    # Every mutated recipe is compared against all 512 freshly computed exact columns.
    for a in results['literal_adapters']:
        prefix='frame '+str(a['frame'])+': '
        for label,key,value in [('drop global phase','phase',0),
                                ('drop affine translation','offset',0),
                                ('drop linear phase','linear_Z4',[0]*9),
                                ('replace permutation by identity','matrix_columns',list(C.eye(9)))]:
            mutant=deepcopy(a);mutant[key]=value
            rejected(prefix+label,lambda mutant=mutant:C.validate_adapter_recipe(mutant,columns[a['frame']]),'exact_adapter_recipe_mutation')
    s=deepcopy(statements);s['B3']['local_hypotheses'].remove('physical Inv or GInv route package')
    rejected('promote scalar B3 to unconditional physical claim',lambda:statement_fidelity(s),'statement_drift_guard')
    s=deepcopy(statements);s['endpoint']['owner_rule']='g=d*A'
    rejected('statement wrong inverse',lambda:statement_fidelity(s),'statement_drift_guard')
    s=deepcopy(statements);s['not_certified'].remove('multiplication exponent')
    rejected('remove exponent boundary',lambda:statement_fidelity(s),'statement_drift_guard')
    s=deepcopy(statements);s['formalization']='complete provider Lean theorem'
    rejected('overstate Lean scope',lambda:statement_fidelity(s),'statement_drift_guard')
    # The actual binding verifier reads a corrupted temporary copy of the fixtures.
    with tempfile.TemporaryDirectory(prefix='source-binding-mutation-') as t:
        target=Path(t)
        shutil.copy2(ROOT/'PROVENANCE.json',target/'PROVENANCE.json')
        for r in json.loads((ROOT/'PROVENANCE.json').read_text())['sources']:
            dest=target/r['packet_path'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/r['packet_path'],dest)
        corrupt=target/'sources/pr390/data/prefix18.json.gz'
        corrupt.write_bytes(corrupt.read_bytes()+b'!')
        rejected('corrupt pinned source byte',lambda:C.binding(target),'source_binding_pipeline_mutation')
    return out

def lean_check(path):
    exe=Path(path)
    require(exe.is_absolute() and exe.is_file(),'--lean must be an absolute installed executable path')
    require(exe.resolve().name!='elan','refusing elan shim; give the installed toolchain lean binary')
    v=subprocess.run([str(exe),'--version'],capture_output=True,text=True,timeout=30,check=True).stdout.strip()
    require('version 4.33.0' in v,'only the recorded Lean 4.33.0 version is accepted')
    with tempfile.TemporaryDirectory(prefix='interface-lean-') as t:
        r=subprocess.run([str(exe),'-o',str(Path(t)/'StructuralCore.olean'),str(ROOT/'formal/StructuralCore.lean')],cwd=ROOT,capture_output=True,text=True,timeout=60)
        require(r.returncode==0 and 'error:' not in r.stdout+r.stderr,'Lean compilation failed: '+r.stdout+r.stderr)
        require('sorryAx' not in r.stdout+r.stderr,'unexpected sorry dependency')
        require((Path(t)/'StructuralCore.olean').is_file(),'Lean output missing')
    verification=json.loads((ROOT/'formal/VERIFICATION.json').read_text())
    source_sha=hashlib.sha256((ROOT/'formal/StructuralCore.lean').read_bytes()).hexdigest()
    require(v==verification['version'],'Lean version differs from recorded verification')
    require(source_sha==verification['source_sha256'],'Lean source differs from recorded verification')
    require(r.stdout==(ROOT/'formal/lean.log').read_text(),'fresh Lean axiom output differs from recorded log')
    require(hashlib.sha256(r.stdout.encode()).hexdigest()==verification['axiom_output_sha256'],'Lean log binding mismatch')
    return {'status':'PASS','version':v,'source_sha256':source_sha,'axiom_output':r.stdout.strip(),'recorded_output_matches':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--lean',help='absolute path to installed Lean 4.33.0 binary; no shim/install')
    parser.add_argument('--integrity-only',action='store_true',help='only check all packet hashes; useful for tamper controls')
    args=parser.parse_args()
    count=integrity()
    if args.integrity_only:
        print(json.dumps({'status':'PASS_INTEGRITY_ONLY','files':count}));return
    C=load_checker();sources=C.binding()
    statements=json.loads((ROOT/'STATEMENTS.json').read_text())
    fidelity=statement_fidelity(statements)
    c=json.loads(C.gzip.decompress((C.E8/'data/prefix18.json.gz').read_bytes()))
    provenance=C.endpoint_provenance(c)
    require(statements['evidence_scope']['binary_final_values']=={'355':1,'403':1},'binary final scope drift')
    require(statements['evidence_scope']['modified_walk_certified'] is False,'changed walk is not certified')
    columns={}
    results={'source_files_verified':sources,'literal_adapters':C.literal_adapters(c,columns),'endpoint_banks':C.endpoint_banks(c),'b3':C.b3_geometry(),'completion_exhaustive_signed_cases':C.completion_small(),'status':'PASS_EXACT_CONDITIONAL_THEOREMS_AND_FINITE_WITNESSES'}
    expected=json.loads((ROOT/'expected/results.json').read_text())
    expected['endpoint_banks']['source_declared_physical']=expected['endpoint_banks'].pop('physical')
    derived=json.loads((ROOT/'expected/literal-endpoint-adapters.json').read_text())
    require(json.loads(json.dumps(results['literal_adapters']))==derived['adapters'],'derived adapter copy differs from fresh columns')
    for k in expected:
        if k!='source_files_verified':
            require(json.loads(json.dumps(results[k]))==expected[k],'independent replay differs from original verified result: '+k)
    b3=statements['B3']
    require(b3['idle_per_side_h9']==results['b3']['idle_h9'][::2],'B3 displayed price/ranks mismatch')
    for claim,actual in zip(statements['endpoint']['adapters'],results['literal_adapters']):
        require((claim['frame'],claim['normal'],claim['offset'],claim['global_phase_Z4'])==(actual['frame'],actual['normal'],actual['offset'],actual['phase']),'displayed adapter drift')
        require(claim['matrix_columns']==list(actual['matrix_columns']),'displayed adapter matrix drift')
        require(actual['linear_Z4']==[claim['linear_coefficient_Z4'] if i==claim['linear_axis'] else 0 for i in range(9)],'displayed linear phase drift')
    negative=negative_controls(C,results,statements,columns)
    lean=lean_check(args.lean) if args.lean else {'status':'NOT_RUN','recorded_compilation':'formal/lean.log','scope':'partial standalone formalization'}
    receipt={'status':'PASS','packet_files_verified':count,'source_blobs_verified':sources,'statement_fidelity':fidelity,'control_categories':dict(Counter(x['category'] for x in negative)),'controls':negative,'endpoint_provenance':provenance,'count_provenance':{'recomputed':['slots','rank8','rank9','banks','routes','nonsymmetric_routes','calls','padding_calls','adapter_uses','live','rank_mass_per_stage'],'source_declared_only':['source_declared_physical'],'original_reference_source_count':expected['source_files_verified']},'results':results,'lean':lean,'scope':'Independent conditional B3 and endpoint audit; no full PR390/compiler/exponent certification'}
    encoded=json.dumps(receipt,indent=2)+'\n'
    if args.output:args.output.write_text(encoded)
    print(encoded)

if __name__=='__main__':
    try:main()
    except Exception as e:
        print('FAIL: '+str(e),file=sys.stderr)
        raise SystemExit(1)
