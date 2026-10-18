"""Fresh supplier construction, frozen owner reconstruction and strict T37 admission.

Python 3.11+ and the retained cold-baseline build dependencies. No search,
owner optimizer runs; the new constructor uses only the standard library.
The retained bit replay includes its unchanged exact move-rediscovery controls.
Use a new output directory outside the source checkout. Every supplier stage
is rebuilt; retained repository dependencies are checked before and after.
"""
import argparse,os,shutil,subprocess,sys,time
from pathlib import Path
from common import P,ROOT,read,dump,sha,identity
import package

def tree_pins(root):
    return {str(p.relative_to(root)):sha(p)for p in sorted(root.rglob('*'))if p.is_file() and '__pycache__'not in p.parts}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    pins=package.validate();work=a.work.resolve();assert not work.exists() and not work.is_relative_to(ROOT);work.mkdir(parents=True)
    view=work/'source';view.mkdir()
    for relative in package.COPY_TREES:
        shutil.copytree(ROOT/relative,view/relative,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for relative in package.COPY_FILES:
        (view/relative).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,view/relative)
    for name in ('gauge44-leaver8','gauge44-slots'):
        shutil.copytree(P/'vendor/pr1022/research'/name,view/'research'/name)
    for name in ('k8-coordinated-owners','k8-eight-ends','k8-eight-ends-t16','k8-three-demotions','k8-joint-entrances'):
        shutil.copytree(P/'vendor/pr1148/research'/name,view/'research'/name)
    # Legacy builders copy source permissions into outputs they then extend.
    # The frozen input stays read-only; only run-owned staging is writable.
    for path in view.rglob('*'):
        path.chmod(0o755 if path.is_dir() else 0o644)
    source_pins=tree_pins(view);dump(work/'STAGED-SOURCE-PINS.json',source_pins)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0')
    for key in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(key,None)
    temp=work/'temp';temp.mkdir();env.update(TMPDIR=str(temp),TMP=str(temp),TEMP=str(temp))
    stages=[]
    def run(name,script,*args):
        log=work/(name+'.log');start=time.monotonic()
        dump(work/'STATUS.json',dict(status='RUNNING',stage=name,pid=os.getpid(),stages=stages))
        with log.open('w')as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],env=env,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,exit_code=r.returncode,seconds=round(time.monotonic()-start,3),log_sha256=sha(log)))
        dump(work/'STAGES.json',stages)
        if r.returncode:
            dump(work/'STATUS.json',dict(status='FAILED',stage=name,stages=stages))
            raise RuntimeError(name+'\n'+log.read_text()[-6000:])
        print('PASS',name,stages[-1]['seconds'],flush=True)
    leaver=view/'research/gauge44-leaver8';slots=view/'research/gauge44-slots';pr635=P/'vendor/pr635'
    run('retained-cold-ancestry',view/'scripts/verify_frontier799.py','--work',work/'ancestry799')
    run('ancestry-coverage',ROOT/'research/complex-t21-owners/vendor/pr858/baseline_coverage.py','--ancestor',work/'ancestry799/ancestor','--out',work/'ANCESTRY-COVERAGE.json')
    run('leaver-manifest',leaver/'verify_manifest.py')
    run('slots-manifest',slots/'verify_manifest.py')
    run('base-word',leaver/'construction/reproduce.py','--main',view,'--pr635',pr635,'--out',work/'base','--until','word')
    run('leaver-cells',leaver/'construction/leaver/reproduce_leaver.py','--main',view,'--pr635',pr635,'--word-dir',work/'base','--id','k8','--out',work/'cells','--word-only')
    run('leaver-chain',leaver/'construction/leaver/reproduce_leaver_chain.py','--main',view,'--pr635',pr635,'--leaver-dir',work/'cells','--hamming',work/'base/hamming','--id','k8','--out',work/'chain')
    run('chain-independent-audit',leaver/'independent/audit_local.py','--main',view,'--word',work/'chain/frames/FULL-WORD.json.gz','--output',work/'CHAIN-AUDIT.json')
    run('k8-global',leaver/'verify_global.py','--main',view,'--local',work/'chain/local','--work',work/'k8-global')
    run('seven-slots',slots/'construction/slots/verify_slots.py','--main',view,'--pr635',pr635,'--baseline',work/'chain','--work',work/'slots')
    run('joint-entrance-supplier',view/'research/k8-joint-entrances/verify.py','--base',work/'slots/slots/FULL-WORD.json.gz','--work',work/'joint')
    run('x54-manifest',P/'vendor/pr1130/research/gauge44-ends7-x54-t16/verify_manifest.py')
    run('x54-local',P/'native_x54.py','--main',view,'--pr635',pr635,'--baseline',work/'joint','--work',work/'x54')
    run('flow-normalization',P/'normalize_flow.py','--out',work/'FLOW-NORMALIZATION.json')
    local=work/'x54/local';baseline=work/'slots/global';base=baseline/'global/base'
    retained=work/'ancestry799/global/global/base'
    for relative in ('split-centres/GLOBAL-TEMPLATE.json.gz','split-centres/CANONICAL-WORD.json.gz','work/complex-nine-native/DATA-PHASES.json'):
        assert read(base/relative)==read(retained/relative),'Cold ancestral parent binding: '+relative
    run('frozen-flow-construction',P/'construct.py','--parent',base/'split-centres/GLOBAL-TEMPLATE.json.gz','--word',local/'CANONICAL-WORD.json.gz','--out',work/'constructed')
    assert read(work/'constructed/OWNERS.json.gz')==read(P/'data/OWNERS.json.gz'),'Reconstructed owners differ'
    assert sha(work/'constructed/OWNERS.json.gz')==sha(P/'data/OWNERS.json.gz'),'Portable owner bytes differ'
    import controls
    controls.check(read(base/'split-centres/GLOBAL-TEMPLATE.json.gz'),read(local/'CANONICAL-WORD.json.gz'),work/'FLOW-CONTROLS.json')
    run('independent-owners',P/'audit.py','--base',base,'--local',local,'--owners',work/'constructed/OWNERS.json.gz','--out',work/'INDEPENDENT-OWNERS.json')
    import prepare,controller,price
    global_work=work/'t37';global_work.mkdir();prepare.prepare(global_work,baseline)
    run('independent-parent',global_work/'adapted/check_parent.py','--source',base/'split-centres/GLOBAL-TEMPLATE.json.gz','--parent',global_work/'lift/GLOBAL-TEMPLATE.json.gz','--out',work/'PARENT-CHECK.json')
    result=controller.replay(global_work,local)
    independent=read(work/'INDEPENDENT-OWNERS.json')
    owner=read(global_work/'strict/global/audit/OWNERS-AND-PROFILE.json')
    assert independent['actual_73_axis_charts']==owner['actual_73column_sigmas']
    prices=price.price(work/'PRICE.json')
    assert prices['kappa']==result['kappa']
    assert tree_pins(view)==source_pins,'Staged supplier source changed during verification'
    final_pins=package.validate();assert final_pins==pins,'Package changed during verification'
    result.update(status='PASS_FRESH_T37_JOINT_X54_CONSTRUCTION_AND_STRICT_ADMISSION',pins=pins,
      source_view_sha256=identity(source_pins),independent_owners_sha256=sha(work/'INDEPENDENT-OWNERS.json'),
      construction_sha256=sha(work/'constructed/CONSTRUCTION.json'),price_sha256=sha(work/'PRICE.json'),
      supplier_stages=stages,flow_controls=8,independent_owner_controls=6,joint_entrance_controls=27,eight_end_controls=32,x54_negative_controls=8)
    dump(work/'RESULT.json',result)
    math=dict(status=result['status'],claim=read(P/'CLAIM.json'),price=prices,
      constructed_owner_sha256=sha(work/'constructed/OWNERS.json.gz'),flow_sha256=sha(P/'data/FLOW.json.gz'),
      package_manifest_sha256=pins['manifest_sha256'],controls=dict(flow=8,owner=6,controller=15,admission=69,bit_supplier=12,joint_entrances=27,eight_ends=32,x54_negative=8))
    dump(work/'MATH.json',math)
    dump(work/'STATUS.json',dict(status='COMPLETE',kappa=result['kappa'],result_sha256=sha(work/'RESULT.json')))
    print(result['status'],result['kappa_decimal'],flush=True)
if __name__=='__main__':main()
