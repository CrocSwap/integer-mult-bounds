#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Adam Gall, with substantial OpenAI Codex assistance.
"""Exact two-writer dirty compensation census; no supplier admission or new kappa.

No predecessor executable is imported. Source geometry implements the unchanged
nested-frame law specified in the pinned eumemic xcheck_p.py, lines 18--23.
The single-writer positive fixture is credited to Sagar Thakrar / PR1868.
"""
import argparse
import copy
import gzip
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
SPEC = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
INPUTS = [SPEC, WORD]
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_pin(data, expected):
    need(sha(data) == expected, 'source pin mismatch')


def load_word():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    pins = {x['path']: x['sha256'] for x in manifest['files'] if x['usage'] == 'input'}
    need(sorted(pins) == INPUTS, 'complete source inventory')
    need(json.loads((HERE / 'VERIFY.json').read_text(encoding='utf-8'))['inputs'] == INPUTS,
         'complete replay inventory')
    data = {}
    for path in INPUTS:
        data[path] = (ROOT / path).read_bytes()
        check_pin(data[path], pins[path])
    return json.loads(gzip.decompress(data[WORD]))


def xor_rows(rows, gates):
    for _, dest, donors in gates:
        for donor in donors:
            rows[dest] ^= rows[donor]
    return rows


def stream(word):
    n = 2 * word['v'] + word['R']
    ops = [('add', d, s) for section in 'DA' for _, d, ss in word[section] for s in ss]
    for j, centre in enumerate(word['ret']):
        ops.append(('copy', n, centre))
        ops.extend(('add', word['v'] + t, n) for t, row in enumerate(word['scatter']) if j in row)
        ops.append(('erase', n, centre))
    ops.extend(('add', d, s) for section in 'BC' for _, d, ss in word[section] for s in ss)
    return ops


def literal(word, reverse=False):
    n = 2 * word['v'] + word['R']
    rows = [1 << k for k in range(n)] + [0]
    ops = stream(word)
    for kind, d, s in reversed(ops) if reverse else ops:
        if reverse:
            kind = {'copy': 'erase', 'erase': 'copy'}.get(kind, kind)
        if kind == 'add':
            rows[d] ^= rows[s]
        elif kind == 'copy':
            need(rows[d] == 0, 'COPY requires a clean temporary')
            rows[d] = rows[s]
        else:
            need(rows[d] == rows[s], 'ERASE requires matching current value')
            rows[d] = 0
    need(rows[-1] == 0, 'unrestored temporary')
    return rows[:-1]


def wanted(word):
    v = word['v']
    return [(1 << k) ^ ((1 << (k - v)) if v <= k < 2 * v else 0)
            for k in range(2 * v + word['R'])]


def bill(word):
    ops = stream(word)
    maxima = []
    for reverse in (False, True):
        vals = [1] * (2 * word['v'] + word['R'] + 1)
        peak = 1
        for kind, d, s in reversed(ops) if reverse else ops:
            if reverse:
                kind = {'copy': 'erase', 'erase': 'copy'}.get(kind, kind)
            vals[d] = vals[d] + vals[s] if kind == 'add' else vals[s] if kind == 'copy' else 0
            peak = max(peak, vals[d])
        maxima.append(peak)
    f, b = maxima
    return {'ADDs': sum(k == 'add' for k, _, _ in ops), 'F': f, 'B': b,
            'local_bound': str(64 * f**3 * b**2),
            'nine_stage_bound': str((1 << 18) * f**5 * b**4)}


