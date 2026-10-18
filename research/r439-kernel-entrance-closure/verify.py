#!/usr/bin/env python3
"""All-support R439 common-frame kernel closure; Apache-2.0.

Prepared for mightyOil with substantial OpenAI Codex assistance.
This finite classifier does not admit a physical supplier or change kappa.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def rref(rows, width=8):
    """Canonical rational rowspace; no physical coordinates reduced mod 2."""
    a = [list(map(Q, row)) for row in rows]
    require(all(len(row) == width for row in a), 'row width')
    k = 0
    for col in range(width):
        p = next((i for i in range(k, len(a)) if a[i][col]), None)
        if p is None:
            continue
        a[k], a[p] = a[p], a[k]
        divisor = a[k][col]
        a[k] = [x / divisor for x in a[k]]
        for i in range(len(a)):
            if i != k and a[i][col]:
                multiplier = a[i][col]
                a[i] = [x - multiplier*y for x, y in zip(a[i], a[k])]
        k += 1
    return tuple(tuple(row) for row in a[:k])


def orthogonal(rows, width=8):
    reduced = rref(rows, width)
    pivots = [next(i for i, x in enumerate(row) if x) for row in reduced]
    out = []
    for free in range(width):
        if free not in pivots:
            row = [Q(int(i == free)) for i in range(width)]
            for p, equation in zip(pivots, reduced):
                row[p] = -equation[free]
            out.append(row)
    return rref(out, width)


def subspace(a, b):
    return len(rref(a + b)) == len(b)


def geometry_closure(frames):
    """Complete nonzero intersection closure when every generator has dim <= 2."""
    require(all(1 <= len(f) <= 2 for f in frames), 'first-contact dimension outside theorem')
    planes = sorted(f for f in frames if len(f) == 2)
    result = set(frames)
    normals = {f: orthogonal(f) for f in planes}
    intersecting = 0
    for a, b in combinations(planes, 2):
        joined_rank = len(rref(a + b))
        require(joined_rank in (3, 4), 'distinct plane rank')
        if joined_rank == 3:
            result.add(orthogonal(normals[a] + normals[b]))
            intersecting += 1
    return sorted(result), intersecting


def extract(word):
    require((word['v'], word['R']) == (111, 439), 'fixed R439 dimensions')
    offset = 2*word['v']
    columns = [0]*word['R']
    for f, target, sources in word['D']:
        require(f == 0 and word['v'] <= target < offset, 'original D shape')
        for source in sources:
            require(offset <= source < offset+word['R'], 'D source is helper')
            columns[source-offset] ^= 1 << (target-word['v'])
    first = {}
    for f, target, sources in word['A'] + word['B']:
        for role in [target] + sources:
            if role >= offset:
                require(role < offset+word['R'], 'raw helper range')
                first.setdefault(role, f)
    require(set(first) == set(range(offset, offset+word['R'])), 'all helpers contacted')
    spaces = {f: rref([word['lines'][i] for i in word['frames'][f]]) for f in set(first.values())}
    # The claimed response is rederived from the raw chronological A/scatter/B/C
    # program, independently of the compensation list D used to form columns.
    rows = [1 << i for i in range(offset+word['R'])]
    a_helpers = {r for _, t, ss in word['A'] for r in [t]+ss if r >= offset}
    require(set(word['ret']) <= a_helpers, 'retained copies have preceding A contact')
    for phase in ('A', 'scatter', 'B', 'C'):
        if phase == 'scatter':
            copied = [rows[h] for h in word['ret']]
            for i, terms in enumerate(word['scatter']):
                for term in terms:
                    rows[word['v']+i] ^= copied[term]
        else:
            for _, target, sources in word[phase]:
                for source in sources:
                    rows[target] ^= rows[source]
    for role, actual in enumerate(rows):
        expected = 1 << role
        if word['v'] <= role < offset:
            target = role-word['v']
            expected ^= 1 << target
            for j, col in enumerate(columns):
                if col >> target & 1:
                    expected ^= 1 << (j+offset)
        require(actual == expected, 'raw response/compensation equality on every dirty column')
    return columns, first, spaces


def kernel(columns, helpers, offset=222):
    """Column elimination retaining dependency masks, hence a full F2 nullbasis."""
    basis = {}
    dependencies = []
    for helper in sorted(helpers):
        response, mask = columns[helper-offset], 1 << helper
        while response:
            pivot = response.bit_length()-1
            if pivot not in basis:
                basis[pivot] = (response, mask)
                break
            old_response, old_mask = basis[pivot]
            response ^= old_response
            mask ^= old_mask
        if not response:
            dependencies.append([h for h in sorted(helpers) if (mask >> h) & 1])
    return len(basis), dependencies


def classify(word):
    columns, first, frames = extract(word)
    closure, pairs = geometry_closure(set(frames.values()))
    rows = []
    for frame in closure:
        allowed = [h for h in sorted(first) if subspace(frame, frames[first[h]])]
        rank, nullbasis = kernel(columns, allowed)
        rows.append(dict(frame=[[str(x) for x in row] for row in frame],
                         eligible_helpers=allowed, response_rank=rank,
                         nullity=len(allowed)-rank, kernel_basis=nullbasis))
        require(len(nullbasis) == len(allowed)-rank, 'nullity identity')
    return dict(helper_count=len(first), response_rows=word['v'],
                first_frame_ids=len(frames), first_rowspaces=len(set(frames.values())),
                first_dimensions=dict(sorted(Counter(len(frames[first[h]]) for h in first).items())),
                initial_subspace_dimensions=dict(sorted(Counter(map(len, set(frames.values()))).items())),
                distinct_plane_pairs=sum(1 for _ in combinations([f for f in set(frames.values()) if len(f)==2], 2)),
                intersecting_distinct_plane_pairs=pairs,
                closure_dimensions=dict(sorted(Counter(map(len, closure)).items())),
                nullity_histogram=dict(sorted(Counter(row['nullity'] for row in rows).items())),
                classes=rows)


def controls():
    tested = []
    # No support cutoff: unique dependency requires six helpers, beyond PR1179's four.
    e = tuple(Q(int(i == 0)) for i in range(8))
    columns = [1, 2, 4, 8, 16, 31]
    rank, deps = kernel(columns, list(range(6)), offset=0)
    require((rank, deps) == (5, [[0, 1, 2, 3, 4, 5]]), 'six-support fixture')
    tested.append('six-helper minimal kernel beyond sparse cutoff')
    rank, deps = kernel([1, 2, 4, 8, 16, 63], list(range(6)), offset=0)
    require((rank, deps) == (6, []), 'response mutation escapes kernel')
    tested.append('one-response-bit mutation removes six-helper kernel')
    basis = [tuple(Q(int(i == j)) for i in range(8)) for j in range(4)]
    plane_a = rref([basis[0], basis[1]])
    plane_b = rref([basis[0], basis[2]])
    plane_c = rref([basis[2], basis[3]])
    closure, count = geometry_closure({plane_a, plane_b, plane_c})
    require(rref([basis[0]]) in closure and rref([basis[2]]) in closure and count == 2, 'generated lines')
    tested.append('two absent input lines recovered as plane intersections')
    require(not subspace(rref([basis[1]]), plane_b), 'incompatible entrance rejected')
    tested.append('kernel alone does not imply a common entrance')
    try:
        geometry_closure({rref(basis[:3])})
    except ValueError:
        tested.append('dimension-three source fails closed')
    else:
        raise ValueError('dimension-three source incorrectly admitted')
    require(rref([tuple(2*x for x in e)]) == rref([e]), 'rational geometry retained')
    tested.append('even-coordinate physical line is nonzero over Q')
    return tested


def sources():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin: '+row['path'])
    return manifest


def run():
    manifest = sources()
    word = json.loads(gzip.decompress((ROOT/WORD).read_bytes()))
    census = classify(word)
    live = [row for row in census['classes'] if row['nullity']]
    require(len(live) == 1 and live[0]['kernel_basis'] == [[444, 470]], 'unique all-support kernel')
    require(live[0]['frame'] == [['0','1','0','-1','1','0','1','0']], 'unique entrance line')
    require(live[0]['eligible_helpers'] == [390,391,444,470,578,580,582], 'eligible set')
    return dict(schema_version=1, base_commit=manifest['base_commit'], seed=5,
                classification=census, raw_endpoint_columns=661, controls=controls(), new_kappa=False,
                scope='binary response-null directions with arbitrary support and a nonzero rational common first-contact frame; fixed PR589 raw word')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a new receipt; refuses overwrite')
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open('x') as handle:
            json.dump(result, handle, sort_keys=True, indent=2)
            handle.write('\n')
    else:
        expected = json.loads((HERE/'CERTIFICATE.json').read_text())
        require(canonical(result) == canonical(expected), 'certificate mismatch')
    print('PASS_R439_KERNEL_ENTRANCE_CLOSURE classes=366 zero_nullity=365 unique_kernel=444+470 controls=6 no_new_kappa')


if __name__ == '__main__':
    main()
