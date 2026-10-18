"""Relocated source-export replay and effective source/CLI corruptions."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

P=Path(__file__).resolve().parent
ROOT=P.parents[1]


def need(ok,message):
    if not ok:
        raise ValueError(message)


def digest_tree(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def run():
    controls=[]
    with tempfile.TemporaryDirectory(prefix='triadic-export-') as tmp:
        root=Path(tmp)
        package=root/'research'/P.name
        shutil.copytree(P,package)
        for item in json.loads((P/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            dst=root/item['path'];dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/item['path'],dst)
        before=digest_tree(root)
        def call(name='verify.py',args=(),success=True,contains=None):
            p=subprocess.run([sys.executable,'-I','-O','-B',str(package/name),*args],
                             cwd=root,text=True,encoding='utf-8',capture_output=True,timeout=180)
            need((p.returncode==0)==success, 'unexpected child status: '+p.stdout+p.stderr)
            if contains:
                need(contains in p.stdout+p.stderr,'missing diagnostic: '+p.stdout+p.stderr)
        call(contains='PASS_TRIADIC_NONUNIT_LOWERING')
        call('independent.py',contains='PASS_INDEPENDENT_NONUNIT_LOWERING')
        need(digest_tree(root)==before,'default execution mutated export')
        for path in [package/'vendor/program.py',package/'vendor/PROOF.md',
                     root/'research/dyadic-query-pair/program.py',root/'research/dyadic-query-pair/PROOF.md']:
            raw=path.read_bytes()
            path.write_bytes(raw+b'\n# unauthenticated alteration\n')
            call(success=False,contains='source hash:')
            path.write_bytes(raw)
            controls.append(str(path.relative_to(root)))
        path=package/'vendor/program.py'
        raw=path.read_bytes()
        # If unauthenticated executable code ran, this would create a marker.
        path.write_bytes(b"open('EXECUTED_BAD_SOURCE','w').write('bad')\n"+raw)
        call(success=False,contains='source hash:')
        need(not (root/'EXECUTED_BAD_SOURCE').exists(),'source executed before authentication')
        path.write_bytes(raw);controls.append('authenticate_before_exec')
        call(args=('--unknown',),success=False,contains='unrecognized arguments')
        controls.append('unknown_cli')
        call(args=('--write',),success=False,contains='refusing receipt overwrite')
        controls.append('exclusive_receipt')
        need(digest_tree(root)==before,'corruption restoration')
    print('PASS_TRIADIC_NONUNIT_INTEGRITY relocated=2 controls='+str(len(controls)))


if __name__=='__main__':
    run()
