"""Exact actual-stream minima with three dirty roles; standard library only."""
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
POINTS = (1, 2, 3, 5, 6, 7, 9, 10, 11)
FULL_ID = tuple(1 << j for j in range(12))
PACKED_ID = sum(1 << (10 * j) for j in range(9))
LABELS = ((0, 1, 3, 2), (0, 3, 2, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def apply(columns, vector):
    result = 0
    for j, column in enumerate(columns):
        if vector >> j & 1:
            result ^= column
    return result


def compose(left, right):
    return tuple(apply(left, column) for column in right)


def pack(columns):
    return sum(((columns[p] >> q) & 1) << (9 * i + j)
               for i, q in enumerate(POINTS) for j, p in enumerate(POINTS))


def paid_alphabet():
    gates = []
    for label, pair in enumerate(((1, 2), (0, 2))):
        for u, v in product(range(1, 8), repeat=2):
            if (u & v).bit_count() % 2 == 0:
                continue
            sources = tuple(3 * r + p for r in range(3) if v >> r & 1
                            for p in pair)
            destinations = sum(1 << (9 * (3 * r + p)) for r in range(3)
                               if u >> r & 1 for p in pair)
            gates.append((label, u, v, sources, destinations))
    require(len(gates) == 56, 'complete rank-one projector alphabet')
    return tuple(gates)


def step(state, gate):
    value = 0
    for row in gate[3]:
        value ^= (state >> (9 * row)) & 511
    return state ^ (value * gate[4])


def packed_ball(gates):
    paths = {PACKED_ID: ()}
    frontier = [PACKED_ID]
    layers = [1]
    for _ in range(3):
        next_frontier = []
        for state in frontier:
            for index, gate in enumerate(gates):
                output = step(state, gate)
                if output not in paths:
                    paths[output] = paths[state] + (index,)
                    next_frontier.append(output)
        frontier = next_frontier
        layers.append(len(frontier))
    return paths, layers


def scalar_bases():
    bases = []
    for a, b, c in product(range(1, 8), repeat=3):
        if b in (a,) or c in (a, b, a ^ b):
            continue
        columns = (a, b, c)
        images = tuple(apply(columns, x) for x in range(8))
        require(len(set(images)) == 8, 'invertible scalar basis')
        inverse = tuple(images.index(1 << j) for j in range(3))
        bases.append((columns, inverse))
    require(len(bases) == 168, 'all scalar GL3 bases')
    return bases


def conjugated_call(basis, inverse, role, permutation):
    columns = []
    for source, point in product(range(3), range(4)):
        coefficients = inverse[source]
        output = 0
        for middle in range(3):
            if coefficients >> middle & 1:
                destination = permutation[point] if middle == role else point
                for target in range(3):
                    if basis[middle] >> target & 1:
                        output ^= 1 << (4 * target + destination)
        columns.append(output)
    return tuple(columns)


def full_alphabet():
    # This engine derives its alphabet by all 168 free scalar basis changes.
    operators = set()
    for basis, inverse in scalar_bases():
        for role, permutation in product(range(3), LABELS):
            operators.add(conjugated_call(basis, inverse, role, permutation))
    require(len(operators) == 56, '56 distinct actual conjugated calls')
    for operator in operators:
        require(compose(operator, operator) == FULL_ID, 'paid involution')
    return tuple(sorted(operators))


def lookup(columns):
    table = [0] * 4096
    for x in range(1, 4096):
        bit = x & -x
        table[x] = table[x ^ bit] ^ columns[bit.bit_length() - 1]
    return tuple(table)


def full_ball(operators):
    tables = tuple(lookup(operator) for operator in operators)
    distances = {FULL_ID: 0}
    frontier = [FULL_ID]
    layers = [1]
    for depth in range(1, 4):
        next_frontier = []
        for state in frontier:
            for table in tables:
                output = tuple(table[column] for column in state)
                if output not in distances:
                    distances[output] = depth
                    next_frontier.append(output)
        frontier = next_frontier
        layers.append(len(frontier))
    return distances, layers


def inverse(columns):
    rows = [sum(((columns[j] >> i) & 1) << j for j in range(12))
            | (1 << (12 + i)) for i in range(12)]
    for j in range(12):
        pivots = [i for i in range(j, 12) if rows[i] >> j & 1]
        require(bool(pivots), 'invertible actual stream operator')
        pivot = pivots[0]
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(12):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    return tuple(sum(((rows[i] >> (12 + j)) & 1) << i
                     for i in range(12)) for j in range(12))


def address_paths():
    paths = {tuple(range(4)): ()}
    frontier = [tuple(range(4))]
    for _ in range(3):
        next_frontier = []
        for permutation in frontier:
            for label, paid in enumerate(LABELS):
                output = tuple(paid[x] for x in permutation)
                if output not in paths:
                    paths[output] = paths[permutation] + (label,)
                    next_frontier.append(output)
        frontier = next_frontier
    require(len(paths) == 6, 'six GL2 point permutations')
    return paths


def endpoint(first, second):
    return tuple(1 << (4 * r + permutation[p])
                 for r, permutation in enumerate((first, second, tuple(range(4))))
                 for p in range(4))


def compare_balls(paths, distances):
    converted = {pack(state): depth for state, depth in distances.items()}
    require(len(converted) == len(distances), 'actual-to-packed injection')
    require(converted == {state: len(word) for state, word in paths.items()},
            'independent complete balls and distances agree')


def attaining_word(first, second, paths, gates):
    word = []
    for role, permutation in enumerate((first, second)):
        for label in paths[permutation]:
            candidates = [i for i, gate in enumerate(gates)
                          if gate[:3] == (label, 1 << role, 1 << role)]
            require(len(candidates) == 1, 'coordinate call exists uniquely')
            word.append(candidates[0])
    return tuple(word)


def replay(word, gates):
    state = PACKED_ID
    for index in word:
        require(type(index) is int and 0 <= index < 56, 'paid index')
        state = step(state, gates[index])
    return state


def shorter_join(target, direct, paths, distances, small_inverses, packed_inverses):
    if direct == 0:
        return 0
    budget = direct - 1
    left_radius, right_radius = budget // 2, budget - budget // 2
    row_order = [POINTS.index(target.index(1 << p)) for p in POINTS]
    target_table = lookup(target)
    probes = 0
    for state, inv in small_inverses:
        if distances[state] > left_radius:
            continue
        residual = tuple(target_table[column] for column in inv)
        full_hit = distances.get(residual, 4) <= right_radius
        packed_inverse = packed_inverses[pack(state)]
        packed_residual = sum(((packed_inverse >> (9 * j)) & 511) << (9 * i)
                              for i, j in enumerate(row_order))
        packed_hit = (packed_residual in paths
                      and len(paths[packed_residual]) <= right_radius)
        require(full_hit == packed_hit, 'independent target joins agree')
        require(not full_hit, 'a shorter actual-stream word exists')
        probes += 1
    return probes


def expect_rejection(operation, message):
    try:
        operation()
    except ValueError as error:
        require(message in str(error), 'control failed at intended predicate')
        return 1
    raise ValueError('negative control accepted')


def controls(paths, distances, rows, gates, actual, small_inverses, packed_inverses):
    count = 0
    missing = dict(distances)
    missing.pop(next(state for state, depth in missing.items() if depth == 3))
    count += expect_rejection(lambda: compare_balls(paths, missing), 'agree')
    wrong_depth = dict(distances)
    wrong_depth[next(state for state, depth in distances.items() if depth == 2)] = 1
    count += expect_rejection(lambda: compare_balls(paths, wrong_depth), 'agree')
    for row in rows:
        word = row['word']
        target = row['packed_target']
        for omitted in range(len(word)):
            mutant = word[:omitted] + word[omitted + 1:]
            count += expect_rejection(
                lambda: require(replay(mutant, gates) == target, 'endpoint'),
                'endpoint')
    # A leaked source bit in the spectator must fail the full endpoint test.
    target = endpoint(tuple(range(4)), tuple(range(4)))
    leak = list(target)
    leak[0] ^= 1 << 8
    count += expect_rejection(lambda: require(tuple(leak) == target, 'spectator'),
                              'spectator')
    shortest = next(row for row in rows if row['direct'] == 6)
    injected = dict(paths)
    injected[shortest['packed_target']] = ()
    count += expect_rejection(lambda: compare_balls(injected, distances), 'agree')
    one_call = next(row for row in rows if row['direct'] == 1)
    target = endpoint(one_call['first'], one_call['second'])
    count += expect_rejection(
        lambda: shorter_join(target, 2, paths, distances, small_inverses,
                             packed_inverses), 'shorter actual-stream word')
    require(len(actual) == len(gates) == 56, 'all labels retained')
    return count


def transfer_checks(gates, actual):
    # f1=e2+e3 and f2=e1+e3 on each physical role.
    basis = tuple(v << (4 * r) for r in range(3) for v in (12, 10))
    embedding = tuple(apply(basis, x) for x in range(64))
    decoding = {physical: x for x, physical in enumerate(embedding)}
    require(len(decoding) == 64, 'active summand injection')
    checked = 0
    for gate in gates:
        label, u, v = gate[:3]
        operator = next(g for g in actual if pack(g) == step(PACKED_ID, gate))
        for x in range(64):
            natural = x
            # Natural a writes coordinate 0 from 1; b writes 1 from 0.
            source_coordinate, target_coordinate = (1, 0) if label == 0 else (0, 1)
            coefficient = 0
            for role in range(3):
                if v >> role & 1:
                    coefficient ^= (x >> (2 * role + source_coordinate)) & 1
            for role in range(3):
                if u >> role & 1 and coefficient:
                    natural ^= 1 << (2 * role + target_coordinate)
            require(decoding[apply(operator, embedding[x])] == natural,
                    'actual-stream to natural-module bridge')
            checked += 1
    paths = address_paths()
    swap = tuple(LABELS[0][LABELS[1][LABELS[0][x]]] for x in range(4))
    for permutation, word in paths.items():
        completion = tuple(swap[permutation.index(x)] for x in range(4))
        require(completion in paths and len(paths[completion]) == 3 - len(word),
                'geodesic completion length')
        require(tuple(completion[x] for x in permutation) == swap,
                'completed two-SWAP endpoint')
    return checked, len(paths)


def calculate():
    gates = paid_alphabet()
    paths, layers = packed_ball(gates)
    actual = full_alphabet()
    require({pack(g) for g in actual} == {step(PACKED_ID, g) for g in gates},
            'both derivations enumerate the same paid alphabet')
    transfer_cases, completion_cases = transfer_checks(gates, actual)
    distances, full_layers = full_ball(actual)
    require(layers == full_layers == [1, 56, 1750, 45144], 'exact BFS layers')
    compare_balls(paths, distances)
    small_inverses = [(state, inverse(state)) for state, depth in distances.items()
                      if depth <= 2]
    packed_inverses = {}
    for state, inv in small_inverses:
        require(compose(state, inv) == FULL_ID, 'full inverse check')
        packed_inverses[pack(state)] = replay(reversed(paths[pack(state)]), gates)
        require(packed_inverses[pack(state)] == pack(inv), 'independent inverses')
    single = address_paths()
    rows, probes, full_columns = [], 0, 0
    for first, second in product(single, repeat=2):
        target = endpoint(first, second)
        direct = len(single[first]) + len(single[second])
        word = attaining_word(first, second, single, gates)
        require(replay(word, gates) == pack(target), 'attaining packed endpoint')
        full_state = FULL_ID
        for index in word:
            operator = next(g for g in actual if pack(g) == step(PACKED_ID, gates[index]))
            full_state = compose(operator, full_state)
        require(full_state == target, 'all twelve dirty input columns')
        full_columns += len(target)
        probes += shorter_join(target, direct, paths, distances, small_inverses,
                               packed_inverses)
        rows.append({'first': first, 'second': second, 'direct': direct,
                     'minimum': direct, 'word': word, 'packed_target': pack(target)})
    rejected = controls(paths, distances, rows, gates, actual, small_inverses,
                        packed_inverses)
    return {'status': 'PASS_GL2_WIDTH_ONE_THIRD_ROLE', 'claim_type': 'scoped proof', 'evidence_type': 'finite certificate',
            'roles': 3, 'width': 1, 'paid_alphabet': len(gates), 'layers': layers,
            'states': len(paths), 'expanded_transitions_per_engine': 56 * 1807,
            'join_probes_per_engine': probes, 'full_endpoint_columns': full_columns,
            'minimum_histogram': dict(sorted(Counter(row['minimum'] for row in rows).items())),
            'rejected_controls': rejected, 'transfer_cases': transfer_cases,
            'completion_cases': completion_cases, 'targets': rows}


def main():
    result = calculate()
    result['source_sha256'] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in sorted(HERE.iterdir()) if path.is_file()}
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
