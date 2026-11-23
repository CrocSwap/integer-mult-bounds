#!/usr/bin/env python3
"""Reject four independently altered bill fixtures without touching the inputs."""
from argparse import ArgumentParser
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ap = ArgumentParser()
ap.add_argument('--inputs', type=Path, required=True)
ap.add_argument('--expected-result', type=Path, required=True)
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
source = json.loads(args.inputs.read_bytes())
expected = json.loads(args.expected_result.read_bytes())
checker = Path(__file__).with_name('check_bill.py')
results = []
with tempfile.TemporaryDirectory(prefix='independent-bill-controls-') as directory:
    root = Path(directory)
    for name in ('cell', 'last-height', 'gaussian-height', 'repinned-clock'):
        data, result = deepcopy(source), deepcopy(expected)
        if name == 'cell':
            cell = data['gaussian']['cells'][0]
            cell[2] = str(Fraction(cell[2]) + Fraction(1, 2**100))
        elif name == 'last-height':
            data['terminal']['ordinary_heights'][-1] -= 1
        elif name == 'gaussian-height':
            data['terminal']['gaussian_height'] -= 1
        else:
            result['complete_log2_C'] -= 1
        result_bytes = (json.dumps(result, sort_keys=True) + '\n').encode()
        if name == 'repinned-clock':
            data['source']['expected_result_sha256'] = sha256(result_bytes).hexdigest()
        else:
            result_bytes = args.expected_result.read_bytes()
        inp, exp = root / f'{name}-inputs.json', root / f'{name}-expected.json'
        inp.write_text(json.dumps(data, sort_keys=True) + '\n')
        exp.write_bytes(result_bytes)
        run = subprocess.run([sys.executable, '-IB', str(checker), '--inputs', str(inp), '--expected-result', str(exp)],
                             capture_output=True, text=True, timeout=30)
        assert run.returncode != 0 and 'PASS_INDEPENDENT_FROZEN_TWO_TIER_BILL' not in run.stdout, name
        results.append({'control': name, 'returncode': run.returncode, 'stderr_sha256': sha256(run.stderr.encode()).hexdigest(),
                        'stderr_last_line': run.stderr.strip().splitlines()[-1] if run.stderr.strip() else ''})
out = args.output.resolve()
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({'controls': results}, indent=2) + '\n')
print('PASS_INDEPENDENT_BILL_NEGATIVE_CONTROLS', out, flush=True)
