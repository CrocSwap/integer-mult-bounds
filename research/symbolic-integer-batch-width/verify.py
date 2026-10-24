#!/usr/bin/env python3
"""Exact finite-flow batch replication. JoyboyBrian, OpenAI Codex; Apache-2.0."""
from collections import Counter
from fractions import Fraction
from itertools import product
from math import factorial, gcd, lcm, prod
from pathlib import Path
import hashlib
import json

PACKAGE = Path(__file__).resolve().parent
TARGETS = {3: 1, 4: 1}
PAID = (1, 2, 2)
MAX_RANK = 25
MAX_BITS = 4096
MAX_RECORDS = 10000


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_log2(n):
    need(n > 0, 'positive logarithm argument required')
    return (n - 1).bit_length()


def depth(n, targets, paid):
    need(bool(targets) and bool(paid), 'nonempty unit required')
    need(all(type(k) is int and k >= 2 and type(w) is int and w > 0
             for k, w in targets.items()), 'positive target multiplicities and ranks >= 2 required')
    need(all(type(r) is int and 1 <= r < min(targets) for r in paid), 'separation required')
    need(max(targets) <= n <= MAX_RANK, 'fixture rank outside bounded non-base domain')
    g, scale = 0, max(targets)
    while scale * min(targets) <= n:
        scale *= min(targets)
        g += 1
    return g


def indices(total, length):
    if length == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for tail in indices(total - first, length - 1):
                yield (first,) + tail


