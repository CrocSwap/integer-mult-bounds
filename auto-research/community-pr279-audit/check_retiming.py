#!/usr/bin/env python3
"""Independent exact check of PR279's selected common-delivery frames.

Imports no contributor code. This checks the local frame identity, not the
whole circuit or all-size transfer. Douglas Colkitt, with OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path


def rank(rows):
    pivots = {}
    for row in rows:
        x = list(map(Q, row))
        for j, y in sorted(pivots.items()):
            c = x[j]
            if c:
                x = [a - c*b for a, b in zip(x, y)]
        j = next((j for j, a in enumerate(x) if a), None)
        if j is not None:
            c = x[j]
            pivots[j] = [a/c for a in x]
    return len(pivots)


def check_entry(row, pair, frames):
    a, b, coefficient, category = row['scalar']
    assert {a, b} == {pair['carrier'], pair['passive']}
    assert coefficient == 1 and row['old_dimension'] == 2
    assert row['new_dimension'] == 22
    B = row['new_basis']
    A = frames[str(pair['deliver_frame'])]['a']
    assert len(A) == 2 and len(B) == 22
    assert all(len(r) == 24 and all(type(x) is int for x in r) for r in A+B)
    assert rank(A) == 2 and rank(B) == 22
    assert all(sum(x*y for x, y in zip(a, b)) == 0 for a in A for b in B)
    # For G=I-J/9, nondegeneracy on ker(A) is equivalent to that of
    # A G^-1 A^T. Multiply this 2x2 matrix by 9-h=-15.
    gram = [[-15*sum(x*y for x, y in zip(a, b)) + sum(a)*sum(b)
             for b in A] for a in A]
    assert gram[0][0]*gram[1][1]-gram[0][1]*gram[1][0] != 0
    assert pair['carrier_ranks'] == [1, 20, 2]
    assert pair['passive_ranks'] == [1, 22]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('package', type=Path)
    args = ap.parse_args()
    root = args.package
    selection_path = root/'descent-selection.json'
    selection = json.loads(selection_path.read_text())
    frames = json.loads(gzip.decompress((root/'gen4bit/selected/bit/frames_p12.json.gz').read_bytes()))['frames']
    entries = json.loads((root/'gen4bit/selected/bit/kchron_p12.json').read_text())['entries']
    pairs = {tuple(sorted((e['carrier'], e['passive']))): e for e in entries}
    seen = set()
    for row in selection['entries']:
        key = tuple(sorted(row['scalar'][:2]))
        assert key not in seen
        seen.add(key)
        check_entry(row, pairs[key], frames)
    assert seen == set(pairs) and len(seen) == 880
    delta = Counter({21:1760, 2:880, 1:-1760, 20:-880, 22:-880})
    assert sum(delta.values()) == -880 and sum(r*n for r,n in delta.items()) == 0
    assert dict(delta) == {int(k):v for k,v in selection['expected_local_histogram_delta'].items()}
    bad = dict(selection['entries'][0])
    bad['new_basis'] = [r[:] for r in bad['new_basis']]
    bad['new_basis'][0] = [0]*24
    try:
        check_entry(bad, pairs[tuple(sorted(bad['scalar'][:2]))], frames)
    except AssertionError:
        pass
    else:
        raise AssertionError('rank-deficient selected frame accepted')
    print(json.dumps(dict(status='PASS_INDEPENDENT_COMMON_DELIVERY_FRAME_CHECK',
        pairs=len(seen), rank_mass_change=0, local_call_change=-880,
        singular_frame_control_rejected=True,
        selection_sha256=hashlib.sha256(selection_path.read_bytes()).hexdigest(),
        scope='Exact equality to existing delivery subspaces and nondegeneracy; no contributor imports. Full chronological/endpoint checks supplied by the separately replayed package.'), indent=2))


if __name__ == '__main__':
    main()
