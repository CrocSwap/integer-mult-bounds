#!/usr/bin/env python3
"""Read-only aggregate verification of the selected joint finite witness."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)


def digest(path):return sha256(path.read_bytes()).hexdigest()


def pins():
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    assert manifest['files'],'Empty source closure'
    values={name:digest(ROOT/name) for name in manifest['files']}
    assert values==manifest['files'],'Pinned construction or dependency bytes changed'
    return values


def run(relative):
    result=subprocess.run([sys.executable,'-B',str(HERE/relative)],text=True,capture_output=True)
    if result.returncode:raise ValueError(relative+' failed:\n'+result.stdout+result.stderr)
    return json.loads(result.stdout)


def build():
    print('Checking new signed complex word, all formal columns, frames and exact moment.',file=sys.stderr,flush=True)
    complex_result=run('complex/prove.py')
    print('Checking frozen PR168-v3 bit frames and aliases, full F2 identity and paid moment envelope.',file=sys.stderr,flush=True)
    bit_result=run('bit/prove.py')
    sys.path.insert(0,str(HERE/'arithmetic'))
    from certificate import certificate
    arithmetic=certificate(complex_result['profile'],complex_result['physical'])
    assert bit_result['coarse']['coarse_saving']==arithmetic['coarse_bit_saving']
    assert bit_result['coarse']['atom_beta']==arithmetic['atom_exponent']
    assert bit_result['coarse']['ordinary_saving']==arithmetic['actual_uniform_bit_saving']
    assert complex_result['moment']['complex_saving']==arithmetic['complex_saving']
    return dict(status='PASS conditional finite witness',kappa=arithmetic['kappa'],
        complex=complex_result,bit=bit_result,arithmetic=arithmetic,
        scope='Finite word, paid moments, full finite bridge and 47 strict arithmetic constraints; source-specified all-size contracts remain assumptions.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Authoring only: write the canonical derived certificate before freezing SOURCE.json')
    args=parser.parse_args()
    assert not sys.flags.optimize,'Assertions must remain enabled'
    before=None if args.write else pins()
    result=build();target=HERE/'certificate.json'
    if args.write:target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        assert result==json.loads(target.read_text()),'Canonical certificate does not reproduce'
        assert pins()==before,'Source closure changed during verification'
    print('PASS paired-cube-terminal-168 kappa='+result['kappa']+'; complete complex and bit words, 47 constraints, seven margins, and '+str(result['arithmetic']['adverse_control_count'])+' assembly controls.')


if __name__=='__main__':main()
