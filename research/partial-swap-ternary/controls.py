"""Independent finite controls for the PR18 partial-swap transfer.

Exact rational conjugation follows icekylinx's PR18 construction. The
rightmost-pivot lower/lower elimination is independently implemented here,
following the ordering used by our PR14 rational_checks.py. These finite
controls do not prove the general h30 basis or network theorem.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import argparse
import json
import random


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mul(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def sub(a, b):
    return [[x-y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def transpose(a):
    return list(map(list, zip(*a)))


def inverse(a):
    n = len(a)
    rows = [list(map(F, row)) + tail for row, tail in zip(a, eye(n))]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [x/scale for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x-scale*y for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def blocks(a, b, c, d):
    return [x+y for x, y in zip(a, b)] + [x+y for x, y in zip(c, d)]


def partial_swap(p):
    complement = sub(eye(len(p)), p)
    return blocks(complement, p, p, complement)


def nested_difference(old, new):
    """Return the projector for either orientation; reject incomparable edges."""
    if mul(old, new) == old and mul(new, old) == old:
        return sub(new, old)
    if mul(old, new) == new and mul(new, old) == new:
        return sub(old, new)
    raise ValueError('Frame edge is not nested in both multiplication orders')


def lower(a):
    return all(not a[i][j] for i in range(len(a)) for j in range(i+1, len(a)))


def factor(p):
    """Return lower invertible L,R and partial permutation Pi with P=L Pi R."""
    n = len(p)
    a = [list(map(F, row)) for row in p]
    left, right = eye(n), eye(n)
    for i in range(n):
        nz = [j for j, value in enumerate(a[i]) if value]
        if not nz:
            continue
        j = max(nz)
        pivot = a[i][j]
        a[i] = [x/pivot for x in a[i]]
        left[i] = [x/pivot for x in left[i]]
        for k in range(i+1, n):
            scale = a[k][j]
            a[k] = [x-scale*y for x, y in zip(a[k], a[i])]
            left[k] = [x-scale*y for x, y in zip(left[k], left[i])]
        for k in range(j):
            scale = a[i][k]
            for mat in (a, right):
                for row in mat:
                    row[k] -= scale*row[j]
    assert all(x in (0, 1) for row in a for x in row)
    assert all(sum(row) <= 1 for row in a)
    assert all(sum(col) <= 1 for col in zip(*a))
    l, r = inverse(left), inverse(right)
    assert lower(l) and lower(r) and mul(mul(l, a), r) == p
    return l, a, r


def rational_controls():
    rng = random.Random(180017)
    tested = non_symmetric = omitted_k_failures = 0
    dimensions = [2, 3, 4, 5]
    for n in dimensions:
        for repeat in range(3):
            s = eye(n)
            for _ in range(6*n):
                i, j = rng.sample(range(n), 2)
                scale = F(rng.choice((-2, -1, 1, 2)), rng.choice((1, 2, 3)))
                s[i] = [x+scale*y for x, y in zip(s[i], s[j])]
            si = inverse(s)
            projectors = []
            for rank in range(n+1):
                diagonal = [[F(i == j and i < rank) for j in range(n)] for i in range(n)]
                p = mul(mul(s, diagonal), si)
                projectors.append(p)
                non_symmetric += p != transpose(p)
                assert mul(p, p) == p
                dp = partial_swap(p)
                assert mul(dp, dp) == eye(2*n)
                assert mul(partial_swap(sub(eye(n), p)), dp) == partial_swap(eye(n))
                l, pi, r = factor(p)
                c = mul(r, l)
                qx, qy = mul(pi, transpose(pi)), mul(transpose(pi), pi)
                assert mul(mul(pi, c), pi) == pi
                k = sub(mul(qy, c), mul(c, qx))
                zero = [[F(0)]*n for _ in range(n)]
                g0 = blocks(l, zero, zero, inverse(r))
                g = mul(g0, blocks(eye(n), zero, k, eye(n)))
                swap = blocks(sub(eye(n), qx), pi, transpose(pi), sub(eye(n), qy))
                assert lower(g) and lower(inverse(g))
                assert mul(dp, g) == mul(g, swap)
                omitted_k_failures += mul(dp, g0) != mul(g0, swap)
                tested += 1
            for p in projectors:
                for q in projectors:
                    difference = nested_difference(p, q)
                    assert mul(difference, difference) == difference
                    assert mul(partial_swap(q), partial_swap(p)) == partial_swap(difference)
    assert non_symmetric and omitted_k_failures
    # Individually valid projectors need not form an allowed nested edge.
    p = [[F(1), F(0)], [F(0), F(0)]]
    q = [[F(0), F(0)], [F(0), F(1)]]
    try:
        nested_difference(p, q)
    except ValueError:
        rejected = True
    else:
        raise AssertionError('Nonnested edge was accepted')
    return dict(field='Q', dimensions=dimensions, projector_cases=tested,
                nonsymmetric_cases=non_symmetric,
                omitted_K_negative_controls=omitted_k_failures,
                incomparable_edge_rejected=rejected,
                factor_identity='P=L Pi R; D_P G=G Swap(Pi)',
                involutions_nested_edges_and_complement_endpoints=True)


def address_permutation(p, prime=5):
    matrix = partial_swap(p)
    addresses = list(product(range(prime), repeat=len(matrix)))
    index = {address: i for i, address in enumerate(addresses)}
    residues = [[int(x.numerator)*pow(int(x.denominator), -1, prime) % prime
                 for x in row] for row in matrix]
    permutation = [index[tuple(sum(a*b for a, b in zip(row, address)) % prime
                              for row in residues)] for address in addresses]
    assert sorted(permutation) == list(range(len(addresses)))
    return permutation


def dirty_network(relocated=False, omit_cleanup=False, wrong_target=False, extra_outer_shear=False):
    """Full sparse linear map over F3, including all arbitrary dirty inputs.

    Logical roles X,Y,Z0,Z1 have independently labelled initial symbols at
    every F5^4 address. Framing conjugates each elementary scalar gate by a
    common address permutation; every transition is independently checked
    to have nested projector endpoints.
    """
    z = [[F(0), F(0)], [F(0), F(0)]]
    p = [[F(1), F(1)], [F(0), F(0)]]
    i = eye(2)
    cp = sub(i, p)
    matrices = [z, p, i, cp]
    permutations = [address_permutation(a) for a in matrices]
    count = len(permutations[0])
    arrays = [[{role*count+a: 1} for a in range(count)] for role in range(4)]
    frames = [1, 0, 1 if relocated else 0, 1 if relocated else 0]
    events = 0
    transitions = 0
    skipped_cleanup = False

    def reframe(role, target):
        nonlocal transitions
        old = frames[role]
        difference = nested_difference(matrices[old], matrices[target])
        assert mul(partial_swap(matrices[target]), partial_swap(matrices[old])) == partial_swap(difference)
        perm_old, perm_new = permutations[old], permutations[target]
        moved = [None]*count
        for a in range(count):
            moved[perm_new[perm_old[a]]] = arrays[role][a]
        arrays[role] = moved
        frames[role] = target
        transitions += old != target

    def gate(target, source, coefficient):
        nonlocal events
        common = events % 3
        reframe(target, common)
        if source != target:
            reframe(source, common)
        if target == source:
            arrays[target] = [{k: (coefficient*v) % 3 for k, v in row.items()
                               if (coefficient*v) % 3} for row in arrays[target]]
        else:
            for a in range(count):
                row = dict(arrays[target][a])
                for key, value in arrays[source][a].items():
                    result = (row.get(key, 0)+coefficient*value) % 3
                    if result:
                        row[key] = result
                    else:
                        row.pop(key, None)
                arrays[target][a] = row
        events += 1

    def wrapper(source, target, sign):
        nonlocal skipped_cleanup
        # L,-J,L^-1,V,L,J,L^-1,-V with JLV=1 over F3.
        gate(2, 3, 1)
        gate(target, 2, -sign)
        gate(target, 3, -2*sign)
        gate(2, 3, -1)
        gate(2, source, 1)
        gate(3, source, 1)
        gate(2, 3, 1)
        gate(target, 2, sign)
        gate(target, 3, 2*sign)
        gate(2, 3, -1)
        if omit_cleanup and not skipped_cleanup:
            skipped_cleanup = True
        else:
            gate(2, source, -1)
            gate(3, source, -1)

    wrapper(0, 1, 1)
    wrapper(1, 0, -1)
    wrapper(0, 1, 1)
    gate(0, 0, -1)
    end = [2, 3, 3 if relocated else 2, 3 if relocated else 2]
    if wrong_target:
        end[1] = 2
    for role, target in enumerate(end):
        # Complement may be incomparable with P: take a valid nested route
        # through I when necessary, charging/checking both transitions.
        try:
            nested_difference(matrices[frames[role]], matrices[target])
        except ValueError:
            reframe(role, 2)
        reframe(role, target)
    expected = [[None]*count for _ in range(4)]
    for role, origin in enumerate((1, 0, 2, 3)):
        for a in range(count):
            expected[role][permutations[2][a]] = {origin*count+a: 1}
    if extra_outer_shear:
        # A legacy post-wrapper shear acts on the already completed physical
        # endpoint map; it must not be silently included a second time.
        for a in range(count):
            for key, value in arrays[0][a].items():
                updated = (arrays[1][a].get(key, 0)+value) % 3
                if updated:
                    arrays[1][a][key] = updated
                else:
                    arrays[1][a].pop(key, None)
    matches = arrays == expected
    if not omit_cleanup and not wrong_target and not extra_outer_shear:
        assert matches, 'Framed dirty-scratch network did not match full endpoint map'
    else:
        assert not matches, 'Negative control unexpectedly passed'
    return dict(scalar_field=3, address_field=5, address_dimension=4,
                addresses_per_role=count, roles=4, independent_input_symbols=4*count,
                elementary_scalar_gates=events, nontrivial_frame_transitions=transitions,
                relocated_auxiliary_endpoints=relocated,
                complete_linear_map_matches=matches,
                negative_control=('omitted_cleanup' if omit_cleanup else
                                  'wrong_target_frame' if wrong_target else
                                  'extra_outer_shear' if extra_outer_shear else None),
                expected='Swap X/Y roles and exchange both address banks on every role')


def run():
    return dict(rational=rational_controls(),
                dirty_scratch=[dirty_network(), dirty_network(relocated=True)],
                negative_network_controls=[dirty_network(omit_cleanup=True),
                                           dirty_network(wrong_target=True),
                                           dirty_network(extra_outer_shear=True)],
                scope='Finite exact controls only; not a proof of the general h30 theorem')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, indent=2)+'\n'
    if args.output:
        destination = args.output.resolve()
        root = Path('/Volumes/SP AI 01_16/CodexWorkspaces').resolve()
        if not destination.is_relative_to(root):
            raise ValueError('Control output must be under the SSD workspace')
        args.output.write_text(encoded)
    print(encoded, end='')
