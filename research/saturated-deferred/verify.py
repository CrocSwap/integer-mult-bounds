#!/usr/bin/env python3
"""Rebuild the saturated deferred witness in a disposable tree, then compare every result."""
import sys
if not __debug__:
    raise RuntimeError('Assertions required')
sys.dont_write_bytecode = True
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json, os
from pathlib import Path
import shutil, subprocess, tempfile, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVES = ROOT/'references/signed-recursion'
from pin_sources import check as check_sources

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def stable(value):
    if isinstance(value, dict):
        return {k:stable(v) for k,v in value.items() if k != 'elapsed'}
    if isinstance(value, list):
        return [stable(v) for v in value]
    return value

def equal(actual, expected):
    assert stable(json.loads(actual.read_text())) == stable(json.loads(expected.read_text())), expected.name

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true', help='Write only timing receipt and execution log')
    args = parser.parse_args()
    for dependency, expected in [('sympy','1.14.0'), ('mpmath','1.3.0')]:
        assert version(dependency) == expected, 'Install '+dependency+'=='+expected
    manifest = check_sources()
    before = {name:digest(ROOT/name) for name in manifest['files']}
    before[str((HERE/'SOURCE.json').relative_to(ROOT))] = digest(HERE/'SOURCE.json')
    before[str((HERE/'independent-audit.json').relative_to(ROOT))] = digest(HERE/'independent-audit.json')
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    steps, exit_code, error = [], 0, None
    if args.record:
        logpath = HERE/'verification.log'
    else:
        with tempfile.NamedTemporaryFile(prefix='saturated-deferred-', suffix='.log', delete=False) as stream:
            logpath = Path(stream.name)
    with tempfile.TemporaryDirectory(prefix='saturated-deferred-') as directory, logpath.open('w') as log:
        work = Path(directory)
        # Root layout is preserved so unmodified upstream scripts resolve their
        # exact inherited modules. Only the selected schedule is substituted.
        shutil.copytree(ARCHIVES/'pr97', work, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
        pkg = work/'research/deferred-signed'
        source99 = ARCHIVES/'pr99/research/nondegenerate-readout-saturation'
        p99 = work/'research/nondegenerate-readout-saturation'
        shutil.copytree(source99, p99, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
        chosen = p99/'experiments/round7-review/saturated-Z.json.gz'
        assert chosen.read_bytes() == (HERE/'schedule.json.gz').read_bytes()
        shutil.copyfile(chosen, pkg/'swapnil-round7/certificates/round7/deferred_23.json.gz')
        native = pkg/'swapnil-round7'
        jobs = [('saturation exact geometry and scalar controls', [p99/'verify.py', '--full'], p99)]
        for name in ('round7_literal_frame_ledger', 'round7_tensor_endpoint_controls',
                     'round6_complex_interface_controls', 'round6_complex_literal_ledger',
                     'check_complex_identity', 'round7_balanced_assembly_candidate'):
            jobs.append((name, [pkg/(name+'.py')], pkg))
        for name, arguments in [('check_word',['23']), ('check_lifted',['23']),
                                ('check_stair',['23']), ('check_stair_control',['23','--control'])]:
            script = 'check_stair' if name == 'check_stair_control' else name
            jobs.append((name, [native/'independent/deferred-readout'/(script+'.py'), *arguments], native))
        jobs += [('complete exact composition', [HERE/'compose.py', '--work', work, '--output', work/'certificate.json'], ROOT),
                 ('independent arithmetic and controls', [HERE/'independent_check.py', '--certificate', work/'certificate.json'], ROOT)]
        try:
            for name, arguments, cwd in jobs:
                print('RUN', name, flush=True)
                log.write('\nRUN '+name+'\n');log.flush()
                tick = time.monotonic()
                result = subprocess.run([sys.executable, *map(str, arguments)], cwd=cwd,
                                        stdout=log, stderr=subprocess.STDOUT,
                                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
                steps.append(dict(step=name, exit_code=result.returncode, elapsed_seconds=round(time.monotonic()-tick,3)))
                if result.returncode:
                    raise RuntimeError(name+' failed with exit '+str(result.returncode))
                if name == 'check_stair_control':
                    log.flush()
                    assert 'certified=False' in logpath.read_text()
            for fresh, frozen in [('round7-literal-ledger/result.json','bit-ledger.json'),
                                  ('round6-complex-literal-ledger/result.json','complex-ledger.json'),
                                  ('round7-tensor-endpoint-controls.json','tensor-controls.json'),
                                  ('round6-complex-interface-controls.json','complex-controls.json'),
                                  ('round7-balanced-assembly-candidate.json','bridge.json')]:
                equal(pkg/fresh, HERE/frozen)
            equal(work/'certificate.json', HERE/'certificate.json')
        except (AssertionError, RuntimeError) as failure:
            exit_code, error = 1, repr(failure)
            log.write('\nERROR '+error+'\n')
        changed = [name for name,value in before.items() if not (ROOT/name).exists() or digest(ROOT/name)!=value]
        if changed:
            exit_code = 1
        log.write('\nchanged_frozen_files='+json.dumps(changed)+'\nexit_code='+str(exit_code)+'\n')
    if not exit_code:
        check_sources()
    certificate = json.loads((HERE/'certificate.json').read_text())
    receipt = dict(status='PASS' if not exit_code else 'FAIL', started_utc=started,
                   finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=round(time.monotonic()-start,3),
                   exit_code=exit_code, error=error, steps=steps, changed_frozen_files=changed,
                   source_manifest_sha256=digest(HERE/'SOURCE.json'), certificate_sha256=digest(HERE/'certificate.json'),
                   kappa=certificate['kappa'], log_sha256=digest(logpath),
                   scope='Fresh saturated frames/scalar controls, both reflected literal networks and tensor/complex endpoint controls, regenerated bridge and two exact arithmetic implementations. Inherited analytic and fixed-tape assumptions remain conditional.')
    if args.record:
        (HERE/'validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('Log:',logpath,flush=True)
    if exit_code:
        print('\n'.join(logpath.read_text().splitlines()[-60:]),flush=True)
    print('PASS saturated-deferred finite gate' if not exit_code else 'FAIL saturated-deferred finite gate',flush=True)
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
