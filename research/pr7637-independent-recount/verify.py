#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent recount of the PR #7637 word, paid and target invoices.

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
INPUTS = HERE / 'inputs' / 'pr7637'
PR_HEAD = '32e3853b2250f1971932919cbbc01348cd8245be'
# SHA256 of the vendored bytes. They must equal the PR head blobs.
PINS = {
    'base-7633-word.json.gz':
        '49bd1b5527e5c0de1ba22101a167a66d0d7ab0fd6665569a2cb1648e71ed5ff0',
    'word-7637.json.gz':
        'd7eb204bb24b2e1b5a3e4ebc282d346a4706ddd738004929d1e9ac345085a79a',
    'invoice-7633.json':
        'f0c0fb377df557197b391a80a918da1e37d2a2ed707d1b4971d881c2c441bc3b',
    'invoice-7637.json':
        'c35c9d04c8b237b9cf384b3e8b759b67b3736d238e1cb695b462a95b7091997b',
}
# Canonical JSON digests that the READMEs of #7633 and #7637 state.
STATED = {
    'base-7633-word.json.gz':
        '4961e5e9351fa532a51eb8ff2b534bab6acd50cfd35972027cc483810cf635c3',
    'word-7637.json.gz':
        '8ab3d9dbe2e2e24202ac96c6122b010b3e7980912f935cc0cc2db2e9d85f83aa',
}
CENSUS = {'INIT': 233, 'ADD': 68049, 'SCALE': 3890, 'MOVE': 6191,
          'CLEAR': 233}
PEAK_OWNED = 50
OWNED_LABELS = 52
CALLS = 17
CLAIM = Q(37, 10000)
# The crossing of this audit is measured. The PR states only the claim.
CROSS_LO = Q('0.00370007')
CROSS_HI = Q('0.00370008')
TESTED_7633 = Q('0.00366719319432207')
KAPPA_7633 = Q('0.003667193194322')
ABOVE_7633 = Q('0.0036672')
CLAIM_7636 = Q('0.0036807241001')
BIT_CAP = Q('0.00376669')
# Native MOVE rank change per call that the PR reports. This audit measures it.
NATIVE_DELTA = {1: -13, 2: -46, 3: -7, 4: -40, 5: 4, 6: 43, 8: 1}
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
    wanted = [('#7637 at claim', new, CLAIM, 1),
              ('#7637 below measured crossing', new, CROSS_LO, 1),
              ('#7637 above measured crossing', new, CROSS_HI, -1),
              ('#7637 at #7636 claim', new, CLAIM_7636, 1),
              ('#7637 at #7633 value', new, KAPPA_7633, 1),
              ('#7637 at bit cap', new, BIT_CAP, -1),
              ('#7633 at tested point', old, TESTED_7633, 1),
              ('#7633 above its value', old, ABOVE_7633, -1),
              ('#7633 at #7637 claim', old, CLAIM, -1)]
    for label, profile, kappa, sign in wanted:
        require(sign_at(profile, kappa, logs) == sign, label + ': sign')
    require(TESTED_7633 < ABOVE_7633 < CLAIM_7636 < CLAIM < CROSS_LO
            < CROSS_HI < BIT_CAP, 'point order')
    ratio = float(CLAIM / KAPPA_7633)
    slopes = [derivative_upper(x, BIT_CAP, logs) for x in (old, new)]
    require(all(s < 0 for s in slopes), 'moment is not strictly decreasing')
    low, high = uniform_gain(old, new)
    require(low >= 0 and high > 0, 'not better for every tent tariff')
    return {'points': [label for label, _, _, _ in wanted],
            'derivative_upper_7633': float(slopes[0]),
            'derivative_upper_7637': float(slopes[1]),
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
    # 9. The #7633 invoice does not support the #7637 claim.
    control('#7633 invoice at claim',
            sign_at(signed_profile(old_inv), CLAIM, logs) == -1)
    # 10. A point above the stated bracket is not positive.
    higher = CROSS_HI + Q(1, 10 ** 12)
    control('#7637 above crossing',
            sign_at(signed_profile(new_inv), higher, logs) == -1)
    return seen


# ---------------------------------------------------------------------- main

def census(word):
    ops = collections.Counter(e[0] for e in word['program'])
    live, peak, labels = set(), 0, set()
    for e in word['program']:
        if e[0] == 'INIT':
            live.add(e[1])
            labels.add(e[1])
            peak = max(peak, len(live))
        elif e[0] == 'CLEAR':
            live.discard(e[1])
    return dict(sorted(ops.items())), peak, len(labels)


def audit(raw):
    for name, pin in PINS.items():
        require(sha(raw[name]) == pin, 'input pin ' + name)
    old = load_word(raw['base-7633-word.json.gz'])
    new = load_word(raw['word-7637.json.gz'])
    old_inv = json.loads(raw['invoice-7633.json'])
    new_inv = json.loads(raw['invoice-7637.json'])
    canon = {}
    for name, word in (('base-7633-word.json.gz', old),
                       ('word-7637.json.gz', new)):
        canon[name] = sha(json.dumps(word, sort_keys=True,
                                     separators=(',', ':')).encode())
        require(canon[name] == STATED[name], 'canonical digest ' + name)

    same = [k for k in old if k not in ('program', 'initial')]
    require(old.keys() == new.keys() and all(old[k] == new[k] for k in same),
            'word headers differ beyond initial charts')
    require(old['initial'] == new['initial'], 'initial charts changed')
    require(new['initial'][457] == 281, 'entrance of field 457')
    ops, peak, labels = census(new)
    require(ops == CENSUS and len(new['program']) == 78596, 'opcode census')
    require((peak, labels) == (PEAK_OWNED, OWNED_LABELS), 'owned census')
    report = {'canonical_word_digests': canon, 'census': ops,
              'peak_owned': peak, 'owned_labels_used': labels,
              'chronology': {'7633': chronology(old), '7637': chronology(new)}}

    h_old, h_new = move_histogram(old), move_histogram(new)
    delta = diff(h_old, h_new)
    require(delta == NATIVE_DELTA, 'native MOVE rank delta')
    require((sum(h_old.values()), sum(h_new.values())) == (6249, 6191),
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
    require(paid == [110009, 109023] and targets[0] == targets[1],
            'invoice position counts')
    require(paid[0] - paid[1] == CALLS * (6249 - 6191), 'paid saving')
    report['recount'] = {
        'law': 'rank(a->b) = dim(A+B) - dim(A meet B) over GF(2); all nested',
        'moves_7633': dict(sorted(h_old.items())),
        'moves_7637': dict(sorted(h_new.items())),
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
    report['status'] = 'PASS_INDEPENDENT_RECOUNT_PR7637_DECLARED_SCOPE'
    report['scope'] = ('Finite recount of pinned bytes at PR head ' + PR_HEAD +
                       '. Not a native, physical, compiler or outer admission.')
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except Reject as error:
        sys.exit('REJECT: %s' % error)
