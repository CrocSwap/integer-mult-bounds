"""Replay retained paid-controller receipts without modifying the checkout."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable import PACKAGE, replay_scripts, require, workspace_path

CASES = (
    ('screen.py', 'RESULT.json'),
    ('banked.py', 'BANKED.json'),
    ('encoder.py', 'ENCODER.json'),
    ('encoder_conservative.py', 'ENCODER-CONSERVATIVE.json'),
    ('full_centers.py', 'FULL-CENTERS.json'),
    ('unfused/verify.py', 'unfused/RESULT.json'),
    ('RECTANGLE-LOWER/verify.py', 'RECTANGLE-LOWER/RESULT.json'),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, help='External output directory; temporary by default')
    parser.add_argument('--normal', action='store_true', help='Use -I without -O for child scripts')
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    for receipt in ('unfused/RESULT.json', 'RECTANGLE-LOWER/RESULT.json'):
        source = json.loads((directory / receipt).read_text())['source']
        require(hashlib.sha256((PACKAGE / source['path']).read_bytes()).hexdigest()
                == source['sha256'], 'Pinned cost engine hash')
    workspace = workspace_path(args.workspace)
    rows = replay_scripts(directory, CASES, workspace, optimized=not args.normal)
    result = dict(status='PASS_PAID_CONTROLLER_PORTABLE', cases=rows,
                  scope='Conditional accounting and scoped obstructions, not an admitted supplier or kappa gain.')
    path = workspace / 'paid-controller/PORTABLE-REPLAY.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    print(f'Receipts and logs: {workspace}')


if __name__ == '__main__':
    main()
