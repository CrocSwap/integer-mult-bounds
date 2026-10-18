"""Fresh U10/T37 global replay with complete source-bound PR799 ancestry.

Rebuilds U8 (PR869/870), then U10 (construction/u10: two further triangle-hybrid slots),
and hosts the U10 locals with PR942's unchanged T37 owner map.

Inherits all mathematical hypotheses of PR890. No optimizer runs.
Run with Python3.11+, Linux build/scientific dependencies, and a new output
outside the checkout. The optional baseline must be a full cold799 replay.
"""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from common import P,ROOT,T21,read,load
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--baseline799',type=Path);a=ap.parse_args()
    pins=load(P/'package.py','t37_package').validate()
    work=a.work.resolve();assert not work.exists()and not work.is_relative_to(ROOT);work.mkdir(parents=True)
    baseline=a.baseline799.resolve()if a.baseline799 else work/'baseline799'
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',PYTHON=sys.executable,SW4_FRAME8_PYTHON=sys.executable,T37_WORK=str(work),T37_BASELINE=str(baseline),T37_LOCAL=str(work/'native10/local'))
    temp=work/'temp';temp.mkdir();env.update(TEMP=str(temp),TMP=str(temp),TMPDIR=str(temp))
    for k in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):env.pop(k,None)
    stages=[]
    def run(name,script,*args):
        log=work/(name+'.log');start=time.monotonic()
        with log.open('w',encoding='utf-8')as f:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,exit_code=r.returncode,seconds=round(time.monotonic()-start,3),log_sha256=sha(log)))
        (work/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
        if r.returncode:raise RuntimeError(name+'\n'+log.read_text(errors='replace')[-5000:])
        print('PASS',name,stages[-1]['seconds'],flush=True)
    if a.baseline799 is None:run('baseline799-cold',ROOT/'scripts/verify_frontier799.py','--work',baseline)
    run('ancestry-coverage',T21/'vendor/pr858/baseline_coverage.py','--ancestor',baseline/'ancestor','--out',work/'ANCESTRY-COVERAGE.json')
    run('baseline799-binding',ROOT/'scripts/verify_frontier799_bindings.py','--ancestor',baseline/'ancestor','--native',baseline/'native','--global',baseline/'global','--independent',baseline/'INDEPENDENT-LOCAL.json','--price',baseline/'INDEPENDENT-PRICE.json','--out',work/'BASELINE-BINDING.json')
    run('u8-native',T21/'vendor/pr870/construction/barch/reproduce_barch.py','--main',ROOT,'--pr635',ROOT/'research/complex-sw4-frame8/vendor/pr635','--jx-dir',baseline/'native','--recipe','U8','--out',work/'native')
    run('u10-native',P/'construction/u10/reproduce_u10.py','--main',ROOT,'--pr635',ROOT/'research/complex-sw4-frame8/vendor/pr635','--u8-word',work/'native/barch/FULL-WORD.json.gz','--out',work/'native10')
    run('prepare',P/'prepare.py')
    independent=P/'independent'
    run('frozen-construction',independent/'verify_construct.py','--out',work/'CONSTRUCTION-CHECK.json')
    run('independent-owners',independent/'check_t37.py','--word',work/'native10/local/CANONICAL-WORD.json.gz','--local-replay',work/'native10/local/INDEPENDENT-LOCAL-REPLAY.json','--baseline-base',baseline/'global/global/base','--out',work/'INDEPENDENT-OWNERS.json')
    run('build-parent',work/'adapted/build_parent.py','--base',baseline/'global/global/base','--owners',P/'OWNERS.json.gz','--order',P/'ORDER.json','--out',work/'lift')
    run('check-parent',work/'adapted/check_parent.py','--source',baseline/'global/global/base/split-centres/GLOBAL-TEMPLATE.json.gz','--parent',work/'lift/GLOBAL-TEMPLATE.json.gz','--out',work/'PARENT-CHECK.json')
    run('independent-price',independent/'all_t_bound.py','--out',work/'ALL-T-BOUND.json')
    run('discovery',P/'replay.py','discovery')
    run('strict',P/'replay.py','strict')
    run('payload-controls',independent/'check_payload_controls.py','--work',work,'--out',work/'PAYLOAD-CONTROLS.json')
    run('final-binding',P/'final_binding.py','--work',work,'--baseline',baseline)
    assembly=read(work/'strict/ASSEMBLY.json');invoice=read(work/'strict/global/audit/PREFIX-AND-INVOICE.json');owner=read(work/'strict/global/audit/OWNERS-AND-PROFILE.json')
    claim=read(P/'CLAIM.json')
    assert assembly['kappa_decimal']==claim['kappa_decimal']=='0.001662039077758742'
    assert assembly['complex_profile']==claim['profile']
    independent_owner=read(work/'INDEPENDENT-OWNERS.json')
    for key in ('roles','calls','live','physical','rank_mass','deficit','prefix_bits','idle'):
        assert independent_owner[key]==claim[key], key
    assert invoice['charged_prefix_bits']==claim['charged_prefix_bits']
    assert invoice['finite']['physical_row_coefficient']==claim['physical_row_coefficient']
    assert invoice['global_prefix_bits']==779 and invoice['charged_prefix_bits']==1024 and invoice['finite']['physical_row_coefficient']==17495
    assert owner['hosted_residuals']==167832 and owner['live']==33152 and owner['deficit']==11840
    result=dict(status='PASS_U10_T37_STRICT_WITH_SOURCE_BOUND_ANCESTRY',kappa=assembly['kappa'],kappa_decimal=assembly['kappa_decimal'],cold_baseline=str(baseline),reused_completed_baseline=a.baseline799 is not None,stages=stages,roles=167832,calls=333,prefix_bits=779,charged_prefix_bits=1024,row_coefficient=17495,source_sha256={str(p.relative_to(ROOT)):sha(p)for p in (P/'OWNERS.json.gz',P/'ORDER.json',P/'EDITS.json',P/'prepare.py',P/'replay.py',P/'verify.py')},scope='Finite conditional composition. Independent owner/construction/all-T checks supplement this replay. Inherited all-size/compiler, physical-realization, precision/tape, analytic and bitH1-H5 assumptions remain.')
    assert read(work/'FINAL-BINDING.json')['pins']==pins, 'Source package changed during replay'
    result['pins']=pins;result['final_binding_sha256']=sha(work/'FINAL-BINDING.json');result['source_sha256']['research/complex-t37-owners/final_binding.py']=sha(P/'final_binding.py')
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['kappa_decimal'])
if __name__=='__main__':main()
