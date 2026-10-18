"""Apply PR1130's X54 slot recipe after PR1148 joint entrances."""
import argparse,gzip,hashlib,os,subprocess,sys,time
from pathlib import Path
from common import P,read,dump,sha

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('main','pr635','baseline','work'):ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args();root=a.main.resolve();base=a.baseline.resolve();work=a.work.resolve()
    assert not work.exists() and not work.is_relative_to(root);work.mkdir(parents=True)
    prior=read(base/'RESULT.json')
    assert prior['status']=='PASS_JOINT_ENTRANCES_COMPLETE_ADMISSION'
    assert not prior['native_reuse'] and not prior['parent_reuse']
    assert prior['kappa_decimal']==read(P/'vendor/pr1148/research/k8-joint-entrances/CLAIM.json')['kappa_decimal']
    expected=['parent','build','independent-local','entrance-controls','native','strict-global','all-replica-bound']
    assert [s['step']for s in prior['steps']]==expected and all(s['exit_code']==0 for s in prior['steps'])
    pkg=P/'vendor/pr1130/research/gauge44-ends7-x54-t16';x54=pkg/'construction/ends7/x54'
    source=root/'research/complex-k492-owner-repair/vendor/multicold';ancestor=source/'vendor/pr558';parent=ancestor/'vendor/pr552'
    up=a.pr635.resolve()/'research/complex-571-cold14-st2';input_word=base/'FULL-WORD.json.gz'
    recipe=P/'data/X54-RECIPE.json';rec=read(recipe)
    assert hashlib.sha256(gzip.decompress(input_word.read_bytes())).hexdigest()==rec['base_sha256']
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',MULTICOLD_SOURCE=str(source),GAIN_PR564_SOURCE=str(source))
    env.pop('PYTHONOPTIMIZE',None);steps=[]
    def run(name,script,*args,portable=False):
        begin=time.monotonic();cmd=[sys.executable,'-B']+([str(source/'code/run_portable.py')]if portable else[])+[str(script),*map(str,args)]
        log=work/(name+'.log')
        with log.open('w')as f:r=subprocess.run(cmd,env=env,cwd=root,stdout=f,stderr=subprocess.STDOUT)
        steps.append(dict(name=name,exit_code=r.returncode,seconds=round(time.monotonic()-begin,3),log_sha256=sha(log)));dump(work/'STAGES.json',steps)
        if r.returncode:raise RuntimeError(name+'\n'+log.read_text()[-5000:])
        print('PASS',name,flush=True)
    raw=work/'FULL-WORD.json.gz';local=work/'local';routing=parent/'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz'
    run('construct',x54/'build_tri.py',input_word,recipe,raw)
    assert hashlib.sha256(gzip.decompress(raw.read_bytes())).hexdigest()==rec['expect_sha256']
    run('x54-controls',x54/'run_controls.py',input_word,recipe,pkg/'independent/audit_local.py',work/'controls')
    controls=read(work/'controls/controls.json');assert len(controls)==10 and all(c['ok']for c in controls.values())
    run('native',up/'code/hpe_audit_and_transport.py','--raw',raw,'--routing',routing,'--out',local,portable=True)
    run('ledgers',up/'code/hpe_emit_local.py',local,portable=True)
    run('local-replay',up/'code/hpe_audit_local.py',local,portable=True)
    run('wrappers',up/'code/hpe_adapters_local.py',local/'CANONICAL-WORD.json.gz',local/'RESIDUAL-ADAPTERS.json',local/'WRAPPER-CHECKS.json',portable=True)
    run('phases',ancestor/'code/phases_full.py',local,parent/'complex-global/vendor531/vendor/clifford',portable=True)
    run('independent',pkg/'independent/audit_local.py','--main',root,'--word',raw,'--output',work/'INDEPENDENT-LOCAL.json')
    run('leaver-premise',pkg/'construction/ends7/premise/premise_check.py',raw)
    independent=read(work/'INDEPENDENT-LOCAL.json');claim=read(P/'CLAIM.json')
    assert independent['status']=='PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES'
    assert independent['local_profile']==claim['local_profile']and independent['width_inventory']==claim['width_inventory']
    premise=__import__('json').loads((work/'leaver-premise.log').read_text().strip().splitlines()[-1])
    assert premise['status']=='PASS_LEAVER_PREMISE'and premise['cells']==8 and premise['paid_profile']==claim['local_profile']
    old=read(base/'native/local/CANONICAL-WORD.json.gz');new=read(local/'CANONICAL-WORD.json.gz')
    widths=lambda w:[len(w['frames'][w['final'][q]])-len(w['frames'][w['start'][q]])for q in range(224,704)]
    assert widths(old)==widths(new)==read(P/'data/SUPPLIER-PLAN.json')['provider_registry']['gauge44']['widths']
    result=dict(status='PASS_JOINT_ENTRANCE_X54_LOCAL_RECIPE_CONTROLS_NATIVE_PHASES_INDEPENDENT_AND_LEAVER',steps=steps,
      recipe_sha256=sha(recipe),word_content_sha256=rec['expect_sha256'],canonical_sha256=sha(local/'CANONICAL-WORD.json.gz'),x54_negative_controls=8,unchanged_helper_width_vector=True)
    dump(work/'RESULT.json',result);print(result['status'],flush=True)
if __name__=='__main__':main()
