#!/usr/bin/env python3
"""Exercise rejection of damaged finite-dependency evidence through the real CLI."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run():
    cases = ('missing_engine', 'wrong_finite_result', 'changed_output',
             'changed_source', 'changed_adapter', 'wrong_r4_arguments', 'false_primary_status')
    inputs = json.loads((HERE / 'VERIFY.json').read_text())['inputs']
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='s4-dependency-control-') as directory:
            root = Path(directory)
            package = root / 'research' / HERE.name
            shutil.copytree(HERE, package)
            for name in inputs:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, path)
            receipt_path = package / 'finite/REPLAY.json'
            receipt = json.loads(receipt_path.read_text())
            if case == 'false_primary_status':
                path = package / 'finite/PRIMARY_STOP.json'
                value = json.loads(path.read_text())
                value['status'] = 'PASS'
                path.write_text(json.dumps(value))
            elif case == 'missing_engine':
                receipt['records'].pop()
            elif case == 'wrong_finite_result':
                receipt['records'][0]['result'] += ' changed'
            elif case == 'wrong_r4_arguments':
                receipt['records'][0]['run_argv'][1] = '5'
            elif case == 'changed_output':
                path = package / 'finite/indep.stdout'
                path.write_bytes(path.read_bytes() + b'corruption\n')
            elif case == 'changed_source':
                path = root / 'research/s4-mixed-tuple-tight-word-search/search.cpp'
                path.write_bytes(path.read_bytes() + b'\n// changed\n')
            else:
                path = package / 'compat/bits/stdc++.h'
                path.write_bytes(path.read_bytes() + b'\n// changed\n')
            receipt_path.write_text(json.dumps(receipt))
            result = subprocess.run([sys.executable, '-I', '-O', '-B', str(package / 'verify.py')],
                                    cwd=root, text=True, capture_output=True, timeout=30)
            if result.returncode == 0 or 'ValueError:' not in result.stderr:
                raise ValueError('negative control failed: ' + case + result.stderr)
    print('PASS_S4_FINITE_DEPENDENCY_CONTROLS groups=7 optimized=true')


if __name__ == '__main__':
    run()
