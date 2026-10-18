"""Git-free source export, read-only replay and meaningful rejection controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def tree(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    controls=0
    with tempfile.TemporaryDirectory(prefix='compact-repair-export-') as tmp:
        root=Path(tmp).resolve()
        pkg=root/'research'/HERE.name
        shutil.copytree(HERE,pkg)
        for item in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            if item.get('usage')=='input':
                out=root/item['path'];out.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/item['path'],out)
        def run(extra=(),expect='PASS_COMPACT_GUARDED_REPAIR'):
            result=subprocess.run([sys.executable,'-I','-O','-B',str(pkg/'verify.py'),*extra],cwd=root,capture_output=True,text=True,timeout=180)
            if expect.startswith('PASS_'):
                need(result.returncode==0 and expect in result.stdout,'export failed: '+result.stdout+result.stderr)
            else:
                need(result.returncode!=0 and expect in result.stdout+result.stderr,'control did not reject: '+result.stdout+result.stderr)
        before=tree(root)
        run();need(tree(root)==before,'read-only replay changed export')
        run(['--write'],'refuse receipt overwrite');controls+=1
        run(['--unknown'],'unrecognized arguments');controls+=1
        for file in ('vendor/pr2250/compact.py','vendor/pr2250/streams.py'):
            path=pkg/file;original=path.read_bytes()
            path.write_bytes(original+b'\nraise RuntimeError("UNAUTHENTICATED_EXECUTION")\n')
            run(expect='source hash:');path.write_bytes(original);controls+=1
        path=pkg/'Repair.lean';original=path.read_bytes();path.write_bytes(original+b'\n-- mutation\n')
        run(expect='formal source receipt mismatch');path.write_bytes(original);controls+=1
        path=pkg/'KERNEL.json';original=path.read_bytes();data=json.loads(original);data['axioms']['CompactRepair.fill_correct'].append('sorryAx')
        path.write_text(json.dumps(data),encoding='utf-8');run(expect='formal receipt toolchain/axioms');path.write_bytes(original);controls+=1
        path=pkg/'RESULT.json';original=path.read_bytes();data=json.loads(original);data['kernel_checked_by_this_command']=0
        path.write_text(json.dumps(data),encoding='utf-8');run(expect='receipt mismatch');path.write_bytes(original);controls+=1
        need(tree(root)==before,'mutation restoration failed')
    print('PASS_COMPACT_REPAIR_INTEGRITY git_free=1 controls='+str(controls))


if __name__=='__main__':main()
