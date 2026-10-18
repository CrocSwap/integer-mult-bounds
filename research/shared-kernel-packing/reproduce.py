# SPDX-License-Identifier: Apache-2.0
"""Cold/shared-native replay from exact PR2833 source; explicit retained reuse optional."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent

def need(c,m):
    if not c:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def authenticate():
    pins=read(HERE/'MANIFEST.json');actual={}
    for f in HERE.rglob('*'):
        need(not f.is_symlink(),'package symlink')
        if f.is_file()and f!=HERE/'MANIFEST.json':actual[f.relative_to(HERE).as_posix()]=sha(f)
    need(actual==pins,'complete package inventory/hashes');return pins

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--prepared-retained',type=Path);ap.add_argument('--jobs',type=int,choices=range(1,4),default=3);ap.add_argument('--dry-run',action='store_true');a=ap.parse_args();need(not sys.flags.optimize,'assertions required');pins=authenticate();sys.path.insert(0,str(HERE/'tools'))
    from materialize_source import authenticate_source,MANIFEST_SHA
    source=a.source.resolve();work=a.work.resolve();sourcepins=authenticate_source(source)
    need(not work.exists()and not work.is_relative_to(HERE)and not HERE.is_relative_to(work)and not work.is_relative_to(source)and not source.is_relative_to(work),'fresh disjoint external work')
    expected=Q('0.001720100805416885927944')-Q(1,10**46)-Q(1,10**70);need(Q(read(HERE/'CLAIM.json')['kappa'])==expected,'frozen full headline')
    core=HERE/'vendor/pr2857';retained=a.prepared_retained.resolve()if a.prepared_retained else work/'retained-native'
    if a.prepared_retained:
        need(not retained.is_relative_to(work)and not work.is_relative_to(retained),'reuse/work disjoint')
        rr=read(retained/'RESULT.json');need(rr['status']=='PASS_PR2833_FRESH_NATIVE_PREPARATION'and rr['native_receipt_sha256']==sha(retained/'NATIVE-RECEIPT.json'),'completed source-bound retained preparation')
        need(rr['source_manifest_sha256']in[MANIFEST_SHA,'44ed6a457e1d1ba24726f35db86dc9e551072dd9331a8fed3ad3f0efa33ff0be'],'known immutable retained source')
    recipe=[]
    if not a.prepared_retained:recipe.append(('fresh-retained-bootstrap',[sys.executable,'-B',HERE/'tools/prepare_retained.py','--source',source,'--out',retained,'--jobs',str(a.jobs)]))
    overlay=work/'source';native=work/'shared-native';candidate=work/'candidate';bound=work/'prepare_shared_bound.py'
    recipe += [('derive-source',[sys.executable,'-B',core/'build_overlay.py','--source',source,'--generator',core/'shared_kernel.py','--review',core/'review_four_groups.py','--candidate-dir',core/'words','--out',overlay]),('fresh-shared-native',[sys.executable,'-B',bound,'--source',overlay,'--retained-cache',retained/'native-cache','--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',native,'--jobs',str(min(2,a.jobs))]),('complete-admission',[sys.executable,'-B',HERE/'tools/admit2857.py','--source',overlay,'--fill',HERE/'data/FILL.json.gz','--order',HERE/'data/ORDER.json','--dispatch',HERE/'data/DISPATCH.json','--native-cache',native/'native-cache','--native-receipt',native/'NATIVE-RECEIPT.json','--work',candidate,'--replica-helper-dir',core/'vendor/pr2839','--reconstructor',core/'vendor/pr2839/reconstruct_replica.py','--blocknorm-checker',core/'vendor/pr2839/blocknorm_certificate.py','--comparison-claim',core/'CLAIM.json','--source-profile','shared-four','--comparison-profile','pr2857','--jobs','1'])]
    if a.dry_run:
        print(json.dumps(dict(status='PREFLIGHT_ONLY_NOT_REPLAY',explicit_retained_reuse=bool(a.prepared_retained),commands=[dict(stage=n,argv=list(map(str,c)))for n,c in recipe]),indent=2));return
    work.mkdir(parents=True);env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONPATH',None)
    for n in ['PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(n,None)
    stages=[]
    for name,cmd in recipe:
        if name=='fresh-shared-native':
            # Bind the unchanged strict preparer to THIS authenticated bootstrap.
            template=(core/'prepare_shared_native.py').read_text(encoding='utf-8');old="OLD_RECEIPT_SHA='a56d2fe28812e93c5526564ef77f7e5e8d1cbb111efeb6c3b0f53c9ec01ca2bc'";need(template.count(old)==1,'exact retained pin preimage');h=sha(retained/'NATIVE-RECEIPT.json');body=template.replace(old,"OLD_RECEIPT_SHA='"+h+"'");bound.write_text(body,encoding='utf-8',newline='\n')
            (work/'RETAINED-PIN.json').write_text(json.dumps(dict(template_sha256=sha(core/'prepare_shared_native.py'),bound_preparer_sha256=sha(bound),retained_receipt_sha256=h,scope='One exact receipt pin changes; all full-cache, source, native-word,16-stage parent and new native checks remain. Fresh/explicit reused provenance recorded separately.'),indent=2)+'\n',encoding='utf-8',newline='\n')
        log=work/(name+'.txt');start=time.monotonic()
        with log.open('w',encoding='utf-8',newline='\n')as out:proc=subprocess.run(list(map(str,cmd)),env=env,cwd=work,stdout=out,stderr=subprocess.STDOUT)
        stages.append(dict(stage=name,exit_code=proc.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));(work/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n',encoding='utf-8',newline='\n');need(proc.returncode==0,'failed '+name+'; see '+str(log));print('PASS',name,flush=True)
    result=read(candidate/'RESULT.json');release=read(candidate/'release/RELEASE-RECEIPT.json');need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE','complete final release');need(Q(result['kappa'])==Q(release['kappa_decimal'])==expected,'exact frozen headline');need(sha(candidate/'release/RELEASE-RECEIPT.json')==result['release_receipt_sha256']and result['package_manifest_sha256']==release['manifest_sha256'],'release chain');need(authenticate()==pins and authenticate_source(source)==sourcepins,'immutable input drift')
    final=dict(status='PASS_T185_PORTABLE_COMPLETE_REPLAY',kappa=str(expected),fresh_changed_native_chains=2,explicit_retained_reuse=bool(a.prepared_retained),fresh_retained_bootstrap=not bool(a.prepared_retained),native_receipt_sha256=sha(native/'NATIVE-RECEIPT.json'),candidate_result_sha256=sha(candidate/'RESULT.json'),stages=stages,scope='Conditional finite and outer release; inherited all-size hypotheses remain.')
    (work/'RESULT.json').write_text(json.dumps(final,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n');print(final['status'])
if __name__=='__main__':main()
