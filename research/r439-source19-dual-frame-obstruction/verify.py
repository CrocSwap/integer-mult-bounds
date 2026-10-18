#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact, standard-library checker for the R439/F508/source19 obstruction.

Run: python3 -I -B verify.py
     python3 -I -O -B verify.py --json certificate.json --fixture positive-fixture.json
Optional pinned-byte audit: python3 -I -B verify.py --word /path/to/bitE8mut-p111-tuned.json.gz

The all-length arguments are in audit.md. This program checks their finite
premises and controls; finite tests do not replace those arguments. Independently
written for this handoff. Predecessor input/provenance credit: Arham Tahir, with
substantial OpenAI Codex assistance, and the authors credited in audit.md.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import platform

R = (19, 27, 35, 43, 57, 65, 66, 74, 89, 97, 466)
M = (1, 767, 509, 891, 927, 943, 765, 1019, 911, 254, 1914)
EXPECTED_INVERSE = (1, 66, 709, 842, 272, 288, 885, 136, 583, 515, 1033)
L = {
    19: (1, 0, -1, 0, 1, 0, -1, 0),
    27: (1, -1, 0, 0, 0, 0, 1, -1),
    35: (1, -1, 0, 0, 1, -1, 0, 0),
    43: (1, 0, -1, 0, 0, 1, 0, -1),
    57: (0, 0, 0, 0, 1, -1, -1, 1),
    65: (1, -1, -1, -1, 0, 0, 0, 0),
    66: (1, 0, 0, 1, 1, 0, 0, -1),
    74: (0, 1, 0, 1, 1, 0, -1, 0),
    89: (0, 0, 1, 1, 1, -1, 0, 0),
    97: (0, 1, 0, 1, 0, 1, 0, -1),
}
ENTRY_ROOTS = (
    (19, 27), (27, 97), (35, 74), tuple(L), tuple(L),
    (65,), (66,), (43, 74), (27, 89), (19, 97), tuple(L),
)
ENTRY_IDS = (152, 156, 159, 508, 508, 67, 68, 160, 155, 154, 508)
PIN_SHA256 = 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f'
PIN_BLOB = '85a4499bf9e4911a705d50567a2c2ef6cf23739a'


def need(condition, message):
    """Deliberately not assert: checks must survive python -O."""
    if not condition:
        raise ValueError(message)


@lru_cache(maxsize=None)
def span(vectors):
    """Canonical rational RREF; geometry is never reduced modulo two."""
    if not vectors:
        return ()
    a = [list(map(Q, row)) for row in vectors]
    width = len(a[0])
    need(all(len(row) == width for row in a), 'ragged rational matrix')
    rank = 0
    for col in range(width):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        scale = a[rank][col]
        a[rank] = [x / scale for x in a[rank]]
        for i in range(len(a)):
            if i != rank and a[i][col]:
                scale = a[i][col]
                a[i] = [x - scale * y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return tuple(tuple(row) for row in a[:rank])


def join(*spaces):
    return span(tuple(v for space in spaces for v in space))


def inside(small, large):
    return join(small, large) == large


def determinant(matrix):
    """Separate exact elimination, used for the integer Gram witness."""
    a = [list(map(Q, row)) for row in matrix]
    n = len(a)
    need(all(len(row) == n for row in a), 'nonsquare determinant')
    result = Q(1)
    for j in range(n):
        p = next((i for i in range(j, n) if a[i][j]), None)
        if p is None:
            return Q(0)
        if p != j:
            a[j], a[p] = a[p], a[j]
            result = -result
        pivot = a[j][j]
        result *= pivot
        for i in range(j + 1, n):
            factor = a[i][j] / pivot
            for k in range(j, n):
                a[i][k] -= factor * a[j][k]
    return result


F = span(tuple(L.values()))
ENTRIES = tuple(span(tuple(L[j] for j in roots)) for roots in ENTRY_ROOTS)
H_TEST = span(tuple(L[j] for j in (19, 27, 97)))
AMBIENT = span(tuple(tuple(int(i == j) for j in range(8)) for i in range(8)))


def identity(n):
    return tuple(1 << j for j in range(n))


def shape(rows):
    n = len(rows)
    need(n > 0 and all(isinstance(x, int) and 0 <= x < 1 << n for x in rows),
         'invalid binary matrix')
    return n


def xor_selected(mask, rows):
    out = 0
    while mask:
        bit = mask & -mask
        out ^= rows[bit.bit_length() - 1]
        mask ^= bit
    return out


def multiply(a, b):
    need(shape(a) == shape(b), 'binary product dimensions')
    return tuple(xor_selected(row, b) for row in a)


def columns(rows):
    n = shape(rows)
    return tuple(sum(((rows[i] >> j) & 1) << i for i in range(n)) for j in range(n))


def inverse(rows):
    n = shape(rows)
    a = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if (a[i] >> j) & 1), None)
        need(pivot is not None, 'singular binary matrix')
        a[j], a[pivot] = a[pivot], a[j]
        for i in range(n):
            if i != j and ((a[i] >> j) & 1):
                a[i] ^= a[j]
    need(tuple(x & ((1 << n) - 1) for x in a) == identity(n), 'inverse reduction')
    return tuple(x >> n for x in a)


