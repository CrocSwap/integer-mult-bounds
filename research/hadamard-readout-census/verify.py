"""Independent permutation census, free-operator replay, and package checks."""

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent
H = ((1, 1, 1, 1), (1, -1, 1, -1),
     (1, 1, -1, -1), (1, -1, -1, 1))
TARGETS = tuple((1,) + t for t in product((-1, 1), repeat=3))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def balanced_calls(n):
    # Price literal emitted programs rather than importing the generator's
    # analytical count recurrence.
    return len(product_word(tuple(('price', 0, j) for j in range(n)), 0, 1,
                            tuple(range(2, 12))))


def difference_minima(vertices):
    """Independent shortest sum of state differences; no multiset enumerator."""
    d1 = {tuple(a[j] - b[j] for j in range(4)) for a in vertices for b in vertices}
    d2 = {tuple(a[j] + b[j] for j in range(4)) for a in d1 for b in d1}
    out = {}
    for t in TARGETS:
        if t in d1:
            out[t] = 2
        elif t in d2:
            out[t] = 4
        elif any(tuple(t[j] - d[j] for j in range(4)) in d2 for d in d1):
            out[t] = 6
        else:
            # Every coordinate unit difference occurs in this loop; four
            # pairs give an explicit upper bound for every target sign row.
            out[t] = 8
    return out


def independent_census():
    histogram = Counter()
    cache = {}
    events = tuple((j, s) for j in range(4) for s in (-1, 1))
    for word in permutations(events):
        first = [0] * 4
        q = [0] * 4
        qs = [(0, 0, 0, 0)]
        for j, s in word:
            if first[j] == 0:
                first[j] = s
            q[j] += s
            qs.append(tuple(q))
        require(q == [0] * 4, 'source loop failed')
        vertices = tuple(sorted({tuple(v[j] * first[j] for j in range(4)) for v in qs}))
        if vertices not in cache:
            cache[vertices] = difference_minima(vertices)
        minima = cache[vertices]
        profile = []
        for row in H:
            target = tuple(row[j] * first[j] for j in range(4))
            target = tuple(target[0] * x for x in target)
            profile.append(minima[target])
        histogram[tuple(profile)] += 1
    return histogram, len(cache)


def query_replay(word, expected=H):
    q = [0] * 4
    initial = [0] * 4
    endpoint = [[0] * 4 for _ in range(4)]
    calls = {'A': [0] * 4, 'B': [0] * 4}
    for kind, i, sign in word:
        require(kind in calls and type(i) is int and 0 <= i < 4 and sign in (-1, 1), 'bad query')
        calls[kind][i] += 1
        if kind == 'B':
            q[i] += sign
        else:
            initial[i] += sign
            for j in range(4):
                endpoint[i][j] += sign * q[j]
    require(q == [0] * 4, 'dirty connector not restored')
    require(initial == [0] * 4, 'initial connector dirt leaks into outputs')
    require(tuple(map(tuple, endpoint)) == tuple(map(tuple, expected)), 'wrong signed endpoint')
    return calls


def inverse(word):
    return [(d, s, a, -sign) for d, s, a, sign in reversed(word)]


def product_word(factors, source, target, pool):
    if len(factors) == 1:
        return [(target, source, factors[0], 1)]
    require(pool, 'insufficient dirty child pool')
    middle, deeper = pool[0], pool[1:]
    split = len(factors) // 2
    b = product_word(factors[:split], source, middle, deeper)
    a = product_word(factors[split:], middle, target, deeper)
    return b + a + inverse(b) + inverse(a)


def lower(word, alengths, blengths):
    out = []
    for kind, i, sign in word:
        n = alengths[i] if kind == 'A' else blengths[i]
        factors = tuple((kind, i, j) for j in range(n))
        source, target = (8, 4 + i) if kind == 'A' else (i, 8)
        query = product_word(factors, source, target, (9, 10, 11))
        out.extend(query if sign > 0 else inverse(query))
    return out


