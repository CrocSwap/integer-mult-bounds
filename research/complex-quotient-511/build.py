#!/usr/bin/env python3
"""Build the rank-8 quotient of the complex supplier. Apache-2.0.

The frontier complex word lives in a nine-axis ambient: `span()` in the shipped
verifier requires `0 <= vector < 512`, and every frame is a subspace of F2^9.
The map

    phi(v) = (v & 0xFF) ^ (0xFF if v & 0x100 else 0)

is linear, surjective onto F2^8, and has kernel span{511}.  `511` lies outside
every one of the 112 dim-8 main finals and outside every main entrance, so the
only frames the quotient moves are the full-ambient ones:

  * the 112 ground-entrance mains end at dim-8 finals and stay 0 -> 8;
  * the 112 rank-1-entrance mains end at the full ambient and become 1 -> 8
    (was 1 -> 9);
  * the ground frame stays ground.

Main rank mass therefore falls from 1,792 to 1,680 and the local deficit from
1,856 to 1,744.  The quotient leaves the ninth ambient direction unused, so
`pad_ambient` then spends it on one helper: that keeps the word's ambient at nine
axes, which is what makes the block-8 ladder charge correct rather than
assumed.

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

KERNEL = 511


def phi(v):
    return (v & 0xFF) ^ (0xFF if v & 0x100 else 0)


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


def pad_ambient(word):
    """Spend the ninth axis on one helper so the word occupies F2^9 fully.

    The quotient leaves one ambient direction unused (the union of the frame
    spans is dim 8).  The tensor block is `ambient - 1`, so a word that only
    spans 8 dimensions invites the reading that its block is 7.  Extending one
    helper's final frame by the ninth axis costs that helper one rank and one
    paid rank, leaving the deficit unchanged, and makes the word occupy all nine
    dimensions unambiguously.
    """
    axis = 256
    frames = word['frames']
    for role in range(224, 632):
        final = word['final'][role]
        if axis in span_of(frames[final]):
            continue
        new = dedupe(frames[final]+[axis])
        if len(new) != len(frames[final])+1:
            continue
        frames.append(new)
        word['final'][role] = len(frames)-1
        return role
    raise ValueError('no helper could absorb the ninth axis')


def write_gzip(path, payload):
    """Deterministic gzip: fixed mtime so repeated builds are byte-identical."""
    with open(path, 'wb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as handle:
            handle.write(json.dumps(payload, sort_keys=True).encode())


def main():
    patch = F.read(JOINT/'PATCH.json')
    base_word, base_programs, _, _, _ = construct(patch, return_raw=True)
    word, programs, remap = quotient(base_word, base_programs)
    padded = pad_ambient(word)
    ranks = [len(b) for b in word['frames']]
    union = set()
    for basis in word['frames']:
        union |= span_of(basis)
    print('padded helper %d ; ambient dim %d' % (padded, len(union).bit_length()-1))
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
                'padded_helper': padded,
                'start': list(word['start']),
                'final': list(word['final']),
                'kernel_vector': KERNEL,
                'map': 'phi(v) = (v & 0xFF) ^ (0xFF if v & 0x100 else 0)',
                'patch_source_head': patch['source_head'],
                'main_rank_mass': sum(main.values()),
                'helper_rank_mass': sum(helper.values())}
    write_gzip(HERE/'QUOTIENT-WORD.json.gz', artifact)
    write_gzip(HERE/'QUOTIENT-PROGRAMS.json.gz', programs)
    print('wrote QUOTIENT-WORD.json.gz and QUOTIENT-PROGRAMS.json.gz')


if __name__ == '__main__':
    main()
