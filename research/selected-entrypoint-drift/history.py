#!/usr/bin/env python3
"""Replay the selected-result entry-point binder over every historical selection.

Each pinned commit changed certificates/selected-result.json, except the first,
which is this package's base. For each commit, the entry points and record are
read from git objects into a fresh directory, and the current binder
scripts/verify_selected_entrypoints.py is applied unchanged. The output records
every finding that does not match. "mismatch" means a restatement contradicts that commit's record;
"missing" means the binder found no anchor in that commit's wording, which for
older commits usually reflects a different format rather than drift.

Requires a non-shallow clone. Run from the repository root:

    python3 -I -B research/selected-entrypoint-drift/history.py --check

Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5,
Anthropic, via Claude Code). Apache-2.0.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPECTED = HERE / 'HISTORY.json'
BASE = '9a16422bf8d0ebd3342c1156c33cb5703c6cb02a'
# Every commit through BASE that changed certificates/selected-result.json, newest first.
SELECTIONS = (
    '3b83e4f14825ce1ae038a8c8159f130646991086', 'd6dfd8f21b1e0b7e3f93b7e30e64639390e48504',
    'c290b7b919790300e14004a75d8d24b55ca3c5b5', '2cdd93d0250554e5160edbb8535c4500c4227349',
    '5c5567d15bd019186519a4db267914257b5f1ac0', '2e9ed969d09570fbe949324b80da27a7f31d9399',
    '1db1fbe68cb5186899cf1fd691bc92056a845e49', '7f6ccd7ed1e5ee7fba9599f44f9a6fe08f582d62',
    '270c2458cf7f34fc252afe7c9d697f2cd6c93a59', '1c1e42f0d87c605496b8de9b7a0504099a8360f1',
    'a1e7d84866e73aa6f3355629ea31b24b8076b113', '91e29e7bbb7eab7d9ef8a4adc5d6971cd06bda51',
    '27d82ebe85596ddae65307c272e1c1cc350de904', 'd697aaa79d1d12882a8aa3432eaa45e37968da96',
    '86b30e035fcdffb72db93f759b4fda6a41b24de5', 'e2a02cac14dccf1279b3cfe673ce59ef0ba702d0',
    '6aed8701e3e3102898c66b5dcfc28d3cfc264edc',
)

spec = importlib.util.spec_from_file_location('selected_entrypoints', ROOT / 'scripts/verify_selected_entrypoints.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def git(*args):
    return subprocess.run(('git', '-C', str(ROOT)) + args, capture_output=True, check=False)


def materialize(commit, names, root):
    for name in names:
        blob = git('show', f'{commit}:{name}')
        if blob.returncode == 0:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blob.stdout)


def row(commit):
    require_commit = git('cat-file', '-e', commit + '^{commit}')
    if require_commit.returncode:
        raise SystemExit('Missing commit object; use a non-shallow clone: ' + commit)
    record = json.loads(git('show', f'{commit}:{checker.RECORD}').stdout)
    record.setdefault('reproduce', '')
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        names = checker.ENTRY_POINTS + ((record['previous_record'],) if 'previous_record' in record else ())
        materialize(commit, names, root)
        findings = checker.check(record, root)
    summary = {}
    for f in findings:
        statuses = summary.setdefault(f['entry'], set())
        statuses.add(f['status'])
    return {
        'commit': commit,
        'subject': git('log', '-1', '--format=%s', commit).stdout.decode().strip(),
        'selected_kappa': record['kappa'],
        'primary_pr': checker.primary_pr(record),
        'entries': {entry: ('contradicts' if 'mismatch' in s else 'no anchor' if 'missing' in s else 'agrees')
                    for entry, s in summary.items()},
        'checked': len(findings),
        'not_matching': [f for f in findings if f['status'] != 'match'],
    }


def history():
    return {'base': BASE, 'binder': 'scripts/verify_selected_entrypoints.py',
            'rows': [row(commit) for commit in (BASE,) + SELECTIONS]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='Require equality with the committed HISTORY.json')
    parser.add_argument('--write', action='store_true', help='Rewrite the committed HISTORY.json')
    args = parser.parse_args()
    result = history()
    text = json.dumps(result, indent=1, ensure_ascii=False) + '\n'
    if args.write:
        EXPECTED.write_text(text, encoding='utf-8')
    if args.check and EXPECTED.read_text(encoding='utf-8') != text:
        raise SystemExit('FAIL regenerated history differs from ' + str(EXPECTED.relative_to(ROOT)))
    for r in result['rows']:
        stale = sorted(e for e, s in r['entries'].items() if s == 'contradicts')
        print(r['commit'][:8], 'PR' + str(r['primary_pr'] or '?'), r['selected_kappa'],
              'contradicted by: ' + (', '.join(stale) or 'none'))
    print('PASS selected-entrypoint history: {} commits replayed'.format(len(result['rows'])))


if __name__ == '__main__':
    main()