def formal_replay(program, alengths, blengths, query=None):
    initial = [{((), r): 1} for r in range(12)]
    state = [dict(p) for p in initial]
    maximum_terms = 1

    def apply(program):
        nonlocal maximum_terms
        for dst, src, factor, sign in program:
            require(dst != src, 'source/target alias')
            require(dst >= 4, 'external source written at a prefix')
            for (letters, row), coefficient in list(state[src].items()):
                key = ((factor,) + letters, row)
                state[dst][key] = state[dst].get(key, 0) + sign * coefficient
                if not state[dst][key]:
                    del state[dst][key]
            maximum_terms = max(maximum_terms, max(map(len, state)))

    apply(program)
    expected = [dict(p) for p in initial]
    if query is None:
        for i, row in enumerate(H):
            for j, sign in enumerate(row):
                letters = tuple(('A', i, k) for k in reversed(range(alengths[i])))
                letters += tuple(('B', j, k) for k in reversed(range(blengths[j])))
                expected[4 + i][(letters, j)] = sign
    else:
        kind, i, sign = query
        n = alengths[i] if kind == 'A' else blengths[i]
        source, target = (8, 4 + i) if kind == 'A' else (i, 8)
        letters = tuple((kind, i, k) for k in reversed(range(n)))
        expected[target][(letters, source)] = sign
    require(state == expected, 'free noncommuting dirty-state endpoint failed')
    apply(inverse(program))
    require(state == initial, 'literal primitive inverse failed')
    return maximum_terms


def prefix_bound(program, operator_bound=6, input_bound=7):
    """Bound row and scalar intermediates, including independent initial dirt."""
    state = [{((), r): 1} for r in range(12)]
    largest = input_bound
    for dst, src, factor, sign in program:
        target_bound = input_bound * sum(abs(c) * operator_bound ** len(key[0])
                                         for key, c in state[dst].items())
        increment_bound = input_bound * sum(abs(c) * operator_bound ** (len(key[0]) + 1)
                                            for key, c in state[src].items())
        # Also cover partial dot products, coefficient products and target
        # addition before symbolic cancellation can lower the row bound.
        largest = max(largest, target_bound + increment_bound)
        for (letters, row), coefficient in list(state[src].items()):
            key = ((factor,) + letters, row)
            state[dst][key] = state[dst].get(key, 0) + sign * coefficient
            if state[dst][key] == 0:
                del state[dst][key]
        bound = input_bound * sum(abs(c) * operator_bound ** len(key[0])
                                  for key, c in state[dst].items())
        largest = max(largest, bound)
    return largest