def rref(rows):
    rows = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for col in range(8):
        found = next((k for k in range(pivot, len(rows)) if rows[k][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        divisor = rows[pivot][col]
        rows[pivot] = [x / divisor for x in rows[pivot]]
        for k in range(len(rows)):
            if k != pivot and rows[k][col]:
                multiplier = rows[k][col]
                rows[k] = [x - multiplier * y for x, y in zip(rows[k], rows[pivot])]
        pivot += 1
    return rows[:pivot]


class Geometry:
    def __init__(self, word):
        self.lines = word['lines']
        self.frames = [frozenset(x) for x in word['frames']]
        self.bases = {}

    def basis(self, frame):
        if frame not in self.bases:
            self.bases[frame] = rref([self.lines[k] for k in sorted(self.frames[frame])])
        return self.bases[frame]

    def failure_witness(self, section, gate, register, old, new):
        basis = self.basis(new)
        # The set test alone is not the certificate: require an actual rational
        # source-label vector outside the proposed receiving frame's span.
        for label in sorted(self.frames[old] - self.frames[new]):
            extended = rref(basis + [self.lines[label]])
            if len(extended) > len(basis):
                return {'section': section, 'gate': gate, 'register': register,
                        'old_frame': old, 'new_frame': new, 'outside_label': label,
                        'receiving_rank': len(basis), 'extended_rank': len(extended)}
        raise ValueError('frame-set rejection lacks a rational noncontainment witness')

    def paths(self, word):
        paths = [[f] for f in word['start']]
        for section in 'DABC':
            for index, (frame, dest, donors) in enumerate(word[section]):
                for register in (dest, *donors):
                    old = paths[register][-1]
                    if old == frame:
                        continue
                    if not self.frames[old] < self.frames[frame]:
                        return None, self.failure_witness(section, index, register, old, frame)
                    paths[register].append(frame)
        for register, frame in enumerate(word['final']):
            old = paths[register][-1]
            if old != frame:
                if not self.frames[old] < self.frames[frame]:
                    return None, self.failure_witness('final', -1, register, old, frame)
                paths[register].append(frame)
        return paths, None

    def paid_profile(self, word):
        paths, error = self.paths(word)
        need(error is None, 'no paid profile admitted for an illegal frame path')
        counts = Counter(len(self.basis(b)) - len(self.basis(a))
                         for path in paths for a, b in zip(path, path[1:]))
        current = list(word['start'])
        for section in 'DA':
            for frame, dest, donors in word[section]:
                for register in (dest, *donors):
                    current[register] = frame
        counts.update(len(self.basis(current[r])) for r in word['ret'])
        return dict(sorted(counts.items()))


def star_domain(word):
    v, d = word['v'], word['D']
    count = sum(dest >= 2 * v for _, dest, _ in d)
    need(count % 2 == 0, 'paired helper preparation/restoration')
    count //= 2
    prep, rest = d[:count], d[-count:]
    need(rest == prep[::-1], 'literal star restoration suffix')
    need(all(f == 0 and a >= 2*v and len(ss) == 1 and ss[0] >= 2*v for f,a,ss in prep),
         'source-free zero-frame helper stars')
    need(all(f == 0 and v <= a < 2*v for f,a,ss in d[count:-count]), 'target-only middle')
    edges = [(a, ss[0]) for _, a, ss in rest]
    centres = {a for a, _ in edges}
    leaves = [b for _, b in edges]
    need(len(set(leaves)) == len(leaves) and centres.isdisjoint(leaves), 'disjoint star leaves')
    first = {a: next((i for i, (_, _, ss) in enumerate(word['A']) if a in ss), len(word['A']))
             for a in centres}
    writers = {a: [i for i, (_, d, _) in enumerate(word['A'][:first[a]]) if d == a] for a in centres}
    n = 2*v + word['R']
    rows = xor_rows([1 << k for k in range(n)], word['D'])
    need(all(rows[k] == 1 << k for k in list(range(v)) + list(range(2*v, n))),
         'D restores every source/helper')
    need(all(d not in ss and len(ss) == len(set(ss)) and all(not v <= s < 2*v for s in ss)
             for _, d, ss in word['A']), 'target-free A donor sets without self reads')
    cuts = {i for ws in writers.values() for i in ws}
    snapshots = {}
    for i, gate in enumerate(word['A']):
        if i in cuts:
            need(len(set(rows)) == n and all(rows), 'invertible state has distinct nonzero rows')
            snapshots[i] = tuple(rows)
        xor_rows(rows, [gate])
    return count, edges, first, writers, snapshots


def omit_restoration(word, centre, leaf, count):
    out = copy.deepcopy(word)
    matches = [k for k in range(len(out['D'])-count, len(out['D']))
               if out['D'][k] == [0, centre, [leaf]]]
    need(len(matches) == 1, 'unique specified terminal restoration')
    out['D'].pop(matches[0])
    return out


def candidate(word, solution, count):
    _, centre, leaf, i, j, s, t = solution
    out = omit_restoration(word, centre, leaf, count)
    for gate, donor in ((i, s), (j, t)):
        out['A'][gate][2] = sorted(set(out['A'][gate][2]) ^ {donor})
    return out


def solve(word):
    n, v = 2 * word['v'] + word['R'], word['v']
    count, edges, first, writers, snapshots = star_domain(word)
    solutions, trials, pairs = [], 0, 0
    for centre, leaf in sorted(edges):
        donors = [r for r in range(n) if r != centre and not v <= r < 2*v]
        for i, j in itertools.combinations(writers[centre], 2):
            pairs += 1
            lookup = {snapshots[j][r]: r for r in donors}
            need(len(lookup) == len(donors), 'unique second donor lookup')
            for s in donors:
                trials += 1
                # r_i(s) XOR r_j(t) = e_leaf is necessary and sufficient.
                t = lookup.get(snapshots[i][s] ^ (1 << leaf))
                if t is not None:
                    delta = -1 + (1 - 2*(s in word['A'][i][2])) + (1 - 2*(t in word['A'][j][2]))
                    solutions.append((delta, centre, leaf, i, j, s, t))
    return count, pairs, trials, sorted(solutions), first, writers, snapshots


def expect_rejection(function):
    try:
        function()
    except ValueError:
        return
    raise ValueError('negative control was accepted')


def run(word):
    need((word['v'], word['R']) == (111, 439), 'fixed source dimensions')
    target = wanted(word)
    need(literal(word) == target and literal(word, True) == target, 'baseline dirty boundary')
    geo = Geometry(word)
    paths, error = geo.paths(word)
    need(error is None, 'baseline frame legality')
    profile = geo.paid_profile(word)
    need(profile == PROFILE, 'baseline complete paid histogram')
    base_bill = bill(word)
    need(base_bill['ADDs'] == 11500, 'baseline scalar invoice')
    count, pairs, trials, solutions, first, writers, snapshots = solve(word)
    rows = []
    for solution in solutions:
        change, centre, leaf, i, j, s, t = solution
        out = candidate(word, solution, count)
        need(literal(out) == target and literal(out, True) == target, 'full dirty completion')
        need(sum(len(ss) for sec in 'DABC' for _, _, ss in out[sec]) -
             sum(len(ss) for sec in 'DABC' for _, _, ss in word[sec]) == change, 'complete ADD delta')
        _, error = geo.paths(out)
        need(error is not None, 'a frame-legal two-toggle completion exists')
        rows.append({'solution': list(solution), 'failure': error})
    need((count, pairs, trials, len(solutions)) == (236, 414, 227286, 314), 'complete census counts')
    need(Counter(s[0] for s in solutions) == {-1: 52, 1: 262}, 'scalar saving census')

    # Source-bound legal single-writer positive: PR1868, not a new construction.
    positive = omit_restoration(word, 506, 374, count)
    need(positive['A'][288] == [71, 506, [374]], 'positive fixture source gate')
    positive['A'][288][2] = [69]
    need(literal(positive) == target and literal(positive, True) == target, 'single-writer positive boundary')
    need(geo.paths(positive)[0] == paths and geo.paid_profile(positive) == profile,
         'single-writer positive frame paths and full paid profile')
    positive_bill = bill(positive)
    need(positive_bill['ADDs'] == 11499, 'single-writer positive invoice')
    for priced in (base_bill, positive_bill):
        need(int(priced['local_bound']) < 1 << 104 and int(priced['nine_stage_bound']) < 1 << 192,
             'source control precision guards')

    fixture = solutions[0]
    need(fixture == (-1, 231, 459, 9, 527, 109, 459), 'canonical counterexample')
    _, centre, leaf, i, j, s, t = fixture
    need(snapshots[i][s] == 1 << 109 and snapshots[j][t] == (1 << 109) ^ (1 << 459),
         'explicit arbitrary-dirty correction rows')
    full = candidate(word, fixture, count)
    controls = []
    for name, altered in [('omit_both_corrections', omit_restoration(word, centre, leaf, count)),
                          ('keep_restoration', copy.deepcopy(full)),
                          ('omit_first_correction', copy.deepcopy(full)),
                          ('omit_second_correction', copy.deepcopy(full)),
                          ('wrong_first_donor', copy.deepcopy(full))]:
        if name == 'keep_restoration':
            altered['D'] = copy.deepcopy(word['D'])
        elif name == 'omit_first_correction':
            altered['A'][i] = copy.deepcopy(word['A'][i])
        elif name == 'omit_second_correction':
            altered['A'][j] = copy.deepcopy(word['A'][j])
        elif name == 'wrong_first_donor':
            altered['A'][i][2] = sorted(set(altered['A'][i][2]) ^ {109, 108})
        actual = literal(altered)
        need(actual != target, 'boundary control: ' + name)
        register = next(k for k, (a, b) in enumerate(zip(actual, target)) if a != b)
        defect = actual[register] ^ target[register]
        column = (defect & -defect).bit_length() - 1
        controls.append({'name': name, 'first_bad_register': register, 'witness_input_column': column})
    # Both exact frame failure and integrity checks must remain active with -O.
    expect_rejection(lambda: geo.paid_profile(full))
    expect_rejection(lambda: check_pin(b'changed source', sha(b'source')))
    controls.extend([{'name': 'illegal_frame_cannot_be_billed'}, {'name': 'source_corruption'}])
    return {'format': 'r439-two-writer-absorption/1', 'columns': 661,
            'star_edges': count, 'edge_writer_pair_counts': dict(sorted(Counter(
                len(list(itertools.combinations(writers[a], 2))) for a, _ in star_domain(word)[1]).items())),
            'writer_pairs': pairs, 'donors_per_first_writer': 549, 'first_donor_trials': trials,
            'exact_completions': len(solutions), 'scalar_improving': 52, 'frame_legal': 0,
            'domain': [{'centre': a, 'leaf': b, 'first_read_A': first[a], 'writers_A': writers[a]}
                       for a, b in sorted(star_domain(word)[1])],
            'solutions': rows, 'baseline_bill': base_bill, 'paid_profile': profile,
            'rank_mass': sum(r * c for r, c in profile.items()),
            'single_writer_positive': {'credit': 'Sagar Thakrar / PR1868', 'centre': 506, 'leaf': 374,
                                       'A_gate': 288, 'new_donors': [69], 'bill': positive_bill,
                                       'same_frame_paths_and_profile': True},
            'controls': controls, 'no_new_kappa': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate only this package certificate')
    args = parser.parse_args()
    # Normalize integer histogram keys before canonical comparison with JSON.
    report = json.loads(canonical(run(load_word())))
    path = HERE / 'CERTIFICATE.json'
    if args.write:
        path.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    else:
        need(canonical(report) == canonical(json.loads(path.read_text(encoding='utf-8'))), 'certificate mismatch')
    print('PASS_R439_TWO_WRITER_ABSORPTION pairs=414 trials=227286 exact=314 scalar_saving=52 legal=0 columns=661 controls=7 no_new_kappa')


if __name__ == '__main__':
    main()
