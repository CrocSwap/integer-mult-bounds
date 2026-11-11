#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Integration by Rohan Arun with substantial OpenAI Codex assistance.
# Upstream scientific scripts remain byte-for-byte unchanged; see DEPENDENCIES.json.
"""Portable complete T488/retimed-supplier composition replay.

--check-inputs authenticates the small vendored closure without scientific replay.
--materialize-only reconstructs pinned sources and their existing source controls.
The default path regenerates literal owners, two fresh changed-native chains,
and every inherited complete admission/outer gate. Parent reuse is explicit.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,hashlib,json,os,platform,subprocess,sys,time

HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def read(path):
    data=path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def safe_file(base,relative):
    rel=Path(relative)
    need(not rel.is_absolute() and '..' not in rel.parts,'unsafe dependency path')
    path=base/rel
    need(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(base),'dependency must be an ordinary contained file')
    return path

def authenticate():
    need(__debug__ and not sys.flags.optimize,'enabled assertions required by inherited scientific gates')
    dependencies=read(HERE/'DEPENDENCIES.json');spec=read(HERE/'SPEC.json')
    need(dependencies['schema']=='retimed-t488-full-replay-dependencies/v1','dependency manifest schema')
    expected=set(dependencies['files'])
    actual={p.relative_to(HERE).as_posix() for directory in ('vendor','comparator') for p in (HERE/directory).rglob('*') if p.is_file()}
    need(actual==expected,'exact vendored file inventory')
    for rel,row in dependencies['files'].items():
        p=safe_file(HERE,rel);body=p.read_bytes()
        need(sha(p)==row['sha256'],'immutable dependency hash '+rel)
        need(hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==row['git_blob'],'Git blob identity '+rel)
        need(row['head']==dependencies['upstreams'][row['dependency']],'dependency head identity')
    main=read(HERE/dependencies['main_export_manifest'])
    need(main['base_commit']==dependencies['frozen_main_commit'] and len(main['sha256'])==dependencies['main_export_file_count'],'frozen main export inventory')
    owner=read(HERE/'vendor/pr3633/owners/SOURCE-PINS.json')
    need(all(main['sha256'].get(p)==h for p,h in owner['repo_files'].items()),'owner source closure covered by authenticated main export')
    comparator=read(HERE/'comparator/PR3642-CLAIM.json')
    prior=Q(comparator['kappa'])
    need(prior==Q(spec['comparison_kappa']),'exact exported modern comparator')
    return dependencies,spec,prior

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,help='Read-only Git repository containing the frozen main object')
    ap.add_argument('--work',type=Path,help='Fresh writable output directory outside this package and the source repository')
    ap.add_argument('--jobs',type=int,choices=(1,2),default=1)
    ap.add_argument('--check-inputs',action='store_true')
    ap.add_argument('--materialize-only',action='store_true')
    a=ap.parse_args();dependencies,spec,prior=authenticate()
    if a.check_inputs:
        need(not a.materialize_only,'choose one bounded mode')
        print(json.dumps({'status':'PASS_FULL_REPLAY_INPUT_INTEGRITY_ONLY','vendored_files':len(dependencies['files']),'main_export_files':dependencies['main_export_file_count'],'comparator':str(prior),'scope':'No source materialization, native replay, ownership, controller or outer admission executed.'},sort_keys=True));return
    need(a.repo is not None and a.work is not None,'--repo and --work required for materialization or full replay')
    repo=a.repo.resolve();work=a.work.resolve();package=HERE.parent
    need(repo.exists() and not work.exists() and work.parent.is_dir(),'existing source repository and fresh output under an existing parent required')
    need(not work.is_relative_to(package) and not work.is_relative_to(repo),'work must be outside package and read-only repository')
    need(os.access(work.parent,os.W_OK),'output parent must be writable')
    # On macOS an absent removable volume must never become a fake mount directory.
    if sys.platform=='darwin' and work.parts[:2]==('/','Volumes'):
        need(len(work.parts)>2 and os.path.ismount(Path(*work.parts[:3])),'actual external volume mount required')
    work.mkdir();(work/'tmp').mkdir()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPYCACHEPREFIX=str(work/'pycache'),PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',TMPDIR=str(work/'tmp'),GIT_NO_REPLACE_OBJECTS='1',GIT_OPTIONAL_LOCKS='0')
    for key in ('PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER'):env.pop(key,None)
    stages=[];before={p:row['sha256'] for p,row in dependencies['files'].items()}
    write(work/'PLAN.json',{'status':'EXPERIMENT_NOT_ADMITTED','started_unix':time.time(),'pid':os.getpid(),'python':sys.version,'platform':platform.platform(),'entrypoint_sha256':sha(Path(__file__)),'dependencies_sha256':sha(HERE/'DEPENDENCIES.json'),'spec_sha256':sha(HERE/'SPEC.json'),'upstreams':dependencies['upstreams'],'comparison_claim_sha256':sha(HERE/'comparator/PR3642-CLAIM.json'),'scope':spec['scope']})
    def run(label,args,extra=None):
        cmd=[sys.executable,'-B',*map(str,args)];started=time.time()
        write(work/'ACTIVE.json',{'stage':label,'command':cmd,'started_unix':started,'parent_pid':os.getpid()})
        print('START',label,flush=True)
        with (work/(label+'.log')).open('w') as log:
            child=subprocess.run(cmd,cwd=work,env=dict(env,**(extra or {})),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
        stages.append({'stage':label,'command':cmd,'exit_code':child.returncode,'seconds':time.time()-started,'log_sha256':sha(work/(label+'.log'))})
        write(work/'STAGES.json',stages)
        need(child.returncode==0,label+' failed; preserved log '+str(work/(label+'.log')))
        print('PASS',label,flush=True)
    try:
        materialized=work/'materialized'
        run('source-materialization',[HERE/'vendor/pr3642/reproduce.py','--repo',repo,'--work',materialized,'--materialize-only'])
        src=materialized/'retimed';source=src/'source';old=materialized/'prepared/predecessor';main_files=materialized/'main-files'
        manifest=read(source/'MANIFEST.json')
        need(sha(source/'MANIFEST.json')==dependencies['source_manifest_sha256'] and len(manifest)==dependencies['source_file_count'],'exact retimed source manifest')
        need(all(sha(source/p)==h for p,h in manifest.items()),'complete retimed source payload')
        if a.materialize_only:
            need(all(sha(HERE/p)==h for p,h in before.items()),'immutable dependencies changed')
            write(work/'RESULT.json',{'status':'PASS_T488_COMPOSITION_SOURCE_MATERIALIZATION_ONLY','source_manifest_sha256':sha(source/'MANIFEST.json'),'source_files':len(manifest),'stages':stages,'scope':'Fresh upstream reconstruction and existing source controls. No literal T488 owners, native providers, controller or full release replay.'})
            print('PASS_T488_COMPOSITION_SOURCE_MATERIALIZATION_ONLY');return
        allocation=work/'allocation'
        run('t488-literal',[HERE/'vendor/pr3633/owners/portable_expand.py','--out',allocation],{'OWNER_SOURCE_REPO':str(main_files)})
        fill=read(allocation/'FILL.json.gz');order=read(allocation/'ORDER.json')
        need(fill['columns']==spec['fill_columns'] and len(fill['rows'])==spec['roles'] and len(order)==spec['calls'],'complete literal T488 allocation')
        need(not fill.get('dispatch_overrides',[]),'no dispatch overrides')
        oldproviders=read(allocation/'PROVIDERS.json');newproviders=read(source/'new/BORROW-PROVIDERS.json')
        need(set(oldproviders)==set(newproviders),'provider inventory')
        need(all(oldproviders[p]['widths']==newproviders[p]['widths'] for p in oldproviders),'every retained role has identical width')
        oldprofile={int(k):v for k,v in read(allocation/'PROFILE.json').items()};profile=dict(oldprofile)
        oldlocals=[{int(k):v for k,v in p['actual_paid_profile'].items()} for p in oldproviders.values()]
        newlocals=[{int(k):v for k,v in p['actual_paid_profile'].items()} for p in newproviders.values()]
        need(all(x==oldlocals[0] for x in oldlocals) and all(x==newlocals[0] for x in newlocals),'both provider profiles agree')
        oldlocal,newlocal=oldlocals[0],newlocals[0]
        for k in oldlocal.keys()|newlocal.keys():profile[k]=profile.get(k,0)+len(order)*(newlocal.get(k,0)-oldlocal.get(k,0))
        need(profile=={int(k):v for k,v in spec['expected_complete_profile'].items()},'expected full profile derived from actual local bills')
        need(sum(k*v for k,v in profile.items())==sum(k*v for k,v in oldprofile.items())==spec['rank_mass_per_replica']*spec['replicas'],'unchanged complete rank mass')
        write(work/'EXPECTED-PROFILE.json',{'profile':profile,'oldlocal':oldlocal,'newlocal':newlocal,'calls':len(order),'scope':'Expected only; independent physical admission must reproduce this invoice.'})
        run('fresh-native',[src/'prepare_extension_native.py','--source',source,'--retained-cache',old/'native-cache','--retained-receipt',old/'NATIVE-RECEIPT.json','--out',work/'native','--jobs',a.jobs])
        fill['dispatch_overrides']=[];legacy=work/'FILL-legacy.json.gz';legacy.write_bytes(gzip.compress(json.dumps(fill,separators=(',',':')).encode(),mtime=0));del fill
        command=[src/'admit_extension.py']
        paths={'source':source,'fill':legacy,'order':allocation/'ORDER.json','dispatch':allocation/'DISPATCH.json','native-cache':work/'native/native-cache','native-receipt':work/'native/NATIVE-RECEIPT.json','work':work/'admission','replica-helper-dir':old/'helpers','reconstructor':old/'helpers/reconstruct_replica.py','comparison-claim':old/'PR2969-CLAIM.json','blocknorm-checker':old/'adapters/extension_blocknorm.py'}
        for key,value in paths.items():command+=['--'+key,value]
        command+=['--source-profile','staged3605','--comparison-profile','pr2969','--jobs',a.jobs]
        run('complete-admission',command)
        result=read(work/'admission/RESULT.json');receipt=work/'admission/release/RELEASE-RECEIPT.json';release=read(receipt)
        need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and result['replicas']==spec['replicas'],'completed exact T488 admission')
        need({int(k):v for k,v in result['profile'].items()}==profile,'admitted complete profile')
        kappa=Q(result['kappa']);C=Q(result['complex_lower'])
        need(kappa==C-Q(spec['outer_margin'])-Q(spec['grid_margin']) and C==Q(spec['expected_complex_lower']) and kappa>prior,'exact modern headline and improvement over pinned PR3642')
        need(Q(result['kappa_decimal'])==kappa and release['status']=='PASS_RELEASE' and Q(release['kappa_decimal'])==kappa,'final rational/decimal release agreement')
        need(result['release_receipt_sha256']==sha(receipt) and release['manifest_sha256']==result['package_manifest_sha256']==sha(work/'admission/package/MANIFEST.json'),'final scientific receipt/package binding')
        need(sha(source/'MANIFEST.json')==dependencies['source_manifest_sha256'] and all(sha(source/p)==h for p,h in manifest.items()),'immutable source drift')
        need(all(sha(HERE/p)==h for p,h in before.items()),'immutable vendored input drift')
        write(work/'RESULT.json',{'status':'PASS_T488_RETIMER_COMPLETE_CONDITIONAL_RELEASE','kappa':str(kappa),'kappa_decimal':result['kappa_decimal'],'complex_lower':str(C),'prior_PR3642':str(prior),'absolute_gain':str(kappa-prior),'profile':profile,'source_manifest_sha256':sha(source/'MANIFEST.json'),'package_manifest_sha256':release['manifest_sha256'],'release_receipt_sha256':sha(receipt),'native_receipt_sha256':sha(work/'native/NATIVE-RECEIPT.json'),'comparison_claim_sha256':sha(HERE/'comparator/PR3642-CLAIM.json'),'dependencies_sha256':sha(HERE/'DEPENDENCIES.json'),'stages':stages,'scope':spec['scope'],'reuse':'Two current providers freshly replayed. Unchanged predecessor native and parent admission reused only through the unchanged source-bound upstream authentication.'})
        print('PASS_T488_RETIMER_COMPLETE_CONDITIONAL_RELEASE',result['kappa_decimal'],flush=True)
    except Exception as exc:
        write(work/'RESULT.json',{'status':'FAILED_PRESERVED','error':str(exc),'stages':stages,'scope':'No conditional improvement claimed by this failed run.'})
        raise
if __name__=='__main__':main()
