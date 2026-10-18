"""Regenerate the three scoped certificates without changing the checkout."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1]
CASES = (
    ('encoder_receipt.py', 'ENCODER-PARTIAL.json'),
    ('compensation_rank.py', 'COMPENSATION-RANK.json'),
    ('mobius_frames.py', 'MOBIUS-FRAMES.json'),
)


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
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    checked = []
    for script, receipt in CASES:
        result = subprocess.run(
            [sys.executable, *flags, str(HERE / script)],
            cwd=output, env=env, check=True, capture_output=True, text=True,
        )
        (output / receipt).write_text(result.stdout)
        if result.stderr:
            (output / (script + '.stderr')).write_text(result.stderr)
        actual = json.loads(result.stdout)
        expected = json.loads((HERE / receipt).read_text())
        if actual != expected:
            raise ValueError(f'Certificate mismatch: {receipt}')
        checked.append(receipt)
    summary = {
        'status': 'PASS_HELPER_ROUTE_CERTIFICATES',
        'matched_receipts': checked,
        'scope': 'Partial encoder, compensation rank, and direct Mobius schedule only; no complete improved supplier is asserted.',
    }
    (output / 'REPLAY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
