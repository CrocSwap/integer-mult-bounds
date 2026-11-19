"""Check the three-relation word obstruction for the four-projector pool.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
from itertools import combinations, product
import json
from math import factorial
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PAIRS = ((1, 3), (3, 2), (5, 9), (11, 6))
SUPPORTS = tuple((tuple(i for i in range(4) if u >> i & 1),
                  tuple(i for i in range(4) if v >> i & 1)) for u, v in PAIRS)
NONCOMMUTING = ((0, 2), (1, 2), (1, 3), (2, 3))


def require(value, message):
    if not value:
        raise ArithmeticError(message)


def xor_all(values):
    result = 0
    for value in values:
        result ^= value
    return result


def matrix(pair):
    u, v = pair
    return sum((u >> i & v >> j & 1) << (4 * i + j)
               for i in range(4) for j in range(4))


def multiply(a, b):
    return sum((sum(a >> (4 * i + k) & b >> (4 * k + j) & 1 for k in range(4)) % 2)
               << (4 * i + j) for i in range(4) for j in range(4))


def off(a):
    return a & ~sum(1 << (5 * i) for i in range(4))


def basis(values):
    result = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in result:
                result[pivot] = value
                break
            value ^= result[pivot]
    return result


def check_alphabet():
    matrices = list(map(matrix, PAIRS))
    require(all(multiply(p, p) == p for p in matrices), 'idempotents')
    require(multiply(matrices[0], matrices[1]) == multiply(matrices[1], matrices[0]) == 0,
            'P and Q are orthogonal')
    require(multiply(matrices[0], matrices[3]) == multiply(matrices[3], matrices[0]) == 0,
            'P and S are orthogonal')
    patterns = [off(matrices[i]) for i in (0, 2, 3)]
    require(off(matrices[1]) == patterns[0], 'P/Q common pattern')
    commutators = [off(multiply(matrices[i], matrices[j]) ^ multiply(matrices[j], matrices[i]))
                   for i, j in NONCOMMUTING]
    rows = patterns + commutators
    require(len(basis(rows)) == 7, 'four independent commutators modulo patterns')
    for mask in range(1, 128):
        require(xor_all(row for i, row in enumerate(rows) if mask >> i & 1) != 0,
                'independent seven-row certificate')
    for private, writer in ((2, 2), (3, 3)):
        require([i for i, (u, _) in enumerate(PAIRS) if u >> private & 1] == [writer],
                'unique private writer')
        require(PAIRS[writer][1] & ~(1 << private), 'writer reads outside its private coordinate')
    return {'rows': rows, 'echelon_rows': [basis(rows)[p] for p in sorted(basis(rows), reverse=True)],
            'rank': 7, 'nonempty_subsets': 127}


def words(counts):
    remaining = list(counts)

    def visit(prefix):
        if not any(remaining):
            yield tuple(prefix)
            return
        for kind in range(4):
            if remaining[kind]:
                remaining[kind] -= 1
                prefix.append(kind)
                yield from visit(prefix)
                prefix.pop()
                remaining[kind] += 1

    return visit([])


def position_words(counts):
    n = sum(counts)
    positions = set(range(n))
    for p in combinations(range(n), counts[0]):
        after_p = positions - set(p)
        for q in combinations(sorted(after_p), counts[1]):
            after_q = after_p - set(q)
            for r in combinations(sorted(after_q), counts[2]):
                word = [3] * n
                for kind, selected in enumerate((p, q, r)):
                    for index in selected:
                        word[index] = kind
                yield tuple(word)


def good_order(word):
    r = [i for i, kind in enumerate(word) if kind == 2]
    s = [i for i, kind in enumerate(word) if kind == 3]
    if any(word[i] in (0, 1) for i in range(r[0] + 1, r[-1])):
        return False
    if any(word[i] == 1 for i in range(s[0] + 1, s[-1])):
        return False
    projection = [kind for kind in word if kind in (2, 3)]
    return 1 + sum(a != b for a, b in zip(projection, projection[1:])) <= 3


def labels_for_counts(counts):
    dimension = sum(counts) - 3
    unit = lambda i: tuple(int(j == i) for j in range(dimension))
    next_axis = 1
    labels = []
    free = []
    for kind, count in enumerate(counts):
        row = [unit(i) for i in range(next_axis, next_axis + count - 1)]
        free.extend(row)
        next_axis += count - 1
        total = unit(0) if kind < 2 else (0,) * dimension
        row.append(tuple(total[i] - sum(v[i] for v in row) for i in range(dimension)))
        labels.append(row)
    require(free == [unit(i) for i in range(1, dimension)], 'paid private unit basis')
    require(tuple(sum(v[i] for v in labels[0]) for i in range(dimension)) == unit(0),
            'paid common unit recovered over integers')
    require(all(any(v) for row in labels for v in row), 'nonzero paid vectors')
    return labels


def ordered_labels(word, labels):
    indices = [0] * 4
    result = []
    for kind in word:
        result.append(labels[kind][indices[kind]])
        indices[kind] += 1
    return result


def degree_two(word, vectors):
    dimension = len(vectors[0])
    masks = [sum((value & 1) << i for i, value in enumerate(v)) for v in vectors]
    prefix = [0] * 4
    result = [0] * 4
    for kind, mask in zip(word, masks):
        for index, (left, right) in enumerate(NONCOMMUTING):
            if kind != left:
                continue
            for i in range(dimension):
                if mask >> i & 1:
                    for j in range(dimension):
                        if prefix[right] >> j & 1:
                            result[index] ^= 1 << (min(i, j) * dimension + max(i, j))
        prefix[kind] ^= mask
    return result


def encoded_product(word, exponents):
    offset = sum(-x for x in exponents if x < 0)
    one = 1 << offset
    rows = [[one if i == j else 0 for j in range(4)] for i in range(4)]
    for kind, exponent in zip(word, exponents):
        image, covector = SUPPORTS[kind]
        for column in range(4):
            donor = xor_all(rows[row][column] for row in covector)
            shifted = donor << exponent if exponent >= 0 else donor >> -exponent
            require(exponent >= 0 or shifted << -exponent == donor, 'Laurent shift')
            delta = shifted ^ donor
            for row in image:
                rows[row][column] ^= delta
    return rows, offset


def sparse_product(word, vectors):
    zero = (0,) * len(vectors[0])
    rows = [[{zero} if i == j else set() for j in range(4)] for i in range(4)]
    for kind, exponent in zip(word, vectors):
        u, v = PAIRS[kind]
        factor = [[({zero} if i == j else set()) ^
                   ({zero, exponent} if u >> i & v >> j & 1 else set())
                   for j in range(4)] for i in range(4)]
        result = [[set() for _ in range(4)] for _ in range(4)]
        for i, j, k in product(range(4), repeat=3):
            for a in factor[i][k]:
                for b in rows[k][j]:
                    value = tuple(x + y for x, y in zip(a, b))
                    if value in result[i][j]:
                        result[i][j].remove(value)
                    else:
                        result[i][j].add(value)
        rows = result
    return rows


def check_words():
    records = []
    sparse_checks = 0
    for n in range(6, 10):
        for counts in product(range(1, n), repeat=4):
            if sum(counts) != n or min(counts[2:]) < 2:
                continue
            orders = list(words(counts))
            expected = factorial(n)
            for count in counts:
                expected //= factorial(count)
            require(len(orders) == expected and set(orders) == set(position_words(counts)),
                    'independent order coverage')
            labels = labels_for_counts(counts)
            dimension = n - 3
            powers = [3 ** i for i in range(dimension)]
            digest = sha256()
            passing = 0
            for index, word in enumerate(orders):
                vectors = ordered_labels(word, labels)
                expected_diagonal = good_order(word)
                require((not any(degree_two(word, vectors))) == expected_diagonal,
                        'quadratic chronology equivalence')
                exponents = [sum(a * b for a, b in zip(v, powers)) for v in vectors]
                rows, offset = encoded_product(word, exponents)
                diagonal = all(not rows[i][j] for i in range(4) for j in range(4) if i != j)
                require(diagonal == expected_diagonal, 'full word classification')
                if diagonal:
                    require([rows[i][i] for i in range(4)] ==
                            [1 << (offset + 1), 1 << (offset + 1), 1 << offset, 1 << offset],
                            'two productive labels and two identities')
                    passing += 1
                digest.update(json.dumps(rows, separators=(',', ':')).encode() + b'\n')
                if index in {0, 1, len(orders) // 3, len(orders) // 2, len(orders) - 1}:
                    sparse = sparse_product(word, vectors)
                    encoded = [[sum(1 << (offset + sum(a * b for a, b in zip(v, powers)))
                                    for v in entry) for entry in row] for row in sparse]
                    require(rows == encoded, 'independent multivariate product')
                    sparse_checks += 1
            records.append({'multiplicities': list(counts), 'paid_rank': dimension,
                            'relations': 3, 'orders': len(orders), 'diagonal': passing,
                            'full_matrix_sha256': digest.hexdigest()})
    return {'domains': records, 'words': sum(r['orders'] for r in records),
            'diagonal': sum(r['diagonal'] for r in records), 'sparse_products': sparse_checks}


def check_controls():
    writer_cases = 0
    for writer in (2, 3):
        others = tuple(i for i in range(4) if i != writer)
        for length in range(4):
            for prefix in product(others, repeat=length):
                for label in (-2, -1, 1, 2, 4):
                    word = prefix + (writer,) + prefix[::-1]
                    exponents = (1,) * length + (label,) + (-1,) * length
                    rows, _ = encoded_product(word, exponents)
                    require(any(rows[writer][j] for j in range(4) if j != writer),
                            'single private writer cannot return a diagonal row')
                    writer_cases += 1
    word = (0, 1, 2, 2, 3, 3)
    labels = labels_for_counts((1, 1, 2, 2))
    vectors = ordered_labels(word, labels)
    powers = (1, 5, 25)
    for changed in (1, 3, 5):
        mutant = list(vectors)
        mutant[changed] = (mutant[changed][0] + 2, *mutant[changed][1:])
        require(not any(degree_two(word, mutant)), 'even mutation keeps degree two')
        rows, offset = encoded_product(word, [sum(a * b for a, b in zip(v, powers)) for v in mutant])
        sparse = sparse_product(word, mutant)
        encoded = [[sum(1 << (offset + sum(a * b for a, b in zip(v, powers)))
                        for v in entry) for entry in row] for row in sparse]
        require(rows == encoded, 'independent exact fault product')
        require(any(rows[i][j] for i in range(4) for j in range(4) if i != j),
                'exact endpoint rejects even total mutation')
    return {'unique_writer_words': writer_cases,
            'even_total_faults': ['Q total', 'R total', 'S total']}


def source_replay():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        data = (ROOT / pin['retained']).read_bytes()
        require(sha256(data).hexdigest() == pin['sha256'], 'retained SHA256')
        require(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == pin['git_blob'], 'retained Git blob')
    command = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
               '-B', str(ROOT / 'retained/maximizer/verify.py')]
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    require('PASS_EVEN_ONE_EDGE_MAXIMIZER' in result.stdout, 'unchanged geometry replay')
    return len(pins)


def collect():
    return {'source_files': source_replay(), 'alphabet': check_alphabet(),
            'words': check_words(), 'controls': check_controls()}


def main():
    actual = collect()
    require(actual == json.loads((ROOT / 'RESULT.json').read_text()), 'saved certificate')
    print('PASS_ONE_EDGE_WORD_OBSTRUCTION')
    print('35 multiplicity domains; 108904 type orders; exact degree-two and full Laurent checks')
    print(f"{actual['words']['diagonal']} diagonal endpoints; 175 independent sparse products; 400 unique-writer controls")
    print('All-length three-relation classification: exact R/S cancellation and endpoint diag([u],[u],1,1)')


if __name__ == '__main__':
    main()
