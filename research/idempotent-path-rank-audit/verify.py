#!/usr/bin/env python3
"""Reproduce a scoped idempotent path-rank audit using exact rational arithmetic.

Copyright 2026 Curtis Dransfield. Apache-2.0; substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from linalg import (F, add, analyze_pair, eye, inverse, kron, matrix, mul,
                    path_excess, rank, require, scale, serializable, sub, transpose)
from independent import independent_check, rank_by_minors


def verify_pins(root=ROOT, manifest=None):
    if manifest is None:
        manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for relative, expected in manifest['sha256'].items():
        actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
        require(actual == expected, 'Source pin mismatch: ' + relative)
    return dict(base_commit=manifest['base_commit'], checked_files=len(manifest['sha256']))


def named_witnesses():
    fixtures = json.loads((HERE / 'WITNESSES.json').read_text())
    output = {}
    for name, fixture in fixtures.items():
        P, Q = matrix(fixture['P']), matrix(fixture['Q'])
        profile = analyze_pair(P, Q)
        mats = P, Q, mul(P, Q), mul(Q, P), sub(sub(eye(len(P)), P), Q)
        independent_ranks = [rank_by_minors(M) for M in mats]
        require(independent_ranks == fixture['expected_ranks'], name + ': minor ranks changed')
        require([rank(M) for M in mats] == independent_ranks, name + ': rank implementations differ')
        direct = path_excess((P, sub(eye(len(P)), Q)))
        require(direct['excess'] == profile['minimum_path_excess'] == fixture['expected_excess'],
                name + ': direct-edge sharpness failed')
        output[name] = dict(P=P, Q=Q, profile=profile, independent_ranks=independent_ranks,
                            direct_edge=direct)
    P, Q = (matrix(fixtures['one_sided_rank_one'][k]) for k in ('P', 'Q'))
    PQ = mul(P, Q)
    require(sum(PQ[i][i] for i in range(len(PQ))) == 0 and rank(PQ) == 1,
            'Trace-zero nonzero product control failed')
    return output


def random_controls():
    rng = random.Random(71)
    cases = []
    for d in range(2, 7):
        for trial in range(6):
            labels = []
            for _ in range(2):
                # Invertibility is constructive: product of determinant-one shears.
                S = eye(d)
                for _ in range(2*d):
                    i, j = rng.sample(range(d), 2)
                    shear = [list(row) for row in eye(d)]
                    shear[i][j] = F(rng.choice((-2, -1, 1, 2)), rng.choice((1, 2, 3)))
                    S = mul(matrix(shear), S)
                label_rank = rng.randrange(d+1)
                D = matrix([[int(i == j and i < label_rank) for j in range(d)] for i in range(d)])
                labels.append(mul(mul(S, D), inverse(S)))
            P, Q = labels
            profile = analyze_pair(P, Q)
            internal = [matrix([[F(rng.randrange(-2, 3), rng.randrange(1, 4))
                                 for _ in range(d)] for _ in range(d)]) for _ in range(2)]
            path = path_excess((P, *internal, sub(eye(d), Q)))
            require(path['excess'] >= profile['minimum_path_excess'], 'Arbitrary internal path failed')
            cases.append(dict(d=d, trial=trial, P=P, Q=Q, internal=internal,
                              profile=profile, path=path))
    encoded = json.dumps(serializable(cases), sort_keys=True, separators=(',', ':')).encode()
    return dict(seed=71, dimensions=list(range(2, 7)), trials_per_dimension=6,
                completed_pairs=len(cases), arbitrary_internal_matrices=2*len(cases),
                generator='2d elementary rational shears per label; independent uniform ranks 0..d',
                stopping_rule='Exactly 6 pairs in each dimension 2..6; no adaptive search',
                transcript_sha256=hashlib.sha256(encoded).hexdigest(),
                product_rank_histogram=dict(sorted(Counter(
                    str((x['profile']['rank_PQ'], x['profile']['rank_QP'])) for x in cases).items())))


def original_contract_controls():
    sys.path.insert(0, str(ROOT / 'scripts'))
    from audit_cancellation import line_projection
    from experiments.rank_product_core import check_projector_core, compile_projector_core
    from experiments.block_core import check_block_projectors, compile_block

    triples = list(combinations(range(6), 3))
    H = sub(eye(6), scale(matrix([[1]*6 for _ in range(6)]), F(1, 9)))
    require(rank(H) == 6, 'Original h=6 form is degenerate')
    labels = [matrix(line_projection(6, T)) for T in triples]
    for P in labels:
        require(mul(H, P) == mul(transpose(P), H), 'Original common form failed')
    hist = Counter()
    for i, P in enumerate(labels):
        for j, Q in enumerate(labels):
            profile = analyze_pair(P, Q)
            overlap = len(set(triples[i]) & set(triples[j]))
            expected = 0 if overlap == 1 else 2
            require(profile['minimum_path_excess'] == expected, 'Original triple penalty changed')
            hist[str(overlap)] += 1

    fixture = json.loads((HERE / 'WITNESSES.json').read_text())['one_sided_rank_one']
    P, Q = matrix(fixture['P']), matrix(fixture['Q'])
    rejected = []
    for ell, checker, projections in (
        (1, check_projector_core, (P, Q)),
        (2, check_block_projectors, (kron(P, eye(2)), kron(Q, eye(2))))):
        checker([1, 2], projections)  # No side edge: these are legal labels.
        for rows in ([3, 2], [1, 3]):
            try:
                checker(rows, projections)
            except ValueError as exc:
                require('mutual' in str(exc), 'Unexpected original rejection reason')
                rejected.append(dict(ell=ell, rows=rows, reason=str(exc)))
            else:
                raise ValueError('Original checker accepted one-sided annihilation')
    check_projector_core([3, 3], (P, sub(eye(2), P)))
    check_block_projectors([3, 3], (kron(P, eye(2)), kron(sub(eye(2), P), eye(2))))

    # Check actual time-2/time-5 compiler matrices, including reversed stage 1.
    # Eight groups have sizes 2,1,2,1,1,2,1,2 for these n=2 controls.
    compiled = []
    for name in ('one_sided_rank_one', 'asymmetric_rank_two'):
        f = json.loads((HERE / 'WITNESSES.json').read_text())[name]
        Ps = [matrix(f[k]) for k in ('P', 'Q')]
        d, ell = len(Ps[0]), rank(Ps[0])
        if ell == 1:
            candidate, _ = compile_projector_core([1, 2], Ps)
        else:
            candidate, _ = compile_block(check_block_projectors([1, 2], Ps))
        offset = 0
        checked = []
        for stage in range(3):
            for fixed in product(range(2), repeat=2):
                a = list(fixed)
                a.insert(stage, 0)
                prior, future = eye(1), eye(1)
                for j in range(stage):
                    prior = kron(prior, Ps[a[j]])
                for j in range(stage+1, 3):
                    future = kron(future, Ps[a[j]])
                B = sub(eye(len(prior)), prior)
                common = kron(kron(B, eye(d)), future)
                endpoints = []
                for t, group_start in ((0, 3), (1, 7)):
                    position = t if stage != 1 else 1-t
                    frame = matrix(candidate['gates'][offset + group_start + position]['frame'])
                    active = Ps[t] if group_start == 3 else sub(eye(d), Ps[t])
                    variable = kron(kron(prior, active), future)
                    require(frame == add(common, variable), 'Compiled endpoint differs from formula')
                    require(not any(x for row in mul(common, variable) for x in row)
                            and not any(x for row in mul(variable, common) for x in row),
                            'Compiler summands fail mutual annihilation')
                    require(rank(frame) == rank(common) + rank(variable), 'Compiler rank additivity failed')
                    endpoints.append(frame)
                actual = path_excess(endpoints)
                multiplier = rank(prior)*rank(future)
                expected = multiplier*(rank(mul(Ps[0], Ps[1])) + rank(mul(Ps[1], Ps[0])))
                require(actual['excess'] == expected, 'Tensor-stage excess failed')
                checked.append(dict(stage=stage, fixed=fixed, spectator_rank=multiplier,
                                    exact_excess=actual['excess']))
                offset += 12
        require(offset == len(candidate['gates']), 'Compiler gate coverage changed')
        compiled.append(dict(name=name, ambient_dimension=d, label_rank=ell,
                             compiled_gates=len(candidate['gates']), endpoint_pairs=checked,
                             scope='Actual endpoint matrices only; no full scalar/rank-sum certification'))
    return dict(original_triples=dict(h=6, labels=20, ordered_pairs=400,
                                      intersection_histogram=dict(sorted(hist.items()))),
                original_mutual_annihilation_rejections=rejected,
                positive_contract_controls=4, compiled_endpoint_controls=compiled)


def certificate():
    pins = verify_pins()  # Before importing any inherited implementation.
    result = dict(status='PASS_EXACT_IDEMPOTENT_PATH_RANK_AUDIT', source_pins=pins,
                  witnesses=named_witnesses(), independent=independent_check(),
                  generated_controls=random_controls(), inherited_controls=original_contract_controls(),
                  scope='Written proof plus finite exact evidence; no new circuit, no new kappa, '
                        'no formal proof of the multiplication theorem')
    return serializable(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Write a fresh certificate; refuses to overwrite')
    args = parser.parse_args()
    result = certificate()
    if args.out:
        with args.out.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        require(result == json.loads((HERE / 'CERTIFICATE.json').read_text()),
                'Recomputed certificate differs from committed evidence')
    print('PASS_EXACT_IDEMPOTENT_PATH_RANK_AUDIT: 10 named witnesses; 1936 exhaustive pairs; '
          '30 generated pairs; 400 original triple pairs; 24 compiled endpoint pairs')


if __name__ == '__main__':
    main()
