"""Source-bound PR1800 composition replay; assertions must be enabled.

Fetches the exact immutable dependency when --dependency is omitted. All downloads,
replay outputs and dependency copies stay under --work. No predecessor is edited.
"""
import argparse, concurrent.futures, hashlib, json, os, shutil, subprocess, sys, time, urllib.request
from pathlib import Path
from fractions import Fraction as Q
P=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
    if not __debug__:raise RuntimeError('Assertions required')
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--dependency',type=Path);ap.add_argument('--arithmetic-only',action='store_true');a=ap.parse_args()
    work=a.work.resolve();assert not work.exists() and not work.is_relative_to(P);work.mkdir(parents=True)
    pins=read(P/'MANIFEST.json')
    for n,h in pins.items():assert sha(P/n)==h,n
    info=read(P/'DEPENDENCY.json');dpins=read(P/'DEPENDENCY-MANIFEST.json');stages=[]
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',TMPDIR=str(work))
    env.pop('PYTHONOPTIMIZE',None)
    def run(name,script,*args):
        t=time.monotonic();log=work/(name+'.log')
        with log.open('w') as out:r=subprocess.run([sys.executable,'-B',str(script),*map(str,args)],cwd=work,env=env,stdout=out,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,exit_code=r.returncode,seconds=time.monotonic()-t,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(stages,indent=2))
        assert r.returncode==0,(name,log.read_text()[-3000:]);print('PASS',name,flush=True)
    run('endpoint',P/'certify_endpoint.py',work/'ENDPOINT-REPLAY.json');run('ledger',P/'check_ledger.py',work/'arithmetic');run('balance',P/'independent_check.py',work/'arithmetic')
    ledger=read(work/'arithmetic/LEDGER.json');balance=read(work/'arithmetic/INDEPENDENT.json');claim=read(P/'CLAIM.json')
    row=ledger['rows']['struct_boundary_radix_union'];k=Q(row['kappa']['rational'])
    assert k==Q(balance['rows']['struct_boundary_radix_union']['kappa'])==Q(claim['kappa'])
    assert k>Q(read(P/'inputs/LEADER1839.json')['kappa_rational'])
    assert len(row['strict_checks'])==57 and all(Q(x['rational'])>0 for x in row['strict_checks'].values())
    assert len(ledger['rejecting_controls']['struct_boundary_radix_union'])==17
    if a.arithmetic_only:
        (work/'RESULT.json').write_text(json.dumps(dict(status='PASS_ARITHMETIC_ONLY',kappa=str(k),full_admission=False,stages=stages),indent=2));return
    dependency=work/'dependency'
    if a.dependency:
        src=a.dependency.resolve()
        assert sha(src/'MANIFEST.json')==info['manifest_sha256']
        for n,h in dpins.items():assert sha(src/n)==h,n
        shutil.copytree(src,dependency)
    else:
        dependency.mkdir()
        base='https://raw.githubusercontent.com/'+info['repository']+'/'+info['head']+'/'+info['package']+'/'
        def fetch(n):
            f=dependency/n;assert f.resolve().is_relative_to(dependency.resolve())
            raw=urllib.request.urlopen(base+n,timeout=120).read();assert hashlib.sha256(raw).hexdigest()==dpins[n],n
            f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:list(ex.map(fetch,dpins))
        raw=urllib.request.urlopen(base+'MANIFEST.json').read();assert hashlib.sha256(raw).hexdigest()==info['manifest_sha256'];(dependency/'MANIFEST.json').write_bytes(raw)
    for n,h in dpins.items():assert sha(dependency/n)==h,n
    assert sha(P/'inputs/SOURCE-SPEC.json')==sha(dependency/'new/SPEC.json')
    run('inherited-outer',P/'replay_outer.py',dependency,work/'inherited-outer')
    run('supplier',dependency/'verify.py','--work',work/'supplier','--audit-shards','1')
    result=read(work/'supplier/RESULT.json');asm=read(work/'supplier/strict/ASSEMBLY.json');spec=read(P/'inputs/SPEC.json');bj=read(P/'inputs/B.json')
    assert result['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION'
    assert asm['status']=='PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY' and len(asm['outer'])==47
    assert Q(asm['complex_lower'])==Q(read(P/'inputs/SOURCE-SPEC.json')['expected']['complex_lower'])
    assert Q(asm['complex_lower'])<Q(bj['b'])<Q(spec['expected']['complex_lower'])<Q(bj['b_above_endpoint'])
    assert read(work/'ENDPOINT-REPLAY.json')['status']=='PASS_TWO_ENGINE_ENDPOINT_BRACKET'
    assert {int(x):v for x,v in asm['complex_profile'].items()}=={int(x):v for x,v in bj['profile'].items()}
    assert Q(asm['bit_lower'])==Q('0.001733427039589844234749')
    out=dict(status='PASS_CONDITIONAL_SLACK_REFINEMENT_FINITE_ADMISSION',kappa=str(k),kappa_decimal=claim['kappa_decimal'],dependency_head=info['head'],dependency_manifest=info['manifest_sha256'],package_manifest=sha(P/'MANIFEST.json'),assembly_sha256=sha(work/'supplier/strict/ASSEMBLY.json'),full_admission=True,stages=stages,scope=claim['scope'])
    (work/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],flush=True)
if __name__=='__main__':main()
