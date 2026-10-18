#!/usr/bin/env python3
"""Exact h9 common-frame weight-five census; Apache-2.0, Codex for ToikY.

This producer uses explicit XOR-closed subspaces and complete source subsets.
It imports no predecessor implementation and certifies geometry only.
"""
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
H = 9
BASE = '1b59b624d21924f8e3537cdc1ac52d3be6eda2fe'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique_keys(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'duplicate certificate key')
        out[key] = value
    return out


def pc(x):
    return bin(x).count('1')


def dot(x, y):
    return pc(x & y) % 2


def kernel(s, t):
    return (1, 0, -1, 0)[pc(s & t) % 4]


def span(basis):
    out = {0}
    for x in basis:
        out |= {v ^ x for v in out}
    return out


def character(space, basis):
    candidates = [x for x in sorted(space)
                  if all(dot(x, b) == dot(b, b) for b in basis)]
    need(len(candidates) == 1, 'unique characteristic in nondegenerate frame')
    return candidates[0]


def basis_of(space):
    basis, have = [], {0}
    for x in sorted(space):
        if x not in have:
            basis.append(x)
            have |= {v ^ x for v in have}
    need(have == space, 'basis spans complete space')
    return basis


def orthonormal_basis(space):
    """Exhaust all choices; choosing the first norm-one vector can fail."""
    if space == {0}:
        return []
    for x in sorted(space):
        if dot(x, x):
            residual = {v for v in space if not dot(v, x)}
            result = orthonormal_basis(residual)
            if result is not None:
                answer = [x] + result
                need(span(answer) == space, 'orthonormal basis span')
                need(all(dot(a, b) == int(i == j)
                         for i, a in enumerate(answer)
                         for j, b in enumerate(answer)), 'identity Gram')
                return answer
    return None


def quotient_planes(a, b):
    """All 2667 planes in V/E, represented by their three nonzero cosets."""
    E = span([a, b])
    need(len(E) == 4, 'source pair independence')
    cosets = sorted({min(x ^ e for e in E) for x in range(1 << H)})
    need(len(cosets) == 128 and cosets[0] == 0, 'quotient dimension seven')
    planes = set()
    for u, v in combinations(cosets[1:], 2):
        w = min((u ^ v) ^ e for e in E)
        need(w and len({u, v, w}) == 3, 'quotient plane independence')
        planes.add(tuple(sorted((u, v, w))))
    need(len(planes) == 2667, 'complete binary Gaussian coefficient [7,2]')
    for u, v, w in sorted(planes):
        basis = [a, b, u, v]
        U = span(basis)
        need(len(U) == 16 and w in U, 'lifted frame dimension four')
        yield basis, U


def has_degenerate_pair(labels):
    return any(dot(a, b) for a, b in combinations(labels, 2))


