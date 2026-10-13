#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""Per-audit ablation: one honest transport audit of the T37 U8 word (from the repository's T37 archive) under
cumulative accelerator configurations, interleaved, best of N process-CPU times each.  Outputs are checked identical.
Usage: python3 -I -B bench.py [--repeats N] [--out BENCH.json]
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import sys
import tarfile
import tempfile
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code'))
sys.path.insert(0, str(HERE))
import hpe_audit_and_transport as atc  # noqa: E402
import fast_hpe_transport as fh        # noqa: E402

ROUTING = ROOT / ('research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/'
                  'pr558/vendor/pr552/complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz')
ORIG = dict(Q=atc.Q, apply=atc.apply, copy=atc.copy, basis=atc.basis, state_maps=atc.state_maps)
CONFIGS = ['pinned', '+Q/apply', '+copy', '+basis', '+state_maps']


def configure(level):
    for k, v in ORIG.items():
        setattr(atc, k, v)
    if level >= 1:
        atc.Q, atc.apply = fh.Qx, fh.fast_apply
    if level >= 2:
        atc.copy = types.SimpleNamespace(deepcopy=fh._deepcopy)
    if level >= 3:
        atc.basis = fh.make_basis(ORIG['basis'])     # fresh, cold cache for every run
    if level >= 4:
        atc.state_maps = fh.make_state_maps(ORIG['state_maps'])


def one(word, out):
    t0 = time.process_time()
    with contextlib.redirect_stdout(io.StringIO()):
        atc.run(word, ROUTING, out)
    cpu = time.process_time() - t0
    receipt = json.loads((out / 'SCALAR-FRAME-AUDIT.json').read_text())
    receipt.pop('seconds')
    digest = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode() + (out / 'CANONICAL-WORD.json.gz').read_bytes()
                            + (out / 'FULL-WORD.json.gz').read_bytes()).hexdigest()
    return cpu, digest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repeats', type=int, default=7)
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='fast-hpe-bench-') as tmp:
        tmp = Path(tmp)
        word = tmp / 'word.json.gz'
        with tarfile.open(ROOT / 'research/community-frontier942-audit/t37-replay.tar.gz') as t:
            word.write_bytes(t.extractfile('native/barch/FULL-WORD.json.gz').read())
        best, digests, k = {c: float('inf') for c in CONFIGS}, set(), 0
        for r in range(a.repeats):
            for level, name in enumerate(CONFIGS):
                configure(level)
                cpu, digest = one(word, tmp / ('run%d' % k))
                k += 1
                best[name] = min(best[name], cpu)
                digests.add(digest)
        configure(0)
    assert len(digests) == 1, 'outputs differ between configurations'
    base = best['pinned']
    report = dict(workload='hpe_audit_and_transport.run on the T37 U8 raw word (honest audit)', repeats=a.repeats,
                  best_process_cpu_seconds={c: round(v, 4) for c, v in best.items()},
                  speedup_vs_pinned={c: round(base / v, 2) for c, v in best.items()},
                  identical_outputs=True, python=sys.version.split()[0], load_average=[round(x, 1) for x in os.getloadavg()])
    print(json.dumps(report, indent=1))
    if a.out:
        a.out.write_text(json.dumps(report, indent=1) + '\n')


if __name__ == '__main__':
    main()
