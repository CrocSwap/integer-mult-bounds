#!/usr/bin/env python3
"""Fresh replay: PR284's full verifier, two frozen retiming passes, then PR284's native checks.

Usage:
  python3 -B verify.py --pr284 /path/to/pr284/research/gen4-collective-families-283 --output /fresh/dir \
      [--cxx g++] [--boost-include /path]
"""
import argparse, concurrent.futures, hashlib, json, shutil, struct, subprocess, sys, time
from collections import Counter
from pathlib import Path

if not __debug__:
    raise SystemExit('assertions are required')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'code'))
import emit, frames_audit  # noqa: E402

PR284_MANIFEST = '465a382eabdf64fbe2627292d6a73266b19099b8c55dc5911b16746772283bff'
WORD_FILES = ('COHORT249-RECORDS.bin', 'COHORT249-FRAMES.json', 'COHORT249-INITIAL.json', 'COHORT249-FINAL.json')
RECEIPTS = ('LEGALITY.json', 'PREFIX.json', 'GLOBAL.json', 'BANK-CHARTS.json', 'BANK-REVIEW.json',
            'PRICE.json', 'FINITE.json', 'FIXED-PRICE.json')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(out, label, cmd):
    t = time.monotonic()
    with (out / 'logs' / (label + '.log')).open('w') as log:
        subprocess.run([str(c) for c in cmd], check=True, stdout=log, stderr=subprocess.STDOUT, timeout=3600)
    print('PASS %-22s %7.1fs' % (label, time.monotonic() - t), flush=True)


