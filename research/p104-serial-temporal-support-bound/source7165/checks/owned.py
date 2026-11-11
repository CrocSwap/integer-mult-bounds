"""Exact #7161 charged owned-MOVE sharing ceilings on retained contact clocks."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path
from time import monotonic

PACKAGE = 'research/p104-rank8-exit-funded-split'
HEAD = 'e3f8d39c43b07063dfc5b800f71c5d21015259e6'
PINS = {
    f'peer/{PACKAGE}/WORD.json.gz': 'c1caec11ca3ee264ef03018dd91037eac10c3e28950c4c525ee1b4bf5ee210e2',
    f'peer/{PACKAGE}/WORD.json.gz#decompressed': '9eff91418d838f1ffa20fe5c5975dc2c43a79b32d501fcbe30b90c50a7b11ce3',
    f'peer/{PACKAGE}/RESULT.json': '59080d75e7281b1a8c1353930917fd15869ad747ff4200948898f78f11c14089',
    'caller-inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'caller-inputs/interval_gate.py': '60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5',
}
TARGET = Fraction('0.0040075385047236')
PRIME = 2147483647
STAGES = 17
PUBLIC_SEEDS = (0, 1, 4, 6, 7, 8)
HOSTED_SEEDS = (2, 3, 5, 9, 10, 11)


def pinned(path, label):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == PINS[label], path
    return raw


def canonical_digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def span(vectors):
    result = {0}
    for vector in vectors:
        assert vector not in result
        result.update(value ^ vector for value in tuple(result))
    return frozenset(result)


def dimension(space):
    assert len(space) > 0 and len(space) & (len(space) - 1) == 0
    return len(space).bit_length() - 1


def distance(a, b):
    return dimension(a) + dimension(b) - 2 * dimension(a & b)


def overlap_interval(a, b, c, d):
    low1, high1 = (a, b) if a < b else (b, a)
    low2, high2 = (c, d) if c < d else (d, c)
    joint_lower = {u ^ v for u in low1 for v in low2}
    joint_upper = high1 & high2
    ranks = (dimension(joint_lower), dimension(joint_upper))
    return ranks, ranks[1] - ranks[0] if joint_lower <= joint_upper else None


def scan_word(word, check_time, event_cap):
    public = word['public']
    fields = word['owned_fields']
    spaces = list(map(span, word['frames']))
    charts = word['initial'] + [None] * fields
    active = set()
    contacts = defaultdict(list)
    native_moves, owned_moves = [], []
    opcodes = Counter()
    lifetimes = peak = 0
    program = word['program']
    assert len(program) <= event_cap, {'first_pending_native_event': event_cap}
    for i, event in enumerate(program):
        if i % 1024 == 0:
            check_time()
        op, r, *args = event
        assert 0 <= r < len(charts)
        opcodes[op] += 1
        if op != 'SCALE':
            contacts[r].append((i, op if op not in ('ADD', 'COPY') else op + '_DEST'))
        if op == 'MOVE':
            a, b, owned = args
            assert charts[r] == a and owned == (r >= public)
            assert spaces[a] < spaces[b] or owned and spaces[b] < spaces[a]
            rank = distance(spaces[a], spaces[b])
            move = dict(event=i, role=r, source=a, target=b, rank=rank)
            native_moves.append(move)
            if owned:
                assert r in active
                owned_moves.append(move)
            charts[r] = b
        elif op == 'INIT':
            assert r >= public and charts[r] is None and r not in active
            charts[r] = args[0]
            active.add(r)
            lifetimes += 1
            peak = max(peak, len(active))
        elif op == 'CLEAR':
            assert r >= public and charts[r] == args[0] and r in active
            charts[r] = None
            active.remove(r)
        elif op in ('ADD', 'COPY'):
            s, coeff, frame = args
            assert 0 <= s < len(charts) and s != r
            assert charts[r] == charts[s] == frame and Fraction(coeff)
            contacts[s].append((i, op + '_SOURCE'))
        else:
            assert op == 'SCALE' and charts[r] == args[1] and Fraction(args[0])
    assert charts == word['final'] + [None] * fields and not active
    for move in owned_moves:
        history = contacts[move['role']]
        j = history.index((move['event'], 'MOVE'))
        assert 0 < j < len(history) - 1
        before, after = history[j-1], history[j+1]
        move.update(window=[before[0]+1, after[0]], previous=before, following=after)
    assert (public, fields, lifetimes, peak, len(program), len(owned_moves)) == (1499, 63, 66, 48, 76349, 47)
    return spaces, native_moves, owned_moves, dict(
        public=public, owned_labels=fields, lifetimes=lifetimes, peak=peak, events=len(program), opcodes=opcodes,
    )


def full_invoice(word, caller, result, native_moves):
    dports = word['hosted']['Dports']
    second = dict(zip(dports, zip(word['hosted']['X2'], word['hosted']['Y2'])))
    assert caller['types']['A']['ports'] == dports
    assert sorted(dports + caller['types']['B']['ports']) == list(range(104))
    assert caller['ambient_rank'] == 145 and caller['stages'] == STAGES
    main = set(word['live']) | {r+112 for r in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    helpers = set(range(word['public'])) - main
    positions, staged = [], []
    paid = Counter()
    for ce, event in enumerate(caller['events']):
        if event[0] == 'J':
            stage, pa, pb = event[1:]
            staged.append(stage)
            mapping = {}
            for pi, r in enumerate(word['live']):
                a, b = pa[:2] if pi in second else pb[:2]
                mapping[r] = ('main', pi, a)
                mapping[r+112] = ('main', pi, b)
                if pi in second:
                    x, y = second[pi]
                    mapping[x] = ('main', pi, pa[2])
                    mapping[y] = ('main', pi, pa[3])
            assert set(mapping) == main and len(set(mapping.values())) == len(main)
            mapping.update((r, ('helper', ce, r)) for r in helpers)
            for r in range(word['public'], word['public'] + word['owned_fields']):
                mapping[r] = ('owned', ce, r-word['public'])
            assert len(mapping) == len(set(mapping.values())) == word['public'] + word['owned_fields']
            for move in native_moves:
                rank = move['rank']
                paid[rank] += 1
                positions.append([ce, move['event'], mapping[move['role']], rank, move['source'], move['target']])
        else:
            kind, op, role, *args = event
            if op not in ('IDLE_ONE', 'IDLE_ODD', 'QUERY'):
                assert op in ('ADD', 'SWAP', 'SCALE', 'LAMBDA')
                continue
            rank = 1 if op == 'QUERY' else 8 * len(args[0]) + (op == 'IDLE_ODD')
            for pi in caller['types'][kind]['ports']:
                owner = ('query_scratch', ce, pi) if op == 'QUERY' else ('main', pi, role)
                paid[rank] += 1
                positions.append([ce, op, owner, rank])
    assert staged == list(range(1, STAGES+1))
    binding = result['checks']['ODD-PHYSICAL-BINDING.json']
    assert binding['native_sha256'] == PINS[f'peer/{PACKAGE}/WORD.json.gz#decompressed']
    assert binding['caller_sha256'] == PINS['caller-inputs/CALLER.json']
    assert result['caller_sha256'] == binding['caller_sha256']
    geom = binding['occurrence_and_geometry']
    positions_sha = canonical_digest(positions)
    assert positions_sha == geom['complete_paid_position_digest']
    invoice = result['price']['after']
    assert paid == {int(r): n for r, n in invoice['P'].items()}
    assert invoice['T'] == geom['targets']
    assert sum(paid.values()) == geom['paid_positions'] == 110519
    assert sum(invoice['T'].values()) == geom['productive_fields'] == 22427
    signed = Counter({int(r): n for r, n in invoice['T'].items()})
    signed.subtract(paid)
    assert sum(r*n for r, n in signed.items()) == invoice['S'] == 1424
    return signed, dict(P=paid, T=invoice['T'], S=1424, paid_position_sha256=positions_sha)


def overlap(left, right):
    lo = max(left[0], right[0])
    hi = min(left[1], right[1])
    return [lo, hi] if lo <= hi else None


def match_max(edges):
    graph = defaultdict(dict)
    for i, j, weight in edges:
        if weight > 0:
            graph[i][j] = graph[j][i] = weight

    @lru_cache(None)
    def best(vertices):
        if not vertices:
            return 0, ()
        i = min(vertices, key=lambda v: (len(graph[v].keys() & vertices), v))
        rest = vertices - {i}
        winner = best(rest)
        for j in sorted(graph[i].keys() & rest):
            total, matching = best(rest - {j})
            pair = tuple(sorted((i, j)))
            winner = max(winner, (total + graph[i][j], tuple(sorted((pair,) + matching))))
        return winner

    value, chosen = best(frozenset(graph))
    return value, chosen, best.cache_info().currsize


def scan_pairs(owned, spaces, gate, check_time, pair_cap):
    counts = Counter({k: 0 for k in ('pairs', 'same_owner', 'distinct_owner', 'disjoint_windows',
                                   'overlap_windows', 'common_positive_interval', 'same_source',
                                   'same_target', 'cross_supply')})
    compatible, pending = [], None
    for left, right in combinations(owned, 2):
        i, j = left['event'], right['event']
        if counts['pairs'] == pair_cap:
            pending = [i, j]
            break
        check_time()
        counts['pairs'] += 1
        if left['role'] == right['role']:
            counts['same_owner'] += 1
            continue
        counts['distinct_owner'] += 1
        clock = overlap(left['window'], right['window'])
        if clock is None:
            counts['disjoint_windows'] += 1
            continue
        counts['overlap_windows'] += 1
        a, b, c, d = (spaces[move[key]] for move in (left, right) for key in ('source', 'target'))
        ranks, width = overlap_interval(a, b, c, d)
        relations = dict(common_positive_interval=width is not None and width > 0,
                         same_source=a == c, same_target=b == d, cross_supply=a == d or c == b)
        counts.update(key for key, present in relations.items() if present)
        credit = gate.moment(Counter((left['rank'], right['rank'])), TARGET)
        compatible.append(dict(events=[i, j], owners=[left['role'], right['role']], clock=clock,
                               paid_ranks=[left['rank'], right['rank']], overlap_ranks=ranks,
                               width=width, relations=relations, both_debits=gate.show(credit),
                               distances=[distance(a, b), distance(c, d), distance(a, d),
                                          distance(c, b), distance(b, d)]))
    return counts, compatible, pending


def pair_weights(pairs, gate, check_time):
    @lru_cache(None)
    def weight(rank):
        return gate.power(rank, TARGET) if rank else (0, 0)

    @lru_cache(None)
    def star(ab, ac, bc):
        # If a length exceeds this limit, clamping it preserves all inequalities.
        limit = max(ab, ac, bc)
        answer = None
        for a in range(limit+1):
            for b in range(max(0, ab-a), limit+1):
                c = max(0, ac-a, bc-b)
                candidate = (weight(a)[0] + weight(b)[0] + weight(c)[0], (a, b, c))
                answer = candidate if answer is None else min(answer, candidate)
        return answer

    result = []
    for pair in pairs:
        check_time()
        ab, cd, ad, cb, bd = pair['distances']
        assert pair['paid_ranks'] == [ab, cd]
        old = gate.add(weight(ab), weight(cd))
        star_a, lengths_a = star(ab, ad, bd)
        star_c, lengths_c = star(cb, cd, bd)
        costs = (old[0], weight(ad)[0]+weight(cb)[0], star_a, star_c)
        # Keeping the original charges has exactly zero saving, without roundoff.
        upper = max(0, old[1]-min(costs[1:]))
        i, j = pair['events']
        result.append((i, j, upper))
        pair.update(reroute_cost_lower=gate.show((min(costs), min(costs)))[0],
                    reroute_upper=gate.show((upper, upper))[0], star_lengths=[lengths_a, lengths_c])
    return result


def probe(word, sites, check_time):
    public = word['public']
    main = set(word['live']) | {r+112 for r in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    # Separate seed sets preserve the pair and triple witnesses.
    public_seeds = set(PUBLIC_SEEDS)
    rows = []
    for r in range(public + word['owned_fields']):
        x = tuple(int.from_bytes(sha256(f'owned-7161:{j}:{r}'.encode()).digest(), 'big') % PRIME
                  if (j in public_seeds and r < public or j not in public_seeds and r in main)
                  else 0 for j in range(len(PUBLIC_SEEDS) + len(HOSTED_SEEDS)))
        rows.append(x)
    zero = (0,) * (len(PUBLIC_SEEDS) + len(HOSTED_SEEDS))
    snapshots = {}
    seen_coeffs = {}

    def residue(s):
        if s not in seen_coeffs:
            q = Fraction(s)
            assert q.denominator % PRIME
            seen_coeffs[s] = q.numerator * pow(q.denominator, -1, PRIME) % PRIME
        return seen_coeffs[s]

    for i, (op, role, *args) in enumerate(word['program']):
        if i % 1024 == 0:
            check_time()
        if i in sites:
            assert op == 'MOVE' and args[-1]
            snapshots[i] = rows[role]
        if op == 'INIT':
            assert rows[role] == zero
        elif op == 'CLEAR':
            rows[role] = zero
        elif op == 'SCALE':
            c = residue(args[0])
            assert c
            rows[role] = tuple(c*x % PRIME for x in rows[role])
        elif op in ('ADD', 'COPY'):
            s, coeff, _ = args
            c = residue(coeff)
            if op == 'COPY':
                assert rows[role] == zero
            rows[role] = tuple((x+c*y) % PRIME for x, y in zip(rows[role], rows[s]))
        else:
            assert op == 'MOVE'
    assert snapshots.keys() == sites
    return snapshots, len(seen_coeffs)


def determinant(a, b, i, j):
    return (a[i]*b[j]-a[j]*b[i]) % PRIME


def determinant3(a, b, c, i, j, k):
    return (a[i]*determinant(b, c, j, k) - a[j]*determinant(b, c, i, k)
            + a[k]*determinant(b, c, i, j)) % PRIME


def async_chains(owned, snapshots, spaces, check_time):
    graph = defaultdict(set)
    pairs = []
    for a, b in combinations(owned, 2):
        check_time()
        i, j = a['event'], b['event']
        if determinant(snapshots[i], snapshots[j], 0, 1):
            continue
        graph[i].add(j)
        graph[j].add(i)
        pairs.append([i, j])

    move = {m['event']: m for m in owned}
    seen = set()
    chains = []
    for start in sorted(graph):
        if start in seen:
            continue
        component, stack = set(), [start]
        while stack:
            node = stack.pop()
            if node in component:
                continue
            component.add(node)
            stack.extend(graph[node] - component)
        seen.update(component)
        itinerary = [move[i] for i in sorted(component)]
        first, last = itinerary[0], itinerary[-1]
        # The four source/target cases follow one common calculation: later
        # original root frames are already required as earlier output frames.
        assert all(x['window'][1] < y['window'][0] and x['target'] == y['source']
                   for x, y in zip(itinerary, itinerary[1:]))
        labels = [first['source']] + [x['target'] for x in itinerary]
        assert len(set(spaces[x] for x in labels)) == len(labels)
        endpoint_distance = distance(spaces[first['source']], spaces[last['target']])
        assert all(m['rank'] == 1 for m in itinerary[:-1])
        assert endpoint_distance == sum(m['rank'] for m in itinerary)
        chains.append(dict(events=sorted(component), labels=labels, ranks=[m['rank'] for m in itinerary],
                           clocks=[m['window'] for m in itinerary], endpoint_distance=endpoint_distance,
                           necessary_positive_legs=len(itinerary)))
    return dict(zero_minor_pairs=pairs, chains=chains, compatible_pair_count=len(pairs),
                screened_pairs=len(owned)*(len(owned)-1)//2, saving_upper=0)


def scan_triples(owned, snapshots, gate, check_time, triple_cap):
    counts = Counter({k: 0 for k in ('unordered_triples', 'same_owner', 'disjoint_windows',
                                   'clock_compatible_tested', 'all_public_zero_minor', 'hosted_zero_minor')})
    checked, pending = [], None
    ranks = {m['event']: m['rank'] for m in owned}
    for group in combinations(owned, 3):
        check_time()
        counts['unordered_triples'] += 1
        if len({m['role'] for m in group}) != 3:
            counts['same_owner'] += 1
            continue
        left, center, right = [m['window'] for m in group]
        shared = overlap(left, center)
        shared = overlap(shared, right) if shared else None
        if not shared:
            counts['disjoint_windows'] += 1
            continue
        events = [m['event'] for m in group]
        if counts['clock_compatible_tested'] == triple_cap:
            pending = events
            break
        counts['clock_compatible_tested'] += 1
        a, b, c = map(snapshots.__getitem__, events)
        public_minor = determinant3(a, b, c, 0, 1, 4)
        hosted_minor = determinant3(a, b, c, 2, 3, 5)
        counts['all_public_zero_minor'] += not public_minor
        counts['hosted_zero_minor'] += not hosted_minor
        checked.append(dict(events=events, clock=shared, all_public_minor=public_minor,
                            hosted_only_minor=hosted_minor))

    vertices = {i for triple in checked for i in triple['events']}
    survivors = [t for t in checked if not t['all_public_minor']]
    survivor_vertices = {i for triple in survivors for i in triple['events']}

    def all_debits_upper(sites):
        return gate.smul(gate.moment(Counter(ranks[i] for i in sites), TARGET), STAGES)

    return dict(cap=triple_cap, first_pending=pending, counts=counts, tested=checked,
                vertices=sorted(vertices), price_before=gate.show(all_debits_upper(vertices)),
                survivors=survivors, survivor_price=gate.show(all_debits_upper(survivor_vertices)))


def rank_and_determinant(rows):
    matrix = [list(row) for row in rows]
    size = len(matrix)
    assert all(len(row) == size for row in matrix)
    rank = 0
    value = 1
    for col in range(size):
        pivot = next((i for i in range(rank, size) if matrix[i][col]), None)
        if pivot is None:
            continue
        if pivot != rank:
            matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
            value = -value
        coefficient = matrix[rank][col]
        value = value*coefficient % PRIME
        inverse = pow(coefficient, -1, PRIME)
        for i in range(rank+1, size):
            multiple = matrix[i][col]*inverse % PRIME
            if multiple:
                matrix[i] = [(x-multiple*y) % PRIME for x,y in zip(matrix[i], matrix[rank])]
        rank += 1
    return rank, value % PRIME if rank == size else 0


def maximal_clock_sets(owned, snapshots, check_time, cap):
    # Every compatible subset has a witness at its latest left endpoint.
    starts = sorted({m['window'][0] for m in owned})
    choices = {}
    count = 0
    multi_owner_cuts = 0
    for cut in starts:
        check_time()
        active = defaultdict(list)
        for move in owned:
            if move['window'][0] <= cut <= move['window'][1]:
                active[move['role']].append(move['event'])
        multi_owner_cuts += any(len(moves) > 1 for moves in active.values())
        for candidate in product(*active.values()):
            if count == cap:
                return dict(first_pending=[cut, sorted(candidate)], candidate_count=count, cap=cap)
            choices.setdefault(frozenset(candidate), cut)
            count += 1
    maximal = [s for s in choices if not any(s < t for t in choices)]
    hist = Counter()
    tests = []
    for compatible in sorted(maximal, key=lambda x: tuple(sorted(x))):
        check_time()
        events = sorted(compatible)
        width = len(events)
        hist[width] += 1
        assert width <= min(len(PUBLIC_SEEDS), len(HOSTED_SEEDS)), 'insufficient deterministic probes'

        def evaluate(seeds):
            matrix = [[snapshots[i][s] for s in seeds[:width]] for i in events]
            rank, value = rank_and_determinant(matrix)
            return dict(rank=rank, determinant=value)

        tests.append(dict(events=events, witness_cut=choices[compatible],
                          all_public=evaluate(PUBLIC_SEEDS), hosted_only=evaluate(HOSTED_SEEDS)))
    pending = [r for r in tests if r['all_public']['rank'] < len(r['events'])]
    return dict(first_pending=None, cap=cap, candidate_count=count, tested=tests, maximal_widths=hist,
                distinct_count=len(choices), max_width=max(hist), start_count=len(starts),
                same_owner_choices_at_cuts=multi_owner_cuts, modular_rank_unresolved=pending)


def run(peer_root, caller_path, gate_path, event_cap, pair_cap, triple_cap, seconds):
    started = monotonic()

    def check_time():
        assert monotonic()-started <= seconds, 'time cap reached before exhaustion'

    package = peer_root / PACKAGE
    compressed = pinned(package/'WORD.json.gz', f'peer/{PACKAGE}/WORD.json.gz')
    raw = gzip.decompress(compressed)
    assert sha256(raw).hexdigest() == PINS[f'peer/{PACKAGE}/WORD.json.gz#decompressed']
    word = json.loads(raw)
    result = json.loads(pinned(package/'RESULT.json', f'peer/{PACKAGE}/RESULT.json'))
    caller = json.loads(pinned(caller_path, 'caller-inputs/CALLER.json'))
    pinned(gate_path, 'caller-inputs/interval_gate.py')
    spec = spec_from_file_location('pinned_owned_interval', gate_path)
    gate = module_from_spec(spec)
    spec.loader.exec_module(gate)

    # Lucas–Lehmer for the prime exponent 31 verifies the reduction field.
    mersenne = 4
    for _ in range(29):
        mersenne = (mersenne*mersenne - 2) % PRIME
    assert PRIME == 2**31-1 and mersenne == 0
    h0, h1, h2 = (span(xs) for xs in ([], [1], [1, 2]))
    h3 = span([2])
    assert overlap_interval(h0, h2, h1, h2) == ((1, 2), 1)
    assert overlap_interval(h0, h1, h1, h2) == ((1, 1), 0)
    assert overlap_interval(h0, h1, h3, h2) == ((1, 1), None)
    assert overlap([1, 2], [2, 3]) == [2, 2] and overlap([1, 2], [3, 4]) is None
    assert match_max([(1, 2, 8), (1, 3, 7), (3, 4, 2)])[:2] == (10, ((1, 2), (3, 4)))
    assert determinant((1, 2), (2, 4), 0, 1) == 0
    assert determinant((1, 2), (2, 5), 0, 1) == 1
    assert determinant3((1, 0, 0), (0, 1, 0), (1, 1, 0), 0, 1, 2) == 0
    assert determinant3((1, 0, 0), (0, 1, 0), (1, 1, 1), 0, 1, 2) == 1
    assert rank_and_determinant(((0, 1), (1, 0))) == (2, PRIME-1)
    assert rank_and_determinant(((0, 1), (0, 2))) == (1, 0)

    spaces, native, owned, census = scan_word(word, check_time, event_cap)
    signed, invoice = full_invoice(word, caller, result, native)
    lo, hi = map(Fraction, result['price']['gate']['raw_bracket'])
    lo_sign, hi_sign = gate.moment(signed, lo), gate.moment(signed, hi)
    assert lo_sign[0] > 0 > hi_sign[1]
    baseline = gate.moment(signed, TARGET)
    hist = Counter(move['rank'] for move in owned)
    debit = gate.smul(gate.moment(hist, TARGET), STAGES)
    assert gate.add(baseline, debit)[0] > 0
    counts, pairs, pending = scan_pairs(owned, spaces, gate, check_time, pair_cap)
    if pending is not None:
        return dict(status='PAIR_CAP_PENDING', pins=PINS, census=census, counts=counts, first_pending=pending)
    assert counts['pairs'] == len(owned)*(len(owned)-1)//2
    assert counts['overlap_windows'] == len(pairs)
    ranks = {m['event']: m['rank'] for m in owned}
    candidates = [pair for pair in pairs if any(pair['relations'].values())]
    loose_edges = [(i, j, gate.moment(Counter((ranks[i], ranks[j])), TARGET)[1])
                   for i, j in (pair['events'] for pair in pairs)]
    direct_edges = [(i, j, gate.moment(Counter((ranks[i], ranks[j])), TARGET)[1])
                     for i, j in (pair['events'] for pair in candidates)]
    time_only = match_max(loose_edges)
    direct = match_max(direct_edges)
    direct_union = gate.moment(Counter(ranks[i] for i in {k for a,b,_ in direct_edges for k in (a,b)}), TARGET)[1]
    assert gate.add(baseline, (0, STAGES*direct_union))[1] < 0

    detour = pair_weights(pairs, gate, check_time)
    detour_before = match_max(detour)
    assert gate.add(baseline, (0, STAGES*detour_before[0]))[1] > 0
    snapshots, coeffs = probe(word, set(ranks), check_time)
    by_pair = {(i, j): upper for i, j, upper in detour}
    left_edges = []
    main_left_edges = []
    for pair in pairs:
        i, j = pair['events']
        minor = determinant(snapshots[i], snapshots[j], 0, 1)
        main_minor = determinant(snapshots[i], snapshots[j], 2, 3)
        pair.update(all_public_minor=minor, hosted_only_minor=main_minor)
        if not minor:
            left_edges.append((i, j, by_pair[i, j]))
        if not main_minor:
            main_left_edges.append((i, j, by_pair[i, j]))
    after_probe = match_max(left_edges)
    after_main_probe = match_max(main_left_edges)
    nonzero = sum(any(values[:2]) for values in snapshots.values())
    assert nonzero == 47
    async_result = async_chains(owned, snapshots, spaces, check_time)
    triple_result = scan_triples(owned, snapshots, gate, check_time, triple_cap)
    maximal_result = maximal_clock_sets(owned, snapshots, check_time, triple_cap)

    def price_report(upper, chosen=(), states=None):
        saving = STAGES * upper
        return dict(saving_upper=gate.show((saving, saving))[0], matching=chosen, states=states,
                    moment_upper=gate.show(gate.add(baseline, (0, saving)))[1])

    return dict(status='EXHAUSTED_OWNED_SHARE_NECESSARY_GATES', head=HEAD, pins=PINS,
                target=str(TARGET), census=census, invoice=invoice, raw_bracket=[str(lo), str(hi)],
                bracket_moments=[gate.show(lo_sign), gate.show(hi_sign)], baseline=gate.show(baseline),
                caps=dict(events=event_cap, pairs=pair_cap, triple_candidates=triple_cap, seconds=seconds),
                first_pending=triple_result['first_pending'] or maximal_result['first_pending'],
                counts=counts, owned_rank_hist=hist, owned=owned, pairs=pairs,
                all_old_debits=gate.show(debit), time_only=price_report(*time_only),
                direct_pair=price_report(*direct), direct_vertex_union=price_report(direct_union),
                arbitrary_nested_before_probe=price_report(*detour_before),
                arbitrary_nested_after_probe=price_report(*after_probe),
                arbitrary_nested_hosted_only_after_probe=price_report(*after_main_probe),
                asynchronous_cache=async_result, triple_corecovery=triple_result,
                maximal_common_clock=maximal_result,
                probe=dict(prime=PRIME, distinct_coefficient_tokens=coeffs, snapshots=snapshots,
                           nonzero_public_rows=nonzero, public_zero_minor_pairs=len(left_edges),
                           hosted_zero_minor_pairs=len(main_left_edges),
                           public_positive_credit_survivors=[(i,j) for i,j,u in left_edges if u>0],
                           hosted_positive_credit_survivors=[(i,j) for i,j,u in main_left_edges if u>0]),
                controls=['positive and zero-width intervals', 'incomparable interval', 'inclusive clock',
                          'matching cannot reuse one vertex', 'proportional and nonproportional minors',
                          'dependent and independent three-lane controls', 'singular and pivot-swap elimination'])


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    for label in ('peer_root', 'caller_path', 'gate_path'):
        parser.add_argument(label, type=Path)
    parser.add_argument('--event-cap', type=int, default=80000)
    parser.add_argument('--pair-cap', type=int, default=4096)
    parser.add_argument('--triple-cap', type=int, default=4096)
    parser.add_argument('--seconds', type=int, default=600)
    args = parser.parse_args()
    assert 0 < args.event_cap <= 80000 and 0 < args.pair_cap <= 4096 and 0 < args.seconds <= 600
    assert 0 < args.triple_cap <= 4096
    print(json.dumps(run(**vars(args)), indent=2, sort_keys=True))
