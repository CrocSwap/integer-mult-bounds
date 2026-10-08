#!/usr/bin/env python3
"""Exact controls for masked arbitrary-source compact XOR and routing.

This is an address model, not a fixed-tape multiplication implementation.
The tape transfer and all-size assumptions are stated in its companion report.
No upstream compact implementation is imported. Source positions may lie
inside guard fields and at inactive selected positions, but never in the
global active target set of the simultaneous shear.
"""

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import random
import time


def specification(width, K, G, sources, unmasked=False, rho=0):
    """sources maps low spaced target-slot indices to source-bit positions."""
    assert width >= K >= G + 3 and G >= 1
    assert 0 <= rho < K
    slots = (width - rho) // K
    assert slots >= 1 and sources
    targets = {rho + i * K for i in sources}
    assert all(0 <= i < slots for i in sources)
    assert all(0 <= j < width and j not in targets for j in sources.values())
    assert len(set(sources.values())) == len(sources)
    identity_slots = set(range(slots)) if unmasked else set(sources)
    widths = {'u': slots * G, 't': slots * G, 'y': width, 'b': slots * G}
    order = ('u', 't', 'y', 'b')
    position = {name: i for i, name in enumerate(order)}
    ops = []

    def rotate(target, kind, sign=1):
        controls = {'first': ('u', 't'), 'second': ('u', 't'),
                    'load_t': ('y',), 'unload_t': ('y', 'u'),
                    'source': ('y',)}[kind]
        assert all(position[c] < position[target] for c in controls)
        ops.append(('rotate', target, kind, sign))

    def identity():
        rotate('y', 'first')
        ops.append(('swap', 't', 'b', 0))
        rotate('b', 'load_t')
        ops.append(('swap', 't', 'b', 0))
        rotate('y', 'second')
        ops.append(('swap', 't', 'b', 0))
        rotate('b', 'unload_t', -1)
        ops.append(('swap', 't', 'b', 0))

    identity()
    ops.append(('swap', 'u', 'b', 0))
    rotate('b', 'source')
    ops.append(('swap', 'u', 'b', 0))
    identity()
    ops.append(('swap', 'u', 'b', 0))
    rotate('b', 'source', -1)
    ops.append(('swap', 'u', 'b', 0))
    assert sum(op[0] == 'rotate' for op in ops) == 10
    assert sum(op[0] == 'swap' for op in ops) == 12
    return widths, order, ops, identity_slots


def execute(state, width, K, G, sources, inverse=False, unmasked=False, rho=0):
    widths, order, ops, identity_slots = specification(width, K, G, sources, unmasked, rho)
    q = dict(zip(order, state))
    assert all(0 <= q[n] < 1 << w for n, w in widths.items())
    B = 1 << G

    def digit(field, i):
        return (q[field] >> (i * G)) & (B - 1)

    def offset(kind):
        if kind in ('first', 'second'):
            return sum((digit('u', i) & 1) *
                       (2 * digit('t', i) if kind == 'first' else 1 - 2 * digit('t', i)) *
                       (1 << (rho + i * K)) for i in identity_slots)
        if kind == 'source':
            return sum(((q['y'] >> s) & 1) << (i * G) for i, s in sources.items())
        return sum((((q['y'] >> (rho + i * K)) & 1) ^
                    ((digit('u', i) & 1) if kind == 'unload_t' else 0)) << (i * G)
                   for i in identity_slots)

    for action, target, other, sign in reversed(ops) if inverse else ops:
        if action == 'swap':
            q[target], q[other] = q[other], q[target]
        else:
            q[target] = (q[target] + (-sign if inverse else sign) * offset(other)) % (1 << widths[target])
    return tuple(q[name] for name in order)


def ideal(state, K, sources, rho=0):
    u, t, y, b = state
    return u, t, y ^ sum(((y >> s) & 1) << (rho + i * K) for i, s in sources.items()), b


def bad(state, K, G, sources, rho=0):
    u, t, y, b = state
    B = 1 << G
    for i in sources:
        if ((u >> (i * G)) & (B - 1)) == B - 1:
            return True
        if ((t >> (i * G)) & (B - 1)) == B - 1:
            return True
        guard = ((y >> (rho + i * K)) & ((1 << K) - 1)) >> 1
        if not 2 * B <= guard < (1 << (K - 1)) - 2 * B:
            return True
    return False


def key(state, widths, order):
    z = 0
    for name, v in zip(order, state):
        z = (z << widths[name]) | v
    return z


