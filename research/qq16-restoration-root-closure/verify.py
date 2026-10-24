#!/usr/bin/env python3
"""Check exact sources, exposed proof clauses and semantic alias controls."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from bundle import materialize, need
import contract


def run(runtime_controls=False):
    with tempfile.TemporaryDirectory(prefix='qq16-contract-') as folder:
        base=Path(folder)
        hashes,outer=materialize(base)
        machine=(base/'macro_machine.py').read_text()
        binding=(base/'macro_binding.py').read_text()
        session=next(data.decode() for key,data in outer.items() if key.endswith(':session.py'))
        structural=contract.check(machine,binding,session)
        rejected=contract.controls(machine,binding,session)
    pins=json.loads((HERE/'SOURCE-EXPORTS.json').read_text())
    for name,digest in pins['sha256'].items():
        need(sha256((HERE/name).read_bytes()).hexdigest()==digest,'Retained source export '+name)
    result={'status':'PASS_SOURCE_ROOT_CONTRACT','source_hashes':hashes,
            'contract':structural,'rejecting_source_controls':rejected}
    if runtime_controls:
        expectations={'binding_history':'Only the current generation at a closed dispatch',
                      'boundary_backedge':'Only the current generation at a closed dispatch',
                      'program_backedge':'Literal generation schemas'}
        failures={}
        for fault,message in expectations.items():
            completed=subprocess.run([sys.executable,'-I','-B',str(HERE/'calibrate.py'),'--fault',fault],
                                     capture_output=True,text=True,timeout=90)
            need(completed.returncode!=0 and completed.stderr.rstrip().endswith('ValueError: '+message),
                 'Expected semantic rejection for '+fault+': '+completed.stderr[-1000:])
            failures[fault]=message
        result['rejecting_runtime_controls']=failures
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-controls',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    raw=json.dumps(run(args.runtime_controls),indent=2,sort_keys=True)+'\n'
    if args.output:args.output.write_text(raw)
    else:print(raw,end='')
