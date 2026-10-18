#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Arham Tahir, with substantial OpenAI Codex assistance.
"""Independent rational dependency-span and paid-path audit; see README.md.

No predecessor implementation is imported. Checks remain active with -O.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    'pr589': 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz',
    'helper_star': 'research/r439-helper-stars-seed19/candidate.json.gz',
    'composition': 'research/r439-bsection-stars-seed01/composition.json.gz',
    'candidate': 'research/r439-bsection-stars-seed01/candidate.json.gz',
}
# Slices in PR589 and helper_star; spliced words have different offsets.
BLOCKS = ((506, 102, 128), (507, 128, 163), (519, 163, 205),
          (508, 205, 242), (520, 242, 283), (509, 283, 314),
          (521, 314, 361), (522, 361, 404), (523, 404, 449), (524, 449, 490))
BASE_PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
BLOCKED = (506, 507, 519, 520, 521, 522, 523, 524)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    pins = {r['path']: r for r in manifest['files'] if r['usage'] == 'input'}
    require(set(pins) == set(INPUTS.values()), 'live source inventory')
    words = {}
    for name, path in INPUTS.items():
        raw = (ROOT / path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pins[path]['sha256'], 'source pin: ' + path)
        words[name] = json.loads(gzip.decompress(raw))
    return words


def span_basis(lines, indices):
    """Exact rational basis returned as a subset of the supplied root indices."""
    pivots, chosen = {}, []
    for i in sorted(set(indices)):
        row = list(map(Fraction, lines[i]))
        for p in sorted(pivots):
            t = row[p]
            if t:
                row = [x - t * y for x, y in zip(row, pivots[p])]
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            t = row[p]
            pivots[p] = [x / t for x in row]
            chosen.append(i)
    return chosen


def paths_and_profile(w):
    fs = [set(f) for f in w['frames']]
    dims = [len(span_basis(w['lines'], f)) for f in fs]
    paths = [[f] for f in w['start']]
    for sec in 'DABC':
        for f, d, ss in w[sec]:
            require(ss and all(s != d for s in ss), 'gate source')
            for r in (d, *ss):
                old = paths[r][-1]
                if old != f:
                    require(fs[old] < fs[f], 'non-nested gate frame')
                    paths[r].append(f)
        if sec == 'A':
            copies = [dims[paths[r][-1]] for r in w['ret']]
    for r, f in enumerate(w['final']):
        old = paths[r][-1]
        if old != f:
            require(fs[old] < fs[f], 'non-nested final frame')
            paths[r].append(f)
    prof = Counter(copies)
    for path in paths:
        for a, b in zip(path, path[1:]):
            require(dims[b] > dims[a], 'zero-rank climb')
            prof[dims[b] - dims[a]] += 1
    return paths, dict(sorted(prof.items())), copies


def block_matrix(ops, regs, frame=None):
    index = {r: i for i, r in enumerate(regs)}
    rows = [1 << i for i in range(len(regs))]
    for f, d, ss in ops:
        require(frame is None or f == frame, 'block operation frame')
        require(d in index and all(s in index and s != d for s in ss), 'block wire alphabet')
        for s in ss:
            rows[index[d]] ^= rows[index[s]]
    return rows


def inverse_rows(rows):
    n = len(rows)
    aug = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for p in range(n):
        k = next((k for k in range(p, n) if aug[k] >> p & 1), None)
        require(k is not None, 'singular block map')
        aug[p], aug[k] = aug[k], aug[p]
        for k in range(n):
            if k != p and aug[k] >> p & 1:
                aug[k] ^= aug[p]
    require([row & ((1 << n) - 1) for row in aug] == [1 << i for i in range(n)], 'inverse reduction')
    return [row >> n for row in aug]


def source_prefix_obstruction(w, frame, regs, entry, rows, source):
    """Unique star P making M P fix the exceptional source row and column."""
    i = regs.index(source)
    require(rows[i] == 1 << i, 'exceptional source is modified')
    inv = inverse_rows(rows)
    mask = sum((row >> i & 1) << j for j, row in enumerate(inv)) ^ (1 << i)
    require(mask and not (mask >> i & 1), 'source-prefix shape')
    require([((row & mask).bit_count() % 2) ^ (row >> i & 1) for row in rows]
            == [int(j == i) for j in range(len(regs))], 'source-prefix residual column')
    donors = [r for j, r in enumerate(regs) if mask >> j & 1]
    required = {root for r in [source, *donors] for root in w['frames'][entry[r]]}
    basis = span_basis(w['lines'], required)
    require(len(basis) == 4, 'source-prefix obstruction premise failed')
    return {'source': source, 'unique_prefix_donors': donors,
            'required_prefix_root_basis': basis, 'required_prefix_rank': len(basis)}


def dependency_obligation(w, frame, regs, entry, rows):
    """Exit-frame lower bounds from output support and monotone nesting."""
    require(len(rows) == len(regs) and all(0 <= x < 1 << len(regs) for x in rows), 'matrix shape')
    fs = [set(x) for x in w['frames']]
    full = fs[frame]
    require(len(span_basis(w['lines'], full)) == 4, 'block rank')
    out = []
    for i, r in enumerate(regs):
        require(fs[entry[r]] <= full, 'entry outside block frame')
        inputs = [s for j, s in enumerate(regs) if rows[i] >> j & 1]
        required = set(fs[entry[r]])
        for s in inputs:
            require(fs[entry[s]] <= full, 'dependency entry outside block frame')
            required.update(fs[entry[s]])
        basis = span_basis(w['lines'], required)
        essential = rows[i] != 1 << i or any(
            bool(rows[j] >> i & 1) != (i == j) for j in range(len(regs)))
        require(essential, 'identity wire can be omitted')
        out.append({'register': r, 'entry_frame': entry[r],
                    'entry_rank': len(span_basis(w['lines'], fs[entry[r]])),
                    'output_inputs': inputs, 'required_root_basis': basis,
                    'forced_exit_rank': len(basis)})
    return out


def prove_block(w, frame, a, b):
    ops = w['B'][a:b]
    require(ops and all(f == frame for f, _, _ in ops), 'block slice')
    regs = sorted({r for _, d, ss in ops for r in (d, *ss)})
    require(all(r < w['v'] or r >= 2 * w['v'] for r in regs), 'block changes target wire')
    entry = list(w['start'])
    for sec in 'DA':
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                entry[r] = f
    for f, d, ss in w['B'][:a]:
        for r in (d, *ss):
            entry[r] = f
    rows = block_matrix(ops, regs, frame)
    dependencies = dependency_obligation(w, frame, regs, entry, rows)
    weak = [r['register'] for r in dependencies if r['forced_exit_rank'] != 4]
    require(not weak if frame in BLOCKED else weak == ([19] if frame == 508 else [22]),
            'lower-frame obstruction premise failed')
    report = {'frame': frame, 'slice': [a, b], 'registers': regs,
            'matrix_rows': rows, 'original_adds': sum(len(g[2]) for g in ops),
            'dependencies': dependencies, 'weak_wires': weak, 'lower_frame_barrier': not weak}
    if weak:
        report['source_prefix_obstruction'] = source_prefix_obstruction(w, frame, regs, entry, rows, weak[0])
    return report


def literal_endpoint(w, reverse=False):
    """All arbitrary dirty columns, with one explicitly clean COPY temporary."""
    n = 2 * w['v'] + w['R']
    ops = [('add', d, s) for sec in 'DA' for _, d, ss in w[sec] for s in ss]
    for j, r in enumerate(w['ret']):
        ops.append(('copy', n, r))
        ops.extend(('add', w['v'] + i, n) for i, ss in enumerate(w['scatter']) if j in ss)
        ops.append(('erase', n, r))
    ops.extend(('add', d, s) for sec in 'BC' for _, d, ss in w[sec] for s in ss)
    rows = [1 << i for i in range(n)] + [0]
    for kind, d, s in (reversed(ops) if reverse else ops):
        if reverse:
            kind = {'copy': 'erase', 'erase': 'copy'}.get(kind, kind)
        if kind == 'add':
            rows[d] ^= rows[s]
        elif kind == 'copy':
            require(rows[d] == 0, 'COPY temporary not clean')
            rows[d] = rows[s]
        else:
            require(rows[d] == rows[s], 'ERASE mismatch')
            rows[d] = 0
    want = [((1 << i) ^ (1 << (i - w['v']))) if w['v'] <= i < 2 * w['v']
            else 1 << i for i in range(n)] + [0]
    require(rows == want, 'literal dirty endpoint')


def run(words):
    baseline = words['pr589']
    require(baseline['v'] == 111 and baseline['R'] == 439, 'word dimensions')
    base_paths, base_profile, copies = paths_and_profile(baseline)
    require(base_profile == BASE_PROFILE and copies == [7] * 9, 'baseline paid profile')
    blocks = [prove_block(baseline, *b) for b in BLOCKS]
    require(sum(len(b['registers']) for b in blocks) ==
            len({r for b in blocks for r in b['registers']}), 'blocks share wires')
    reports = {}
    for name, w in words.items():
        for field in ('v', 'R', 'lines', 'frames', 'start', 'final', 'ret', 'scatter', 'A'):
            require(w[field] == baseline[field], 'outside interface drift: ' + field)
        paths, prof, cr = paths_and_profile(w)
        require(paths == base_paths and prof == base_profile and cr == copies, 'reference itinerary drift')
        full = next(i for i, f in enumerate(w['frames']) if len(f) == w['v'])
        cleanup = [[full, d, ss] for _, d, ss in reversed(w['A'] + w['B'])
                   if d < w['v'] or d >= 2 * w['v']]
        require(w['C'] == cleanup, 'nonliteral cleanup')
        for old in blocks:
            frame = old['frame']
            positions = [i for i, g in enumerate(w['B']) if g[0] == frame]
            require(positions and positions == list(range(positions[0], positions[-1] + 1)), 'noncontiguous block')
            ops = w['B'][positions[0]:positions[-1] + 1]
            require(block_matrix(ops, old['registers'], frame) == old['matrix_rows'], 'block map changed')
            require({r for _, d, ss in ops for r in (d, *ss)} == set(old['registers']), 'block wire set changed')
        literal_endpoint(w)
        literal_endpoint(w, reverse=True)
        reports[name] = {'complete_adds': sum(len(g[2]) for sec in 'DABC' for g in w[sec])
            + sum(len(ss) for ss in w['scatter']), 'profile': prof,
            'copy_ranks': cr, 'ordered_paths_sha256': hashlib.sha256(canonical(paths)).hexdigest(),
            'dirty_columns': 661, 'orientations': 2}
    require([reports[n]['complete_adds'] for n in INPUTS] == [24305, 11783, 11515, 11500], 'positive fixture counts')
    climbs = Counter(4 - d['entry_rank'] for b in blocks if b['lower_frame_barrier'] for d in b['dependencies'])
    climbs.pop(0, None)
    return {'status': 'PASS_R439_BBLOCK_FRAME_BARRIER', 'blocked_frames': list(BLOCKED),
            'blocked_wire_incidents': sum(len(b['registers']) for b in blocks if b['lower_frame_barrier']),
            'forced_exit_incidents': sum(d['forced_exit_rank'] == 4 for b in blocks for d in b['dependencies']),
            'exceptions': {'508': 19, '509': 22}, 'baseline_block_climbs': dict(sorted(climbs.items())),
            'moment_domain': '0 < a < 1; operation frames contained in the named rank-four block frame',
            'blocks': blocks, 'word_fixtures': reports,
            'not_checked': ['native/hosted admission', 'replacement bit interface',
                'frames outside the block frame', 'additional wires or cross-block rewrites',
                'all-size realization, precision/tape, analytic transfer, proof-assistant formalization']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-certificate', action='store_true')
    args = ap.parse_args()
    report = run(load_sources())
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    else:
        require(canonical(report) == canonical(json.loads(path.read_text(encoding='utf-8'))), 'certificate mismatch')
    print('PASS_R439_BBLOCK_FRAME_BARRIER blocks=8/10 blocked_wires=92 forced_exits=112/114 '
          'exceptions=508:19,509:22 fixtures=4 no_new_kappa')


if __name__ == '__main__':
    main()
