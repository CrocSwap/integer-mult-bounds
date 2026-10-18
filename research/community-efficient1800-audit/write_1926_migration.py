from pathlib import Path
import json
P=Path('/tmp/pr-efficient1800');H=P/'combined-1926/research/unittest-receipt-comparison'
code='''#!/usr/bin/env python3
"""Replay Arham Tahir's PR1926 in its exact historical runtime context.

Original comparison, tests and result are unchanged. This bounded replay does
not run the full repository benchmark or replace the current isolated runner.
Maintenance: Douglas Colkitt with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from hashlib import sha256
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = 'research/unittest-receipt-comparison'
ORIGINAL_FILES = __ORIGINAL__
INPUTS = __INPUTS__
ARCHIVED_METADATA = {'README.md', 'SOURCES.json', 'VERIFY.json'}
MARKER = 'PASS_UNITTEST_RECEIPT_COMPARISON collisions=2 tests=20'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def prepare(root, snapshot):
    """Authenticate everything before creating the private replay tree."""
    root = Path(root)
    content = {}
    for name, digest in ORIGINAL_FILES.items():
        physical = root / PACKAGE / ('historical' if name in ARCHIVED_METADATA else '') / name
        raw = physical.read_bytes()
        require(sha256(raw).hexdigest() == digest, 'Original package changed: ' + name)
        content[PACKAGE + '/' + name] = raw
    for relative, row in INPUTS.items():
        raw = (root / row['physical']).read_bytes()
        require(sha256(raw).hexdigest() == row['sha256'], 'Historical input changed: ' + relative)
        content[relative] = raw
    require(not snapshot.exists(), 'Replay destination already exists')
    for relative, raw in content.items():
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    return {name: sha256(raw).hexdigest() for name, raw in content.items()}


def inventory(root):
    return {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def replay(root=ROOT, optimized=False):
    with tempfile.TemporaryDirectory(prefix='pr1926-historical-') as td:
        snapshot = Path(td) / 'repo'
        before = prepare(root, snapshot)
        command = [sys.executable, '-B', *(['-O'] if optimized else []),
                   str(snapshot / PACKAGE / 'verify.py')]
        env = os.environ.copy()
        env.pop('PYTHONOPTIMIZE', None)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        result = subprocess.run(command, cwd=snapshot, env=env, capture_output=True,
                                text=True, timeout=120)
        require(result.returncode == 0, 'Historical verifier failed: ' + result.stdout + result.stderr)
        require(result.stdout.splitlines() and result.stdout.splitlines()[-1] == MARKER,
                'Historical verifier did not report complete 20-test replay')
        require(inventory(snapshot) == before, 'Historical replay inputs changed')
        print(result.stdout, end='')
    print('PASS_PR1926_HISTORICAL_CONTEXT optimized=' + str(optimized))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--optimized', action='store_true')
    args = parser.parse_args()
    replay(optimized=args.optimized)


if __name__ == '__main__':
    main()
'''
code=code.replace('__ORIGINAL__',repr(json.loads((P/'1926-original-pins.json').read_text()))).replace('__INPUTS__',repr(json.loads((P/'1926-input-map.json').read_text())))
(H/'historical_replay.py').write_text(code.replace('import shutil\n',''))
(H/'test_historical_replay.py').write_text('''#!/usr/bin/env python3
"""Fail-closed controls for the PR1926 historical migration, not suite timing.
Douglas Colkitt with OpenAI Codex assistance; Apache-2.0.
"""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('historical1926', HERE / 'historical_replay.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class HistoricalReplay(unittest.TestCase):
    def fixture(self, root):
        paths = [m.PACKAGE + '/' + ('historical/' if n in m.ARCHIVED_METADATA else '') + n
                 for n in m.ORIGINAL_FILES]
        paths += [row['physical'] for row in m.INPUTS.values()]
        for relative in paths:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(m.ROOT / relative, target)
        return paths

    def test_exact_context_and_every_changed_source_rejects_before_copy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'source'
            paths = self.fixture(root)
            target = Path(td) / 'positive'
            expected = m.prepare(root, target)
            self.assertEqual(m.inventory(target), expected)
            self.assertEqual(len(expected), len(m.ORIGINAL_FILES) + len(m.INPUTS))
            for relative in paths:
                f = root / relative
                original = f.read_bytes()
                f.write_bytes(original + b'\\ncorruption\\n')
                destination = Path(td) / 'rejected'
                with self.subTest(path=relative), self.assertRaises(ValueError):
                    m.prepare(root, destination)
                self.assertFalse(destination.exists())
                f.write_bytes(original)
            archive = root / m.INPUTS['scripts/run_isolated_tests.py']['physical']
            archive.unlink()
            with self.assertRaises(FileNotFoundError):
                m.prepare(root, Path(td) / 'missing')

    def test_existing_destination_rejects(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                m.prepare(m.ROOT, root)

    def test_failed_or_silent_successful_child_rejects(self):
        for code, out, error in [(1, m.MARKER + '\\n', 'failed'),
                                 (0, '', 'did not report'),
                                 (0, m.MARKER + '\\npartial\\n', 'did not report')]:
            result = subprocess.CompletedProcess([], code, out, '')
            with self.subTest(code=code, out=out), patch.object(m.subprocess, 'run', return_value=result):
                with self.assertRaisesRegex(ValueError, error):
                    m.replay()

    def test_post_replay_mutation_rejects(self):
        def child(command, **kw):
            source = Path(kw['cwd']) / m.PACKAGE / 'RESULT.json'
            source.write_bytes(source.read_bytes() + b' ')
            return subprocess.CompletedProcess(command, 0, m.MARKER + '\\n', '')
        with patch.object(m.subprocess, 'run', side_effect=child):
            with self.assertRaisesRegex(ValueError, 'inputs changed'):
                m.replay(optimized=True)


if __name__ == '__main__':
    unittest.main()
''')
f=H/'README.md';s=f.read_text();s=s.replace('predecessor inputs are live and must still match their immutable pins.', 'predecessor inputs are historical runtime inputs and must still match their immutable pins. The current registered replay uses the authenticated private context described below.')
s=s.replace('python3 -B research/unittest-receipt-comparison/verify.py\npython3 -O -B research/unittest-receipt-comparison/verify.py\npython3 -B research/unittest-receipt-comparison/test_comparison.py -v','python3 -B research/unittest-receipt-comparison/historical_replay.py\npython3 -O -B research/unittest-receipt-comparison/historical_replay.py --optimized\npython3 -I -O -B research/unittest-receipt-comparison/test_historical_replay.py')
s=s.replace("To use the strict comparator with the predecessor's **entire** benchmark:","In the exact historical checkout only, the strict comparator can be used with the predecessor's **entire** benchmark:")
s=s.replace('## Open next questions','''## Maintainer historical context

Later accepted assertion, cancellation and completion fixes changed the live
isolated runner. The original adapter intentionally rejects that source drift.
The registered commands now authenticate the exact original package and its
three runtime inputs, copy them into a temporary tree, and run the unchanged
20-test verifier there in normal and optimized modes. Both complete deterministic
receipts must match; silent early exit or changes to any copied input reject.
The current live runner is neither imported nor replaced by this replay.

`historical/` retains the original README, SOURCES and VERIFY bytes. The active
source inventory points to the original runner blob already preserved by
PR2859 at `scripts/historical-ci-inputs/ledger-batch932-run_isolated_tests.py`.
It remains an executable input, not a provenance-only entry. Original comparison,
adapter, tests, RESULT and VALIDATION files are unchanged. The private tree
restores the original SOURCES context before executing them; it requires no
Git metadata or network access at runtime.

The full-suite adapter command above has **not** been run or migrated to the
current runner. It remains an opt-in historical command; this migration checks
the complete declared bounded controls, not full-suite compatibility or timing.
Maintenance by Douglas Colkitt with OpenAI Codex assistance, following Dennis /
antunishdPursuit's exact historical snapshot in PR2859. Arham Tahir's original
contribution and predecessor notices are retained.

## Open next questions''')
f.write_text(s)
print('Wrote migration, four guard tests and precise README scope')
