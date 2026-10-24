#!/usr/bin/env python3
"""Costed lower-frame observations in the changed, center-free word.

Extends the packet's rank-eight/rank-one observer screen to every rank.
Uses the necessary K_G |0>=|0> specialization. Any positive is a candidate,
not a physical recovery proof. Apache-2.0; OpenAI Codex assistance.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import argparse
import gzip
import json
import sys
import time

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--packet', type=Path, required=True)
    args = ap.parse_args()
    root, start = args.packet, time.monotonic()
    sys.path[:0] = [str(root/'research/operator_alignment_next'),
                   str(root/'research/retained_state_next')]
    import augmented_rank1_observers as obs
    fc = obs.fc
    path = root/'research/retained_state_next/F9-SOURCE-DAG-ALL8-WORD.json.gz'
    raw = path.read_bytes()
    w = json.loads(gzip.decompress(raw))
    c = w['canonical']
    rpath = root/'upstream/research/involutory-producer-raw-dual/inputs/R/R.json'
    R = [[Q(v) for v in row] for row in json.loads(rpath.read_text())]
    events = [e for e in w['programs']['backward'] if e[0] != 'physical_add']
    owned = 1+w['owned_extra_slots_by_direction']['backward']
    rows = [{i: Q(1)} for i in range(632)]+[{} for _ in range(owned)]
    cur = c['start'][:]+[None]*owned
    full, seen, contacts = [], defaultdict(set), defaultdict(list)
    counts = Counter()

    def save(d, pos):
        f = cur[d]
        if f is None or not rows[d]:
            return
        counts[len(c['frames'][f])] += 1
        key = tuple(sorted(rows[d].items()))
        if key in seen[f]:
            return
        seen[f].add(key)
        item = {'owner': d, 'after_event': pos, 'frame': f}, dict(rows[d])
        if f == 1:
            full.append(item)
        else:
            contacts[f].append(item)

    for d in range(632):
        save(d, -1)
    for pos, e in enumerate(events):
        typ, d = e[0], None
        if typ == 'scalar':
            a, f = e[1:]
            d = a[1][1]+632*(a[1][0] == 'C')
            if a[0] == 'clear':
                rows[d], cur[d] = {}, f
            elif a[0] in ('add', 'copy'):
                s = a[2][1]+632*(a[2][0] == 'C')
                assert cur[s] == cur[d] == f
                rows[d] = dict(rows[s]) if a[0] == 'copy' else fc.add(rows[d], fc.scale(rows[s], Q(a[3], a[4])))
            else:
                assert a[0] == 'scale'
                rows[d] = fc.scale(rows[d], Q(a[2], a[3]))
        elif typ == 'warp':
            d = e[1][1]+632*(e[1][0] == 'C')
            assert cur[d] == e[3]
            cur[d] = e[4]
        elif typ == 'climb':
            d = e[2]
            assert cur[d] == e[3]
            cur[d] = e[4]
        else:
            assert typ in ('phase', 'adapter')
        if d is not None:
            save(d, pos)
    assert cur[:632] == c['final'] and all(not row for row in rows[632:])
    # Bind the changed endpoint in this necessary specialization.
    for i in range(632):
        expected = {i: Q(1)}
        if i < 112:
            expected[i+112] = Q(-1)
            for r in R:
                if r[i]:
                    for j, a in enumerate(r):
                        if a:
                            expected[j+112] = expected.get(j+112, Q(0))+r[i]*a/4
        assert rows[i] == {k: a for k, a in expected.items() if a}
    print('REPLAY',len(events),'full unique',len(full),'frames',len(contacts),flush=True)
    sbasis = fc.sparse_basis(full)
    pivots = [(i, b[0]) for i, b in sorted(sbasis.items())]
    targets = [obs.reduce_with_pivots({112+i: a for i, a in enumerate(r) if a}, pivots) for r in R]
    assert len(fc.sparse_basis(list(enumerate(targets)))) == 8
    print('FULL_BASIS',len(sbasis),'seconds',time.monotonic()-start,flush=True)
    candidates, per_rank, quotient_spaces = [], defaultdict(list), {}
    # All original Y values are available at ground on entry. Their eight
    # R combinations are an explicit basis at lift rank nine; rebuilding a
    # large ground-frame elimination cannot improve that equal-cost basis.
    for k, r in enumerate(R):
        desc = {'frame': 0, 'frame_rank': 0, 'full_lift_rank': 9,
                'target_modes': {str(k): '1'},
                'gather': [{'owner': 112+i, 'after_event': -1, 'frame': 0,
                            'coefficient': str(a)} for i, a in enumerate(r) if a]}
        candidates.append((desc, {k: Q(1)}))
        per_rank[0].append((desc, {k: Q(1)}))
    for f, original in sorted(contacts.items()):
        if f == 0:
            continue
        reduced = []
        keys = set()
        for desc, row in original:
            row = obs.reduce_with_pivots(row, pivots)
            key = tuple(sorted(row.items()))
            if row and key not in keys:
                keys.add(key)
                reduced.append((desc, row))
        quotient_spaces[f] = reduced
        _, solutions = obs.intersection(reduced, targets)
        rank = len(c['frames'][f])
        for target, recipe in solutions:
            desc = {'frame': f, 'frame_rank': rank, 'full_lift_rank': 9-rank,
                    'target_modes': {str(k): str(a) for k, a in target.items()},
                    'gather': [{**reduced[j][0], 'coefficient': str(a)} for j, a in recipe.items()]}
            candidates.append((desc, target))
            per_rank[rank].append((desc, target))
        if f % 100 == 0:
            print('FRAME',f,'candidates',len(candidates),'seconds',time.monotonic()-start,flush=True)
    by_rank = {str(r): {'contact_frames': sum(len(c['frames'][f]) == r for f in contacts),
                       'candidate_directions': len(data),
                       'combined_R_mode_rank': len(fc.sparse_basis(data)),
                       'one_lift_rank_per_direction': 9-r}
               for r in range(9) for data in [per_rank[r]]}
    # Equal-rank candidates have identical moment cost. Greedy basis selection
    # is optimal for this vector-matroid relaxation, including all ranks.
    chosen, basis = [], []
    for desc, target in sorted(candidates, key=lambda x: x[0]['full_lift_rank']):
        if len(fc.sparse_basis(basis+[(desc, target)])) > len(basis):
            basis.append((desc, target))
            chosen.append(desc)
    out = {'status': 'NECESSARY_COSTED_LOWER_FRAME_OBSERVER_SCREEN',
           'source_sha256': sha256(raw).hexdigest(), 'R_sha256': sha256(rpath.read_bytes()).hexdigest(),
           'all_632_original_amplitudes': True, 'all_408_helpers_retained': True,
           'changed_center_free_endpoint_checked': True, 'full_snapshot_augmentation_rank': len(sbasis),
           'observed_snapshots_by_frame_rank': dict(sorted(counts.items())),
           'all_ranks': by_rank, 'candidate_count': len(candidates),
           'minimum_basis_in_individually_clean_lift_family': chosen,
           'minimum_individually_clean_lift_rank_mass': sum(x['full_lift_rank'] for x in chosen),
           'recovered_mode_dimension': len(chosen),
           'scope': 'Necessary fixed-vector quotient of the actual changed word; individually clean same-frame mode gathers at every rank and free full-frame side information. Full lifts are separately paid at rank 9-dim(frame). The 72 mass is optimal only when each new observation individually gives a pure R-mode combination modulo side information. Jointly decoding several noisy observations is outside that bound. A positive still needs exact operator cleanup, phase lowering, chronology and every helper; no kappa is claimed.',
           'new_kappa_claimed': False, 'elapsed_seconds': time.monotonic()-start}
    (HERE/'evidence/observer-probe.json').write_text(json.dumps(out, indent=2)+'\n')
    subspaces = {'targets': [[[i,str(a)] for i,a in sorted(row.items())] for row in targets],
                 'frames': [{'frame': f, 'rank': len(c['frames'][f]),
                             'rows': [{'description': desc, 'row': [[i,str(a)] for i,a in sorted(row.items())]}
                                      for desc,row in data]}
                            for f,data in sorted(quotient_spaces.items()) if data]}
    (HERE/'evidence/observer-subspaces.json.gz').write_bytes(gzip.compress(json.dumps(subspaces,separators=(',',':')).encode(),mtime=0))
    print(json.dumps({k: out[k] for k in ('status', 'all_ranks', 'candidate_count',
          'minimum_individually_clean_lift_rank_mass', 'recovered_mode_dimension', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
