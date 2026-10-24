#!/usr/bin/env python3
"""Exact selective-port quotient budget; Apache-2.0, Codex assistance."""
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-CANONICAL.json.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(basis):
    values = {0}
    for v in basis:
        need(isinstance(v, int) and 0 <= v < 512, 'nine-bit vector')
        values |= {x ^ v for x in values}
    return values


def normal(basis):
    need(len(basis) == 8 and len(span(basis)) == 256, 'hyperplane basis')
    candidates = [n for n in range(1, 512)
                  if all((n & v).bit_count() % 2 == 0 for v in basis)]
    need(len(candidates) == 1, 'unique nonzero normal')
    return candidates[0]


def geometry(word):
    frames, start, final = word['frames'], word['start'], word['final']
    need(word['v'] == 112 and len(start) == len(final) == 632, 'source inventory')
    ports = [normal(frames[final[112 + i]]) for i in range(112)]
    centers = [normal(frames[f]) for f in word['center_frames']]
    need(len(centers) == 8, 'eight retained centers')
    for i in range(112):
        p, h = span(frames[start[i]]), span(frames[final[112 + i]])
        need(len(p) == 2 and p & h == {0}, 'source complementary port')
        need(len(span(frames[final[i]])) == 512, 'full first main exit')
        need(span(frames[start[112 + i]]) == {0}, 'ground second main entrance')
    combined = ports + centers
    expected = {n for n in range(1, 512) if n.bit_count() in (3, 7)}
    need(len(set(combined)) == 120 and set(combined) == expected,
         '112 ports plus eight centers are the weight-three/seven set')
    return ports, centers


def census(ports, centers):
    rows = []
    for k in range(1, 512):
        v = sum((k & n).bit_count() % 2 == 0 for n in ports)
        c = sum((k & n).bit_count() % 2 == 0 for n in centers)
        rows.append({'kernel': k, 'compatible_ports': v,
                     'retained_center_rank': 64 - c, 'local_rank_balance': v + c - 64})
    combined = Counter(r['compatible_ports'] + 64 - r['retained_center_rank'] for r in rows)
    need(combined == {0: 1, 56: 255, 64: 255}, 'all 511 hyperplane counts')
    need(max(r['local_rank_balance'] for r in rows) == 0, 'proper-line rank budget')
    return rows


def verify(word):
    ports, centers = geometry(word)
    rows = census(ports, centers)
    # A seven-space lies in three hyperplanes. Its points occur three times
    # and the other points once: 120+2|S intersect L| <= 3*64.
    seven_bound = (3 * 64 - 120) // 2
    need(seven_bound == 36 and seven_bound <= 8 * 7, 'codimension-two incidence bound')
    bounds = []
    for r in range(9):
        count = 0 if r == 0 else (64 if r == 8 else seven_bound if r == 7 else 2 ** (r - 1))
        need(count <= 8 * r, 'all proper dual subspace dimensions')
        bounds.append({'dual_dimension': r, 'kernel_dimension': 9 - r,
                       'port_and_center_normal_count_upper_bound': count,
                       'local_rank_balance_upper_bound': count - 8 * r})
    return {'claim': 'retained-center selective-port quotient rank budget only; no new kappa',
            'source_ports': 112, 'source_centers': 8, 'normal_weight_counts': {'3': 84, '7': 36},
            'unquotiented_local_rank_balance': 48,
            'line_kernel_cases': 511,
            'line_balance_counts': {str(k): v for k, v in sorted(Counter(r['local_rank_balance'] for r in rows).items())},
            'line_compatible_port_counts': {str(k): v for k, v in sorted(Counter(r['compatible_ports'] for r in rows).items())},
            'kernel_153': rows[152],
            'all_kernel_dimension_bounds': bounds,
            'line_census_sha256': hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}


def controls(word):
    mutations = []
    bad = deepcopy(word)
    bad['final'][112] = bad['start'][0]
    mutations.append(bad)
    bad = deepcopy(word)
    bad['center_frames'][0] = bad['center_frames'][1]
    mutations.append(bad)
    bad = deepcopy(word)
    bad['start'][0] = bad['final'][112]
    mutations.append(bad)
    bad = deepcopy(word)
    frame = bad['final'][112]
    bad['frames'][frame][-1] = bad['frames'][frame][0]
    mutations.append(bad)
    for bad in mutations:
        try:
            verify(bad)
        except ValueError:
            continue
        raise ValueError('geometry mutation falsely accepted')
    changed = deepcopy(word)
    for b in changed['frames']:
        if len(b) >= 2:
            b[0] ^= b[1]
    need(verify(changed) == verify(word), 'basis-change invariance')
    return {'geometry_mutations_rejected': len(mutations), 'basis_change_invariance': True}


def main():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    pin = next(x for x in pins['files'] if x['path'] == SOURCE)
    raw = (ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source bytes')
    word = json.loads(gzip.decompress(raw))
    result = verify(word)
    result['controls'] = controls(word)
    path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads(path.read_text()), 'committed result equality')
    print('PASS_SELECTIVE_QUOTIENT_PORT_BUDGET: 511 lines; all nonzero kernel dimensions; no new kappa')


if __name__ == '__main__':
    main()
