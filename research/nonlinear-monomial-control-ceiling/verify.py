#!/usr/bin/env python3
"""Portable finite support discriminator; all-width theorem remains written proof."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parent

def need(ok, why):
    if not ok:
        raise ValueError(why)

def authenticate():
    manifest=json.loads((ROOT/'EVIDENCE.json').read_text())
    actual={str(f.relative_to(ROOT)) for f in (ROOT/'evidence').rglob('*') if f.is_file()}
    need(actual==set(manifest['files']), 'Evidence file inventory differs')
    for name,digest in manifest['files'].items():
        p=ROOT/name
        need(not p.is_symlink() and sha256(p.read_bytes()).hexdigest()==digest,
             'Frozen evidence mismatch: '+name)
    review=ROOT/'evidence/proof-review'
    for row in json.loads((review/'FILES.json').read_text())['files']:
        p=review/row['path']
        need(p.stat().st_size==row['bytes'] and sha256(p.read_bytes()).hexdigest()==row['sha256'],
             'Original proof-review capture mismatch: '+row['path'])
    finite=ROOT/'evidence/finite-check'
    for name,digest in json.loads((finite/'FREEZE.json').read_text())['files'].items():
        need(sha256((finite/name).read_bytes()).hexdigest()==digest,
             'Original finite-check freeze mismatch: '+name)
    proof=review/'frozen/REVIEWED-PROOF.md'
    need(sha256(proof.read_bytes()).hexdigest()==json.loads((review/'RESULT.json').read_text())['reviewed_proof_sha256'],
         'Written review binds a different proof')
    return manifest

def main():
    manifest=authenticate()
    review=ROOT/'evidence/proof-review'
    finite=ROOT/'evidence/finite-check'
    # Unchanged checker derives ROOT from its own location; mirror exactly the
    # four original source paths in private scratch. All generated files stay there.
    with tempfile.TemporaryDirectory(prefix='nonlinear-support-') as temporary:
        temp=Path(temporary)
        logical={
          'outputs/nonlinear-monomial-control-ceiling-20261023/PROOF.md':review/'frozen/REVIEWED-PROOF.md',
          'outputs/released-operator-intersection-20261023/PROOF.md':review/'frozen/PREDECESSOR-PROOF.md',
          'outputs/released-operator-intersection-20261023/SOURCES.json':review/'frozen/PREDECESSOR-SOURCES.json',
          'outputs/released-operator-intersection-20261023/frozen/PHYSICAL.md':review/'frozen/PHYSICAL.md'}
        for name,source in logical.items():
            target=temp/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
        work=temp/'outputs/nonlinear-monomial-support-check-20261023'
        work.mkdir()
        shutil.copyfile(finite/'check_support.py',work/'check_support.py')
        command=[sys.executable,'-I']
        if sys.flags.optimize:
            command.append('-O')
        command+=['-W','error','-B',str(work/'check_support.py')]
        replay=subprocess.run(command,cwd=temp,check=True,capture_output=True,timeout=45)
        for stem in ['RESULT','MATRICES']:
            data=(work/(stem+'.json')).read_bytes()
            for suffix in ['', '-OPTIMIZED']:
                need(data==(finite/(stem+suffix+'.json')).read_bytes(),
                     'Complete generated '+stem+' differs from frozen '+suffix+' receipt')
        need(all((temp/name).read_bytes()==source.read_bytes() for name,source in logical.items()),
             'Private source capture changed')
        result=json.loads((work/'RESULT.json').read_text())
        matrices=(work/'MATRICES.json').read_bytes()
        compact=json.loads(replay.stdout)
    print(json.dumps({
      'status':'PASS_PORTABLE_NONLINEAR_FINITE_SUPPORT_ONLY',
      'immutable_evidence_files':len(manifest['files']),
      'written_proof_sha256':sha256((review/'frozen/REVIEWED-PROOF.md').read_bytes()).hexdigest(),
      'independent_review_sha256':sha256((review/'REVIEW.md').read_bytes()).hexdigest(),
      'finite_result_sha256':sha256((finite/'RESULT.json').read_bytes()).hexdigest(),
      'finite_matrices_sha256':sha256(matrices).hexdigest(),
      'positive_examples':compact['positive_examples'],
      'terminal_sandwiches':result['terminal_nonmonomial_count'],
      'scope':'Finite exact16x16 support examples and controls only. Independently reviewed written proof supplies sufficiently-large-width fixed finite complete-product support theorem. No17-axis/all-width phase/native/compiler/caller or kappa replay.'
    },indent=2,sort_keys=True))

if __name__=='__main__':
    main()
