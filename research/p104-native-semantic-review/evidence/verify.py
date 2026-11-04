"""Read-only, Git-free native admission delta checks; no historical suite."""
from pathlib import Path
from hashlib import sha256
import argparse
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent


def load(name):
    spec=importlib.util.spec_from_file_location('delta_driver_'+name,HERE/(name+'.py'))
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    return m


def result(receipts):
    return {'schema':'current-native-source-bound-admission-delta/1',
            'status':'PASS_EXACT_CURRENT_NATIVE_DELTA',
            'receipts':{name:sha256(raw.encode()).hexdigest() for name,raw in receipts.items()},
            'scope':'Author-side independent application evidence against the exact selected6030 source. All actual current emitted recipes receive an exact signed-Pauli and complete zero-column check; only39 unmatched operators and5 helper normalizations receive all512 columns. Current scalar and ownership endpoints are replayed independently. No new kappa, framework assumption discharge or external scientific admission.'}


def run(write=False):
    C=load('compare_maps');S=load('check_signatures');D=load('check_dense');R=load('check_scalar')
    comparison=C.run()
    results={'COMPARISON.json':comparison,'SIGNATURES.json':S.run(comparison),
             'DENSE.json':D.run(comparison),'SCALAR.json':R.run()}
    receipts={}
    for name,r in results.items():
        raw=json.dumps(r,sort_keys=True,indent=2)+'\n';receipts[name]=raw
        if write:(HERE/name).write_text(raw)
        else:C.need((HERE/name).read_text()==raw,'read-only exact receipt '+name)
    final=json.dumps(result(receipts),sort_keys=True,indent=2)+'\n'
    if write:(HERE/'RESULT.json').write_text(final)
    else:C.need((HERE/'RESULT.json').read_text()==final,'read-only complete result')
    print('PASS_EXACT_CURRENT_NATIVE_DELTA')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();run(a.write)
