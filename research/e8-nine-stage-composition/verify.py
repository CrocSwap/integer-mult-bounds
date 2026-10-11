"""Fresh replay of the unchanged PR376 bit and PR377 complex suppliers.

Usage: python3 -B verify.py /fresh/output [--bit PATH] [--bit-parent PATH]
       [--complex PATH]. Requires Python >=3.12 for the full pinned bit recipe.
Prepared with OpenAI Codex assistance. Apache-2.0. No network is used.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import copy
import json
import os
import subprocess
import sys
import assembly
import complex_supplier

assert __debug__, 'Run without -O'
assert sys.version_info >= (3,12), 'The pinned full bit recipe requires Python >=3.12'
HERE = Path(__file__).resolve().parent
def digest(p): return sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def write(p,x): Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')


def manifest(directory, name):
    if name == 'MANIFEST.json':
        expected = read(directory/name)['files']
    else:
        pairs = [line.split(None,1) for line in (directory/name).read_text().splitlines()]
        expected = {relative.strip().removeprefix('./'):want for want,relative in pairs}
        assert len(expected) == len(pairs)
    for relative,want in expected.items():
        p=directory/relative
        assert p.resolve().is_relative_to(directory) and not p.is_symlink()
        assert digest(p)==want,('source hash mismatch',relative)
    return len(expected)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--bit',type=Path,default=HERE.parent/'e8-bit-helper-reuse')
    parser.add_argument('--bit-parent',type=Path,default=HERE.parent/'e8-bit-seven-stage')
    parser.add_argument('--complex',type=Path,default=HERE.parent/'nine-stage-complex-e8')
    args=parser.parse_args()
    out,bit,parent,cx=(p.resolve() for p in (args.output,args.bit,args.bit_parent,args.complex))
    assert not out.exists(),'Use a fresh output directory'
    for p in (HERE,bit,parent,cx):
        assert not out.is_relative_to(p)
    for p in (out,bit,parent,cx,Path(sys.executable).resolve()):
        assert not any(c.isspace() for c in str(p)),'Inherited bit shell requires paths without whitespace'
    manifest(HERE,'MANIFEST.sha256')
    source,expected=read(HERE/'SOURCE.json'),read(HERE/'EXPECTED.json')
    for relative,item in source['row_argument_sources']['files'].items():
        assert digest(HERE/relative)==item['sha256']
    counts={}
    for key,p in [('bit',bit),('bit_parent',parent),('complex',cx)]:
        item=source[key]
        assert digest(p/item['manifest'])==item['manifest_sha256']
        counts[key]=manifest(p,item['manifest'])
        for relative,want in item.get('files',{}).items():assert digest(p/relative)==want
    for name in ('moment.py','base_two_moment.py','outer.py'):
        assert digest(cx/'work/pr361/code/engines'/name)==digest(parent/'code/pricing'/name)
    out.mkdir(parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    for key in ('PYTHONOPTIMIZE','PR315','CX_SOURCE_PINS','CX_PINS','CX_RECORD','CX_RECEIPT','B3_OUT'):
        env.pop(key,None)
    env['PATH']=str(Path(sys.executable).parent)+os.pathsep+env.get('PATH','')
    checks=[]
    def run(name,*argv):
        print('CHECK',name,flush=True)
        with (out/(name+'.log')).open('w') as log:
            subprocess.run([sys.executable,'-B',*map(str,argv)],env=env,
                           stdout=log,stderr=subprocess.STDOUT,check=True)
        checks.append(name)
    run('fresh-bit',bit/'verify.py',out/'bit','--parent',parent)
    run('fresh-unsplit-bit',HERE/'unsplit_bit.py',parent,out/'bit',out/'unsplit-bit')
    run('fresh-complex',cx/'verify.py','--work',out/'complex')
    supplier=complex_supplier.run(cx,out/'complex')
    write(out/'complex-supplier.json',supplier)
    assert digest(out/'complex-supplier.json')==expected['supplier_sha256']
    split_priced,split_finite=read(out/'bit/kappa.json'),read(out/'bit/finite.json')
    priced,finite=read(out/'unsplit-bit/kappa-input.json'),read(out/'unsplit-bit/finite.json')
    assert digest(out/'unsplit-bit/RECEIPT.json')==expected['unsplit_receipt_sha256']
    assert finite['coefficient']==expected['finite_coefficient']
    assert digest(out/'bit/word.json')==expected['word_sha256']
    assert {name:digest(out/'bit/records'/name) for name in expected['records']}==expected['records']
    result=assembly.run(parent,priced,finite,supplier)
    write(out/'assembly.json',result)
    assert digest(out/'assembly.json')==expected['assembly_sha256']
    for key in ('kappa','bit_coarse','complex_coarse','binding'):assert result[key]==expected[key]
    original=assembly.run(parent,read(out/'bit/parent/kappa.json'),read(out/'bit/parent/finite.json'),supplier)
    write(out/'original-bit-assembly.json',original)
    assert digest(out/'original-bit-assembly.json')==expected['original_bit_assembly_sha256']
    assert assembly.Q(result['kappa']) > assembly.Q(original['kappa'])
    split=assembly.run(parent,split_priced,split_finite,supplier)
    write(out/'split-bit-assembly.json',split)
    assert digest(out/'split-bit-assembly.json')==expected['split_bit_assembly_sha256']
    assert assembly.Q(result['kappa']) > assembly.Q(split['kappa']) > assembly.Q(original['kappa'])
    controls=[]
    for name,mutate in [
        ('stale rank mass',lambda p,f:f.__setitem__('rank_mass',f['rank_mass']+1)),
        ('stale child count',lambda p,f:f.__setitem__('positive_rank_children',f['positive_rank_children']+1)),
        ('uncharged finite coefficient',lambda p,f:f.__setitem__('coefficient',0)),
        ('false one-level halving',lambda p,f:p.__setitem__('halving_degree',1)),
        ('missing internal depth charge',lambda p,f:f['row_reserve'].__setitem__('internal_coefficient',3137)),
    ]:
        p,f=copy.deepcopy(priced),copy.deepcopy(finite);mutate(p,f)
        try:assembly.run(parent,p,f,supplier)
        except AssertionError:controls.append(name)
        else:raise AssertionError('control accepted: '+name)
    checks+=['fresh-complex-interface-and-dual-moments','eight-finite-bootstraps-and-47-constraints','five-composition-controls']
    for key,p in [('bit',bit),('bit_parent',parent),('complex',cx)]:
        assert digest(p/source[key]['manifest'])==source[key]['manifest_sha256']
        manifest(p,source[key]['manifest'])
    receipt=dict(status='PASS_FRESH_R822_BIT_AND_NINE_STAGE_COMPLEX_COMPOSITION',
                 kappa=result['kappa'],bit_coarse=result['bit_coarse'],complex_coarse=result['complex_coarse'],
                 binding=result['binding'],finite_coefficient=finite['coefficient'],
                 checks=checks,rejected_controls=controls,source_files_checked=counts,
                 source=source,assembly_sha256=digest(out/'assembly.json'),
                 complex_supplier_sha256=digest(out/'complex-supplier.json'),
                 bit_receipt_sha256=digest(out/'bit/RECEIPT.json'),
                 original_bit_kappa=original['kappa'],
                 original_bit_assembly_sha256=digest(out/'original-bit-assembly.json'),
                 split_bit_kappa=split['kappa'],split_bit_assembly_sha256=digest(out/'split-bit-assembly.json'),
                 unsplit_receipt_sha256=digest(out/'unsplit-bit/RECEIPT.json'),
                 scope='Conditional composition only: retains both suppliers\' stated construction, compiler, row, precision, routing, recovery and analytic interfaces. No new Lean theorem, certificate-producer regeneration, signed E8 integer decoder or cover enumeration is claimed.')
    write(out/'RECEIPT.json',receipt)
    print(receipt['status'],result['kappa'],flush=True)


if __name__=='__main__':main()
