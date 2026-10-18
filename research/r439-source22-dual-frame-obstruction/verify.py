#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact, standard-library checker for the R439/F509/source22 obstruction.

Run: python3 -I -B verify.py
     python3 -I -O -B verify.py
Optional pinned-word binding:
     python3 -I -B verify.py --word /path/to/bitE8mut-p111-tuned.json.gz

The all-length argument is the inverse-column frame invariant of https://github.com/CrocSwap/integer-mult-bounds/pull/1511
(Andrey Mas), applied here to the separately pinned block-509 boundary;
see README.md. This program checks the finite premises and controls of that
argument; finite tests do not replace it. Written independently for this
handoff; no predecessor implementation is imported. Predecessor credit:
Arham Tahir (https://github.com/CrocSwap/integer-mult-bounds/pull/1368 data, forward bounds, prefix inverse matrices) and
Andrey Mas (https://github.com/CrocSwap/integer-mult-bounds/pull/1511 invariant). Contributor: Aaron Wang / navinor, with
help from opencode.
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

R = (17, 22, 33, 38, 50, 60, 67, 77, 87, 92, 468)
M = (1023, 2, 1020, 1011, 943, 991, 959, 891, 1018, 508, 1524)
EXPECTED_INVERSE = (7, 2, 262, 271, 80, 33, 65, 391, 958, 516, 1807)
L = {
    17: (1, 0, 1, 0, -1, 0, -1, 0),
    22: (1, 1, 0, 0, 0, 0, 1, 1),
    33: (1, 1, 0, 0, -1, -1, 0, 0),
    38: (1, 0, 1, 0, 0, 1, 0, 1),
    50: (0, 1, -1, 0, 0, -1, 1, 0),
    60: (1, 1, 1, -1, 0, 0, 0, 0),
    67: (1, 0, 0, 1, -1, 0, 0, 1),
    77: (0, 1, 0, -1, 1, 0, 1, 0),
    87: (0, 0, 1, -1, 0, 0, -1, -1),
    92: (0, 0, 1, -1, 1, 1, 0, 0),
}
ALL = (17, 22, 33, 38, 50, 60, 67, 77, 87, 92)
ENTRY_ROOTS = (
    ALL, (17, 22), (33, 38), (38, 77), (50,), (60,),
    (50, 67), (33, 77), (38, 87), (22, 92), ALL,
)
ENTRY_IDS = (509, 182, 185, 188, 52, 62, 192, 186, 189, 184, 509)
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
    row = 0
    for col in range(width):
        pivot = next((i for i in range(row, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        lead = a[row][col]
        a[row] = [x / lead for x in a[row]]
        for i in range(len(a)):
            if i != row and a[i][col]:
                factor = a[i][col]
                a[i] = [x - factor * y for x, y in zip(a[i], a[row])]
        row += 1
        if row == len(a):
            break
    return tuple(tuple(x for x in r) for r in a[:row])


def join(*spaces):
    rows = []
    for space in spaces:
        rows.extend(space)
    return span(tuple(rows))


def inside(small, large):
    return join(small, large) == large


def determinant(matrix):
    a = [list(map(Q, row)) for row in matrix]
    det = Q(1)
    for col in range(len(a)):
        pivot = next((i for i in range(col, len(a)) if a[i][col]), None)
        if pivot is None:
            return Q(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            det = -det
        det *= a[col][col]
        lead = a[col][col]
        for i in range(col + 1, len(a)):
            factor = a[i][col] / lead
            for k in range(col, len(a)):
                a[i][k] -= factor * a[col][k]
    return det


ENTRIES = tuple(span(tuple(L[j] for j in roots)) for roots in ENTRY_ROOTS)
F = span(tuple(L[i] for i in ALL))


def identity(n):
    return tuple(1 << i for i in range(n))


def shape(rows):
    n = len(rows)
    need(n == len(ENTRIES) == 11, 'entry dimensions')
    need(all(0 <= r < (1 << n) for r in rows), 'mask out of range')


def multiply(a, b):
    out = []
    for i in range(len(a)):
        mask = 0
        for j in range(len(a)):
            if (a[i] >> j) & 1:
                mask ^= b[j]
        out.append(mask)
    return tuple(out)


def columns(rows):
    n = len(rows)
    return tuple(sum(((rows[i] >> j) & 1) << i for i in range(n)) for j in range(n))


def inverse(rows):
    n = len(rows)
    shape(rows)
    a = [[(rows[i] >> j) & 1 for j in range(n)]
         + [1 if i == k else 0 for k in range(n)] for i in range(n)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if a[i][col]), None)
        need(pivot is not None, 'singular map')
        a[col], a[pivot] = a[pivot], a[col]
        for i in range(n):
            if i != col and a[i][col]:
                for k in range(2 * n):
                    a[i][k] ^= a[col][k]
    return tuple(sum(a[i][n + j] << j for j in range(n)) for i in range(n))


def forward_labels(rows, entries):
    shape(rows)
    out = []
    for i, row in enumerate(rows):
        out.append(join(*([entries[i]] + [entries[j] for j in range(len(rows))
                                         if (row >> j) & 1])))
    return tuple(out)


def dual_labels(inv_rows, entries):
    shape(inv_rows)
    cols = columns(inv_rows)
    return tuple(join(*[entries[j] for j in range(len(inv_rows))
                        if (cols[i] >> j) & 1]) for i in range(len(inv_rows)))


def check_exit(rows, inv_rows, entries, exits, use_dual=True):
    """Every exit frame must contain the forced forward (and dual) label."""
    shape(rows)
    need(len(exits) == len(rows), 'exit count')
    forward = forward_labels(rows, entries)
    dual = dual_labels(inv_rows, entries) if use_dual else forward
    for i in range(len(rows)):
        need(inside(join(forward[i], dual[i]), exits[i]),
             'exit frame below forced label')
    return forward, dual


def essential(rows, i):
    """Wire i has a nonidentity row or a nonidentity column."""
    n = len(rows)
    return rows[i] != (1 << i) or columns(rows)[i] != (1 << i)


class Trace:
    """Symbolic dirty values, forward rows, inverse columns and rational frames."""

    def __init__(self, registers, entries, ambient):
        self.registers = tuple(registers)
        self.index = {r: i for i, r in enumerate(self.registers)}
        self.entries = tuple(entries)
        self.ambient = ambient
        need(all(inside(s, ambient) for s in entries), 'entry outside allowed frame')
        self.rows = list(identity(len(self.registers)))
        self.inv = list(identity(len(self.registers)))
        self.frames = list(entries)
        self.hist = Counter()

    def visit(self, register, frame):
        need(register in self.index, 'register outside the block')
        i = self.index[register]
        need(inside(self.frames[i], frame), 'frame descent or incomparable frame')
        increment = len(frame) - len(self.frames[i])
        if increment > 0:
            self.hist[increment] += 1
        self.frames[i] = frame

    def audit(self):
        rows, inv = tuple(self.rows), tuple(self.inv)
        need(multiply(rows, inv) == multiply(inv, rows) == identity(len(rows)),
             'inverse tracking lost')
        check_exit(rows, inv, self.entries, tuple(self.frames))

    def add(self, destination, source, frame):
        need(destination in self.index and source in self.index,
             'register outside the block')
        need(destination != source, 'self ADD is not a reversible gate')
        d, s = self.index[destination], self.index[source]
        need(inside(join(self.frames[d], self.frames[s]), frame),
             'one-sided operand hosting: common frame must contain both operands')
        self.rows[d] ^= self.rows[s]
        for j in range(len(self.inv)):
            if (self.inv[j] >> d) & 1:
                self.inv[j] ^= 1 << s
        self.visit(destination, frame)
        self.visit(source, frame)
        self.audit()


def constructor(rows):
    """Deterministic Gaussian factorization; not a length search."""
    n = len(rows)
    current = list(rows)
    ops = []
    for col in range(n):
        pivot = next((i for i in range(col, n) if (current[i] >> col) & 1), None)
        need(pivot is not None, 'singular map')
        if pivot != col:
            current[col] ^= current[pivot]
            ops.append((col, pivot))
        for i in range(n):
            if i != col and (current[i] >> col) & 1:
                current[i] ^= current[col]
                ops.append((i, col))
    need(tuple(current) == identity(n), 'constructor failed')
    return tuple(reversed(ops))


def execute(gates, entries=ENTRIES, frame=F):
    t = Trace(R, entries, frame)
    for d, s in gates:
        t.add(R[d], R[s], frame)
    return t


def matrix_on_bits(rows, value):
    out = 0
    for i, row in enumerate(rows):
        bits = bin(row & value).count('1')
        if bits & 1:
            out |= 1 << i
    return out


def gates_on_bits(gates, value):
    for d, s in gates:
        value ^= ((value >> s) & 1) << d
    return value


def concavity_controls():
    """Exact integer controls for the step t^q >= t (0<=t<=1, 0<q<1).

    With t = d1/D and q = p/d in lowest terms, t^p >= t^d is the integer
    inequality d1^p * D^(d-p) >= d1^d. These are finite samples of the
    two-line argument in README.md, not its proof.
    """
    checks = []
    for p, d in ((1, 2), (1, 4), (3, 4), (7, 8)):
        for total in range(2, 7):
            for d1 in range(1, total):
                need(d1 ** p * total ** (d - p) >= d1 ** d,
                     'concavity sample failed')
        checks.append({'q': str(Q(p, d)), 'samples': 'splits of 2..6'})
    return checks


def digest_check(data, expected):
    need(hashlib.sha256(data).hexdigest() == expected, 'SHA256 mismatch')


def optional_word(path):
    """Read-only provenance/slice/entry/continuation adapter.

    Not a whole-word dirty replay. It binds the constants above to the pinned
    frozen word: bytes, root transcription, entry frames, the 31-ADD slice
    B[283:314], its endpoint and bill, the continuation boundary and the
    literal full-frame cleanup shape.
    """
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

    need(frame(509) == F, 'block frame transcription')
    current = list(w['start'])
    for section in (w['D'], w['A'], w['B'][:283]):
        for f, d, sources in section:
            for r in [d] + sources:
                current[r] = f
    need(tuple(current[r] for r in R) == ENTRY_IDS, 'entry frame IDs')
    need(tuple(frame(current[r]) for r in R) == ENTRIES, 'entry rational spans')
    local = w['B'][283:314]
    need(len(local) == 31 and sum(len(ss) for _, _, ss in local) == 31, 'slice length')
    t = Trace(R, ENTRIES, F)
    for f, d, ss in local:
        need(f == 509, 'slice frame')
        for s in ss:
            t.add(d, s, F)
    need(tuple(t.rows) == M and t.hist == Counter({2: 7, 3: 2}),
         'pinned block endpoint/bill')
    full = next(i for i, roots in enumerate(w['frames']) if len(set(roots)) == w['v'])
    expected_cleanup = [[full, d, ss] for _, d, ss in reversed(w['A'] + w['B'])
                        if d < w['v'] or d >= 2 * w['v']]
    need(w['C'] == expected_cleanup, 'literal full-frame cleanup shape')
    need(len(frame(full)) == 8, 'cleanup rank')
    visits = {}
    for section, offset, gates in (('B', 314, w['B'][314:]), ('C', 0, w['C'])):
        for k, (f, d, ss) in enumerate(gates, offset):
            for r in dict.fromkeys([d] + list(ss)):
                if r in R and r not in visits:
                    need(inside(F, frame(f)),
                         'continuation does not contain original exit')
                    visits[r] = {'section': section, 'index': k,
                                 'frame': f, 'rank': len(frame(f))}
    need(len(visits) == 11, 'a block wire missing from continuation and cleanup')
    return {'status': 'PASS', 'sha256': PIN_SHA256, 'git_blob': git_blob,
            'slice': [283, 314], 'unit_adds': 31,
            'profile': dict(t.hist),
            'first_later_visits': {str(r): visits[r] for r in R},
            'cleanup_frame': full, 'cleanup_rank': 8,
            'whole_word_dirty_replay': 'NOT PERFORMED by this adapter'}


def run():
    report = {'status': 'PASS_R439_F509_SOURCE22_DUAL_BARRIER',
              'python': platform.python_version(), 'search_performed': False}

    # Geometry over Q; never modulo two.
    basis = tuple(L[i] for i in (17, 22, 33, 60))
    gram = tuple(tuple(sum(x * y for x, y in zip(v, w)) for w in basis) for v in basis)
    need(len(F) == 4 and span(basis) == F, 'rational rank-four block frame')
    need(gram == ((4, 0, 2, 2), (0, 4, 2, 2), (2, 2, 4, 2), (2, 2, 2, 4)),
         'Gram matrix transcription')
    need(determinant(gram) == 64, 'Gram determinant')
    need(determinant(tuple(tuple(Q(x, 2) for x in row) for row in gram)) == 4,
         'ham pairing determinant')
    need(tuple(map(len, ENTRIES)) == (4, 2, 2, 2, 1, 1, 2, 2, 2, 2, 4), 'entry ranks')
    need(ENTRIES[0] == ENTRIES[10] == F, 'full-frame entry labels')
    need(span((L[17], L[22])) == ENTRIES[1], 'source-22 entry label')

    # Exact binary algebra over F2.
    inv = inverse(M)
    need(inv == EXPECTED_INVERSE, 'inverse transcription')
    need(multiply(M, inv) == multiply(inv, M) == identity(11), 'two-sided inverse')
    mask = columns(inv)[1]
    support = [r for j, r in enumerate(R) if (mask >> j) & 1]
    need(mask == 1423 and support == [17, 22, 33, 38, 77, 87, 468],
         'critical inverse column')
    need(matrix_on_bits(M, mask) == 2, 'direct inverse-column equation M*(M^-1 e_22)=e_22')
    need((inv[0] >> 1) & 1 and (inv[10] >> 1) & 1, 'full-frame wires in critical column')
    need(ENTRIES[0] == F and ENTRIES[10] == F, 'full-frame helper/source premise')
    # Orientation control: the inverse row of 22 does not close the case.
    row_support = [r for j, r in enumerate(R) if (inv[1] >> j) & 1]
    row_idx = [j for j in range(11) if (inv[1] >> j) & 1]
    col_idx = [j for j in range(11) if (mask >> j) & 1]
    need(inv[1] == 2 and row_support == [22], 'inverse row orientation control')
    need(len(join(*[ENTRIES[j] for j in row_idx])) == 2, 'inverse row gives rank two')
    need(len(join(*[ENTRIES[j] for j in col_idx])) == 4, 'inverse column gives rank four')

    forward = forward_labels(M, ENTRIES)
    dual = dual_labels(inv, ENTRIES)
    need(tuple(map(len, forward)) == (4, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4), 'forward bounds')
    need(tuple(map(len, dual)) == (4, 4, 4, 4, 3, 3, 2, 4, 4, 4, 4), 'dual bounds')
    need(all(join(a, b) == F for a, b in zip(forward, dual)), 'all exits equal F')
    need(all(essential(M, i) and essential(inv, i) for i in range(11)),
         'essential cleanup wires')
    report['geometry'] = {'F_rank': 4, 'basis_roots': [17, 22, 33, 60],
                          'Gram_matrix': [list(r) for r in gram],
                          'Gram_determinant': 64, 'ham_Gram_determinant': 4,
                          'entry_ranks': list(map(len, ENTRIES))}
    report['binary'] = {'registers': R, 'matrix_rows': M, 'inverse_rows': inv,
                        'inverse_source_column_mask': mask,
                        'inverse_source_column_support': support,
                        'inverse_row_of_source': row_support,
                        'critical_entries': ['(M^-1)[17,22] = 1', '(M^-1)[468,22] = 1'],
                        'forward_exit_ranks': list(map(len, forward)),
                        'dual_exit_ranks': list(map(len, dual)),
                        'combined_exit_ranks': [4] * 11}

    # Invoice: single-climb minimum 7*2^q + 2*3^q for 0 < q = 1-a < 1.
    bill = Counter(4 - len(e) for e in ENTRIES if len(e) < 4)
    need(bill == Counter({2: 7, 3: 2}), 'single-climb profile')
    report['invoice'] = {'single_climb_profile': {str(k): v for k, v in bill.items()},
                         'block_moment': '7*2^q + 2*3^q, q = 1-a, minimal for 0<a<1',
                         'baseline_attained_by': 'the original 31-ADD word and the fixture'}
    report['concavity_controls'] = concavity_controls()

    # Positive fixture at the true entries; a constructor, not a length search.
    gates = constructor(M)
    t = execute(gates)
    need(tuple(t.rows) == M, 'positive fixture target')
    need(t.hist == Counter({2: 7, 3: 2}) and all(f == F for f in t.frames),
         'positive fixture bill')
    for value in range(1 << 11):
        image = gates_on_bits(gates, value)
        need(image == matrix_on_bits(M, value), 'truth table forward')
        need(gates_on_bits(tuple(reversed(gates)), image) == value,
             'truth table inverse cleanup')
    backward = execute(tuple(reversed(gates)))
    need(tuple(backward.rows) == inv, 'reflected block matrix')
    report['positive_fixture'] = {'gates': len(gates), 'profile': dict(t.hist),
                                  'note': 'control fixture, not a shortening claim'}

    # Failure controls: each must be rejected for its own reason.
    controls = []

    def rejected(name, fn):
        try:
            fn()
        except ValueError as exc:
            controls.append({'control': name, 'rejected': str(exc)})
            return
        raise ValueError('failure control not rejected: ' + name)

    low2 = list(ENTRIES)
    low2[1] = span((L[17], L[22]))
    rejected('proposed rank-two source-22 exit',
             lambda: check_exit(M, inv, ENTRIES, tuple(low2)))
    low3 = [F if i != 1 else span((L[17], L[22], L[33])) for i in range(11)]
    rejected('proposed rank-three source-22 exit',
             lambda: check_exit(M, inv, ENTRIES, tuple(low3)))
    corrupted = list(EXPECTED_INVERSE)
    corrupted[0] ^= 1
    rejected('corrupt critical inverse bit',
             lambda: need(tuple(inverse(M)) == tuple(corrupted), 'inverse mismatch'))
    rejected('singular map', lambda: inverse((0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 0)))
    bad = Trace(R, ENTRIES, F)
    rejected('self ADD', lambda: bad.add(R[1], R[1], F))
    rejected('extra register', lambda: bad.add(1234, R[1], F))
    rejected('one-sided operand hosting', lambda: bad.add(R[1], R[2], ENTRIES[1]))
    t2 = Trace(R, ENTRIES, F)
    t2.add(R[1], R[2], F)
    lower = list(t2.frames)
    lower[1] = ENTRIES[1]
    rejected('frame descent',
             lambda: [t2.visit(R[1], ENTRIES[1])])
    truncated = constructor(M)[:-1]
    rejected('truncated positive circuit',
             lambda: need(tuple(execute(truncated).rows) == M, 'endpoint mismatch'))
    omitted = tuple(reversed(constructor(M)))[:-1]
    try:
        for value in range(1 << 11):
            need(gates_on_bits(omitted, gates_on_bits(constructor(M), value)) == value,
                 'inverse cleanup incomplete')
    except ValueError as exc:
        controls.append({'control': 'omitted inverse gate', 'rejected': str(exc)})
    else:
        raise ValueError('failure control not rejected: omitted inverse gate')
    rejected('corrupted source bytes',
             lambda: digest_check(b'b' * 8, PIN_SHA256))
    report['failure_controls'] = controls
    need(len(controls) == 11, 'failure control count')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', type=Path)
    parser.add_argument('--word', type=Path)
    args = parser.parse_args()
    report = run()
    if args.word is not None:
        report['word_binding'] = optional_word(args.word)
    if args.json is not None:
        args.json.write_text(json.dumps(report, indent=1, sort_keys=True),
                             encoding='utf-8')
    print(report['status'])
    print('failure_controls=%d inverse_column=%s all_exits=F509 bill={2:7,3:2}'
          % (len(report['failure_controls']),
             report['binary']['inverse_source_column_support']))


if __name__ == '__main__':
    main()