@lru_cache(maxsize=None)
def support_space(mask, entries):
    return join(*(entries[i] for i in range(len(entries)) if (mask >> i) & 1))


def obligations(rows, entries):
    n = shape(rows)
    need(n == len(entries), 'entry dimensions')
    invcols = columns(inverse(rows))
    forward = tuple(join(entries[i], support_space(rows[i], entries)) for i in range(n))
    dual = tuple(join(entries[i], support_space(invcols[i], entries)) for i in range(n))
    return forward, dual


def check_exit(rows, entries, exits, use_dual=True):
    forward, dual = obligations(rows, entries)
    need(len(exits) == len(entries), 'exit dimensions')
    for i, exit_frame in enumerate(exits):
        need(inside(forward[i], exit_frame), 'forward exit obligation')
        if use_dual:
            need(inside(dual[i], exit_frame), 'inverse-column exit obligation')


def essential(rows, i):
    return rows[i] != 1 << i or columns(rows)[i] != 1 << i


class Trace:
    """Symbolic dirty values, inverse columns, rational frames and all climbs."""
    def __init__(self, registers, entries, ambient):
        need(len(registers) == len(set(registers)) == len(entries), 'wire inventory')
        need(all(inside(s, ambient) for s in entries), 'entry outside allowed frame')
        self.registers = tuple(registers)
        self.index = {r: i for i, r in enumerate(registers)}
        self.entries = tuple(entries)
        self.frames = list(entries)
        self.ambient = ambient
        self.rows = list(identity(len(entries)))
        self.invcols = list(identity(len(entries)))
        self.hist = Counter()
        self.climbs = []
        self.gates = []
        self.source_changed = False

    def visit(self, register, frame):
        need(register in self.index, 'extra wire')
        i = self.index[register]
        need(inside(frame, self.ambient), 'frame outside allowed ambient')
        need(inside(self.frames[i], frame), 'frame descent or incomparable frame')
        increment = len(frame) - len(self.frames[i])
        if increment:
            self.hist[increment] += 1
            self.climbs.append((len(self.gates), register, increment))
        self.frames[i] = frame

    def audit(self):
        actual_inverse = inverse(tuple(self.rows))
        need(tuple(self.invcols) == columns(actual_inverse), 'inverse-column update')
        need(multiply(tuple(self.rows), actual_inverse) == identity(len(self.rows)),
             'prefix matrix product')
        check_exit(tuple(self.rows), self.entries, self.frames)

    def add(self, destination, source, frame):
        need(destination in self.index and source in self.index, 'extra wire')
        need(destination != source, 'self ADD is not allowed')
        # Validate both operands before changing either one.
        need(inside(frame, self.ambient), 'frame outside allowed ambient')
        for r in (destination, source):
            need(inside(self.frames[self.index[r]], frame), 'common operand frame')
        self.visit(destination, frame)
        self.visit(source, frame)
        d, s = self.index[destination], self.index[source]
        self.rows[d] ^= self.rows[s]
        self.invcols[s] ^= self.invcols[d]  # Column source, NOT column destination.
        self.gates.append((destination, source))
        self.source_changed |= self.rows[0] != 1
        self.audit()


