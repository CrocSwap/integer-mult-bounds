"""Two architectural budget screens; no finite network or improved exponent.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
Only exact Fraction arithmetic determines acceptance. Float output is diagnostic.
"""
from collections import Counter
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/kappa-nine'))
from target_budget import audit as baseline_audit, encode, moment, require


def subtract(A, B):
    return [[x-y for x, y in zip(a, b)] for a, b in zip(A, B)]


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(A, B):
    return [[sum(x*y for x, y in zip(a, b)) for b in zip(*B)] for a in A]


def tensor(A, B):
    return [[x*y for x in a for y in b] for a in A for b in B]


def rank(A):
    rows = [[Q(x) for x in row] for row in A]
    k = 0
    for j in range(len(rows[0])):
        pivot = next((i for i in range(k, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[k], rows[pivot] = rows[pivot], rows[k]
        c = rows[k][j]
        rows[k] = [x/c for x in rows[k]]
        for i in range(k+1, len(rows)):
            c = rows[i][j]
            rows[i] = [x-c*y for x, y in zip(rows[i], rows[k])]
        k += 1
    return k


def join_control(P, Qp):
    """Exact control for the general commuting-idempotent proof in REPORT.md."""
    da, db = len(P), len(Qp)
    require(multiply(P, P) == P and multiply(Qp, Qp) == Qp, 'idempotents required')
    require(rank(P) == rank(Qp) == 1, 'rank-one labels required')
    E = tensor(identity(da), Qp)
    D = tensor(subtract(identity(da), P), identity(db))
    I = identity(da*db)
    old = rank(subtract(I, E)) + rank(D)
    new = rank(subtract(D, E))
    require(multiply(E, D) == multiply(D, E), 'commuting tensor factors')
    require(new == da*db-da-db+2 and old-new == da*db-2, 'join rank formula')
    return dict(dimensions=[da, db], old_rank=old, joined_rank=new,
                rank_saved=old-new, capacity_removed=da*db, deficit_lost=2)


def composition_screen():
    # Per data pair. All fixed central loss is already erased; every
    # retained macro and every new join gets ideal single-child batching.
    da, db, m = 23, 25, 575
    fixed = Counter({528: 2, 1: 1, 22: 2, 24: 2})
    floor = fixed.copy()
    floor.update({da: 1, m-da: 1, db: 1, m-db: 1})
    joined = floor.copy()
    joined[m-da] -= 1
    joined[m-db] -= 1
    joined[m-da-db+2] += 1
    old_bound, joined_bound = moment(floor, m, 4), moment(joined, m, 3)
    old_boundary = moment({m-da: 1, m-db: 1}, m, 1)
    new_boundary = moment({m-da-db+2: 1}, m, 1)
    slope = (1+new_boundary[0]-old_boundary[1],
             1+new_boundary[1]-old_boundary[0])
    extra = {
        'unpaired_first': moment({da: 1, m-da: 1}, m, 1),
        'unpaired_second': moment({db: 1, m-db: 1}, m, 1),
        'paired': moment({da: 1, db: 1, m-da-db+2: 1}, m, 1),
    }
    require(old_bound[0] > 1 and slope[0] > 0, 'sharing exclusion failed')
    require(all(x[0] > 1 for x in extra.values()), 'extra role coefficient')
    # Oblique, nonsymmetric rational controls; not a search or a new network.
    controls = [join_control([[Q(1), Q(2)], [Q(0), Q(0)]],
                              [[Q(1), Q(-1), Q(3)], [Q(0)]*3, [Q(0)]*3]),
                join_control([[Q(1,2), Q(1,2)], [Q(1,2), Q(1,2)]],
                              [[Q(1), Q(0)], [Q(0), Q(0)]])]
    # Positive control: genuinely nested cuts save the full removed capacity.
    E = [[Q(1), Q(0)], [Q(0), Q(0)]]
    D = identity(2)
    nested_saved = rank(subtract(identity(2), E))+rank(D)-rank(subtract(D, E))
    require(nested_saved == 2, 'nested positive control')
    return dict(status='REJECTED at target before construction search',
        model='Sequential reuse of independent first/second-axis auxiliary roles; fixed E=I tensor Q and D=(I-P) tensor I cuts; other macro obligations retained.',
        unshared_floor_moment=old_bound, fully_shared_floor_moment=joined_bound,
        numerator_minus_role_volume_slope_per_join=slope,
        additional_role_moments=extra, exact_matrix_controls=controls,
        nested_control_rank_saved=nested_saved,
        proof_scope='Every sharing fraction 0<=x<=1 of the mandatory source banks, and arbitrary extra paired/unpaired roles, under the stated ledger. Does not cover data-role borrowing, changed cuts, recoding, or removed internal computations.')


def cube_screen():
    q, d = 16, 32
    n = 2**(2*q-1)
    r = 2*sum(comb(2*q-1, i) for i in range(q//2))
    # Candidate: recursive Cayley/Boolean-subset side program for C+I,
    # replacing the raw edge compiler. Give it impossible advantages to
    # screen BEFORE designing any such program or its rational frames.
    m = d*d
    rows = Counter({(d-1)**2: 2, 1: 1, d-1: 4})
    free = moment(rows, m, 2)
    with_return = rows.copy()
    with_return[d] += Q(2*r, n)
    source_floor = rows.copy()
    source_floor[d] += 2
    source_floor[m-d] += 2
    coefficient = moment({d: 1, m-d: 1}, m, 1)
    require(free[0] > 1 and coefficient[0] > 1, 'cube target exclusion failed')
    require(n > 6*r*d, 'wrong positive historical core')
    return dict(status='REJECTED at target before construction search',
        q=q, labels=n, rational_dimension=d, supplied_binary_factor_size=r,
        positive_historical_three_stage_numerator=n-6*r*d,
        hypothetical_pair_dimension=m,
        zero_auxiliary_zero_central_loss_moment=free,
        supplied_factor_full_center_span_moment=moment(with_return, m, 2),
        zero_central_loss_one_source_per_label_moment=moment(source_floor, m, 4),
        auxiliary_coefficient=coefficient,
        lower_bound_rows=rows,
        proof_scope='Rank-one 32x32 two-stage macro ledger only, even with every central cost and all auxiliary roles erased and ideal macro batching. Not an exclusion of all cube topologies or of cross-macro/fewer-stage transfers.',
        complex_obstruction='Direct reduction of signed cube labels modulo 2 gives the same isotropic all-ones vector (dimension 32); it does not supply the existing nondegenerate phase-label interface.')


def audit():
    baseline = baseline_audit()  # Replays pinned hashes, profiles and 47 assembly rows.
    sources = [ROOT/'research/kappa-nine/target_budget.py',
               ROOT/'research/kappa-nine/baseline/SOURCE.json',
               ROOT/'docs/research/stage-pair-audit.md',
               ROOT/'docs/research/cube-core-family.md',
               ROOT/'docs/research/stronger-rank-screens.md',
               ROOT/'research/pair-assembly/balanced_assembly.py']
    return dict(status='TWO SCOPED ARCHITECTURAL REJECTIONS; NO NEW KAPPA',
        target_kappa=Q(1,512), necessary_bit_saving=Q(1,511),
        necessary_complex_saving_at_beta_1_over_20=Q(20,9709),
        baseline=baseline['baseline'],
        baseline_47_constraints_replayed=len(baseline['hypothetical_joint_target']['all_47_slacks']),
        composition=composition_screen(), different_topology=cube_screen(),
        construction_experiments=0,
        reason_no_construction_experiments='Both optimistic scoped budgets fail. Exact matrix controls validate the join identity; they are not a candidate search.',
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit()
    if args.output:
        args.output.write_text(json.dumps(encode(result), indent=2, sort_keys=True)+'\n')
    for name in ('composition', 'different_topology'):
        print(name+': '+result[name]['status'])
    print('PASS pinned baseline, exact root bounds, join controls; no new network or exponent')
