#!/usr/bin/env python3
"""Verify the packed PR187 bit supplier with PR193's complex supplier, offline."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,subprocess,sys
if sys.flags.optimize:raise SystemExit('Assertions required')
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent
import packing,arithmetic,audit,controls


def serial(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serial(v) for v in value]
    return value


def run(root,script,*args):
    subprocess.run([sys.executable,'-B',str(root/script),*args],cwd=root,check=True,
                   env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complex-root',type=Path,required=True,help='Checkout of the pinned PR193 commit')
    parser.add_argument('--bit-root',type=Path,required=True,help='Checkout of the pinned PR187 commit')
    parser.add_argument('--full',action='store_true',help='Regenerate both suppliers and actual packing')
    parser.add_argument('--write',action='store_true',help='Regenerate certificate; requires --full')
    args=parser.parse_args();assert not args.write or args.full
    ROOT=args.complex_root.resolve()
    source=json.loads((HERE/'SOURCE.json').read_text())
    head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
    assert head==source['complex_commit'],'Wrong complex checkout commit'
    for name,expected in source['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,('Changed source',name)
    inherited=json.loads((ROOT/'research/source-assisted-v4/SOURCE.json').read_text())
    for name,expected in inherited['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,('Changed complex dependency',name)
    bit=args.bit_root.resolve()
    head=subprocess.check_output(['git','-C',str(bit),'rev-parse','HEAD'],text=True).strip()
    assert head==source['bit_commit'],'Wrong bit checkout commit'
    manifest_path=bit/'research/source-assisted-bit-bootstrap/SOURCE.json'
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest()==source['bit_manifest_sha256']
    manifest=json.loads(manifest_path.read_text())
    inventory=dict(manifest['repository_files'])
    inventory.update({'research/source-assisted-bit-bootstrap/'+name:sha
                      for name,sha in manifest['package_files'].items()})
    for name,expected in inventory.items():
        assert hashlib.sha256((bit/name).read_bytes()).hexdigest()==expected,('Changed bit dependency',name)
    if args.full:
        run(ROOT,'research/source-assisted-v4/verify.py')
        run(bit,'research/source-assisted-bit-bootstrap/verify.py','--full')
        physical=packing.build(bit)
    else:
        physical=json.loads((HERE/'certificate.json').read_text())['physical']
    result=arithmetic.build(ROOT,bit,physical)
    baseline=json.loads((bit/'research/source-assisted-bit-bootstrap/certificate.json').read_text())
    independent=audit.run(result,baseline['profile'])
    record=dict(physical=physical,arithmetic=result,independent=independent,
                bank_controls=controls.run(),immutable_bit_files=len(inventory)+1)
    out=serial(record)
    if args.write:(HERE/'certificate.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:assert out==json.loads((HERE/'certificate.json').read_text()),'Certificate differs'
    print('PASS exact packed profile, two moment engines, finite leaf composition, 47 constraints and seven margins')
    print('conditional kappa = '+out['arithmetic']['after_packing']['kappa'])


if __name__=='__main__':main()