def constructor(rows):
    """Deterministic Gaussian fixture, not an optimizing or bounded search."""
    a = list(rows)
    n = shape(rows)
    reduction = []

    def add(d, s):
        a[d] ^= a[s]
        reduction.append((d, s))

    for p in range(n):
        k = next((k for k in range(p, n) if (a[k] >> p) & 1), None)
        need(k is not None, 'singular constructor target')
        if k != p:
            add(p, k)
            add(k, p)
            add(p, k)
        for k in range(n):
            if k != p and ((a[k] >> p) & 1):
                add(k, p)
    need(tuple(a) == identity(n), 'constructor reduction failed')
    return tuple(reversed(reduction))


def execute(gates, entries=ENTRIES, frame=F):
    t = Trace(R, entries, F)
    for d, s in gates:
        t.add(R[d], R[s], frame)
    return t


def extension(rank):
    result = F
    for v in AMBIENT:
        if len(result) == rank:
            break
        result = join(result, span((v,)))
    need(len(result) == rank and inside(F, result), 'continuation fixture frame')
    return result


def floor_root(x, degree):
    need(x >= 0 and degree > 0, 'root domain')
    lo, hi = 0, 1 << ((x.bit_length() + degree - 1) // degree + 1)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid ** degree <= x:
            lo = mid
        else:
            hi = mid
    return lo


def power_interval(base, numerator, denominator, bits=64):
    """Rational enclosure for base**(numerator/denominator), no floats."""
    need(base >= 0 and 0 < numerator < denominator, 'power domain')
    if base == 0:
        return Q(0), Q(0)
    scale = 1 << bits
    target = base ** numerator * scale ** denominator
    k = floor_root(target, denominator)
    lower = Q(k, scale)
    return lower, lower if k ** denominator == target else Q(k + 1, scale)


def cost_interval(coefficients, p, d):
    low = high = Q(0)
    for base, coefficient in coefficients.items():
        a, b = power_interval(base, p, d)
        low += coefficient * (a if coefficient >= 0 else b)
        high += coefficient * (b if coefficient >= 0 else a)
    return low, high


def matrix_on_bits(rows, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(rows))


def gates_on_bits(gates, value):
    for d, s in gates:
        value ^= ((value >> s) & 1) << d
    return value


def digest_check(data, expected):
    need(hashlib.sha256(data).hexdigest() == expected, 'SHA256 mismatch')


def optional_word(path):
    """Read-only provenance/slice/entry/cleanup adapter; not a whole-word replay."""
    data = Path(path).read_bytes()
    digest_check(data, PIN_SHA256)
    git_blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    need(git_blob == PIN_BLOB, 'Git blob mismatch')
    w = json.loads(gzip.decompress(data))
    need(w['v'] == 111 and w['R'] == 439, 'word dimensions')
    for r, vector in L.items():
        need(tuple(w['lines'][r]) == vector, 'root transcription mismatch')

    @lru_cache(maxsize=None)
    def frame(i):
        return span(tuple(tuple(w['lines'][j]) for j in w['frames'][i]))

    need(frame(508) == F, 'block frame transcription')
    current = list(w['start'])
    for section in (w['D'], w['A'], w['B'][:205]):
        for f, d, sources in section:
            for r in [d] + sources:
                current[r] = f
    need(tuple(current[r] for r in R) == ENTRY_IDS, 'entry frame IDs')
    need(tuple(frame(current[r]) for r in R) == ENTRIES, 'entry rational spans')
    local = w['B'][205:242]
    need(len(local) == 37 and sum(len(ss) for _, _, ss in local) == 37, 'slice length')
    t = Trace(R, ENTRIES, F)
    for f, d, ss in local:
        need(f == 508, 'slice frame')
        for s in ss:
            t.add(d, s, F)
    need(tuple(t.rows) == M and t.hist == Counter({2: 6, 3: 2}), 'pinned block endpoint/bill')
    full = next(i for i, roots in enumerate(w['frames']) if len(set(roots)) == w['v'])
    expected_cleanup = [[full, d, ss] for _, d, ss in reversed(w['A'] + w['B'])
                        if d < w['v'] or d >= 2 * w['v']]
    need(w['C'] == expected_cleanup, 'literal full-frame cleanup shape')
    need(len(frame(full)) == 8, 'cleanup rank')
    next_visit = None
    for section, offset, gates in (('B', 242, w['B'][242:]), ('C', 0, w['C'])):
        for k, (f, d, ss) in enumerate(gates, offset):
            if 19 in [d] + ss:
                next_visit = {'section': section, 'index': k, 'frame': f, 'rank': len(frame(f))}
                need(inside(F, frame(f)), 'continuation does not contain original exit')
                break
        if next_visit is not None:
            break
    need(next_visit is not None, 'source missing from continuation and cleanup')
    return {'status': 'PASS', 'sha256': PIN_SHA256, 'git_blob': git_blob,
            'slice': [205, 242], 'unit_adds': 37, 'profile': dict(t.hist),
            'source_first_later_visit': next_visit,
            'cleanup_frame': full, 'cleanup_rank': 8,
            'whole_word_dirty_replay': 'NOT PERFORMED by this adapter'}


def run():
    report = {'status': 'PASS_R439_F508_SOURCE19_DUAL_BARRIER',
              'python': platform.python_version(), 'search_performed': False}
    basis = tuple(L[i] for i in (19, 27, 35, 65))
    gram = tuple(tuple(sum(x * y for x, y in zip(v, w)) for w in basis) for v in basis)
    need(len(F) == 4 and span(basis) == F, 'rational rank-four basis')
    need(determinant(gram) == 64, 'Gram determinant')
    need(determinant(tuple(tuple(Q(x, 2) for x in row) for row in gram)) == 4,
         'ham pairing determinant')
    need(tuple(map(len, ENTRIES)) == (2, 2, 2, 4, 4, 1, 1, 2, 2, 2, 4), 'entry ranks')
    inv = inverse(M)
    need(inv == EXPECTED_INVERSE, 'inverse transcription')
    need(multiply(M, inv) == multiply(inv, M) == identity(11), 'two-sided inverse')
    mask = columns(inv)[0]
    support = [r for j, r in enumerate(R) if (mask >> j) & 1]
    need(mask == 1861 and support == [19, 35, 66, 89, 97, 466], 'critical inverse column')
    need(matrix_on_bits(M, mask) == 1, 'direct inverse-column equation')
    need((inv[10] & 1) == 1 and ENTRIES[10] == F, 'full-frame helper premise')
    forward, dual = obligations(M, ENTRIES)
    need(tuple(map(len, forward)) == (2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4), 'forward bounds')
    need(tuple(map(len, dual)) == (4, 4, 4, 4, 4, 2, 4, 3, 4, 4, 4), 'dual bounds')
    need(all(join(a, b) == F for a, b in zip(forward, dual)), 'all exits equal F')
    need(all(essential(M, i) and essential(inv, i) for i in range(11)), 'essential cleanup wires')
    report['geometry'] = {'F_rank': 4, 'basis_roots': [19, 27, 35, 65],
                          'Gram_determinant': 64, 'ham_Gram_determinant': 4,
                          'entry_ranks': list(map(len, ENTRIES))}
    report['binary'] = {'registers': R, 'matrix_rows': M, 'inverse_rows': inv,
                        'inverse_source_column_mask': mask, 'inverse_source_column_support': support,
                        'critical_entry': '(M^-1)[466,19] = 1',
                        'forward_exit_ranks': list(map(len, forward)),
                        'dual_exit_ranks': list(map(len, dual)), 'combined_exit_ranks': [4] * 11}

    # Favorable fully charged relaxation: all possible first-contact entry ranks.
    contact = {r: len(join(ENTRIES[0], ENTRIES[j])) for j, r in enumerate(R) if j}
    need(contact == {27: 3, 35: 4, 43: 4, 57: 4, 65: 3,
                     66: 3, 74: 4, 89: 3, 97: 3, 466: 4}, 'first-contact geometry')
    eligible = [r for r in contact if contact[r] <= 3]
    need(all(contact[r] > 2 for r in contact), 'rank-two first contact exists')
    need(all(len(ENTRIES[R.index(r)]) in (1, 2) for r in eligible), 'carrier entry rank')
    need(27 in eligible and len(ENTRIES[1]) == 2, 'best carrier class absent')
    need(4 < 5 and 5 ** 5 < 2 ** 12, 'analytic power inequality premises')
    q_tests = []
    for p, d in ((1, 16), (1, 8), (1, 4), (1, 2), (3, 4), (7, 8), (15, 16), (31, 32)):
        # Alternative minus original, even at the most favorable g=8.
        lo, hi = cost_interval({1: 3, 2: -2, 4: -1, 5: 1}, p, d)
        need(lo > 0, 'exact rational-exponent relaxation check')
        q_tests.append({'q': str(Q(p, d)), 'gap_lower': str(lo), 'gap_upper': str(hi)})
    report['fully_charged_relaxation'] = {
        'first_contact_joint_ranks': contact, 'proper_frame_first_contacts': eligible,
        'best_carrier_split_penalty': '2 - 2^q',
        'complete_gap_lower_bound': '3 - 2*2^q + 5^q - 4^q > 0, 0<q<1',
        'integer_analytic_premise': {'5^5': 5 ** 5, '2^12': 2 ** 12},
        'rational_exponent_controls_not_universal_proof': q_tests}

    # Positive fixture at the true entries; constructor is not a length search.
    gates = constructor(M)
    t = execute(gates)
    need(len(gates) == 45 and tuple(t.rows) == M, 'positive fixture target')
    need(t.hist == Counter({2: 6, 3: 2}) and all(f == F for f in t.frames), 'positive fixture bill')
    for value in range(1 << 11):
        image = gates_on_bits(gates, value)
        need(image == matrix_on_bits(M, value), 'truth table forward')
        need(gates_on_bits(tuple(reversed(gates)), image) == value, 'truth table inverse cleanup')
    backward = execute(tuple(reversed(gates)))
    need(tuple(backward.rows) == inv, 'reflected block matrix')
    for d, s in gates:
        backward.add(R[d], R[s], F)
    need(tuple(backward.rows) == identity(11), 'reflected-then-forward identity')

    # Temporary writes to source 19 at a proper frame are explicitly exercised.
    padded = Trace(R, ENTRIES, F)
    need(len(H_TEST) == 3 and inside(ENTRIES[0], H_TEST) and inside(ENTRIES[1], H_TEST), 'test H')
    padded.add(19, 27, H_TEST)
    need(padded.rows[0] == 3 and len(padded.frames[0]) == 3, 'temporary source write')
    padded.add(19, 27, H_TEST)
    need(padded.rows[0] == 1, 'temporary source restoration')
    for d, s in gates:
        padded.add(R[d], R[s], F)
    need(padded.source_changed and tuple(padded.rows) == M, 'source-destination positive fixture')
    need(padded.hist == Counter({1: 4, 2: 4, 3: 2}), 'all padded carrier climbs')

    continuation_tests = []
    for g in range(4, 9):
        c = execute(gates)
        common = extension(g)
        # This is an expressly synthetic continuation/cleanup fixture OUTSIDE
        # the replacement block, not permission for outside-F block operations.
        c.ambient = common
        before = c.hist.copy()
        for d, s in reversed(gates):
            c.add(R[d], R[s], common)
        expected_tail = Counter({g - 4: 11}) if g > 4 else Counter()
        need(c.hist - before == expected_tail, 'complete cleanup climb accounting')
        need(tuple(c.rows) == identity(11), 'literal dirty inverse cleanup')
        need(all(f == common for f in c.frames), 'cleanup endpoint frames')
        continuation_tests.append({'common_frame_rank': g, 'extra_profile': dict(expected_tail)})
    # Entry-interface sensitivity control: same target DOES fit a proper frame
    # when all entries are deliberately changed to that frame.
    changed = execute(gates, entries=(ENTRIES[0],) * 11, frame=ENTRIES[0])
    need(tuple(changed.rows) == M and not changed.hist and len(changed.frames[0]) == 2,
         'changed-interface proper-frame positive control')
    report['positive_fixtures'] = {
        'gaussian_unit_adds': len(gates), 'block_profile': {2: 6, 3: 2},
        'all_bit_assignments_checked': 2048, 'symbolic_dirty_columns': 11,
        'source_destination_padded_adds': len(gates) + 2,
        'source_destination_padded_profile': {1: 4, 2: 4, 3: 2},
        'synthetic_continuation_cleanup_controls': continuation_tests,
        'changed_entry_interface_proper_frame_control': 'PASS; NOT an admissible candidate'}

    # Independent finite algebra control of U' = U E: every GL(3,2) matrix,
    # every one of its six oriented ADD updates. Not a circuit search.
    invertible = updates = 0
    for encoding in range(1 << 9):
        a = tuple((encoding >> (3 * i)) & 7 for i in range(3))
        try:
            u = inverse(a)
        except ValueError:
            continue
        invertible += 1
        for d in range(3):
            for s in range(3):
                if d == s:
                    continue
                b = list(a)
                b[d] ^= b[s]
                expected_columns = list(columns(u))
                expected_columns[s] ^= expected_columns[d]
                need(columns(inverse(tuple(b))) == tuple(expected_columns), 'exhaustive dual update')
                updates += 1
    need((invertible, updates) == (168, 1008), 'GL(3,2) coverage')
    report['finite_algebra_controls'] = {'invertible_3x3_matrices': invertible, 'oriented_updates': updates}

    failures = []

    def rejects(name, thunk, fragment):
        try:
            thunk()
        except ValueError as exc:
            need(fragment in str(exc), 'control failed for an unexpected reason: ' + name)
            failures.append(name)
        else:
            raise ValueError('failure control accepted: ' + name)

    for source_frame, label in ((ENTRIES[0], 'rank2'), (H_TEST, 'rank3')):
        exits = (source_frame,) + (F,) * 10
        check_exit(M, ENTRIES, exits, use_dual=False)
        rejects('forward-only false exit ' + label,
                lambda exits=exits: check_exit(M, ENTRIES, exits), 'inverse-column')
    broken_inverse = EXPECTED_INVERSE[:-1] + (EXPECTED_INVERSE[-1] ^ 1,)
    rejects('critical inverse bit corruption',
            lambda: need(multiply(M, broken_inverse) == identity(11), 'inverse certificate'), 'inverse certificate')
    rejects('singular map', lambda: inverse(M[:-1] + (M[0],)), 'singular')
    rejects('self ADD', lambda: Trace(R, ENTRIES, F).add(19, 19, F), 'self ADD')
    rejects('extra register', lambda: Trace(R, ENTRIES, F).add(999, 19, F), 'extra wire')
    rejects('outside-F block frame', lambda: Trace(R, ENTRIES, F).add(19, 27, AMBIENT), 'outside')
    rejects('one-sided operand hosting', lambda: Trace(R, ENTRIES, F).add(19, 466, H_TEST), 'common operand')
    descent = execute(gates)
    rejects('frame descent', lambda: descent.visit(19, H_TEST), 'descent')
    truncated = execute(gates[:-1])
    rejects('wrong dirty endpoint', lambda: need(tuple(truncated.rows) == M, 'dirty endpoint'), 'dirty endpoint')
    unclean = execute(gates)
    for d, s in tuple(reversed(gates))[1:]:
        unclean.add(R[d], R[s], F)
    rejects('missing inverse gate', lambda: need(tuple(unclean.rows) == identity(11), 'dirty cleanup'), 'dirty cleanup')
    omitted = padded.hist.copy()
    omitted[1] -= 1
    rejects('omitted carrier climb', lambda: need(omitted == padded.hist, 'paid histogram'), 'paid histogram')
    rejects('corrupt pinned bytes', lambda: digest_check(b'not the pinned word', PIN_SHA256), 'SHA256')
    need(len(support_space(inv[0], ENTRIES)) == 2 and len(support_space(mask, ENTRIES)) == 4,
         'inverse row/column orientation control')
    report['negative_controls'] = failures
    report['negative_control_count'] = len(failures)
    report['orientation_control'] = 'inverse ROW 19 only gives rank 2; inverse COLUMN 19 gives rank 4'
    report['whole_pinned_word'] = 'NOT RUN (supply --word for read-only pin/slice/entry/cleanup checks)'
    report['not_claimed'] = [
        'bounded or all-length synthesis search', 'whole 661-wire dirty replay',
        'native/hosting or supplier admission', 'new H2/K bit-interface proof',
        'precision/tape/all-size/analytic-transfer obligations',
        'kappa or selected-frontier change', 'proof-assistant formalization',
        'absence of overlapping public work']
    return report, gates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', type=Path, help='write exact finite certificate')
    parser.add_argument('--fixture', type=Path, help='write deterministic positive fixture and all block climbs')
    parser.add_argument('--word', type=Path, help='optional original compressed word; strict byte pins')
    args = parser.parse_args()
    report, gates = run()
    if args.word:
        report['whole_pinned_word'] = optional_word(args.word)
    if args.json:
        args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if args.fixture:
        t = execute(gates)
        fixture = {'purpose': 'positive checker fixture, NOT a lower-frame candidate or shorter word',
                   'registers': R, 'matrix_rows': M, 'operation_frame': 'F508',
                   'gates_dst_src': [(R[d], R[s]) for d, s in gates],
                   'paid_climbs_gate_index_zero_based_register_increment': t.climbs,
                   'block_histogram': dict(t.hist),
                   'source_destination_control_prefix': [[19, 27], [19, 27]],
                   'prefix_frame_basis_roots': [19, 27, 97],
                   'cleanup': 'reverse the gate sequence; see audit.md for frame accounting'}
        args.fixture.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')
    print(report['status'])
    print('Python:', report['python'])
    print('Rational F rank = 4; basis Gram determinant = 64; ham Gram determinant = 4')
    print('Inverse rows:', list(EXPECTED_INVERSE))
    print('Inverse column 19:', report['binary']['inverse_source_column_support'])
    print('All 11 exits forced to F508; critical entry (M^-1)[466,19] = 1')
    print('Fully charged relaxation: 3 - 2*2^q + 5^q - 4^q > 0 (analytic proof in audit.md)')
    print('Exact rational-exponent controls:', len(report['fully_charged_relaxation']['rational_exponent_controls_not_universal_proof']))
    print('Positive fixture: 45 ADDs, profile {2: 6, 3: 2}, 11 symbolic dirty inputs, 2048 bit assignments')
    print('Source-as-destination fixture: 47 ADDs, profile {1: 4, 2: 4, 3: 2}')
    print('Synthetic full inverse-cleanup controls: ranks 4,5,6,7,8; both matrix orientations checked')
    print('Finite algebra controls: 168 invertible 3x3 matrices, 1008 oriented updates')
    print('Failure controls rejected:', report['negative_control_count'])
    for name in report['negative_controls']:
        print('  REJECTED:', name)
    print('Optional original-word audit:', report['whole_pinned_word'])
    print('No synthesis search, native/hosting test, whole-word dirty replay, or frontier change claimed.')


if __name__ == '__main__':
    main()
