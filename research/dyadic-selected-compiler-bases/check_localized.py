#!/usr/bin/env python3
"""Source-bound exact controls for carried dyadic projector bases.

This is finite corroboration for PROOF.md's localization argument, not an
enumeration of the selected enormous compiler word. No contributor module is
imported. Raw immutable records and the two literal compiler sources are pinned.
"""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import ast
import gzip
import json
import platform

HERE = Path(__file__).resolve().parent
# Read the local implementation directly; isolated replay must not depend on a
# pre-existing bytecode cache or on Python placing this directory on sys.path.
exec(compile((HERE/'localized.py').read_bytes(), str(HERE/'localized.py'), 'exec'), globals())
PINS = {
    'BIT-NATIVE-WORD.json.gz': '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78',
    'EFREE-RESULT.json': 'a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b',
    'EFREE-CALLER.json.gz': '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b',
    'check.py': '460ed9a77d66264b00c31d0a7f8dab1db9aab21ec4cc0eaf0452bd4be4ef585e',
}


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(v) for v in value]
    return value


def key(matrix):
    return tuple(tuple(row) for row in matrix)


def bareiss_determinant(matrix):
    """Independent fraction-free integer determinant for lattice-index checks."""
    a = [list(map(int, row)) for row in matrix]
    need(a == matrix, 'Bareiss needs integral entries')
    n, sign, previous = len(a), 1, 1
    for k in range(n-1):
        row = next((j for j in range(k, n) if a[j][k]), None)
        if row is None:
            return 0
        if row != k:
            a[row], a[k] = a[k], a[row]
            sign = -sign
        pivot = a[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                numerator = pivot*a[i][j]-a[i][k]*a[k][j]
                need(numerator % previous == 0, 'Bareiss exact division')
                a[i][j] = numerator//previous
            a[i][k] = 0
        previous = pivot
    return sign*a[-1][-1]


def pivot_columns(matrix):
    """Naive fixed rational pivot selection, used only as a negative control."""
    a = [[Q(x) for x in row] for row in matrix]
    rank, chosen = 0, []
    for j in range(len(a[0])):
        row = next((i for i in range(rank, len(a)) if a[i][j]), None)
        if row is None:
            continue
        a[rank], a[row] = a[row], a[rank]
        pivot = a[rank][j]
        a[rank] = [x/pivot for x in a[rank]]
        for i in range(rank+1, len(a)):
            coefficient = a[i][j]
            a[i] = [x-coefficient*y for x, y in zip(a[i], a[rank])]
        chosen.append(j)
        rank += 1
        if rank == len(a):
            break
    return chosen


def reduce_matrix(matrix, modulus):
    return [[Q(x).numerator*pow(Q(x).denominator, -1, modulus) % modulus
             for x in row] for row in matrix]


def modular_product(a, b, modulus):
    return [[sum(x*y for x, y in zip(row, column)) % modulus
             for column in zip(*b)] for row in a]


def reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError('Negative control accepted: '+label)


def main():
    from hashlib import sha1
    origins = json.loads((HERE/'ORIGINS.json').read_text())
    for row in origins['files']:
        data = (HERE/row['local']).read_bytes()
        need(sha256(data).hexdigest() == row['sha256'], 'Retained origin SHA-256: '+row['local'])
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],
             'Retained origin Git blob: '+row['local'])
    for name, digest in PINS.items():
        need(sha256((HERE/'retained'/name).read_bytes()).hexdigest() == digest,
             'Immutable source digest: '+name)
    native = json.loads(gzip.decompress((HERE/'retained/BIT-NATIVE-WORD.json.gz').read_bytes()))
    receipt = json.loads((HERE/'retained/EFREE-RESULT.json').read_text())
    caller = json.loads(gzip.decompress((HERE/'retained/EFREE-CALLER.json.gz').read_bytes()))
    frames, projectors, ranks, bases = native['frames'], {}, {}, {}
    frame_determinants, port_determinants = Counter(), Counter()
    for label, frame in frames.items():
        label, rank = int(label), frame['dim']
        basis = transpose(frame['B']+frame['A'])
        inverse, det = invdet(basis)
        need(det == bareiss_determinant(basis) and dyadic_unit(det), 'Raw complete basis index')
        projector = mul(mul(basis, diagonal_projector(8, range(rank))), inverse)
        need(mul(projector, projector) == projector, 'Raw projector idempotence')
        need(projector == transpose(projector), 'Raw frame orthogonal split')
        need(all(dyadic(x) for row in inverse for x in row), 'Raw inverse must be dyadic')
        projectors[label], ranks[label], bases[label] = projector, rank, basis
        frame_determinants[str(det)] += 1
    need(len(frames) == 636, 'Exact raw frame count')

    port_bases = []
    for chart in receipt['source']['charts']:
        basis = [[Q(x) for x in row] for row in chart['basis']]
        inverse, det = invdet(basis)
        need(inverse == [[Q(x) for x in row] for row in chart['inverse']], 'Stored port inverse')
        need(det == Q(chart['determinant']) == bareiss_determinant(basis), 'Stored port determinant')
        need(dyadic_unit(det), 'Port complete basis must have no odd determinant factor')
        head = mul(mul(basis, diagonal_projector(8, [0])), inverse)
        need(head == projectors[chart['input_frame']], 'Actual normalized head projector')
        need(add(eye(8), head, -1) == projectors[chart['output_frame']],
             'Actual normalized complementary body projector')
        port_bases.append(basis)
        port_determinants[str(det)] += 1
    need(len(port_bases) == 111, 'Exact paired-port count')

    # Every one of the eighteen stages is this same 8+7 local chart, placed
    # in its own fresh seven-space. The other 119 coordinates are identity.
    stage_route_cases = 0
    local_swap = permutation((0, *range(8, 15), *range(1, 8)))
    fresh_body = diagonal_projector(15, range(8, 15))
    for basis in port_bases:
        extended = direct_sum(basis, eye(7))
        extended_inverse, _ = invdet(extended)
        route = mul(mul(extended, local_swap), extended_inverse)
        head = mul(mul(extended, diagonal_projector(15, [0])), extended_inverse)
        body = mul(mul(extended, diagonal_projector(15, range(1, 8))), extended_inverse)
        need(mul(route, route) == eye(15), 'Actual stage route involution')
        need(mul(mul(route, head), route) == head, 'Stage route fixes actual head')
        need(mul(mul(route, body), route) == fresh_body, 'Stage route sends exact body to fresh space')
        need(mul(mul(route, fresh_body), route) == body, 'Stage route returns complete body')
        stage_route_cases += 1
    need(caller['stages'] == 18 and caller['roles'] == 38, 'Selected paired caller dimensions')
    target_coordinate_patterns = []
    for entry in caller['diagonal']:
        need(entry['q'] in (0, 1) and len(set(entry['stages'])) == len(entry['stages'])
             and all(1 <= s <= 18 for s in entry['stages']), 'Actual disjoint caller target pattern')
        selected = ((0,) if entry['q'] else ()) + tuple(
            j for s in entry['stages'] for j in range(8+7*(s-1), 8+7*s))
        need(len(set(selected)) == len(selected) and all(0 <= j < 134 for j in selected),
             'Actual 134-axis target is a coordinate split in U_i directsum I_126')
        target_coordinate_patterns.append(selected)
    need(len(target_coordinate_patterns) == 38, 'Selected actual target pattern count')

    moves = [tuple(event[2:]) for event in native['program'] if event[0] == 'MOVE']
    helpers = [(native['start'][j], native['final'][j]) for j in range(222, native['public'])]
    need(len(moves) == 2871 and len(set(moves)) == 2374 and len(helpers) == 437,
         'Selected MOVE/helper population')
    differences, representatives, missing = {}, {}, []
    raw_projector_keys = {key(value) for value in projectors.values()}
    for first, second in sorted(set(moves+helpers)):
        smaller, larger = sorted((first, second), key=lambda f: ranks[f])
        p, q = projectors[larger], projectors[smaller]
        need(mul(p, q) == q == mul(q, p), 'Actual source nested pair')
        difference = add(p, q, -1)
        need(mul(difference, difference) == difference, 'Actual nested difference idempotence')
        need(sum(difference[j][j] for j in range(8)) == ranks[larger]-ranks[smaller],
             'Exact nested-difference rank')
        signature = key(difference)
        differences[signature] = difference
        representatives.setdefault(signature, (smaller, larger))
        if signature not in raw_projector_keys:
            missing.append((smaller, larger))
    need(len(differences) == 513, 'Unique actual nested differences')

    normalized = []
    basis_determinants, clearings, difference_ranks = Counter(), Counter(), Counter()
    naive_failure = None
    max_entry_bits = 0
    for signature, projector in differences.items():
        basis, inverse, rank, scale, det = integral_split_basis(projector)
        need(det == bareiss_determinant(basis), 'Independent completed basis determinant')
        need(dyadic_unit(det) and all(dyadic(x) for row in inverse for x in row),
             'Complete difference basis added an odd denominator')
        need(mul(basis, inverse) == eye(8), 'Completed inverse')
        normalized.append((projector, basis, inverse, rank))
        basis_determinants[str(det)] += 1
        clearings[str(scale)] += 1
        difference_ranks[str(rank)] += 1
        max_entry_bits = max(max_entry_bits, *(abs(Q(x).numerator).bit_length() for row in basis for x in row))
        if naive_failure is None:
            complement = add(eye(8), projector, -1)
            naive = concatenate(columns(projector, pivot_columns(projector)),
                                columns(complement, pivot_columns(complement)))
            _, naive_det = invdet(naive)
            if not dyadic_unit(naive_det):
                naive_failure = {'nested_pair': representatives[signature], 'projector': projector,
                                 'naive_basis': naive, 'naive_determinant': naive_det,
                                 'localized_basis': basis, 'localized_determinant': det}

    # Independent modular reductions test both summands, including prime powers.
    modular_cases = 0
    for projector, basis, inverse, rank in normalized:
        for modulus in (3, 9, 5, 25, 7, 49):
            b, bi, p = (reduce_matrix(matrix, modulus) for matrix in (basis, inverse, projector))
            need(modular_product(b, bi, modulus) == reduce_matrix(eye(8), modulus), 'Local-ring inverse')
            need(modular_product(modular_product(bi, p, modulus), b, modulus)
                 == reduce_matrix(diagonal_projector(8, range(rank)), modulus), 'Both local-ring summands')
            modular_cases += 1

    # The literal compiler adds complete permutations. Extract just that function,
    # without executing or trusting any source test module.
    schedule = HERE/'retained/schedule.py'
    product = HERE/'retained/product.py'
    expected_blobs = {'schedule.py': '0f3b6547ba751878d4e391e2df7d413a4badaed0',
                      'product.py': '9b2ba02afaa4cbaed5b09813dfd1a926c447fac7'}
    for path in (schedule, product):
        data = path.read_bytes()
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == expected_blobs[path.name],
             'Literal compiler source Git blob')
    tree = ast.parse(schedule.read_text())
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'complete_order')
    namespace = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(schedule), 'exec'), namespace)
    complete_order = namespace['complete_order']
    placement_cases = 0
    for n in range(1, 13):
        for active in ((), tuple(range(n)), tuple(range(n-1, -1, -2))):
            order = complete_order(active, n)
            pi = permutation(order)
            need(mul(transpose(pi), pi) == eye(n), 'Actual complete placement inverse')
            placement_cases += 1

    # Carried split: all complement columns are retained. Validate every prefix
    # and a reversed non-prefix selection on actual normalized source jobs.
    split_cases, matcher_cases = 0, 0
    by_rank = {}
    for projector, basis, inverse, rank in normalized:
        by_rank.setdefault(rank, basis)
        for selected in (tuple(range(rank//2)), tuple(range(rank-1, -1, -2))):
            split_basis = split_in_carried_basis(basis, rank, selected)
            split_inverse, split_det = invdet(split_basis)
            child = mul(mul(basis, diagonal_projector(8, selected)), inverse)
            need(mul(mul(split_inverse, child), split_basis) == diagonal_projector(8, range(len(selected))),
                 'Exact child image and full kernel')
            rest = add(projector, child, -1)
            need(mul(rest, child) == mul(child, rest) == [[Q(0)]*8 for _ in range(8)],
                 'Nested split orthogonality')
            need(mul(rest, rest) == rest and add(child, rest) == projector, 'Nested split completion')
            need(dyadic_unit(split_det), 'Coordinate split determinant')
            split_cases += 1
        right = by_rank[rank]
        right_inverse, _ = invdet(right)
        other = mul(mul(right, diagonal_projector(8, range(rank))), right_inverse)
        route = matcher(basis, rank, right, rank)
        route_inverse, route_det = invdet(route)
        need(mul(mul(route, other), route_inverse) == projector, 'Whole-job matcher target')
        need(mul(mul(route, add(eye(8), other, -1)), route_inverse)
             == add(eye(8), projector, -1), 'Whole-job matcher kernel')
        need(dyadic_unit(route_det), 'Matcher determinant')
        matcher_cases += 1

    # A nonorthogonal sector exercises the exact guarded-sum formula; merely
    # controlling the determinant of S is not enough for an arbitrary sum.
    seed = [[Q(2), Q(3)], [Q(3), Q(5)]]
    seed_inv, seed_det = invdet(seed)
    e = mul(mul(seed, diagonal_projector(2, [0])), seed_inv)
    s = [[Q(1), Q(1, 2)], [Q(0), Q(2)]]
    si, sd = invdet(s)
    guard = add(kron(s, e), kron(eye(2), add(eye(2), e, -1)))
    guard_inverse = add(kron(si, e), kron(eye(2), add(eye(2), e, -1)))
    gi, gd = invdet(guard)
    need(gi == guard_inverse and mul(guard, guard_inverse) == eye(4) and gd == sd,
         'Restricted-sector embedding and inverse')
    ds = direct_sum(seed, s)
    _, dsd = invdet(ds)
    tensor = kron(seed, s)
    _, td = invdet(tensor)
    need(dsd == seed_det*sd and td == seed_det**2*sd**2, 'Direct sum and Kronecker determinants')

    # This unimodular split projector has no dyadic-unit entry. Rank-one
    # certificates cannot in general be one prescribed unit minor.
    need(e == [[Q(10), Q(-6)], [Q(15), Q(-9)]], 'Fixed-minor exact fixture')
    need(not any(dyadic_unit(x) for row in e for x in row), 'No unit rank-one minor')
    need(e[0][0] % 5 == 0 and e[0][1] % 5 != 0, 'False q=5 exclusion by a fixed minor')
    need(3*e[0][1]-2*e[1][1] == 0 and e[0][0]+e[1][1] == 1,
         'Unit determinantal ideal despite no unit entry')
    bad_pivot = [[Q(3), Q(1)], [Q(2), Q(1)]]
    _, bad_pivot_det = invdet(bad_pivot)
    need(bad_pivot_det == 1 and bad_pivot[0][0] % 3 == 0 and bad_pivot[1][0] % 3 != 0,
         'Unimodularity does not make a fixed Gaussian pivot a unit')
    negative = [
        reject(lambda: integral_split_basis([[Q(2), Q(0)], [Q(0), Q(0)]]), 'non-idempotent rejected'),
        reject(lambda: split_in_carried_basis(seed, 1, (0, 0)), 'duplicate split coordinate rejected'),
        reject(lambda: matcher(seed, 1, seed, 0), 'rank mismatch rejected'),
        reject(lambda: permutation((0, 0)), 'incomplete placement rejected'),
        reject(lambda: complete_order((0, 0), 2), 'literal duplicate placement rejected'),
    ]
    bad_sector = [[Q(2), Q(0)], [Q(0), Q(0)]]
    bad_guard = add(kron(s, bad_sector), kron(eye(2), add(eye(2), bad_sector, -1)))
    bad_inverse = add(kron(si, bad_sector), kron(eye(2), add(eye(2), bad_sector, -1)))
    need(mul(bad_guard, bad_inverse) != eye(4), 'Guarded-sum failure without idempotence')
    negative.append('non-idempotent guarded sum fails the proposed inverse')

    report = {
        'status': 'PASS_LOCALIZED_ALTERNATE_IMPLEMENTATION',
        'claim': 'Source-specific raw dyadic certificate plus universal carried-basis proof; no full compiler execution',
        'python': platform.python_version(),
        'source_sha256': PINS,
        'authenticated_origin_files': len(origins['files']),
        'raw_frames': len(frames), 'raw_frame_determinants': dict(sorted(frame_determinants.items())),
        'port_pairs': len(port_bases), 'port_determinants': dict(sorted(port_determinants.items())),
        'exact_15_axis_port_stage_routes': stage_route_cases,
        'source_stage_placements_per_port': 18,
        'actual_134_axis_target_patterns': len(target_coordinate_patterns),
        'move_occurrences': len(moves), 'unique_directed_moves': len(set(moves)),
        'helper_endpoints': len(helpers), 'unique_pairs_including_helpers': len(set(moves+helpers)),
        'unique_nested_difference_projectors': len(differences),
        'pairs_whose_difference_is_not_an_existing_raw_frame': len(missing),
        'first_missing_raw_frame_pairs': missing[:12],
        'difference_ranks': dict(sorted(difference_ranks.items())),
        'difference_clearing_denominators': dict(sorted(clearings.items())),
        'localized_basis_determinants': dict(sorted(basis_determinants.items())),
        'maximum_localized_basis_entry_bits': max_entry_bits,
        'basis_catalogue_sha256': sha256(json.dumps(encode(normalized), sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
        'modular_both_summands_cases': modular_cases,
        'literal_complete_placement_cases': placement_cases,
        'actual_source_coordinate_split_cases': split_cases,
        'actual_source_equal_rank_matcher_cases': matcher_cases,
        'naive_fixed_pivot_source_counterexample': naive_failure,
        'fixed_minor_negative_control': {'basis': seed, 'projector': e, 'incorrectly_excluded_prime': 5},
        'fixed_pivot_negative_control': {'basis': bad_pivot, 'determinant': bad_pivot_det,
                                        'failed_fixed_pivot_prime': 3},
        'negative_controls': negative,
        'caller_roles': caller['roles'], 'caller_stages': caller['stages'],
        'limits': ['Alternate image/kernel bases can differ from a predecessor choice.',
                   'No uniform fixed minor or fixed Gaussian pivot factorization is asserted.',
                   'Native semantics, charged routes, finite compiler, stock and analytic recovery remain separately required.',
                   'The growing outer fine-prime assumption is untouched.'],
    }
    output = HERE/'EVIDENCE.json'
    output.write_text(json.dumps(encode(report), indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: report[k] for k in ('status', 'raw_frames', 'port_pairs',
          'unique_nested_difference_projectors', 'modular_both_summands_cases',
          'actual_source_coordinate_split_cases', 'actual_source_equal_rank_matcher_cases')}, sort_keys=True))
    print('naive source counterexample:', None if naive_failure is None else
          encode({k: naive_failure[k] for k in ('nested_pair', 'naive_determinant', 'localized_determinant')}))


if __name__ == '__main__':
    main()
