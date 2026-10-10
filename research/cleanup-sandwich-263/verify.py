#!/usr/bin/env python3
"""Verify the cleanup-sandwich rewrite of 45 helpers on #263's word (SymPy 1.14.0, g++ with C++17, Boost headers).

  1. Pins.  The base package (#263, research/multicut-kernel-condensation) matches SOURCE.json: its MANIFEST.json
     hash and every file it lists.
  2. Base replay.  The base package's own verify.py regenerates the word from its pinned sources and passes
     (about 6 minutes).  Its word hash equals SOURCE.json.  With --replay, an existing completed base replay is
     accepted after the same hash check.
  3. Rewrite (sandwich263.py).  Each of the 45 frozen helpers has exactly the gates t += a, a += b, t += a after the
     first cut, with t not a control between them.  The rewritten word moves a += b to the cut at a new
     four-dimensional frame and keeps t += b.  Every new frame is nondegenerate for 9I - J and every new connector
     is an exact rational inclusion.  The F2 replay of all formal source, target and dirty columns is the
     identity, and omitting either new gate is rejected.
  4. Endpoints and banks (endpoints263.banks).  Each shortened endpoint is the rank-3 partial swap D_(P_F - P_S),
     with an exact chart.  The width-120 banks re-tile exactly with 300 fewer banks per stage.
  5. Normalizers (endpoints263.normalizers).  Exact charts for every new frame, connector and endpoint, below the
     inherited factor bound and with entries below 2^80.
  6. The base package's native checkers, unchanged: independent frame legality of the new word with its new final
     frames, and the five-stage columns.
  7. Price.  The base price engine reproduces the base kappa on the base word, then prices the new word: 47 strict
     constraints positive and the adjacent grid point rejected.
  8. The base finite invoice on the new word and bank inventory.
  9. The results equal expected.json.

Usage: python3 -B research/cleanup-sandwich-263/verify.py --base PKG --boost-include DIR --output NEW_DIR [--replay DIR]
  PKG is research/multicut-kernel-condensation from a checkout of commit 87129308 (#263).
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
import struct
import subprocess
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import endpoints263
import sandwich263

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
    assert load(replay / 'CERTIFICATE.json')['status'] == 'PASS_ALL_SEVEN_NATIVE_CHECKERS_AND_PINNED_RECEIPTS'
    assert digest(replay / 'lead/COHORT249-RECORDS.bin') == SOURCE['word_sha256'], 'base word differs from SOURCE.json'
    log('PASS base replay: kappa', load(replay / 'CERTIFICATE.json')['kappa'])

    # 3. Rewrite.
    helpers = load(HERE / 'selection.json')['helpers']
    records, new_frames, receipt = sandwich263.rewrite(replay, helpers)
    word = out / 'word'
    word.mkdir()
    (word / 'records.bin').write_bytes(records)
    save(word / 'frames.json', new_frames)
    save(word / 'rewrite.json', receipt)
    log('PASS rewrite: %d helpers, %d formal columns, controls %s, histogram delta %s' % (
        receipt['helpers_retired'], receipt['formal_columns'], receipt['omission_controls_wrong_rows'],
        receipt['histogram_delta']))

    # 4-5. Endpoints, banks and normalizers.
    bank = endpoints263.banks(replay, new_frames, receipt)
    log('PASS endpoints and banks: %d banks per stage, literal stock %d' % (bank['banks_per_stage'], bank['literal_stock']))
    norm = endpoints263.normalizers(replay, new_frames, records, receipt)
    log('PASS normalizers: %d charts, at most %d factors, max entry %d' % (
        norm['charts'], norm['max_factors'], norm['max_numerator_denominator']))

    # 6. Native checkers of the base package, compiled from its pinned sources.
    binaries = {}
    for name in ('legality-independent', 'five-stage-columns', 'finite-invoice', 'price'):
        binaries[name] = out / name
        cmd = [args.cxx, '-std=c++17', '-O2', '-I', args.boost_include.resolve(), '-I', base / 'vendor']
        if name == 'price':
            cmd += ['-DPR254_PRICE_SOURCE="%s"' % (base / 'code/cohort-price.cpp'), HERE / 'price263.cpp']
        else:
            cmd += [base / ('code/cohort-%s.cpp' % name)]
        run(cmd + ['-o', binaries[name]], out / ('compile-%s.log' % name))
    export = replay / 'temporal/CURRENT249-EXPORT'
    gin, gout = out / 'geometry-input', out / 'geometry-output'
    gin.mkdir()
    gout.mkdir()
    for name in ('frames.json', '249-DONOR-OWNERSHIP.json'):
        shutil.copyfile(export / name, gin / name)
    states = load(export / '249-states.json')
    states['final'].update({str(e['helper']): e['frame'] for e in receipt['edits']})
    save(gin / '249-states.json', states)
    frames = load(replay / 'lead/COHORT249-FRAMES.json')
    for f, spec in new_frames.items():
        rows = []
        for row in spec['A']:
            q = [Q(x) for x in row]
            d = lcm(*(x.denominator for x in q))
            rows.append([int(x * d) for x in q])
        frames[f] = dict(spec, A=rows)
    save(gout / 'COHORT249-FRAMES.json', frames)
    for name in ('COHORT249-INITIAL.json', 'COHORT249-SELECTION.json'):
        shutil.copyfile(replay / 'lead' / name, gout / name)
    (gout / 'COHORT249-RECORDS.bin').write_bytes(records)
    run([binaries['legality-independent'], gin, gout, word / 'legality.json'], out / 'legality.log')
    run([binaries['five-stage-columns'], word / 'records.bin', word / 'columns.json'], out / 'columns.log')
    log('PASS native legality and five-stage columns')

    # 7. Price: control on the base word, then the new word.
    old_bank = load(replay / 'compiler/COHORT-BANK-REVIEW.json')
    M = max(norm['max_numerator_denominator'], int(old_bank['max_intermediate_numerator']),
            int(old_bank['max_intermediate_denominator']))
    U = 40 * M * M
    guard = 2 * U * U
    assert guard < 2 ** 80
    invoice = dict(bank, normalized_stock=bank['literal_stock'] // 5,
                   new_exact_charts=old_bank['new_exact_charts'] + len(receipt['edits']) + norm['move_pairs'],
                   max_new_chart_factors=max(old_bank['max_new_chart_factors'], norm['max_factors']) + 24,
                   max_intermediate_numerator=str(guard), max_intermediate_denominator=str(guard),
                   selector_charge=2 * 5 * 40 * (bank['literal_stock'] - 1 + 16587 * 120 * 787),
                   routing_prime_guard={'normalized_scaled_chart_entry_bound': U, 'pairwise_difference_numerator_bound': guard})
    save(word / 'bank-invoice.json', invoice)
    for label, blob, receipt_path in (('base', replay / 'lead/COHORT249-RECORDS.bin', replay / 'compiler/COHORT-BANK-REVIEW.json'),
                                      ('new', word / 'records.bin', word / 'bank-invoice.json')):
        save(out / ('%s-histogram.json' % label), {'histogram': dict(sandwich263.histogram(
            struct.iter_unpack('<6i', blob.read_bytes())))})
        run([binaries['price'], out / ('%s-histogram.json' % label), receipt_path, out / ('%s-price.json' % label)],
            out / ('price-%s.log' % label))
    assert load(out / 'base-price.json')['candidate'] == load(replay / 'lead/COHORT-EXACT-PRICE.json')['cohort_candidate'], \
        'price engine does not reproduce the base price'
    price = load(out / 'new-price.json')['candidate']
    assert price['positive_constraints'] == 47 and price['next_kappa_rejected'] > 0
    save(word / 'root-price.json', {'cohort_candidate': price})
    log('PASS price: base reproduced; new kappa', price['kappa'], '; adjacent grid point rejected')

    # 8. Finite invoice.
    run([binaries['finite-invoice'], word / 'records.bin', word / 'root-price.json', word / 'bank-invoice.json',
         word / 'columns.json', word / 'finite.json'], out / 'finite.log')
    log('PASS finite invoice')

    # 9. Expected values.
    result = {'kappa': price['kappa'], 'base_kappa': load(replay / 'lead/COHORT-EXACT-PRICE.json')['cohort_candidate']['kappa'],
              'coarse_saving': price['coarse'], 'stock': price['stock'], 'deficit': price['deficit'],
              'helpers_retired': receipt['helpers_retired'], 'histogram_delta': receipt['histogram_delta'],
              'word_sha256': receipt['output_sha256']}
    assert result == EXPECT, ('results differ from expected.json', result)
    save(out / 'CERTIFICATE.json', dict(result, status='PASS conditional finite witness', scope=(
        'Finite rewrite of #263; all-size compiler, analytic and assembly interfaces are those retained by #263.'),
        receipts={'rewrite': receipt, 'banks': {k: v for k, v in bank.items() if k != 'bank_patterns'},
                  'normalizers': norm, 'legality': load(word / 'legality.json'), 'finite': load(word / 'finite.json')}))
    log('PASS kappa = %s = %.15e, equal to expected.json' % (price['kappa'], float(Q(price['kappa']))))


if __name__ == '__main__':
    main()
