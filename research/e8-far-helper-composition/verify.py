"""Replay the frozen unsplit R822 baseline, then derive and admit PR378 helper composition.

Usage: python3 -B verify.py /fresh/output [--baseline PATH] [--bit PATH]
       [--bit-parent PATH] [--complex PATH] [--far PATH]. No network or binary witness needed.
Prepared with OpenAI Codex assistance. Apache-2.0; inherited notices apply.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import copy
import gzip
import importlib.util
import json
import os
import subprocess
import sys
import candidate_from378
import complex_supplier
import two_alias

assert __debug__, 'Run without -O'
assert sys.version_info >= (3,12)
HERE=Path(__file__).resolve().parent
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def manifest(directory):
    rows=[x.split(None,1)for x in (directory/'MANIFEST.sha256').read_text().splitlines()]
    assert len({x[1]for x in rows})==len(rows)
    for want,relative in rows:
        p=directory/relative
        assert p.resolve().is_relative_to(directory) and not p.is_symlink()
        assert digest(p)==want,relative
    return len(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    p.add_argument('--baseline',type=Path,default=HERE.parent/'e8-nine-stage-composition')
    p.add_argument('--bit',type=Path,default=HERE.parent/'e8-bit-helper-reuse')
    p.add_argument('--bit-parent',type=Path,default=HERE.parent/'e8-bit-seven-stage')
    p.add_argument('--complex',type=Path,default=HERE.parent/'nine-stage-complex-e8')
    p.add_argument('--far',type=Path,default=HERE.parent/'e8-complex-far-retiming')
    args=p.parse_args();out,baseline,bit,parent,cx,far=(q.resolve()for q in (args.output,args.baseline,args.bit,args.bit_parent,args.complex,args.far))
    assert not out.exists(),'Use a fresh output directory'
    for q in (HERE,baseline,bit,parent,cx,far):assert not out.is_relative_to(q)
    for q in (out,baseline,bit,parent,cx,far,Path(sys.executable).resolve()):
        assert not any(c.isspace()for c in str(q)),'Inherited bit shell requires paths without whitespace'
    manifest(HERE);source,expected=read(HERE/'SOURCE.json'),read(HERE/'EXPECTED.json')
    assert digest(baseline/'MANIFEST.sha256')==source['baseline']['manifest_sha256']
    manifest(baseline)
    for relative,want in source['baseline']['files'].items():assert digest(baseline/relative)==want
    assert digest(cx/'MANIFEST.json')==source['complex']['manifest_sha256']
    for relative,want in source['witness_modules'].items():assert digest(HERE/relative)==want
    assert digest(far/'MANIFEST.sha256')==source['far']['manifest_sha256']
    manifest(far)
    out.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for key in ('PYTHONOPTIMIZE','PR315','CX_SOURCE_PINS','CX_PINS','CX_RECORD','CX_RECEIPT','B3_OUT'):
        env.pop(key,None)
    env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
    env['PYTHON']=sys.executable
    checks=[]
    def run(name,*argv):
        print('CHECK',name,flush=True)
        with (out/(name+'.log')).open('w')as log:
            subprocess.run([sys.executable,'-B',*map(str,argv)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        checks.append(name)
    run('fresh-baseline',HERE/'baseline_portable.py',out/'baseline','--baseline',baseline,'--bit',bit,'--bit-parent',parent,'--complex',cx)
    print('CHECK fresh-far-source',flush=True)
    with (out/'fresh-far-source.log').open('w')as log:
        subprocess.run(['bash',str(far/'verify.sh'),str(out/'far')],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    checks.append('fresh-far-source-including-regeneration')
    run('fresh-derived-complex',HERE/'replay.py',cx,far,out/'derived')
    run('derived-source-span',far/'code/cxcheck.py',
        out/'derived/work/pr361/complex/gcert1-e8-r783.json.gz',far/'complex/gx')
    assert digest(out/'derived/candidate.json')==expected['candidate_sha256']
    assert digest(out/'derived/SOURCE-DIFFS.json')==expected['source_diffs_sha256']
    supplier=complex_supplier.run(cx,out/'derived');write(out/'complex-supplier.json',supplier)
    assert digest(out/'complex-supplier.json')==expected['supplier_sha256']
    A=load('r781_baseline_assembly',baseline/'assembly.py')
    priced,finite=read(out/'baseline/replay/unsplit-bit/kappa-input.json'),read(out/'baseline/replay/unsplit-bit/finite.json')
    result=A.run(parent,priced,finite,supplier);write(out/'assembly.json',result)
    assert digest(out/'assembly.json')==expected['assembly_sha256']
    for key in ('kappa','bit_coarse','complex_coarse','binding'):assert result[key]==expected[key]
    old=read(out/'baseline/replay/assembly.json')
    assert old['kappa']==expected['baseline_kappa'] and A.Q(result['kappa'])>A.Q(old['kappa'])
    controls=[]
    raw=(far/'data/gcert1-e8-r783-far.json.gz').read_bytes()
    bad=bytearray(raw);bad[-1]^=1
    try:candidate_from378.build(bytes(bad))
    except AssertionError:controls.append('changed pinned source')
    else:raise AssertionError('changed source accepted')
    retimed=json.loads(gzip.decompress(raw))
    for name,drop,use in [('wrong donor',706,269),('self substitution',706,706),('retained helper',504,268)]:
        try:two_alias.build(copy.deepcopy(retimed),drop,use)
        except AssertionError:controls.append(name)
        else:raise AssertionError('invalid alias accepted: '+name)
    checks+=['fresh-complex-moments-and-common-interface','eight-cutoffs-and-47-constraints','four-witness-controls']
    manifest(HERE);manifest(baseline)
    for relative,want in source['baseline']['files'].items():assert digest(baseline/relative)==want
    assert digest(cx/'MANIFEST.json')==source['complex']['manifest_sha256']
    manifest(far)
    assert digest(far/'MANIFEST.sha256')==source['far']['manifest_sha256']
    receipt=dict(status='PASS_FRESH_PR378_HELPER_NINE_COMPLEX_AND_UNSPLIT_R822_COMPOSITION',
        kappa=result['kappa'],bit_coarse=result['bit_coarse'],complex_coarse=result['complex_coarse'],
        binding=result['binding'],baseline_kappa=old['kappa'],
        absolute_gain=str(A.Q(result['kappa'])-A.Q(old['kappa'])),
        candidate_sha256=expected['candidate_sha256'],source_diffs_sha256=expected['source_diffs_sha256'],
        baseline_receipt_sha256=digest(out/'baseline/RECEIPT.json'),
        supplier_sha256=digest(out/'complex-supplier.json'),assembly_sha256=digest(out/'assembly.json'),
        source=source,checks=checks,rejected_controls=controls,
        scope='Conditional finite construction and composition. Inherits baseline bit admissions and PR377 compressed-window, phase, arbitrary-bank correlated-dirt, local/compiler, complete-stream, precision, row and analytic interfaces; no new Lean theorem or universal machine cutoff.')
    write(out/'RECEIPT.json',receipt);print(receipt['status'],result['kappa'],flush=True)


if __name__=='__main__':main()
