#!/usr/bin/env python3
"""Build a rank-8 quotient of the complex supplier. Apache-2.0.

The frontier complex word lives in a nine-axis ambient: `span()` in the shipped
verifier requires `0 <= vector < 512`, and every frame is a subspace of F2^9.
For any nonzero KERNEL the map

    phi(v) = v xor KERNEL when the pivot bit is set, then the pivot is dropped

is linear, surjective onto F2^8, and has kernel span{KERNEL}.  `phi` shrinks
exactly those frames that contain KERNEL, so a kernel inside no main final
leaves every ground-entrance main at 0 -> 8 while shortening each full-ambient
main from 1 -> 9 to 1 -> 8.  Main rank mass then falls below 1,792 and the local
deficit below 1,856.

Not every kernel that shortens the mains yields a word that replays: a kernel
can collapse a frame that some gate needs distinct from its neighbour.  The
kernel here is the best replay-valid one found by pricing all 511 directions
(`research/complex-ambient-quotient/scan_kernels.py`).

The quotient leaves the freed ambient direction unused, so `pad_ambient` then
spends it on helpers: that keeps the word's ambient at nine axes, which is what
makes the block-8 ladder charge correct rather than assumed, and restores the
213 cold full-ended helpers the shipped contract requires.

This builder writes the quotiented word and both quotiented programs.

    python3 -B build.py
"""
import gzip
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
JOINT = ROOT/'research/joint-helper-lattice'
sys.path.insert(0, str(JOINT))
sys.path.insert(0, str(ROOT/'research/fresh-helper-boundary'))

import native as F  # noqa: E402

need = F.need


def construct(patch, allow_main_entrances=False, return_raw=False):
    c = F.read(F.BASE/'THREE-base-FULL-IDENTITY-CANONICAL.json.gz')
    original = F.read(F.BASE/'THREE-base-FULL-IDENTITY-NATIVE.json.gz')
    parent = F.read(F.HERE/'CHANGES.json')
    maps = {d: F.gates(p) for d, p in original.items()}
    need(set(maps['forward']) == set(maps['backward']), 'Same scalar contact inventory')
    for key in maps['forward']:
        f = original['forward'][maps['forward'][key]]
        b = original['backward'][maps['backward'][key]]
        need(b[1] == F.dual(f[1]) and b[2] == f[2], 'Retained exact dual scalar words')
    for key, field in [('entrances', 'start'), ('exits', 'final')]:
        for r, old, new in parent[key]:
            need(c[field][r] == old, 'Parent boundary pin')
            c[field][r] = new
    for phase, ordinal, old, new in parent['gates']:
        for d, p in original.items():
            i = maps[d][phase, ordinal]
            need(p[i][2] == old, 'Parent scalar pin')
            p[i][2] = new
    prior = F.read(ROOT/'research/missing-join-frame/PATCH.json')
    need(prior['phase'] == 'B' and prior['ordinal'] == 480, 'Exact prior contact')
    prior_frame = len(c['frames'])
    c['frames'].append(prior['new_basis'])
    for d, p in original.items():
        i = maps[d]['B', 480]
        need(p[i][2] == prior['old_frame'], 'Missing-span parent pin')
        p[i][2] = prior_frame
    baseline = deepcopy(c)
    before = {d: F.synthesize(c, p) for d, p in original.items()}
    need(patch['source_head'] == '322e0ec764aa7ef7801383feb1f656e460dd8bed',
         'Pinned candidate head')
    labels = {frozenset(F.span(b)): i for i, b in enumerate(c['frames'])}

    def label(b):
        s = frozenset(F.span(b))
        need(len(s) == 2**len(b), 'Independent binary basis')
        if s not in labels:
            labels[s] = len(c['frames'])
            c['frames'].append(b)
        return labels[s]

    seen = set()
    counts = Counter()
    for move in patch['changes']:
        phase, r = move['phase'], move['ordinal']
        key = (phase, r)
        need(key not in seen, 'No duplicate changed boundary/contact')
        seen.add(key)
        a, b = F.span(move['old']), F.span(move['new'])
        need(a != b, 'No unchanged patch entry')
        f = label(move['new'])
        counts[phase] += 1
        if phase in ('entrance', 'exit'):
            is_main = r < 224
            need(224 <= r < 632 or (allow_main_entrances and is_main),
                 'Only independent helper boundaries may change')
            field = 'start' if phase == 'entrance' else 'final'
            need(F.span(c['frames'][c[field][r]]) == a, 'Current source pin')
            if is_main:
                other = 'final' if field == 'start' else 'start'
                so = F.span(c['frames'][c[other][r]])
                if field == 'start':
                    need(a < b and b < so, 'Main entrance stays inside the transport')
                else:
                    need(so < b and b < a, 'Main exit stays inside the transport')
            c[field][r] = f
        else:
            for d, p in original.items():
                i = maps[d][key]
                need(F.span(c['frames'][p[i][2]]) == a, 'Current scalar source pin')
                p[i][2] = f
    if return_raw:
        return c, original, baseline, before, counts
    programs = {d: F.synthesize(c, p) for d, p in original.items()}
    return c, programs, baseline, before, counts

