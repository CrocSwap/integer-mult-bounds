#!/usr/bin/env python3
"""Cold replay of PR799; optional reuse requires a complete, source-bound PR741 replay."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from verify_frontier741_bindings import check as check_ancestry, digest
from verify_frontier799_bindings import check

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'research/gauge44-frames-x'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--ancestor',type=Path,help='Reuse a completed verify_frontier741.py output after binding checks')
    a=p.parse_args();work=a.work.resolve()
    if sys.flags.optimize or work.exists() or work.is_relative_to(ROOT):
        raise SystemExit('Use enabled assertions and a fresh output directory outside the repository')
    work.mkdir(parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHON=sys.executable,SW4_FRAME8_PYTHON=sys.executable)
    for key in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(key,None)
    steps=[]
    def run(name,cmd):
        start=time.monotonic();log=work/(name+'.log');print('RUN',name,flush=True)
        with log.open('w') as f:r=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        steps.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=digest(log)))
        (work/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
        if r.returncode:raise RuntimeError(f'{name} failed; see {log}')
        print('PASS',name,flush=True)
    ancestor=a.ancestor.resolve() if a.ancestor else work/'ancestor'
    if a.ancestor is None:run('ancestor',[sys.executable,'-B',ROOT/'scripts/verify_frontier741.py','--work',ancestor])
    parent=check_ancestry(ancestor/'bit',ancestor/'complex')
    (work/'ANCESTRY.json').write_text(json.dumps(dict(reused=a.ancestor is not None,binding=parent),indent=2)+'\n')
    run('manifest',[sys.executable,'-B',PACKAGE/'verify_manifest.py'])
    native=work/'native';global_dir=work/'global'
    run('native',[sys.executable,'-B',PACKAGE/'construction/jx/reproduce_jx.py','--main',ROOT,
        '--pr635',ROOT/'research/complex-sw4-frame8/vendor/pr635','--sw4-dir',ancestor/'complex','--out',native])
    run('global',[sys.executable,'-B',PACKAGE/'verify_global.py','--main',ROOT,'--local',native/'local','--work',global_dir])
    independent=work/'INDEPENDENT-LOCAL.json';price=work/'INDEPENDENT-PRICE.json'
    run('independent-local',[sys.executable,'-B',PACKAGE/'independent/audit_local.py','--word',native/'jx/FULL-WORD.json.gz','--main',ROOT,'--output',independent])
    run('independent-price',[sys.executable,'-B',PACKAGE/'independent/price_profile.py','--main',ROOT,'--output',price])
    result=check(ancestor,native,global_dir,independent,price)
    result['reused_ancestry']=a.ancestor is not None
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['decimal'])

if __name__=='__main__':main()
