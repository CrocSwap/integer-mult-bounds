#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""One-command check of the opt-in transport-audit accelerator.

1. tests/test_exactness.py with Fraction._from_coprime_ints and again with the public Fraction constructor;
2. equivalence.py on the four archived control suites (or --quick: the T37 suite only);
3. every deterministic field of the equivalence report must equal EXPECTED.json.  Timings are printed, not compared.
Usage: python3 -I -B research/fast-transport-audit-seed87/verify.py [--quick] [--write-expected]
"""
import argparse
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROUTING = ROOT / ('research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/'
                  'pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz')


def deterministic(report):
    return {name: {k: v for k, v in s.items() if k != 'timing'} for name, s in report['suites'].items()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--write-expected', action='store_true')
    ap.add_argument('--report', type=Path, help='also save the full equivalence report (with timings) here')
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='fast-hpe-verify-') as tmp:
        tmp = Path(tmp)
        word = tmp / 'u8.json.gz'
        with tarfile.open(ROOT / 'research/community-frontier942-audit/t37-replay.tar.gz') as t:
            word.write_bytes(t.extractfile('native/barch/FULL-WORD.json.gz').read())
        env = dict(os.environ, FAST_HPE_TEST_WORD=str(word), FAST_HPE_TEST_ROUTING=str(ROUTING))
        for flag in ([], ['--public-fraction']):
            r = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'tests/test_exactness.py'), *flag],
                               env=env, capture_output=True, text=True)
            last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''
            if r.returncode or last != 'PASS_FAST_HPE_EXACTNESS':
                raise SystemExit('FAIL exactness tests %s\n%s%s' % (flag, r.stdout[-3000:], r.stderr[-2000:]))
            print('PASS exactness tests', 'public Fraction' if flag else 'coprime constructor', flush=True)
        out = tmp / 'EQUIVALENCE.json'
        cmd = [sys.executable, '-I', '-B', str(HERE / 'equivalence.py'), '--out', str(out)]
        if a.quick:
            cmd += ['--suite', 't37-u8-layer-end']
        r = subprocess.run(cmd)
        if r.returncode:
            raise SystemExit('FAIL equivalence')
        report = json.loads(out.read_text())
        if a.report:
            a.report.write_text(out.read_text())
    got = deterministic(report)
    if a.write_expected:
        (HERE / 'EXPECTED.json').write_text(json.dumps(got, indent=1, sort_keys=True) + '\n')
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    for name, fields in got.items():
        if fields != expected.get(name):
            raise SystemExit('FAIL %s differs from EXPECTED.json' % name)
    total = [sum(s['timing'][k] for s in report['suites'].values()) for k in ('direct_cpu', 'fast_cpu')]
    print('PASS_FAST_HPE_TRANSPORT suites=%d audits=%d identical_receipts_logs_outcomes cpu=%.1fs->%.1fs (%.2fx)' % (
        len(got), sum(s['audits'] for s in got.values()), total[0], total[1], total[0] / total[1]))


if __name__ == '__main__':
    main()
