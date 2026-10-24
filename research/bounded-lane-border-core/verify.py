#!/usr/bin/env python3
"""Read-only bounded replay. Yiyang, OpenAI Codex assistance. Apache-2.0."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(value, message):
    if not value:
        raise RuntimeError(message)


def inputs_and_profile():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row['sha256'],
                    'changed live input: ' + row['path'])
    word = json.loads(gzip.decompress((ROOT / 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
    expected = Counter({1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8})
    split = {1: [1], 2: [2], 3: [3], 4: [3, 1], 5: [3, 2], 8: [3, 3, 2]}
    paid = Counter()
    for orientation, program in word['programs'].items():
        census = Counter(event[-1] for event in program if event[0] in ('climb', 'center'))
        require(census == expected, 'paid source census: ' + orientation)
        require(len(program) == 21449, 'source event count')
        for rank, count in census.items():
            for part in split[rank]:
                paid[part] += count
    c = word['canonical']
    require(c['v'] == 112 and len(c['start']) == len(c['final']) == 632, 'source owners')
    frames = c['frames']
    helpers = Counter(len(frames[c['final'][i]]) - len(frames[c['start'][i]])
                      for i in range(224, 632))
    require(helpers == Counter({4: 28, 7: 7, 8: 47, 9: 326}), 'helper source rank increments')
    target = Counter({rank: 2 * count for rank, count in helpers.items()})
    target[17] = 224
    receipt = json.loads((PACKAGE / 'core/RESULT.json').read_text())['moment']
    require(dict(paid) == {int(k): v for k, v in receipt['paid_base'].items()}, 'bound paid profile')
    require(dict(target) == {int(k): v for k, v in receipt['target'].items()}, 'bound target profile')
    return {'paid_sites': 6596, 'source_events': 42898,
            'paid_split': dict(sorted(paid.items())), 'target': dict(sorted(target.items()))}


def run(relative, arguments=(), compare_json=None):
    # Fresh interpreter cache also prevents stale bytecode reads under -B.
    with tempfile.TemporaryDirectory(prefix='lane-replay-') as cache:
        command = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + cache]
        if sys.flags.optimize:
            command.append('-O')
        command += [str(PACKAGE / relative), *map(str, arguments)]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=120)
        require(result.returncode == 0, relative + ': ' + result.stdout + result.stderr)
        if compare_json:
            require(json.loads(result.stdout) == json.loads((PACKAGE / compare_json).read_text()),
                    relative + ': frozen receipt mismatch')
        require(bool(result.stdout.strip()), relative + ': empty result')
        return {'checker': relative, 'status': 'PASS',
                'stdout_sha256': hashlib.sha256(result.stdout.encode()).hexdigest()}


def main():
    source = inputs_and_profile()
    checks = [run('core/verify.py', ['--compare', PACKAGE / 'core/RESULT.json']),
              run('precision/verify_counterexample.py'),
              run('precision/verify_extraction.py'),
              run('independent/check.py'), run('independent/truncated.py'),
              run('independent/moment.py'),
              run('native-gates/check.py', compare_json='native-gates/RESULT.json')]
    print(json.dumps({'status': 'PASS_BOUNDED_LANE_BORDER_CORE', 'source': source,
                      'checks': checks, 'no_new_kappa': True}, sort_keys=True))


if __name__ == '__main__':
    main()