def symbolic_flow(n, targets=TARGETS, paid=PAID):
    """Section 3's multinomial classes, with chronological paid-position labels."""
    g = depth(n, targets, paid)
    kinds = tuple(sorted(targets))
    sources, exits, instances = Counter(), [], 0

    def visit(path, rho):
        nonlocal instances
        h = g - len(path)
        for a in indices(h, len(kinds)):
            c = prod(k ** count for k, count in zip(kinds, a))
            if max(kinds) * rho * c > n:
                continue
            u = factorial(h) // prod(factorial(count) for count in a)
            u *= prod(targets[k] ** count for k, count in zip(kinds, a))
            instances += u
            for k in kinds:
                if not path or max(kinds) * (rho // paid[path[-1]]) * c * k > n:
                    sources[k * rho * c] += targets[k] * u
        for j, r in enumerate(paid):
            if h:
                visit(path + (j,), rho * r)
            else:
                exits.append((path + (j,), rho * r, 1))
        need(instances + len(exits) <= MAX_RECORDS, 'flow fixture record cap exceeded')

    visit((), 1)
    return dict(sorted(sources.items())), exits, instances


def direct_flow(n, targets=TARGETS, paid=PAID):
    """Independent literal target-word slots and incoming-parent bijections."""
    g = depth(n, targets, paid)
    roles = tuple((k, role) for k, w in sorted(targets.items()) for role in range(w))
    sources, exits, instances = [], [], 0

    def visit(path, rho, incoming):
        nonlocal instances
        words = [word for word in product(roles, repeat=g-len(path))
                 if max(targets) * rho * prod(k for k, _ in word) <= n]
        instances += len(words)
        slots = {(role,) + word: role[0] * rho * prod(k for k, _ in word)
                 for word in words for role in roles}
        need(set(incoming) <= set(slots), 'unconsumed parent demand')
        for word, rank in incoming.items():
            need(slots[word] == rank, 'rank mismatch at actual parent slot')
        sources.extend(rank for word, rank in slots.items() if word not in incoming)
        for j, r in enumerate(paid):
            requests = {word: rho * r * prod(k for k, _ in word) for word in words}
            if len(path) < g:
                visit(path + (j,), rho * r, requests)
            else:
                need(len(requests) == 1, 'deepest class must have one unit')
                exits.append((path + (j,), next(iter(requests.values())), len(requests)))
        need(instances + len(exits) <= MAX_RECORDS, 'literal fixture record cap exceeded')

    visit((), 1, {})
    return dict(sorted(Counter(sources).items())), exits, instances


def batches(n, sources, exits):
    return [('complement', (s,), n-s, count) for s, count in sources.items() if n-s] + [
        ('exit', label, rank, count) for label, rank, count in exits]


def replication(rows, widths):
    need(all(rank in widths and type(count) is int and count > 0
             for _, _, rank, count in rows), 'invalid child batch')
    return lcm(*(widths[rank] // gcd(widths[rank], count) for _, _, rank, count in rows))


def check_divisibility(a, rows, widths):
    need(type(a) is int and a > 0, 'replication must be positive')
    for kind, label, rank, count in rows:
        need(a * count % widths[rank] == 0,
             f'nonintegral {kind} {label}: {a}*{count} / {widths[rank]}')


def compile_table(limit=MAX_RANK):
    widths = {n: 1 for n in range(1, max(TARGETS))}
    leaves = {n: n for n in widths}
    owned = {n: 0 for n in widths}
    width_bounds = {n: 0 for n in widths}
    owned_bounds = {n: 0 for n in widths}
    receipts = []
    for n in range(max(TARGETS), limit + 1):
        sources, exits, unit_count = symbolic_flow(n)
        need((sources, exits, unit_count) == direct_flow(n), 'symbolic/literal flow mismatch')
        rows = batches(n, sources, exits)
        deps = sorted({rank for _, _, rank, _ in rows})
        need(all(0 < rank < n for rank in deps), 'nondecreasing dependency')
        a = replication(rows, widths)
        check_divisibility(a, rows, widths)
        s = sum(sources.values())
        widths[n] = a * s
        leaves[n] = sum(a * count // widths[rank] * leaves[rank]
                        for _, _, rank, count in rows)
        owned[n] = a * unit_count + sum(a * count // widths[rank] * owned[rank]
                                       for _, _, rank, count in rows)
        need(Fraction(leaves[n], widths[n]) == sum(
            (Fraction(count * leaves[rank], widths[rank]) for _, _, rank, count in rows),
            Fraction()) / s, 'normalized paid leaf identity failed')
        width_bounds[n] = ceil_log2(s) + sum(width_bounds[q] for q in deps)
        h = sum(row[3] for row in rows)
        owned_bounds[n] = (sum(width_bounds[q] for q in deps)
                           + ceil_log2(unit_count + h + 1)
                           + max((owned_bounds[q] for q in deps), default=0))
        g = depth(n, TARGETS, PAID)
        w, j = sum(TARGETS.values()), len(PAID)
        c = ceil_log2(w) + ceil_log2(g+1) + g * ceil_log2(max(w, j))
        d = 1 + ceil_log2(2+w+j) + ceil_log2(g+1) + g * ceil_log2(max(w, j))
        closed_b = c * 2 ** (n-max(TARGETS))
        closed_o = c * 2 ** (n-max(TARGETS)+1) + (n-max(TARGETS)+1) * d
        need(ceil_log2(widths[n]) <= width_bounds[n] <= closed_b, 'width bit bound failed')
        need(ceil_log2(owned[n]+1) <= owned_bounds[n] <= closed_o, 'owned bit bound failed')
        need(max(widths[n].bit_length(), leaves[n].bit_length(), owned[n].bit_length()) <= MAX_BITS,
             'fixture integer bit cap exceeded')
        receipts.append({'N': n, 'G': g, 'sources': sources,
                         'ordered_exit_ranks': [e for _, e, _ in exits],
                         'flow_instances': unit_count, 'a': a, 'B': widths[n],
                         'P': leaves[n], 'O': owned[n],
                         'child_widths': sorted({widths[q] for q in deps}),
                         'width_log2_bound': width_bounds[n],
                         'owned_plus_one_log2_bound': owned_bounds[n]})
    return widths, leaves, owned, receipts


def reject(call, message):
    try:
        call()
    except ValueError as exc:
        need(message in str(exc), f'wrong rejection: {exc}')
        return
    raise ValueError('semantic mutant was accepted')


def verify():
    for row in json.loads((PACKAGE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            raw = (PACKAGE.parents[1] / row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source hash mismatch')
    widths, leaves, owned, receipts = compile_table()
    by_n = {row['N']: row for row in receipts}
    need((by_n[4]['B'], by_n[4]['P'], by_n[4]['O']) == (2, 6, 1), 'N4 calibration')
    need((by_n[5]['B'], by_n[5]['P'], by_n[5]['O']) == (2, 8, 1), 'N5 calibration')
    need(by_n[12]['sources'] == {4: 1, 8: 2, 9: 1, 12: 1}, 'N12 source calibration')
    need(by_n[12]['child_widths'] == [1, 2, 4], 'distinct recursive widths absent')
    need(by_n[12]['ordered_exit_ranks'] == [1, 2, 2, 2, 4, 4, 2, 4, 4], 'ordered exit calibration')
    # Direct integer batching checks every minimal factor and every allocated instance.
    for receipt in receipts:
        n = receipt['N']
        sources, exits, unit_count = direct_flow(n)
        rows = batches(n, sources, exits)
        a = receipt['a']
        for smaller in range(1, a):
            need(any(smaller * count % widths[rank] for _, _, rank, count in rows),
                 'smaller integral replication exists')
        need(a * unit_count + sum(sum(owned[rank] for _ in range(a*count//widths[rank]))
             for _, _, rank, count in rows) == receipt['O'], 'literal owned-instance census')
    sources7, exits7, _ = symbolic_flow(7)
    rows7 = batches(7, sources7, exits7)
    a_without_complement = replication([row for row in rows7 if row[0] == 'exit'], widths)
    reject(lambda: check_divisibility(a_without_complement, rows7, widths), 'nonintegral complement')
    sources25, exits25, _ = symbolic_flow(25)
    rows25 = batches(25, sources25, exits25)
    maximum = max(widths[q] // gcd(widths[q], t) for _, _, q, t in rows25)
    need(maximum == 16 and replication(rows25, widths) == 80, 'max/lcm witness changed')
    reject(lambda: check_divisibility(maximum, rows25, widths), 'nonintegral complement')
    rows22 = batches(22, *symbolic_flow(22)[:2])
    need(replication(rows22, widths) == 20 and lcm(*(widths[q] for _, _, q, _ in rows22)) == 40,
         'batch-sensitive improvement lost')
    # Isolate the actual N12 exit phase so its complement lcm cannot mask illegal coalescing.
    sources12, exits12, _ = symbolic_flow(12)
    exit_rows = [row for row in batches(12, sources12, exits12) if row[0] == 'exit']
    merged = Counter()
    for _, _, rank, count in exit_rows:
        merged[rank] += count
    merged_rows = [('exit', (), rank, count) for rank, count in merged.items()]
    need(replication(merged_rows, widths) == 1 and replication(exit_rows, widths) == 2,
         'ordered-exit coalescing witness changed')
    reject(lambda: check_divisibility(1, exit_rows, widths), 'nonintegral exit')
    # Nontrivial target multiplicities exercise Pascal role counts separately from the toy.
    need(symbolic_flow(12, {3: 2, 4: 1}) == direct_flow(12, {3: 2, 4: 1}),
         'multinomial target-role multiplicity mismatch')
    reject(lambda: symbolic_flow(4, {2: 1, 4: 1}, (2,)), 'separation required')
    reject(lambda: symbolic_flow(MAX_RANK+1), 'bounded non-base domain')
    return {'schema_version': 1, 'scope': 'toy finite integer flow; conditional general recurrence',
            'unit': {'targets': TARGETS, 'ordered_paid': PAID},
            'checked_ranks': [4, MAX_RANK], 'rows': receipts,
            'controls': ['omitted complement rejected at N7', 'max instead of lcm rejected at N25',
                         'merged repeated exits rejected in actual N12 exit phase',
                         'separation and rank cap enforced', 'nonunit target multiplicities checked'],
            'largest_fixture_integer_bits': max(x.bit_length() for table in (widths, leaves, owned)
                                               for x in table.values()),
            'not_claimed': ['native supplier admissibility', 'selected profile validation',
                            'physical allocation or runtime', 'new kappa', 'complete multiplication theorem']}


if __name__ == '__main__':
    result = verify()
    expected = PACKAGE / 'RESULT.json'
    if expected.exists():
        need(json.loads(expected.read_text()) == json.loads(json.dumps(result)), 'receipt mismatch')
    print(json.dumps(result, indent=2))
