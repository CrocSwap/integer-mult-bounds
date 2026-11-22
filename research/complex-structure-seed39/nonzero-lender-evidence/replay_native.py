#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Fresh finite native chain for both seed39 four-alias high48 words."""
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
CODE=HERE.parent/'anticipatory-stage-evidence/interface/pr2269'
INTERFACE=CODE.parent

def main():
    if not __debug__:raise RuntimeError('assertions must remain enabled')
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    out=a.out.resolve();out.mkdir(exist_ok=a.resume,parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0');env.pop('PYTHONOPTIMIZE',None)
    steps=json.loads((out/'STEPS.json').read_text()) if a.resume else []
    completed={s['step'] for s in steps if s['exit_code']==0}
    if a.resume:
        for tag in ('base','extra'):
            if tag+'-transport' in completed:
                old=gzip.decompress((out/tag/'FULL-WORD.json.gz').read_bytes())
                current=gzip.decompress((HERE/'words'/f'FOUR-{tag}.json.gz').read_bytes())
                if old!=current:raise RuntimeError('resume input word changed: '+tag)
    # Exact immutable predecessor compiler bytes, including all mathematical checks.
    manifest=json.loads((CODE/'FETCH.json').read_text())
    for name,record in manifest['files'].items():
        local=CODE/('vendor/clifford/clifford_exact.py' if name.endswith('clifford_exact.py') else Path(name).name)
        if hashlib.sha256(local.read_bytes()).hexdigest()!=record['sha256']:
            raise RuntimeError('changed pinned native dependency: '+str(local))
    def run(label,script,*args):
        if label in completed:
            print('REUSE_COMPLETED',label,flush=True);return
        t=time.monotonic();p=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env)
        attempt=1+sum(x['step']==label for x in steps)
        logfile=label+('' if attempt==1 else '-attempt'+str(attempt))+'.log'
        (out/logfile).write_bytes(p.stdout);steps.append(dict(step=label,exit_code=p.returncode,seconds=time.monotonic()-t,log=logfile))
        (out/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
        if p.returncode:raise RuntimeError(f'{label} failed: {p.stdout[-2500:].decode(errors="replace")}')
        print('PASS',label,round(steps[-1]['seconds'],2),flush=True)
    for tag in ('base','extra'):
        word=HERE/'words'/f'FOUR-{tag}.json.gz';local=out/tag
        run(tag+'-transport',HERE/'transport_lifted.py',word,local)
        run(tag+'-emit',CODE/'bw_emit.py',local)
        run(tag+'-independent',CODE/'bw_audit_local.py',local)
        run(tag+'-wrappers',CODE/'bw_adapters.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
        run(tag+'-phases',CODE/'bw_phases.py',local)
        run(tag+'-recipes',CODE/'bw_check_recipes.py',local)
        run(tag+'-orientations',HERE/'orientation_lifted.py',local)
    run('lemmag',INTERFACE/'lemmag_stage.py',out/'LEMMAG-CHECKS.json',out/'base',out/'extra')
    print('PASS_FOUR_LIFTED_NATIVE_BOTH_WORDS_NO_GLOBAL_ADMISSION')
if __name__=='__main__':main()
