#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Ross Richardson, with substantial OpenAI Codex assistance.
"""Exact instance data for the written dirty-workspace theorem in README.md.
No predecessor implementation is imported. All checks survive -O.
"""
import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORDS = (
    'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
    'research/r439-bsection-stars-seed01/candidate.json.gz',
)
PRIOR = 'research/r439-bblock-frame-barrier/CERTIFICATE.json'
FRAMES = (506, 507, 519, 508, 520, 509, 521, 522, 523, 524)
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def pinned(root=ROOT):
    pins = json.loads((HERE / 'SOURCES.json').read_text())['files']
    pins = {p['path']: p for p in pins if p['usage'] == 'input'}
    need(set(pins) == {*WORDS, PRIOR}, 'input inventory')
    result = {}
    for path, pin in pins.items():
        data = (root / path).read_bytes()
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source SHA256: ' + path)
        blob = b'blob ' + str(len(data)).encode() + b'\0' + data
        need(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'source Git blob: ' + path)
        result[path] = json.loads(gzip.decompress(data) if path.endswith('.gz') else data)
    return result


def invert(rows):
    n = len(rows)
    a = [r | (1 << (n + i)) for i, r in enumerate(rows)]
    for c in range(n):
        p = next((i for i in range(c, n) if (a[i] >> c) & 1), None)
        need(p is not None, 'singular matrix')
        a[p], a[c] = a[c], a[p]
        for i in range(n):
            if i != c and ((a[i] >> c) & 1):
                a[i] ^= a[c]
    need([r & ((1 << n) - 1) for r in a] == [1 << i for i in range(n)], 'inverse left half')
    inverse = [r >> n for r in a]
    for left, right in ((rows, inverse), (inverse, rows)):
        for i, row in enumerate(left):
            out = 0
            for j, value in enumerate(right):
                if (row >> j) & 1:
                    out ^= value
            need(out == 1 << i, 'two-sided inverse')
    return inverse


def geometry(word):
    lines = word['lines']

    @lru_cache(None)
    def basis(indices):
        pivots, chosen = {}, []
        for index in indices:
            row = list(map(Fraction, lines[index]))
            for c in sorted(pivots):
                factor = row[c]
                if factor:
                    row = [x - factor * y for x, y in zip(row, pivots[c])]
            c = next((j for j, x in enumerate(row) if x), None)
            if c is not None:
                pivots[c] = [x / row[c] for x in row]
                chosen.append(index)
        return tuple(chosen)

    def span(indices):
        return basis(tuple(sorted(set(indices))))
    return span


