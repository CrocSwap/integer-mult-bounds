"""Independent literal finite checks; not an all-field proof kernel.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
from runpy import run_path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
API = SimpleNamespace(**run_path(str(PACKAGE / 'core.py'), run_name='four_frame_core'))
FILES = ('README.md', 'PROOF.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'core.py', 'verify.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def action(a, vector, q):
    return tuple(sum(x * y for x, y in zip(row, vector, strict=True)) % q for row in a)


def literal_domain(q, n):
    vectors = tuple(product(range(q), repeat=n))
    index = {v: i for i, v in enumerate(vectors)}
    operators, group = {}, []
    for flat in product(range(q), repeat=n * n):
        matrix = tuple(flat[i * n:(i + 1) * n] for i in range(n))
        table = tuple(index[action(matrix, v, q)] for v in vectors)
        operators[table] = matrix
        if len(set(table)) == len(vectors):
            inverse = tuple(table.index(i) for i in range(len(vectors)))
            group.append((table, inverse))
    require(len(group) == { (2, 2): 6, (3, 2): 48, (2, 3): 168 }[q, n], 'literal GL group incomplete')
    return vectors, operators, group


def complete_orbits(q, n):
    vectors, operators, group = literal_domain(q, n)
    index = {v: i for i, v in enumerate(vectors)}
    unseen, profiles, rows = set(operators), set(), []
    histogram = Counter()
    for representative in sorted(operators):
        if representative not in unseen:
            continue
        realizers = {}
        for perm, inverse in group:
            image = tuple(perm[representative[inverse[i]]] for i in range(len(vectors)))
            realizers.setdefault(image, set()).add(perm)
        key = API.profile(operators[representative], q)
        require(key not in profiles, 'same primary invariant in different literal orbits')
        profiles.add(key)
        stabilizer = len(realizers[representative])
        require(len(realizers) * stabilizer == len(group), 'literal orbit-stabilizer mismatch')
        for image, expected in sorted(realizers.items()):
            target = operators[image]
            require(API.profile(target, q) == key, 'primary invariant changed within literal orbit')
            require(API.centralizer(target, q) == stabilizer, 'primary centralizer count mismatch')
            found = API.intertwiners(operators[representative], target, q)
            literal_found = {tuple(index[action(s, v, q)] for v in vectors) for s in found}
            require(len(found) == len(literal_found) and literal_found == expected,
                    'intertwiner solver differs from every literal realizing matrix')
            rows.append((target, key, len(expected)))
        histogram[stabilizer] += 1
        unseen.difference_update(realizers)
    require(not unseen, 'unclassified literal matrix')
    return {'q': q, 'r': n, 'operators': len(operators), 'GL': len(group), 'orbits': len(profiles),
            'stabilizer_histogram': {str(k): v for k, v in sorted(histogram.items())},
            'classification_sha256': sha256(json.dumps(sorted(rows), separators=(',', ':')).encode()).hexdigest()}


def companion(polynomial, q):
    n = len(polynomial) - 1
    return tuple(tuple(int(i == j + 1) if j < n - 1 else -polynomial[i] % q
                       for j in range(n)) for i in range(n))


def block(a, b):
    return tuple(tuple(row) + (0,) * len(b) for row in a) + tuple((0,) * len(a) + tuple(row) for row in b)


def binary_centralizer(a):
    """Independent all-matrix binary oracle: bit-vector actions, no elimination."""
    n = len(a)
    columns = tuple(sum(a[i][j] << i for i in range(n)) for j in range(n))
    def apply(cols, vector):
        value = 0
        for i in range(n):
            if vector & (1 << i):
                value ^= cols[i]
        return value
    count = 0
    for candidate in product(range(1 << n), repeat=n):
        if any(apply(columns, candidate[j]) != apply(candidate, columns[j]) for j in range(n)):
            continue
        span = {0}
        for column in candidate:
            span |= {v ^ column for v in tuple(span)}
        count += len(span) == 1 << n
    return count


def primary_controls():
    zero = ((0, 0, 0),) * 3
    j3 = ((0, 1, 0), (0, 0, 1), (0, 0, 0))
    j21 = ((0, 1, 0), (0, 0, 0), (0, 0, 0))
    cubic = companion((1, 1, 0, 1), 2)
    quadratic = companion((1, 1, 1), 2)
    quadratic_squared = companion((1, 0, 1, 0, 1), 2)
    repeated = block(quadratic, quadratic)
    j2 = ((0, 1), (0, 0))
    fixtures = [('scalar_zero', zero, 168), ('nilpotent_J3', j3, 4),
                ('nilpotent_J2_J1', j21, 8), ('irreducible_cubic', cubic, 7),
                ('irreducible_squared', quadratic_squared, 12), ('repeated_irreducible', repeated, 180),
                ('repeated_nilpotent', block(j2, j2), 96),
                ('mixed_primary', block(j2, ((1, 1), (0, 1))), 4)]
    result = []
    for name, a, expected in fixtures:
        literal = binary_centralizer(a)
        require(literal == expected == API.centralizer(a, 2) == len(API.intertwiners(a, a, 2)),
                'nonsemisimple or mixed-primary count failed: ' + name)
        result.append({'name': name, 'r': len(a), 'count': expected, 'profile': API.profile(a, 2)})
    require(API.characteristic(quadratic_squared, 2) == API.characteristic(repeated, 2), 'charpoly control differs')
    require(API.profile(quadratic_squared, 2) != API.profile(repeated, 2), 'primary partitions lost')
    require(not API.complete(API.identity(4), quadratic_squared, API.identity(4), repeated, 2)['compatible'],
            'same-characteristic nonsemisimple graphs accepted')
    require(API.characteristic(zero, 2) == API.characteristic(j3, 2) and
            not API.complete(API.identity(3), zero, API.identity(3), j3, 2)['compatible'],
            'nilpotent characteristic-only control accepted')
    return result


def graph_frames(left, fourth, q, unused=0):
    n, tail = len(left), (0,) * unused
    vectors = tuple(product(range(q), repeat=n))
    zero = (0,) * n
    return (frozenset(x + zero + tail for x in vectors), frozenset(zero + x + tail for x in vectors),
            frozenset(x + action(left, x, q) + tail for x in vectors),
            frozenset(x + action(fourth, x, q) + tail for x in vectors))


def incidence(frames, q):
    result = []
    for mask in range(1, 16):
        selected = [frames[i] for i in range(4) if mask & (1 << i)]
        intersection, total = set(selected[0]), {(0,) * len(next(iter(selected[0])))}
        for frame in selected:
            intersection &= frame
            total = {tuple((a + b) % q for a, b in zip(x, y, strict=True)) for x in total for y in frame}
        result.append((len(intersection), len(total)))
    return result


def verify_images(source, target, g, q):
    require(all(frozenset(action(g, x, q) for x in a) == b for a, b in zip(source, target, strict=True)),
            'constructed map fails one of the four ordered graph images')
    vectors = tuple(product(range(q), repeat=len(g)))
    require(len({action(g, x, q) for x in vectors}) == len(vectors), 'constructed ambient map not invertible')


def geometry_controls():
    t = companion((1, 1, 0, 1), 2)
    other = companion((1, 0, 1, 1), 2)
    i = API.identity(3)
    first, second = graph_frames(i, t, 2, 3), graph_frames(i, other, 2, 3)
    require(incidence(first, 2) == incidence(second, 2), 'incidence-only counterexample lost')
    require(all(len(a & b) == 1 for frames in (first, second) for a, b in combinations(frames, 2)),
            'binary cubic graph frames not pairwise complementary')
    require(not API.complete(i, t, i, other, 2, unused=3)['compatible'], 'dimension-only incompatibility lost')
    same = API.complete(i, t, i, t, 2, unused=3)
    require(same['active_realizers'] == 7 and same['ambient_realizers'] == 7 * 2 ** 18 * 168,
            'unused-complement realization multiplier lost')
    verify_images(first, first, same['map'], 2)
    left = ((1, 1, 0), (0, 1, 1), (0, 0, 1))
    target_left = ((0, 1, 0), (0, 0, 1), (1, 0, 0))
    s0 = ((1, 0, 1), (0, 1, 0), (0, 0, 1))
    target_t = API.multiply(API.multiply(s0, t, 2), API.inverse(s0, 2), 2)
    fourth, target_fourth = API.multiply(left, t, 2), API.multiply(target_left, target_t, 2)
    shear = tuple(tuple((j + 2 * k) % 3 == 0 for j in range(3)) for k in range(6))
    shear = tuple(tuple(int(x) for x in row) for row in shear)
    result = API.complete(left, fourth, target_left, target_fourth, 2, unused=3,
                          shear=shear, complement=target_left)
    verify_images(graph_frames(left, fourth, 2, 3), graph_frames(target_left, target_fourth, 2, 3), result['map'], 2)
    require(result['active_realizers'] == 7 and result['ambient_realizers'] == same['ambient_realizers'],
            'normalization changed the realization count')
    j3 = ((0, 1, 0), (0, 0, 1), (0, 0, 0))
    singular = API.complete(i, j3, i, j3, 2)
    verify_images(graph_frames(i, j3, 2), graph_frames(i, j3, 2), singular['map'], 2)
    ternary = ((1, 1), (0, 2))
    source = ((1, 0), (0, 2))
    directed = API.complete(API.identity(2), source, API.identity(2), ternary, 3)
    verify_images(graph_frames(API.identity(2), source, 3), graph_frames(API.identity(2), ternary, 3), directed['map'], 3)
    empty = API.complete((), (), (), (), 2, unused=3)
    require(empty['active_realizers'] == 1 and empty['ambient_realizers'] == 168, 'zero active space lost')
    return {'binary_cubic_incidence_sizes': incidence(first, 2), 'binary_cubic_incompatible': True,
            'native_ambient_dimension': 9, 'native_self_realizers': same['ambient_realizers'],
            'nonidentity_graphs_and_ambient_shear': True, 'singular_fourth_allowed': True,
            'directed_ternary_images': True, 'empty_active_complement': 168}


def rejection_controls():
    i, z = API.identity(1), ((0,),)
    calls = [lambda: API.matrix(((True,),), 2), lambda: API.matrix(((2,),), 2),
             lambda: API.matrix(((0, 1),), 2), lambda: API.matrix(API.identity(5), 2),
             lambda: API.complete(i, i, i, i, True), lambda: API.complete(i, i, i, i, 4),
             lambda: API.complete(z, i, i, i, 2), lambda: API.complete(i, i, z, i, 2),
             lambda: API.complete(i, i, API.identity(2), API.identity(2), 2),
             lambda: API.complete(i, i, i, i, 2, unused=True),
             lambda: API.complete(i, i, i, i, 2, unused=-1),
             lambda: API.complete(i, i, i, i, 2, unused=8),
             lambda: API.complete(i, i, i, i, 2, unused=1, shear=((0,),)),
             lambda: API.complete(i, i, i, i, 2, unused=1, shear=((True,), (0,))),
             lambda: API.complete(i, i, i, i, 2, unused=1, complement=((0,),)),
             lambda: API.intertwiners(((0, 0, 0, 0),) * 4, ((0, 0, 0, 0),) * 4, 2)]
    for call in calls:
        try:
            call()
        except ValueError:
            continue
        raise ValueError('invalid input or reference-bound violation accepted')
    five = API.complete(i, z, i, z, 5)
    require(five['active_realizers'] == 4, 'prime-five positive control failed')
    return {'invalid_inputs_rejected': len(calls), 'prime_five_scalar_realizers': 4}


def bindings():
    root = PACKAGE.parents[1]
    sources = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    result = {}
    for row in sources['files']:
        if row['usage'] == 'input':
            digest = sha256((root / row['path']).read_bytes()).hexdigest()
            require(digest == row['sha256'], 'changed source input: ' + row['path'])
            result[row['path']] = digest
    return result


def receipt():
    return {'schema': 'four-frame-shared-map/1', 'claim_type': 'scoped-proof-with-finite-corroboration',
            'files': {name: sha256((PACKAGE / name).read_bytes()).hexdigest() for name in FILES},
            'source_inputs': bindings(), 'domains': [complete_orbits(2, 2), complete_orbits(3, 2), complete_orbits(2, 3)],
            'primary_controls': primary_controls(), 'geometry': geometry_controls(), 'rejections': rejection_controls()}


def canonical(value):
    # JSON encodings retain bool/int distinctions, unlike Python's True == 1.
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    expected = receipt()
    if args.write:
        with args.write.open('x', encoding='utf-8') as out:
            out.write(json.dumps(expected, indent=2) + '\n')
    else:
        actual = json.loads((PACKAGE / 'RESULT.json').read_bytes())
        require(canonical(actual) == canonical(expected), 'typed receipt differs from exact recomputation')
    print('PASS_FOUR_FRAME_SHARED_MAP', canonical({'operators': sum(d['operators'] for d in expected['domains']),
          'orbits': sum(d['orbits'] for d in expected['domains']), 'primary_fixtures': len(expected['primary_controls']),
          'native_self_realizers': expected['geometry']['native_self_realizers']}))


if __name__ == '__main__':
    main()
