#!/usr/bin/env python3
"""Cold Git-free replay and actual source/receipt corruption controls.

@CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is transport/failure-detection evidence, not a third mathematical engine.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def demand(value, label):
    if not value:
        raise ValueError(label)


def main():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    inputs = [row['path'] for row in manifest['files'] if row['usage'] == 'input']
    with tempfile.TemporaryDirectory(prefix='dyadic-omega-cold-') as folder:
        root = Path(folder)
        package = root / 'research' / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for path in inputs:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / path).read_bytes())
        demand(not (root / '.git').exists(), 'Git-free tree')

        def run(script, expected=None):
            result = subprocess.run([sys.executable, '-I', '-B', '-O', '-W', 'error',
                                     str(package / script)], cwd=root, capture_output=True,
                                    text=True, timeout=180, check=False)
            if expected is not None:
                demand(result.returncode == 0, script + ': ' + result.stderr)
                data = json.loads(result.stdout)
                demand(data['status'] == expected, script + ': wrong status')
                return data
            return result

        primary = run('verify.py', 'PASS_DYADIC_OMEGA_COUNTEREXAMPLE')
        forward = run('forward_check.py', 'PASS_FORWARD_OMEGA_COUNTEREXAMPLE')
        rejected_sources = []
        for path in inputs:
            target = root / path
            original = target.read_bytes()
            try:
                target.write_bytes(original + b'\n# deliberate source corruption\n')
                result = run('verify.py')
                demand(result.returncode != 0 and 'input SHA256: ' + path in result.stderr,
                       'corrupt source was not rejected: ' + path)
                rejected_sources.append(path)
            finally:
                target.write_bytes(original)
        receipt = package / 'WITNESS.json'
        original = receipt.read_bytes()
        try:
            data = json.loads(original)
            data['new']['total_mass'] -= 1
            receipt.write_text(json.dumps(data))
            result = run('verify.py')
            demand(result.returncode != 0 and 'exact typed receipt mismatch' in result.stderr,
                   'actual corrupted witness was not rejected')
        finally:
            receipt.write_bytes(original)
        print(json.dumps({'status': 'PASS_COLD_OPTIMIZED_AND_TAMPER_CONTROLS',
                          'git_free': True, 'python_optimized': True,
                          'primary_status': primary['status'], 'forward_status': forward['status'],
                          'rejected_source_corruptions': rejected_sources,
                          'rejected_witness_corruptions': 1}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
