#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent recount of the PR #7631 and #7633 words and invoices.

Imports no constructor, application or pricing engine from the audited PRs.
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
INPUTS = HERE / 'inputs' / 'pr7633'
HEAD_7631 = '2f1cc8c0f8c281afd2f99aeeeae6153e269f4721'
HEAD_7633 = '8b885be4a553dea375303808fdfff52ed0d71019'
# SHA256 of the vendored bytes. They must equal the PR head blobs.
PINS = {
    'word-7631-source.json.gz':
        '3b0947df9d291308279a00e009f9c1f845151b5b40f81960a53a2949cb44c9a9',
    'word-7631.json.gz':
        '736d475843e2ca53cad8a193ed582926e2659abaec40895a41d55efd4fca532f',
    'word-7633.json.gz':
        '49bd1b5527e5c0de1ba22101a167a66d0d7ab0fd6665569a2cb1648e71ed5ff0',
    'invoice-7631-source.json':
        'e9df1b46a4505848f1c03dffbaa4bda156c546bc5d3f2bce439d7052981c278f',
    'invoice-7631.json':
        'b75347941e7545ccaf50f5607f39f743f88fd1313ec3b3de7e385633cac2bd40',
    'invoice-7633.json':
        'f0c0fb377df557197b391a80a918da1e37d2a2ed707d1b4971d881c2c441bc3b',
}
# Canonical JSON digests that the README of #7633 states for its two words.
STATED = {
    'word-7631.json.gz':
        '1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e',
    'word-7633.json.gz':
        '4961e5e9351fa532a51eb8ff2b534bab6acd50cfd35972027cc483810cf635c3',
}
CALLS = 17
RANK_SURPLUS = 1424
BIT_CAP = Q('0.00376669')
K_7627 = Q('0.003665731276')
CLAIM_7631 = Q('0.003666272802')
RAW_7631 = (Q(36662728030282446501616146236939, 10 ** 34),
            Q(1833136401514122325080807311847, 5 * 10 ** 32))
CLAIM_7633 = Q(1833596597161, 500000000000000)
TESTED_7633 = Q(366719319432207, 10 ** 17)
RAW_7633 = (Q(18335965971611647646010791187619, 5 * 10 ** 33),
            Q(36671931943223295292021582375239, 10 ** 34))
# Each link: the step from an old word to a new word. The expected changes are
# the PR's statements. This audit measures them and compares.
LINKS = [
    {'name': '#7631', 'old': 'word-7631-source.json.gz',
     'new': 'word-7631.json.gz', 'old_inv': 'invoice-7631-source.json',
     'new_inv': 'invoice-7631.json', 'rebirth': {},
     'native_delta': {2: -1, 3: -1, 5: 1}, 'helper_delta': {},
     'moves': (6251, 6250), 'paid': (110043, 110026),
     'claim': CLAIM_7631, 'bracket': RAW_7631,
     'points': [('#7631 at claim', 'new', CLAIM_7631, 1),
                ('#7631 at lower bracket', 'new', RAW_7631[0], 1),
                ('#7631 at upper bracket', 'new', RAW_7631[1], -1),
                ('#7627 value, source', 'old', K_7627, 1),
                ('#7627 value, #7631', 'new', K_7627, 1),
                ('source at #7631 claim', 'old', CLAIM_7631, -1)]},
    {'name': '#7633', 'old': 'word-7631.json.gz',
     'new': 'word-7633.json.gz', 'old_inv': 'invoice-7631.json',
     'new_inv': 'invoice-7633.json', 'rebirth': {457: (3, 281)},
     'native_delta': {3: -1}, 'helper_delta': {6: 1, 9: -1},
     'moves': (6250, 6249), 'paid': (110026, 110009),
     'claim': CLAIM_7633, 'bracket': RAW_7633,
     'points': [('#7633 at claim', 'new', CLAIM_7633, 1),
                ('#7633 at tested point', 'new', TESTED_7633, 1),
                ('#7633 at lower bracket', 'new', RAW_7633[0], 1),
                ('#7633 at upper bracket', 'new', RAW_7633[1], -1),
                ('#7631 at its lower bracket', 'old', RAW_7631[0], 1),
                ('#7631 at its upper bracket', 'old', RAW_7631[1], -1),
                ('#7631 at #7633 claim', 'old', CLAIM_7633, -1),
                ('#7633 at #7631 claim', 'new', CLAIM_7631, 1)]},
]


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




