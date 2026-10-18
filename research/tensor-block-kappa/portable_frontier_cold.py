#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portable T114 block-norm replay: four fresh native chains by default.

The pinned native preparer authenticates original491 source plus exact overlay506,
runs four native chains and the retained-parent check, then the admission driver
checks the actual T114 fill, required block-norm certificate and complete release.
The final exact target must also beat the complete delivered T104 rational;
the inherited exact PR2802 source/comparison pins remain enforced.
Explicit retained-only reuse and completed frontier-baseline reuse are separately
labelled. --prepare-only checks source preparation without issuing admission.
"""
import argparse, gzip, hashlib, json, os, platform, subprocess, sys, time
from fractions import Fraction
from pathlib import Path, PurePosixPath

HERE=Path(__file__).resolve().parent
FRONTIER_HEAD='17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd'
BASELINE_PINS_SHA='fae7e9161707d3627c7ba444543b1bdd0d736df57b8495ea112bb221a2693497'
SOURCE_SHA='9c72b4301057a6c204c40bb6584eb74b779e06618bcd98d706d726c3e2c92451'
COMPARISON_SHA='a2fcbc8a3ad3095ecbd310a26c02e9d11c28e4d105669a08bbdfb39d7704db51'
EXPECTED_REPLICAS=114
EXPECTED_T114_KAPPA=Fraction('0.001717795274221416686578')-Fraction(1,10**46)-Fraction(1,10**70)
PREDECESSOR_T104_KAPPA=Fraction('0.001717795222616587743198')-Fraction(1,10**46)-Fraction(1,10**70)
COLD_STAGES={'literal-review','native-base','native-extra','native-retained-base','native-retained-extra','retained-parent','complete-admission'}
LF_ADAPTER=r'''"""Task-scoped Windows LF compatibility for authenticated generated source text.
No validation predicates or immutable source bytes are changed.
"""
from pathlib import Path
_original_write_text=Path.write_text

def _write_text_lf(self,data,encoding=None,errors=None,newline=None):
 return _original_write_text(self,data,encoding=encoding,errors=errors,newline='\n' if newline is None else newline)
Path.write_text=_write_text_lf
'''

def need(ok,why):
    if not ok:raise RuntimeError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def tree(root,exclude=()):
    result={}
    for p in sorted(root.rglob('*')):
        need(not p.is_symlink(),'unbound symlink: '+str(p))
        if p.is_file()and p.relative_to(root).as_posix()not in exclude:result[p.relative_to(root).as_posix()]=sha(p)
    return result
def write(p,x):
    lock=p.with_name(p.name+'.lock');fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        os.write(fd,str(os.getpid()).encode());os.close(fd);fd=None
        p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    finally:
        if fd is not None:os.close(fd)
        lock.unlink()

def authenticate_vendor(directory,pins):
    need(sha(pins)==BASELINE_PINS_SHA,'exact baseline Git/SHA inventory pin')
    inventory=read(pins);need(inventory['head']==FRONTIER_HEAD,'exact current frontier head');records=inventory['files'];need(len(records)==124,'exact 124 frontier files')
    expected={}
    for r in records:
        name=r['path'];parts=PurePosixPath(name)
        need(name and not parts.is_absolute()and '..'not in parts.parts and '\\'not in name,'safe baseline relative file')
        p=directory/name;raw=p.read_bytes()
        need(len(raw)==r['bytes'] and sha(p)==r['sha256'],'baseline file bytes: '+name)
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],'baseline Git blob: '+name)
        expected[name]=r['sha256']
    need(len(expected)==124 and tree(directory,('DOWNLOAD-MANIFEST.json',))==expected,'complete exact frontier file set')
    return expected

def authenticate_completed_baseline(root,vendor_claim):
    result=read(root/'RESULT.json');native=read(root/'NATIVE-RECEIPT.json');source=root/'source';cache=root/'native-cache'
    need(result['status']=='PASS_T74_JOINT_TWELVE_COLD_COMPLETE_RELEASE' and result['explicit_native_cache_reuse'] is False,'local baseline must be a completed fresh cold replay')
    need(Fraction(result['kappa'])==Fraction(vendor_claim['kappa']) and Fraction(result['complex_lower'])==Fraction(vendor_claim['complex_lower']),'complete baseline claim binding')
    need(result['profile']=={str(k):v for k,v in vendor_claim['profile'].items()},'baseline full profile')
    need(result['native_receipt_sha256']==sha(root/'NATIVE-RECEIPT.json'),'baseline native receipt binding')
    need(native['status']=='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and native['source_commit']=='local-joint12-pr2733' and native['manifest_sha256']==SOURCE_SHA,'complete native source binding')
    need(sha(source/'MANIFEST.json')==SOURCE_SHA and len(read(source/'MANIFEST.json'))==506 and tree(source,('MANIFEST.json',))==read(source/'MANIFEST.json'),'exact 506 derived frontier source files')
    need(tree(cache)==native['cache_files'],'complete local native/parent cache file hashes')
    stages=result['cold_stages'];need(len(stages)==7 and {s['name']for s in stages}==COLD_STAGES and all(s['exit_code']==0 for s in stages),'all fresh baseline stages')
    for s in stages:need(sha(root/(s['name']+'.log'))==s['log_sha256'],'baseline stage log binding')
    package=root/'admission/package';release=root/'admission/release/RELEASE-RECEIPT.json';receipt=read(release)
    need(result['release_receipt_sha256']==sha(release) and receipt['status']=='PASS_RELEASE','completed baseline release receipt')
    need(result['package_manifest_sha256']==sha(package/'MANIFEST.json')==receipt['manifest_sha256'],'baseline admitted package manifest binding')
    need(tree(package,('MANIFEST.json',))==read(package/'MANIFEST.json'),'complete admitted baseline package')
    need(Fraction(receipt['kappa_decimal'])==Fraction(result['kappa']),'baseline release rational')
    return dict(result_sha256=sha(root/'RESULT.json'),native_receipt_sha256=sha(root/'NATIVE-RECEIPT.json'),source_manifest_sha256=SOURCE_SHA,cache_files=native['cache_files'],release_receipt_sha256=sha(release),scope='Explicit reuse of completed local fresh baseline; no native rerun by this invocation.')

def authenticate_prepared_native(root):
    result=read(root/'RESULT.json');receipt=read(root/'NATIVE-RECEIPT.json')
    need(result['status']=='PASS_PORTABLE_NATIVE_PREPARATION','native producer PASS, without any intermediate T74 admission claim')
    need(result['native_receipt_sha256']==sha(root/'NATIVE-RECEIPT.json'),'native producer receipt binding')
    need(receipt['status']=='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and receipt['source_commit']=='local-joint12-pr2733' and receipt['manifest_sha256']==SOURCE_SHA,'native producer source/protocol binding')
    source=root/'source';cache=root/'native-cache'
    need(sha(source/'MANIFEST.json')==SOURCE_SHA and len(read(source/'MANIFEST.json'))==506 and tree(source,('MANIFEST.json',))==read(source/'MANIFEST.json'),'exact506 derived source')
    need(tree(cache)==receipt['cache_files'],'complete producer native/parent cache')
    need(receipt['fresh_current_provider_count']==2,'both changed current providers freshly checked')
    fresh=receipt['fresh_retained_native_count'];reused=receipt['reused_retained_native_count']
    need((fresh,reused)in ((2,0),(0,2)) and receipt['fresh_retained_parent']==(fresh==2) and receipt['reused_retained_parent']==(reused==2),'explicit retained fresh/reuse accounting')
    if reused:need(receipt['retained_reuse_receipt_sha256']==sha(root/'RETAINED-REUSE.json'),'retained reuse receipt binding')
    return dict(result_sha256=sha(root/'RESULT.json'),native_receipt_sha256=sha(root/'NATIVE-RECEIPT.json'),source_manifest_sha256=SOURCE_SHA,cache_files=receipt['cache_files'],fresh_current_provider_count=2,fresh_retained_native_count=fresh,reused_retained_native_count=reused,scope='Native preparation only; actual replica release checked separately.')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--package',type=Path,default=HERE)
    ap.add_argument('--baseline-dir',type=Path)
    ap.add_argument('--baseline-pins',type=Path)
    ap.add_argument('--source',type=Path,help='Optional authenticated preobtained original PR2679 tree; otherwise pinned HTTPS download.')
    ap.add_argument('--native-preparer',type=Path)
    ap.add_argument('--blocknorm-checker',type=Path,help='Actual source-topology/block-norm certificate checker, hash-bound and required by admission.')
    ap.add_argument('--reuse-retained-baseline',type=Path,help='Explicit unchanged retained2 native chains and retained-parent reuse; current2 providers still freshly checked.')
    ap.add_argument('--reuse-frontier-baseline',type=Path,help='Explicit completed fresh PR2802 T74 cold baseline reuse; a native-only bundle is not a completed baseline.')
    ap.add_argument('--fill',type=Path);ap.add_argument('--order',type=Path);ap.add_argument('--dispatch',type=Path)
    ap.add_argument('--comparison-claim',type=Path)
    ap.add_argument('--replica-helper-dir',type=Path);ap.add_argument('--reconstructor',type=Path);ap.add_argument('--admission-driver',type=Path)
    ap.add_argument('--jobs',type=int,default=4)
    ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--check-only',action='store_true',help='Only authenticate vendored/input/reuse files; run no proof subprocesses.')
    a=ap.parse_args();need(not sys.flags.optimize and 1<=a.jobs<=4,'enabled assertions/one to four jobs');sys.dont_write_bytecode=True
    need(not (a.reuse_frontier_baseline and a.reuse_retained_baseline),'choose completed-baseline reuse or retained-only reuse')
    package=a.package.resolve();vendor=(a.baseline_dir or package/'vendor/frontier').resolve();pins=(a.baseline_pins or package/'vendor/frontier/DOWNLOAD-MANIFEST.json').resolve()
    fill=(a.fill or package/'data/FILL.json.gz').resolve();order=(a.order or package/'data/ORDER.json').resolve();dispatch=(a.dispatch or package/'data/DISPATCH.json').resolve()
    comparison=(a.comparison_claim or package/'references/PR2802-CLAIM.json').resolve()
    helper=(a.replica_helper_dir or package).resolve();reconstructor=(a.reconstructor or package/'reconstruct_replica.py').resolve();driver=(a.admission_driver or package/'admit_frontier_replica.py').resolve()
    preparer=(a.native_preparer or package/'portable_prepare_native.py').resolve()
    blocknorm=(a.blocknorm_checker or package/'blocknorm_certificate.py').resolve()
    vendor_inventory=authenticate_vendor(vendor,pins)
    need(sha(comparison)==COMPARISON_SHA and 'kappa'in read(comparison) and 'headline_kappa_source'not in read(comparison),'exact full PR2802 headline claim')
    files=[fill,order,dispatch,comparison,reconstructor,driver,preparer,blocknorm,helper/'lift_parent.py',helper/'replica_parent.py']
    inputs={str(p):sha(p)for p in files};order_value=read(order);need(order_value,'nonempty literal owner order')
    T=1+max(r for st,r in order_value);need(T==EXPECTED_REPLICAS and len(order_value)==9*T and set(map(tuple,order_value))=={(st,r)for st in range(9)for r in range(T)},'complete T114 candidate replica coverage')
    reuse=a.reuse_frontier_baseline.resolve()if a.reuse_frontier_baseline else None
    binding=authenticate_completed_baseline(reuse,read(vendor/'CLAIM.json'))if reuse else None
    work=a.work.resolve();need(not work.exists(),'fresh external work directory')
    for root in [package,vendor,helper]+[p.resolve()for p in (a.source,reuse,a.reuse_retained_baseline)if p]:need(not work.is_relative_to(root),'work/input tree separation')
    if a.check_only:
        print(json.dumps(dict(status='PASS_PORTABLE_INPUT_PREFLIGHT_NOT_ADMISSION',T=T,vendor_files=len(vendor_inventory),input_sha256=inputs,expected_T114_kappa=str(EXPECTED_T114_KAPPA),predecessor_T104_kappa=str(PREDECESSOR_T104_KAPPA),blocknorm_checker_sha256=inputs[str(blocknorm)],explicit_baseline_reuse=bool(reuse),baseline_binding={k:v for k,v in binding.items()if k!='cache_files'}if binding else None),sort_keys=True));return
    work.mkdir(parents=True);shim=work/'process-lf-adapter';shim.mkdir();(shim/'sitecustomize.py').write_text(LF_ADAPTER,encoding='utf-8',newline='\n')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    env['PYTHONPATH']=str(shim)+(os.pathsep+env['PYTHONPATH']if env.get('PYTHONPATH')else'')
    for name in ('PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD'):env.pop(name,None)
    stages=[];start=time.monotonic()
    def run(name,script,*args):
        begin=time.monotonic();command=[sys.executable,'-B',str(script),*map(str,args)];log=work/(name+'.log')
        with log.open('w',encoding='utf-8')as f:r=subprocess.run(command,env=env,cwd=work,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,exit_code=r.returncode,command=command,script_sha256=sha(script),log_sha256=sha(log),seconds=time.monotonic()-begin));write(work/'STAGES.json',stages)
        need(r.returncode==0,'failed '+name+'; see '+str(log));print('PASS',name,flush=True)
    if reuse:baseline=reuse
    else:
        baseline=work/'native' # Leave absent: native producer requires fresh --work.
        opts=[]
        if a.source:opts+=['--source',a.source.resolve()]
        if a.reuse_retained_baseline:opts+=['--reuse-retained-baseline',a.reuse_retained_baseline.resolve()]
        if a.prepare_only:opts+=['--prepare-only']
        run('native-preparation',preparer,'--work',baseline,'--vendor-frontier',vendor,'--jobs',a.jobs,*opts)
        if a.prepare_only:
            prepared=read(baseline/'RESULT.json')
            need(prepared['status']=='PASS_AUTHENTICATED_NATIVE_SOURCE_PREPARATION_ONLY' and prepared['native_receipt_issued'] is False and not (baseline/'NATIVE-RECEIPT.json').exists(),'prepare-only emits no native proof or admission')
            need(authenticate_vendor(vendor,pins)==vendor_inventory and all(sha(Path(p))==h for p,h in inputs.items()),'unchanged prepared inputs')
            receipt=dict(status='PREPARED_PORTABLE_REPLICA_NOT_ADMITTED',replicas=T,native_preparation_result_sha256=sha(baseline/'RESULT.json'),native_receipt_issued=False,admission_run=False,input_sha256=inputs,vendor_inventory_sha256=BASELINE_PINS_SHA,stages=stages,scope='Source preparation only; no native proof checks or replica admission.')
            write(work/'RESULT.json',receipt);print(receipt['status'],flush=True);return
        binding=authenticate_prepared_native(baseline)
    args=['--source',baseline/'source','--fill',fill,'--order',order,'--dispatch',dispatch,'--native-cache',baseline/'native-cache','--native-receipt',baseline/'NATIVE-RECEIPT.json','--work',work/'candidate','--replica-helper-dir',helper,'--blocknorm-checker',blocknorm,'--reconstructor',reconstructor,'--comparison-claim',comparison,'--source-profile','pr2802','--comparison-profile','pr2802','--jobs',a.jobs]
    if a.prepare_only:args+=['--prepare-only']
    run('replica-candidate',driver,*args)
    result=read(work/'candidate/RESULT.json')
    if a.prepare_only:need(result['status']=='PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED','prepared status')
    else:
        need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','full candidate release status')
        need(result['replicas']==EXPECTED_REPLICAS and Fraction(result['kappa'])==EXPECTED_T114_KAPPA,'complete exact T114 target binding')
        need(Fraction(result['kappa'])>PREDECESSOR_T104_KAPPA,'strict gain over the complete exact T104 rational')
        need(Fraction(result['kappa'])>Fraction(read(comparison)['kappa']),'strict exact full headline gain')
    need(authenticate_vendor(vendor,pins)==vendor_inventory,'vendored baseline changed')
    need(all(sha(Path(p))==h for p,h in inputs.items()),'input bytes changed')
    need((authenticate_completed_baseline(baseline,read(vendor/'CLAIM.json'))if reuse else authenticate_prepared_native(baseline))==binding,'native/source/cache inputs changed')
    receipt=dict(status='PREPARED_PORTABLE_REPLICA_NOT_ADMITTED'if a.prepare_only else'PASS_PORTABLE_REPLICA_COMPLETE_RELEASE',replicas=T,explicit_local_baseline_reuse=bool(reuse),fresh_native_preparation_run=not bool(reuse),explicit_retained_only_reuse=bool(a.reuse_retained_baseline),baseline_binding=binding,candidate_result_sha256=sha(work/'candidate/RESULT.json'),candidate_status=result['status'],kappa=result.get('kappa'),input_sha256=inputs,vendor_inventory_sha256=BASELINE_PINS_SHA,comparison_claim_sha256=COMPARISON_SHA,predecessor_T104_kappa=str(PREDECESSOR_T104_KAPPA),expected_T114_kappa=str(EXPECTED_T114_KAPPA),blocknorm_checker_sha256=inputs[str(blocknorm)],stages=stages,seconds=time.monotonic()-start,python=platform.python_version(),compatibility=dict(scope='Process-scoped UTF8/LF text adapter only; all upstream hash predicates remain unchanged.',adapter_sha256=sha(shim/'sitecustomize.py')),scope=result['scope'])
    write(work/'RESULT.json',receipt);print(receipt['status'],result.get('kappa_decimal',''),flush=True)
if __name__=='__main__':main()

