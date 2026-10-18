"""Run the public CLI from a Git-free export and exercise integrity failures."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok: raise ValueError(message)


def digest(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='paired-block-export-') as tmp:
        root = Path(tmp)
        package = root/'research'/HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
            if row['usage'] != 'input': continue
            target = root/row['path']; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/row['path'], target)
        unrelated = root/'unrelated'; unrelated.mkdir()
        def run(extra=()):
            return subprocess.run([sys.executable, '-I', '-O', '-B', str(package/'verify.py'), *extra],
                                  cwd=unrelated, capture_output=True, text=True, timeout=120)
        before = digest(root)
        result = run()
        need(result.returncode == 0 and 'PASS_PAIRED_PLANE_BLOCK_RANK' in result.stdout, 'relocated CLI '+result.stderr)
        need(digest(root) == before, 'default replay must not write')
        source = package/'predecessor/PR2484-CERTIFICATE.json'
        original = source.read_bytes(); source.write_bytes(original+b' ')
        result = run()
        need(result.returncode != 0 and 'source SHA256 predecessor/PR2484-CERTIFICATE.json' in result.stderr, 'source corruption rejected before interpretation')
        source.write_bytes(original)
        receipt = package/'RESULT.json'; original = receipt.read_bytes()
        value = json.loads(original); value['ports'] = '112'
        receipt.write_text(json.dumps(value), encoding='utf-8')
        result = run()
        need(result.returncode != 0 and 'complete typed receipt mismatch' in result.stderr, 'typed receipt corruption')
        receipt.write_bytes(original)
        result = run(['--write', str(receipt)])
        need(result.returncode != 0 and 'FileExistsError' in result.stderr and receipt.read_bytes() == original,
             'exclusive output leaves existing receipt intact')
        need(digest(root) == before, 'integrity tests restore export')
    print('PASS_BLOCK_RANK_INTEGRITY relocated_readonly source_pin typed_receipt exclusive_output')


if __name__ == '__main__': main()