# ------------------------------------------------------------------ moments

def check_moments(link, old_inv, new_inv):
    invs = {'old': old_inv, 'new': new_inv}
    for inv in invs.values():
        model = inv['contract']['model']
        require(model == 'mixed-target-unnormalized-power-v1', 'invoice model')
    old, new = signed_profile(old_inv), signed_profile(new_inv)
    profiles = {'old': old, 'new': new}
    logs = log_table(max(max(old), max(new)))
    for profile in profiles.values():
        lo, hi = moment_bounds(profile, Q(0), logs)
        exact = sum(r * s for r, s in profile.items())
        tight = hi - lo < Q(1, 1 << 200)
        require(lo <= exact <= hi and tight, 'engine self-test')
        require(exact == RANK_SURPLUS, 'rank surplus')
    require(link['bracket'][0] < link['bracket'][1] < BIT_CAP, 'bracket order')
    for label, which, kappa, sign in link['points']:
        require(sign_at(profiles[which], kappa, logs) == sign, label + ': sign')
    slopes = [derivative_upper(x, BIT_CAP, logs) for x in (old, new)]
    require(all(s < 0 for s in slopes), 'moment is not strictly decreasing')
    low, high = uniform_gain(old, new)
    require(low >= 0 and high > 0, 'not better for every tent tariff')
    return {'points': [label for label, _, _, _ in link['points']],
            'derivative_upper_old': float(slopes[0]),
            'derivative_upper_new': float(slopes[1]),
            'tent_gain_min_max': [low, high]}, logs


# ------------------------------------------------------------------ controls

def rejects(fn, *args):
    try:
        fn(*args)
    except Reject:
        return True
    return False


def controls(link, old, new, old_inv, new_inv, logs):
    seen = []

    def control(name, ok):
        require(ok, 'control did not reject: ' + name)
        seen.append(name)

    h_old, h_new = move_histogram(old), move_histogram(new)
    k_old, k_new = caller_part(h_old, old_inv), caller_part(h_new, new_inv)
    t_new = target_rest(helper_targets(new), new_inv)
    wrong = growth_only_histogram(new)
    control('growth-only rank law',
            rejects(caller_part, wrong, new_inv)
            or caller_part(wrong, new_inv) != k_new)
    bad = copy.deepcopy(new_inv)
    bad['paid']['1'] += 1
    control('invoice paid unit', caller_part(h_new, bad) != k_new)
    control('old word with new invoice',
            rejects(caller_part, h_old, new_inv)
            or caller_part(h_old, new_inv) != k_old)
    if link['helper_delta']:
        control('old helper targets with new invoice',
                rejects(target_rest, helper_targets(old), new_inv)
                or target_rest(helper_targets(old), new_inv) != t_new)
        field, (before, _) = sorted(link['rebirth'].items())[0]
        bad = copy.deepcopy(new)
        bad['initial'][field] = before
        control('rebirth undone', rejects(chronology, bad))
    index = next(i for i, e in enumerate(new['program']) if e[0] == 'ADD')
    bad = copy.deepcopy(new)
    bad['program'][index][4] += 1
    control('ADD at the wrong chart', rejects(chronology, bad))
    index = next(i for i, e in enumerate(new['program']) if e[0] == 'MOVE')
    bad = copy.deepcopy(new)
    event = bad['program'][index]
    event[3] = (event[3] + 1) % len(bad['frames'])
    control('MOVE to another chart', rejects(chronology, bad))
    move = next(e for e in new['program'] if e[0] == 'MOVE')
    bad = copy.deepcopy(new)
    bad['frames'][move[3]] = bad['frames'][move[3]] + [1 << 20]
    control('changed frame',
            rejects(move_histogram, bad)
            or caller_part(move_histogram(bad), new_inv) != k_new)
    control('old invoice at the new claim',
            sign_at(signed_profile(old_inv), link['claim'], logs) == -1)
    higher = link['bracket'][1] + Q(1, 10 ** 12)
    control('new invoice above bracket',
            sign_at(signed_profile(new_inv), higher, logs) == -1)
    return seen


