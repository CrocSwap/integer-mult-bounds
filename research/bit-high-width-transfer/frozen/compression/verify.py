#!/usr/bin/env python3
"""Independent exact controls for the written helper-compression theorem.

Worker A review for @CubeJerry, with substantial OpenAI Codex assistance.
Apache-2.0. Finite controls do not establish the universal theorem.
"""
from collections import Counter
from itertools import product
import json
from pathlib import Path
from random import Random
import runpy

core = runpy.run_path(str(Path(__file__).with_name('compress.py')))
compress_calls = core['compress_calls']
factor_helpers = core['factor_helpers']
ZERO = (0, 0, 0, 0)
E11, E22, ONES = (1, 0, 0, 0), (0, 0, 0, 1), (1, 1, 1, 1)
SEED = 2026110617


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return sum(((x >> j) & 1) * ((y >> j) & 1)
               for j in range(max(x.bit_length(), y.bit_length()))) % 2


def rank_by_span(vectors):
    """Independent rank oracle: enumerate the entire binary span, no elimination."""
    span = {0}
    for v in vectors:
        span |= {x ^ v for x in tuple(span)}
    return len(span).bit_length() - 1


def gram(left, right):
    return [sum(dot(y, x) << j for j, y in enumerate(right)) for x in left]


def same_pairings(left, right, smaller_left, smaller_right):
    need(gram(left, right) == gram(smaller_left, smaller_right), 'Every scalar pairing preserved')


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def negative(a):
    return tuple(-x for x in a)


def rank_one(a):
    return len(a) == 4 and a != ZERO and a[0] * a[3] == a[1] * a[2]


def identity(n):
    return [[{ZERO} if i == j else set() for j in range(n)] for i in range(n)]


def ring_product(a, b):
    result = set()
    for x in a:
        for y in b:
            z = add(x, y)
            result.symmetric_difference_update((z,))
    return result


