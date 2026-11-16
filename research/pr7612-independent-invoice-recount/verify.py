#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent recount of the PR #7612 word, paid invoice and moment signs.

Imports no constructor, application or pricing engine from the audited PR.
Scope: finite checks on pinned bytes. Not a supplier admission.
"""
import argparse
import collections
import copy
import gzip
import hashlib
import json
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).absolute().parent
INPUTS = HERE / 'inputs' / 'pr7612'
PR_HEAD = 'e814828ee5b869c9468282d57ba28c364b07d130'
PR_ROOT = 'research/p104-contact134-329-on7611'
# SHA256 of the vendored bytes. They must equal the PR head blobs.
PINS = {
    'word-7612.json.gz': '92a3b664c99e5a8d52771f3d682af6b34dead3df3498eeb58d4f437873db33d6',
    'word-7611.json.gz': 'cb8c33817afbf7863074af90e3d287d1ef48c45a761f653143947ce2f58db1b6',
    'invoice-7612.json': 'c34cea264b96ad495401064bee801de6bea6509372770daec6e8bb3053b3d883',
    'invoice-7611.json': '3e02c92a82e403154a33dc4ad7cc7b49e3add55ec9a1f8db330b3ac32007ccbb',
}
# Canonical JSON digests that PROOF.md of the PR states for the two words.
CANONICAL = {
    'word-7612.json.gz': 'ff380ae02b238bdf41db5247a2278f7e7be391fe49879f91950fdb775a0f983a',
    'word-7611.json.gz': '177b74c42ac633aaee21b0bbd5373441ccba8e5bad029d827877cf2d585fd0e3',
}
CALLS = 17
# Word-independent caller part of the paid histogram. This audit measures it.
CALLER = {1: 384, 8: 656, 9: 32, 16: 416, 24: 416, 32: 416, 40: 416,
          48: 416, 56: 416, 64: 208}
NATIVE_DELTA = {1: -2, 2: 2, 3: -1, 4: -1, 5: 1}
CLAIM = Q('0.003652740309')
TESTED = Q('0.003652740309007')
NEW_LO = Q(6128281319, 1677721600000)
NEW_HI = Q(153207033, 41943040000)
OLD_HI = CLAIM - Q(20741937499, 65536000000000000)
BIT_CAP = Q('0.00376669')
LINEAGE = {
    7604: ('retained/pr7605/retained/pr7604/word.json.gz',
           'retained/pr7605/retained/pr7604/invoice-new.json'),
    7605: ('retained/pr7605/data/word.json.gz',
           'retained/pr7605/data/invoice-new.json'),
    7608: ('retained/pr7608/data/word.json.gz',
           'retained/pr7608/data/invoice-new.json'),
}


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


# ------------------------------------------------------------ edit recount

def edit_script(old, new):
    """Positions where the programs differ, found without the PR literals."""
    p, q = old['program'], new['program']
    require(all(old[k] == new[k] for k in old if k != 'program')
            and old.keys() == new.keys(), 'word headers differ')
    require(len(q) == len(p) - 1, 'event count')
    first = next(i for i in range(len(q)) if p[i] != q[i])
    # A dropped event leaves p[d+1:] aligned with q[d:] up to substitutions.
    # Accept only substitutions that keep the opcode and the acted field.
    found = []
    for d in range(first, min(first + 8, len(p))):
        aligned = p[:d] + p[d + 1:]
        changes = [(i if i < d else i + 1, x, y)
                   for i, (x, y) in enumerate(zip(aligned, q)) if x != y]
        if len(changes) <= 8 and all(x[:2] == y[:2] for _, x, y in changes):
            found.append((d, changes))
    require(len(found) == 1, 'no unique dropped event explains the edit')
    return found[0]


def check_edit(old, new):
    drop, changes = edit_script(old, new)
    p = old['program']
    require(p[drop][0] == 'MOVE' and not p[drop][4], 'dropped event')
    fields = {p[drop][1]} | {x[1] for _, x, _ in changes}
    require(fields == {134, 329}, 'edited fields')
    for i, x, y in changes:
        require(x[0] == y[0] and x[1] == y[1], 'opcode or field changed')
        if x[0] == 'MOVE':
            require(x[4] is False and y[4] is False, 'owned MOVE changed')
            require(x[2] == y[2] or x[3] == y[3], 'both MOVE charts changed')
        else:
            require(x[0] == 'ADD' and x[:4] == y[:4], 'scalar content changed')
    frames = old['frames']
    before = sorted(move_rank(frames, e[2], e[3])[0]
                    for e in [p[drop]] + [x for _, x, _ in changes]
                    if e[0] == 'MOVE')
    after = sorted(move_rank(frames, y[2], y[3])[0]
                   for _, _, y in changes if y[0] == 'MOVE')
    require(before == [1, 1, 3, 4] and after == [2, 2, 5], 'incident ranks')
    return {'dropped_index': drop, 'dropped': p[drop],
            'substituted_indices': [i for i, _, _ in changes],
            'ranks_before': before, 'ranks_after': after}


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


def check_moments(old_inv, new_inv):
    for inv in (old_inv, new_inv):
        require(inv['contract']['model'] == 'mixed-target-unnormalized-power-v1',
                'invoice model')
    old, new = signed_profile(old_inv), signed_profile(new_inv)
    logs = log_table(max(max(old), max(new)))
    # Self-test of the engine against exact integer powers at kappa = 0.
    lo, hi = moment_bounds(new, Q(0), logs)
    exact = sum(r * s for r, s in new.items())
    require(lo <= exact <= hi and hi - lo < Q(1, 1 << 200), 'engine self-test')
    require(exact == 1424, 'rank surplus')
    wanted = [('candidate at claim', new, CLAIM, 1),
              ('candidate at tested point', new, TESTED, 1),
              ('candidate at stated lower bracket', new, NEW_LO, 1),
              ('candidate at stated upper bracket', new, NEW_HI, -1),
              ('candidate at #7611 raw upper', new, OLD_HI, 1),
              ('#7611 at claim', old, CLAIM, -1),
              ('#7611 at its raw upper', old, OLD_HI, -1)]
    for label, profile, kappa, sign in wanted:
        require(sign_at(profile, kappa, logs) == sign, label + ': sign')
    require(OLD_HI < CLAIM < TESTED < NEW_LO < NEW_HI < BIT_CAP, 'point order')
    slopes = [derivative_upper(x, BIT_CAP, logs) for x in (old, new)]
    require(all(s < 0 for s in slopes), 'moment is not strictly decreasing')
    return {'points': [label for label, _, _, _ in wanted],
            'derivative_upper_7611': float(slopes[0]),
            'derivative_upper_7612': float(slopes[1]),
            'interval': ['0', str(BIT_CAP)], 'engine_bits': BITS}, logs


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

    hist = move_histogram(new)
    drop, changes = edit_script(old, new)
    # 1. A rank law that charges only frame growth does not fit the invoice.
    wrong = growth_only_histogram(new)
    control('growth-only rank law',
            rejects(caller_part, wrong, new_inv)
            or caller_part(wrong, new_inv) != CALLER)
    # 2. One more paid unit in the invoice.
    bad = copy.deepcopy(new_inv)
    bad['paid']['1'] += 1
    control('invoice paid unit', caller_part(hist, bad) != CALLER)
    # 3. The candidate invoice with the old word.
    control('old word with new invoice',
            rejects(caller_part, move_histogram(old), new_inv)
            or caller_part(move_histogram(old), new_inv) != CALLER)
    # 4. The edited ADD stays at the old contact chart.
    index, x, _ = next(c for c in changes if c[1][0] == 'ADD')
    bad = copy.deepcopy(new)
    bad['program'][index - 1] = x
    control('ADD at the old contact chart', rejects(chronology, bad))
    # 5. The dropped MOVE returns without the other substitutions.
    bad = copy.deepcopy(new)
    bad['program'].insert(drop, old['program'][drop])
    control('dropped MOVE restored', rejects(chronology, bad))
    # 6. A changed MOVE loses its restoration chart.
    index, _, y = [c for c in changes if c[1][0] == 'MOVE'][-1]
    bad = copy.deepcopy(new)
    bad['program'][index - 1] = y[:3] + [y[3] + 1, y[4]]
    control('wrong restoration chart', rejects(chronology, bad))
    # 7. A frame vector change breaks nestedness or the paid count.
    bad = copy.deepcopy(new)
    bad['frames'][373] = [30, 320]
    control('changed frame 373',
            rejects(move_histogram, bad)
            or caller_part(move_histogram(bad), new_inv) != CALLER)
    # 8. The #7611 invoice does not support the claim.
    control('#7611 invoice at claim',
            sign_at(signed_profile(old_inv), CLAIM, logs) == -1)
    # 9. A point above the stated upper bracket is not positive.
    control('candidate above bracket',
            sign_at(signed_profile(new_inv), NEW_HI + Q(1, 10 ** 12), logs) == -1)
    return seen


# ---------------------------------------------------------------------- main

def audit(raw):
    for name, pin in PINS.items():
        require(sha(raw[name]) == pin, 'input pin ' + name)
    new, old = load_word(raw['word-7612.json.gz']), load_word(raw['word-7611.json.gz'])
    for name, word in (('word-7612.json.gz', new), ('word-7611.json.gz', old)):
        canon = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
        require(sha(canon) == CANONICAL[name], 'canonical digest ' + name)
    new_inv = json.loads(raw['invoice-7612.json'])
    old_inv = json.loads(raw['invoice-7611.json'])

    report = {'edit': check_edit(old, new)}
    report['chronology'] = {'7611': chronology(old), '7612': chronology(new)}
    h_old, h_new = move_histogram(old), move_histogram(new)
    delta = {r: h_new[r] - h_old[r] for r in sorted(set(h_old) | set(h_new))
             if h_new[r] != h_old[r]}
    require(delta == NATIVE_DELTA, 'native MOVE rank delta')
    require(caller_part(h_old, old_inv) == CALLER, '#7611 caller part')
    require(caller_part(h_new, new_inv) == CALLER, '#7612 caller part')
    require(old_inv['targets'] == new_inv['targets'], 'targets changed')
    paid_old, paid_new = (sum(x['paid'].values()) for x in (old_inv, new_inv))
    require((paid_old, paid_new) == (110281, 110264), 'paid positions')
    require(sum(new_inv['targets'].values()) == 22461, 'target positions')
    report['recount'] = {
        'law': 'rank(a->b) = dim(A+B) - dim(A meet B) over GF(2); all nested',
        'moves_7611': dict(sorted(h_old.items())),
        'moves_7612': dict(sorted(h_new.items())),
        'native_delta': delta, 'calls': CALLS, 'caller_part': CALLER,
        'paid_positions': [paid_old, paid_new]}
    report['moments'], logs = check_moments(old_inv, new_inv)
    report['controls'] = controls(old, new, old_inv, new_inv, logs)
    return report


def lineage(head):
    """Optional: the same paid split on three earlier words in the PR tree."""
    out = {}
    for number, (word_path, invoice_path) in LINEAGE.items():
        blobs = []
        for path in (word_path, invoice_path):
            done = subprocess.run(
                ['git', 'cat-file', 'blob', '%s:%s/%s' % (head, PR_ROOT, path)],
                capture_output=True, cwd=str(HERE))
            if done.returncode:
                return {'status': 'SKIPPED_PR_HEAD_OBJECT_ABSENT', 'head': head}
            blobs.append(done.stdout)
        hist = move_histogram(load_word(blobs[0]))
        require(caller_part(hist, json.loads(blobs[1])) == CALLER,
                'lineage caller part #%d' % number)
        out[str(number)] = dict(sorted(hist.items()))
    return {'status': 'PASS_LINEAGE_SAME_CALLER_PART', 'head': head, 'moves': out}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lineage', action='store_true',
                        help='also check #7604/#7605/#7608 from local Git objects')
    args = parser.parse_args()
    raw = {name: (INPUTS / name).read_bytes() for name in PINS}
    report = audit(raw)
    if args.lineage:
        report['lineage'] = lineage(PR_HEAD)
    report['status'] = 'PASS_INDEPENDENT_RECOUNT_PR7612_DECLARED_SCOPE'
    report['scope'] = ('Finite recount of pinned bytes at PR head ' + PR_HEAD +
                       '. Not a native, physical, compiler or outer admission.')
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except Reject as error:
        sys.exit('REJECT: %s' % error)