def exhaustive():
    rows = []
    for K, source in product((5, 6), range(1, 5)):
        G, width, sources = 1, K, {0: source}
        widths, order, _, _ = specification(width, K, G, sources)
        states = list(product(*(range(1 << widths[name]) for name in order)))
        actual = [None] * len(states)
        expected = [None] * len(states)
        good = 0
        for identity, state in enumerate(states):
            image = execute(state, width, K, G, sources)
            assert execute(image, width, K, G, sources, True) == state
            assert execute(execute(state, width, K, G, sources, True), width, K, G, sources) == state
            target = ideal(state, K, sources)
            assert bad(target, K, G, sources) == bad(state, K, G, sources)
            assert bad(image, K, G, sources) == bad(state, K, G, sources)
            if not bad(state, K, G, sources):
                assert image == target
                good += 1
            assert actual[key(image, widths, order)] is None
            actual[key(image, widths, order)] = identity
            expected[key(target, widths, order)] = identity
        holes = [key(s, widths, order) for s in states if bad(s, K, G, sources)]
        extracted = []
        for k in holes:
            state = states[k]
            destination = ideal(execute(state, width, K, G, sources, True), K, sources)
            extracted.append((key(destination, widths, order), actual[k]))
        for bit in range(sum(widths.values())):
            extracted = [r for r in extracted if not (r[0] >> bit) & 1] + [
                r for r in extracted if (r[0] >> bit) & 1]
        assert [r[0] for r in extracted] == holes
        for k, (_, payload) in zip(holes, extracted):
            actual[k] = payload
        assert actual == expected
        bound = min(Fraction(1), Fraction(2, 1 << G) + Fraction(8 * (1 << G), 1 << K))
        assert Fraction(len(holes), len(states)) <= bound
        rows.append({'K': K, 'source_inside_guard': source, 'addresses': len(states),
                     'good': good, 'bad': len(holes), 'stable_repair_exact': True})
    return rows


def adversarial(seed=109):
    rng = random.Random(seed)
    checked = good = repaired = 0
    families = 0
    for slots, G, gap, rho_choice in product((2, 3, 5), (1, 2, 3), (4, 5, 8), (0, 1, 2)):
        K = G + gap
        rho = (0, 1, K - 1)[rho_choice]
        width, B = slots * K + rho, 1 << G
        # Inactive selected positions are deliberately allowed as sources.
        for active in ({0}, set(range(0, slots, 2)), set(range(slots))):
            available = [j for j in range(width) if j not in {rho + i * K for i in active}]
            rng.shuffle(available)
            sources = dict(zip(sorted(active), available))
            widths, order, _, _ = specification(width, K, G, sources, rho=rho)
            low, high = 2 * B, (1 << (K - 1)) - 2 * B
            families += 1
            for ut, tt, guard, parity in product((0, B - 2, B - 1), (0, B - 2, B - 1),
                                               (low - 1, low, high - 1, high), (0, 1)):
                q = {name: rng.randrange(1 << w) for name, w in widths.items()}
                for i in active:
                    mask = (B - 1) << (i * G)
                    q['u'] = (q['u'] & ~mask) | (ut << (i * G))
                    q['t'] = (q['t'] & ~mask) | (tt << (i * G))
                    mask = ((1 << K) - 1) << (rho + i * K)
                    q['y'] = (q['y'] & ~mask) | ((2 * guard + parity) << (rho + i * K))
                state = tuple(q[n] for n in order)
                image = execute(state, width, K, G, sources, rho=rho)
                assert execute(image, width, K, G, sources, True, rho=rho) == state
                assert bad(image, K, G, sources, rho) == bad(state, K, G, sources, rho)
                if not bad(state, K, G, sources, rho):
                    assert image == ideal(state, K, sources, rho)
                    good += 1
                assert ideal(execute(image, width, K, G, sources, True, rho=rho), K, sources, rho) == ideal(state, K, sources, rho)
                repaired += image != ideal(state, K, sources, rho)
                checked += 1
    # This mutation omits masks and must fail when a source is an inactive target.
    state, K, G, sources = (2, 0, 8 | (8 << 5), 0), 5, 1, {0: 5}
    wrong = execute(state, 10, K, G, sources, unmasked=True)
    assert not bad(state, K, G, sources)
    assert wrong != ideal(state, K, sources)
    assert execute(state, 10, K, G, sources) == ideal(state, K, sources)
    return {'families': families, 'adversarial_addresses': checked, 'good': good,
            'nontrivial_repairs': repaired, 'seed': seed,
            'unmasked_counterexample': {'input': state, 'sources': sources,
                'wrong_image': wrong, 'ideal_image': ideal(state, K, sources)}}


