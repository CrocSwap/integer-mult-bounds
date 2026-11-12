"""Reverse lifetime indexing and BFS for the exact current multi-ADD census."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha1, sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm

ROOT = Path(__file__).resolve().parent
PINS = {
    '7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    '7361-REVERSE.json': '917ddb1a1af768333e9e6dd797f4f99704e8160ea9a8210128b9293e0a7166cc',
}


def verify_inputs():
    sources = {}
    for path, digest in PINS.items():
        data = (ROOT / 'inputs' / path).read_bytes()
        assert sha256(data).hexdigest() == digest, path
        sources[path] = data
    old = sources['7361-REVERSE.json']
    assert sha1(f'blob {len(old)}\0'.encode() + old).hexdigest() == '24889261999bc4dc9f764d5a0dafbc3845ba5351'
    word = decompress(sources['7334-WORD.json.gz'])
    assert sha256(word).hexdigest() == '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
    return loads(word), loads(old)


def reverse_trace(w):
    tape, n = w['program'], w['public']
    cursor = {r: (r, len(tape)) for r in range(n)}
    frames = {cursor[r]: c for r, c in enumerate(w['final'])}
    fixed = set(cursor.values())
    adj, contacts, transport = defaultdict(set), defaultdict(set), defaultdict(set)
    for t in range(len(tape) - 1, -1, -1):
        op, r, *payload = tape[t]
        if op == 'CLEAR':
            assert r >= n and r not in cursor
            cursor[r] = r, t
            frames[cursor[r]] = payload[0]
            continue
        outgoing = cursor[r]
        if op == 'INIT':
            assert r >= n and frames[outgoing] == payload[0]
            del cursor[r]
        elif op == 'MOVE':
            lo, hi, owned = payload
            assert frames[outgoing] == hi and owned == (r >= n)
            incoming = r, t
            frames[incoming] = lo
            cursor[r] = incoming
            transport[incoming].add((t, hi, 'source'))
            transport[outgoing].add((t, lo, 'target'))
        elif op in ('ADD', 'COPY'):
            s, _, chart = payload
            other = cursor[s]
            assert r != s and frames[other] == frames[outgoing] == chart
            adj[outgoing].add(other)
            adj[other].add(outgoing)
            contacts[outgoing].add((t, op))
            contacts[other].add((t, op))
        else:
            assert op == 'SCALE' and frames[outgoing] == payload[1]
            contacts[outgoing].add((t, op))
    assert sorted(cursor) == list(range(n))
    assert [frames[cursor[r]] for r in range(n)] == w['initial']
    fixed.update(cursor.values())
    return frames, fixed, adj, contacts, transport


def components(adj):
    seen = set()
    for vertex in sorted(adj):
        if vertex in seen:
            continue
        group, stack = {vertex}, [vertex]
        while stack:
            node = stack.pop()
            new = adj[node] - group
            stack.extend(new)
            group.update(new)
        seen.update(group)
        yield group


def frame_space(basis):
    points = {0}
    for size in range(1, len(basis) + 1):
        for terms in combinations(basis, size):
            v = 0
            for term in terms:
                v ^= term
            points.add(v)
    assert len(points) == 1 << len(basis)
    return points


def solve(w, inherited):
    n = w['public']
    main = set(w['live']) | {i + 112 for i in w['live']} | set(w['hosted']['X2']) | set(w['hosted']['Y2'])
    assert len(main) == 400 and n == 1501 and len(w['program']) == 76466
    frames, fixed, adj, contacts, transport = reverse_trace(w)
    spaces = [frame_space(f) for f in w['frames']]
    ranks = [len(f) for f in w['frames']]
    tariff = run_path(str(ROOT / 'inputs' / 'pricing.py'))['power_bounds']
    k0 = Fraction('0.00364665195644044790699554028334161')
    k1 = Fraction('0.00364665195644044790699554028334162')
    lower = [Fraction(0)] + [tariff(r, k1)[0] for r in range(1, 10)]
    upper = [Fraction(0)] + [tariff(r, k0)[1] for r in range(1, 10)]

    @cache
    def priced(deltas):
        lo = sum((lower[r] if c > 0 else upper[r]) * c for r, c in deltas)
        hi = sum((upper[r] if c > 0 else lower[r]) * c for r, c in deltas)
        return str(17 * lo), str(17 * hi)

    counts, rows = Counter(), []
    for group in components(adj):
        events = sorted(set().union(*(contacts[s] for s in group)))
        if sum(tag == 'ADD' for _, tag in events) < 2:
            continue
        counts['multi_add'] += 1
        if any(r in main or r >= n for r, _ in group):
            counts['main_or_owned'] += 1
            continue
        if group & fixed:
            counts['fixed_endpoint'] += 1
            continue
        counts['closed_pure'] += 1
        chart, = {frames[s] for s in group}
        edges = sorted(set().union(*(transport[s] for s in group)))
        assert edges and len(edges) == len({t for t, _, _ in edges})
        incoming = [c for _, c, side in edges if side == 'target']
        outgoing = [c for _, c, side in edges if side == 'source']
        assert len(incoming) == len(outgoing) == len(group)
        lo = max(ranks[c] + 1 for c in incoming)
        hi = min(ranks[c] - 1 for c in outgoing)
        low_space, high_space = {0}, set(range(512))
        for c in incoming:
            low_space = {a ^ b for a in low_space for b in spaces[c]}
        for c in outgoing:
            high_space &= spaces[c]
        d = ranks[chart]
        assert low_space <= spaces[chart] <= high_space and lo <= d <= hi
        first = max(lo, len(low_space).bit_length() - 1)
        last = min(hi, len(high_space).bit_length() - 1)
        assert first <= d <= last
        old = Counter([d - ranks[c] for c in incoming] + [ranks[c] - d for c in outgoing])

        def endpoints(a, b):
            out = []
            for rank in sorted({a, b}):
                terms = old.copy()
                terms.subtract([rank - ranks[c] for c in incoming])
                terms.subtract([ranks[c] - rank for c in outgoing])
                quote = priced(tuple(sorted((r, c) for r, c in terms.items() if c)))
                if Fraction(quote[1]) > 0:
                    out.append((rank, quote))
            return out

        relaxed = endpoints(lo, hi)
        if not relaxed:
            counts['dimension_nonpositive'] += 1
            continue
        possible = endpoints(first, last)
        counts['geometry_survivor' if possible else 'geometry_exclusion'] += 1
        rows.append({'first_contact': events[0][0], 'old_chart': chart, 'old_rank': d,
                     'roles': sorted({r for r, _ in group}), 'contacts': events, 'moves': edges,
                     'relaxed_ranks': [lo, hi], 'feasible_ranks': [first, last],
                     'price_positive_relaxed': relaxed, 'price_positive_feasible': possible,
                     'lower_span': sorted(low_space), 'upper_span': sorted(high_space)})
    rows.sort(key=lambda r: r['first_contact'])
    rebind = {(r['key'][0], min(r['clock_map'][x] for x in r['signed_ancestor_ADDs'])) for r in inherited['outcomes']}
    actual = {(r['old_chart'], min(t for t, tag in r['contacts'] if tag == 'ADD')) for r in rows}
    assert len(rebind) == 13 and actual - rebind == {(746, 40834)} and rebind <= actual
    changed, = (r for r in rows if r['old_chart'] == 746)
    assert [t for t, tag in changed['contacts'] if tag == 'ADD'] == [40834, 41179]
    assert changed['relaxed_ranks'] == [4, 6] and changed['feasible_ranks'] == [5, 6]
    assert not changed['price_positive_feasible']
    return {'counts': counts, 'cases': rows, 'exact_prior_7361_keys': sorted(rebind),
            'exact_prior_7369_key': [746, 40834], 'new_price_positive_keys': [], 'runner_cap_seconds': 40}


def main():
    assert __debug__
    alarm(40)
    result = solve(*verify_inputs())
    alarm(0)
    print(dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
