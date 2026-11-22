#!/usr/bin/env python3
"""Portable bounded replay; full native admission remains a separate cold run.

Fast mode verifies source hashes, replays exact controls in a temporary copy,
and compares proof-relevant JSON without changing the package. Cold binding
mode checks an existing complete PR1661 native run against the pinned source.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, gzip, hashlib, json, os, shutil, subprocess, sys, tempfile

if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(500000)
PIN='f852af5e178ce035cd46181a29d9330bcbcaa206'
SOURCE_REL=Path('target002_upstream/pr1661/research/gmx-t74-p566-ep400')
EXPECTED_KAPPA=Q('0.001677160151714381')
CHECKS=[
 ('frontier_fusion/check_frontier_fusion.py','frontier_fusion/FRONTIER-FUSION-ARITHMETIC.json'),
 ('frontier_fusion/independent_substitution_check.py','frontier_fusion/INDEPENDENT-SUBSTITUTION-RECEIPT.json'),
 ('evidence/inplace_algebra_ultra/check_exact_algebra.py','evidence/inplace_algebra_ultra/EXACT-ALGEBRA.json'),
 ('evidence/inplace_algebra_ultra/check_tensor_compiler.py','evidence/inplace_algebra_ultra/TENSOR-COMPILER-CONTROLS.json'),
 ('evidence/inplace_algebra_ultra/check_supplier_capacity.py','evidence/inplace_algebra_ultra/SUPPLIER-CAPACITY-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_lower.py','evidence/gaussian_fast_ultra/LOWER-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_bilateral.py','evidence/gaussian_fast_ultra/BILATERAL-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_upper_data.py','evidence/gaussian_fast_ultra/UPPER-DATA-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_upper_merge.py','evidence/gaussian_fast_ultra/UPPER-MERGE-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_capped_gauges.py','evidence/gaussian_fast_ultra/CAPPED-GAUGE-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_dyadic_interiors.py','evidence/gaussian_fast_ultra/DYADIC-INTERIOR-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_cyclic_scan.py','evidence/gaussian_fast_ultra/CYCLIC-SCAN-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_forward_cell.py','evidence/gaussian_fast_ultra/FORWARD-CELL-CONTROLS.json'),
 ('evidence/gaussian_fast_ultra/check_log_a_schur.py','evidence/gaussian_fast_ultra/LOG-A-SCHUR-CONTROLS.json'),
 ('evidence/halo_layout_ultra/check_halo.py','evidence/halo_layout_ultra/HALO-CONTROLS.json'),
 ('evidence/halo_layout_ultra/check_embedding.py','evidence/halo_layout_ultra/EMBEDDING-CONTROLS.json'),
 ('evidence/halo_layout_ultra/check_ragged.py','evidence/halo_layout_ultra/RAGGED-CONTROLS.json'),
 ('evidence/halo_layout_ultra/check_sparse_shear.py','evidence/halo_layout_ultra/SPARSE-SHEAR-CONTROLS.json'),
 ('evidence/phase_layout_audit_ultra/check_union.py','evidence/phase_layout_audit_ultra/UNION-CONTROLS.json'),
 ('evidence/phase_layout_audit_ultra/check_q_embedding.py','evidence/phase_layout_audit_ultra/Q-EMBEDDING-CONTROLS.json'),
 ('evidence/phase_layout_audit_ultra/check_capped_layout.py','evidence/phase_layout_audit_ultra/CAPPED-LAYOUT-CONTROLS.json'),
]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(cond,msg):
    if not cond: raise RuntimeError(msg)
def normalized(x):
    # Only locations/timing are nonsemantic. All statuses, counts, rational
    # values, source digests, and control outcomes must agree exactly.
    if isinstance(x,dict):return {k:normalized(v) for k,v in x.items() if k not in {'seconds','native_required_output'}}
    if isinstance(x,list):return [normalized(v) for v in x]
    return x

def check_inputs(package):
    manifest=read(package/'PACKAGE-MANIFEST.json')
    need(isinstance(manifest,dict) and manifest,'missing nonempty package manifest')
    for rel,h in manifest.items():
        p=Path(rel)
        need(not p.is_absolute() and '..' not in p.parts,'unsafe manifest path')
        need(sha(package/p)==h,'package input hash mismatch: '+rel)
    present={p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='PACKAGE-MANIFEST.json'}
    need(present==set(manifest),'unlisted or missing package files')
    source=package/SOURCE_REL; sm=read(source/'MANIFEST.json')
    for required in ['new/SPEC.json','CLAIM.json','inputs/PR589-EXPECTED.json']:
        need((source/required).is_file(),'missing pinned native input: '+required)
    for f in source.rglob('*'):
        if f.is_file() and f.name!='MANIFEST.json':
            rel=f.relative_to(source).as_posix()
            need(rel in sm and sha(f)==sm[rel],'pinned native source mismatch: '+rel)
    b=read(package/'frontier_fusion/NATIVE-ADMISSION-BINDING.json')
    need(b['source_head']==PIN,'wrong native commit')
    need(b['source_manifest_sha256']==sha(source/'MANIFEST.json'),'wrong native source manifest')
    need(b['status']=='PASS_FRESH_NATIVE_ADMISSION_BOUND_TO_CONDITIONAL_SUBSTITUTION','native receipt not admitted')
    need(Q(b['recomposed_final_kappa']['strassen'])==EXPECTED_KAPPA,'wrong headline result')
    bit=read(source/'inputs/PR589-EXPECTED.json')
    need(Q(bit['nine']['bit_lower'])==Q('0.001733427039589844234749'),'wrong retained bit lower bound')
    for rel,h in b['receipt_sha256'].items():
        if (package/rel).is_file():need(sha(package/rel)==h,'included historical native receipt mismatch: '+rel)
    capsule=read(package/'NATIVE-RECEIPT-CAPSULE.json')
    need(capsule['source_commit']==PIN and capsule['source_manifest_sha256']==b['source_manifest_sha256'],'capsule source pin mismatch')
    pref={'native_work':'target002_upstream/full-1661-verification/','native_source':SOURCE_REL.as_posix()+'/'}
    bound={pref[z['root']]+z['path']:z['historical_sha256'] for z in capsule['receipts']}
    need(bound==b['receipt_sha256'],'capsule receipt inventory differs from historical native binding')
    need(sum('semantic_sha256' in z for z in capsule['receipts'])==46,'capsule semantic receipt coverage changed')
    return len(manifest)

def fast(package):
    count=check_inputs(package)
    need(__debug__,'assertions must be enabled')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',PYTHONINTMAXSTRDIGITS='500000')
    env.pop('PYTHONOPTIMIZE',None)
    with tempfile.TemporaryDirectory(prefix='phase-fusion-replay-') as td:
        root=Path(td)/'package';shutil.copytree(package,root,ignore=shutil.ignore_patterns('__pycache__'))
        results=[]
        for script,artifact in CHECKS:
            (root/artifact).unlink()
            cp=subprocess.run([sys.executable,'-B',str(root/script)],cwd=root,env=env,capture_output=True,text=True,timeout=120)
            need(cp.returncode==0,script+' failed\n'+cp.stdout[-3000:]+cp.stderr[-3000:])
            need((root/artifact).is_file(),'checker did not recreate artifact: '+artifact)
            need(normalized(read(root/artifact))==normalized(read(package/artifact)),'proof-relevant JSON changed: '+artifact)
            results.append({'script':script,'artifact':artifact,'status':'PASS_EXACT_REPLAY'})
        out=read(root/'frontier_fusion/FRONTIER-FUSION-ARITHMETIC.json')
        need(Q(out['rows']['strassen']['kappa']['rational'])==EXPECTED_KAPPA,'headline not derived')
        need(len(out['rows']['strassen']['strict_checks'])==45,'missing headline strict checks')
        need(len(out['rejecting_controls']['strassen'])==5,'missing headline rejecting controls')
    return {'status':'PASS_PORTABLE_EXACT_PHASE_FUSION_PACKAGE','scope':'Exact finite controls and arithmetic plus retained native receipt binding. This does not replay the entire native dependency or discharge all-size hypotheses. The matrix corollary retains an additional external premise.','package_files':count,'headline_kappa':str(EXPECTED_KAPPA),'checks':results}

def cold_binding(package,source,run):
    source=source.resolve();run=run.resolve()
    sm=read(source/'MANIFEST.json');need(sha(source/'MANIFEST.json')==sha(package/SOURCE_REL/'MANIFEST.json'),'cold source manifest differs from pinned input')
    for rel,h in sm.items():need(sha(source/rel)==h,'cold source bytes differ: '+rel)
    result=read(run/'RESULT.json');spec=read(source/'new/SPEC.json');claim=read(source/'CLAIM.json')
    need(result['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION','cold admission did not pass')
    need(Q(result['kappa'])==Q(claim['kappa'])==Q(spec['expected']['kappa']),'native endpoint disagreement')
    need(result['manifest_sha256']==sha(source/'MANIFEST.json'),'native run source mismatch')
    steps=read(run/'STAGES.json');required={'fine-engine-oracle','retained-provider-and-parent-admission','native-new-base','native-new-extra','reconstruct-owners','lift-parent','rebuild-words-566','audit-local-566-base','audit-local-566-extra','rebind-566','strict-t74','geometry-controls'}
    need({s['name'] for s in steps}==required and all(s['exit_code']==0 for s in steps),'cold stage coverage incomplete')
    need(steps==result['stages'],'top-level stage binding differs')
    for s in steps:need(s['log_sha256']==sha(run/(s['name']+'.log')),'cold stage log mismatch: '+s['name'])
    strict=read(run/'strict/RESULT.json');need(strict['status']=='PASS_STRICT_MIXED_T74_EXACT_FILL','strict admission failed')
    need(Q(strict['kappa'])==Q(result['kappa']),'strict kappa differs')
    assembly=read(run/'strict/ASSEMBLY.json')
    need(assembly['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY','assembly failed')
    need(Q(assembly['complex_lower'])==Q(spec['expected']['complex_lower']),'native complex endpoint differs')
    need(assembly['complex_profile']=={str(k):v for k,v in spec['expected']['global_profile'].items()},'native profile differs')
    need(len(assembly['outer'])==47 and all(Q(x)>0 for x in assembly['outer'].values()),'native strict inequalities failed')
    words={}
    for key,word in [('base','gauge44-word-566.json.gz'),('extra','extra-word-566.json.gz')]:
        d=run/('native-new-'+key);st=read(d/'STEPS.json')
        need([s['step'] for s in st]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in st),'native word coverage failed: '+key)
        need(gzip.decompress((d/'local/FULL-WORD.json.gz').read_bytes())==gzip.decompress((source/'new'/word).read_bytes()),'native word payload differs: '+key)
        words[key]=sha(source/'new'/word)
    caps=read(package/'frontier_fusion/NATIVE-ADMISSION-BINDING.json')
    need(result['controls']==caps['control_counts'],'cold control coverage differs')
    capsule=read(package/'NATIVE-RECEIPT-CAPSULE.json')
    def native_normalized(x):
        if isinstance(x,dict):return {k:native_normalized(v)for k,v in x.items()if k not in {'seconds','log_sha256'}}
        if isinstance(x,list):
            y=[native_normalized(v)for v in x]
            return sorted(y,key=lambda v:v['name']) if y and all(isinstance(v,dict)and'name'in v and'exit_code'in v for v in y) else y
        if isinstance(x,str):return x.replace(str(run),'{native-work}').replace(str(source),'{native-source}')
        return x
    bound={}
    for z in capsule['receipts']:
        root=run if z['root']=='native_work' else source
        f=root/z['path'];need(f.is_file(),'missing native receipt: '+z['path'])
        bound[z['root']+'/'+z['path']]=sha(f)
        if 'semantic_sha256' in z:
            digest=hashlib.sha256(json.dumps(native_normalized(read(f)),sort_keys=True,separators=(',',':')).encode()).hexdigest()
            need(digest==z['semantic_sha256'],'native semantic receipt differs: '+z['path'])
    files=[run/'RESULT.json',run/'STAGES.json',run/'strict/RESULT.json',run/'strict/ASSEMBLY.json']
    return {'status':'PASS_FRESH_NATIVE_RUN_BOUND_TO_PINNED_PHASE_FUSION','scope':'Existing complete cold native run checked against the pinned source and the independently replayed outer inputs; all-size assumptions remain.','source_commit':PIN,'source_manifest_sha256':sha(source/'MANIFEST.json'),'native_words':words,'complex_lower':assembly['complex_lower'],'profile':assembly['complex_profile'],'controls':result['controls'],'canonical_native_receipts_checked':46,'all_native_receipt_sha256':bound,'run_receipt_sha256':{str(f.relative_to(run)):sha(f) for f in files}}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--native-source',type=Path);ap.add_argument('--native-work',type=Path);ap.add_argument('--output',type=Path);a=ap.parse_args()
    need((a.native_source is None)==(a.native_work is None),'provide both --native-source and --native-work')
    package=a.package.resolve()
    if a.output:need(not a.output.resolve().is_relative_to(package),'--output must be outside the immutable package')
    out=fast(package)
    if a.native_source:out['cold_native_binding']=cold_binding(package,a.native_source,a.native_work)
    if a.output:a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],len(out['checks']),'exact control replays')
    if 'cold_native_binding' in out:print(out['cold_native_binding']['status'])
if __name__=='__main__':main()
