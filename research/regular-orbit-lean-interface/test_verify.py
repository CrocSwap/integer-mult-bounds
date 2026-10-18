"""Git-free read-only export and source/typed receipt failure controls."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest_tree(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='regular-orbit-export-') as tmp:
        root = Path(tmp)/'checkout'
        pkg = root/'research'/HERE.name
        shutil.copytree(HERE,pkg,ignore=shutil.ignore_patterns('__pycache__','*.olean'))
        for name in ('research/bit-faithful-finite-address/README.md','certificates/selected-result.json'):
            target = root/name
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes())
        env = dict(os.environ)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        def run(*extra, expected=0, needle=None):
            result = subprocess.run([sys.executable,'-I','-O','-B',str(pkg/'verify.py'),*map(str,extra)],
                                    cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
            need((result.returncode == 0) == (expected == 0),result.stdout+result.stderr)
            if needle:
                need(needle in result.stdout+result.stderr,'wrong refusal: '+result.stdout+result.stderr)
        before = digest_tree(root)
        run(needle='PASS_EXTERNAL_REGULAR_ORBIT_CONFORMANCE')
        need(before == digest_tree(root),'export verifier changed files')
        for name, needle in (('source/pr2599/verify.py','source binding'),('RegularOrbit.lean','formal artifact binding')):
            path = pkg/name
            raw = path.read_bytes()
            path.write_bytes(raw+b'\n')
            run(expected=1,needle=needle)
            path.write_bytes(raw)
        receipt = pkg/'RESULT.json'
        original = receipt.read_bytes()
        changed = json.loads(original)
        changed['matrix_count'] = 168.0
        receipt.write_text(json.dumps(changed),encoding='utf-8')
        run(expected=1,needle='typed exact receipt mismatch')
        receipt.write_bytes(original)
        receipt.write_text('{"schema_version":1,"schema_version":1}',encoding='utf-8')
        run(expected=1,needle='duplicate JSON key')
        receipt.write_bytes(original)
        new = Path(tmp)/'new-result.json'
        run('--write-result',new)
        need(json.loads(new.read_text(encoding='utf-8')) == json.loads(original),'regeneration mismatch')
        new_bytes = new.read_bytes()
        run('--write-result',new,expected=1,needle='output already exists')
        need(new.read_bytes() == new_bytes,'existing output changed')
        need(before == digest_tree(root),'final export changed')
    print('PASS_REGULAR_ORBIT_EXPORT_CONTROLS groups=4 no_Lean_compilation=True')


if __name__ == '__main__':
    main()
