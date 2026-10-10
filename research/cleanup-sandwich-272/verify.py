#!/usr/bin/env python3
"""Verify the cleanup-sandwich rewrite of 99 helpers on #272's word (SymPy 1.14.0, g++ with C++17, Boost headers).

  1. Pins.  The base package (#272, research/filtered-kernel-target120) matches SOURCE.json: its MANIFEST.json hash
     and every file it lists.
  2. Base replay.  #272's own verify.py regenerates the word from its pinned sources, compiles its nine native
     checkers and passes (about 7 minutes).  Its final word hash and kappa equal SOURCE.json.  With --replay, an
     existing completed base replay is accepted after the same checks.
  3. Rewrite (sandwich272.py).  Each of the 99 frozen helpers has exactly the gates t += a, a += b, t += a after the
     first cut, with t not a control between them.  The rewritten word moves a += b to the cut at a new
     four-dimensional frame and keeps t += b.  Every new frame is nondegenerate for 9I - J and every new connector
     is an exact rational inclusion.  The F2 replay of all formal source, target and dirty columns is the
     identity, and omitting either new gate is rejected.
  4. #272's native checkers, unchanged, on the new word: independent frame legality, multi-cut prefix kernels,
     the generic bank charts and role census, and the five-stage columns.
  5. Endpoints and banks (endpoints272.banks).  Each shortened endpoint is the rank-3 partial swap D_(P_F - P_S),
     with an exact chart, and the bank review is re-tiled exactly for the shortened residuals.
  6. Normalizers (endpoints272.normalizers).  Exact charts for every new frame, connector and endpoint, below the
     chart-factor bound and with entries below 2^80.
  7. #272's price engine reproduces its baseline, then prices the new histogram at the re-tiled stock: 47 strict
     constraints positive and the adjacent grid point rejected.  #272's finite invoice and fixed-prime refinement
     pass on the new word and bank inventory.
  8. The results equal expected.json.

Usage: python3 -B research/cleanup-sandwich-272/verify.py --base PKG --boost-include DIR --output NEW_DIR [--replay DIR]
  PKG is research/filtered-kernel-target120 from a checkout of commit 4d23d0ee (#272).
"""
import sys

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import shutil
import subprocess
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import endpoints272
import sandwich272

T0 = time.time()
SOURCE = json.loads((HERE / 'SOURCE.json').read_text())
EXPECT = json.loads((HERE / 'expected.json').read_text())


