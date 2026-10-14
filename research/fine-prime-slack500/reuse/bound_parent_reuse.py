"""Authenticate complete prior finite evidence before reusing an unchanged parent.

No proof is inferred from a status string alone: every frozen source and every
file of the prior completed execution is matched to the reviewed seal.
"""
import hashlib,json,sys
from pathlib import Path
sys.set_int_max_str_digits(0)

def need(value,message):
    if not value:raise ValueError(message)

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()

def snapshot(root):
    return {p.relative_to(root).as_posix():digest(p) for p in root.rglob('*') if p.is_file()}

def read(path):return json.loads(path.read_bytes())

def verified_original_run(run_root,source_root,parent_root,seal_path):
    run_root=Path(run_root).resolve();source_root=Path(source_root).resolve()
    parent_root=Path(parent_root).resolve();seal_path=Path(seal_path).resolve()
    need(digest(seal_path)=='56fea2ce39c3c333862d68ecf65d5f5dd327b95fd5265d9f516ecd5928e854fb',
         'seal is not the authoritative reviewed full proof')
    seal=read(seal_path)
    need(seal['review_sha256']=='3d8778780afcaf4872f6225b784160572f628d50f1f46049014f0786cdfa801f',
         'prior independent review is not the admitted review')
    need(seal['schema']=='complete-finite-proof-reuse/1','unknown finite-proof seal')
    need(snapshot(source_root)==seal['baseline_source_files'],'complete prior source changed')
    need(snapshot(run_root)==seal['baseline_run_files'],'complete prior run closure changed')
    need(digest(source_root/'MANIFEST.json')==seal['baseline_manifest_sha256'], 'baseline source manifest')
    parent_snapshot={k.removeprefix('parent/'):v for k,v in seal['baseline_source_files'].items() if k.startswith('parent/')}
    need(snapshot(parent_root)==parent_snapshot,'current native parent differs from actual prior parent')
    need(digest(parent_root/'MANIFEST.json')==seal['parent_manifest_sha256'],'native parent manifest differs')
    review_path=seal_path.parent/seal['review_file']
    need(digest(review_path)==seal['review_sha256'],'independent actual review changed')
    review=read(review_path)
    need(review['status']=='PASS_POST_TERMINAL_CLOSURE','prior proof not independently reviewed')
    terminal=read(run_root/'TERMINAL.json');declaration=read(run_root/'DECLARATION.json')
    need(digest(run_root/'TERMINAL.json')==seal['actual_terminal_sha256'],'prior terminal pin')
    need(terminal['status']=='TERMINAL_PASS' and terminal['exit_code']==0 and terminal['limit_reason'] is None,
         'prior finite group not successfully terminal')
    need(terminal['sources_unchanged'] is True and terminal['active_descendants_at_exit']==0,'unfinished or changed prior group')
    need(terminal['declaration_sha256']==digest(run_root/'DECLARATION.json') and terminal['log_sha256']==digest(run_root/'process.log'),
         'prior controller source/log closure differs')
    need(declaration['source_files']==seal['baseline_source_files'],'prior actual input snapshot differs')
    result=read(run_root/'science/RESULT.json')
    need(result['status']=='PASS_ADDITIVE_FINITE_REFINEMENT_FULL_NATIVE' and result['parent_full_replay'] is True
         and result['native_reuse'] is False,'baseline is not a fresh actual finite proof')
    need(result['manifest_sha256']==seal['baseline_manifest_sha256']==review['manifest_sha256'],'actual baseline source review mismatch')
    original=run_root/'science/original'
    release=read(original/'RELEASE-RECEIPT.json')
    need(release['status']=='PASS_RELEASE' and release['manifest_sha256']==seal['parent_manifest_sha256'],'parent release not actually admitted')
    supplier=read(original/'verify/RESULT.json')
    need(supplier['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION' and not any(supplier['native_reuse'].values()),
         'supplier baseline reused unaccepted native material')
    for native in [original/'verify/parent/native-base',original/'verify/parent/native-extra',
                   original/'verify/native-new-base',original/'verify/native-new-extra']:
        rows=read(native/'STEPS.json')
        need([r['step'] for r in rows]==['native','ledgers','local-replay','wrappers','phases']
             and all(r['exit_code']==0 for r in rows),'incomplete prior native chain')
    assembly=read(original/'verify/strict/ASSEMBLY.json')
    need(assembly['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and len(assembly['outer'])==47,'prior strict assembly incomplete')
    return original,{'status':'PASS_COMPLETE_SOURCE_AND_EXECUTION_BOUND_PARENT_REUSE',
        'seal_sha256':digest(seal_path),'baseline_source_manifest':seal['baseline_manifest_sha256'],
        'baseline_review_sha256':seal['review_sha256'],'parent_manifest':seal['parent_manifest_sha256'],
        'source_files':len(seal['baseline_source_files']),'execution_files':len(seal['baseline_run_files']),
        'original_run':str(original),'scope':'Exact reviewed prior native evidence only; new arithmetic must be replayed on its actual admitted profile. Bit supplier remains cited/repriced and all-size hypotheses remain.'}
