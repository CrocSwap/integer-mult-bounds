#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent recount of the PR #7636 word, paid and target invoices.

Imports no constructor, application or pricing engine from the audited PR.
Scope: finite checks on pinned bytes. Not a supplier admission.
"""
import argparse
import collections
import copy
import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).absolute().parent
INPUTS = HERE / 'inputs' / 'pr7636'
PR_HEAD = '7e68d8dd62d9a38c0f3c942262a7a85ca7125b75'
# SHA256 of the vendored bytes. They must equal the PR head blobs.
PINS = {
    'base-7630-word.json.gz':
        'fa1a8dad12d28e6e5ced5a6989d49074efe15d6647ffc122cb28fcd666f366c2',
    'word-7636.json.gz':
        '1b4e33c3e3b69d1f1b42d019a2e372ac612fa28494bd8da18a734618f9bda659',
    'invoice-7630.json':
        '887128e79be28ded1a8a62fc6311ccaa975e5bcf9b7868dbcc5c8bdceaa6e9d4',
    'invoice-7636.json':
        '18adee673515c4ece7208b53c7cc17a2e121843d55f62067d2e43e341872f0d5',
}
CALLS = 17
CLAIM = Q('0.0036807241001')
UPPER = Q('0.0036807241002')
# Exact crossing that the PR states, to 32 digits.
CROSSING = Q('0.00368072410014727862067955898005')
CROSS_EPS = Q(1, 10 ** 30)
CLAIM_7630 = Q('0.0036667343458')
ABOVE_7630 = Q('0.0036667343459')
KAPPA_7633 = Q('0.003667193194322')
KAPPA_7627 = Q('0.003665731276')
BIT_CAP = Q('0.00376669')
# Native MOVE rank change per call that the PR reports. This audit measures it.
NATIVE_DELTA = {2: -18, 3: -6, 4: -20, 6: 20, 7: 2}
HELPER_DELTA = {}
RANK_SURPLUS = 1424


class Reject(Exception):
    pass


def require(ok, message):
    if not ok:
        raise Reject(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_word(raw):
    return json.loads(gzip.decompress(raw))


# ---------------------------------------------------------------- GF(2) ranks

def gf2_rank(vectors):
    basis = {}
    for v in vectors:
        while v:
            top = v.bit_length() - 1
            if top not in basis:
                basis[top] = v
                break
            v ^= basis[top]
    return len(basis)


def move_rank(frames, a, b):
    """Rank dim(A+B) - dim(A meet B), and whether the two frames are nested."""
    ra, rb = gf2_rank(frames[a]), gf2_rank(frames[b])
    ru = gf2_rank(frames[a] + frames[b])
    return 2 * ru - ra - rb, ru == max(ra, rb)


def move_histogram(word):
    frames = word['frames']
    hist = collections.Counter()
    for e in word['program']:
        if e[0] == 'MOVE':
            r, nested = move_rank(frames, e[2], e[3])
            require(nested, 'a MOVE joins two frames that are not nested')
            require(r > 0, 'a MOVE has rank zero')
            hist[r] += 1
    return hist


def growth_only_histogram(word):
    # Wrong law for the negative control: charge only dim(A+B) - dim(A).
    frames = word['frames']
    hist = collections.Counter()
    for e in word['program']:
        if e[0] == 'MOVE':
            r = gf2_rank(frames[e[2]] + frames[e[3]]) - gf2_rank(frames[e[2]])
            if r:
                hist[r] += 1
    return hist


def caller_part(word_hist, invoice):
    paid = {int(r): n for r, n in invoice['paid'].items()}
    rest = collections.Counter(paid)
    for r, n in word_hist.items():
        rest[r] -= CALLS * n
    require(all(n >= 0 for n in rest.values()), 'paid is below the word count')
    return {r: n for r, n in sorted(rest.items()) if n}


# ------------------------------------------------------- chart chronology

def chronology(word):
    """Follow the chart of each field through the complete program."""
    require(len(word['initial']) == word['public'] == len(word['final']),
            'public field header')
    chart = dict(enumerate(word['initial']))
    owned = set()
    nframes = len(word['frames'])
    for i, e in enumerate(word['program']):
        op = e[0]
        where = '%s at event %d' % (op, i)
        if op == 'MOVE':
            require(len(e) == 5 and e[2] != e[3] and 0 <= e[3] < nframes, where)
            require(chart.get(e[1]) == e[2], where + ': source chart')
            require(e[4] is (e[1] in owned), where + ': owner flag')
            chart[e[1]] = e[3]
        elif op in ('ADD', 'COPY'):
            require(len(e) == 5 and e[1] != e[2], where)
            require(chart.get(e[1]) == e[4] == chart.get(e[2]),
                    where + ': operands are not at the stated chart')
        elif op == 'SCALE':
            require(len(e) == 4 and chart.get(e[1]) == e[3], where + ': chart')
        elif op == 'INIT':
            require(len(e) == 3 and e[1] not in chart, where + ': live field')
            require(e[1] >= word['public'], where + ': public field')
            chart[e[1]] = e[2]
            owned.add(e[1])
        elif op == 'CLEAR':
            require(len(e) == 3 and e[1] in owned, where + ': not owned')
            require(chart[e[1]] == e[2], where + ': chart')
            del chart[e[1]]
            owned.remove(e[1])
        else:
            raise Reject(where + ': unknown opcode')
    require(not owned, 'an owned field stays live at the end')
    require([chart[f] for f in range(word['public'])] == word['final'],
            'final charts')
    return {'events': len(word['program']), 'fields': len(chart)}


# ------------------------------------------- exact interval moment engine

BITS = 256
ONE = 1 << BITS


def _atanh_inv(q):
    """Integer bounds of atanh(1/q) * 2^BITS for an integer q >= 3."""
    lo = hi = 0
    j = 0
    while True:
        den = (2 * j + 1) * q ** (2 * j + 1)
        lo += ONE // den
        hi += -(-ONE // den)
        j += 1
        if den > ONE:
            break
    # Tail < next_term / (1 - q^-2) <= 2 * next_term, and next_term < 1 ulp.
    return lo, hi + 2


def log_table(top):
    """ln(n) bounds from ln(n) = ln(n-1) + 2 atanh(1/(2n-1))."""
    table = {1: (0, 0)}
    for n in range(2, top + 1):
        a, b = _atanh_inv(2 * n - 1)
        table[n] = (table[n - 1][0] + 2 * a, table[n - 1][1] + 2 * b)
    return table


def _exp_bounds(y_lo, y_hi):
    """Bounds of exp(y) * 2^BITS for 0 <= y < 8, y scaled by 2^BITS."""
    require(0 <= y_lo <= y_hi < 8 * ONE, 'exp domain')
    lo, term = ONE, ONE
    n = 0
    while term:
        n += 1
        term = term * y_lo // (n * ONE)
        lo += term
    hi, term = ONE, ONE
    n = 0
    while n < 32 or term > 1:
        n += 1
        term = -(-term * y_hi // (n * ONE))
        hi += term
    # n >= 32 > 2 * y_hi, so the tail is below the last term, which is <= 1.
    return lo, hi + 2


def moment_bounds(signed, kappa, logs):
    """Bounds of sum_r signed[r] * r^(1-kappa), as exact rationals."""
    p = 1 - kappa
    require(0 < p <= 1, 'exponent domain')
    lo = hi = 0
    for r, s in signed.items():
        l_lo, l_hi = logs[r]
        y_lo = l_lo * p.numerator // p.denominator
        y_hi = -(-l_hi * p.numerator // p.denominator)
        e_lo, e_hi = _exp_bounds(y_lo, y_hi)
        lo += s * (e_lo if s > 0 else e_hi)
        hi += s * (e_hi if s > 0 else e_lo)
    return Q(lo, ONE), Q(hi, ONE)


def derivative_upper(signed, cap, logs):
    """Upper bound of d/dkappa of the moment on the interval [0, cap]."""
    total = 0
    for r, s in signed.items():
        if r == 1 or s == 0:
            continue
        l_lo, l_hi = logs[r]
        if s > 0:
            # -s ln(r) r^(1-kappa) is largest at kappa = cap.
            e_lo = moment_bounds({r: 1}, cap, logs)[0]
            total -= s * Q(l_lo, ONE) * e_lo
        else:
            # |s| ln(r) r^(1-kappa) is largest at kappa = 0.
            total += -s * Q(l_hi, ONE) * r
    return total


def signed_profile(invoice):
    out = collections.Counter()
    for r, n in invoice['targets'].items():
        out[int(r)] += n
    for r, n in invoice['paid'].items():
        out[int(r)] -= n
    return {r: s for r, s in out.items() if s}


def sign_at(signed, kappa, logs):
    lo, hi = moment_bounds(signed, kappa, logs)
    require(lo > 0 or hi < 0, 'moment sign is not resolved')
    return 1 if lo > 0 else -1




# ------------------------------------------------------------- recounts

def diff(a, b):
    d = collections.Counter(b)
    d.subtract(a)
    return {k: v for k, v in sorted(d.items()) if v}


def mains(word):
    """Main fields as the PR defines them. Other public fields are helpers."""
    live = set(word['live'])
    hosted = word['hosted']
    shifted = {r + 112 for r in live}
    return live | shifted | set(hosted['X2']) | set(hosted['Y2'])


def helper_targets(word):
    """Per call: rank(final frame) - rank(initial frame), for each helper."""
    ranks = [gf2_rank(f) for f in word['frames']]
    main = mains(word)
    out = collections.Counter()
    for r in range(word['public']):
        if r not in main:
            d = ranks[word['final'][r]] - ranks[word['initial'][r]]
            require(d > 0, 'helper %d has no productive rank' % r)
            out[d] += 1
    return out


def target_rest(helpers, invoice):
    """Targets left after the helpers of all calls. Word-independent."""
    rest = collections.Counter(
        {int(r): n for r, n in invoice['targets'].items()})
    for r, n in helpers.items():
        rest[r] -= CALLS * n
    require(all(n >= 0 for n in rest.values()), 'targets are below the count')
    return {r: n for r, n in sorted(rest.items()) if n}


def uniform_gain(old_s, new_s):
    """Smallest and largest gain over the tents min(r, a), a = 1 .. max rank."""
    d = collections.Counter(new_s)
    d.subtract(old_s)
    top = max(max(old_s), max(new_s))
    gains = [sum(s * min(r, a) for r, s in d.items())
             for a in range(1, top + 1)]
    return min(gains), max(gains)


def check_moments(old_inv, new_inv):
    for inv in (old_inv, new_inv):
        model = inv['contract']['model']
        require(model == 'mixed-target-unnormalized-power-v1', 'invoice model')
    old, new = signed_profile(old_inv), signed_profile(new_inv)
    logs = log_table(max(max(old), max(new)))
    for profile in (old, new):
        lo, hi = moment_bounds(profile, Q(0), logs)
        exact = sum(r * s for r, s in profile.items())
        tight = hi - lo < Q(1, 1 << 200)
        require(lo <= exact <= hi and tight, 'engine self-test')
        require(exact == RANK_SURPLUS, 'rank surplus')
    wanted = [('#7636 at claim', new, CLAIM, 1),
              ('#7636 at upper bracket', new, UPPER, -1),
              ('#7636 below crossing', new, CROSSING - CROSS_EPS, 1),
              ('#7636 above crossing', new, CROSSING + CROSS_EPS, -1),
              ('#7636 at #7633 value', new, KAPPA_7633, 1),
              ('#7636 at #7630 claim', new, CLAIM_7630, 1),
              ('#7636 at #7627 value', new, KAPPA_7627, 1),
              ('#7630 at its claim', old, CLAIM_7630, 1),
              ('#7630 above its claim', old, ABOVE_7630, -1),
              ('#7630 at #7636 claim', old, CLAIM, -1)]
    for label, profile, kappa, sign in wanted:
        require(sign_at(profile, kappa, logs) == sign, label + ': sign')
    require(KAPPA_7627 < CLAIM_7630 < ABOVE_7630 < KAPPA_7633 < CLAIM
            < CROSSING < UPPER < BIT_CAP, 'point order')
    ratio = float(CLAIM / KAPPA_7633)
    require(round(ratio, 8) == 1.00368972, 'ratio over #7633')
    slopes = [derivative_upper(x, BIT_CAP, logs) for x in (old, new)]
    require(all(s < 0 for s in slopes), 'moment is not strictly decreasing')
    low, high = uniform_gain(old, new)
    require(low >= 0 and high > 0, 'not better for every tent tariff')
    return {'points': [label for label, _, _, _ in wanted],
            'derivative_upper_7630': float(slopes[0]),
            'derivative_upper_7636': float(slopes[1]),
            'tent_gain_min_max': [low, high],
            'ratio_over_7633': ratio, 'interval': ['0', str(BIT_CAP)],
            'engine_bits': BITS}, logs


# ------------------------------------------------------------------ controls

def rejects(fn, *args):
    try:
        fn(*args)
    except Reject:
        return True
    return False


def controls(old, new, old_inv, new_inv, logs):
    seen = []

    def control(name, ok):
        require(ok, 'control did not reject: ' + name)
        seen.append(name)

    h_old, h_new = move_histogram(old), move_histogram(new)
    k_old, k_new = caller_part(h_old, old_inv), caller_part(h_new, new_inv)
    # 1. A rank law that charges only frame growth does not fit the invoice.
    wrong = growth_only_histogram(new)
    control('growth-only rank law',
            rejects(caller_part, wrong, new_inv)
            or caller_part(wrong, new_inv) != k_new)
    # 2. One more paid unit in the invoice.
    bad = copy.deepcopy(new_inv)
    bad['paid']['1'] += 1
    control('invoice paid unit', caller_part(h_new, bad) != k_new)
    # 3. The new invoice with the old word.
    control('old word with new invoice',
            rejects(caller_part, h_old, new_inv)
            or caller_part(h_old, new_inv) != k_old)
    # 4. A dropped MOVE breaks the chart chronology.
    index = next(i for i, e in enumerate(new['program']) if e[0] == 'MOVE')
    bad = copy.deepcopy(new)
    del bad['program'][index]
    control('dropped MOVE', rejects(chronology, bad))
    # 5. A changed initial chart breaks the chart chronology.
    bad = copy.deepcopy(new)
    bad['initial'][457] += 1
    control('changed initial chart', rejects(chronology, bad))
    # 6. An ADD at the wrong chart.
    index = next(i for i, e in enumerate(new['program']) if e[0] == 'ADD')
    bad = copy.deepcopy(new)
    bad['program'][index][4] += 1
    control('ADD at the wrong chart', rejects(chronology, bad))
    # 7. A MOVE that lands on another chart.
    index = next(i for i, e in enumerate(new['program']) if e[0] == 'MOVE')
    bad = copy.deepcopy(new)
    event = bad['program'][index]
    event[3] = (event[3] + 1) % len(bad['frames'])
    control('MOVE to another chart', rejects(chronology, bad))
    # 8. A frame vector change breaks nestedness or the paid count.
    move = next(e for e in new['program'] if e[0] == 'MOVE')
    bad = copy.deepcopy(new)
    bad['frames'][move[3]] = bad['frames'][move[3]] + [1 << 20]
    control('changed frame',
            rejects(move_histogram, bad)
            or caller_part(move_histogram(bad), new_inv) != k_new)
    # 9. The #7630 invoice does not support the #7636 claim.
    control('#7630 invoice at claim',
            sign_at(signed_profile(old_inv), CLAIM, logs) == -1)
    # 10. A point above the stated bracket is not positive.
    higher = UPPER + Q(1, 10 ** 12)
    control('#7636 above bracket',
            sign_at(signed_profile(new_inv), higher, logs) == -1)
    return seen


# ---------------------------------------------------------------------- main

def audit(raw):
    for name, pin in PINS.items():
        require(sha(raw[name]) == pin, 'input pin ' + name)
    old = load_word(raw['base-7630-word.json.gz'])
    new = load_word(raw['word-7636.json.gz'])
    old_inv = json.loads(raw['invoice-7630.json'])
    new_inv = json.loads(raw['invoice-7636.json'])

    same = [k for k in old if k not in ('program', 'initial')]
    require(old.keys() == new.keys() and all(old[k] == new[k] for k in same),
            'word headers differ beyond initial charts')
    require(old['initial'] == new['initial'], 'initial charts changed')
    report = {'chronology': {'7630': chronology(old), '7636': chronology(new)}}

    h_old, h_new = move_histogram(old), move_histogram(new)
    delta = diff(h_old, h_new)
    require(delta == NATIVE_DELTA, 'native MOVE rank delta')
    require((sum(h_old.values()), sum(h_new.values())) == (6250, 6228),
            'native MOVE count')
    require(sum(r * n for r, n in delta.items()) == 0, 'total MOVE rank')
    k_old, k_new = caller_part(h_old, old_inv), caller_part(h_new, new_inv)
    require(k_old == k_new, 'caller part of the paid profile changed')
    ht_old, ht_new = helper_targets(old), helper_targets(new)
    hdelta = diff(ht_old, ht_new)
    require(hdelta == HELPER_DELTA, 'helper target delta')
    tk_old, tk_new = target_rest(ht_old, old_inv), target_rest(ht_new, new_inv)
    require(tk_old == tk_new, 'caller part of the target profile changed')
    paid = [sum(x['paid'].values()) for x in (old_inv, new_inv)]
    targets = [sum(x['targets'].values()) for x in (old_inv, new_inv)]
    require(paid == [110026, 109652] and targets[0] == targets[1],
            'invoice position counts')
    require(paid[0] - paid[1] == CALLS * (6250 - 6228), 'paid saving')
    report['recount'] = {
        'law': 'rank(a->b) = dim(A+B) - dim(A meet B) over GF(2); all nested',
        'moves_7630': dict(sorted(h_old.items())),
        'moves_7636': dict(sorted(h_new.items())),
        'native_delta_per_call': delta, 'helper_delta_per_call': hdelta,
        'calls': CALLS, 'caller_paid_part': k_new,
        'caller_target_part': tk_new, 'paid_positions': paid,
        'target_positions': targets}
    report['moments'], logs = check_moments(old_inv, new_inv)
    report['controls'] = controls(old, new, old_inv, new_inv, logs)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    raw = {name: (INPUTS / name).read_bytes() for name in PINS}
    report = audit(raw)
    report['status'] = 'PASS_INDEPENDENT_RECOUNT_PR7636_DECLARED_SCOPE'
    report['scope'] = ('Finite recount of pinned bytes at PR head ' + PR_HEAD +
                       '. Not a native, physical, compiler or outer admission.')
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except Reject as error:
        sys.exit('REJECT: %s' % error)
