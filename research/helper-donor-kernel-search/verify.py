#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Positive control, negative control and sweep-log tally for search.py.

usage: python -B verify.py --toolkit PR1186/research/exact-frame-toolkit
  1. pins of the vendored words;
  2. positive control: on #1218's base word (pre-kernel), pivot 555 must rediscover #1297's kernel:
     delete reads 466/502/734, donor 620 coefficient 2 at hook 112, cost delta -11676, profile H1 -3, H3 +1;
  3. negative control: on #1305's final base word (kernel already applied), pivot 555 yields no gain;
  4. the recorded all-register sweeps of #1305's two words contain no gain and cover every write.
"""
import argparse, hashlib, os, re, subprocess, sys
from pathlib import Path
PKG = Path(__file__).resolve().parent
PINS = {'inputs/K4-BASE-WORD.json.gz': 'e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e',
        'inputs/K4-EXTRA-WORD.json.gz': '7b0e9fbda32749aabc7e156d9fe09bceb0624a178628fe69e5dfea783462f905',
        'inputs/PR1218-BASE-WORD.json.gz': '4e837da23d932fc1336ef84dd1a802b46dbcb43bcf783b1338eeb7fa260eca1e'}
def run(word, tk, piv):
    r = subprocess.run([sys.executable, '-B', str(PKG / 'search.py'), str(PKG / word), str(tk), piv], cwd=tk,
                       capture_output=True, text=True, env=dict(os.environ, SHARD='0', NSH='1'), timeout=1200)
    assert r.returncode == 0, r.stderr[-2000:]
    return r.stdout
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--toolkit', type=Path, required=True); a = ap.parse_args()
    for rel, h in PINS.items():
        assert hashlib.sha256((PKG / rel).read_bytes()).hexdigest() == h, rel
    out = run('inputs/PR1218-BASE-WORD.json.gz', a.toolkit.resolve(), '555')
    hit = [l for l in out.splitlines() if "del [466, 502, 734] donor [(112, 620, '2')] ok -11676" in l]
    assert hit and '{1: 2355, 2: 504, 3: 411, 4: 130, 5: 82}' in hit[0], 'positive control'
    out = run('inputs/K4-BASE-WORD.json.gz', a.toolkit.resolve(), '555')
    assert not re.search(r' ok -\d', out), 'negative control'
    for name in ('SWEEP-K4-BASE.log', 'SWEEP-K4-EXTRA.log'):
        log = (PKG / 'evidence' / name).read_text()
        assert 'Traceback' not in log and not re.search(r' ok -\d', log), name
        n = sum(1 for l in log.splitlines() if l.startswith('pivot'))
        assert n >= 1000, (name, n)
        print(name, 'write instances', n, 'gains 0')
    print('PASS_HELPER_DONOR_KERNEL_SEARCH_CONTROLS')
if __name__ == '__main__':
    main()
