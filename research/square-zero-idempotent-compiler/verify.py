"""Exact square-zero compiler checks; standard library, no generated files.

Produced by Nick Petalas. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path


MAX_WIDTH = 20


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(1 << i for i in range(n))


def rank(rows):
    pivots = {}
    for original in rows:
        value = original
        for bit in range(MAX_WIDTH * 2 - 1, -1, -1):
            if value & (1 << bit):
                if bit in pivots:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return len(pivots)


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a, b):
    n = len(a)
    require(len(b) == n <= MAX_WIDTH * 2, 'matrix width')
    return tuple(xor_selected(row, b) for row in a)


def xor_selected(mask, vectors):
    value = 0
    for i, vector in enumerate(vectors):
        if mask & (1 << i):
            value ^= vector
    return value


def columns(rows):
    n = len(rows)
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows))
                 for j in range(n))


def inverse(rows):
    n = len(rows)
    work = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if work[i] & (1 << j)), None)
        require(pivot is not None, 'singular basis')
        work[j], work[pivot] = work[pivot], work[j]
        for i in range(n):
            if i != j and work[i] & (1 << j):
                work[i] ^= work[j]
    require(tuple(row & ((1 << n) - 1) for row in work) == identity(n),
            'inverse elimination')
    return tuple(row >> n for row in work)


def coordinates(vector, basis):
    work = [(value, 1 << i) for i, value in enumerate(basis)]
    pivots = {}
    for value, label in work:
        for bit in range(MAX_WIDTH - 1, -1, -1):
            if value & (1 << bit):
                if bit in pivots:
                    other, coefficient = pivots[bit]
                    value ^= other
                    label ^= coefficient
                else:
                    pivots[bit] = (value, label)
                    break
    result = 0
    for bit in range(MAX_WIDTH - 1, -1, -1):
        if vector & (1 << bit):
            require(bit in pivots, 'outside image span')
            value, label = pivots[bit]
            vector ^= value
            result ^= label
    require(vector == 0, 'coordinate residual')
    return result


def jordan_basis(matrix):
    n = len(matrix)
    image, preimages = [], []
    cols = columns(matrix)
    for j, vector in enumerate(cols):
        if rank(image + [vector]) > len(image):
            image.append(vector)
            preimages.append(1 << j)
    q = len(image)
    basis = image + preimages
    require(rank(basis) == 2 * q, 'Jordan chain independence')
    for j, vector in enumerate(cols):
        kernel = (1 << j) ^ xor_selected(coordinates(vector, image), preimages)
        if rank(basis + [kernel]) > len(basis):
            basis.append(kernel)
    require(len(basis) == n, 'Jordan basis completeness')
    change = columns(tuple(basis))
    undo = inverse(change)
    canonical = tuple((1 << (q + i)) if i < q else 0 for i in range(n))
    require(multiply(multiply(undo, matrix), change) == canonical,
            'Jordan conjugation')
    return q, change, undo


def outer(u, v, n):
    return tuple(v if u & (1 << i) else 0 for i in range(n))


def canonical_projectors(q, n):
    groups = [tuple(range(q))] if q % 2 else [tuple(range(q - 1)), (q - 1,)]
    result = []
    for group in groups:
        functional = sum(1 << i for i in group)
        for i in group:
            result.append(outer(1 << i, functional ^ (1 << (q + i)), n))
        result.append(outer(functional, functional, n))
    return result


def compile_matrix(matrix):
    n = len(matrix)
    require(1 <= n <= MAX_WIDTH and all(0 <= row < (1 << n) for row in matrix),
            'binary matrix boundary')
    require(not any(multiply(matrix, matrix)), 'coupling must be square-zero')
    if not any(matrix):
        return []
    q, change, undo = jordan_basis(matrix)
    result = [multiply(multiply(change, p), undo)
              for p in canonical_projectors(q, n)]
    require(len(result) == q + 1 + (q % 2 == 0), 'optimal length')
    total = (0,) * n
    for projector in result:
        require(rank(projector) == 1 and multiply(projector, projector) == projector,
                'legal rank-one projector')
        total = add(total, projector)
    require(total == matrix, 'projector sum')
    return result


def formal_product(projectors, n):
    zero = (0,) * n
    a, b = identity(n), zero
    for p in projectors:
        c = add(identity(n), p)
        a, b = add(multiply(c, a), multiply(p, b)), add(multiply(p, a), multiply(c, b))
    return a, b


def regular_action(projectors, n, period=2):
    """Literal address rotation, using neither formal convolution nor its output."""
    result = []
    mask = (1 << period) - 1
    for column in range(n * period):
        state = [0] * n
        state[column // period] = 1 << (column % period)
        for p in projectors:
            read = [xor_selected(row, state) for row in p]
            for i in range(n):
                rotated = ((read[i] << 1) & mask) | (read[i] >> (period - 1))
                state[i] ^= read[i] ^ rotated
        result.append(tuple(state))
    return tuple(result)


def desired_action(matrix, period=2):
    n = len(matrix)
    result = []
    for column in range(n * period):
        role, address = divmod(column, period)
        state = [0] * n
        state[role] = 1 << address
        for i, row in enumerate(matrix):
            if row & (1 << role):
                state[i] ^= (1 << address) ^ (1 << ((address + 1) % period))
        result.append(tuple(state))
    return tuple(result)


def unpack(value, n):
    return tuple((value >> (n * i)) & ((1 << n) - 1) for i in range(n))


def pack(rows):
    n = len(rows)
    return sum(row << (n * i) for i, row in enumerate(rows))


def shortest_sums(n):
    size = 1 << (n * n)
    projectors = sorted({pack(outer(u, v, n)) for u in range(1, 1 << n)
                         for v in range(1, 1 << n) if (u & v).bit_count() % 2})
    distances = [-1] * size
    distances[0] = 0
    queue = [0]
    for index in range(size):
        require(index < len(queue), 'projectors do not span matrix space')
        value = queue[index]
        for p in projectors:
            target = value ^ p
            if distances[target] < 0:
                distances[target] = distances[value] + 1
                queue.append(target)
    require(len(queue) == size, 'shortest-path coverage')
    return distances


def exhaustive_checks():
    counts = {'binary_matrices': 0, 'square_zero': 0, 'rank_two_minimum_four': 0,
              'formal_endpoints': 0, 'regular_columns': 0}
    for n in range(1, 5):
        distances = shortest_sums(n)
        for value, distance in enumerate(distances):
            counts['binary_matrices'] += 1
            matrix = unpack(value, n)
            if any(multiply(matrix, matrix)):
                continue
            q = rank(matrix)
            expected = q + 1 + (q % 2 == 0) if q else 0
            require(distance == expected, 'independent shortest-sum minimum')
            counts['square_zero'] += 1
            counts['rank_two_minimum_four'] += q == 2 and distance == 4
            projectors = compile_matrix(matrix)
            require(formal_product(projectors, n) == (add(identity(n), matrix), matrix),
                    'full formal endpoint')
            require(regular_action(projectors, n) == desired_action(matrix),
                    'regular arbitrary-input columns')
            counts['formal_endpoints'] += 1
            counts['regular_columns'] += 2 * n
    return counts


def larger_checks():
    counts = {'larger_endpoints': 0, 'larger_regular_columns': 0, 'omission_controls': 0}
    for q in range(1, 9):
        n = 2 * q + 2
        canonical = tuple((1 << (q + i)) if i < q else 0 for i in range(n))
        change = list(identity(n))
        for i in range(n):
            change[i] ^= change[(i + 1) % n]
        undo = inverse(tuple(change))
        matrix = multiply(multiply(tuple(change), canonical), undo)
        projectors = compile_matrix(matrix)
        require(formal_product(projectors, n) == (add(identity(n), matrix), matrix),
                'conjugated full formal endpoint')
        require(regular_action(projectors, n) == desired_action(matrix),
                'conjugated full dirty action')
        counts['larger_endpoints'] += 1
        counts['larger_regular_columns'] += 2 * n
        for i in range(len(projectors)):
            omitted = projectors[:i] + projectors[i + 1:]
            require(formal_product(omitted, n) != (add(identity(n), matrix), matrix),
                    'omitted reflection must fail')
            counts['omission_controls'] += 1
    return counts


def boundary_controls():
    for bad in [(1,), (2, 1)]:
        try:
            compile_matrix(bad)
        except ValueError:
            pass
        else:
            raise ValueError('non-square-zero input accepted')
    n, q = 8, 3
    matrix = tuple((1 << (q + i)) if i < q else 0 for i in range(n))
    projectors = compile_matrix(matrix)
    require(len(projectors) == 4 < 2 * q, 'first strict improvement')
    require(regular_action(projectors, n, 3) != desired_action(matrix, 3),
            'noninvolutory-label control')
    mutant = list(matrix)
    mutant[0] ^= 1 << (n - 1)
    require(desired_action(tuple(mutant)) != desired_action(matrix),
            'dirty-input-only leakage')
    return {'boundary_controls': 4, 'rank_three_calls': len(projectors),
            'rank_three_factorwise_calls': 2 * q}


def source_hashes():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    manifest = json.loads((package / 'SOURCES.json').read_text())
    hashes = {}
    for item in manifest['files']:
        if item['usage'] == 'input':
            data = (root / item['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == item['sha256'], 'source SHA256')
            blob = b'blob ' + str(len(data)).encode() + b'\0' + data
            require(hashlib.sha1(blob).hexdigest() == item['git_blob'], 'source Git blob')
            hashes[item['path']] = item['sha256']
    for path in sorted(package.iterdir()):
        if path.is_file():
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    hashes = source_hashes()
    result = exhaustive_checks() | larger_checks() | boundary_controls()
    result['file_sha256'] = hashes
    print(json.dumps(result, sort_keys=True))
    print('PASS_SQUARE_ZERO_IDEMPOTENT_COMPILER rank3=4 previous=6 no_new_kappa')


if __name__ == '__main__':
    main()
