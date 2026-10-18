#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise relocation, source drift and semantic corruptions under -I -O -B."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix='compact late read only ') as temporary:
        root = Path(temporary)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        inputs = [r['path'] for r in json.loads((HERE / 'SOURCES.json').read_text())['files']
                  if r['usage'] == 'input']
        for name in inputs:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        for p in root.rglob('*'):
            if p.is_file():
                p.chmod(0o444)
        command = [sys.executable, '-I', '-O', '-B', str(package / 'verify.py')]

        def run():
            return subprocess.run(command, cwd=temporary, capture_output=True, text=True, timeout=180)

        before = inventory(root)
        positive = run()
        need(positive.returncode == 0 and 'PASS_COMPACT_LATE_CARRY_GUARD' in positive.stdout,
             'Minimal relocated replay failed: ' + positive.stderr)
        need(inventory(root) == before, 'Normal replay wrote files')
        faults = 0

        def fault(path, replacement, marker):
            nonlocal faults
            original = path.read_bytes()
            path.chmod(0o644)
            path.write_bytes(replacement)
            path.chmod(0o444)
            try:
                result = run()
                need(result.returncode != 0 and marker in result.stderr,
                     'Corruption was not rejected for its intended reason: ' + str(path))
                faults += 1
            finally:
                path.chmod(0o644)
                path.write_bytes(original)
                path.chmod(0o444)

        for name in inputs:
            path = root / name
            fault(path, path.read_bytes() + b'\n', 'Source SHA256 drift: ' + name)
        verifier = package / 'verify.py'
        raw = verifier.read_bytes()
        for old, new, marker in [
                (b'(incoming and carry)', b'(False and carry)', 'incoming_carry guard separation'),
                (b'3 * B // 2 - 1', b'3 * B // 2 + 1', 'Digit transfer count'),
                (b't + self.pack(y ^ self.masks[z])', b't - self.pack(y ^ self.masks[z])', 'Literal inverse')]:
            need(raw.count(old) == 1, 'Mutation target must be unique')
            fault(verifier, raw.replace(old, new), marker)
        receipt = package / 'RESULT.json'
        changed = json.loads(receipt.read_text())
        changed['headline']['good_fraction'] = '1'
        fault(receipt, (json.dumps(changed) + '\n').encode(), 'Committed receipt drift')
        need(inventory(root) == before, 'Fault tests did not restore private fixtures')
    print(f'PASS_COMPACT_LATE_CARRY_PACKAGE read_only_relocated=PASS source_faults={len(inputs)} '
          f'algorithm_faults=3 receipt_faults=1 total_faults={faults}')


if __name__ == '__main__':
    main()
