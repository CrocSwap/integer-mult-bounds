"""Fresh mixed local replay, deterministic owner reconstruction and strict admission.

No allocation optimizer or discovery-mode controller runs. Outputs must be new
and outside the checkout. Optional cold PR799 reuse is independently rebound
with the retained maintainer checker and fixed stage/artifact coverage.
"""
import argparse,os,shutil,subprocess,sys,tarfile,time
from pathlib import Path
from common import P,ROOT,read,dump,sha,identity,load
import package

ARCHIVE=ROOT/'research/community-frontier1042-audit/selected-replay.tar.gz'
ARCHIVE_SHA='22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--ancestry799',type=Path,help='Completed cold verify_frontier799.py output; all bindings and coverage are rechecked')
    a=ap.parse_args();pins=package.validate();w=a.work.resolve()
    assert not w.exists() and not w.is_relative_to(ROOT);w.mkdir(parents=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',PYTHON=sys.executable)
    for k in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(k,None)
    steps=[]
    def run(name,script,*args):
        log=w/(name+'.log');start=time.monotonic()
        with log.open('w')as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        steps.append(dict(name=name,exit_code=r.returncode,seconds=round(time.monotonic()-start,3),log_sha256=sha(log)))
        dump(w/'STAGES.json',steps)
        if r.returncode:raise RuntimeError(name+'\n'+log.read_text()[-5000:])
        print('PASS',name,flush=True)
    assert sha(ARCHIVE)==ARCHIVE_SHA
    baseline=w/'retained1042';baseline.mkdir()
    with tarfile.open(ARCHIVE)as t:
        for m in t.getmembers():
            assert (baseline/m.name).resolve().is_relative_to(baseline) and (m.isfile() or m.isdir())
        t.extractall(baseline,filter='data')
    baseline=baseline/'slots/global';base=baseline/'global/base'
    import build_word,controls,audit,prepare,controller,price
    dump(w/'WORD-RECIPE.json',build_word.build(w/'FOUR-WORD.json.gz'))
    providers={}
    for pid,word in [('demote3',P/'vendor/pr1148/JOINT-WORD.json.gz'),('demote4',w/'FOUR-WORD.json.gz')]:
        run('raw-'+pid,ROOT/'research/gauge44-slots/independent/audit_local.py','--word',word,'--main',ROOT,'--output',w/('RAW-'+pid+'.json'))
        run('native-'+pid,P/'native.py',word,w/pid)
        providers[pid]=w/pid/'local'
        stages=read(w/pid/'STEPS.json')
        assert [v['step']for v in stages]==['native','ledgers','local-replay','wrappers','phases'] and all(v['exit_code']==0 for v in stages)
        assert read(providers[pid]/'FULL-WORD.json.gz')==read(word)
    run('entrance-controls',P/'local_controls.py','--out',w/'ENTRANCE-CONTROLS.json')
    run('owners',P/'construct.py','--parent',base/'split-centres/GLOBAL-TEMPLATE.json.gz',
        '--word3',providers['demote3']/'CANONICAL-WORD.json.gz','--word4',providers['demote4']/'CANONICAL-WORD.json.gz','--out',w/'constructed')
    assert read(w/'constructed/OWNERS.json.gz')==read(P/'data/OWNERS.json.gz')
    controls.check(read(base/'split-centres/GLOBAL-TEMPLATE.json.gz'),{pid:read(d/'CANONICAL-WORD.json.gz')for pid,d in providers.items()},w/'FLOW-CONTROLS.json')
    independent=audit.check(base,providers,w/'constructed/OWNERS.json.gz',w/'INDEPENDENT-OWNERS.json')
    global_work=w/'t37';global_work.mkdir();prepare.prepare(global_work,baseline,providers)
    run('parent',global_work/'adapted/check_parent.py','--source',base/'split-centres/GLOBAL-TEMPLATE.json.gz','--parent',global_work/'lift/GLOBAL-TEMPLATE.json.gz','--out',w/'PARENT-CHECK.json')
    result=controller.replay(global_work,providers)
    owner=read(global_work/'strict/global/audit/OWNERS-AND-PROFILE.json')
    assert independent['actual_73_axis_charts']==owner['actual_73column_sigmas']
    prices=price.price(providers,w/'PRICE.json');assert prices['kappa']==result['kappa']
    ancestry=a.ancestry799.resolve()if a.ancestry799 else w/'ancestry799'
    if not a.ancestry799:run('cold-ancestry799',ROOT/'scripts/verify_frontier799.py','--work',ancestry)
    cover=load(ROOT/'research/complex-t21-owners/vendor/pr858/baseline_coverage.py','fixed_baseline_coverage').check(ancestry/'ancestor')
    binding=load(ROOT/'scripts/verify_frontier799_bindings.py','cold_ancestry_bindings').check(ancestry/'ancestor',ancestry/'native',ancestry/'global',ancestry/'INDEPENDENT-LOCAL.json',ancestry/'INDEPENDENT-PRICE.json')
    for rel in ('split-centres/GLOBAL-TEMPLATE.json.gz','split-centres/CANONICAL-WORD.json.gz','work/complex-nine-native/DATA-PHASES.json'):
        assert read(base/rel)==read(ancestry/'global/global/base'/rel),'Cold ancestral parent binding: '+rel
    asm=read(global_work/'strict/ASSEMBLY.json');old=read(ancestry/'global/ASSEMBLY.json')
    assert asm['bit_lower']==old['bit_lower'] and asm['bit_supplier']==old['bit_supplier']
    dump(w/'ANCESTRY.json',dict(reused=bool(a.ancestry799),coverage=cover,binding=binding,archive_sha256=ARCHIVE_SHA))
    assert package.validate()==pins,'Sources changed during verification'
    result.update(status='PASS_MIXED_JOINT_ENTRANCES_T37_COMPLETE_ADMISSION',source_pins=pins,
      native_providers=2,entrance_controls=11,flow_controls=8,independent_owner_controls=8,
      ancestry_sha256=sha(w/'ANCESTRY.json'),price_sha256=sha(w/'PRICE.json'),steps=steps)
    dump(w/'RESULT.json',result)
    print(result['status'],result['kappa_decimal'],flush=True)
if __name__=='__main__':main()
