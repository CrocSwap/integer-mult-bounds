#!/usr/bin/env python3
"""Replay the selected productive-helper construction without altering frozen inputs.

Douglas Colkitt, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from verify_selected_result import check

ROOT = Path(__file__).resolve().parents[1]

def main():
    if sys.flags.optimize:
        raise SystemExit("Assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check-only', action='store_true')
    mode.add_argument('--work', type=Path)
    args = parser.parse_args()
    record = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    if record['audited_source_head'] != 'da637c87c89482bc4c86be36bd0071b3d400dbed':
        record = json.loads((ROOT / 'certificates/checkpoints/frontier4359.json').read_text())
    if record['audited_source_head'] != 'da637c87c89482bc4c86be36bd0071b3d400dbed':
        raise SystemExit("Wrong historical PR4359 checkpoint")
    check(record, historical=True)
    command = [sys.executable, '-B', str(ROOT / 'research/kappa-0023-productive-jobs/verify.py')]
    command += ['--check-only'] if args.check_only else ['--out', str(args.work.resolve())]
    subprocess.run(command, cwd=ROOT, check=True)

if __name__ == '__main__':
    main()
