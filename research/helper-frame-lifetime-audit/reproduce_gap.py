#!/usr/bin/env python3
"""Reproduce a scalar-preserving frame mutation accepted by the old interface.

Runs the frozen interface script on temporary copies; never edits its source
or the archived fixtures. Requires the old script's runtime dependencies.
Prepared for sk1-j with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from verify import ROOT, FIXTURE, check_word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    fixture = ROOT / FIXTURE / 'ck'
    source = ROOT / 'scripts/verify_cold617_interface.py'
    word = json.loads(gzip.decompress((fixture / 'CANONICAL-WORD.json.gz').read_bytes()))
    if word['tail'][34] != ['add', 234, 0, -1, 2, 52]:
        raise ValueError('Frozen regression fixture changed')
    bad = copy.deepcopy(word)
    bad['tail'][34][-1] = 1
    if [g[:-1] for g in word['tail']] != [g[:-1] for g in bad['tail']]:
        raise ValueError('Mutation changed scalar operations')
    check_word(word)
    try:
        check_word(bad)
    except ValueError as error:
        rejection = str(error)
        if 'Nonmonotone helper 234 at tail[35]' not in rejection:
            raise
    else:
        raise ValueError('Independent checker accepted invalid lifetime')
    results = []
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    with tempfile.TemporaryDirectory(prefix='helper-lifetime-audit-') as directory:
        for label, candidate in [('original', word), ('full_then_proper', bad)]:
            run = Path(directory) / label
            run.mkdir()
            (run / 'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(json.dumps(candidate).encode(), mtime=0))
            (run / 'RESIDUAL-ADAPTERS.json').write_bytes((fixture / 'RESIDUAL-ADAPTERS.json').read_bytes())
            output = run / 'INTERFACE.json'
            completed = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(source), str(run),
                                        '--entering', '36', '--cold', '22', '--out', str(output)],
                                       cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', timeout=120)
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr or completed.stdout)
            report = json.loads(output.read_text(encoding='utf-8'))
            if report['status'] != 'PASS_FINITE_MULTI_TAIL_AND_EXACT_WRAPPER_BINDING':
                raise ValueError('Unexpected frozen checker result')
            results.append(dict(case=label, exit_code=completed.returncode, status=report['status']))
    result = dict(status='REPRODUCED_STANDALONE_INTERFACE_GAP',
                  frozen_checker_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  scalar_operations_unchanged=True, mutation='ck tail[34] frame 52 -> FULL (1)',
                  original_checker=results, independent_rejection=rejection,
                  scope='The upstream transport already checks monotonicity. This is not a counterexample to the selected result.')
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