KERNEL = 153
_PIVOT = (KERNEL & -KERNEL).bit_length()-1


def phi(v):
    """Surjection onto F2^8 with kernel span{KERNEL}.

    Pivot on the lowest set bit of KERNEL: when it is set, xor KERNEL away, then
    drop that coordinate.  Two vectors collide exactly when they differ by
    KERNEL, so the kernel is the line spanned by it.
    """
    if (v >> _PIVOT) & 1:
        v ^= KERNEL
    low = v & ((1 << _PIVOT) - 1)
    high = v >> (_PIVOT + 1)
    return low | (high << _PIVOT)


def span_of(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in out}
    return frozenset(out)


def dedupe(vectors):
    pivots = {}
    keep = []
    for v in vectors:
        y = v
        while y:
            bit = y.bit_length()-1
            if bit in pivots:
                y ^= pivots[bit]
            else:
                pivots[bit] = y
                keep.append(v)
                break
    return keep


def quotient(base_word, base_programs):
    frames = base_word['frames']
    span_index = {}
    new_frames = []

    def frame_index(basis):
        mapped = dedupe([phi(v) for v in basis])
        key = span_of(mapped)
        if key not in span_index:
            span_index[key] = len(new_frames)
            new_frames.append(mapped)
        return span_index[key]

    remap = {i: frame_index(basis) for i, basis in enumerate(frames)}
    word = deepcopy(base_word)
    for r in range(len(word['start'])):
        word['start'][r] = remap[word['start'][r]]
        word['final'][r] = remap[word['final'][r]]
    programs = {}
    for direction, program in base_programs.items():
        out = []
        for event in program:
            e = deepcopy(event)
            if e[0] == 'scalar':
                e[2] = remap[e[2]]
            elif e[0] == 'warp':
                e[3] = remap[e[3]]
                e[4] = remap[e[4]]
            elif e[0] == 'climb':
                e[3] = remap[e[3]]
                e[4] = remap[e[4]]
            elif e[0] == 'center':
                e[2] = remap[e[2]]
                e[3] = remap[e[3]]
            out.append(e)
        programs[direction] = out
    word['frames'] = new_frames
    return word, programs, remap


def repad_helpers(word, target=213):
    """Restore the shipped contract's count of cold full-ended helpers.

    `native_extensions.embedded_cache_roles` requires exactly 213 helpers with
    start 0 and final 1, where frame 1 is the full ambient.  Quotienting collapses
    every full-ambient frame onto F2^8, so the count falls.  Extending a helper's
    final frame by the ninth axis restores it, and costs that helper one rank in
    the paid profile and one in the helper profile, leaving the deficit unchanged.
    """
    axis = 256
    frames = word['frames']
    span_index = {span_of(b): i for i, b in enumerate(frames)}

    def frame_of(basis):
        key = span_of(basis)
        if key not in span_index:
            span_index[key] = len(frames)
            frames.append(basis)
        return span_index[key]

    full = [i for i, b in enumerate(frames) if len(b) == 9]
    full_frame = frame_of(frames[full[0]] if full
                          else [256, 128, 64, 32, 16, 8, 4, 2, 1])
    count = 0
    repadded = 0
    for role in range(224, 632):
        if word['start'][role] != 0:
            continue
        if len(frames[word['final'][role]]) == 9:
            count += 1
            continue
        if count+repadded >= target:
            break
        word['final'][role] = full_frame
        repadded += 1
    need(count+repadded == target, 'could not reach %d full-ended helpers' % target)
    return repadded, full_frame


