"""Git-free replay and actual source/receipt rejection through public entry points."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='integer-taylor-integrity-') as temp:
        root = Path(temp)
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            if row['usage'] == 'input':
                target = root/row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/row['path'], target)
        originals = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}

        def run(program, success, marker, *args):
            cp = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/program), *args],
                                cwd=root, capture_output=True, text=True, timeout=120)
            if (cp.returncode == 0) != success or marker not in cp.stdout+cp.stderr:
                raise ValueError(repr((cp.returncode, cp.stdout, cp.stderr)))
            if 'EXECUTED_CHANGED_SOURCE' in cp.stdout+cp.stderr:
                raise ValueError('changed source executed before rejection')

        run('verify.py', True, 'PASS_CEILING_INTEGER_TAYLOR')
        for name in ('ceiling.py', 'levers.py', 'verify.py'):
            path = root/'research/complex-local-word-ceiling'/name
            path.write_bytes(b'raise RuntimeError("EXECUTED_CHANGED_SOURCE")\n'+originals[path])
            run('adapter.py', False, 'source hash: research/complex-local-word-ceiling/'+name)
            path.write_bytes(originals[path])
        path = package/'RESULT.json'
        changed = json.loads(originals[path])
        changed['endpoint_checks'] += 1
        path.write_text(json.dumps(changed), encoding='utf-8')
        run('verify.py', False, 'typed complete receipt mismatch')
        path.write_bytes(originals[path])
        if any(p.read_bytes() != raw for p, raw in originals.items()):
            raise ValueError('source or receipt changed during read-only replay')
    print('PASS_INTEGER_TAYLOR_INTEGRITY git_free=1 source_rejections=3 receipt_rejections=1')


if __name__ == '__main__':
    main()
