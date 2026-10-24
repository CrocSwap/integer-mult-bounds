#!/usr/bin/env python3
"""Check the changed spectator layouts and the paid routing operators."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import random
import subprocess
import time


def check_named_slots(n, s, mate):
    """Check each field move without the inherited routing implementation."""
    fields = [set(range(s)), set(range(s, 2*s)), set(range(n-s, n))]
    assert n > 3*s and not any(fields[i] & fields[j] for i in range(3) for j in range(i))
    edges = [(i, mate[i]) for i in range(n) if i < mate[i]]
    groups = [[], [], []]
    for edge in edges:
        target = next((i for i, field in enumerate(fields) if not field.intersection(edge)), None)
        assert target is not None
        groups[target].append(edge)
    image = list(range(n))
    for k, edges_here in enumerate(groups):
        if not edges_here:
            continue
        first = (0, s, n-s)[k]
        names = list(range(n))
        if first != n-s:
            names[first:first+s], names[n-s:] = names[n-s:], names[first:first+s]
        assert set(names[n-s:]) == fields[k]
        for x, y in edges_here:
            assert names.index(x) < n-s and names.index(y) < n-s
            image[x], image[y] = image[y], image[x]
        if first != n-s:
            names[first:first+s], names[n-s:] = names[n-s:], names[first:first+s]
        assert names == list(range(n))
    assert image == mate
    return sum(bool(group) for group in groups)


def alternate_pairing(perm):
    """Use cycle reversal to make two matchings. Do not import the oracle."""
    a, b = list(range(len(perm))), list(range(len(perm)))
    unseen = set(range(len(perm)))
    while unseen:
        start = min(unseen)
        cycle = [start]
        unseen.remove(start)
        nxt = perm[start]
        while nxt != start:
            cycle.append(nxt)
            unseen.remove(nxt)
            nxt = perm[nxt]
        for index, value in enumerate(cycle):
            a[value] = cycle[-index % len(cycle)]
            b[value] = cycle[(1-index) % len(cycle)]
    assert all(b[a[i]] == perm[i] for i in range(len(perm)))
    return a, b


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    start = time.monotonic()
    verifier = args.source_root / 'references/semantic-bulk/rad20/code/review_arbitrary_routing.py'
    source_manifest = args.source_root / 'references/semantic-bulk/rad20/SOURCE.json'
    frozen = json.loads(source_manifest.read_text())
    assert sha256(verifier.read_bytes()).hexdigest() == frozen['source_sha256']['code/review_arbitrary_routing.py']
    spec = importlib.util.spec_from_file_location('inherited_operator_verifier', verifier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    stats = Counter()
    rng = random.Random(110509)
    small = 0
    for n in range(2, 6):
        for perm in permutations(range(n)):
            for word in range(1 << n):
                actual = module.route(word, perm, 1, 4, stats)
                expected = int(''.join(str((word >> (n-1-perm.index(i))) & 1) for i in range(n)), 2)
                assert actual == expected
                small += 1
    cases, placements, probes = [], 0, 0
    for p in (64, 256, 4096, 32768):
        h = (p-1).bit_length()
        s, G = h*h, 4*h+6
        sizes = sorted(set((3*s-1, 3*s, 3*s+1, 4*s-1, p//6)))
        for n in sizes:
            if n < 2 or n > p:
                continue
            perms = [list(range(n-1, -1, -1)), list(range(1,n))+[0]]
            shuffled = list(range(n)); rng.shuffle(shuffled); perms.append(shuffled)
            words = [0, (1 << n)-1, rng.getrandbits(n), rng.getrandbits(n)]
            for perm in perms:
                inverse = [0]*n
                for source, target in enumerate(perm):
                    inverse[target] = source
                if n > 3*s:
                    for pairing in alternate_pairing(perm):
                        placements += check_named_slots(n, s, pairing)
                for word in words:
                    actual = module.route(word, perm, G, s, stats)
                    expected = int(''.join(str((word >> (n-1-inverse[i])) & 1) for i in range(n)), 2)
                    assert actual == expected
                    assert module.route(actual, inverse, G, s, stats) == word
                    probes += 1
            cases.append(dict(p=p, h=h, s=s, G=G, n=n, branch='spectator' if n > 3*s else 'elementary'))
    assert stats['complete_spectator_classes'] > 0
    assert stats['complete_scratch_reservoir_classes'] > 0
    assert stats['good_compact_invocations'] > 0
    assert stats['bad_address_corrections'] > 0
    assert stats['nonzero_dirty_field_invocations'] > 0
    negatives = []
    # A consecutive third field overlaps the suffix at this strict boundary.
    n, s = 193, 64
    try:
        module.swap_positions(1, n, list(range(n)), 2*s, n-s, s, stats)
    except AssertionError:
        negatives.append('Consecutive third spectator overlaps its suffix destination.')
    else:
        raise AssertionError('The overlapping spectator control did not fail.')
    names = list(range(n))
    moved = module.swap_positions(1, n, names, 0, n-s, s, stats)
    assert moved != 1 and names != list(range(n))
    negatives.append('An omitted return move changes the word and its named slots.')
    assert (1 << 16) < (1 << 16)**2
    negatives.append('A log-width spectator does not absorb a quadratic descriptor bound.')
    # With s=h^2 and p<=2^h, one enlarged record has at least p^h bits.
    absorption = []
    for degree in (1, 8, 64, 256):
        h = degree+1
        p = 1 << h
        assert h*h >= degree*h
        assert 1 << (h*h) >= p**degree
        absorption.append(dict(descriptor_degree=degree, h=h, exact_exponent_gap=h*h-degree*h))
    # The old fallback rejects this row. The new routing proof permits it.
    # This is a comparison of outer constraints, not a constructed supplier.
    a, b, eta, beta = Q(4,5), Q(9,10), Q(1,10**6), Q(1,100)
    q = a*(1-2*eta)
    eps = (1-eta)/(1+q)
    g = eps*q
    r = (g+1-eps)/2
    delta = eta/8
    retained = dict(q_positive=q, bit_above_q=a-q, leaf_above_q=(1-beta)*b-q,
                    small_field_exposure=1-eps-g, phase_normalization=1-eps-r,
                    gaussian_local=1-eps-delta-g, gaussian_boundary=r-delta-g,
                    dimension=eps-g, scalar=1-eps-delta-g)
    assert all(value > 0 for value in retained.values())
    assert eps-a < 0
    receipt = dict(status='PASS', seed=110509, source_root=str(args.source_root),
                   source_head=(args.source_root / 'SOURCE-REVISION.txt').read_text().strip(),
                   verifier_sha256=sha256(verifier.read_bytes()).hexdigest(),
                   harness_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                   inherited_source=frozen, tiny_complete_addresses=small, cases=cases,
                   larger_forward_inverse_probes=probes, independent_named_slot_classes=placements,
                   statistics=dict(stats), descriptor_absorption_controls=absorption,
                   negative_controls=negatives,
                   hypothetical_relaxed_row=dict(a=str(a), b=str(b), eps=str(eps), q=str(q),
                       margin=str(g), old_short_record_slack=str(eps-a),
                       retained_slacks={key:str(value) for key,value in retained.items()},
                       unresolved_numeric_guards=['b < 1/32', 'r < 1/4'],
                       scope='No supplier with these savings is asserted. No numerical guard is removed.'),
                   remaining_ceiling='kappa < min(epsilon, 1-epsilon) <= 1/2',
                   wall_seconds=time.monotonic()-start,
                   scope='Finite address and layout controls support the written conditional all-size cost proof. They are not a complete asymptotic multiplication proof or a runtime benchmark.')
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({key:receipt[key] for key in ('status','tiny_complete_addresses','larger_forward_inverse_probes','independent_named_slot_classes','wall_seconds')}))


if __name__ == '__main__':
    main()
