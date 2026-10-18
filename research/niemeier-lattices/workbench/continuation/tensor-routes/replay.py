"""Replay the tensor lift and frozen clique certificate outside the checkout."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output_directory', type=Path)
    args = parser.parse_args()
    output = args.output_directory.resolve()
    if output.is_relative_to(PACKAGE.parents[1]):
        raise ValueError('Output must be outside the checkout')
    output.mkdir(parents=True, exist_ok=False)
    flags = ['-B']
    if sys.flags.isolated:
        flags.append('-I')
    if sys.flags.optimize:
        flags.append('-' + 'O' * sys.flags.optimize)
    result = subprocess.run(
        [sys.executable, *flags, str(HERE / 'verify_tensor.py')],
        cwd=output, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
        check=True, capture_output=True, text=True,
    )
    receipt = 'NATIVE-TENSOR-LIFT.json'
    (output / receipt).write_text(result.stdout)
    if result.stderr:
        (output / 'verify_tensor.stderr').write_text(result.stderr)
    if json.loads(result.stdout) != json.loads((HERE / receipt).read_text()):
        raise ValueError(f'Certificate mismatch: {receipt}')
    summary = {
        'status': 'PASS_NATIVE_TENSOR_LIFT_CERTIFICATE',
        'matched_receipts': [receipt],
        'scope': 'Exact common-frame embedding and scalar-factor transport. The inherited native supplier and its paid endpoint normalization are assumed, not replayed.',
    }
    (output / 'REPLAY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