# ---------------------------------------------------------------------- main

def recount(link, words, invs):
    old, new = words[link['old']], words[link['new']]
    old_inv, new_inv = invs[link['old_inv']], invs[link['new_inv']]
    same = [k for k in old if k not in ('program', 'initial')]
    require(old.keys() == new.keys() and all(old[k] == new[k] for k in same),
            'word headers differ beyond initial charts')
    changed = {r: (a, b) for r, (a, b) in
               enumerate(zip(old['initial'], new['initial'])) if a != b}
    require(changed == link['rebirth'], 'initial charts')
    events = [chronology(old)['events'], chronology(new)['events']]
    h_old, h_new = move_histogram(old), move_histogram(new)
    delta = diff(h_old, h_new)
    require(delta == link['native_delta'], 'native MOVE rank delta')
    require((sum(h_old.values()), sum(h_new.values())) == link['moves'],
            'native MOVE count')
    k_old, k_new = caller_part(h_old, old_inv), caller_part(h_new, new_inv)
    require(k_old == k_new, 'caller part of the paid profile changed')
    ht_old, ht_new = helper_targets(old), helper_targets(new)
    hdelta = diff(ht_old, ht_new)
    require(hdelta == link['helper_delta'], 'helper target delta')
    tk_old = target_rest(ht_old, old_inv)
    tk_new = target_rest(ht_new, new_inv)
    require(tk_old == tk_new, 'caller part of the target profile changed')
    paid = [sum(x['paid'].values()) for x in (old_inv, new_inv)]
    targets = [sum(x['targets'].values()) for x in (old_inv, new_inv)]
    require(tuple(paid) == link['paid'] and targets[0] == targets[1],
            'invoice position counts')
    return {'events': events, 'native_delta_per_call': delta,
            'helper_delta_per_call': hdelta, 'paid_positions': paid,
            'target_positions': targets,
            'initial_changes': {str(r): list(v) for r, v in changed.items()},
            'moves': [dict(sorted(h_old.items())),
                      dict(sorted(h_new.items()))]}, (k_new, tk_new)


def audit(raw):
    for name, pin in PINS.items():
        require(sha(raw[name]) == pin, 'input pin ' + name)
    words, canon = {}, {}
    for name in PINS:
        if name.startswith('word-'):
            words[name] = load_word(raw[name])
            canon[name] = sha(json.dumps(words[name], sort_keys=True,
                                         separators=(',', ':')).encode())
    for name, digest in STATED.items():
        require(canon[name] == digest, 'canonical digest ' + name)
    invs = {n: json.loads(raw[n]) for n in PINS if n.startswith('invoice-')}
    report = {'canonical_word_digests': canon, 'links': {}}
    callers = []
    for link in LINKS:
        entry, callers_of = recount(link, words, invs)
        moments, logs = check_moments(link, invs[link['old_inv']],
                                      invs[link['new_inv']])
        entry['moments'] = moments
        entry['controls'] = controls(
            link, words[link['old']], words[link['new']],
            invs[link['old_inv']], invs[link['new_inv']], logs)
        report['links'][link['name']] = entry
        callers.append(callers_of)
    require(all(c == callers[0] for c in callers), 'caller parts differ')
    report['caller_paid_part'] = callers[0][0]
    report['caller_target_part'] = callers[0][1]
    report['law'] = ('rank(a->b) = dim(A+B) - dim(A meet B) over GF(2); '
                     'all nested; paid = 17 H(word) + K; targets = 17 T(word) '
                     '+ K_T')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    raw = {name: (INPUTS / name).read_bytes() for name in PINS}
    report = audit(raw)
    report['status'] = 'PASS_INDEPENDENT_RECOUNT_PR7631_PR7633_DECLARED_SCOPE'
    report['scope'] = ('Finite recount of pinned bytes at PR heads ' +
                       HEAD_7631 + ' (#7631) and ' + HEAD_7633 + ' (#7633). '
                       'Not a native, physical, compiler or outer admission.')
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except Reject as error:
        sys.exit('REJECT: %s' % error)
