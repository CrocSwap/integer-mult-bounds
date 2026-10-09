#!/usr/bin/env python3
"""Run the complete fresh finite construction and independent acceptance gate."""
import sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import argparse,json,os,subprocess,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
from pin_sources import check,digest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--record',action='store_true');a=p.parse_args()
    manifest=check();before={name:digest(ROOT/name)for name in manifest['files']}
    for name in('SOURCE.json','independent-audit.json','bit-audit.json','gauge-audit.json','endpoint-audit.json'):
        before[str((HERE/name).relative_to(ROOT))]=digest(HERE/name)
    if a.record:logpath=HERE/'verification.log'
    else:
        with tempfile.NamedTemporaryFile(prefix='stopped-gauges-',suffix='.log',delete=False)as f:logpath=Path(f.name)
    started=datetime.now(timezone.utc).isoformat();tick=time.monotonic();steps=[];code=0;error=None
    with tempfile.TemporaryDirectory(prefix='stopped-gauges-')as directory,logpath.open('w')as log:
        work=Path(directory)
        jobs=[('reproduce.py',['--work',work]),('bit_profile.py',['--work',work]),
              ('complex_profile.py',['--work',work]),('endpoint_check.py',[]),
              ('compose.py',['--work',work,'--output',work/'certificate.json']),
              ('independent_check.py',['--work',work,'--certificate',work/'certificate.json']),
              ('test_controls.py',[])]
        try:
            for script,args in jobs:
                print('RUN',script,flush=True);log.write('\nRUN '+script+'\n');log.flush();t=time.monotonic()
                r=subprocess.run([sys.executable,str(HERE/script),*map(str,args)],cwd=ROOT,
                                 stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
                steps.append(dict(step=script,exit_code=r.returncode,elapsed_seconds=round(time.monotonic()-t,3)))
                if r.returncode:raise RuntimeError(script+' failed: '+str(r.returncode))
            assert (work/'certificate.json').read_bytes()==(HERE/'certificate.json').read_bytes(),'Fresh certificate differs'
        except (RuntimeError,AssertionError)as e:code=1;error=repr(e)
        changed=[name for name,value in before.items()if not(ROOT/name).exists()or digest(ROOT/name)!=value]
        if changed:code=1
        log.write('\nerror='+str(error)+'\nchanged_frozen_files='+json.dumps(changed)+'\nexit_code='+str(code)+'\n')
    if not code:check()
    receipt=dict(status='PASS'if not code else'FAIL',exit_code=code,error=error,started_utc=started,
                 finished_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-tick,3),
                 steps=steps,changed_frozen_files=changed,source_manifest_sha256=digest(HERE/'SOURCE.json'),
                 certificate_sha256=digest(HERE/'certificate.json'),log_sha256=digest(logpath),
                 kappa=json.loads((HERE/'certificate.json').read_text())['kappa'],
                 scope='Fresh complex graph/matching and h25 bit word; full inherited bit dirty replay; all signed-gauge cap/chain/chronology and reflected endpoint checks; complete paid distributions, fresh precision/three-stock bridge and independent 47/7 exact arithmetic. Retains inherited and newly proposed all-size interfaces.')
    if a.record:(HERE/'validation.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('Log:',logpath)
    if code:print('\n'.join(logpath.read_text().splitlines()[-70:]))
    print('PASS stopped signed-gauge finite gate'if not code else'FAIL stopped signed-gauge finite gate')
    return code
if __name__=='__main__':sys.exit(main())
