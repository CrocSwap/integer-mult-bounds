"""Replay a source-bound copy of the frozen baseline with payload-based receipts.

Only the copied unsplit receipt's word hash and its matching expected digest
change. The original 14-file baseline is verified before and after, never edited.
Usage: python3 -B baseline_portable.py OUTPUT [--baseline PATH] [--bit PATH]
       [--bit-parent PATH] [--complex PATH]. No stronger supplier is needed.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import copy
import difflib
import gzip
import json
import os
import subprocess
import sys

assert __debug__ and sys.version_info >= (3,12)
HERE=Path(__file__).resolve().parent
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def encoded(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def write(p,x):Path(p).write_bytes(encoded(x))

def verify_package():
    rows=[line.split(None,1)for line in (HERE/'MANIFEST.sha256').read_text().splitlines()]
    assert len({row[1]for row in rows})==len(rows)
    for want,name in rows:
        p=HERE/name
        assert p.resolve().is_relative_to(HERE) and not p.is_symlink()
        assert digest(p)==want,name


def prepare(baseline, destination):
    pins=read(HERE/'SOURCE.json')['baseline']
    assert digest(baseline/'MANIFEST.sha256')==pins['manifest_sha256']
    for name,want in pins['files'].items():assert digest(baseline/name)==want,name
    assert not destination.exists();destination.mkdir()
    for name in pins['files']:(destination/name).write_bytes((baseline/name).read_bytes())
    expected=read(baseline/'EXPECTED.json')
    reference=HERE/'baseline-unsplit-reference.json'
    assert digest(reference)==expected['unsplit_receipt_sha256']
    old_receipt=read(reference);canonical=copy.deepcopy(old_receipt)
    canonical['word_sha256']=expected['word_sha256']
    code=(baseline/'unsplit_bit.py').read_text()
    old='word_sha256=sha(WORD)'
    new='word_sha256=hashlib.sha256(gzip.decompress(WORD.read_bytes())).hexdigest()'
    assert code.count(old)==1
    changed=code.replace(old,new)
    expected['unsplit_receipt_sha256']=sha256(encoded(canonical)).hexdigest()
    changes={'unsplit_bit.py':changed.encode(),'EXPECTED.json':encoded(expected)}
    diffs=[]
    for name,data in changes.items():
        before=(baseline/name).read_bytes();(destination/name).write_bytes(data)
        diffs.append(dict(path=name,before_sha256=sha256(before).hexdigest(),
            after_sha256=sha256(data).hexdigest(),
            unified_diff=''.join(difflib.unified_diff(before.decode().splitlines(True),data.decode().splitlines(True),
                fromfile='frozen/'+name,tofile='portable-copy/'+name))))
    members=sorted(n for n in pins['files']if n!='MANIFEST.sha256')
    (destination/'MANIFEST.sha256').write_text(''.join(digest(destination/n)+'  '+n+'\n'for n in members))
    for name in pins['files']:
        if name not in {*changes,'MANIFEST.sha256'}:assert (destination/name).read_bytes()==(baseline/name).read_bytes()
    return canonical,dict(status='SOURCE_BOUND_GZIP_PAYLOAD_RECEIPT_ADAPTER',
        source_manifest_sha256=pins['manifest_sha256'],copy_manifest_sha256=digest(destination/'MANIFEST.sha256'),
        old_receipt_sha256=digest(reference),canonical_receipt_sha256=sha256(encoded(canonical)).hexdigest(),
        source_files_changed=diffs,
        scope='Container metadata is excluded from the word identity; every original mathematical, native, geometry, source and finite assertion remains enabled in the copied full replay.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('output',type=Path)
    ap.add_argument('--baseline',type=Path,default=HERE.parent/'e8-nine-stage-composition')
    ap.add_argument('--bit',type=Path,default=HERE.parent/'e8-bit-helper-reuse')
    ap.add_argument('--bit-parent',type=Path,default=HERE.parent/'e8-bit-seven-stage')
    ap.add_argument('--complex',type=Path,default=HERE.parent/'nine-stage-complex-e8')
    a=ap.parse_args();out,baseline,bit,parent,cx=(p.resolve()for p in (a.output,a.baseline,a.bit,a.bit_parent,a.complex))
    verify_package();assert not out.exists()
    for p in (HERE,baseline,bit,parent,cx):assert not out.is_relative_to(p)
    for p in (out,baseline,bit,parent,cx,Path(sys.executable).resolve()):assert not any(c.isspace()for c in str(p))
    out.mkdir(parents=True);canonical,report=prepare(baseline,out/'source')
    write(out/'SOURCE-DIFFS.json',report)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for key in ('PYTHONOPTIMIZE','PR315','CX_SOURCE_PINS','CX_PINS','CX_RECORD','CX_RECEIPT','B3_OUT'):env.pop(key,None)
    env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
    with (out/'replay.log').open('w')as log:
        subprocess.run([sys.executable,'-B',str(out/'source/verify.py'),str(out/'replay'),
            '--bit',str(bit),'--bit-parent',str(parent),'--complex',str(cx)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    actual=read(out/'replay/unsplit-bit/RECEIPT.json');assert actual==canonical
    raw=(out/'replay/bit/word.json').read_bytes();assert sha256(raw).hexdigest()==actual['word_sha256']
    gz=(out/'replay/bit/word.json.gz').read_bytes();assert gzip.decompress(gz)==raw
    controls=[]
    for os_byte in (3,19,255):
        altered=bytearray(gz);altered[9]=os_byte
        assert gzip.decompress(altered)==raw
        controls.append(dict(gzip_os_byte=os_byte,payload_sha256=sha256(gzip.decompress(altered)).hexdigest()))
    for name,want in read(HERE/'SOURCE.json')['baseline']['files'].items():assert digest(baseline/name)==want,name
    result=dict(status='PASS_FULL_PORTABLE_BASELINE_COPY_REPLAY',
        source_manifest_sha256=report['source_manifest_sha256'],copy_manifest_sha256=report['copy_manifest_sha256'],
        source_diffs_sha256=digest(out/'SOURCE-DIFFS.json'),canonical_unsplit_receipt_sha256=digest(out/'replay/unsplit-bit/RECEIPT.json'),
        baseline_receipt_sha256=digest(out/'replay/RECEIPT.json'),kappa=read(out/'replay/RECEIPT.json')['kappa'],
        gzip_metadata_controls=controls,source_unchanged=True)
    verify_package();write(out/'RECEIPT.json',result);print(result['status'],result['kappa'],flush=True)


if __name__=='__main__':main()
