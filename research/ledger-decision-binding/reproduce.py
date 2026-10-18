#!/usr/bin/env python3
"""Replay a pinned before/after ledger-projection failure without changing files.

roife, with substantial OpenAI Codex assistance. Apache-2.0.
This checks review metadata integrity, not the multiplication theorem.
"""
import argparse
import contextlib
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
CHECKER = 'scripts/verify_pr_reconciliation.py'
BASE_CHECKER_SHA256 = '423991a79b1ee0304c1ab075c041eff6d3111da08a75a5815ddc5661a47c12e2'
CASES = (
    ('unchanged', {}),
    ('paired_forged_heads', {'reviewed_head': '0' * 40, 'current_head': '0' * 40}),
    ('unsupported_superseded', {'disposition': 'superseded'}),
    ('invented_location', {'integration_location': ['research/not-the-reviewed-contribution']}),
    ('erased_closure', {'closure': None}),
    ('contradictory_github_state', {'github_state': 'OPEN'}),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_checker(source):
    module = types.ModuleType('ledger_reproduction_checker')
    module.__file__ = str(ROOT / CHECKER)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module


def run_case(checker, ledger, updates):
    # Only the ledger JSON read is replaced. Every source, receipt, archived
    # artifact and decision read still reaches the unchanged checkout.
    changed = json.loads(json.dumps(ledger))
    row = next(p for p in changed['pull_requests'] if p['number'] == 626)
    row.update(updates)
    read_text = Path.read_text

    def read(path, *args, **kwargs):
        if path == ROOT / 'docs/research/pr-ledger.json':
            return json.dumps(changed)
        return read_text(path, *args, **kwargs)

    output = io.StringIO()
    try:
        with patch.object(Path, 'read_text', read), contextlib.redirect_stdout(output):
            checker.main()
    except ValueError as exc:
        return {'status': 'REJECTED', 'reason': str(exc)}
    return {'status': 'ACCEPTED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional JSON evidence file')
    args = parser.parse_args()
    original = subprocess.check_output(['git', 'show', BASE + ':' + CHECKER], cwd=ROOT)
    require(sha256(original).hexdigest() == BASE_CHECKER_SHA256, 'Unexpected baseline checker bytes')
    current = (ROOT / CHECKER).read_bytes()
    ledger_path = 'docs/research/pr-ledger.json'
    ledger_bytes = (ROOT / ledger_path).read_bytes()
    pinned_ledger = subprocess.check_output(['git', 'show', BASE + ':' + ledger_path], cwd=ROOT)
    require(ledger_bytes == pinned_ledger, 'This historical replay requires the base ledger bytes')
    ledger = json.loads(ledger_bytes)
    before, after = load_checker(original), load_checker(current)
    results = []
    for name, updates in CASES:
        baseline = run_case(before, ledger, updates)
        fixed = run_case(after, ledger, updates)
        require(baseline['status'] == 'ACCEPTED', 'Baseline did not accept ' + name)
        require(fixed['status'] == ('REJECTED' if updates else 'ACCEPTED'),
                'Unexpected fixed result for ' + name)
        if updates:
            require('ledger differs from family decision' in fixed['reason'],
                    'Mutation failed for an unrelated reason: ' + name)
        results.append({'case': name, 'pr': 626, 'updates': updates,
                        'baseline': baseline, 'fixed': fixed})
        print(name + ': baseline ' + baseline['status'] + ', fixed ' + fixed['status'], flush=True)
    inputs = {ledger_path: sha256(ledger_bytes).hexdigest()}
    for name in ledger['family_rounds']:
        inputs[name] = sha256((ROOT / name).read_bytes()).hexdigest()
    report = {'base_commit': BASE, 'seed': 99,
              'scope': 'Offline review metadata projection; no mathematical or live GitHub-state claim.',
              'baseline_checker_sha256': BASE_CHECKER_SHA256,
              'fixed_checker_sha256': sha256(current).hexdigest(),
              'source_sha256': inputs, 'cases': results}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: unchanged ledger accepted; all five previously accepted provenance mutations rejected')


if __name__ == '__main__':
    main()
