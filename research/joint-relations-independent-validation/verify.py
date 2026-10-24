#!/usr/bin/env python3
"""Fresh serial independent replay; receipts stay outside the frozen package."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

# -B suppresses writes but does not suppress stale .pyc reads. Set before imports.
_CACHE=tempfile.TemporaryDirectory(prefix='joint-independent-pycache-')
sys.pycache_prefix=_CACHE.name
sys.dont_write_bytecode=True
# The master verifier is the externally commit/export-bound trust anchor.
# Authenticate both helpers as regular working files before any helper import.
_BOOTSTRAP={'source_guard.py': '9ef48a8b1fad7e391c8b585691d741c3c4642745aed36e00b5b65b0cf4cdac12', 'receipt_guard.py': '67336a39205247ca3ad1639e29f2dfcdc334f8e8f68cc173e87cd58f80d6adda'}
_bootstrap_here=Path(__file__).absolute().parent
for _name,_digest in _BOOTSTRAP.items():
    _path=_bootstrap_here/_name
    if _path.is_symlink() or not _path.is_file():
        raise ValueError('Missing or symlinked bootstrap helper: '+_name)
    if hashlib.sha256(_path.read_bytes()).hexdigest()!=_digest:
        raise ValueError('Changed bootstrap helper working bytes: '+_name)
from source_guard import check, require
from receipt_guard import validate

HERE=Path(__file__).resolve().parent
COMMANDS_SHA256='a1137cf53296d6b56db2a785a1e923e4b807e799e1de41a911353ed5e7aa0433'

def prepare_scratch(source,root):
    # copytree preserves source directory modes. Read-only exports must remain
    # read-only, but this new private execution tree owns its regenerated files.
    shutil.copytree(source,root,dirs_exist_ok=True)
    root.chmod(0o700)
    for path in root.rglob('*'):
        if path.is_dir():
            path.chmod(0o700)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bindings-only',action='store_true')
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    before=check(HERE)
    if args.bindings_only:
        print(json.dumps({'status':before['status'],'files':before['files']}));return
    claims=json.loads((HERE/'CLAIMS.json').read_bytes())
    require(claims['review_status']=='READY_FOR_COLD_REPLAY','Package scientific freeze is pending')
    root=Path(tempfile.mkdtemp(prefix='joint-independent-replay-'))
    destination=(args.output or root/'REPLAY.json').absolute()
    for component in [destination,*destination.parents]:
        require(not component.is_symlink(),'Symlink output component: '+str(component))
    require(not destination.exists() or destination.stat().st_nlink==1,'Hardlinked output file')
    destination=destination.resolve()
    require(not destination.is_relative_to(HERE.resolve()),'Receipt output must be outside frozen package')
    report={'status':'RUNNING','optimization':sys.flags.optimize,'source_bindings':before,'runs':[],'python':sys.version,'scratch':str(root)}
    try:
        prepare_scratch(HERE/'capsule',root)
        manifest=json.loads((HERE/'SOURCE-BINDINGS.json').read_bytes())
        for row in manifest['files']:
            if row['path'].startswith('capsule/'):
                target=root/row['path'].removeprefix('capsule/')
                require(hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256'],'Scratch copy differs from working input')
        command_bytes=(HERE/'COMMANDS.json').read_bytes()
        require(hashlib.sha256(command_bytes).hexdigest()==COMMANDS_SHA256,'Changed or truncated registered scientific command schedule')
        commands=json.loads(command_bytes)['commands']
        for i,command in enumerate(commands):
            cache=root/f'cache-{i}';cache.mkdir()
            env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None)
            env['PYTHONPYCACHEPREFIX']=str(cache);env['PYTHONDONTWRITEBYTECODE']='1'
            flags=['-O']*sys.flags.optimize
            argv=[sys.executable,*flags,'-B','-X','pycache_prefix='+str(cache),*command['argv']]
            started=time.monotonic()
            run=subprocess.run(argv,cwd=root,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=command['timeout_seconds'])
            (root/f'run-{i}.stdout').write_text(run.stdout)
            (root/f'run-{i}.stderr').write_text(run.stderr)
            report['runs'].append({'name':command['name'],'argv':argv,'returncode':run.returncode,'seconds':time.monotonic()-started,'stdout_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr.encode()).hexdigest()})
            require(run.returncode==0,'Scientific replay failed: '+command['name']+'; see '+str(root/f'run-{i}.stderr'))
        report['fresh_scientific_summary']=validate(root,claims,before)
        after=check(HERE);require(before==after,'Frozen working inputs changed during replay')
        report['status']='PASS_INDEPENDENT_TWO_LITERAL_WORDS_SAME_PREMISES'
        report['limits']=['Retains the five literal framework premises in CLAIMS.json.','Selected phase/BIT foundation is authenticated historical reuse, not fresh phase/BIT replay.','No unconditional theorem, selected promotion, human or formal-kernel acceptance.']
    except BaseException as error:
        report['status']='FAIL';report['error']=repr(error);raise
    finally:
        destination.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w',dir=destination.parent,prefix='.joint-receipt-',delete=False) as output:
            output.write(json.dumps(report,indent=2,sort_keys=True)+'\n'); temporary=Path(output.name)
        os.replace(temporary,destination)
        print(json.dumps({'status':report['status'],'receipt':str(destination),'scratch':str(root)}))

if __name__=='__main__':main()
