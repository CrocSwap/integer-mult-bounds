#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact fixed-continuation audit; no predecessor executable code is imported.

Arham Tahir, with substantial OpenAI Codex assistance. Checks remain active
under -O. Default replay is read-only and requires the committed certificate.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD_PATHS = {
    'pr967': 'research/r439-helper-stars-seed19/candidate.json.gz',
    'pr1062-composition': 'research/r439-bsection-stars-seed01/composition.json.gz',
    'pr1062-candidate': 'research/r439-bsection-stars-seed01/candidate.json.gz',
}
BASELINE = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
INPUTS = set(WORD_PATHS.values()) | {BASELINE, 'research/r439-omission-atlas-seed81/README.md'}
PROFILE = {'1': 1323, '2': 1342, '3': 79, '4': 44, '5': 102, '6': 11, '7': 19}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(data):
    def bad_constant(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(data, object_pairs_hook=unique_pairs, parse_constant=bad_constant)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_pins(root):
    pins = read_json((HERE / 'SOURCES.json').read_bytes())
    live = [entry for entry in pins['files'] if entry['usage'] == 'input']
    need(len(live) == len(INPUTS) and {entry['path'] for entry in live} == INPUTS, 'exact input pin inventory')
    for entry in live:
        data = (root / entry['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == entry['sha256'], 'source SHA256: ' + entry['path'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        need(blob == entry['git_blob'], 'source Git blob: ' + entry['path'])
    return pins['base_commit']


def load_word(root, path):
    return read_json(gzip.decompress((root / path).read_bytes()))


def expanded(word, sections):
    return [(dest, source) for section in sections for _, dest, sources in word[section] for source in sources]


def literal_stream(word, sections=('D', 'A', 'scatter', 'B', 'C')):
    n = 2 * word['v'] + word['R']
    stream = []
    for section in sections:
        if section == 'scatter':
            for j, center in enumerate(word['ret']):
                stream.append(('copy', n, center))
                stream.extend(('add', word['v'] + i, n) for i, sources in enumerate(word['scatter']) if j in sources)
                stream.append(('erase', n, center))
        else:
            stream.extend(('add', d, s) for d, s in expanded(word, (section,)))
    return stream


def literal_rows(stream, n, reverse=False):
    rows = [1 << i for i in range(n)] + [0]
    for kind, d, s in reversed(stream) if reverse else stream:
        if reverse and kind in ('copy', 'erase'):
            kind = 'erase' if kind == 'copy' else 'copy'
        if kind == 'add':
            rows[d] ^= rows[s]
        elif kind == 'copy':
            need(rows[d] == 0, 'COPY destination is live')
            rows[d] = rows[s]
        else:
            need(rows[d] == rows[s], 'ERASE center has changed')
            rows[d] = 0
    need(rows[n] == 0, 'copy temporary not cleared')
    return rows[:n]


def boolean_word(word, values, omit=(), append=()):
    """Separate direct interpreter: no bitset rows or literal-stream builder."""
    v = word['v']
    vals = list(values)
    omitted = set(omit)
    for section in ('D', 'A'):
        for index, (_, d, sources) in enumerate(word[section]):
            if section == 'D' and index in omitted:
                continue
            for source in sources:
                vals[d] = vals[d] != vals[source]
    for j, center in enumerate(word['ret']):
        copied = vals[center]
        for i, sources in enumerate(word['scatter']):
            if j in sources:
                vals[v + i] = vals[v + i] != copied
        need(copied == vals[center], 'Boolean ERASE center changed')
    for section in ('B', 'C'):
        for _, d, sources in word[section]:
            for source in sources:
                vals[d] = vals[d] != vals[source]
    for index in append:
        _, d, sources = word['D'][index]
        for source in sources:
            vals[d] = vals[d] != vals[source]
    return vals


def relocated(word, indices, append=True):
    variant = copy.deepcopy(word)
    selected = set(indices)
    full = next(i for i, frame in enumerate(word['frames']) if len(frame) == word['v'])
    gates = [[full, d, list(sources)] for index, (_, d, sources) in enumerate(word['D']) if index in selected]
    variant['D'] = [gate for index, gate in enumerate(variant['D']) if index not in selected]
    if append:
        variant['C'].extend(gates)
    return variant


def rank(rows):
    basis = {}
    for row in rows:
        row = list(map(Fraction, row))
        for column, pivot in sorted(basis.items()):
            scalar = row[column]
            row = [a - scalar * b for a, b in zip(row, pivot)]
        first = next((i for i, x in enumerate(row) if x), None)
        if first is not None:
            divisor = row[first]
            basis[first] = [x / divisor for x in row]
    return len(basis)


def frame_bill(word, dimensions):
    fs = list(map(set, word['frames']))
    current = list(word['start'])
    paths = [[f] for f in current]
    moves = Counter()
    copies = []
    def visit(register, frame):
        previous = current[register]
        if previous != frame:
            need(fs[previous] < fs[frame] and dimensions[previous] < dimensions[frame], 'non-nested MOVE')
            moves[dimensions[frame] - dimensions[previous]] += 1
            current[register] = frame
            paths[register].append(frame)
    for section in ('D', 'A', 'scatter', 'B', 'C'):
        if section == 'scatter':
            copies = [dimensions[current[q]] for q in word['ret']]
        else:
            for frame, dest, sources in word[section]:
                for register in (dest, *sources):
                    visit(register, frame)
    for register, frame in enumerate(word['final']):
        visit(register, frame)
    profile = moves + Counter(copies)
    return paths, {'moves': sum(moves.values()), 'copy_ranks': copies,
                   'profile': {str(k): profile[k] for k in sorted(profile)},
                   'rank_mass': sum(k * amount for k, amount in profile.items()),
                   'adds': sum(len(g[2]) for section in 'DABC' for g in word[section]) + sum(map(len, word['scatter']))}


def star_suffix(word):
    v = word['v']
    first = len(word['D'])
    while first and word['D'][first - 1][1] >= 2 * v:
        first -= 1
    suffix = []
    for index in range(first, len(word['D'])):
        frame, dest, sources = word['D'][index]
        need(frame == 0 and len(sources) == 1 and sources[0] >= 2 * v and dest != sources[0], 'restoration shape')
        suffix.append((index, dest, sources[0]))
    prep = word['D'][:len(suffix)]
    need(prep == list(reversed(word['D'][first:])), 'preparation/restoration symmetry')
    centers = {d for _, d, _ in suffix}
    leaves = [s for _, _, s in suffix]
    need(centers.isdisjoint(leaves) and len(set(leaves)) == len(leaves), 'distinct-leaf star geometry')
    need(max(Counter(d for _, d, _ in suffix).values()) <= 2, 'two-leaf star bound')
    return suffix


def expected_rows(n, v):
    return [(1 << i) ^ (1 << (i - v)) if v <= i < 2 * v else 1 << i for i in range(n)]


def audit_word(name, word, baseline, baseline_raw, dimensions):
    v, n = word['v'], 2 * word['v'] + word['R']
    need((v, word['R']) == (111, 439), 'R439 dimensions')
    want = expected_rows(n, v)
    raw = literal_rows(literal_stream(word, ('A', 'scatter', 'B')), n)
    full = next(i for i, frame in enumerate(word['frames']) if len(frame) == v)
    cleanup = [[full, d, list(sources)] for _, d, sources in reversed(word['A'] + word['B'])
               if d < v or d >= 2 * v]
    need(word['C'] == cleanup, 'baseline C is the literal z inverse')
    need(raw[v:2 * v] == baseline_raw[v:2 * v], 'fixed raw target response')
    ymask = ((1 << v) - 1) << v
    hmask = ((1 << word['R']) - 1) << (2 * v)
    xmask = (1 << v) - 1
    need(all(raw[r] & ymask == 0 for r in list(range(v)) + list(range(2 * v, n))), 'raw z must not read targets')
    need(all(raw[v + t] & (xmask | ymask) == (1 << t) | (1 << (v + t)) for t in range(v)), 'raw J/V identity')
    d = literal_rows(literal_stream(word, ('D',)), n)
    need(all(d[r] == 1 << r for r in list(range(v)) + list(range(2 * v, n))), 'D source/helper restoration')
    need(all(d[v + t] == (1 << (v + t)) | (raw[v + t] & hmask) for t in range(v)), 'semantic D matches raw K')
    need(literal_rows(literal_stream(word, ('A', 'scatter', 'B', 'C')), n)[2 * v:] == [1 << r for r in range(2 * v, n)], 'C restores raw helpers')
    for reverse in (False, True):
        need(literal_rows(literal_stream(word), n, reverse) == want, 'baseline complete dirty boundary')
    edges = star_suffix(word)
    centers = sorted({dest for _, dest, _ in edges})
    responses = {dest: [t for t in range(v) if raw[v + t] >> dest & 1] for dest in centers}
    need(all(responses.values()), 'a center is in the reader kernel; obstruction does not apply')
    paths, bill = frame_bill(word, dimensions)
    need(bill['profile'] == PROFILE and bill['rank_mass'] == 5129, 'baseline paid profile')
    records = []
    for index, dest, source in edges:
        changed = relocated(word, [index])
        expected = list(want)
        for t in responses[dest]:
            expected[v + t] ^= 1 << source
        # Complete independent chronological matrix replay for EVERY occurrence.
        for reverse in (False, True):
            need(literal_rows(literal_stream(changed), n, reverse) == expected, 'single relocation full syndrome')
        # Every single witness also passes through a separately written Boolean engine.
        singleton = [r == source for r in range(n)]
        observed = boolean_word(word, singleton, [index], [index])
        expected_bits = [bool(row >> source & 1) for row in expected]
        need(observed == expected_bits and observed != singleton, 'direct dirty witness')
        records.append({'D_record': index, 'center': dest, 'leaf': source,
                        'first_changed_target': v + responses[dest][0], 'changed_targets': len(responses[dest])})
    all_indices = [index for index, _, _ in edges]
    all_changed = relocated(word, all_indices)
    expected = list(want)
    for _, dest, source in edges:
        for t in responses[dest]:
            expected[v + t] ^= 1 << source
    for reverse in (False, True):
        need(literal_rows(literal_stream(all_changed), n, reverse) == expected, 'all-subset full replay')
    changed_paths, changed_bill = frame_bill(all_changed, dimensions)
    need(changed_paths == paths and changed_bill == bill, 'terminal relocation frame/bill equality')
    counts = Counter(len(responses[d]) for _, d, _ in edges)
    # A two-leaf star cancels its drift on all ones but fails on its leaf basis inputs.
    center = next(d for d in centers if sum(dest == d for _, dest, _ in edges) == 2)
    pair = [index for index, dest, _ in edges if dest == center]
    ones = [True] * n
    need(boolean_word(word, ones, pair, pair) == boolean_word(word, ones), 'all-ones cancellation fixture')
    pair_word = relocated(word, pair)
    need(literal_rows(literal_stream(pair_word), n) != want, 'all-ones is not a complete test')
    index, dest, source = edges[0]
    no_undo = relocated(word, [index], append=False)
    no_undo_rows = literal_rows(literal_stream(no_undo), n)
    need(no_undo_rows[dest] != want[dest], 'dirty helpers require eventual restoration')
    # Target-only D observation cannot certify a complete continuation.
    omitted_d = literal_rows(literal_stream(no_undo, ('D',)), n)
    need(omitted_d[v:2*v] == d[v:2*v] and omitted_d[dest] != d[dest], 'D target-only insufficiency')
    clean = [bool(r % 2) if r < 2 * v else False for r in range(n)]
    need(boolean_word(word, clean, [index], [index]) == boolean_word(word, clean), 'clean-only false acceptance')
    wrong_undo = relocated(word, [index])
    wrong_undo['C'][-1] = [full, source, [dest]]
    need(literal_rows(literal_stream(wrong_undo), n) != want, 'wrong-direction terminal undo')
    return {'name': name, 'source': WORD_PATHS[name], 'columns': n,
            'edges': len(edges), 'centers': len(centers), 'eligible_nonempty_subsets': 0,
            'excluded_nonempty_subsets': str((1 << len(edges)) - 1),
            'changed_target_weight_histogram': {str(k): counts[k] for k in sorted(counts)},
            'minimum_changed_targets_per_leaf_witness': min(counts),
            'raw_K_sha256': digest([row & hmask for row in raw[v:2*v]]),
            'center_response_sha256': digest(responses), 'single_relocations': records,
            'full_matrix_singleton_replays': 2 * len(edges), 'boolean_singleton_replays': len(edges),
            'all_edges_replays': 2, 'two_leaf_all_ones_counterexample': {'center': center, 'D_records': pair},
            'bill_unchanged_but_endpoint_invalid': bill}


def synthetic_positive():
    # Nontrivial deferred helper shear is valid when the reader annihilates it.
    word = {'v': 1, 'R': 2, 'frames': [[], [0]], 'ret': [], 'scatter': [[]],
            'D': [[0, 2, [3]], [0, 1, [3]], [0, 2, [3]]],
            'A': [], 'B': [[1, 1, [0]], [1, 1, [3]]], 'C': []}
    changed = relocated(word, [2])
    need(literal_rows(literal_stream(changed), 4) == expected_rows(4, 1), 'nontrivial kernel positive fixture')
    for value in range(16):
        inputs = [bool(value >> r & 1) for r in range(4)]
        need(boolean_word(word, inputs, [2], [2]) == boolean_word(word, inputs), 'all dirty kernel inputs')
    # A different K observes the center; omitted early restoration now leaks.
    observed = copy.deepcopy(word)
    observed['D'] = [[0, 2, [3]], [0, 1, [2, 3]], [0, 2, [3]]]
    observed['B'] = [[1, 1, [0]], [1, 1, [2]]]
    need(literal_rows(literal_stream(observed), 4) == expected_rows(4, 1), 'nonkernel baseline')
    need(literal_rows(literal_stream(relocated(observed, [2])), 4) != expected_rows(4, 1), 'nonkernel negative fixture')
    return {'arbitrary_inputs': 16, 'nontrivial_kernel_deferral': True, 'nonkernel_control_rejected': True}


def run(root):
    base = source_pins(root)
    baseline = load_word(root, BASELINE)
    raw = literal_rows(literal_stream(baseline, ('A', 'scatter', 'B')), 661)
    need(literal_rows(literal_stream(baseline), 661) == expected_rows(661, 111), 'PR589 positive control')
    dimensions = [rank([baseline['lines'][i] for i in frame]) for frame in baseline['frames']]
    words = []
    for name, path in WORD_PATHS.items():
        word = load_word(root, path)
        for field in ('v', 'R', 'lines', 'frames', 'start', 'final', 'ret', 'scatter'):
            need(word[field] == baseline[field], 'baseline field: ' + field)
        words.append(audit_word(name, word, baseline, raw, dimensions))
    return {'status': 'PASS_R439_TERMINAL_STAR_RESTORATION', 'base_commit': base,
            'scope': 'Only identical terminal relocation of any restoration subset across the fixed A/scatter/B/C continuation; arbitrary F2 inputs.',
            'criterion': 'K(S-I)=0; distinct leaf columns prevent cancellations between different edges.',
            'words': words, 'synthetic_positive': synthetic_positive(),
            'singleton_occurrences': sum(word['edges'] for word in words),
            'controls': ['nonkernel synthetic deferral', 'target-only D observation',
                         'all-ones whole-word observation', 'omitted eventual dirty restoration',
                         'clean-only whole-word observation', 'wrong-direction terminal undo'],
            'new_kappa': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=ROOT)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    report = run(args.source_root)
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    else:
        need(canonical(report) == canonical(read_json(path.read_bytes())), 'certificate mismatch')
    print('PASS_R439_TERMINAL_STAR_RESTORATION words=3 singletons=678 forward_reverse=1356 eligible_subsets=0 no_new_kappa')


if __name__ == '__main__':
    main()
