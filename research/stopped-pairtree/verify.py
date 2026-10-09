#!/usr/bin/env python3
"""Fresh complete selected finite gate; recording writes only run receipts."""
import sys
if not __debug__:
    raise RuntimeError('Assertions required')
sys.dont_write_bytecode = True
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json, os
from pathlib import Path
import subprocess, tempfile, time
from pin_sources import check as check_sources

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def digest(path):return sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args=parser.parse_args()
    manifest=check_sources()
    before={name:digest(ROOT/name)for name in manifest['files']}
    for name in ('SOURCE.json','physical-audit.json','interface-audit.json','literal-audit.json','independent-audit.json'):
        before[str((HERE/name).relative_to(ROOT))]=digest(HERE/name)
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    steps,exit_code,error=[],0,None
    if args.record:logpath=HERE/'verification.log'
    else:
        with tempfile.NamedTemporaryFile(prefix='stopped-pairtree-',suffix='.log',delete=False)as stream:logpath=Path(stream.name)
    with tempfile.TemporaryDirectory(prefix='stopped-pairtree-')as directory, logpath.open('w')as log:
        work=Path(directory)
        jobs=[('reproduce.py',['--work',work]),('physical_check.py',['--work',work]),
              ('literal_check.py',['--work',work]),('interface_check.py',[]),('compose.py',['--work',work,'--output',work/'certificate.json']),
              ('independent_check.py',['--certificate',work/'certificate.json']),('test_controls.py',[])]
        try:
            for script,arguments in jobs:
                print('RUN',script,flush=True);log.write('\nRUN '+script+'\n');log.flush();tick=time.monotonic()
                result=subprocess.run([sys.executable,str(HERE/script),*map(str,arguments)],cwd=ROOT,
                                      stdout=log,stderr=subprocess.STDOUT,
                                      env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
                steps.append(dict(step=script,exit_code=result.returncode,elapsed_seconds=round(time.monotonic()-tick,3)))
                if result.returncode:raise RuntimeError(script+' failed with exit '+str(result.returncode))
            assert (work/'certificate.json').read_bytes()==(HERE/'certificate.json').read_bytes(),'Fresh exact certificate differs'
        except (RuntimeError,AssertionError)as failure:
            exit_code,error=1,repr(failure);log.write('\nERROR '+error+'\n')
        changed=[name for name,value in before.items()if not(ROOT/name).exists()or digest(ROOT/name)!=value]
        if changed:exit_code=1
        log.write('\nchanged_frozen_files='+json.dumps(changed)+'\nexit_code='+str(exit_code)+'\n')
    if not exit_code:check_sources()
    certificate=json.loads((HERE/'certificate.json').read_text())
    receipt=dict(status='PASS'if not exit_code else'FAIL',started_utc=started,
                 finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-start,3),
                 exit_code=exit_code,error=error,steps=steps,changed_frozen_files=changed,
                 source_manifest_sha256=digest(HERE/'SOURCE.json'),certificate_sha256=digest(HERE/'certificate.json'),
                 log_sha256=digest(logpath),kappa=certificate['kappa'],
                 scope='Fresh original and selected scalar/frame/carrier producers, independent signed coefficient/frame/matching, literal role-program/inverse and finite factor/atom/wrapper audits, full paid recurrence/three-factor bridge/47 constraints/seven margins. PR104 atom-streaming, stopped ordinary interface, odd grid, balanced layout and retained all-size analytic/tape hypotheses remain explicit dependencies.')
    if args.record:(HERE/'validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('Log:',logpath,flush=True)
    if exit_code:print('\n'.join(logpath.read_text().splitlines()[-70:]),flush=True)
    print('PASS stopped-pairtree finite gate'if not exit_code else'FAIL stopped-pairtree finite gate',flush=True)
    return exit_code

if __name__=='__main__':sys.exit(main())
