"""Focused Git-free/source/receipt controls for the new certificate."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def run(path, extra=(), rejected=None):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(path), *extra],
                            capture_output=True, text=True, timeout=180)
    if rejected is None:
        need(result.returncode == 0, result.stdout + result.stderr)
    else:
        need(result.returncode != 0 and rejected in result.stderr,
             'wrong integrity rejection: ' + result.stdout + result.stderr)


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='qq16-sixteen-cut-') as directory:
        export = Path(directory).resolve()
        package = export / 'research' / HERE.name
        shutil.copytree(HERE, package)
        for row in manifest['files']:
            if row['usage'] == 'input':
                dest = export / row['path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], dest)
        before = hashes(export)
        run(package / 'verify.py')
        run(package / 'independent.py')
        need(hashes(export) == before, 'Git-free export changed')
        for target in (package / 'vendor/operator_audit.py', export / 'research/joint-query/certificate.json.gz'):
            original = target.read_bytes()
            target.write_bytes(original + b'\nraise RuntimeError("SHOULD NOT EXECUTE")\n')
            run(package / 'verify.py', rejected='source SHA256')
            target.write_bytes(original)
        receipt = package / 'RESULT.json'
        original = receipt.read_bytes()
        row = json.loads(original)
        row['retained_early_arrays'] = True  # type-sensitive, never equality of bool and integer
        receipt.write_text(json.dumps(row), encoding='utf-8')
        run(package / 'verify.py', rejected='complete committed receipt mismatch')
        receipt.write_bytes(original)
        run(package / 'verify.py', ('--write-result',), rejected='FileExistsError')
        need(receipt.read_bytes() == original, 'overwrite refusal changed frozen receipt')
        receipt.unlink()
        run(package / 'verify.py', rejected='FileNotFoundError')
        receipt.write_bytes(original)
        need(hashes(export) == before, 'integrity controls left altered export')
    print('PASS_QQ16_SIXTEEN_RECORD_INTEGRITY gitfree=1 source_faults=2 receipt_faults=3')


if __name__ == '__main__':
    main()
