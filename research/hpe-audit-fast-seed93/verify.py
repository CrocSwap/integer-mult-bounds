#!/usr/bin/env python3
"""Differential check: fast exact HPE audit versus the vendored pairwise PR635 baseline.

Inputs are read from the committed selected PR1042 replay archive. For each of
the five words whose layer-end controls the selected chain runs (p6n, promo,
jx, hyb, frames), both implementations must give byte-identical output files,
an identical receipt (apart from elapsed seconds) and identical printed output.
A seeded fuzz then mutates those words (coefficients, including zero, negative,
non-dyadic, huge and non-integer values; gate drops, swaps and duplicates;
registers; frame vectors) and requires the same outcome: the same exception
type and arguments, or the same outputs.

Prepared by Wronskode (@Wronskode) with substantial AI assistance from Claude
(Anthropic) via Claude Code. Apache-2.0.
"""
import argparse
import contextlib
import copy
import gzip
import hashlib
import importlib.util
import io
import json
import random
import shutil
import sys
import tarfile
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz'
REFERENCE = HERE / 'baseline.py'  # pairwise-era PR635 audit (vendored; production path ships integer rows)
ROUTING = ROOT / ('research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/'
                  'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz')
PINS = {
    REFERENCE: 'c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3',
    ROUTING: 'e070ae2c78b4a1b644b418774af62b40d8d16e6ba89602f0474afb557d507c37',
}
WORDS = ('p6n', 'promo', 'jx', 'hyb', 'frames')
SECTIONS = ('A', 'B', 'cut', 'precondition', 'cleanup')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def outcome(module, raw, out):
    printed = io.StringIO()
    t = time.perf_counter()
    try:
        with contextlib.redirect_stdout(printed):
            module.run(raw, ROUTING, out)
    except Exception as exc:
        return ('raise', type(exc).__name__, repr(exc.args)), time.perf_counter() - t
    dt = time.perf_counter() - t
    files = {p.name: p.read_bytes() for p in sorted(out.iterdir())}
    receipt = json.loads(files.pop('SCALAR-FRAME-AUDIT.json'))
    receipt.pop('seconds')
    text = json.loads(printed.getvalue())
    text.pop('seconds')
    return ('pass', files, receipt, text), dt


def compare(ref, fast, word, tmp, tag):
    raw = tmp / (tag + '.json.gz')
    raw.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
    r, tr = outcome(ref, raw, tmp / (tag + '-ref'))
    f, tf = outcome(fast, raw, tmp / (tag + '-fast'))
    if r != f:
        raise SystemExit('MISMATCH %s: reference %s / fast %s' % (tag, str(r)[:300], str(f)[:300]))
    return r, tr, tf


def mutate(word, rng):
    w = copy.deepcopy(word)
    n = 2 * w['report']['v'] + w['report']['R']
    sec = rng.choice([s for s in SECTIONS if w[s]])
    i = rng.randrange(len(w[sec]))
    g = w[sec][i]
    kind = rng.choice(['coef', 'coef', 'coef', 'edge', 'drop', 'swap', 'dup', 'reg', 'frame'])
    if kind == 'coef':
        k = 3 if g[0] == 'add' else 2
        g[k + rng.randrange(2)] = rng.choice([-3, -2, -1, 1, 2, 3, 5, 7, 4, 1024, -1024])
    elif kind == 'edge':
        k = 3 if g[0] == 'add' else 2
        g[k + rng.choice([0, 1])] = rng.choice([0, 3 ** 60, -(5 ** 50), 2 ** 300, 'x', 1.5, None])
    elif kind == 'drop':
        del w[sec][i]
    elif kind == 'swap' and len(w[sec]) > 1:
        j = min(i + 1, len(w[sec]) - 1) if i + 1 < len(w[sec]) else i - 1
        w[sec][i], w[sec][j] = w[sec][j], w[sec][i]
    elif kind == 'dup':
        w[sec].insert(i, copy.deepcopy(g))
    elif kind == 'reg':
        g[1 + (rng.randrange(2) if g[0] == 'add' else 0)] = rng.randrange(n)
    elif kind == 'frame' and isinstance(g[-1], list) and g[-1]:
        j = rng.randrange(len(g[-1]))
        g[-1][j] ^= 1 << rng.randrange(9)
    return w, '%s:%s[%d]' % (kind, sec, i)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fuzz', type=int, default=40, help='mutants per run (spread over the five words)')
    ap.add_argument('--seed', type=int, default=93)
    ap.add_argument('--receipt', type=Path, help='write a JSON receipt here')
    a = ap.parse_args()
    for path, digest in PINS.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit('pinned input changed: %s' % path.relative_to(ROOT))
    ref = load('hpe_reference', REFERENCE)
    fast = load('hpe_fast', HERE / 'hpe_audit_fast.py')
    words = {}
    with tarfile.open(ARCHIVE) as tar:
        for name in WORDS:
            words[name] = json.loads(gzip.decompress(tar.extractfile('chain/%s/FULL-WORD.json.gz' % name).read()))
    tmp = Path(tempfile.mkdtemp())
    receipt = dict(honest={}, fuzz=dict(seed=a.seed, trials=a.fuzz, outcomes={}))
    try:
        t_ref = t_fast = 0.0
        for name, word in words.items():
            r, tr, tf = compare(ref, fast, word, tmp, 'honest-' + name)
            if r[0] != 'pass':
                raise SystemExit('honest word %s rejected: %s' % (name, r))
            receipt['honest'][name] = dict(canonical_sha256=hashlib.sha256(r[1]['CANONICAL-WORD.json.gz']).hexdigest(),
                                           identical=True)
            t_ref, t_fast = t_ref + tr, t_fast + tf
        rng = random.Random(a.seed)
        counts = receipt['fuzz']['outcomes']
        for k in range(a.fuzz):
            name = WORDS[k % len(WORDS)]
            w, desc = mutate(words[name], rng)
            r, tr, tf = compare(ref, fast, w, tmp, 'fuzz%d' % k)
            key = r[0] if r[0] == 'pass' else '%s %s' % (r[1], r[2].split(',')[0][:60])
            counts[key] = counts.get(key, 0) + 1
            t_ref, t_fast = t_ref + tr, t_fast + tf
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    receipt['status'] = 'PASS_HPE_AUDIT_FAST_EQUIVALENCE'
    receipt['timing_seconds'] = dict(reference=round(t_ref, 1), fast=round(t_fast, 1),
                                     note='machine-dependent; not part of the equivalence claim')
    if a.receipt:
        a.receipt.write_text(json.dumps(receipt, indent=1, sort_keys=True) + '\n')
    print('%s | honest 5/5 identical | fuzz %d seed %d identical | reference %.1fs fast %.1fs'
          % (receipt['status'], a.fuzz, a.seed, t_ref, t_fast))


if __name__ == '__main__':
    main()
