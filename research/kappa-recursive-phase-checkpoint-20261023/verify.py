"""Bind the exact source export and replay the declared small R8 gates.

intqwq, with substantial OpenAI Codex assistance. Apache-2.0.
This is not a compiler proof or an exponent-improvement certificate.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGES = (
    'kappa-round8-owner-protocol-20261023',
    'kappa-round8-recursive-phase-20261023',
    'kappa-round8-complement-audit-20261023',
)
REPLAYS = (
    (PACKAGES[0], 'verify.py'),
    (PACKAGES[1], 'verify.py'),
    (PACKAGES[2], 'check_bundle.py'),
)
PRIVATE = {'.scratch', '.solver', '.lean-build', '.toolchain', '.lake', '__pycache__'}


def inventory():
    rows = {}
    for name in (*PACKAGES, HERE.name):
        for path in sorted((ROOT / 'research' / name).rglob('*')):
            if (not path.is_file() or PRIVATE.intersection(path.parts)
                    or path.suffix in {'.olean', '.ilean', '.pyc'}
                    or path == HERE / 'INVENTORY.json'):
                continue
            rows[path.relative_to(ROOT).as_posix()] = sha256(path.read_bytes()).hexdigest()
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    target = HERE / 'INVENTORY.json'
    if args.freeze:
        if target.exists():
            raise ValueError('A frozen export inventory must not be overwritten')
        target.write_text(json.dumps(dict(
            status='FROZEN_CHANGED_INTERFACE_RESEARCH_EXPORT',
            new_kappa=False, baseline_conditional_kappa='0.0030217758',
            files_sha256=inventory(),
            scope='Exact exported bytes and scoped replay; no profitable complete supplier.'
        ), indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    value = json.loads(target.read_text(encoding='utf-8'))
    if value['files_sha256'] != inventory():
        raise ValueError('Export source or receipt bytes changed')
    if value['new_kappa'] is not False:
        raise ValueError('This package claims no new kappa')
    if args.replay:
        scratch = (HERE / '.scratch').resolve()
        scratch.mkdir(exist_ok=True)
        for folder, entry in REPLAYS:
            script = ROOT / 'research' / folder / entry
            if not script.is_file():
                raise ValueError('Missing explicitly declared replay: ' + str(script))
            with tempfile.TemporaryDirectory(prefix='phase-replay-cache-', dir=scratch) as cache:
                if not Path(cache).resolve().is_relative_to(scratch):
                    raise ValueError('Replay cache must stay inside the package scratch directory')
                subprocess.run([sys.executable, '-E', '-S', '-B',
                                '-X', 'pycache_prefix=' + cache, str(script)],
                               cwd=ROOT, check=True, timeout=600)
        if value['files_sha256'] != inventory():
            raise ValueError('Replay modified a frozen export')
    print('PASS_RECURSIVE_PHASE_EXPORT', len(value['files_sha256']),
          'files; no new kappa; replay=' + str(args.replay))


if __name__ == '__main__':
    main()
