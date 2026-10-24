#!/usr/bin/env python3
"""Exact rational check of the two-frame noisy observer family.

Uses modular full-rank minors only as valid rational rank lower bounds;
every deficient pair is checked over Q. Apache-2.0; OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import gzip
import json
import time

from paired_observer_probe import insert as insert_mod, mod
from snapshot_probe import need

HERE = Path(__file__).resolve().parent


def add(a, b, c):
    for i, x in b.items():
        y = a.get(i, Q(0))+c*x
        if y:
            a[i] = y
        else:
            a.pop(i, None)


def insert(basis, row, tag):
    row, tag = dict(row), dict(tag)
    while row:
        p = min(row)
        if p not in basis:
            a = row[p]
            basis[p] = ({i: x/a for i, x in row.items()},
                        {i: x/a for i, x in tag.items()})
            return None
        b, t = basis[p]
        a = row[p]
        add(row, b, -a)
        add(tag, t, -a)
    return tag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--maximum-cost', type=int, default=4)
    args = ap.parse_args()
    need(2 <= args.maximum_cost <= 8, 'Supported pair budget')
    begin = time.monotonic()
    control = {}
    need(insert(control, {99: Q(1)}, {}) is None, 'First noisy control row')
    need(insert(control, {99: Q(1)}, {0: Q(1)}) == {0: Q(1)},
         'Joint noise cancellation positive control')
    path = HERE/'evidence/observer-subspaces.json.gz'
    data = json.loads(gzip.decompress(path.read_bytes()))
    target_basis = {}
    for k, record in enumerate(data['targets']):
        need(insert(target_basis, {int(i): Q(x) for i, x in record}, {k: Q(1)}) is None,
             'Independent target modes')
    frames = []
    for item in data['frames']:
        if 9-item['rank'] >= args.maximum_cost:
            continue
        basis = {}
        for record in item['rows']:
            row = {int(i): Q(x) for i, x in record['row']}
            tag = {}
            for p, (b, t) in sorted(target_basis.items()):
                a = row.get(p, 0)
                if a:
                    add(row, b, -a)
                    add(tag, t, a)
            need(not insert(basis, row, tag), 'No individually clean mode')
        modular = {}
        for row, tag in basis.values():
            need(not insert_mod(modular, {i: mod(x) for i, x in row.items()},
                                {i: mod(x) for i, x in tag.items()}),
                 'No spurious modular clean mode')
        # Distinct rational pivots remain independent modulo the chosen prime.
        need(len(modular) == len(basis), 'Per-frame rank preserved modulo prime')
        if basis:
            frames.append((item['frame'], item['rank'], basis, modular))
    counts, minor_proofs, rational_checks, hits = Counter(), 0, 0, []
    for a, b in combinations(frames, 2):
        price = 18-a[1]-b[1]
        if price > args.maximum_cost:
            continue
        counts[price] += 1
        m = dict(a[3])
        for row, tag in b[3].values():
            insert_mod(m, row, tag)
        if len(m) == len(a[2])+len(b[2]):
            # Full column rank of the nuisance projection over F_p implies
            # full column rank over Q, hence no intersection with target modes.
            minor_proofs += 1
            continue
        rational_checks += 1
        q = dict(a[2])
        for row, tag in b[2].values():
            relation = insert(q, row, tag)
            if relation:
                hits.append({'frames': [a[0], b[0]], 'cost': price,
                             'mode_combination': {str(i): str(x) for i, x in relation.items()}})
    need(not hits, 'Unexpected rational two-frame repair candidate')
    out = {'status': 'PASS_EXACT_TWO_FRAME_QUOTIENT_EXCLUSION',
           'input_sha256': sha256(path.read_bytes()).hexdigest(),
           'maximum_total_lift_rank': args.maximum_cost,
           'frames': len(frames), 'pairs_by_total_lift_rank': dict(sorted(counts.items())),
           'rational_exclusions_by_full_modular_minor': minor_proofs,
           'pairs_checked_by_rational_elimination': rational_checks,
           'rational_hits': hits,
           'joint_noise_cancellation_positive_control': True,
           'scope': 'Exact finite-family exclusion in the necessary fixed-vector quotient: two arbitrary same-frame gathers at different contact frames, within the stated total full-lift rank. Not a bound for three or more frames, early feedback, changed source words or arbitrary physical programs.',
           'new_kappa_claimed': False, 'elapsed_seconds': time.monotonic()-begin}
    name = 'exact-pair-check.json' if args.maximum_cost == 4 else f'exact-pair-check-budget{args.maximum_cost}.json'
    (HERE/'evidence'/name).write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps(out), flush=True)


if __name__ == '__main__':
    main()
