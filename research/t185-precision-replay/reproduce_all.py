#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cold source-bound replay of the T185 baseline and 40-digit parameter refinement.

Needs local Git objects for the two immutable heads below and an isolated Python
with the baseline's documented dependencies. Never fetches, edits the repository,
or reuses an existing baseline run. Every generated artifact stays under --work.
Credit PR2863/2857/2833 and their retained lineage. Prepared by digitalis-p with
substantial OpenAI Codex assistance. Finite success is not a full theorem proof.
"""
import argparse
import contextlib
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import traceback

sys.dont_write_bytecode = True
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
HEAD = '34328b1d5e5bebac62d5cabec993dfbfd7b2123f'
PREFIX = 'research/shared-kernel-packing'
MANIFEST_SHA = 'e1276c24fba1eb4c83ae040da63addad4a73f83120775ab40a79136c6080d59b'
SOURCE_HEAD = 'e9307b48d7d1b690939935ecef0f8e524e6d92f4'
SOURCE_MANIFEST = 'c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
OVERLAY_MANIFEST = '54dc42f25c1d8b85adcf593c4bf6c0f83f7351388af857812790b8a0b4c3d869'
RECOVERY = {'.gitattributes', 'vendor/pr2857/.gitattributes'}
RECOVERY_BYTES = b'* -text\n'
RECOVERY_SHA = '705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da'
C24 = Q('0.001720100805416885927944')
C40 = Q('0.0017201008054168859279440070756063355312')
BASELINE_K = C24-Q(1,10**46)-Q(1,10**70)
CANDIDATE_K = C40-Q(1,10**62)-Q(1,10**86)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw): return hashlib.sha256(raw).hexdigest()
def sha(path): return digest(path.read_bytes())
def read(path): return json.loads(path.read_bytes())
def write(path, data):
    # Only caller-created work files are written. Atomic replace preserves the
    # last complete receipt if execution is interrupted between stage updates.
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    tmp.replace(path)


def decimal(q):
    with localcontext() as ctx:
        ctx.prec=110
        return str(Decimal(q.numerator)/Decimal(q.denominator))


def safe_relative(name):
    p=PurePosixPath(name)
    need(name and not p.is_absolute() and '..' not in p.parts and
         '\\' not in name and '\0' not in name and ':' not in name,
         'unsafe source path: '+repr(name))
    need('__pycache__' not in p.parts and p.suffix!='.pyc','bytecode in immutable source')
    return p


def inventory(root, exclude=()):
    need(root.is_dir() and not root.is_symlink(),'real source directory required')
    result={}
    for path in sorted(root.rglob('*')):
        name=path.relative_to(root).as_posix()
        safe_relative(name)
        need(not path.is_symlink(),'source symlink: '+name)
        if path.is_file():
            if name not in exclude:
                result[name]=sha(path)
        else:
            need(path.is_dir(),'special source entry: '+name)
    return result


def authenticate_source(root, manifest_sha, count):
    need(sha(root/'MANIFEST.json')==manifest_sha,'exact source manifest hash')
    pins=read(root/'MANIFEST.json')
    need(isinstance(pins,dict) and len(pins)==count,'complete manifest entry count')
    for name in pins:
        safe_relative(name)
    need(inventory(root,('MANIFEST.json',))==pins,'complete immutable source bytes')
    return pins


def authenticate_pair(original,recovered=None):
    need(sha(original/'MANIFEST.json')==MANIFEST_SHA,'PR2863 manifest pin')
    pins=read(original/'MANIFEST.json')
    need(isinstance(pins,dict) and len(pins)==164,'PR2863 manifest inventory')
    for name in pins:
        safe_relative(name)
    actual=inventory(original,('MANIFEST.json',))
    need(set(pins)-set(actual)==RECOVERY,'exact two missing published paths')
    need(actual=={n:h for n,h in pins.items() if n not in RECOVERY},
         'all present published source hashes and no extra files')
    need(digest(RECOVERY_BYTES)==RECOVERY_SHA and
         all(pins[n]==RECOVERY_SHA for n in RECOVERY),'manifest-bound recovery bytes')
    if recovered is not None:
        need(sha(recovered/'MANIFEST.json')==MANIFEST_SHA,'recovered manifest unchanged')
        need(inventory(recovered,('MANIFEST.json',))==pins,'complete recovered inventory')
        need(all((recovered/n).read_bytes()==RECOVERY_BYTES for n in RECOVERY),
             'exact recovered file contents')
    return pins


def git_export(repo,original,recovered,env):
    commands=[]
    for head in (HEAD,SOURCE_HEAD):
        argv=['git','-C',str(repo),'rev-parse','--verify',head+'^{commit}']
        result=subprocess.run(argv,env=env,capture_output=True,text=True,check=True)
        commands.append(argv)
        need(result.stdout.strip()==head,'exact commit locally available: '+head)
    argv=['git','-C',str(repo),'archive','--format=tar',HEAD,PREFIX]
    commands.append(argv)
    raw=subprocess.run(argv,env=env,capture_output=True,check=True).stdout
    prefix=PurePosixPath(PREFIX);files={}
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:
        for member in archive.getmembers():
            path=PurePosixPath(member.name)
            need(not path.is_absolute() and '..' not in path.parts and
                 '\\' not in member.name and ':' not in member.name,'unsafe archive path')
            if member.isdir() and (path==prefix or path in prefix.parents):
                continue
            need(path.is_relative_to(prefix),'archive member outside pinned package')
            name=path.relative_to(prefix).as_posix();safe_relative(name)
            need(member.isfile() or member.isdir(),'archive links/special files forbidden')
            if member.isdir():
                continue
            need(name not in files,'duplicate archive member')
            stream=archive.extractfile(member)
            need(stream is not None,'missing archive member stream')
            files[name]=stream.read()
    need('MANIFEST.json' in files and digest(files['MANIFEST.json'])==MANIFEST_SHA,
         'immutable exported manifest')
    pins=json.loads(files['MANIFEST.json'])
    actual={n:digest(b) for n,b in files.items() if n!='MANIFEST.json'}
    need(len(pins)==164 and set(pins)-set(actual)==RECOVERY and
         actual=={n:h for n,h in pins.items() if n not in RECOVERY},
         'complete present exported payload and exact missing pair')
    need(all(pins[n]==RECOVERY_SHA for n in RECOVERY),'exact expected recovery hashes')
    original.mkdir()
    for name,body in files.items():
        destination=original/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb') as f:
            f.write(body)
    authenticate_pair(original)
    shutil.copytree(original,recovered)
    for name in RECOVERY:
        with (recovered/name).open('xb') as f:
            f.write(RECOVERY_BYTES)
    authenticate_pair(original,recovered)
    return dict(status='PASS_EXACT_EXPORT_AND_SEPARATE_MANIFEST_BOUND_RECOVERY',
                head=HEAD,manifest_sha256=MANIFEST_SHA,present_entries=162,
                manifest_entries=164,recovered_files=sorted(RECOVERY),
                recovery_sha256=RECOVERY_SHA,recovery_bytes_hex=RECOVERY_BYTES.hex(),
                source_head_required=SOURCE_HEAD,commands=commands,network_fetch=False,
                original_wrapper_pass_claimed=False,
                scope='Published source retains both missing files; a separate exact recovery restores only their manifest-bound bytes. No checker or manifest is edited.')


def authenticate_release(candidate,expected):
    result=read(candidate/'RESULT.json')
    release=read(candidate/'release/RELEASE-RECEIPT.json')
    need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and
         release['status']=='PASS_RELEASE','complete finite and outer release statuses')
    need(Q(result['kappa'])==Q(release['kappa_decimal'])==expected,'exact release kappa')
    need(result['release_receipt_sha256']==sha(candidate/'release/RELEASE-RECEIPT.json'),
         'release receipt binding')
    manifest_sha=sha(candidate/'package/MANIFEST.json')
    need(result['package_manifest_sha256']==release['manifest_sha256']==manifest_sha,
         'complete candidate package manifest binding')
    need(inventory(candidate/'package',('MANIFEST.json',))==read(candidate/'package/MANIFEST.json'),
         'candidate complete manifested file inventory')
    need(all(s['exit_code']==0 for s in result['stages']),'all candidate stages passed')
    return result,release


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,required=True,help='Local Git repository containing both pinned heads; no fetch is performed')
    ap.add_argument('--work',type=Path,required=True,help='Fresh absolute work directory; all generated files stay here')
    ap.add_argument('--jobs',type=int,choices=(1,2),default=2)
    args=ap.parse_args()
    need(not sys.flags.optimize,'assertions must be enabled')
    need(args.work.is_absolute(),'--work must be absolute')
    need(not args.work.exists() and not args.work.is_symlink(),'fresh --work required')
    work=args.work.resolve();repo=args.repo.resolve()
    need(work.parent.is_dir(),'--work parent must already exist')
    need(repo.is_dir(),'local Git repository directory required')
    for input_root in (repo,HERE):
        need(not work.is_relative_to(input_root) and not input_root.is_relative_to(work),
             '--work must be disjoint from repository and orchestration package')
    runners=[HERE/n for n in ('reproduce_all.py','build_precision_driver.py','endpoint_refiner.py','verify_portable.py')]
    need(all(p.is_file() and not p.is_symlink() for p in runners),'four ordinary sibling scripts required')
    runner_pins={p.name:sha(p) for p in runners}
    work.mkdir()
    for name in ('logs','tmp','cache'):
        (work/name).mkdir()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',
             FINE_ENGINE_WORKERS='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',
             MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',GIT_OPTIONAL_LOCKS='0',
             TMPDIR=str(work/'tmp'),TMP=str(work/'tmp'),TEMP=str(work/'tmp'),
             XDG_CACHE_HOME=str(work/'cache'),PYTHONPYCACHEPREFIX=str(work/'cache'/'fresh-pycache'))
    for key in ('PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD',
                'FINE_ENGINE_CACHE','GAIN_PR564_SOURCE','MULTICOLD_SOURCE'):
        env.pop(key,None)
    started=datetime.now(timezone.utc).isoformat();stages=[];active=None
    original=work/'original-pr2863';recovered=work/'recovered-pr2863'
    source=work/'source-pr2833';baseline=work/'baseline';candidate=work/'candidate'
    def stage(name,argv=None,action=None):
        nonlocal active
        active=name;log=work/'logs'/(name+'.log');begin=time.monotonic()
        record=dict(name=name,kind='subprocess' if argv else 'internal',log=str(log.relative_to(work)))
        if argv:
            argv=list(map(str,argv));record['command']=argv
        try:
            with log.open('w',encoding='utf-8',newline='\n') as output:
                if argv:
                    completed=subprocess.run(argv,cwd=work,env=env,stdout=output,stderr=subprocess.STDOUT)
                    record['exit_code']=completed.returncode
                else:
                    with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):
                        value=action();print(json.dumps(value,sort_keys=True,indent=2))
                    record['exit_code']=0
        except BaseException:
            record['exit_code']=1
            with log.open('a',encoding='utf-8') as output:
                traceback.print_exc(file=output)
            raise
        finally:
            record.update(seconds=time.monotonic()-begin,log_sha256=sha(log))
            stages.append(record);write(work/'STAGES.json',stages)
        need(record['exit_code']==0,'failed '+name+'; retained log: '+str(log))
        print('PASS '+name,flush=True)
    try:
        write(work/'RUN.json',dict(started_utc=started,argv=sys.argv,source_heads=[HEAD,SOURCE_HEAD],
                                  runner_sha256=runner_pins,python=sys.version,executable=sys.executable,
                                  platform=platform.platform(),jobs=args.jobs,fine_engine_workers=1,
                                  baseline_reuse=False,network_fetch=False))
        def export_action():
            receipt=git_export(repo,original,recovered,env)
            write(work/'RECOVERY.json',receipt)
            return receipt
        stage('export-and-recover-pinned-source',action=export_action)
        stage('portable-finite-adapter',[sys.executable,'-B',HERE/'verify_portable.py',
                                        '--original',original,'--recovered',recovered,'--work',work/'portable-finite'])
        need(read(work/'portable-finite/RESULT.json')['status']=='PASS_INDEPENDENT_PORTABLE_FINITE_REPLAY',
             'complete portable finite result')
        stage('export-pr2833-source',[sys.executable,'-B',recovered/'tools/materialize_source.py',
                                     '--repo',repo,'--out',source])
        original_pins=authenticate_pair(original,recovered)
        source_pins=authenticate_source(source,SOURCE_MANIFEST,541)
        stage('cold-baseline',[sys.executable,'-B',recovered/'reproduce.py','--source',source,
                               '--work',baseline,'--jobs',str(args.jobs)])
        baseline_result=read(baseline/'RESULT.json')
        need(baseline_result['status']=='PASS_T185_PORTABLE_COMPLETE_REPLAY' and
             Q(baseline_result['kappa'])==BASELINE_K,'complete exact cold baseline')
        need(baseline_result['fresh_retained_bootstrap'] is True and
             baseline_result['explicit_retained_reuse'] is False and
             baseline_result['fresh_changed_native_chains']==2,'fresh baseline provenance')
        br,_=authenticate_release(baseline/'candidate',BASELINE_K)
        need(sha(baseline/'candidate/RESULT.json')==baseline_result['candidate_result_sha256'],
             'baseline candidate result binding')
        overlay=baseline/'source';native=baseline/'shared-native'
        overlay_pins=authenticate_source(overlay,OVERLAY_MANIFEST,547)
        native_receipt=read(native/'NATIVE-RECEIPT.json')
        native_hash=sha(native/'NATIVE-RECEIPT.json')
        need(native_receipt['status']=='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and
             native_receipt['manifest_sha256']==OVERLAY_MANIFEST and
             native_hash==baseline_result['native_receipt_sha256']==br['native_receipt_sha256'],
             'fresh native receipt and full source bindings')
        cache_pins=inventory(native/'native-cache')
        need(cache_pins==native_receipt['cache_files'],'complete native cache inventory')
        stage('generate-precision-driver',[sys.executable,'-B',HERE/'build_precision_driver.py',
                                          '--package',recovered,'--out',work/'driver40','--digits','40'])
        core=recovered/'vendor/pr2857'
        stage('complete-precision-admission',[sys.executable,'-B',work/'driver40/admit_precision.py',
              '--source',overlay,'--fill',recovered/'data/FILL.json.gz','--order',recovered/'data/ORDER.json',
              '--dispatch',recovered/'data/DISPATCH.json','--native-cache',native/'native-cache',
              '--native-receipt',native/'NATIVE-RECEIPT.json','--work',candidate,
              '--replica-helper-dir',core/'vendor/pr2839','--reconstructor',core/'vendor/pr2839/reconstruct_replica.py',
              '--blocknorm-checker',core/'vendor/pr2839/blocknorm_certificate.py',
              '--comparison-claim',recovered/'CLAIM.json','--source-profile','shared-four',
              '--comparison-profile','pr2863','--jobs','1'])
        cr,release=authenticate_release(candidate,CANDIDATE_K)
        need(Q(cr['complex_lower'])==C40 and Q(cr['comparison_kappa'])==BASELINE_K and
             Q(cr['gain'])==CANDIDATE_K-BASELINE_K>0,'exact refined endpoint and strict full-baseline gain')
        need(cr['comparison_head']==HEAD and cr['native_receipt_sha256']==native_hash,
             'candidate exact baseline/native provenance')
        baseline_spec=read(baseline/'candidate/package/new/SPEC.json')
        candidate_spec=read(candidate/'package/new/SPEC.json')
        for key in ('global_profile','live','physical'):
            need(baseline_spec['expected'][key]==candidate_spec['expected'][key],
                 'unchanged complete finite invoice: '+key)
        need(authenticate_pair(original,recovered)==original_pins and
             authenticate_source(source,SOURCE_MANIFEST,541)==source_pins and
             authenticate_source(overlay,OVERLAY_MANIFEST,547)==overlay_pins and
             inventory(native/'native-cache')==cache_pins and sha(native/'NATIVE-RECEIPT.json')==native_hash,
             'all immutable inputs and authenticated native evidence unchanged')
        need({p.name:sha(p) for p in runners}==runner_pins,'orchestration source drift')
        receipt=dict(status='PASS_COLD_BASELINE_AND_T185_PRECISION40_COMPLETE_RELEASE',
                     started_utc=started,completed_utc=datetime.now(timezone.utc).isoformat(),
                     baseline_head=HEAD,original_source_head=SOURCE_HEAD,baseline_kappa=str(BASELINE_K),
                     complex_lower=str(C40),kappa=str(CANDIDATE_K),kappa_decimal=decimal(CANDIDATE_K),
                     gain=str(CANDIDATE_K-BASELINE_K),gain_decimal=decimal(CANDIDATE_K-BASELINE_K),
                     native_source_reused_from_this_fresh_baseline=True,baseline_reuse=False,
                     original_published_wrapper_pass_claimed=False,
                     baseline_result_sha256=sha(baseline/'RESULT.json'),
                     candidate_result_sha256=sha(candidate/'RESULT.json'),
                     release_receipt_sha256=sha(candidate/'release/RELEASE-RECEIPT.json'),
                     release_manifest_sha256=release['manifest_sha256'],native_receipt_sha256=native_hash,
                     finite_adapter_result_sha256=sha(work/'portable-finite/RESULT.json'),
                     recovery_receipt_sha256=sha(work/'RECOVERY.json'),runner_sha256=runner_pins,stages=stages,
                     scope='Unchanged T185 construction; precision-only exact conditional multiplication exponent refinement. Baseline cold native/finite/outer release and derivative complete admission passed. Two missing immutable files recovered separately; regenerated gzip compared by exact payload in the finite adapter. All inherited asymptotic assumptions remain; no new circuit, unconditional theorem, formal full-theorem proof, measured runtime gain or maintainer acceptance is claimed.')
        write(work/'RESULT.json',receipt)
        print(receipt['status'],receipt['kappa_decimal'],flush=True)
    except BaseException as error:
        write(work/'FAILURE.json',dict(status='FAIL_REPLAY_NOT_CERTIFIED',stage=active,
                                      exception_type=type(error).__name__,message=str(error),
                                      traceback=traceback.format_exc(),stages=stages,
                                      runner_sha256=runner_pins,started_utc=started))
        raise


if __name__=='__main__':
    main()