def renumber_full_ambient(word, programs, full_frame):
    """Frame 1 must be the full ambient: the shipped contract tests `final == 1`."""
    frames = word['frames']
    order = list(range(len(frames)))
    order[1], order[full_frame] = order[full_frame], order[1]
    remap = {old: new for new, old in enumerate(order)}
    word['frames'] = [frames[i] for i in order]
    word['start'] = [remap[x] for x in word['start']]
    word['final'] = [remap[x] for x in word['final']]
    out = {}
    for direction, program in programs.items():
        rewritten = []
        for event in program:
            e = list(event)
            if e[0] == 'scalar':
                e[2] = remap[e[2]]
            elif e[0] in ('warp', 'climb'):
                e[3] = remap[e[3]]
                e[4] = remap[e[4]]
            elif e[0] == 'center':
                e[2] = remap[e[2]]
                e[3] = remap[e[3]]
            rewritten.append(e)
        out[direction] = rewritten
    return out


def write_gzip(path, payload):
    """Deterministic gzip: fixed mtime so repeated builds are byte-identical."""
    with open(path, 'wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as handle:
            handle.write(json.dumps(payload, sort_keys=True).encode())


def main():
    patch = F.read(JOINT/'PATCH.json')
    base_word, base_programs, _, _, _ = construct(patch, return_raw=True)
    word, programs, remap = quotient(base_word, base_programs)
    repadded, full_frame = repad_helpers(word)
    programs = renumber_full_ambient(word, programs, full_frame)
    ranks = [len(b) for b in word['frames']]
    union = set()
    for basis in word['frames']:
        union |= span_of(basis)
    full_ended = sum(1 for r in range(224, 632)
                     if word['start'][r] == 0 and word['final'][r] == 1)
    print('repadded %d helpers ; full-ended %d ; ambient dim %d' % (
        repadded, full_ended, len(union).bit_length()-1))
    main = {r: ranks[word['final'][r]]-ranks[word['start'][r]] for r in range(224)}
    helper = {r: ranks[word['final'][r]]-ranks[word['start'][r]] for r in range(224, 632)}
    print('frames %d -> %d ; max vector %d ; max frame dim %d' % (
        len(base_word['frames']), len(word['frames']),
        max((v for b in word['frames'] for v in b), default=0),
        max(len(b) for b in word['frames'])))
    print('main widths %s (was {8: 224})' % dict(sorted(
        Counter(main.values()).items())))
    print('main rank mass %d (was 1792)' % sum(main.values()))
    print('helper rank mass %d (was 3471)' % sum(helper.values()))

    artifact = {'frames': word['frames'],
                'ambient_dim': len(union).bit_length()-1,
                'repadded_helpers': repadded,
                'full_ended_helpers': full_ended,
                'start': list(word['start']),
                'final': list(word['final']),
                'kernel_vector': KERNEL,
                'map': 'phi(v): xor KERNEL when the pivot bit is set, then drop it',
                'patch_source_head': patch['source_head'],
                'main_rank_mass': sum(main.values()),
                'helper_rank_mass': sum(helper.values())}
    write_gzip(HERE/'QUOTIENT-WORD.json.gz', artifact)
    write_gzip(HERE/'QUOTIENT-PROGRAMS.json.gz', programs)
    print('wrote QUOTIENT-WORD.json.gz and QUOTIENT-PROGRAMS.json.gz')


if __name__ == '__main__':
    main()
