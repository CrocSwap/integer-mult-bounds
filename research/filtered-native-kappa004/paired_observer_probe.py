#!/usr/bin/env python3
"""Screen pairs of noisy observations, then recheck every hit rationally.

Observations from different frames may cancel each other's nuisance. This
is intentionally outside the individually-clean observer bound.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import argparse
import gzip
import itertools
import json
import sys
import time

HERE = Path(__file__).resolve().parent
PRIME = 65537


def mod(x):
    x = Q(x)
    return x.numerator*pow(x.denominator, -1, PRIME) % PRIME


def add(a, b, c):
    for k, x in b.items():
        z = (a.get(k, 0)+c*x) % PRIME
        if z:
            a[k] = z
        else:
            a.pop(k, None)


def insert(basis, row, tag):
    row, tag = dict(row), dict(tag)
    while row:
        p = min(row)
        if p not in basis:
            a = pow(row[p], -1, PRIME)
            basis[p] = ({k: x*a % PRIME for k, x in row.items()},
                        {k: x*a % PRIME for k, x in tag.items()})
            return None
        b, t = basis[p]
        a = row[p]
        add(row, b, -a)
        add(tag, t, -a)
    return tag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--packet', type=Path, required=True)
    ap.add_argument('--maximum-pair-lift-rank', type=int, default=4)
    args = ap.parse_args()
    begin = time.monotonic()
    path = HERE/'evidence/observer-subspaces.json.gz'
    data = json.loads(gzip.decompress(path.read_bytes()))
    targets = [{int(i): Q(a) for i, a in row} for row in data['targets']]
    tb = {}
    for k, row in enumerate(targets):
        z = insert(tb, {i: mod(a) for i, a in row.items()}, {k: 1})
        assert z is None
    frames = []
    for item in data['frames']:
        if 9-item['rank'] >= args.maximum_pair_lift_rank:
            continue
        basis = {}
        original = []
        for record in item['rows']:
            original.append((record['description'], {int(i): Q(a) for i, a in record['row']}))
            row = {int(i): mod(a) for i, a in record['row']}
            tag = {}
            for p, (b, t) in sorted(tb.items()):
                a = row.get(p, 0)
                if a:
                    add(row, b, -a)
                    add(tag, t, a)
            relation = insert(basis, row, tag)
            # A modular rank degeneration can create a spurious clean mode;
            # record it as a pair hit for rational checking, never a proof.
            assert not relation, 'Unexpected modular individual-mode direction'
        if basis:
            frames.append({**item, 'basis': basis, 'original': original})
    sys.path[:0] = [str(args.packet/'research/operator_alignment_next'),
                   str(args.packet/'research/retained_state_next')]
    import augmented_rank1_observers as obs
    tested, hits, checked = Counter(), [], []
    for a, b in itertools.combinations(frames, 2):
        price = 18-a['rank']-b['rank']
        if price > args.maximum_pair_lift_rank:
            continue
        tested[price] += 1
        basis = dict(a['basis'])
        found = []
        for row, tag in b['basis'].values():
            relation = insert(basis, row, tag)
            if relation:
                found.append(relation)
        if not found:
            continue
        hits.append((a['frame'], b['frame']))
        _, solutions = obs.intersection(a['original']+b['original'], targets)
        records = []
        joined = a['original']+b['original']
        for target, recipe in solutions:
            records.append({'target_modes': {str(k): str(x) for k, x in target.items()},
                            'gather': [{**joined[j][0], 'coefficient': str(x)} for j, x in recipe.items()]})
        checked.append({'frames': [a['frame'], b['frame']], 'pair_lift_rank': price,
                        'rational_mode_dimension': len(solutions), 'solutions': records})
        print('PAIR', a['frame'], b['frame'], price, len(solutions), flush=True)
    out = {'status': 'PAIRED_NOISY_OBSERVATION_SCREEN', 'prime': PRIME,
           'input_sha256': sha256(path.read_bytes()).hexdigest(),
           'frames': len(frames), 'pairs_tested_by_total_lift_rank': dict(sorted(tested.items())),
           'modular_hits': len(hits), 'rational_rechecks': checked,
           'scope': 'Fixed-vector augmentation; two same-frame gathers lifted to full, with summed lift rank at most the stated budget. Positive modular hits are rechecked over Q. A negative modular screen is discovery evidence only, not rational infeasibility; a rational positive is still short of the physical operator identity.',
           'new_kappa_claimed': False, 'elapsed_seconds': time.monotonic()-begin}
    (HERE/'evidence/paired-observer-probe.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'rational_rechecks'}), flush=True)


if __name__ == '__main__':
    main()
