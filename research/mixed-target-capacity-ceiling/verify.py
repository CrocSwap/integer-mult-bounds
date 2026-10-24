#!/usr/bin/env python3
"""Portable exact scalar-source/invoice replay; no capacity theorem or native replay."""
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

def command(script):
    args=[sys.executable,'-I']
    if sys.flags.optimize:
        args.append('-O')
    return args+['-W','error','-B',str(script)]

def authenticate():
    m=json.loads((ROOT/'EVIDENCE.json').read_text())
    actual={str(f.relative_to(ROOT)) for f in (ROOT/'evidence').rglob('*') if f.is_file()}
    need(actual==set(m['files']), 'Evidence inventory differs')
    for name,digest in m['files'].items():
        p=ROOT/name
        need(not p.is_symlink() and sha256(p.read_bytes()).hexdigest()==digest,
             'Immutable evidence mismatch: '+name)
    review=ROOT/'evidence/independent-review'
    for row in json.loads((review/'FILES.json').read_text())['files']:
        p=review/row['path']
        need(p.stat().st_size==row['bytes'] and sha256(p.read_bytes()).hexdigest()==row['sha256'],
             'Original independent freeze differs: '+row['path'])
    freeze=json.loads((review/'FREEZE.json').read_text())
    need(sha256((review/'FILES.json').read_bytes()).hexdigest()==freeze['files_sha256'], 'Review FILES pin differs')
    need(sha256((review/'REVIEW.md').read_bytes()).hexdigest()==freeze['review_sha256'], 'Review prose pin differs')
    author=ROOT/'evidence/author'
    need((author/'REPORT.md').read_bytes()==(review/'frozen/REVIEWED-REPORT.md').read_bytes(), 'Report is not reviewed bytes')
    need(sha256((author/'REPORT.md').read_bytes()).hexdigest()==freeze['reviewed_report_sha256'], 'Reviewed report pin differs')
    need((author/'SOURCES.json').read_bytes()==(review/'frozen/AUTHOR-SOURCES-AT-FREEZE.json').read_bytes(), 'Current author metadata capture differs')
    need((author/'check_source.py').read_bytes()==(review/'frozen/AUTHOR-check_source.py').read_bytes(), 'Author checker capture differs')
    return m

def main():
    m=authenticate()
    author=ROOT/'evidence/author'
    review=ROOT/'evidence/independent-review'
    # Independent checker only reads frozen CODE/NORMALIZERS and prints JSON.
    independent=subprocess.run(command(review/'check_evidence.py'),check=True,capture_output=True,timeout=45).stdout
    for name in ['RESULT.json','RESULT-OPTIMIZED.json']:
        need(independent==(review/name).read_bytes(), 'Full independent receipt differs: '+name)
    # Author checker resolves ROOT from its original output location. Preserve that
    # layout in private scratch and retain every original source path/output field.
    with tempfile.TemporaryDirectory(prefix='mixed-capacity-') as temporary:
        temp=Path(temporary)
        sources=temp/'outputs/released-operator-intersection-20261023/frozen'
        sources.mkdir(parents=True)
        for name in ['CODE.json','NORMALIZERS.json']:
            shutil.copyfile(review/'frozen'/name,sources/name)
        work=temp/'outputs/mixed-target-input-encoder-20261023'
        work.mkdir()
        shutil.copyfile(author/'check_source.py',work/'check_source.py')
        source=subprocess.run(command(work/'check_source.py'),check=True,capture_output=True,timeout=45).stdout
        for name in ['SOURCE-CHECK.json','SOURCE-CHECK-OPTIMIZED.json']:
            need(source==(author/name).read_bytes(), 'Full author source receipt differs: '+name)
        need(all((sources/name).read_bytes()==(review/'frozen'/name).read_bytes() for name in ['CODE.json','NORMALIZERS.json']), 'Private source changed')
    scalar=json.loads(independent)
    print(json.dumps({
      'status':'PASS_SCALAR_SOURCE_AND_MIXED_INVOICE_ONLY',
      'immutable_evidence_files':len(m['files']),
      'reviewed_report_sha256':sha256((author/'REPORT.md').read_bytes()).hexdigest(),
      'independent_review_sha256':sha256((review/'REVIEW.md').read_bytes()).hexdigest(),
      'independent_scalar_receipt_sha256':sha256(independent).hexdigest(),
      'author_source_receipt_sha256':sha256(source).hexdigest(),
      'source_edges':scalar['source_edges'],
      'scalar_controls':len(scalar['controls']),
      'optimistic_target_mass':scalar['optimistic_target_mass'],
      'paid_mass':scalar['paid_mass'],
      'scope':'Exact retained scalar source tables and invoice arithmetic only. Independently reviewed written proof supplies m17<=112 and strict all0<C<1 necessary moment stop under fixed finite complete-product supports including target charts. No native/operator/compiler/caller or kappa replay.'
    },indent=2,sort_keys=True))

if __name__=='__main__':
    main()
