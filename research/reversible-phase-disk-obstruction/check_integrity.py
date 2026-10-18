"""Git-free optimized public replay and controlled source/receipt corruptions."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import authenticate, need


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    authenticate()
    temp_base = Path(tempfile.gettempdir()).resolve()
    with tempfile.TemporaryDirectory(prefix='phase-boundary-', dir=temp_base) as temp:
        root = Path(temp).resolve()
        need(root.is_relative_to(temp_base) and root != temp_base, 'bounded temporary export')
        exported = root / 'export'
        p = exported / 'research' / HERE.name
        shutil.copytree(HERE, p, ignore=shutil.ignore_patterns('__pycache__'))
        for record in json.loads((HERE / 'SOURCES.json').read_text())['files']:
            if record['usage'] == 'input':
                target = exported / record['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE.parents[1] / record['path'], target)
        elsewhere = root / 'elsewhere'
        elsewhere.mkdir()
        def run(*args):
            return subprocess.run([sys.executable, '-I', '-O', '-B', str(p/'verify.py'), *args],
                                  cwd=elsewhere, capture_output=True, text=True, timeout=60)
        def failed(result, text):
            need(result.returncode != 0 and text in result.stderr,
                 'expected rejection ' + text + ': ' + result.stdout + result.stderr)
        before = inventory(root)
        result = run()
        need(result.returncode == 0 and 'PASS_REVERSIBLE_PHASE_DISK_BOUNDARY' in result.stdout,
             'relocated optimized replay: ' + result.stderr)
        need(inventory(root) == before, 'read-only default replay')
        receipt = p / 'RESULT.json'
        raw = receipt.read_bytes()
        for value in (True, 17119):
            data = json.loads(raw)
            data['source_disk_inputs'] = value
            receipt.write_text(json.dumps(data), encoding='utf-8')
            failed(run(), 'receipt type mismatch' if type(value) is bool else 'receipt value mismatch')
        receipt.write_bytes(raw)
        failed(run('--output', str(receipt)), 'FileExistsError')
        need(receipt.read_bytes() == raw, 'exclusive output preserves receipt')
        failed(run('--unknown'), 'unknown arguments')
        for name in ('phase_kernel.py', 'intervals.py'):
            source = p / 'predecessor' / name
            source_raw = source.read_bytes()
            source.write_bytes(source_raw + b'\nraise RuntimeError("UNAUTH_EXECUTED")\n')
            result = run()
            failed(result, 'source SHA:')
            need('UNAUTH_EXECUTED' not in result.stderr, 'authentication before executable source')
            source.write_bytes(source_raw)
        source = exported / 'certificates/selected-result.json'
        source_raw = source.read_bytes()
        source.write_bytes(source_raw + b'\n')
        failed(run(), 'source SHA:')
        source.write_bytes(source_raw)
        pins = p / 'VENDOR.json'
        pins_raw = pins.read_bytes()
        data = json.loads(pins_raw)
        data['files'][0]['git_blob'] = '0'*40
        pins.write_text(json.dumps(data), encoding='utf-8')
        failed(run(), 'source blob:')
        pins.write_bytes(pins_raw)
        need(inventory(root) == before, 'export restored after controls')
    print('PASS_PHASE_BOUNDARY_INTEGRITY read_only_export=1 corruption_cli_controls=8')


if __name__ == '__main__':
    main()