def fixture(basis, sources, targets):
    U = span(basis)
    W = {v for v in range(1 << H) if all(not dot(v, x) for x in U)}
    need(len(U) == 16 and len(W) == 32 and U & W == {0}, 'fixture U4 W5')
    wU = character(U, basis)
    wW = character(W, basis_of(W))
    need(wU ^ wW == 511, 'orthogonal characteristic splitting')
    need(set(sources) <= U and set(targets) <= W, 'fixture endpoints')
    need(all(pc(x) == 5 for x in sources + targets), 'fixture label weights')
    need(wU not in sources and wW not in targets, 'fixture residual criterion')
    need(has_degenerate_pair(sources) and has_degenerate_pair(targets),
         'fixture degeneracy on both sides')
    source_signs = [kernel(s, targets[0]) for s in sources]
    target_signs = [kernel(sources[0], t) * source_signs[0] for t in targets]
    need(all(kernel(s, t) == source_signs[i] * target_signs[j]
             for i, s in enumerate(sources) for j, t in enumerate(targets)),
         'fixture signed outer product')
    incoming, outgoing = [], []
    for labels, ambient, dimension, result in (
            (sources, U, 3, incoming), (targets, W, 4, outgoing)):
        for x in labels:
            residual = {v for v in ambient if not dot(v, x)}
            rows = orthonormal_basis(residual)
            need(rows is not None and len(rows) == dimension,
                 'complete incident orthonormal residual')
            result.append({'label': x, 'basis': rows})
    s, t = len(sources), len(targets)
    return {'frame_basis': basis_of(U), 'frame_vectors': sorted(U),
            'complement_basis': basis_of(W), 'frame_characteristic': wU,
            'complement_characteristic': wW, 'sources': sources,
            'targets': targets, 'source_signs': source_signs,
            'target_signs': target_signs, 'size': [s, t], 'area': s * t,
            'dirty_wrapper_adds': 2 * (s + t),
            'adds_saved_vs_one_add_per_entry': s * t - 2 * (s + t),
            'wrapper_incident_rank_mass': 2 * s * 3 + 2 * t * 4,
            'incoming_residual_bases': incoming,
            'outgoing_residual_bases': outgoing}