def dense_checks(program, alengths, blengths, dimension):
    rng = random.Random(55 + dimension)
    factors = {(kind, i, j): tuple(tuple(rng.randrange(-2, 3) for _ in range(dimension))
               for _ in range(dimension)) for kind, lengths in (('A', alengths), ('B', blengths))
               for i, length in enumerate(lengths) for j in range(length)}

    def mv(matrix, vector):
        return [sum(a * b for a, b in zip(row, vector)) for row in matrix]

    def chain(kind, i, length, vector):
        for j in range(length):
            vector = mv(factors[kind, i, j], vector)
        return vector

    def apply(state, instructions):
        for dst, src, factor, sign in instructions:
            increment = mv(factors[factor], state[src])
            state[dst] = [x + sign * y for x, y in zip(state[dst], increment)]

    cases = []
    for index in range(12 * dimension):
        state = [[0] * dimension for _ in range(12)]
        state[index // dimension][index % dimension] = 1
        cases.append(state)
    cases.append([[rng.randrange(-7, 8) for _ in range(dimension)] for _ in range(12)])
    for initial in cases:
        expected = [list(row) for row in initial]
        for i, hrow in enumerate(H):
            for j, sign in enumerate(hrow):
                value = chain('B', j, blengths[j], list(initial[j]))
                value = chain('A', i, alengths[i], value)
                expected[4 + i] = [x + sign * y for x, y in zip(expected[4 + i], value)]
        state = [list(row) for row in initial]
        apply(state, program)
        require(state == expected, 'independent dense endpoint failed')
        apply(state, inverse(program))
        require(state == initial, 'independent dense inverse failed')
    return len(cases)


def internal_nodes(n):
    return 0 if n == 1 else 1 + 2 * internal_nodes(n // 2) + 2 * internal_nodes(n - n // 2)


def complete_invoice(word, alengths, blengths):
    calls = query_replay(word)
    leaves = sum(calls[kind][i] * balanced_calls(n)
                 for kind, lengths in (('A', alengths), ('B', blengths))
                 for i, n in enumerate(lengths))
    nodes = sum(calls[kind][i] * internal_nodes(n)
                for kind, lengths in (('A', alengths), ('B', blengths))
                for i, n in enumerate(lengths))
    return {'queries': len(word), 'primitive_leaves': leaves, 'echo_nodes': nodes,
            'child_call_entries': leaves + nodes, 'dirty_arrays': 4,
            'source_rows': 4, 'output_rows': 4,
            'coefficient_matrices': sum(alengths) + sum(blengths)}


def source_checks():
    pins = json.loads((ROOT / 'SOURCES.json').read_text())
    names = {'sources/PR997-' + n for n in ('CONSTRUCTION.json', 'PROOF.md', 'NOTICE.md', 'README.md')}
    names |= {'sources/BASE-selected-result.json', 'sources/PR1088-README.md', 'sources/PR1088-NOTICE.md'}
    require(set(pins['files']) == names, 'source inventory coverage gap')
    for name, pin in pins['files'].items():
        path = ROOT / name
        require(hashlib.sha256(path.read_bytes()).hexdigest() == pin['sha256'], 'source pin mismatch: ' + name)


def main():
    source_checks()
    result = json.loads((ROOT / 'CERTIFICATE.json').read_text())
    predecessor = json.loads((ROOT / 'sources/PR997-CONSTRUCTION.json').read_text())
    require(result['format'] == 'hadamard-readout-census/1' and result['assignment_seed'] == 55,
            'experiment metadata mismatch')
    require(result['base_commit'] == 'ce7ad1b6ab09452c3478723a2e96ed5ff212dc08', 'base mismatch')
    require(result['A_lengths'] == predecessor['A_lengths'] and
            result['B_lengths'] == predecessor['B_lengths'], 'comparison fixture changed')
    histogram, cache_count = independent_census()
    expected = Counter({tuple(p['profile']): p['paths'] for p in result['profile_histogram']})
    require(histogram == expected, 'independent exhaustive histogram mismatch')
    require(sum(histogram.values()) == 40320, 'signed coverage gap')
    require(result['unsigned_paths'] == 2520 and result['signed_paths'] == 40320, 'reported coverage mismatch')
    require(len(histogram) == 114, 'profile coverage mismatch')
    frontier = sorted(p for p in histogram if not any(
        q != p and all(x <= y for x, y in zip(q, p)) for q in histogram))
    require(list(map(list, frontier)) == result['pareto_profiles'], 'Pareto mismatch')
    families = {p for pattern in ((2, 4, 4, 4), (2, 2, 6, 6), (2, 2, 4, 8))
                for p in permutations(pattern)}
    require(set(frontier) == families, 'written profile families differ')
    require(8 + min(map(sum, histogram)) == result['minimum_queries'] == 22, 'query optimum mismatch')
    ap = [balanced_calls(n) for n in result['A_lengths']]
    bp = [balanced_calls(n) for n in result['B_lengths']]
    require(ap == result['A_leaf_prices'] and bp == result['B_leaf_prices'], 'price receipt mismatch')
    best = 2 * sum(bp) + min(sum(x * y for x, y in zip(p, ap)) for p in histogram)
    require(best == result['minimum_leaf_calls'] == 222, 'weighted optimum mismatch')
    price_cases = 0
    for prices in product((Fraction(1, 2), Fraction(1), Fraction(3, 2),
                           Fraction(2), Fraction(3), Fraction(4)), repeat=4):
        a, b, c, d = sorted(prices)
        envelope = 4*a + 4*b + 2*c + 2*d + min(2*c, 4*a)
        actual = min(sum(x*y for x, y in zip(p, prices)) for p in histogram)
        require(envelope == actual, 'rational price envelope mismatch')
        price_cases += 1
    local_queries = 0
    for kind in ('A', 'B'):
        for i in range(4):
            for sign in (-1, 1):
                query = (kind, i, sign)
                formal_replay(lower([query], result['A_lengths'], result['B_lengths']),
                              result['A_lengths'], result['B_lengths'], query=query)
                local_queries += 1
    dense = 0
    require([tuple(entry['profile']) for entry in result['frontier_words']] == frontier,
            'frontier witness coverage gap')
    for entry in result['frontier_words']:
        calls = query_replay(entry['word'])
        require(calls['A'] == entry['profile'] and calls['B'] == [2] * 4, 'witness call profile mismatch')
        program = lower(entry['word'], result['A_lengths'], result['B_lengths'])
        formal_replay(program, result['A_lengths'], result['B_lengths'])
        dense += dense_checks(program, result['A_lengths'], result['B_lengths'], 2)
    calls = query_replay(result['word'])
    require(calls['A'] == result['chosen_profile'], 'chosen word profile mismatch')
    bevents = [(i, sign) for kind, i, sign in result['word'] if kind == 'B']
    first = [0] * 4
    for i, sign in bevents:
        if first[i] == 0:
            first[i] = sign
    require([i for i, sign in bevents] == result['source_path'] and first == result['first_signs'],
            'source path receipt mismatch')
    program = lower(result['word'], result['A_lengths'], result['B_lengths'])
    require(len(program) == best, 'complete lowering count mismatch')
    dense += dense_checks(program, result['A_lengths'], result['B_lengths'], 3)
    query_replay(predecessor['word'])
    old = lower(predecessor['word'], predecessor['A_lengths'], predecessor['B_lengths'])
    formal_replay(old, predecessor['A_lengths'], predecessor['B_lengths'])
    require(len(old) == predecessor['leaf_calls'] == 238, 'matched predecessor count mismatch')
    dense += dense_checks(old, predecessor['A_lengths'], predecessor['B_lengths'], 3)
    new_invoice = complete_invoice(result['word'], result['A_lengths'], result['B_lengths'])
    old_invoice = complete_invoice(predecessor['word'], predecessor['A_lengths'], predecessor['B_lengths'])
    require(new_invoice['echo_nodes'] == 66 and old_invoice['echo_nodes'] == 72, 'echo invoice mismatch')
    require(new_invoice['child_call_entries'] == 288 and old_invoice['child_call_entries'] == 310,
            'child dispatch invoice mismatch')
    bound = max(prefix_bound(program + inverse(program)), prefix_bound(old + inverse(old)))
    common_signed_width = bound.bit_length() + 1
    controls = 0
    mutations = []
    for kind in ('A', 'B'):
        for index in [k for k, event in enumerate(result['word']) if event[0] == kind][:2]:
            removed = [list(e) for e in result['word']]
            del removed[index]
            mutations.append(removed)
            flipped = [list(e) for e in result['word']]
            flipped[index][2] *= -1
            mutations.append(flipped)
    for word in mutations:
        try:
            query_replay(word)
        except ValueError:
            controls += 1
        else:
            raise ValueError('mutation unexpectedly passed')
    try:
        formal_replay(program[:-1], result['A_lengths'], result['B_lengths'])
    except ValueError:
        controls += 1
    else:
        raise ValueError('missing restoration leaf passed')
    require(controls == 9, 'control count mismatch')
    # Equal complete query prices prefer a 22-query profile, and sufficiently
    # costly outer dispatch reverses this particular operation-count benefit.
    require(8 + sum(result['chosen_profile']) == 24, 'weighted word query count mismatch')
    require(best + 100 * 24 > 238 + 100 * 22, 'expensive dispatch control failed')
    controls += 1
    print('PASS_HADAMARD_READOUT_CENSUS signed_paths=40320 profiles=114 pareto=22 '
          'queries=22 leaf_calls=222_vs_238 controls=10 no_new_kappa')
    print(json.dumps({'independent_vertex_sets': cache_count,
                      'frontier_free_operator_replays': len(frontier),
                      'dense_basis_and_dirty_replays': dense,
                      'rational_price_cases': price_cases, 'local_child_contracts': local_queries,
                      'common_prefix_absolute_bound': bound, 'common_signed_width_bits': common_signed_width,
                      'chosen_primitive_sha256': hashlib.sha256(json.dumps(program, separators=(',', ':')).encode()).hexdigest(),
                      'predecessor_primitive_sha256': hashlib.sha256(json.dumps(old, separators=(',', ':')).encode()).hexdigest(),
                      'new_invoice': new_invoice, 'predecessor_invoice': old_invoice,
                      'chosen_primitive_calls': len(program),
                      'predecessor_primitive_calls': len(old)}))


if __name__ == '__main__':
    main()
