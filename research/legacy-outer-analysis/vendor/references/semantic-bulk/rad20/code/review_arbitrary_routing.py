#!/usr/bin/env python3
"""Independent complete coordinate-route address operators.

Reimplements the mathematical controlled rotations, genuine packed modular
digit additions, inverse/current-control repair, physical field placements,
two involutions and all three matching shears. No producer is imported.
Large-word address probes are not exhaustive large payload arrays or tape
timings. Tiny cases enumerate complete payload-address permutations.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import random
import resource
import time


def bit(word, n, position):
    return (word >> (n-1-position)) & 1


def swap_positions(word, n, names, left, right, width, stats):
    assert left >= 0 and right >= 0 and width >= 1
    assert left+width <= n and right+width <= n
    if left == right:
        return word
    assert left+width <= right or right+width <= left
    for j in range(width):
        a, b = left+j, right+j
        delta = bit(word, n, a) ^ bit(word, n, b)
        word ^= delta*((1 << (n-1-a)) | (1 << (n-1-b)))
        names[a], names[b] = names[b], names[a]
    stats['completed_original_field_interchanges'] += 1
    return word


def elementary(word, n, names, source, target, stats):
    """Actual placement, fixed four-quarter CNOT, inverse placement."""
    assert source != target
    original_names = names[:]
    placements = []
    pos = names.index(source)
    if pos != 0:
        word = swap_positions(word, n, names, pos, 0, 1, stats)
        placements.append((pos, 0))
    pos = names.index(target)
    if pos != 1:
        word = swap_positions(word, n, names, pos, 1, 1, stats)
        placements.append((pos, 1))
    assert names[:2] == [source, target]
    # Only quarters 10 and 11 are exchanged. No arbitrary offset function.
    if bit(word, n, 0):
        word ^= 1 << (n-2)
    for left, right in reversed(placements):
        word = swap_positions(word, n, names, left, right, 1, stats)
    assert names == original_names
    stats['elementary_four_quarter_CNOTs'] += 1
    return word


def compact_program():
    F = [('rotation', 2, 'even'), ('swap', 1, 3),
         ('rotation', 3, 'parity'), ('swap', 1, 3),
         ('rotation', 2, 'odd'), ('swap', 1, 3),
         ('rotation', 3, 'unparity'), ('swap', 1, 3)]
    return F+[('swap', 0, 3), ('rotation', 3, 'sources'), ('swap', 0, 3)]+F+[
        ('swap', 0, 3), ('rotation', 3, 'unsources'), ('swap', 0, 3)]


def run_compact(q0, H, Y, G, K, rho, source_positions, inverse=False):
    assert H >= 1 and Y >= 1 and K >= G+3
    B = 1 << G
    targets = {rho+i*K for i in source_positions}
    assert all(0 <= j and j+K <= Y for j in targets)
    assert max(source_positions)*G+G <= H
    assert len(set(source_positions.values())) == len(source_positions)
    assert not targets & set(source_positions.values())
    assert all(0 <= s < Y for s in source_positions.values())
    program = compact_program()
    assert sum(op[0] == 'swap' for op in program) == 12
    assert sum(op[0] == 'rotation' for op in program) == 10
    q = list(q0)
    masks = [(1 << H)-1, (1 << H)-1, (1 << Y)-1, (1 << H)-1]

    def offset(kind):
        packed = 0
        for i, source in source_positions.items():
            z = (q[0] >> (i*G)) & 1
            t = (q[1] >> (i*G)) & (B-1)
            j = rho+i*K
            a = (q[2] >> j) & 1
            if kind == 'even':
                packed += 2*z*t*(1 << j)
            elif kind == 'odd':
                packed += z*(1-2*t)*(1 << j)
            elif kind == 'parity':
                packed += a*(1 << (i*G))
            elif kind == 'unparity':
                packed -= (a ^ z)*(1 << (i*G))
            elif kind == 'sources':
                packed += ((q[2] >> source) & 1)*(1 << (i*G))
            elif kind == 'unsources':
                packed -= ((q[2] >> source) & 1)*(1 << (i*G))
            else:
                raise AssertionError(kind)
        return packed

    for op in reversed(program) if inverse else program:
        if op[0] == 'swap':
            q[op[1]], q[op[2]] = q[op[2]], q[op[1]]
        else:
            index, kind = op[1:]
            assert (index == 2 and kind in ('even', 'odd')) or index == 3
            q[index] = (q[index]+(-1 if inverse else 1)*offset(kind)) & masks[index]
    return tuple(q)


def bad(q, G, K, rho, sources):
    B = 1 << G
    for i in sources:
        if ((q[0] >> (i*G)) & (B-1)) == B-1:
            return True
        if ((q[1] >> (i*G)) & (B-1)) == B-1:
            return True
        guard = ((q[2] >> (rho+i*K)) & ((1 << K)-1)) >> 1
        if guard < 2*B or guard >= (1 << (K-1))-2*B:
            return True
    return False


def ideal_group(q, K, rho, sources):
    toggle = sum(((q[2] >> source) & 1)*(1 << (rho+i*K))
                 for i, source in sources.items())
    return q[0], q[1], q[2] ^ toggle, q[3]


def compact_group(word, n, prefix_length, H, G, K, rho, sources, stats):
    Y = prefix_length-3*H
    tail_length = n-prefix_length
    prefix = word >> tail_length
    m = (1 << H)-1
    q0 = (prefix >> (2*H+Y), (prefix >> (H+Y)) & m,
          (prefix >> H) & ((1 << Y)-1), prefix & m)
    actual = run_compact(q0, H, Y, G, K, rho, sources)
    assert run_compact(actual, H, Y, G, K, rho, sources, True) == q0
    inverse = run_compact(q0, H, Y, G, K, rho, sources, True)
    assert run_compact(inverse, H, Y, G, K, rho, sources) == q0
    expected = ideal_group(q0, K, rho, sources)
    initial_bad = bad(q0, G, K, rho, sources)
    assert initial_bad == bad(actual, G, K, rho, sources)
    assert initial_bad == bad(expected, G, K, rho, sources)
    if initial_bad:
        # Evaluate the exact exceptional output-address destination T S^-1.
        actual = ideal_group(run_compact(actual, H, Y, G, K, rho, sources, True),
                             K, rho, sources)
        stats['bad_address_corrections'] += 1
    else:
        stats['good_compact_invocations'] += 1
    assert actual == expected
    stats['compact_invocations'] += 1
    stats['actual_inverse_composites'] += 2
    if any(q0[j] for j in (0, 1, 3)):
        stats['nonzero_dirty_field_invocations'] += 1
    targets = {rho+i*K for i in sources}
    stats['sources_at_inactive_selected_positions'] += sum(
        source % K == rho and source not in targets for source in sources.values())
    stats['sources_inside_active_guard_segments'] += sum(
        any(target < source < target+K for target in targets)
        for source in sources.values())
    u, t, y, back = actual
    prefix = (u << (2*H+Y)) | (t << (H+Y)) | (y << H) | back
    return (prefix << tail_length) | (word & ((1 << tail_length)-1))


def shear(word, n, names, prefix_length, H, G, edges, reverse, stats):
    K = 64*G
    Y = prefix_length-3*H
    positions = {name:i for i, name in enumerate(names)}
    groups, residuals = {}, []
    for a, b in edges:
        source, target = (b, a) if reverse else (a, b)
        s = prefix_length-H-1-positions[source]
        t = prefix_length-H-1-positions[target]
        assert 0 <= s < Y and 0 <= t < Y
        if t+K > Y:
            residuals.append((source, target))
        else:
            rho, index = t % K, t//K
            groups.setdefault(rho, {})[index] = s
    for rho, sources in sorted(groups.items()):
        word = compact_group(word, n, prefix_length, H, G, K, rho, sources, stats)
    assert len(residuals) <= K
    for source, target in residuals:
        word = elementary(word, n, names, source, target, stats)
    return word


def classify(edges, sets):
    groups = [[], [], []]
    assert all(not sets[i] & sets[j] for i in range(3) for j in range(i))
    for edge in edges:
        pair = set(edge)
        k = 0 if not pair & sets[0] else 1 if not pair & sets[1] else 2
        assert not pair & sets[k]
        groups[k].append(edge)
    assert sum(map(len, groups)) == len(edges)
    return groups


def inner_matching(word, n, names, prefix_length, G, edges, stats):
    K = 64*G
    if prefix_length < K:
        for reverse in (False, True, False):
            for a, b in edges:
                source, target = (b, a) if reverse else (a, b)
                word = elementary(word, n, names, source, target, stats)
        stats['short_prefix_matching_fallbacks'] += 1
        return word
    H = ((prefix_length+K-1)//K)*G
    assert 9*H <= prefix_length
    sets = [set(names[2*k*H:(2*k+2)*H]+names[prefix_length-(k+1)*H:prefix_length-k*H])
            for k in range(3)]
    groups = classify(edges, sets)
    original_names = names[:]
    for k, group in enumerate(groups):
        if not group:
            continue
        placements = [(2*k*H, 0), ((2*k+1)*H, H),
                      (prefix_length-(k+1)*H, prefix_length-H)]
        for left, right in placements:
            word = swap_positions(word, n, names, left, right, H, stats)
        assert set(names[:2*H]+names[prefix_length-H:prefix_length]) == sets[k]
        for reverse in (False, True, False):
            word = shear(word, n, names, prefix_length, H, G, group, reverse, stats)
        for left, right in reversed(placements):
            word = swap_positions(word, n, names, left, right, H, stats)
        assert names == original_names
        stats['complete_scratch_reservoir_classes'] += 1
    return word


def matching(word, n, mate, G, ell, stats):
    assert all(mate[mate[i]] == i for i in range(n))
    edges = [(i, mate[i]) for i in range(n) if i < mate[i]]
    names = list(range(n))
    if ell is None:
        return inner_matching(word, n, names, n, G, edges, stats)
    if n <= 3*ell:
        for reverse in (False, True, False):
            for a, b in edges:
                word = elementary(word, n, names, b if reverse else a,
                                  a if reverse else b, stats)
        stats['small_word_matching_fallbacks'] += 1
        return word
    fields = [(0, ell), (ell, 2*ell), (n-ell, n)]
    sets = [set(range(a, b)) for a, b in fields]
    groups = classify(edges, sets)
    for k, group in enumerate(groups):
        if not group:
            continue
        left, _ = fields[k]
        word = swap_positions(word, n, names, left, n-ell, ell, stats)
        assert set(names[-ell:]) == sets[k]
        spectator = word & ((1 << ell)-1)
        word = inner_matching(word, n, names, n-ell, G, group, stats)
        assert word & ((1 << ell)-1) == spectator
        word = swap_positions(word, n, names, left, n-ell, ell, stats)
        assert names == list(range(n))
        stats['complete_spectator_classes'] += 1
    return word


def reflections(perm):
    n = len(perm)
    assert sorted(perm) == list(range(n))
    visited, A, B = set(), list(range(n)), list(range(n))
    for start in range(n):
        if start in visited:
            continue
        cycle, current = [], start
        while current not in visited:
            cycle.append(current); visited.add(current); current = perm[current]
        size = len(cycle)
        for j, point in enumerate(cycle):
            A[point] = cycle[(size-j) % size]
            B[point] = cycle[(size+1-j) % size]
    assert all(A[A[i]] == B[B[i]] == i for i in range(n))
    assert all(B[A[i]] == perm[i] for i in range(n))
    return A, B


def route(word, perm, G, ell, stats):
    A, B = reflections(perm)
    word = matching(word, len(perm), A, G, ell, stats)
    return matching(word, len(perm), B, G, ell, stats)


def closed_expected(word, perm):
    n = len(perm)
    return sum(bit(word, n, source)*(1 << (n-1-destination))
               for source, destination in enumerate(perm))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert not args.output.exists()
    start = time.monotonic()
    stats = {key:0 for key in ('completed_original_field_interchanges',
        'elementary_four_quarter_CNOTs', 'bad_address_corrections',
        'good_compact_invocations', 'compact_invocations', 'actual_inverse_composites',
        'nonzero_dirty_field_invocations', 'sources_at_inactive_selected_positions',
        'sources_inside_active_guard_segments', 'short_prefix_matching_fallbacks',
        'small_word_matching_fallbacks', 'complete_scratch_reservoir_classes',
        'complete_spectator_classes')}
    complete_addresses = complete_permutations = 0
    for n in range(2, 6):
        for perm in permutations(range(n)):
            images = []
            for word in range(1 << n):
                result = route(word, perm, 1, None, stats)
                assert result == closed_expected(word, perm)
                images.append(result)
                complete_addresses += 1
            assert sorted(images) == list(range(1 << n))
            complete_permutations += 1
    rng = random.Random(211)
    cases = []
    for n, G, ell in ((9,1,3), (48,1,16), (49,1,16), (96,1,16),
                      (99,1,32), (128,1,40), (256,2,32), (512,2,80),
                      (192,1,None)):
        ps = [list(range(n)), list(range(n-1,-1,-1)),
              list(range(1,n))+[0]]
        for _ in range(2):
            perm = list(range(n)); rng.shuffle(perm); ps.append(perm)
        words = [0, (1 << n)-1, 1, 1 << (n-1), 1 << (n//2),
                 sum(1 << i for i in range(0,n,2)),
                 sum(1 << i for i in range(1,n,2))]
        words += [rng.randrange(1 << n) for _ in range(3)]
        count = 0
        for perm in ps:
            for word in words:
                actual = route(word, perm, G, ell, stats)
                assert actual == closed_expected(word, perm)
                count += 1
        cases.append(dict(n=n, G=G, K=64*G, ell=ell,
            independent_permutations=len(ps), complete_address_route_probes=count))
    assert stats['good_compact_invocations'] > 0
    assert stats['bad_address_corrections'] > 0
    assert stats['nonzero_dirty_field_invocations'] > 0
    assert stats['sources_inside_active_guard_segments'] > 0
    assert stats['sources_at_inactive_selected_positions'] > 0
    result = dict(status='PASS independent complete named-slot routing address operators',
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        seed=211, exhaustive_small_permutations=complete_permutations,
        exhaustive_small_payload_addresses=complete_addresses, cases=cases,
        statistics=stats, wall_seconds=time.monotonic()-start,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        scope='Complete tiny payload-address permutations and larger exact address probes through all spectator/reservoir placement, three-shear and two-involution stages, actual packed rotations/inverses/current-address repair. Large-word streams, radix sorting and asymptotic tape costs remain separate written proof controls; no producer import.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS whole routes', complete_addresses, 'tiny complete addresses;',
          sum(row['complete_address_route_probes'] for row in cases),
          'large/boundary probes;', stats)


if __name__ == '__main__':
    main()
