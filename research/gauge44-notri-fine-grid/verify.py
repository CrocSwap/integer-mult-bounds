#!/usr/bin/env python3
"""Fresh PR659 construction/admission replay followed by a final-grid refinement.

Standard library only. Source commits must already be present in the Git object
database; see README.md. Does not fetch, alter source packages or selected-result.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def export(commit, package, destination):
    result = subprocess.run(['git','archive',commit,package],cwd=ROOT,capture_output=True)
    need(result.returncode == 0, 'Fetch the pinned source commits in README.md before replaying')
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        for entry in archive.getmembers():
            relative = Path(entry.name)
            need(not relative.is_absolute() and '..' not in relative.parts, 'unsafe archive path')
            if entry.isdir():
                continue
            need(entry.isfile(), 'unexpected source entry type')
            target = destination/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(archive.extractfile(entry).read())
    return destination/package


def main():
    need(__debug__, 'Inherited verifiers require assertions; do not use -O')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    out=args.out.resolve()
    need(not out.exists(), 'Use a new output directory')
    out.mkdir(parents=True)
    pins=json.loads((HERE/'SOURCES.json').read_text())
    package=export(pins['pr659'],'research/gauge44-notri-layered',out/'pr659')
    export(pins['pr635'],'research/complex-571-cold14-st2',out/'pr635')
    environment=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0')
    environment.pop('PYTHONOPTIMIZE',None)
    steps=[]
    def run(label,script,*arguments):
        start=time.monotonic()
        log=out/(label+'.log')
        with log.open('w') as stream:
            result=subprocess.run([sys.executable,'-B',str(script),*map(str,arguments)],cwd=ROOT,env=environment,stdout=stream,stderr=subprocess.STDOUT)
        steps.append(dict(stage=label,exit_code=result.returncode,seconds=round(time.monotonic()-start,3),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
        (out/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
        need(result.returncode == 0, label+' failed; see '+str(log))
        print('PASS',label,flush=True)
    run('manifest',package/'verify_manifest.py')
    run('base-word',package/'construction/reproduce.py','--main',ROOT,'--pr635',out/'pr635','--out',out/'base','--until','word')
    run('no-triangle-word',package/'construction/notri/reproduce_notri.py','--main',ROOT,'--pr635',out/'pr635','--word-dir',out/'base','--out',out/'notri','--word-only')
    run('layers-and-locals',package/'construction/layers_np/reproduce_np.py','--main',ROOT,'--pr635',out/'pr635','--notri-dir',out/'notri','--hamming',out/'base/hamming','--out',out/'layered')
    run('independent-local',package/'independent/audit_local.py','--word',out/'layered/layers/FULL-WORD.json.gz','--main',ROOT,'--output',out/'INDEPENDENT-LOCAL.json')
    run('global-admission',package/'verify_global.py','--main',ROOT,'--local',out/'layered/local','--work',out/'global')
    run('independent-price',package/'independent/price_profile.py','--main',ROOT,'--output',out/'INDEPENDENT-PRICE.json')
    run('fine-grid',HERE/'certify.py','--assembly',out/'global/ASSEMBLY.json','--out',out/'CERTIFICATE.json')
    certificate=json.loads((out/'CERTIFICATE.json').read_text())
    (out/'REPLAY.json').write_text(json.dumps(dict(status='PASS_FRESH_PR659_AND_FINE_GRID',base_commit=pins['base_commit'],source_commits={k:pins[k] for k in ('pr659','pr635','pr589')},python=sys.version,kappa=certificate['kappa'],kappa_decimal=certificate['kappa_decimal'],steps=steps,scope='Fresh complex reconstruction, local and global admission; unchanged cited PR589 bit supplier is repriced, not rebuilt. Final-grid change only.'),indent=2)+'\n')
    print('PASS_FRESH_PR659_AND_FINE_GRID',certificate['kappa_decimal'])


if __name__=='__main__':
    main()