def log(*a):
    print('[%5.0fs]' % (time.time() - T0), *a, flush=True)


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def save(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run(cmd, logfile):
    with logfile.open('w') as out:
        subprocess.run(list(map(str, cmd)), stdout=out, stderr=subprocess.STDOUT, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--boost-include', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--replay', type=Path)
    ap.add_argument('--cxx', default='g++')
    args = ap.parse_args()
    base, out = args.base.resolve(), args.output.resolve()
    assert not out.exists() and not out.is_relative_to(HERE), 'output must be a new directory outside the package'

    # 1. Pins.
    assert digest(base / 'MANIFEST.json') == SOURCE['manifest_sha256'], 'base MANIFEST.json differs from SOURCE.json'
    for name, h in load(base / 'MANIFEST.json')['files'].items():
        assert digest(base / name) == h, ('base file differs from its manifest', name)
    log('PASS pins: base package', SOURCE['commit'][:8], 'matches SOURCE.json')
    out.mkdir(parents=True)

    # 2. Base replay.
    if args.replay:
        replay = args.replay.resolve()
    else:
        replay = out / 'base'
        run([sys.executable, '-B', base / 'verify.py', '--output', replay, '--boost-include', args.boost_include.resolve(),
             '--cxx', args.cxx], out / 'base.log')
    certificate = load(replay / 'CERTIFICATE.json')
    assert certificate['status'] == SOURCE['status'] and certificate['kappa'] == SOURCE['kappa'], 'base replay differs'
    export, lead, binary = replay / 'temporal/CURRENT249-EXPORT', replay / 'targeted', replay / 'bin'
    assert digest(lead / 'COHORT249-RECORDS.bin') == SOURCE['word_sha256'], 'base word differs from SOURCE.json'
    log('PASS base replay: kappa', certificate['kappa'])

    # 3. Rewrite.
    records, new_frames, receipt = sandwich272.rewrite(export, lead, load(HERE / 'selection.json')['helpers'])
    log('PASS rewrite: %d helpers, %d formal columns, controls %s, histogram delta %s' % (
        receipt['helpers_retired'], receipt['formal_columns'], receipt['omission_controls_wrong_rows'],
        receipt['histogram_delta']))

    # The new word in the base layout: final frames, frame table, records and the price input.
    X, L, C, T, V = out / 'export', out / 'lead', out / 'compiler', out / 'temporal', out / 'review'
    shutil.copytree(export, X)
    for d in (L, C, T, V):
        d.mkdir()
    for name in ('COHORT249-INITIAL.json', 'COHORT249-SELECTION.json'):
        shutil.copyfile(lead / name, L / name)
    states = load(X / '249-states.json')
    states['final'].update({str(e['helper']): e['frame'] for e in receipt['edits']})
    save(X / '249-states.json', states)
    frames = load(lead / 'COHORT249-FRAMES.json')
    for f, spec in new_frames.items():
        rows = []
        for row in spec['A']:
            q = [Q(x) for x in row]
            d = lcm(*(x.denominator for x in q))
            rows.append([int(x * d) for x in q])
        frames[f] = dict(spec, A=rows)
    save(L / 'COHORT249-FRAMES.json', frames)
    (L / 'COHORT249-RECORDS.bin').write_bytes(records)

    # 4. Native checkers of the base, unchanged.
    run([binary / 'cohort-legality-independent', X, L, V / 'INDEPENDENT-LEGALITY.json'], out / 'legality.log')
    run([binary / 'cohort-prefix-independent', X, L, V / 'INDEPENDENT-PREFIX.json'], out / 'prefix.log')
    run([binary / 'cohort-bank-review', X, L / 'COHORT249-INITIAL.json', L / 'COHORT249-FRAMES.json', C,
         'actual_multicut120'], out / 'bank-review.log')
    run([binary / 'cohort-five-stage-columns', L / 'COHORT249-RECORDS.bin', T / 'COHORT-FIVE-STAGE-COLUMNS.json'],
        out / 'columns.log')
    log('PASS native legality, prefix kernels, bank charts and five-stage columns')

    # 5-6. Endpoints, banks and normalizers.
    bank, bank_receipt = endpoints272.banks(export, lead, new_frames, receipt, load(C / 'BANK-REVIEW.json'))
    save(C / 'COHORT-BANK-REVIEW.json', bank)
    log('PASS endpoints and banks: %d replicas, %d banks saved per stage, literal stock %d' % (
        bank_receipt['replicas'], bank_receipt['banks_saved_per_stage'], bank['literal_stock']))
    norm = endpoints272.normalizers(export, lead, new_frames, records, receipt)
    log('PASS normalizers: %d charts, at most %d factors, max entry %d' % (
        norm['charts'], norm['max_factors'], norm['max_numerator_denominator']))

    # 7. Price, finite invoice and fixed prime.  #272's price main charges stock 521649 - new_entrance_rank; the
    # re-tiled banks lower the normalized stock by 20 per helper, which is passed through that field.
    replay_summary = load(lead / 'COHORT249-REPLAY.json')
    histogram, delta = dict(replay_summary['histogram']), dict(replay_summary['delta'])
    for r, c in receipt['histogram_delta'].items():
        histogram[r] = histogram.get(r, 0) + c
        delta[r] = delta.get(r, 0) + c
    saved = (load(C / 'BANK-REVIEW.json')['literal_stock'] - bank['literal_stock']) // 5
    assert saved == 20 * receipt['helpers_retired']
    save(L / 'COHORT249-REPLAY.json', dict(replay_summary, histogram=histogram, delta=delta,
                                           new_entrance_rank=replay_summary['new_entrance_rank'] + saved))
    run([binary / 'cohort-price', L / 'COHORT249-REPLAY.json', L / 'COHORT-EXACT-PRICE.json'], out / 'price.log')
    price = load(L / 'COHORT-EXACT-PRICE.json')['cohort_candidate']
    assert price['stock'] * 5 == bank['literal_stock'], 'priced stock differs from the bank inventory'
    assert price['positive_constraints'] == 47 and price['next_kappa_rejected'] > 0
    run([binary / 'cohort-finite-invoice', L / 'COHORT249-RECORDS.bin', L / 'COHORT-EXACT-PRICE.json',
         C / 'COHORT-BANK-REVIEW.json', T / 'COHORT-FIVE-STAGE-COLUMNS.json', T / 'COHORT-FINITE-INVOICE.json'],
        out / 'finite.log')
    run([binary / 'fixed-price', L / 'COHORT-EXACT-PRICE.json', T / 'COHORT-FINITE-INVOICE.json',
         L / 'FIXED-PRICE.json'], out / 'fixed.log')
    fixed = load(L / 'FIXED-PRICE.json')
    log('PASS price, finite invoice and fixed prime: kappa', fixed['kappa'])

    # 8. Expected values.
    result = {'kappa': fixed['kappa'], 'base_kappa': certificate['kappa'], 'exact_price_kappa': price['kappa'],
              'stock': price['stock'], 'deficit': price['deficit'], 'helpers_retired': receipt['helpers_retired'],
              'histogram_delta': receipt['histogram_delta'], 'word_sha256': receipt['output_sha256']}
    assert result == EXPECT, ('results differ from expected.json', result)
    save(out / 'CERTIFICATE.json', dict(result, status='PASS conditional finite witness', scope=(
        'Finite rewrite of #272; all-size compiler, analytic and assembly interfaces are those retained by #272.'),
        receipts={'rewrite': receipt, 'banks': bank_receipt, 'normalizers': norm}))
    log('PASS kappa = %s = %.18e, equal to expected.json' % (fixed['kappa'], float(Q(fixed['kappa']))))


if __name__ == '__main__':
    main()