def replay_receipt(src, dst):
    """PR284's replay receipt with the histogram, delta, mass and record count recounted on the new word."""
    r = json.loads((src / 'COHORT249-REPLAY.json').read_text())
    records = list(struct.iter_unpack('<6i', (dst / 'COHORT249-RECORDS.bin').read_bytes()))
    h = emit.histogram(records)
    old = Counter({int(k): v for k, v in r['histogram'].items()})
    d = Counter(h); d.subtract(old)
    total = Counter({int(k): v for k, v in r['delta'].items()}); total.update(d)
    r.update(histogram={str(k): v for k, v in sorted(h.items())}, delta={str(k): v for k, v in sorted(total.items()) if v},
             new_rank_mass=sum(k * v for k, v in h.items()), new_records=len(records),
             extreme_frame_retiming_delta={str(k): v for k, v in sorted(d.items()) if v})
    (dst / 'COHORT249-REPLAY.json').write_text(json.dumps(r, indent=2) + '\n')
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pr284', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--cxx', default='g++')
    ap.add_argument('--boost-include', type=Path)
    a = ap.parse_args()
    base, out = a.pr284.resolve(), a.output.resolve()
    assert not out.exists() and not out.is_relative_to(HERE) and not out.is_relative_to(base), 'fresh output outside packages'
    assert sha(base / 'MANIFEST.json') == PR284_MANIFEST, 'PR284 package is not the pinned commit'
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    for name, digest in manifest.items():
        assert sha(HERE / name) == digest, 'package file changed: ' + name
    expected = json.loads((HERE / 'expected.json').read_text())
    passes = json.loads((HERE / 'data/passes.json').read_text())
    out.mkdir(parents=True); (out / 'logs').mkdir()
    start = time.monotonic()

    # 1. PR284, freshly and completely (its own nine upstream stages, transforms and checks).
    cmd = [sys.executable, '-X', 'utf8', '-B', base / 'verify.py', '--output', out / 'pr284', '--cxx', a.cxx]
    if a.boost_include:
        cmd += ['--boost-include', a.boost_include]
    run(out, 'pr284-full-verifier', cmd)
    U = out / 'pr284'
    assert json.loads((U / 'CERTIFICATE.json').read_text())['status'] == 'PASS_SOURCE_REGENERATED_COMPOSITION'
    bin_, X, F = U / 'bin', U / 'restored', U / 'restored/frames.json'

    # 2. The PR284 final word, with its pinned final frames written beside it.
    w = out / 'word0'; w.mkdir()
    for name in WORD_FILES[:3]:
        shutil.copy2(U / 'final' / name, w / name)
    (w / 'COHORT249-FINAL.json').write_text(json.dumps(json.loads((X / '249-states.json').read_text())['final']))
    assert sha(w / 'COHORT249-RECORDS.bin') == passes['base']['input_word_sha256'], 'PR284 final word mismatch'

    # 3. Frozen passes, each audited exactly against the word it is applied to.
    report = []
    for i, step in enumerate(passes['passes']):
        aud = frames_audit.audit(F, w, step)
        nxt = out / ('word%d' % (i + 1))
        res = emit.apply_pass(F, w, step, nxt)
        report.append(dict(unit=step['unit'], audit=aud, emit=res))
        print('PASS pass %d (%s): %s' % (i + 1, step['unit'], json.dumps(res['histogram_delta'])), flush=True)
        w = nxt
    D = w
    assert sha(D / 'COHORT249-RECORDS.bin') == expected['word_sha256'], 'final word mismatch'

    # 4. PR284's side inputs (target/kernel receipts used by its checkers), then every native check afresh.
    for p in sorted((U / 'final').glob('*.json')):
        if p.name not in WORD_FILES + RECEIPTS + ('COHORT249-REPLAY.json',):
            shutil.copy2(p, D / p.name)
    replay_receipt(U / 'final', D)
    jobs = [('legality', [bin_ / 'legality', X, D, D / 'LEGALITY.json']),
            ('prefix', [bin_ / 'prefix', X, D, D / 'PREFIX.json']),
            ('bank-charts', [bin_ / 'banks', X, D / 'COHORT249-INITIAL.json', D / 'COHORT249-FRAMES.json', D, 'gen4-composed-endpoints120']),
            ('five-stage-columns', [bin_ / 'global', D / 'COHORT249-RECORDS.bin', X / '249-states.json', D / 'GLOBAL.json'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda j: run(out, *j), jobs))
    run(out, 'exact-price', [bin_ / 'price', D / 'COHORT249-REPLAY.json', D / 'BANK-REVIEW.json', D / 'PRICE.json'])
    run(out, 'finite-invoice', [bin_ / 'finite', D / 'COHORT249-RECORDS.bin', D / 'PRICE.json', D / 'BANK-REVIEW.json', D / 'GLOBAL.json', D / 'FINITE.json'])
    run(out, 'fixed-prime', [bin_ / 'fixed', D / 'PRICE.json', D / 'FINITE.json', D / 'FIXED-PRICE.json'])
    for name in ('LEGALITY.json', 'PREFIX.json', 'GLOBAL.json', 'BANK-REVIEW.json'):
        assert json.loads((D / name).read_text())['status'].startswith('PASS'), name
    fixed = json.loads((D / 'FIXED-PRICE.json').read_text())
    assert fixed['kappa'] == expected['kappa'], (fixed['kappa'], expected['kappa'])
    base_kappa = json.loads((U / 'final/FIXED-PRICE.json').read_text())['kappa']
    for name, digest in manifest.items():
        assert sha(HERE / name) == digest, 'package mutated: ' + name
    cert = dict(status='PASS_PR284_PLUS_EXTREME_FRAME_RETIMING', kappa=fixed['kappa'], kappa_decimal=fixed['kappa_decimal'],
                pr284_kappa=base_kappa, word_sha256=expected['word_sha256'], passes=report,
                seconds=round(time.monotonic() - start, 1),
                scope='Conditional finite construction under PR284\'s retained interfaces; same checkers, fresh receipts.')
    (out / 'CERTIFICATE.json').write_text(json.dumps(cert, indent=2) + '\n')
    print('PASS kappa = ' + fixed['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
