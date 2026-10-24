#!/usr/bin/env python3
"""Run the frozen packet screen and semantic receipt controls.

Prepared with OpenAI Codex assistance.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--run', type=Path, required=True)
ap.add_argument('--work', type=Path, required=True)
args = ap.parse_args()
if not __debug__:
    raise SystemExit('Assertions must be enabled.')
root = args.run.resolve()
packet = root/'packet-joint-basis'
if args.work.exists():
    raise SystemExit('Use a new work directory.')
args.work.mkdir(parents=True)
records = []


def run(name, command, expected_exit=0, reason=None):
    start = time.monotonic()
    result = subprocess.run(command, text=True, capture_output=True, cwd=root)
    stdout = args.work/(name+'-stdout.log')
    stderr = args.work/(name+'-stderr.log')
    stdout.write_text(result.stdout)
    stderr.write_text(result.stderr)
    records.append(dict(name=name, command=list(map(str, command)), exit_code=result.returncode,
                        elapsed_seconds=round(time.monotonic()-start, 6), expected_exit=expected_exit,
                        required_rejection_reason=reason,
                        stdout_sha256=hashlib.sha256(stdout.read_bytes()).hexdigest(),
                        stderr_sha256=hashlib.sha256(stderr.read_bytes()).hexdigest()))
    if result.returncode != expected_exit or reason and reason not in result.stderr:
        raise RuntimeError(name+' failed its command contract')


primary = args.work/'RESULT.json'
run('primary', [sys.executable, '-B', str(packet/'check.py'), '--run', str(root), '--out', str(primary)])
command = [sys.executable, '-B', str(packet/'verify.py'), '--run', str(root)]
run('second-engine', command+['--receipt', str(primary), '--out', str(args.work/'SECOND-ENGINE.json')])
receipt = json.loads(primary.read_text())
bad = copy.deepcopy(receipt)
case = next(c for block in bad['blocks'] for c in block['paired_results'] if c['center_rank_deficit'] == 4)
case['center_rank_deficit'] = 0
mutant = args.work/'BAD-CENTER.json'
mutant.write_text(json.dumps(bad, indent=2)+'\n')
run('bad-center', command+['--receipt', str(mutant), '--out', str(args.work/'invalid-center-result.json')],
    1, 'An unpaid center direction was claimed free.')
bad = copy.deepcopy(receipt)
bad['negative_control']['required_cap'] = [1 << i for i in range(9)]
mutant = args.work/'BAD-FRAME.json'
mutant.write_text(json.dumps(bad, indent=2)+'\n')
run('bad-frame', command+['--receipt', str(mutant), '--out', str(args.work/'invalid-frame-result.json')],
    1, 'The printed output cap includes a forbidden restored direction.')
(args.work/'COMMANDS.json').write_text(json.dumps(records, indent=2)+'\n')
print(json.dumps(dict(status='PASS_CLEAN_REPLAY_AND_SEMANTIC_CONTROLS', commands=len(records))))
