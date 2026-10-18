#!/usr/bin/env python3
"""Exercise real source, receipt and export boundaries. Apache-2.0."""
import json
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


def main():
    workspace = ROOT.parent / 'contribution15-test-tmp'
    workspace.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='git-free-', dir=workspace) as tmp:
        export = Path(tmp)
        package = export / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
        for row in pins['files']:
            if row['usage'] == 'input':
                target = export / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row['path'], target)
        need(not (export / '.git').exists(), 'export must be Git-free')
        def run(*args):
            return subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py'), *args],
                                  cwd=export, text=True, encoding='utf-8', capture_output=True, timeout=180)
        original = {p.relative_to(package).as_posix(): p.read_bytes() for p in package.rglob('*') if p.is_file()}
        answer = run()
        need(answer.returncode == 0 and 'PASS_QQ16_ZERO_RETENTION_COMPARISON' in answer.stdout,
             'Git-free positive replay: ' + answer.stderr[-1500:])
        need(original == {p.relative_to(package).as_posix(): p.read_bytes() for p in package.rglob('*') if p.is_file()},
             'default replay wrote package files')
        source = export / 'research/joint-query/certificate.json.gz'
        saved = source.read_bytes()
        source.write_bytes(bytes([saved[0] ^ 1]) + saved[1:])
        answer = run()
        need(answer.returncode != 0 and 'source hash:' in answer.stderr, 'real source corruption not rejected before parsing')
        source.write_bytes(saved)
        receipt = package / 'RESULT.json'
        saved_receipt = receipt.read_bytes()
        result = json.loads(saved_receipt)
        need(result['two_sided_formal_inverse'] is True, 'positive typed receipt')
        result['two_sided_formal_inverse'] = 1
        receipt.write_text(json.dumps(result), encoding='utf-8')
        answer = run()
        need(answer.returncode != 0 and 'receipt mismatch: RESULT.json' in answer.stderr,
             'bool/int mutation not rejected')
        receipt.write_bytes(saved_receipt)
        answer = run('--write')
        need(answer.returncode != 0 and 'FileExistsError' in answer.stderr and receipt.read_bytes() == saved_receipt,
             'existing result overwritten')
    print('PASS_QQ16_ZERO_RETENTION_INTEGRITY groups=4 git_free read_only source_corruption typed_receipt overwrite_refusal')


if __name__ == '__main__':
    main()
