"""Relocated replay, pre-import source binding and typed full-receipt controls."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise ValueError(why)

def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

def replay(script, reason=None, extra=()):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(script), *extra],
                            capture_output=True, text=True, timeout=600)
    if reason is None:
        need(result.returncode == 0 and 'PASS_NATIVE_OWNER_OBSERVATION_DIMENSION' in result.stdout,
             result.stdout + result.stderr)
    else:
        need(result.returncode != 0 and reason in result.stderr,
             'wrong rejection: ' + result.stdout + result.stderr)

def main():
    with tempfile.TemporaryDirectory(prefix='native-owner-dimension-') as folder:
        root = Path(folder)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package)
        for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']:
            if row.get('usage') == 'input':
                target = root / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], target)
        before = snapshot(root)
        script = package / 'verify.py'
        replay(script)
        need(snapshot(root) == before, 'export replay modified inputs')
        for path in (package / 'source/pr2048/verify.py',
                     root / 'research/frontier1094-recipes-exact-seed76/clifford.py'):
            data = path.read_bytes()
            path.write_bytes(b'raise RuntimeError("MUST_NOT_EXECUTE")\n' + data)
            replay(script, 'source SHA256')
            path.write_bytes(data)
        receipt = package / 'RESULT.json'
        data = receipt.read_bytes()
        replay(script, 'FileExistsError', ('--write', str(receipt)))
        receipt.unlink()
        replay(script, 'FileNotFoundError')
        wrong = json.loads(data)
        wrong['native_port_factors'][111]['normal'] = True
        receipt.write_text(json.dumps(wrong), encoding='utf-8')
        replay(script, 'complete receipt mismatch')
        receipt.write_bytes(data)
        need(snapshot(root) == before, 'controls left export changed')
    print('PASS_NATIVE_OWNER_DIMENSION_INTEGRITY gitfree=1 source_faults=2 receipt_controls=3')

if __name__ == '__main__':
    main()