def run():
    orbits = []
    common_records = []
    best_area, best_saving = -1, -1000
    area_key = saving_key = None
    area_witness = saving_witness = None
    for intersection, a, b in ((1, 31, 481), (3, 31, 103)):
        need(pc(a) == pc(b) == 5 and pc(a & b) == intersection,
             'canonical source pair')
        counts = Counter()
        size_histogram, maximal_sizes, frame_maximum = Counter(), Counter(), Counter()
        digest = hashlib.sha256()
        seen_frames = set()
        for basis, U in quotient_planes(a, b):
            frame_key = tuple(sorted(U))
            need(frame_key not in seen_frames, 'unique lifted U4')
            seen_frames.add(frame_key)
            counts['frames_examined'] += 1
            radical = {x for x in U if all(not dot(x, y) for y in basis)}
            if radical != {0}:
                counts['degenerate_frames'] += 1
                digest.update((json.dumps([list(frame_key), 'degenerate'],
                                          separators=(',', ':')) + '\n').encode())
                continue
            counts['nondegenerate_frames'] += 1
            W = {x for x in range(1 << H) if all(not dot(x, y) for y in basis)}
            need(len(W) == 32 and U & W == {0}, 'orthogonal U4 W5')
            wU = character(U, basis)
            wW = 511 ^ wU
            need(wW in W and all(dot(wW, x) == dot(x, x) for x in W),
                 'complement characteristic')
            sources = sorted(x for x in U if pc(x) == 5 and x != wU)
            targets = sorted(x for x in W if pc(x) == 5 and x != wW)
            need(a in sources and b in sources, 'anchored source residuals')
            other = [s for s in sources if s not in (a, b)]
            source_subsets = qualifying = maximal = local_area = 0
            best_sizes = set()
            local_saving = -1000
            for bits in range(1 << len(other)):
                S = sorted([a, b] + [x for i, x in enumerate(other) if bits >> i & 1])
                source_subsets += 1
                groups = {}
                for t in targets:
                    signs = tuple(kernel(s, t) * kernel(S[0], t) for s in S)
                    need(all(abs(z) == 1 for z in signs), 'nonzero common-frame kernel')
                    groups.setdefault(signs, []).append(t)
                for T in groups.values():
                    if len(T) < 2 or not has_degenerate_pair(T):
                        continue
                    qualifying += 1
                    s, t = len(S), len(T)
                    area, saving = s * t, s * t - 2 * (s + t)
                    size_histogram[s, t] += 1
                    if area > local_area:
                        local_area, best_sizes = area, {(s, t)}
                    elif area == local_area:
                        best_sizes.add((s, t))
                    local_saving = max(local_saving, saving)
                    closure = [x for x in sources if all(
                        kernel(x, y) * kernel(S[0], y)
                        == kernel(x, T[0]) * kernel(S[0], T[0]) for y in T)]
                    if closure == S:
                        maximal += 1
                        maximal_sizes[s, t] += 1
                    key = (tuple(S), tuple(T), frame_key)
                    if area > best_area or (area == best_area and key < area_key):
                        best_area, area_key = area, key
                        area_witness = (basis, S, T)
                    if saving > best_saving or (saving == best_saving and key < saving_key):
                        best_saving, saving_key = saving, key
                        saving_witness = (basis, S, T)
            counts['source_subsets_examined'] += source_subsets
            counts['qualifying_target_classes'] += qualifying
            counts['inclusion_maximal_bicliques'] += maximal
            counts['frames_with_qualifying_biclique'] += int(qualifying > 0)
            frame_maximum[local_area] += 1
            common_records.append([intersection, list(frame_key), len(sources),
                                   len(targets), local_area,
                                   [list(z) for z in sorted(best_sizes)]])
            record = [list(frame_key), sources, targets, wU, wW, source_subsets,
                      qualifying, maximal, local_area,
                      local_saving if qualifying else None]
            digest.update((json.dumps(record, separators=(',', ':')) + '\n').encode())
        need(len(seen_frames) == 2667, 'all U4 containing canonical source E')
        orbits.append({'source_intersection': intersection, 'source_pair': [a, b],
                       'counts': dict(sorted(counts.items())),
                       'qualifying_sizes': [[s, t, n] for (s, t), n in sorted(size_histogram.items())],
                       'inclusion_maximal_sizes': [[s, t, n] for (s, t), n in sorted(maximal_sizes.items())],
                       'frame_maximum_area_histogram': [[a, n] for a, n in sorted(frame_maximum.items())],
                       'ordered_frame_stream_sha256': digest.hexdigest()})
    need(area_witness is not None and saving_witness is not None, 'nonempty finite result')
    return {'schema': 1, 'base_commit': BASE, 'seed': 48, 'ambient_dimension': H,
            'frame_dimension': 4, 'complement_dimension': 5,
            'domain': 'Both sides contain a degenerate pair; constant weight five; one U4/W5; historical orthonormal incident residuals; signed rank one.',
            'coverage': 'Every source pair is coordinate-isomorphic to one of the two anchored pairs. Every U4 containing E is a two-plane in V/E. Every S containing that pair is exhausted; maximal T are normalized signed column classes.',
            'stopping_rule': 'Complete finite exhaustion; no sampled frames or endpoints.',
            'orbits': orbits, 'maximum_area': best_area,
            'common_record_count': len(common_records),
            'common_records_sha256': hashlib.sha256(json.dumps(
                sorted(common_records), separators=(',', ':')).encode()).hexdigest(),
            'maximum_dirty_wrapper_saving': best_saving,
            'maximum_area_witness': fixture(*area_witness),
            'maximum_saving_witness': fixture(*saving_witness),
            'scope': 'Exact finite geometry and scalar wrapper accounting only; no supplier, paid recurrence or kappa claim.'}


def main():
    need(sys.argv[1:] in ([], ['--write']), 'usage: census.py [--write]')
    result = run()
    path = HERE / 'CENSUS.json'
    if sys.argv[1:] == ['--write']:
        path.write_text(json.dumps(result, indent=2) + '\n')
    else:
        saved = json.loads(path.read_text(), object_pairs_hook=unique_keys)
        need(json.dumps(result, sort_keys=True, separators=(',', ':'))
             == json.dumps(saved, sort_keys=True, separators=(',', ':')),
             'committed census mismatch')
    print('PASS_COMMON_FRAME_WEIGHT5_CENSUS frames=5334 maximum_area=%d maximum_dirty_wrapper_saving=%d no_new_kappa'
          % (result['maximum_area'], result['maximum_dirty_wrapper_saving']))


if __name__ == '__main__':
    main()
