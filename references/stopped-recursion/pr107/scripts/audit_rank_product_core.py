#!/usr/bin/env python3
"""Recover a positive rank-product core; no improved multiplication witness."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import json

from certify import require, verify_sources
from finite_bit_contract import inspect_candidate
from experiments.rank_product_core import compile_core, compile_fitting_pair, counts
from audit_joint_frames import matrix, product, sub, row_basis
from prepare_layers import serializable
from search_network import log_integer_bounds


ROOT = Path(__file__).resolve().parents[1]


def controls():
    return (
        ('diagonal', [1, 2], [[1, 0], [0, 1]], [[1, 0], [0, 1]]),
        ('symmetric-rank-one', [3, 3], [[1, 0], [0, 1]], [[1, 0], [0, 1]]),
        ('directed', [3, 2], [[1, 0], [0, 1]], [[1, 0], [0, 1]]),
        ('indefinite', [3, 3], [[1, Q(1, 2)], [1, 2]], [[1, 0], [0, -1]]),
        ('unequal-ranks', [3, 6, 4], [[1, 0], [0, 1], [1, 0]], [[1, 0], [0, 1]]),
    )


def nonselfadjoint_control():
    rows = [5, 2, 5]
    fitting = [[1, 1, 0], [1, 1, 1], [0, 0, 1]]
    candidate, expected = compile_fitting_pair(rows, fitting)
    checked = inspect_candidate(candidate, require_deficit=False)
    require(checked['s'] == expected['s'], 'Oblique compiler accounting failed')
    # P0 and P1 have the same image and distinct kernels. More explicitly,
    # P_i^T H=H P_i for both forces H_00=H_01=0, so every symmetric H is singular.
    Ps = [matrix([[1, 0], [0, 0]]), matrix([[1, 1], [0, 0]])]
    symmetric_basis = [matrix([[1, 0], [0, 0]]), matrix([[0, 1], [1, 0]]), matrix([[0, 0], [0, 1]])]
    equations = []
    for P in Ps:
        differences = [sub(product(matrix(zip(*P)), H), product(H, P)) for H in symmetric_basis]
        equations += [tuple(D[i][j] for D in differences) for i in range(2) for j in range(2)]
    require(row_basis(equations) == matrix([[1, 0, 0], [0, 1, 0]]), 'Common-form obstruction changed')
    return dict(binary_rows=rows, rational_fitting_matrix=fitting, counts=expected,
                checked=checked, common_nondegenerate_symmetric_form_exists=False,
                common_symmetric_form_family='[[0,0],[0,t]], always singular',
                symmetric_form_constraint_basis=row_basis(equations),
                scope='An exact negative-deficit control proving the compiler admits representations outside a common symmetric-form ansatz; not a positive-deficit example.')


def triple_core(h, deletions=0):
    """Compact exact core: triples except the last specified lexicographic ones.

    H=9I-J, C_ST=|S intersection T| mod 2. Full binary incidence rank is
    certified by elimination; the same nonsingular odd minor proves full
    rational incidence rank. No n-by-n matrix or full network is expanded.
    """
    require(h >= 4 and h != 9, 'Use a nondegenerate triple ambient form')
    triples = list(combinations(range(h), 3))
    require(type(deletions) is int and 0 <= deletions < len(triples), 'Invalid deletion count')
    kept = triples[:len(triples)-deletions]
    removed = triples[len(kept):]
    basis = {}; witnesses = []
    for T in kept:
        x = sum(1 << i for i in T)
        for pivot, b in sorted(basis.items()):
            if x >> pivot & 1:
                x ^= b
        if x:
            basis[(x & -x).bit_length()-1] = x
            witnesses.append(T)
    require(len(basis) == h, 'The selected core lost full incidence rank')
    v = comb(h, 3); degree = 3*comb(h-3, 2)
    removed_edges = sum(len(set(S) & set(T)) == 1 for S in removed for T in removed)
    side_edges = v*degree-2*deletions*degree+removed_edges
    n = len(kept)
    accounting = counts(n, h, h, side_edges)
    pair_types = []
    for intersection in range(4):
        binary = intersection % 2
        gram = 9*(intersection-1)
        require(intersection == 3 or not binary or gram == 0, 'Off-diagonal compatibility failed')
        pair_types.append(dict(intersection=intersection, binary_coefficient=binary,
                               rational_inner_product=gram, diagonal=intersection == 3))
    require((9-h)*9**(h-1) != 0, 'Ambient form determinant vanishes')
    lo, hi = log_integer_bounds(h**3)
    eta = accounting['relative_deficit']
    result = dict(h=h, n=n, deletions=deletions, removed_labels=removed,
                  full_binary_and_rational_incidence_rank=h, independent_labels=witnesses,
                  label_sha256=sha256(json.dumps(kept, separators=(',', ':')).encode()).hexdigest(),
                  binary_core_rank=h, rational_gram_rank=h,
                  rational_form='9I-J', rational_form_determinant=(9-h)*9**(h-1),
                  diagonal_norm=18, ordered_side_edges=side_edges,
                  removed_internal_directed_edges=removed_edges, pair_types=pair_types,
                  accounting=accounting,
                  full_network_expanded=False,
                  basis_of_positive_claim='Written general compiler plus exact core and count certificates; not a full expanded-matrix run')
    if eta > 0:
        result['saving_interval'] = [eta/hi, eta/((1-eta)*lo)]
    return result


def dimension_screens():
    """Optimistic dimension ceilings for this three-factor line-label compiler.

    W>=2n^3 and Delta<n^3 imply eta<1/(2d^3). The log inequality gives
    a<1/((2d^3-1)*log(d^3)), even before any side or center cost is charged.
    """
    targets = [('beat-retained-bit', Q(296, 10**11), 219),
               ('kappa-2^-30', 5*Q(1, 2**30), 190),
               ('kappa-2^-24', 5*Q(1, 2**24), 53),
               ('kappa-2^-16', 5*Q(1, 2**16), 10)]
    out = []
    for name, target, excluded in targets:
        lo, hi = log_integer_bounds(excluded**3)
        upper = 1/((2*excluded**3-1)*lo)
        previous_lo, previous_hi = log_integer_bounds((excluded-1)**3)
        previous_lower = 1/((2*(excluded-1)**3-1)*previous_hi)
        require(upper < target < previous_lower, 'Dimension threshold not certified')
        out.append(dict(target=name, required_bit_saving=target,
                        first_excluded_dimension=excluded, all_larger_dimensions_excluded=True,
                        upper_bound_at_excluded=upper,
                        optimistic_bound_lower_at_previous=previous_lower,
                        achievability_established=False,
                        interpretation='The preceding dimension merely passes this necessary screen.'))
    return out


def fixed_graph_rank_floor(h=50):
    """Every binary fitting C for the retained rational triple lines.

    Off-diagonal entries must vanish for even intersections. Triples through
    a fixed pair give an identity principal minor of order h-2. Disjoint
    four-point blocks each contribute their four triples, also an identity
    principal minor. Neither argument assumes symmetry or particular ones
    at intersection-one pairs.
    """
    require(h >= 4, 'Need at least four ground points')
    pair = [(0, 1, i) for i in range(2, h)]
    blocks = [T for start in range(0, h-3, 4)
              for T in combinations(range(start, start+4), 3)]
    for family in (pair, blocks):
        require(all(len(set(S) & set(T)) % 2 == 0
                    for i, S in enumerate(family) for T in family[i+1:]),
                'Claimed identity minor contains an allowed off-diagonal edge')
    lower = max(len(pair), len(blocks))
    result = dict(h=h, rank_lower_bound=lower, fixed_pair_labels=pair,
                  block_labels=blocks, canonical_rank=h,
                  scope='Arbitrary binary diagonal-one matrices supported on the retained triple orthogonality graph; directed matrices allowed.')
    if h == 50:
        n, d, R = 19600, 50, 509194
        W = 2*n**3+2*n*n*(R+lower)
        delta = n**3-6*n*n*lower*d
        eta = Q(delta, W*d**3)
        lo, hi = log_integer_bounds(d**3)
        upper = eta/((1-eta)*lo)
        require(upper/5 < Q(1, 2**30), 'Fixed-side central-rank bound crossed target')
        result['fixed_side_accounting'] = dict(side_roles_per_invocation=R,
            optimistic_center_roles=lower, W=W, deficit=delta, relative_deficit=eta,
            bit_saving_upper=upper, kappa_upper=upper/5, below_2_to_minus_30=True,
            scope='Retains the paired side-role count and stage-sharing ledger; does not exclude changing C and reducing side cost together.')
    return result


def certificate():
    exact = []
    for name, rows, vectors, form in controls():
        candidate, expected = compile_core(rows, vectors, form)
        checked = inspect_candidate(candidate, require_deficit=False)
        require(checked['s'] == expected['s'] and checked['deficit'] == expected['deficit'],
                'Expanded edge accounting disagrees with compiler formula')
        exact.append(dict(name=name, counts=expected, checked=checked,
                          candidate_sha256=sha256(json.dumps(serializable(candidate), sort_keys=True,
                                                             separators=(',', ':')).encode()).hexdigest()))
    smallest_full = triple_core(39)
    extracted = triple_core(39, 12)
    boundary = triple_core(39, 13)
    require(smallest_full['accounting']['positive'] and extracted['accounting']['positive'],
            'Expected positive core missing')
    require(boundary['accounting']['deficit'] == 0, 'Deletion threshold is wrong')
    require(comb(38, 3) < 6*38**2 and comb(39, 3) > 6*39**2, 'Wrong triple-family threshold')
    retained = json.loads((ROOT/'certificates/paired-network.json').read_text())['bit_counts']
    n, r, d = 19600, 50, 50
    R = int(retained['side_roles_per_invocation'])
    W = 2*n**3+2*n*n*(R+r)
    D = n**3-6*n*n*r*d
    require(W == int(retained['W']) and D == int(retained['D']), 'Retained ledger mismatch')
    eta = Q(D, W*d**3)
    require(eta == Q(retained['eta']), 'Retained relative deficit mismatch')
    sources = ('scripts/audit_rank_product_core.py', 'scripts/experiments/rank_product_core.py',
               'scripts/finite_bit_contract.py', 'scripts/audit_joint_frames.py',
               'scripts/audit_stage_pair.py', 'certificates/paired-network.json',
               'docs/research/rank-product-core.md')
    return dict(status='POSITIVE CORE RECOVERED AND ABSTRACT COMPILER CHECKED; NO NEW KAPPA',
                upstream_commit=verify_sources(), exact_expanded_controls=exact,
                nonselfadjoint_expanded_control=nonselfadjoint_control(),
                smallest_full_triple_core=smallest_full, extracted_positive_core=extracted,
                zero_deficit_boundary=boundary,
                retained_core=dict(n=n, binary_rank=r, rational_dimension=d, density=Q(n, r*d),
                    retained_fraction_of_gross_deficit=Q(D, n**3), side_roles_per_invocation=R,
                    W=W, m=d**3, deficit=D, relative_deficit=eta,
                    current_certified_bit_saving=Q(296, 10**11)),
                general_template=dict(m='d^3', W='2*n^3+3*n^2*(E+r)',
                    deficit='n^3-6*n^2*r*d', positive_iff='n>6*r*d',
                    relative_deficit='(1-6*r*d/n)/(d^3*(2+3*(E+r)/n))',
                    side_roles='E is the number of off-diagonal ones in C; edge-explicit, no sharing assumed'),
                dimension_screens=dimension_screens(),
                fixed_triple_graph_rank_floor=fixed_graph_rank_floor(),
                same_field_barrier='If C and the rational fitting matrix F were low-rank over the same field, their diagonal Hadamard product would imply n<=rank(C)*rank(F). The successful core uses different fields.',
                scope='The extracted core is positive but much weaker quantitatively than the retained network. Its full circuit is specified generatively, not expanded. Small expanded controls have negative deficits. No new assembly witness.',
                source_sha256={p: sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/rank-product-core.json').write_text(json.dumps(serializable(result), indent=2, sort_keys=True)+'\n')
    print('PASS six expanded circuit/frame controls, including a nonselfadjoint representation; positive n=9127, r=d=39 core; no new kappa.')
