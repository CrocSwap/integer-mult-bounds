#!/usr/bin/env python3
"""Exact checks for a scoped point-additive frame obstruction over Q.

The general proof is in docs/research/additive-label-obstruction.md. Modular
ranks below are lower bounds on ranks of INTEGER matrices over Q, not claims
that finite-field label constructions lift to rational constructions.
"""
from itertools import combinations
from pathlib import Path
import json

from certify import require

ROOT = Path(__file__).resolve().parents[1]


def rank_mod(rows, prime=101):
    basis = {}
    for original in rows:
        row = [x % prime for x in original]
        for pivot, reduced in sorted(basis.items()):
            if row[pivot]:
                factor = row[pivot]
                row = [(x-factor*y) % prime for x, y in zip(row, reduced)]
        pivot = next((i for i, x in enumerate(row) if x), None)
        if pivot is not None:
            inverse = pow(row[pivot], -1, prime)
            basis[pivot] = [(x*inverse) % prime for x in row]
    return len(basis)


def neighbor_rows(h, target=(0, 1, 2)):
    target = set(target)
    return [[int(i in t) for i in range(h)]
            for t in combinations(range(h), 3) if len(set(t) & target) == 1]


def certificate():
    checks = []
    for h in range(6, 25):
        rows = neighbor_rows(h)
        annihilator = [2 if i < 3 else -1 for i in range(h)]
        require(all(sum(a*b for a, b in zip(row, annihilator)) == 0
                    for row in rows), 'Wrong rational annihilator')
        rank = rank_mod(rows)
        require(rank == h-1, 'Neighbor hyperplane lower bound failed')
        checks.append(dict(h=h, neighbor_count=len(rows),
                           rational_rank=rank, lower_bound_prime=101))
    return {
        'scope': 'One factor in a block fitting representation has frames '
                 'A_T=A_0+sum_{i in T} A_i, up to invertible local basis '
                 'changes; the other factor is arbitrary. Characteristic zero, h>=6.',
        'general_rank_lower': 'k*h for h!=9; k*(h-1) for h=9',
        'target_h': 24, 'target_label_rank': 2,
        'target_ambient_rank_lower': 48,
        'hyperbolic_split_with_one_additive_side_dimension_lower': 24,
        'neighbor_hyperplane_checks': checks,
        'status': 'SCOPED OBSTRUCTION; no new multiplication exponent',
        'unrestricted_indefinite_rank_two_target': 'OPEN',
    }


if __name__ == '__main__':
    out = certificate()
    (ROOT/'certificates/additive-label-audit.json').write_text(
        json.dumps(out, indent=2, sort_keys=True)+'\n')
    print('PASS: arbitrary point-additive rank-two frames need dimension 48 at h=24')
