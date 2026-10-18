"""Actual relocated replay and on-disk receipt/source corruption controls."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def run(root, expected):
    p = subprocess.run([sys.executable, '-I', '-O', '-B', str(root/REL/'verify.py')],
                       cwd=root, capture_output=True, text=True, timeout=60)
    if (p.returncode == 0) != expected:
        raise ValueError('unexpected replay status: '+p.stdout+p.stderr)
    return p.stdout+p.stderr


def main():
    with tempfile.TemporaryDirectory(prefix='bit-packet-staging-') as temporary:
        root = Path(temporary).resolve()
        dest = root/REL
        shutil.copytree(HERE, dest, ignore=shutil.ignore_patterns('__pycache__'))
        sources = json.loads((HERE/'SOURCES.json').read_text())
        for row in sources['files']:
            if row['usage'] == 'input':
                target = root/row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT/row['path'], target)
        before = {p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
        run(root, True)
        after = {p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
        if before != after:
            raise ValueError('default replay writes evidence')
        receipt = dest/'RESULT.json'
        original = receipt.read_bytes()
        value = json.loads(original)
        value['selected']['route_actions_per_call'] -= 1
        receipt.write_text(json.dumps(value))
        if 'committed receipt mismatch' not in run(root, False):
            raise ValueError('receipt control did not reach intended check')
        receipt.write_bytes(original)
        source = root/next(row['path'] for row in sources['files'] if row['usage']=='input')
        source.write_bytes(source.read_bytes()+b'\n')
        if 'source pin' not in run(root, False):
            raise ValueError('source control did not reach intended check')
    print('PASS_BIT_PACKET_STAGING_PACKAGE relocated_read_only=1 on_disk_controls=2')


if __name__ == '__main__':
    main()
