#!/usr/bin/env python3
"""Reproduce overlap against the two historical, byte-pinned public snapshots."""
import argparse
import collections
import gzip
import hashlib
import json
from pathlib import Path
import sympy as S

if not __debug__:
    raise SystemExit('assertions required')


def get(item, key, alternate):
    return item[key] if key in item else item[alternate]


def roles(item):
    return tuple(sorted(item['roles']))


def basis(item):
    return tuple(tuple(str(x) for x in row) for row in S.Matrix(item['basis']).rref()[0].tolist())


def exact(item):
    return (get(item, 'a', 'pivot'), tuple(sorted(item['partners'])), item['cut'], basis(item))


def space(item):
    return (roles(item), item['cut'], basis(item))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package', type=Path, required=True,
                    help='crosscut-response-pairs directory beside retained parent packages')
    ap.add_argument('--snapshots', type=Path, default=Path(__file__).resolve().parent)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists(), 'use a fresh output path'
    base = json.loads(gzip.decompress((a.package.parent/'multicut-kernel-condensation/inputs/candidates.json.gz').read_bytes()))
    ours = json.loads((a.package/'inputs/additional-entrances.json').read_text())
    baseline_pivots = {item['a'] for item in base}
    assert len(base) == 518 and len(ours) == 369
    pins = json.loads((a.snapshots/'SOURCES.json').read_text())
    result = {}
    for num in (266, 267):
        pin = pins[str(num)]
        raw = (a.snapshots/pin['witness_file']).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == pin['sha256']
        theirs = json.loads(raw)
        assert len(theirs) == pin['total_entrances']
        added = [item for item in theirs if get(item, 'a', 'pivot') not in baseline_pivots]
        ours_exact = {exact(item): item for item in ours}
        theirs_exact = {exact(item): item for item in added}
        oe, te = set(ours_exact), set(theirs_exact)
        os, ts = {space(item) for item in ours}, {space(item) for item in added}
        our_roles, their_roles = {roles(item) for item in ours}, {roles(item) for item in added}
        row = dict(total_theirs=len(theirs), new_pivots_not_in_baseline=len(added),
                   ours_new_pivots=len(ours), exact_pivot_donor_cut_subspace_overlap=len(oe&te),
                   unordered_roles_cut_subspace_overlap=len(os&ts),
                   unordered_roles_overlap_ignoring_cut_frame=len(our_roles&their_roles),
                   our_unique_exact=len(oe-te), their_unique_exact=len(te-oe),
                   their_added_dimensions=dict(collections.Counter(get(item, 'dim', 'E_dimension') for item in added)))
        if num == 266:
            row['ours_not_matching266'] = [dict(pivot=item['a'], donors=item['partners'],
                dim=item['dim'], kind=item['kind']) for key, item in ours_exact.items() if key not in te]
        result[str(num)] = row
    result = json.loads(json.dumps(result))
    assert result == json.loads((a.snapshots/'WITNESS-OVERLAP.json').read_text()), 'historical comparison changed'
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS_HISTORICAL_WITNESS_COMPARISON',
          {num: row['exact_pivot_donor_cut_subspace_overlap'] for num, row in result.items()})


if __name__ == '__main__':
    main()
