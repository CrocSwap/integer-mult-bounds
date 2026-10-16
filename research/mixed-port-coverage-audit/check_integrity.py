"""Git-free relocated replay and real source/receipt corruption rejection."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix='mixed-port-integrity-') as temporary:
        root = Path(temporary)
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
            if row['usage'] == 'input':
                dest = root/row['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/row['path'], dest)
        originals = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
        def run(success, marker):
            cp = subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py')],
                                cwd=root, capture_output=True, text=True, timeout=240)
            if (cp.returncode == 0) != success or marker not in cp.stdout+cp.stderr:
                raise ValueError(repr((cp.returncode, cp.stdout, cp.stderr)))
        run(True, 'PASS_MIXED_PORT_COVERAGE')
        candidate = package/'predecessor/CANDIDATE.json'
        candidate.write_bytes(originals[candidate]+b'\n')
        run(False, 'source hash: predecessor/CANDIDATE.json')
        candidate.write_bytes(originals[candidate])
        engine = root/'research/complex-local-word-ceiling/ceiling.py'
        engine.write_bytes(b'raise RuntimeError("EXECUTED_CORRUPTION")\n'+originals[engine])
        run(False, 'source hash: research/complex-local-word-ceiling/ceiling.py')
        engine.write_bytes(originals[engine])
        receipt = package/'RESULT.json'
        bad = json.loads(originals[receipt])
        bad['missing_paid_mass_per_call'] = '0'
        receipt.write_text(json.dumps(bad), encoding='utf-8')
        run(False, 'typed complete receipt mismatch')
        receipt.write_bytes(originals[receipt])
        if any(p.read_bytes() != value for p, value in originals.items()):
            raise ValueError('verification changed source or receipt bytes')
    print('PASS_MIXED_PORT_INTEGRITY git_free=1 source_rejections=2 receipt_rejections=1')


if __name__ == '__main__':
    main()
