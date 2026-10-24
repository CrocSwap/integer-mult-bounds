#!/usr/bin/env python3
"""Conditional scalar construction-target replay; no physical supplier admission."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent

def need(ok,why):
    if not ok:
        raise ValueError(why)

def authenticate():
    manifest=json.loads((ROOT/'EVIDENCE.json').read_text())
    actual={str(f.relative_to(ROOT)) for f in (ROOT/'evidence').rglob('*') if f.is_file()}
    need(actual==set(manifest['files']),'Evidence inventory changed')
    for name,digest in manifest['files'].items():
        f=ROOT/name
        need(not f.is_symlink() and sha256(f.read_bytes()).hexdigest()==digest,'Immutable evidence mismatch: '+name)
    review=ROOT/'evidence/review'
    for row in json.loads((review/'FILES.json').read_text())['files']:
        f=review/row['path']
        need(f.stat().st_size==row['bytes'] and sha256(f.read_bytes()).hexdigest()==row['sha256'],'Independent freeze mismatch: '+row['path'])
    freeze=json.loads((review/'FREEZE.json').read_text())
    need(sha256((review/'FILES.json').read_bytes()).hexdigest()==freeze['files_sha256'],'Review manifest pin changed')
    need(sha256((review/'REVIEW.md').read_bytes()).hexdigest()==freeze['review_sha256'],'Review prose pin changed')
    author=review/'author'
    need(sha256((author/'FREEZE.json').read_bytes()).hexdigest()==freeze['reviewed_author_freeze_sha256'],'Reviewed author freeze changed')
    for name,digest in json.loads((author/'FREEZE.json').read_text())['files'].items():
        need(sha256((author/name).read_bytes()).hexdigest()==digest,'Original author pin changed: '+name)
    for row in json.loads((ROOT/'CAPTURE-BINDINGS.json').read_text())['files']:
        need(sha256((ROOT/row['capture']).read_bytes()).hexdigest()==row['sha256'],'Raw source capture pin changed')
    return manifest

def run_script(script,local_module_directory=None):
    cmd=[sys.executable,'-I']
    if sys.flags.optimize:
        cmd.append('-O')
    cmd+=['-W','error','-B']
    if local_module_directory is None:
        cmd.append(str(script))
    else:
        # Only the authenticated private author directory is added. The unchanged
        # compiler-point script imports its sibling check_merge under isolated Python.
        driver="import runpy,sys;sys.path.insert(0,sys.argv[1]);runpy.run_path(sys.argv[2],run_name='__main__')"
        cmd+=['-c',driver,str(local_module_directory),str(script)]
    return subprocess.run(cmd,check=True,capture_output=True,timeout=150).stdout

def main():
    manifest=authenticate()
    original=ROOT/'evidence/review'
    with tempfile.TemporaryDirectory(prefix='one-fusion-target-') as temporary:
        review=Path(temporary)/'review'
        shutil.copytree(original,review)
        merge=run_script(review/'author/check_merge.py')
        point=run_script(review/'author/check_compiler_point.py',review/'author')
        independent=run_script(review/'check_independent.py')
        for data,names in [(merge,['author/RESULT.json','author/RESULT-OPTIMIZED.json','MERGE-REPLAY.json','MERGE-REPLAY-OPTIMIZED.json']),
                           (point,['author/COMPILER-POINT.json','author/COMPILER-POINT-OPTIMIZED.json','POINT-REPLAY.json','POINT-REPLAY-OPTIMIZED.json']),
                           (independent,['INDEPENDENT.json','INDEPENDENT-OPTIMIZED.json'])]:
            for name in names:
                need(data==(original/name).read_bytes(),'Full regenerated receipt differs: '+name)
        need(all((review/f.relative_to(original)).read_bytes()==f.read_bytes() for f in original.rglob('*') if f.is_file()),'Private frozen copy changed')
    p=json.loads(point)
    need(not p['physical_witness_supplied'] and not p['compiler_executed'],'Conditional admission boundary changed')
    print(json.dumps({
      'status':'PASS_CONDITIONAL_ONE_FUSION_CONSTRUCTION_TARGET_ONLY',
      'immutable_evidence_files':len(manifest['files']),
      'reviewed_report_sha256':sha256((original/'author/REPORT.md').read_bytes()).hexdigest(),
      'independent_review_sha256':sha256((original/'REVIEW.md').read_bytes()).hexdigest(),
      'merge_receipt_sha256':sha256(merge).hexdigest(),
      'compiler_point_receipt_sha256':sha256(point).hexdigest(),
      'independent_receipt_sha256':sha256(independent).hexdigest(),
      'candidate':p['kappa'],
      'tested':p['tested'],
      'hypothetical_paid_delta':{'H1':-36,'H2':18},
      'physical_pair_supplied':False,
      'compiler_executed':False,
      'scope':'Source-bound static census and exact scalar conditional target under retained contracts. No literal pair/phase/raw-dual/native/compiler/caller or new kappa admission.'
    },indent=2,sort_keys=True))

if __name__=='__main__':
    main()
