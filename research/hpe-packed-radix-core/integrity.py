"""Actual exported-source and typed-receipt corruption controls; Apache-2.0."""
import importlib.util,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REL=HERE.relative_to(ROOT)


def require(ok,msg):
    if not ok:raise ValueError(msg)


def main():
    with tempfile.TemporaryDirectory(prefix='packed-radix-export-') as folder:
        root=Path(folder);p=root/REL
        shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__','*.olean'))
        for item in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            if item['usage']=='input':
                dst=root/item['path'];dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/item['path'],dst)
        def invoke(expected=None,auth=False):
            argv=[sys.executable,'-I','-O','-B',str(p/'verify.py')]+(['--authenticate-only'] if auth else [])
            result=subprocess.run(argv,cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=180)
            if expected is None:require(result.returncode==0,result.stdout+result.stderr)
            else:require(result.returncode!=0 and expected in result.stderr,'unexpected rejection '+result.stdout+result.stderr)
        invoke()
        targets=[(root/'research/hpe-unitary-packed-radix/verify.py','changed source:'),
                 (p/'vendor/Energy.lean','changed vendor:'),
                 (p/'PackedRadix.lean','changed formal source')]
        for path,reason in targets:
            original=path.read_bytes();path.write_bytes(b'UNREVIEWED SOURCE\n'+original)
            try:invoke(reason,auth=True)
            finally:path.write_bytes(original)
        spec=importlib.util.spec_from_file_location('exported_receipt_checker',p/'verify.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        original=json.loads((p/'RESULT.json').read_text(encoding='utf-8'))
        changed=json.loads(json.dumps(original));changed['pairs'][0]['left_scale']=True
        require(changed==original,'control must distinguish JSON types beyond Python equality')
        (p/'RESULT.json').write_text(json.dumps(changed),encoding='utf-8')
        try:module.check_receipt(original)
        except ValueError as exc:require('typed receipt mismatch' in str(exc),'wrong receipt rejection')
        else:raise ValueError('typed receipt corruption accepted')
    print('PASS_PACKED_RADIX_GIT_FREE_REPLAY_AND_4_CORRUPTION_CONTROLS')


if __name__=='__main__':main()
