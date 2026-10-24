"""Fresh Lean kernel/axiom check of the three scoped owner identities.
intqwq; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
AUDITOR='research/kappa-lean-verification-20261022/verify_lean.py'


def auditor():
    helper=HERE/'sources'/AUDITOR
    if sha256(helper.read_bytes()).hexdigest()!='6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895':
        raise ValueError('Pinned copied Lean auditor')
    spec=importlib.util.spec_from_file_location('owner_protocol_lean_audit',helper)
    audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    return audit,helper


def check_receipt():
    """Source/log/axiom coherence without a compiler or a compiled object."""
    audit,helper=auditor();r=json.loads((HERE/'LEAN.json').read_bytes())
    source=HERE/r['source'];log=HERE/r['log']
    expected=audit.audit_source(source);reports=audit.parse_axioms(log,expected)
    manifest=json.loads((HERE/'sources/research/kappa-lean-verification-20261022/lake-manifest.json').read_bytes())
    pinned_dependencies=sorted((p['name'],p['rev']) for p in manifest['packages'])
    checks=[r['exit_code']==0,len(expected)==3,r['expected_reports']==expected,r['axioms']==reports,
            r['source_sha256']==sha256(source.read_bytes()).hexdigest(),
            r['log_sha256']==sha256(log.read_bytes()).hexdigest(),
            r['auditor_sha256']==sha256(helper.read_bytes()).hexdigest(),
            r['script_sha256']==sha256(Path(__file__).read_bytes()).hexdigest(),
            set(r['allowed_axioms'])==audit.ALLOW,r['runtime']['mathlib_revision']==audit.MATHLIB,
            sorted((p['name'],p['revision']) for p in r['runtime']['dependencies'])==pinned_dependencies,
            r['runtime']['lean_executable_sha256']=='fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab']
    if not all(checks):raise ValueError('Lean source/log/runtime receipt coherence')
    obj=HERE/'OwnerProtocol.olean'
    if obj.exists() and sha256(obj.read_bytes()).hexdigest()!=r['object_sha256']:
        raise ValueError('Present local object does not match the fresh compilation receipt')
    return r


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--receipt-only',action='store_true')
    parser.add_argument('--runtime',type=Path,default=ROOT/'research/kappa-lean-verification-20261022')
    parser.add_argument('--lake',type=Path)
    args=parser.parse_args()
    if args.receipt_only:
        r=check_receipt();print('PASS_LEAN_SOURCE_LOG_RECEIPT_ONLY',len(r['axioms']),'reports; no fresh compilation');return
    runtime=args.runtime.resolve();audit,helper=auditor()
    if not (runtime/'lakefile.toml').is_file():
        raise ValueError('Fresh compilation requires --runtime PATH with the pinned copied Lake setup and installed toolchain; use --receipt-only for source/log replay.')
    audit.HERE=runtime
    old_capture=audit.capture
    def capture(argv,**kwargs):
        kwargs.setdefault('cwd',runtime);return old_capture(argv,**kwargs)
    audit.capture=capture
    lake=args.lake or runtime/'.toolchain/lean-4.21.0-windows/bin/lake.exe'
    lean,env,versions=audit.environment(str(lake))
    if sha256(Path(lean).read_bytes()).hexdigest()!='fb7a62288f197279fb84e55bb1972348fd2cce1d550845793975f1cebb0c24ab':raise ValueError('Pinned Lean executable')
    paths=[str(Path(p) if Path(p).is_absolute() else (runtime/p).resolve()) for p in env['LEAN_PATH'].split(os.pathsep) if p]
    env['LEAN_PATH']=os.pathsep.join([str(HERE),*paths])
    source=HERE/'OwnerProtocol.lean';before=sha256(source.read_bytes()).hexdigest()
    expected=audit.audit_source(source)
    if len(expected)!=3:raise ValueError('Exactly three scoped axiom reports')
    obj=HERE/'OwnerProtocol.olean';log=HERE/'OwnerProtocol.log'
    with log.open('wb') as out:
        done=subprocess.run([lean,'--root='+str(HERE),'-o',str(obj),str(source)],cwd=HERE,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=120)
    if done.returncode:raise ValueError(log.read_text(encoding='utf-8'))
    if sha256(source.read_bytes()).hexdigest()!=before:raise ValueError('Source changed during Lean compilation')
    reports=audit.parse_axioms(log,expected)
    receipt=dict(status='PASS_LEAN_SCOPED_OWNER_IDENTITIES',source=source.name,source_sha256=before,
                 object_sha256=sha256(obj.read_bytes()).hexdigest(),log=log.name,log_sha256=sha256(log.read_bytes()).hexdigest(),
                 exit_code=done.returncode,axioms=reports,expected_reports=expected,allowed_axioms=sorted(audit.ALLOW),
                 output=log.read_text(encoding='utf-8'),runtime=versions,auditor_sha256=sha256(helper.read_bytes()).hexdigest(),
                 script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),new_kappa=False,
                 environment_provenance=dict(python_executable=sys.executable,python_version=sys.version),
                 scope='Generic arbitrary-input dirty return and order-three completion conditional on CB14I. Concrete data/native phases and resource limits are separately checked in Python; no recursive supplier admission.')
    (HERE/'LEAN.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(receipt['status'],len(reports),'reports')


if __name__=='__main__':main()
