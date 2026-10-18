"""Git-free replay, source authentication and complete receipt controls."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise ValueError(why)

def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

def run(path, reject=None, extra=()):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(path), *extra],
                            capture_output=True, text=True, timeout=600)
    if reject is None:
        need(result.returncode == 0, result.stdout + result.stderr)
    else:
        need(result.returncode != 0 and reject in result.stderr,
             'wrong rejection: ' + result.stdout + result.stderr)

def main():
    with tempfile.TemporaryDirectory(prefix='selected-invocation-frame-') as folder:
        root = Path(folder)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package)
        for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
            if row.get('usage') == 'input':
                target = root / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], target)
        before = hashes(root)
        run(package / 'verify.py')
        need(hashes(root) == before, 'export replay wrote files')
        for target in (package / 'vendor/pipeline.py',
                       root / 'research/community-frontier1094-audit/selected-replay.tar.gz'):
            data = target.read_bytes()
            target.write_bytes(data + b'\nraise RuntimeError("MUST NOT EXECUTE")\n')
            run(package / 'verify.py', 'source SHA256')
            target.write_bytes(data)
        receipt = package / 'RESULT.json'
        data = receipt.read_bytes()
        run(package / 'verify.py', 'FileExistsError', ('--write', str(receipt)))
        receipt.unlink()
        run(package / 'verify.py', 'FileNotFoundError')
        receipt.write_bytes(data)
        wrong = json.loads(data)
        wrong['all_local_bills'][0]['wrapper']['moves'] = True
        receipt.write_text(json.dumps(wrong), encoding='utf-8')
        run(package / 'verify.py', 'complete receipt mismatch')
        receipt.write_bytes(data)
        need(hashes(root) == before, 'controls left altered export')
    print('PASS_INVOCATION_FRAME_INTEGRITY gitfree=1 source_faults=2 receipt_controls=3')

if __name__ == '__main__':
    main()