def matrix_product(a, b):
    n = len(a)
    result = [[set() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for h in range(n):
            if not a[i][h]:
                continue
            for j in range(n):
                if b[h][j]:
                    result[i][j] ^= ring_product(a[i][h], b[h][j])
    return result


def formal_word(calls, registers):
    """Direct matrix multiplication in F_2[(M_2(Z),+)], without the H formula."""
    result = identity(registers)
    for a, x, y in calls:
        need(rank_one(a), 'Nonzero rank-one address fixture')
        need(0 <= x < 1 << registers and 0 <= y < 1 << registers and dot(x, y) == 1,
             'Legal scalar projector')
        factor = identity(registers)
        for i in range(registers):
            if x >> i & 1:
                for j in range(registers):
                    if y >> j & 1:
                        factor[i][j] ^= {ZERO} ^ {a}
        result = matrix_product(result, factor)
    return result


def target_matrix(targets, helpers):
    exponents = list(targets) + [ZERO] * helpers
    return [[{exponents[i]} if i == j else set() for j in range(len(exponents))]
            for i in range(len(exponents))]


def successful_control(name, calls, targets, helpers):
    data, registers = len(targets), len(targets) + helpers
    need(all(a != ZERO for a in targets), 'Count only nonidentity data targets')
    before = tuple(calls)
    need(formal_word(calls, registers) == target_matrix(targets, helpers), 'Full restored-helper endpoint')
    smaller, width = compress_calls(calls, data, registers)
    need(tuple(calls) == before and [a for a, _, _ in smaller] == [a for a, _, _ in calls],
         'Frames, order and source word unchanged')
    mask = (1 << data) - 1
    need(all((x & mask, y & mask) == (xx & mask, yy & mask)
             for (_, x, y), (_, xx, yy) in zip(calls, smaller)), 'Data components unchanged')
    same_pairings([x for _, x, _ in calls], [y for _, _, y in calls],
                  [x for _, x, _ in smaller], [y for _, _, y in smaller])
    need(formal_word(smaller, data + width) == target_matrix(targets, width), 'Compressed full endpoint')
    left, right = [x >> data for _, x, _ in calls], [y >> data for _, _, y in calls]
    u, v = rank_by_span(left), rank_by_span(right)
    need(width == rank_by_span(gram(left, right)), 'Minimal pairing-preserving dimension')
    need(rank_by_span([x for _, x, _ in calls]) == data + u and
         rank_by_span([y for _, _, y in calls]) == data + v, 'Data coordinate spaces included')
    need(u + v <= len(calls) - data and width <= min(u, v) and
         width <= (len(calls) - data) // 2, 'Call-surplus helper bound')
    return {'case': name, 'calls': len(calls), 'data': data, 'original_helpers': helpers,
            'left_rank': u, 'right_rank': v, 'compressed_helpers': width}


def expect_rejection(name, action, controls):
    try:
        action()
    except ValueError:
        controls.append(name)
    else:
        raise ValueError('Control was not rejected: ' + name)


def random_frame(rng):
    while True:
        u, v = [rng.randint(-2, 2) for _ in range(2)], [rng.randint(-2, 2) for _ in range(2)]
        if any(u) and any(v):
            return tuple(a * b for a in u for b in v)


def main():
    widths = Counter()
    for left in product(range(4), repeat=3):
        for right in product(range(4), repeat=3):
            new_left, new_right, width = factor_helpers(left, right)
            need(width == rank_by_span(gram(left, right)), 'Independent exhaustive rank')
            need(len(new_left) == len(new_right) == 3 and
                 all(0 <= x < 1 << width for x in new_left + new_right), 'Compressed dimensions')
            need(rank_by_span(new_left) == rank_by_span(new_right) == width, 'Full rank factors')
            same_pairings(left, right, new_left, new_right)
            widths[width] += 1
    need(widths == {0: 274, 1: 2058, 2: 1764}, 'Independent rank distribution')

    # These 64 arbitrary legal three-call words need not have restored
    # endpoints, so this check does not apply the surplus bound to them.
    selected_words = {(73 * j + 19) % 4096 for j in range(64)}
    for number, (left, right) in enumerate(product(product(range(4), repeat=3), repeat=2)):
        if number not in selected_words:
            continue
        calls = [(a, 1 | (u << 1), (1 ^ dot(u, v)) | (v << 1))
                 for a, u, v in zip((E11, E22, ONES), left, right)]
        smaller, width = compress_calls(calls, 1, 3)
        need(formal_word(calls, 3)[0][0] == formal_word(smaller, 1 + width)[0][0],
             'Ordered data block preserved for an arbitrary endpoint')

    cases = [successful_control('no_data_cancelling_pair',
                                [(E11, 1, 1), (negative(E11), 1, 1)], [], 1)]
    for data in range(1, 4):
        for pairs in range(4):
            calls = [(E11, 1 << j, 1 << j) for j in range(data)]
            for j in range(pairs):
                x = 1 << (data + j)
                calls += [(E22, x, x), (negative(E22), x, x)]
            record = successful_control('sharp_cancellation_pairs', calls, [E11] * data, pairs)
            need(record['compressed_helpers'] == pairs == (len(calls) - data) // 2,
                 'Sharp surplus equality')
            cases.append(record)

    orthogonal = [(E11, 1, 1), (E22, 3, 5), (negative(E22), 3, 5)]
    record = successful_control('orthogonal_nonzero_helper_spans', orthogonal, [E11], 2)
    need((record['left_rank'], record['right_rank'], record['compressed_helpers']) == (1, 1, 0),
         'Zero paired rank despite two nonzero spans')
    cases.append(record)

    radical = [(E11, 1, 1), (E22, 2, 2), (negative(E22), 2, 2),
               (ONES, 6, 10), (negative(ONES), 6, 10)]
    record = successful_control('two_sided_radicals', radical, [E11], 3)
    need((record['left_rank'], record['right_rank'], record['compressed_helpers']) == (2, 2, 1),
         'Both invisible helper directions removed')
    cases.append(record)

    # These projectors commute by orthogonality despite mixing data and
    # helpers. The four-call commutator is a nonadjacent cancellation word.
    commutator = [(E11, 1, 1), (E22, 3, 5), (ONES, 5, 3),
                  (negative(E22), 3, 5), (negative(ONES), 5, 3)]
    record = successful_control('nonadjacent_mixed_commutator', commutator, [E11], 2)
    need(record['compressed_helpers'] == 2, 'Mixed sharp two-helper example')
    cases.append(record)

    rng = Random(SEED)
    random_widths = Counter()
    for trial in range(64):
        data, helpers, depth = rng.randint(1, 3), rng.randint(0, 5), rng.randint(1, 3)
        registers = data + helpers
        calls, targets = [], []
        for j in range(data):
            frame = random_frame(rng)
            calls.append((frame, 1 << j, 1 << j))
            target = frame
            if trial % 2:
                while True:
                    second = random_frame(rng)
                    candidate = add(frame, second)
                    if candidate[0] * candidate[3] != candidate[1] * candidate[2]:
                        break
                calls.append((second, 1 << j, 1 << j))
                target = candidate
            targets.append(target)
        nested = []
        for _ in range(depth):
            x = rng.randrange(1, 1 << registers)
            while True:
                y = rng.randrange(1, 1 << registers)
                if dot(x, y):
                    break
            nested.append((random_frame(rng), x, y))
        calls += nested + [(negative(a), x, y) for a, x, y in reversed(nested)]
        record = successful_control('seeded_nested_inverse', calls, targets, helpers)
        random_widths[record['compressed_helpers']] += 1

    controls = []
    expect_rejection('corrupted_scalar_pairing', lambda: same_pairings([1], [1], [1], [0]), controls)
    expect_rejection('wrong_idempotence', lambda: compress_calls([(E11, 1, 2)], 1, 2), controls)
    unrestored = [(E11, 1, 1), (E22, 2, 2)]
    _, unrestored_width = compress_calls(unrestored, 1, 2)
    need(unrestored_width == 1 > (len(unrestored) - 1) // 2, 'Restoration premise counterexample')
    expect_rejection('nonidentity_helper_endpoint',
                     lambda: successful_control('bad', unrestored, [E11], 1), controls)
    wrong_count = [(E22, 2, 2), (negative(E22), 2, 2)]
    _, wrong_width = compress_calls(wrong_count, 1, 2)
    need(wrong_width == 1 > (len(wrong_count) - 1) // 2, 'Identity data-count counterexample')
    expect_rejection('counted_identity_data_target',
                     lambda: successful_control('bad', wrong_count, [ZERO], 1), controls)
    mutated = [(E11, 1, 1), (E22, 2, 2), (E22, 2, 2)]
    expect_rejection('mutated_cleanup_frame',
                     lambda: successful_control('bad', mutated, [E11], 1), controls)
    zero_call = [(ZERO, 1, 1)]
    _, zero_width = compress_calls(zero_call, 0, 1)
    need(zero_width == 1 > len(zero_call) // 2 and ({ZERO} ^ {ZERO}) == set(),
         'Zero coefficient gives identity but destroys the surplus bound')
    expect_rejection('zero_address_update', lambda: formal_word(zero_call, 1), controls)

    # Preserving self-pairings alone is insufficient: the data blocks differ.
    two = [(E22, 3, 5), (ONES, 5, 3)]
    truncated = [(a, 1, 1) for a, _, _ in two]
    need(formal_word(two, 3)[0][0] != formal_word(truncated, 1)[0][0],
         'Self-pairing-only rejection control')
    controls.append('preserved_self_pairings_only')

    print(json.dumps({'status': 'PASS_RESTORED_HELPER_COMPRESSION',
                      'binary_factorizations': sum(widths.values()),
                      'paired_rank_histogram': dict(sorted(widths.items())),
                      'arbitrary_endpoint_data_block_checks': 64,
                      'structured_restored_word_checks': len(cases),
                      'seeded_nested_inverse_checks': 64,
                      'seed': SEED, 'random_width_histogram': dict(sorted(random_widths.items())),
                      'zero_pairing_example': next(c for c in cases if c['case'] == 'orthogonal_nonzero_helper_spans'),
                      'rejection_controls': controls,
                      'scope': 'Finite exact controls; the universal theorem is the written proof.'}, indent=2))


if __name__ == '__main__':
    main()
