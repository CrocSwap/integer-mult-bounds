#!/usr/bin/env python3
"""Complete finite admission of the signed pivot554 extension; conditional theorem.
Python3.14, SymPy, C++17 and Boost; no solver needed. Deps are PR1319's pinned
package. With no reuse arguments, replay both original and both changed words.
Explicit reuse requires complete matching-word stage receipts. Geometry ancestry
retains the predecessor's declared reuse, not a new paper-to-machine proof.
Prepared for @Pseudoataraxia with substantial OpenAI ChatGPT assistance. Apache-2.0.
"""
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
P=Path(__file__).resolve().parent

def read(p):
    b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,message):
    if not x:raise RuntimeError(message)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--deps',type=Path,required=True,help='root holding research/global-mixed-t74-exact-fill from commit603defe58aac018c6a8457840481390a15846fe4')
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--parent-replay',type=Path)
    ap.add_argument('--native-gauge44',type=Path);ap.add_argument('--native-extra',type=Path)
    a=ap.parse_args();W=a.work.resolve();need(not W.exists(),'work directory already exists');W.mkdir(parents=True)
    B=a.deps.resolve()/'research/global-mixed-t74-exact-fill'
    need(sha(B/'MANIFEST.json')=='5c8e1f7d438003ff9a6934084f4c058148afcdf7578fe049feabf05059ebaeae','PR1319 manifest identity')
    manifest=read(B/'MANIFEST.json')
    for rel,h in manifest.items():need(sha(B/rel)==h,'PR1319 source changed: '+rel)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for key in ('PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(key,None)
    stages=[]
    def run(name,script,*args,allow_fail=False,cwd=None):
        start=time.monotonic();log=W/(name+'.log')
        with log.open('w') as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=cwd or W,env=env,stdout=f,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)))
        (W/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
        if not allow_fail:need(r.returncode==0,name+' failed: '+log.read_text()[-3000:])
        print(name,'exit',r.returncode,flush=True);return r.returncode
    run('local',P/'verify.py','--out',W/'words')
    parent=a.parent_replay.resolve() if a.parent_replay else W/'parent'
    if not a.parent_replay:run('parent',B/'vendor/pr1297/verify.py','--work',parent)
    need(read(parent/'RESULT.json')['status']=='PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION','completed parent receipt')
    need(all(s['exit_code']==0 for s in read(parent/'STAGES.json')),'parent stage failure')
    for pid,raw in [('base','gauge44'),('extra','extra')]:
        need(gzip.decompress((parent/('native-'+pid)/'local/FULL-WORD.json.gz').read_bytes())==gzip.decompress((B/'vendor/pr1297'/(raw+'-word.json.gz')).read_bytes()),'parent word binding')
    layout=parent/'layout';native={}
    for pid in ('gauge44','extra'):
        reuse=getattr(a,'native_'+pid);d=reuse.resolve() if reuse else W/('native-'+pid)
        if not reuse:run('native-'+pid,layout/'joint1148-round45/source/research/k8-eight-ends/replay_native.py',W/'words'/(pid+'.json.gz'),d,cwd=layout)
        need(gzip.decompress((d/'local/FULL-WORD.json.gz').read_bytes())==gzip.decompress((W/'words'/(pid+'.json.gz')).read_bytes()),'new word binding '+pid)
        st=read(d/'STEPS.json');need([s['step'] for s in st]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in st),'new native stages '+pid)
        native[pid]=d
    run('rebind',P/'vendor/rebind1625.py',B,native['gauge44']/'local',native['extra']/'local',W/'data')
    R=layout/('p554-runtime-'+W.name);need(not R.exists(),'runtime collision');R.mkdir();(R/'inputs').mkdir()
    for n in ('replay.py','freeze_spec.py','audit_mixed.py','independent_core.py','geometry_controls.py'):shutil.copy2(B/n,R/n)
    for n in ('code','construction'):shutil.copytree(B/n,R/n)
    shutil.copy2(B/'inputs/PR589-EXPECTED.json',R/'inputs/PR589-EXPECTED.json');shutil.copytree(native['extra'],R/'native-extra')
    rc=run('discovery',R/'replay.py','--data',W/'data','--work',W/'discovery','--local',native['gauge44']/'local','--discover',allow_fail=True)
    if rc:
        ds=read(W/'discovery/STAGES.json')
        need(ds[-1]['name']=='freeze' and ds[-1]['exit_code']!=0 and all(s['exit_code']==0 for s in ds[:-1]),'failure before stale-expected freeze')
        spec=W/'discovery/runtime/data/SPEC.json'
        run('unpin-recomputed-only',P/'vendor/unpin1186.py',spec,W/'discovery')
        run('freeze',R/'freeze_spec.py','--spec',spec,'--discovery',W/'discovery')
        shutil.copy2(spec,W/'data/SPEC.json')
    run('strict',R/'replay.py','--data',W/'data','--work',W/'strict','--local',native['gauge44']/'local')
    sr=read(W/'strict/RESULT.json');asm=read(W/'strict/ASSEMBLY.json')
    need(sr['status']=='PASS_STRICT_MIXED_T74_EXACT_FILL','strict status')
    need(len(read(W/'strict/ADMISSION-CONTROLS.json')['rejected_controls'])==114,'admission controls')
    need(len(read(W/'strict/BIT-CONTROLS.json')['rejected_controls'])==12,'bit controls')
    source=layout/'joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold'
    run('geometry',R/'geometry_controls.py','--source',source,'--strict',W/'strict','--out',W/'GEOMETRY-CONTROLS.json')
    need(len(read(W/'GEOMETRY-CONTROLS.json')['rejected'])==6,'geometry controls')
    from fractions import Fraction
    need(Fraction(sr['kappa'])>Fraction('0.001676896669021300'),'new bound does not exceed even a strict upper rounding of PR1625 headline')
    result=dict(status='PASS_T74_P554_SIGNED_RESTORATION_COMPLETE_FINITE_ADMISSION',kappa=sr['kappa'],kappa_decimal=sr['kappa_decimal'],source_commit='603defe58aac018c6a8457840481390a15846fe4',local_parent_commit='62092e96d2cb8f5751ce7d81b1ca774a0dd3827f',parent_reuse=bool(a.parent_replay),native_reuse={p:bool(getattr(a,'native_'+p)) for p in native},native_receipt_sha256={p:sha(native[p]/'STEPS.json') for p in native},independent={k:sr['independent'][k] for k in ('roles','prefix_bits','charged_prefix_bits','physical_row_coefficient','row_limit')},stages=stages,scope='Conditional finite construction. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, recovery, analytic transfer, PR559 correction and PR589 H1-H5 remain inherited. No selected-frontier edit or unconditional theorem.')
    (W/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'],flush=True)
if __name__=='__main__':main()
