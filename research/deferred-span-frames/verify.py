#!/usr/bin/env python3
"""Reproduce the frozen selected construction and record its complete gate."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def digest(path):return sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true',help='Persist this run receipt and log.')
    args=parser.parse_args()
    artifacts=[HERE/name for name in ('graph-audit.json','primitive_check.json',
        'certificate.json','independent-audit.json')]
    artifacts += [HERE/f'{stem}-{h}.{ext}' for h in (23,25)
        for stem,ext in (('axis','json'),('word','json.gz'),('profile','json'),('transitions','json'))]
    before={p.name:digest(p) for p in artifacts}
    source_before=digest(HERE/'SOURCE.json')
    commands=[[sys.executable,str((HERE/name).relative_to(ROOT))] for name in
        ('producer.py','graph_audit.py','primitive_check.py','check.py','independent_check.py')]
    started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
    exit_code=0;steps=[]
    if args.record:logpath=HERE/'verification.log'
    else:
        with tempfile.NamedTemporaryFile(prefix='deferred-span-verification-',suffix='.log',delete=False) as stream:
            logpath=Path(stream.name)
    with logpath.open('w') as log:
        log.write('Selected deferred-span reproduction and verification\n');log.flush()
        for command in commands:
            print('RUN',' '.join(command),flush=True)
            log.write('\nRUN '+' '.join(command)+'\n');log.flush()
            tick=time.monotonic()
            result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            steps.append(dict(command=command,exit_code=result.returncode,
                              elapsed_seconds=round(time.monotonic()-tick,3)))
            if result.returncode:
                exit_code=result.returncode;break
        changed=[p.name for p in artifacts if not p.exists() or digest(p)!=before[p.name]]
        if digest(HERE/'SOURCE.json')!=source_before:changed.append('SOURCE.json')
        if changed and not exit_code:exit_code=1
        log.write('\nchanged_generated_artifacts='+json.dumps(changed)+'\n')
        log.write('exit_code='+str(exit_code)+'\n')
    receipt=dict(command='python3 research/deferred-span-frames/verify.py --record',
        started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
        elapsed_seconds=round(time.monotonic()-start,3),exit_code=exit_code,steps=steps,
        changed_generated_artifacts=changed,source_manifest_sha256=source_before,
        certificate_sha256=digest(HERE/'certificate.json'),log_sha256=digest(logpath),
        artifact_sha256={p.name:digest(p) for p in artifacts if p.exists()},
        scope='Fresh selected producer, dense graph, two/three-carrier dirty primitive, '
        'full physical dirty replay, literal transitions, exact CRT profiles and two '
        'arithmetic checks. Not the full repository verification suite.')
    if args.record:(HERE/'validation.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    else:print('Run log:',logpath,flush=True)
    print('PASS selected deferred-span gate' if exit_code==0 else 'FAIL selected deferred-span gate',flush=True)
    raise SystemExit(exit_code)

if __name__=='__main__':main()
