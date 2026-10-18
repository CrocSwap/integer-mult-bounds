#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound terminal repair obstruction; default verification is read-only.

Arham Tahir, with substantial OpenAI Codex assistance. No predecessor executable
is imported. All checks remain active with python -O.
"""
import argparse
from collections import Counter, deque
import copy
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORDS = {
    'pr967': 'research/r439-helper-stars-seed19/candidate.json.gz',
    'pr1062-composition': 'research/r439-bsection-stars-seed01/composition.json.gz',
    'pr1062-candidate': 'research/r439-bsection-stars-seed01/candidate.json.gz',
}
BASELINE = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
CHECKER = 'research/e8-bit-p111-tuned/code/xcheck_p.py'
INPUTS = set(WORDS.values()) | {BASELINE, CHECKER}
PROFILE = {'1': 1323, '2': 1342, '3': 79, '4': 44, '5': 102, '6': 11, '7': 19}


def need(test, message):
    if not test:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'duplicate key: ' + key)
        out[key] = value
    return out


def read(data):
    def bad(x):
        raise ValueError('nonfinite JSON: ' + x)
    return json.loads(data, object_pairs_hook=unique, parse_constant=bad)


def pins(root):
    source = read((HERE / 'SOURCES.json').read_bytes())
    live = [f for f in source['files'] if f['usage'] == 'input']
    need({f['path'] for f in live} == INPUTS and len(live) == len(INPUTS), 'input inventory')
    for f in live:
        data = (root / f['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == f['sha256'], 'source hash: ' + f['path'])
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == f['git_blob'], 'source blob')
    return source['base_commit']


def basis(vectors):
    pivots = {}
    for vector in vectors:
        v = list(map(Fraction, vector))
        for col, row in sorted(pivots.items()):
            a = v[col]
            v = [x - a * y for x, y in zip(v, row)]
        pivot = next((i for i, x in enumerate(v) if x), None)
        if pivot is not None:
            a = v[pivot]
            pivots[pivot] = [x / a for x in v]
    return list(pivots.values())


def contained(small, large):
    return len(small) <= len(large) and len(basis(large + small)) == len(large)


def stream(w, omit=(), sections=('D', 'A', 'scatter', 'B', 'C')):
    v, n = w['v'], 2 * w['v'] + w['R']
    out = []
    for section in sections:
        if section == 'scatter':
            for j, center in enumerate(w['ret']):
                out.append(('copy', n, center))
                out.extend(('xor', v + t, n) for t, ss in enumerate(w['scatter']) if j in ss)
                out.append(('erase', n, center))
        else:
            for i, (_, d, ss) in enumerate(w[section]):
                if section != 'D' or i not in omit:
                    out.extend(('xor', d, s) for s in ss)
    return out


def matrix(ops, n, backwards=False):
    rows = [1 << r for r in range(n)] + [0]
    for op, d, s in reversed(ops) if backwards else ops:
        if backwards and op != 'xor':
            op = 'erase' if op == 'copy' else 'copy'
        if op == 'xor':
            need(d != s, 'self XOR')
            rows[d] ^= rows[s]
        elif op == 'copy':
            need(rows[d] == 0, 'live copy destination')
            rows[d] = rows[s]
        else:
            need(rows[d] == rows[s], 'invalid erase')
            rows[d] = 0
    need(rows[n] == 0, 'uncleared temporary')
    return rows[:n]


def truth(w, values, omit, suffix):
    # Separate direct Boolean interpreter, without stream() or matrix().
    vals = list(values)
    v = w['v']
    for section in ('D', 'A', 'scatter', 'B', 'C'):
        if section == 'scatter':
            for j, q in enumerate(w['ret']):
                saved = vals[q]
                for t, ss in enumerate(w['scatter']):
                    if j in ss:
                        vals[v + t] = vals[v + t] != saved
                need(vals[q] == saved, 'Boolean copy was changed')
        else:
            for i, (_, d, ss) in enumerate(w[section]):
                if section == 'D' and i in omit:
                    continue
                for s in ss:
                    vals[d] = vals[d] != vals[s]
    for _, d, s in suffix:
        vals[d] = vals[d] != vals[s]
    return vals


def terminal_frames(w, dims):
    current = list(w['start'])
    paths = [[f] for f in current]
    climbs = Counter()
    sets = list(map(set, w['frames']))
    def visit(r, f):
        before = current[r]
        if before != f:
            need(sets[before] < sets[f] and dims[before] < dims[f], 'illegal original climb')
            climbs[dims[f] - dims[before]] += 1
            paths[r].append(f)
            current[r] = f
    copies = []
    for section in ('D', 'A', 'scatter', 'B', 'C'):
        if section == 'scatter':
            copies = [dims[current[r]] for r in w['ret']]
        else:
            for f, d, ss in w[section]:
                for r in [d] + ss:
                    visit(r, f)
    cut = list(current)
    for r, f in enumerate(w['final']):
        visit(r, f)
    profile = climbs + Counter(copies)
    need({str(k): profile[k] for k in sorted(profile)} == PROFILE, 'local profile')
    return cut, paths, sum(k * x for k, x in profile.items())


def groups(w):
    first = len(w['D'])
    while first and w['D'][first - 1][1] >= 2 * w['v']:
        first -= 1
    suffix = w['D'][first:]
    need(w['D'][:len(suffix)] == list(reversed(suffix)), 'star reverse prefix')
    by_center = {}
    for i, (f, d, ss) in enumerate(suffix, first):
        need(f == 0 and len(ss) == 1 and d != ss[0] and ss[0] >= 2 * w['v'], 'star geometry')
        by_center.setdefault(d, []).append((i, ss[0]))
    leaves = [s for values in by_center.values() for _, s in values]
    need(len(leaves) == len(set(leaves)) and set(leaves).isdisjoint(by_center), 'distinct leaf premise')
    need(set(map(len, by_center.values())) <= {1, 2}, 'one-/two-leaf stars only')
    return by_center


def repair(outputs, leaves):
    # All listed gates are elementary XORs. One dirty source is used as the
    # parity accumulator and restored, rather than allocating a clean wire.
    need(len(leaves) in (1, 2) and len(outputs) >= 2, 'repair domain')
    out = []
    if len(leaves) == 2:
        out.append(('xor', leaves[0], leaves[1]))
    out.extend(('xor', d, leaves[0]) for d in outputs)
    if len(leaves) == 2:
        out.append(('xor', leaves[0], leaves[1]))
    return out


def audit(name, w, original):
    v, n = w['v'], 2 * w['v'] + w['R']
    need((v, w['R']) == (111, 439), 'fixed dimensions')
    for field in ('v', 'R', 'lines', 'frames', 'start', 'final', 'ret', 'scatter'):
        need(w[field] == original[field], 'frozen field ' + field)
    bs = [basis([w['lines'][i] for i in f]) for f in w['frames']]
    dims = list(map(len, bs))
    cut, paths, mass = terminal_frames(w, dims)
    # These are actual post-C frames, not merely requested final frames.
    need(cut == w['final'], 'post-C must already equal final')
    full = next(i for i, f in enumerate(w['frames']) if len(f) == v)
    need(dims[full] == 8 and all(cut[r] == full for r in list(range(v)) + list(range(2*v, n))), 'full source/helper cut')
    targets = list(range(v, 2*v))
    need(all(dims[cut[t]] == 7 for t in targets), 'target rank seven')
    need(len({tuple(w['frames'][cut[t]]) for t in targets}) == v, 'distinct target frames')
    # Exact all-original-wire dependency cone for every prescribed output.
    cones = {}
    for t in targets:
        cones[t] = [r for r in range(n) if contained(bs[cut[r]], bs[w['final'][t]])]
        need(cones[t] == [t], 'terminal output has another admissible original contributor')
    want = [(1 << r) ^ (1 << (r-v)) if v <= r < 2*v else 1 << r for r in range(n)]
    need(matrix(stream(w), n) == want and matrix(stream(w), n, True) == want, 'original arbitrary dirty map')
    raw = matrix(stream(w, sections=('A', 'scatter', 'B')), n)
    stars = groups(w)
    records = []
    singletons = 0
    for center, entries in sorted(stars.items()):
        support = [t for t in targets if raw[t] >> center & 1]
        need(len(support) >= 8, 'nonzero reader premise')
        for size in range(1, len(entries)+1):
            for chosen in itertools.combinations(entries, size):
                omitted = {i for i, _ in chosen}
                leaves = [s for _, s in chosen]
                delta = sum(1 << s for s in leaves)
                broken = matrix(stream(w, omitted), n)
                expected = list(want)
                expected[center] ^= delta
                for t in support:
                    expected[t] ^= delta
                need(broken == expected, 'exact uncorrected terminal defect')
                outputs = [center] + support
                suffix = repair(outputs, leaves)
                minimum = len(outputs) + (2 if size == 2 else 0)
                need(len(suffix) == minimum, 'sharp scalar invoice')
                ops = stream(w, omitted) + suffix
                for backwards in (False, True):
                    need(matrix(ops, n, backwards) == want, 'repaired full dirty map')
                # Witness for the frame barrier, independently interpreted.
                witness = [r == leaves[0] for r in range(n)]
                repaired = truth(w, witness, omitted, suffix)
                bad = truth(w, witness, omitted, [])
                need(repaired == witness and bad[support[0]] and not repaired[support[0]], 'Boolean dirty witness')
                # The required correction cannot be supplied by the only
                # original cut input in this target's legal dependency cone.
                t = support[0]
                need(broken[t] != want[t] and broken[t] >> t & 1 and want[t] >> t & 1, 'one-dimensional cone mismatch')
                # Frame-free witness fails the actual common-frame rule:
                # its first helper-to-target gate needs rank eight > final seven.
                first_target = next((d, s) for _, d, s in suffix if v <= d < 2*v)
                d, s = first_target
                need(dims[cut[s]] == 8 and dims[w['final'][d]] == 7, 'witness frame violation')
                singletons += size == 1
                records.append({'center': center, 'leaves': leaves, 'D_records': sorted(omitted),
                                'target_count': len(support), 'repair_minimum_XORs_without_frames': minimum,
                                'removed_XORs': size, 'net_extra_XORs_without_frames': minimum-size})
    return {'name': name, 'columns': n, 'star_centers': len(stars), 'singletons': singletons,
            'within_star_nonempty_subsets': len(records),
            'center_target_supports': {str(c): [t for t in targets if raw[t] >> c & 1] for c in sorted(stars)},
            'target_cones': {str(k): val for k, val in cones.items()},
            'post_C_ranks': {'sources': 8, 'helpers': 8, 'targets': 7},
            'blocked_arbitrary_nonempty_restoration_subsets': str((1 << singletons)-1),
            'rank_mass': mass, 'paid_profile': PROFILE,
            'ordered_frame_paths_sha256': hashlib.sha256(canonical(paths)).hexdigest(),
            'relaxed_repairs': records}


def tiny_distance(n, goal, bound):
    start = tuple(1 << i for i in range(n))
    seen = {start}
    q = deque([(start, 0)])
    while q:
        state, depth = q.popleft()
        if state == tuple(goal):
            return depth
        if depth == bound:
            continue
        for d in range(n):
            for s in range(n):
                if d == s:
                    continue
                other = list(state)
                other[d] ^= other[s]
                key = tuple(other)
                if key not in seen:
                    seen.add(key)
                    q.append((key, depth+1))
    return None


def controls():
    # Small independent shortest-path check includes one arbitrary dirty extra.
    goal = [1, 2, 4 ^ 1 ^ 2, 8 ^ 1 ^ 2, 16]
    need(tiny_distance(5, goal, 3) is None, 'no <4-gate two-by-two repair')
    good = repair([2, 3], [0, 1])
    need(matrix(good, 5) == goal and len(good) == 4, 'four-gate attainment')
    need(matrix(good[:-1], 5) != goal, 'missing source restoration')
    need(matrix([op for op in good if op[1] != 3], 5) != goal, 'missing output correction')
    # Dirty rather than clean extra is essential to the lower-bound domain.
    need(matrix(repair([1, 2], [0]), 3) == [1, 3, 5], 'one-source target-write floor')
    need(matrix([('xor', 2, 0), ('xor', 2, 1)], 3) == [1, 2, 7], 'one-output two-source exception')
    # Concrete frame test: a low scratch cannot relay a full-frame bit to a
    # rank-one output; promoting the scratch leaves its final edge illegal.
    low, high = basis([[1, 0]]), basis([[1, 0], [0, 1]])
    need(not contained(high, low) and contained(low, high), 'monotone frame direction')
    # When the target-final constraint changes, the scalar repair is valid.
    need(contained(high, high), 'full-output positive fixture')
    # Rows agreeing on target dirt can still disagree on helper dirt.
    need((4 ^ 1) & 4 == 4 and (4 ^ 1) != 4, 'target-only projection false acceptance')
    return ['shorter-word exclusion with dirty extra', 'missing parity undo', 'missing target repair',
            'one-source attainment', 'one-output exception', 'no low-scratch relay',
            'promoted-output positive fixture', 'target-projection false acceptance']


def run(root):
    base = pins(root)
    original = read(gzip.decompress((root / BASELINE).read_bytes()))
    words = [audit(name, read(gzip.decompress((root / path).read_bytes())), original) for name, path in WORDS.items()]
    return {'status': 'PASS_R439_TERMINAL_REPAIR_BARRIER', 'base_commit': base,
            'scope': 'Arbitrary appended elementary XOR suffix, monotone common frames and prescribed final target frames; independent dirty added wires; fixed earlier continuation.',
            'words': words, 'controls': controls(), 'new_kappa': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, default=ROOT)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    report = run(args.source_root)
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(report, indent=2) + '\n')
    else:
        need(canonical(report) == canonical(read(path.read_bytes())), 'certificate mismatch')
    count = sum(len(w['relaxed_repairs']) for w in report['words'])
    print('PASS_R439_TERMINAL_REPAIR_BARRIER words=3 targets=333 sharp_relaxed_repairs=%d no_new_kappa' % count)


if __name__ == '__main__':
    main()