def describe(word):
    need(word['v'] == 111 and word['R'] == 439, 'word dimensions')
    n = 2 * word['v'] + word['R']
    span = geometry(word)
    frames = [set(f) for f in word['frames']]
    dims = [len(span(f)) for f in frames]
    paths = [[f] for f in word['start']]
    entries, ranges = {}, {}
    for frame in FRAMES:
        ix = [i for i, g in enumerate(word['B']) if g[0] == frame]
        need(ix and ix == list(range(ix[0], ix[-1] + 1)), 'contiguous block')
        ranges[frame] = (ix[0], ix[-1] + 1)
    for section in 'DABC':
        for k, (frame, dest, sources) in enumerate(word[section]):
            if section == 'B' and frame in ranges and k == ranges[frame][0]:
                entries[frame] = [p[-1] for p in paths]
            need(sources and all(0 <= s < n and s != dest for s in sources), 'ADD operands')
            for r in (dest, *sources):
                old = paths[r][-1]
                if old != frame:
                    need(frames[old] < frames[frame] and dims[old] < dims[frame], 'monotone frame')
                    paths[r].append(frame)
        if section == 'A':
            copies = [dims[paths[r][-1]] for r in word['ret']]
    for r, final in enumerate(word['final']):
        old = paths[r][-1]
        if old != final:
            need(frames[old] < frames[final] and dims[old] < dims[final], 'final frame')
            paths[r].append(final)
    profile = Counter(copies)
    for path in paths:
        profile.update(dims[b] - dims[a] for a, b in zip(path, path[1:]))
    need(dict(profile) == PROFILE and copies == [7] * 9, 'whole-word paid invoice')
    full = next(i for i, f in enumerate(frames) if len(f) == 111)
    cleanup = [[full, d, ss] for _, d, ss in reversed(word['A'] + word['B'])
               if d < 111 or d >= 222]
    need(word['C'] == cleanup, 'literal cleanup')
    blocks = []
    for frame in FRAMES:
        begin, end = ranges[frame]
        ops = word['B'][begin:end]
        regs = sorted({r for _, d, ss in ops for r in (d, *ss)})
        need(all(r < 111 or r >= 222 for r in regs), 'source/helper block only')
        index = {r: i for i, r in enumerate(regs)}
        rows = [1 << i for i in range(len(regs))]
        for _, d, ss in ops:
            for s in ss:
                rows[index[d]] ^= rows[index[s]]
        inverse = invert(rows)
        entry = [entries[frame][r] for r in regs]
        need(dims[frame] == 4, 'block rank four')
        obligations = []
        for i, r in enumerate(regs):
            forward = [j for j in range(len(regs)) if (rows[i] >> j) & 1]
            dual = [j for j in range(len(regs)) if (inverse[j] >> i) & 1]
            forward_roots = {root for j in {i, *forward} for root in frames[entry[j]]}
            origins = {}
            for j in sorted({i, *forward, *dual}):
                for root in sorted(frames[entry[j]]):
                    origins.setdefault(root, regs[j])
            need(set(origins) <= frames[frame], 'entry outside block frame')
            roots = span(origins)
            need(len(roots) == 4, 'unforced full-frame exit')
            obligations.append({'register': r, 'forward_inputs': [regs[j] for j in forward],
                'inverse_outputs': [regs[j] for j in dual],
                'forward_rank': len(span(forward_roots)), 'forced_rank': len(roots),
                'witness': [[origins[root], root] for root in roots]})
        climbs = Counter(4 - dims[f] for f in entry)
        climbs.pop(0, None)
        blocks.append({'frame': frame, 'registers': regs, 'entry_frames': entry,
            'entry_ranks': [dims[f] for f in entry], 'matrix_rows': rows,
            'inverse_rows': inverse, 'obligations': obligations,
            'minimum_climbs': dict(sorted(climbs.items()))})
    need(sum(len(b['registers']) for b in blocks) == len({r for b in blocks for r in b['registers']}),
         'overlapping original block wires')
    return blocks, {'profile': dict(sorted(profile.items())),
        'rank_mass': sum(r * c for r, c in profile.items()), 'copy_ranks': copies,
        'ordered_paths_sha256': hashlib.sha256(canonical(paths)).hexdigest(),
        'scalar_ADDs': sum(len(ss) for sec in 'DABC' for _, _, ss in word[sec])
                       + sum(len(ss) for ss in word['scatter'])}


def compute(inputs):
    blocks, baseline = describe(inputs[WORDS[0]])
    other, candidate = describe(inputs[WORDS[1]])
    need(blocks == other, 'changed block boundary')
    need(baseline['ordered_paths_sha256'] == candidate['ordered_paths_sha256'], 'path drift')
    need([baseline['scalar_ADDs'], candidate['scalar_ADDs']] == [24305, 11500], 'fixture counts')
    # Prior data is compared only after reconstructing the source instances.
    prior = inputs[PRIOR]
    for block, old in zip(blocks, prior['blocks'], strict=True):
        for field in ('frame', 'registers', 'matrix_rows'):
            need(block[field] == old[field], 'predecessor boundary mismatch: ' + field)
    total = Counter()
    for block in blocks:
        total.update(block['minimum_climbs'])
    need(dict(total) == {2: 93, 3: 10}, 'ten-block invoice')
    need(sum(len(b['registers']) for b in blocks) == 114, '114 original wires')
    return {'schema_version': 1, 'status': 'PASS_R439_DIRTY_WORKSPACE_FRAME_BOUND',
        'no_new_kappa': True, 'blocks': blocks, 'original_wire_count': 114,
        'minimum_original_climbs': dict(sorted(total.items())),
        'minimum_original_rank_mass': sum(r * c for r, c in total.items()),
        'forward_forced_wire_count': sum(o['forward_rank'] == 4 for b in blocks for o in b['obligations']),
        'moment_domain': '0 < q = 1-a < 1',
        'normalization': 'Complete frame-moment comparison holds at identical caller width, role denominator W, fixed outside visits and other charges. Changing W, hosting or precision requires separate pricing.',
        'workspace_scope': 'Any finite number of independent dirty Boolean wires; arbitrary reversible local gates; all operands share a monotone frame inside the block frame. Original output map holds for every workspace input. Workspace output garbage is allowed for this lower bound.',
        'fixtures': {'pr589': baseline, 'pr1062': candidate}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=ROOT)
    ap.add_argument('--write-certificate', action='store_true')
    args = ap.parse_args()
    result = compute(pinned(args.root))
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(canonical(result) == canonical(json.loads(path.read_text())), 'certificate mismatch')
    print('PASS_R439_DIRTY_WORKSPACE_FRAME_BOUND blocks=10 original_wires=114 '
          'minimum=93H2+10H3 mass=216 no_new_kappa')


if __name__ == '__main__':
    main()