def involutions(perm):
    """Return two matchings A,B with B(A(i)) == perm[i]."""
    n = len(perm)
    assert sorted(perm) == list(range(n))
    a, b = list(range(n)), list(range(n))
    seen = set()
    for start in range(n):
        if start in seen:
            continue
        cycle, i = [], start
        while i not in seen:
            seen.add(i)
            cycle.append(i)
            i = perm[i]
        z = len(cycle)
        for j, vertex in enumerate(cycle):
            a[vertex] = cycle[-j % z]
            b[vertex] = cycle[(1 - j) % z]
    assert all(a[a[i]] == b[b[i]] == i and b[a[i]] == perm[i] for i in range(n))
    return a, b


def partition(matching, reservoirs):
    r0, r1, r2 = map(set, reservoirs)
    assert not (r0 & r1 or r0 & r2 or r1 & r2)
    groups = [[], [], []]
    for i, j in enumerate(matching):
        if i >= j:
            continue
        edge = {i, j}
        k = 0 if not edge & r0 else (1 if not edge & r1 else 2)
        assert not edge & (r0, r1, r2)[k]
        groups[k].append((i, j))
    assert sum(map(len, groups)) == sum(i < j for i, j in enumerate(matching))
    return groups


def swap_fields(names, left, right):
    """Original disjoint equal-width chunk interchange on named slots."""
    assert len(left) == len(right) and not set(left) & set(right)
    assert left == list(range(left[0], left[0] + len(left)))
    assert right == list(range(right[0], right[0] + len(right)))
    out = list(names)
    for i, j in zip(left, right):
        out[i], out[j] = names[j], names[i]
    return out


def layouts(seed=211):
    rng = random.Random(seed)
    permutations_checked = partitions = layouts_checked = 0
    for n in range(2, 8):
        for p in permutations(range(n)):
            involutions(p)
            permutations_checked += 1
    for n, H in product((9, 10, 17, 36, 71), (1, 2, 3, 4)):
        if n < 9 * H:
            continue
        fields = [list(range(2 * k * H, (2 * k + 1) * H)) +
                  list(range((2 * k + 1) * H, (2 * k + 2) * H)) +
                  list(range(n - (k + 1) * H, n - k * H)) for k in range(3)]
        assert len(set(sum(fields, []))) == 9 * H
        for k in range(3):
            names = list(range(n))
            swaps = []
            for l, rr in ((list(range(2 * k * H, (2 * k + 1) * H)), list(range(H))),
                          (list(range((2 * k + 1) * H, (2 * k + 2) * H)), list(range(H, 2 * H))),
                          (list(range(n - (k + 1) * H, n - k * H)), list(range(n - H, n)))):
                if l != rr:
                    names = swap_fields(names, l, rr)
                    swaps.append((l, rr))
            assert set(names[:2 * H] + names[-H:]) == set(fields[k])
            for l, rr in reversed(swaps):
                names = swap_fields(names, l, rr)
            assert names == list(range(n))
            layouts_checked += 1
        for _ in range(31):
            perm = list(range(n)); rng.shuffle(perm)
            for match in involutions(perm):
                partition(match, fields)
                partitions += 1
    spectator_layouts = 0
    for ell in range(1, 18):
        for n in range(3 * ell + 1, 5 * ell + 1):
            ss = [list(range(ell)), list(range(ell, 2 * ell)), list(range(n - ell, n))]
            for k in range(3):
                names = list(range(n))
                if k != 2:
                    names = swap_fields(names, ss[k], ss[2])
                assert set(names[-ell:]) == set(ss[k])
                if k != 2:
                    names = swap_fields(names, ss[k], ss[2])
                assert names == list(range(n))
                spectator_layouts += 1
            perm = list(range(n)); rng.shuffle(perm)
            for match in involutions(perm):
                partition(match, ss)
                partitions += 1
    return {'exhaustive_permutation_decompositions': permutations_checked,
            'matching_partitions': partitions, 'scratch_layouts': layouts_checked,
            'spectator_layouts': spectator_layouts, 'seed': seed}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists(), 'Use a fresh output path'
    started = time.monotonic()
    result = {'status': 'PASS finite address/routing controls; transfer separate',
              'source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'exhaustive': exhaustive(), 'adversarial': adversarial(), 'layouts': layouts()}
    result['elapsed_seconds'] = time.monotonic() - started
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'elapsed_seconds': result['elapsed_seconds'],
                      'source_sha256': result['source_sha256']}), flush=True)


if __name__ == '__main__':
    main()
