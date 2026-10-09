#!/usr/bin/env python3
"""Independent small local-ring model of low-residue bank scheduling.

This is a diagnostic for the general argument in BANK-SCHEDULE.md, not a
substitute for PR186's physical word or an all-size tape implementation.
Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
from itertools import product
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


def mul(a, b, modulus):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2)) % modulus
                 for i in range(2) for j in range(2))


def inv(a, modulus):
    d = pow((a[0]*a[3]-a[1]*a[2]) % modulus, -1, modulus)
    return tuple(d*x % modulus for x in (a[3], -a[1], -a[2], a[0]))


def main():
    # GL_2(Z/9): 48 residue classes, each with 81 high-matrix lifts.
    modulus = 9
    group = [a for a in product(range(modulus), repeat=4)
             if (a[0]*a[3]-a[1]*a[2]) % 3]
    require(len(group) == 3888, 'complete group inventory')
    classes = defaultdict(list)
    for a in group:
        classes[tuple(x % 3 for x in a)].append(a)
    require(len(classes) == 48 and {len(v) for v in classes.values()} == {81},
            'complete uniform high-matrix fibers')
    identity, exchange, projector = (1, 0, 0, 1), (0, 1, 1, 0), (1, 0, 0, 0)
    maps = (identity, exchange)
    visits = defaultdict(list)
    for residue, invocations in sorted(classes.items()):
        occupied = set()
        for g in invocations:
            for role, h in enumerate(maps):
                bank = mul(g, inv(h, modulus), modulus)
                require(bank not in occupied, 'no shared live bank in one residue batch')
                occupied.add(bank)
                relative = mul(mul(g, projector, modulus), inv(g, modulus), modulus)
                visits[bank].append((role, relative))
    require(set(visits) == set(group), 'all banks used')
    for bank, schedule in visits.items():
        require(sorted(r for r, _ in schedule) == [0, 1], 'every bank receives every role once')
        ps = [p for _, p in schedule]
        require(tuple((x+y) % modulus for x, y in zip(*ps)) == identity,
                'transported residuals exhaust the ambient space')
        require(mul(ps[0], ps[1], modulus) == (0, 0, 0, 0), 'disjoint residuals')
        # Execute on every basis vector of two complete 2-coordinate banks.
        for column in range(4):
            z = [int(j == column) for j in range(4)]
            for p in ps:
                x, y = z[:2], z[2:]
                delta = [sum(p[2*i+j]*(y[j]-x[j]) for j in range(2)) % modulus
                         for i in range(2)]
                z = [(x[i]+delta[i]) % modulus for i in range(2)] + [
                     (y[i]-delta[i]) % modulus for i in range(2)]
            require(z == [int(j == (column+2) % 4) for j in range(4)],
                    'full completed endpoint on arbitrary contents')
    # A same-embedding substitution must fail the same live-bank predicate.
    occupied = set()
    rejected = False
    try:
        for h in (identity, identity):
            bank = mul(identity, inv(h, modulus), modulus)
            require(bank not in occupied, 'no shared live bank in one residue batch')
            occupied.add(bank)
    except ValueError:
        rejected = True
    require(rejected, 'duplicate embedding was not rejected')
    print(json.dumps(dict(status='PASS', modulus=modulus, invocation_vertices=len(group),
        residue_batches=len(classes), high_lifts_per_batch=81,
        role_visits=2*len(group), full_endpoint_basis_checks=4*len(group),
        duplicate_embedding_collides=True,
        scope='finite scheduling diagnostic; general proof and PR186 word checks are separate'), sort_keys=True))


if __name__ == '__main__':
    main()
