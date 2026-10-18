#!/usr/bin/env python3
"""Rebuild retimed native locals and exact independent controls.
Apache-2.0. Prepared by OpenAI Codex with substantial AI assistance. Native
programs and per-end controls are credited unchanged PR635/PR699 predecessors.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
PKG=HERE.parent


def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)


def sha(p):
    raw=p.read_bytes();return hashlib.sha256(gzip.decompress(raw) if p.suffix=='.gz' else raw).hexdigest()


def main():
    if not __debug__: raise RuntimeError('Assertions are required; do not use Python -O')
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('main','pr635','dependency699','out'):ap.add_argument('--'+k,type=Path,required=True)
    ap.add_argument('--input',type=Path,default=PKG/'inputs/PR699-WORD.json.gz')
    a=ap.parse_args(); main=a.main.resolve();dep=a.dependency699.resolve();out=a.out.resolve()
    assert not out.exists(),'Use a fresh output directory';out.mkdir(parents=True)
    up=a.pr635.resolve()/'research/complex-571-cold14-st2'
    src=main/'research/complex-k492-owner-repair/vendor/multicold';base=src/'vendor/pr558';parent=base/'vendor/pr552'
    # Check source manifests and every PR635 program used by the inherited chain.
    assert hashlib.sha256((dep/'MANIFEST.json').read_bytes()).hexdigest()=='1ec13d3f02dfd2966558264dfb010c52e83364d7cfee63af53df32df9384b9f8','PR699 manifest pin'
    pins=read(dep/'construction/INPUTS.json')
    for family,root in [('main',main),('pr635',a.pr635.resolve())]:
        for relative,expected in pins['files'][family].items():
            assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==expected,('source pin',relative)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',MULTICOLD_SOURCE=str(src),GAIN_PR564_SOURCE=str(src))
    for k in ('PYTHONOPTIMIZE','XPARAM','EXTRAH','PAIRING_RANKS','DIAG','HYBBUDGET','PR635_CODE'):env.pop(k,None)
    steps=[]
    def run(label,script,*args,portable=True):
        t=time.monotonic();cmd=[sys.executable,'-B']+([str(src/'code/run_portable.py')] if portable else [])+[str(script),*map(str,args)]
        with (out/(label+'.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
        steps.append(dict(step=label,exit_code=r.returncode,seconds=round(time.monotonic()-t,3)))
        (out/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
        assert r.returncode==0,(label,(out/(label+'.log')).read_text()[-4000:])
        print('PASS',label,flush=True)
    run('dependency-manifest',dep/'verify_manifest.py',portable=False)
    run('frame-construction',HERE/'build_frame_raises.py','--input',a.input,'--recipe',HERE/'FRAME-RAISES.json','--out',out/'word',portable=False)
    word=out/'word/FULL-WORD.json.gz';local=out/'local';routing=parent/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    run('independent-audit',dep/'independent/audit_local.py','--word',word,'--main',main,'--output',out/'INDEPENDENT-AUDIT.json',portable=False)
    run('native',up/'code/hpe_audit_and_transport.py','--raw',word,'--routing',routing,'--out',local)
    run('ledgers',up/'code/hpe_emit_local.py',local)
    run('local-replay',up/'code/hpe_audit_local.py',local)
    run('wrappers',up/'code/hpe_adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json')
    run('frame-controls',HERE/'frame_controls.py','--input',a.input,'--recipe',HERE/'FRAME-RAISES.json','--word',word,'--audit',dep/'independent/audit_local.py','--main',main,'--out',out/'FRAME-CONTROLS.json',portable=False)
    env['PR635_CODE']=str(up/'code')
    run('layer-end-controls',dep/'construction/layers_p6n/layer_end_controls.py',word,routing,out/'controls')
    env.pop('PR635_CODE');assert len(read(out/'controls/COLD-END-CONTROLS.json')['rejected'])==95
    run('phases',base/'code/phases_full.py',local,parent/'complex-global/vendor531/vendor/clifford')
    checks=read(local/'LOCAL-CHECKS.json')
    record=dict(raw_word_content_sha256=sha(word),canonical_sha256=sha(local/'CANONICAL-WORD.json.gz'),program_sha256={k:checks[k]['sha256'] for k in ('forward','backward')},clifford_recipes_sha256=sha(local/'CLIFFORD-RECIPES.json'),frame_controls=35,layer_controls=95)
    (out/'NATIVE-PINS.json').write_text(json.dumps(record,indent=2)+'\n')
    print('PASS_EIGHT_FRAME_RAISES_FULL_NATIVE_CHAIN',local,flush=True)


if __name__=='__main__':main()
