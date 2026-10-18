#!/usr/bin/env python3
"""Relocation, read-only execution, and corruption controls.

Gareth Davidson (bitplane), with substantial OpenAI Codex assistance.
Apache-2.0. No assertions, external dependencies, or repository mutations.
"""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def snapshot(path):
    return {str(p.relative_to(path)): sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


def run(path, script, *args):
    return subprocess.run([sys.executable, '-I', '-O', '-B', str(path / script), *args],
                          cwd=path.parent, capture_output=True, text=True, timeout=120)


def main():
    original = snapshot(HERE)
    with tempfile.TemporaryDirectory(prefix='phase-closure-check-') as tmp:
        relocated = Path(tmp) / 'unrelated-name'
        shutil.copytree(HERE, relocated)
        before = snapshot(relocated)
        result = run(relocated, 'verify.py')
        require(result.returncode == 0, 'relocated exact replay failed: '+result.stderr[-2000:])
        require('fixtures=23' in result.stdout, 'relocated replay did not complete')
        require(snapshot(relocated) == before, 'ordinary replay wrote package files')

        receipt_path = relocated / 'RESULT.json'
        pristine = receipt_path.read_text()
        receipt = json.loads(pristine)
        receipt['fixtures']['C_3_typed']['invoice']['native_child_operand_cells'][0]['cells'] //= 2
        receipt_path.write_text(json.dumps(receipt))
        result = run(relocated, 'verify.py')
        require(result.returncode != 0 and 'receipt differs' in result.stderr,
                'primary replay accepted a corrupted operand-volume receipt')
        receipt_path.write_text(pristine)

        receipt = json.loads(pristine)
        program = receipt['fixtures']['C_3_typed']['program']
        receipt['fixtures']['C_3_typed']['program'] = [op for op in program if op[0] != 'translate']
        bad = Path(tmp) / 'wrong-return.json'
        bad.write_text(json.dumps(receipt))
        result = run(relocated, 'independent.py', '--receipt', str(bad), '--emit')
        require(result.returncode != 0 and 'independent spectral mismatch' in result.stderr,
                'independent replay accepted the omitted endpoint return')
        require(snapshot(relocated) == before, 'mutation checks left a modified relocated package')
    require(snapshot(HERE) == original, 'package tests modified their source')
    print('PASS_PHASE_PACKAGE_CONTROLS relocation read_only corrupted_volume omitted_return')


if __name__ == '__main__':
    main()
