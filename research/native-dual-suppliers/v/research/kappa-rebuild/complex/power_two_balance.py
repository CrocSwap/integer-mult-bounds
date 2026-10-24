#!/usr/bin/env python3
"""Exact power-of-two balancing of the reconstructed H112 and dirty logger.

Apache-2.0. Substantial OpenAI assistance. This changes only explicit local
coefficient streams and dyadic unit scales; every recursive child is retained.
The exact arbitrary-input verifier and endpoint-gauge phase receipts are reused
from the separately source-bound reconstruction in rebuild_native.py.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import argparse
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rebuild_native as N

N_SHA = 'f94c527cc02215de49350d477618188c4c0da48bc8fb05b4e37b24c482cad7d5'


def make_balanced_h(c, word, geo, exponent=1):
    """Assemble 2^e v, transport it, deliver 12/2^e times that field."""
    N.need(isinstance(exponent, int) and -8 <= exponent <= 8, 'Bounded integral balancing exponent')
    q = N.Q(2)**exponent
    result = N.make_h_word(c, word, geo)
    for direction, program in result.items():
        out = []; completion = False
        for event in program:
            if event[0] == 'phase':
                completion = event[1] == 'fresh_H112_completion'
            if not completion or event[0] != 'scalar':
                out.append(event); continue
            op, frame = event[1:]
            if op[0] == 'copy' and op[1] == ['C', 0]:
                out.append(event)
                if q != 1:
                    out.append(N.scalar(['scale', ['C', 0], q.numerator, q.denominator], frame))
            elif op[0] == 'add':
                factor = q if op[1] == ['C', 0] else 1/q
                amount = N.Q(op[3], op[4])*factor
                out.append(N.scalar(op[:3]+[amount.numerator, amount.denominator], frame))
            else:
                out.append(event)
        result[direction] = out
    return result


def make_balanced_logger(c, word, geo, exponent=1):
    """Scale arbitrary P by 2^e, add 2^e v, scale back; dirty P is preserved."""
    N.need(isinstance(exponent, int) and -8 <= exponent <= 8, 'Bounded integral balancing exponent')
    q = N.Q(2)**exponent
    suffix = [['phase', 'fresh_balanced_forward_dirty_logger']]
    for k, a in enumerate(geo['selected']):
        suffix.append(['cache_child', k, 0, 1, 9])
        if q != 1:
            suffix.append(N.scalar(['scale', ['P', k], q.numerator, q.denominator], 1))
        suffix.append(N.scalar(['add', ['P', k], ['L', a], q.numerator, q.denominator], 1))
        for p, coefficient in sorted(geo['L'][k].items()):
            x = q*coefficient
            suffix.append(N.scalar(['add', ['P', k], ['L', p], x.numerator, x.denominator], 1))
        if q != 1:
            suffix.append(N.scalar(['scale', ['P', k], q.denominator, q.numerator], 1))
    return word['forward']+suffix


def scalar_sum(program):
    return sum(N.primitive_allowance(e[1]) for e in program if e[0] == 'scalar')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE/'balanced-certificates')
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    N.need(N.digest(HERE/'rebuild_native.py') == N_SHA, 'Pinned fresh reconstruction source')
    p, v, ce, receipt, inherited = N.authenticated(); geo = N.geometry(v.PACKET)
    result = dict(schema='fresh-native-power-two-balancing/1', source_sha256=N.digest(Path(__file__)),
                  reconstruction_source_sha256=N_SHA, no_new_kappa_claimed=True, providers={},
                  scope='Finite native all-column and phase certificates; full outer recurrence and rounded induction remain separate.')
    for tag in N.TAGS:
        c = N.read(N.BASE/(tag+'-CANONICAL.json.gz')); word = N.read(N.BASE/(tag+'-NATIVE-WORD.json.gz'))
        base_scalar = scalar_sum(word['forward'])
        scan = []
        for exponent in range(-4, 5):
            hw = make_balanced_h(c, word, geo, exponent)
            lw = make_balanced_logger(c, word, geo, exponent)
            scan.append(dict(exponent=exponent, H_increment=scalar_sum(hw['forward'])-base_scalar,
                             logger_increment=scalar_sum(lw)-base_scalar))
        N.need(min(scan, key=lambda r: r['H_increment'])['exponent'] == 1, 'H minimum in scanned power-two family')
        N.need(min(scan, key=lambda r: r['logger_increment'])['exponent'] == 1, 'Logger minimum in scanned power-two family')
        hw = make_balanced_h(c, word, geo)
        hp = Counter({int(k): n for k, n in c['local_profile'].items()}); hp[1] += 8
        checks = {d: N.replay_extended(v, hw[d], c, geo, d == 'backward', expected_profile=hp)
                  for d in ('forward', 'backward')}
        N.need(all(check['real_scalar_allowance']-base_scalar == 3504 for check in checks.values()), 'H increment3504')
        phases = N.h_child_recipes(p, ce, c, hw)
        lw = make_balanced_logger(c, word, geo)
        lp = Counter({int(k): n for k, n in c['local_profile'].items()}); lp[9] += 8
        logger_check = N.replay_extended(v, lw, c, geo, endpoint='logger', cache_count=8, expected_profile=lp)
        N.need(logger_check['real_scalar_allowance']-base_scalar == 3440, 'Logger increment3440')
        wrong = deepcopy(lw)
        omitted = next(i for i, e in enumerate(wrong) if e[0] == 'scalar' and e[1] == ['scale', ['P', 0], 1, 2])
        wrong.pop(omitted)
        control = N.replay_extended(v, wrong, c, geo, endpoint='logger', cache_count=8, allow_mismatch=True)
        dirty_gain = N.Q(1)
        for event in wrong:
            if event[0] == 'scalar' and event[1][:2] == ['scale', ['P', 0]]:
                dirty_gain *= N.Q(event[1][2], event[1][3])
        N.need(not control['exact_endpoint'] and dirty_gain == 2 and
               any(x['role'] == ['P', 0] for x in control['mismatch_examples']),
               'Missing final dirty-cache rescale exposes arbitrary P coefficient error')
        hpfile = args.out/(tag+'-BALANCED-H112-NATIVE.json.gz')
        lpfile = args.out/(tag+'-BALANCED-FORWARD-LOGGER.json.gz')
        result['providers'][tag] = dict(power_two_scan=scan,
              H=dict(artifact=hpfile.name, sha256=N.save(hpfile, hw), checks=checks, new_child_recipes=phases,
                     increment=dict(profile={'1': 8}, real_scalar_allowance=3504, owned_C_fields=1), saved_scalar_allowance=832),
              logger=dict(artifact=lpfile.name, sha256=N.save(lpfile, lw), check=logger_check,
                          increment=dict(profile={'9': 8}, real_scalar_allowance=3440, arbitrary_P_fields=8), saved_scalar_allowance=784,
                          missing_final_rescale_negative_control=dict(dirty_P0_coefficient=str(dirty_gain),
                                                                     mismatches=control['mismatch_examples'])))
        N.save(args.out/'RESULT.json', result)
        print('PASS balanced', tag, 'H8H1+3504; logger8H9+3440', flush=True)
    result['status'] = 'PASS_BALANCED_H_BOTH_DIRECTIONS_AND_FORWARD_LOGGER_ALL_FOUR_PROVIDERS'
    N.save(args.out/'RESULT.json', result)


if __name__ == '__main__':
    main()
