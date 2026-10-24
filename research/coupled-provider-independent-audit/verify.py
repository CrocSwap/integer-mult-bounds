#!/usr/bin/env python3
"""Authenticated serial independent replay with outputs outside the frozen package."""
import sys
if not sys.flags.isolated:
    import posix
    posix.execv(sys.executable,[sys.executable,'-I',*(['-O']*sys.flags.optimize),'-B',sys.argv[0],*sys.argv[1:]])
import argparse,hashlib,json,os,shutil,subprocess,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
_bootcache=tempfile.TemporaryDirectory(prefix='provider-audit-bootstrap-')
sys.pycache_prefix=_bootcache.name
HERE=Path(__file__).absolute().parent
BOOTSTRAP={'source_guard.py': 'd91d376d0ff60a3d893cf355f351a28ec0dc7bb028a2f70353596346317ca893', 'receipt_guard.py': '4550a708cadb89d1d385984cf604717276bdafbe30ca1065d0f80db65b283b6b', 'engine_adapter.py': 'f50f67691fd9e59759241f02fa5a7a310a9e31c323093455613528d130434352'}
MANIFEST_SHA256='892ca8c2ce8570920c16369b750197b5b1196dc79c592c967d9dbd13dd2869d3'
COMMANDS_SHA256='524ccee9da1eb3334c255f9df76a3c84beb989e8e935c4d6da2d525541726f65'
def need(ok,message):
    if not ok:raise ValueError(message)
for part in [HERE,*HERE.parents]:need(not part.is_symlink(),'Symlink package ancestor')
for name,digest in [('SOURCE-BINDINGS.json',MANIFEST_SHA256),('COMMANDS.json',COMMANDS_SHA256),*BOOTSTRAP.items()]:
    path=HERE/name
    need(not path.is_symlink() and path.is_file() and path.stat().st_nlink==1,'Missing or aliased bootstrap: '+name)
    need(hashlib.sha256(path.read_bytes()).hexdigest()==digest,'Changed trusted bootstrap: '+name)
helpers={}
for name in ['source_guard.py','receipt_guard.py']:
    raw=(HERE/name).read_bytes();space={'__name__':'_authenticated_'+name[:-3],'__file__':str(HERE/name)}
    exec(compile(raw,str(HERE/name),'exec',dont_inherit=True,optimize=0),space);helpers[name]=space
check=helpers['source_guard.py']['check'];validate=helpers['receipt_guard.py']['validate']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bindings-only',action='store_true');ap.add_argument('--output',type=Path);args=ap.parse_args()
    before=check(HERE)
    if args.bindings_only:
        print(json.dumps({'status':before['status'],'files':before['files'],'custody':before['custody']}));return
    root=Path(tempfile.mkdtemp(prefix='coupled-provider-replay-'));root.chmod(0o700)
    destination=(args.output or root/'REPLAY.json').absolute()
    for part in [destination,*destination.parents]:need(not part.is_symlink(),'Symlink output component')
    need(not destination.exists(),'Immutable receipt output exists')
    need(not destination.resolve().is_relative_to(HERE.resolve()),'Output must stay outside frozen package')
    commands=json.loads((HERE/'COMMANDS.json').read_bytes())['commands']
    need([x['name'] for x in commands]==['algebra','same-chart-control','budget','local-envelope','clifford-proof'],'Unexpected scientific schedule')
    report={'status':'RUNNING','wrapper_optimization':sys.flags.optimize,'scientific_compile_optimization':0,'python':sys.version,'bindings':before,'runs':[],'scratch':str(root)}
    try:
        shutil.copytree(HERE/'capsule',root,dirs_exist_ok=True)
        root.chmod(0o700)
        for path in root.rglob('*'):
            if path.is_dir():path.chmod(0o700)
        for row in json.loads((HERE/'SOURCE-BINDINGS.json').read_bytes())['files']:
            if row['path'].startswith('capsule/'):
                target=root/row['path'][8:]
                need(hashlib.sha256(target.read_bytes()).hexdigest()==row['sha256'],'Scratch copy changed')
        for index,command in enumerate(commands):
            cache=root/f'cache-{index}';cache.mkdir(mode=0o700)
            env=os.environ.copy()
            for key in ['PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','PYTHONSTARTUP','PYTHONINSPECT']:env.pop(key,None)
            env['PYTHONDONTWRITEBYTECODE']='1'
            argv=[sys.executable,'-I',*(['-O']*sys.flags.optimize),'-B','-X','pycache_prefix='+str(cache),str(HERE/'engine_adapter.py'),str(root),command['engine'],*command['argv']]
            started=time.monotonic()
            run=subprocess.run(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=command['timeout_seconds'])
            (root/f'run-{index}.stdout').write_bytes(run.stdout);(root/f'run-{index}.stderr').write_bytes(run.stderr)
            report['runs'].append({'name':command['name'],'argv':argv,'returncode':run.returncode,'seconds':time.monotonic()-started,'stdout_sha256':hashlib.sha256(run.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(run.stderr).hexdigest()})
            need(run.returncode==0,'Scientific replay failed: '+command['name']+'; see '+str(root/f'run-{index}.stderr'))
        report['fresh_scientific_summary']=validate(HERE,root,commands)
        need(check(HERE)==before,'Frozen package changed during replay')
        report['status']='PASS_INDEPENDENT_PARTIAL_PROVIDER_AND_CONDITIONAL_BUDGET'
        report['limits']=['Eight coupled outputs earn zero autonomous credit.','144 extra H8 targets are hypothetical; 144 paid H8 cancels them rankwise.','Companion all-n criterion is written proof review; executable oracle is bounded.','Frozen author normal/-O pair is authenticated reuse, never rerun here.','No completed caller, new kappa, full #5376 provider/fusion replay or selected promotion.']
    except BaseException as error:
        report['status']='FAIL';report['error']=repr(error);raise
    finally:
        destination.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w',dir=destination.parent,prefix='.provider-receipt-',delete=False) as out:
            out.write(json.dumps(report,indent=2,sort_keys=True)+'\n');temporary=Path(out.name)
        os.replace(temporary,destination)
        print(json.dumps({'status':report['status'],'receipt':str(destination),'scratch':str(root)}))
if __name__=='__main__':main()
