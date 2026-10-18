"""New endpoint/wrapper/profile and exact-certificate negative controls."""
from copy import deepcopy
import contextlib
import gzip
import json
from pathlib import Path
import runpy
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(HERE))
from construct import read, encode, require, construct
from packing import verify as price


def main(output):
    # Retain mathematical inputs independently of the ephemeral full replay.
    expected = read(HERE/'EXPECTED.json')
    base = ROOT/'research/complex-k492-owner-repair'
    route = base/'vendor/multicold/vendor/pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    require(__debug__, 'Native controls require assertions')
    auditor = ROOT/'research/complex-sw4-frame8/local/hpe_audit_and_transport.py'
    audit = runpy.run_path(str(auditor))['run']
    source = output/'early8/positive-ck.json.gz'
    word = read(source)
    premix_count = len(expected['new_constructions']['positive-ck']['internal_premix'])
    cases = []
    changed = deepcopy(word);del changed['A'][:premix_count]
    cases.append(('omit_internal_premix',changed,'zero-frame precondition/compensation'))
    changed = deepcopy(word);changed['early_cleanup']=changed['early_cleanup'][2:]
    cases.append(('omit_early_tail_admission',changed,'cleanup on non-FULL end'))
    changed = deepcopy(word);changed['helper_final']['448']=changed['helper_final']['448'][:-1]
    cases.append(('declare_rank7_endpoint',changed,'hpe cone pre-check'))
    changed = deepcopy(word);changed['cleanup'][0][3]=0
    cases.append(('omit_one_restore_read',changed,'arbitrary-dirt endpoint'))
    changed = deepcopy(word);changed['report']['local_profile']['1']-=1
    cases.append(('undercharge_profile',changed,'paid local profile differs'))
    results = {}
    with tempfile.TemporaryDirectory(prefix='early8-controls-') as temporary:
        root = Path(temporary)
        for name,changed,reason in cases:
            path=root/(name+'.json.gz');path.write_bytes(gzip.compress(encode(changed),mtime=0))
            with (root/(name+'.log')).open('w',encoding='utf-8') as log,contextlib.redirect_stdout(log):
                try:
                    audit(path,route,root/name)
                except AssertionError as error:
                    require(reason in str(error),'Wrong native rejection: '+name+' '+str(error))
                    results[name]=str(error).split(':')[0]
                else:
                    raise ValueError('Native mutation accepted: '+name)
    model=expected['model'];model['local']={int(r):n for r,n in model['local'].items()}
    for key in ('widths','global','capacities'):
        model[key]={int(r):n for r,n in model[key].items()}
    for variant in model['variants'].values():
        for key in ('profile','widths'):
            variant[key]={int(r):n for r,n in variant[key].items()}
    certificate=read(HERE/'vendor/pr855/EXACT-CERTIFICATE.json')
    for name,change,reason in [
        ('raise_lambda',lambda c:c.update(lambda_units_1e30=c['lambda_units_1e30']+10**24),'Pattern'),
        ('raise_potential',lambda c:c['potentials'].__setitem__(22,c['potentials'][22]+1000),'Pattern potential'),
    ]:
        changed=deepcopy(certificate);change(changed)
        try:price(model,changed)
        except ValueError as error:
            require(reason in str(error),'Wrong potential rejection')
            results[name]='rejected'
        else:raise ValueError('Bad exact certificate accepted')
    changed=deepcopy(certificate);changed['potentials']=[0]*37
    require(price(model,changed)['excluded'] is False,'Integer correction control did not expose an uncertified mixture')
    results['omit_integer_correction']='not certified as excluded'
    print('PASS_EARLY8_CONTROLS',json.dumps(results,sort_keys=True))


if __name__=='__main__':
    main(Path(sys.argv[1]).resolve())
