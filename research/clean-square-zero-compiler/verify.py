"""Clean square-zero compiler. JoyboyBrian, with OpenAI Codex; Apache-2.0."""
import argparse
import hashlib
import json
import random
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def rank(vectors):
    basis = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in basis:
                basis[bit] = value
                break
            value ^= basis[bit]
    return len(basis)


def apply(matrix, vector):
    return sum(parity(row & vector) << i for i, row in enumerate(matrix))


def columns(matrix):
    return tuple(apply(matrix, 1 << i) for i in range(len(matrix)))


def transpose(vectors):
    return tuple(sum(((value >> i) & 1) << j for j, value in enumerate(vectors))
                 for i in range(len(vectors)))


def matrix_product(left, right):
    return transpose(tuple(apply(left, col) for col in columns(right)))


def matrix_input(matrix):
    need(isinstance(matrix, (tuple, list)), 'matrix container')
    n = len(matrix)
    need(1 <= n <= 32, 'verifier matrix width must be 1..32')
    need(all(type(row) is int and 0 <= row < (1 << n) for row in matrix),
         'binary row encoding')
    need(all(apply(matrix, col) == 0 for col in columns(matrix)),
         'matrix is not square-zero')


def chain_basis(matrix):
    image, preimages, kernel, elimination = [], [], [], {}
    for j, col in enumerate(columns(matrix)):
        value, pre = col, 1 << j
        while value:
            bit = value.bit_length() - 1
            if bit not in elimination:
                elimination[bit] = (value, pre)
                image.append(col)
                preimages.append(1 << j)
                break
            other, label = elimination[bit]
            value ^= other
            pre ^= label
        if not value:
            kernel.append(pre)
    q = len(image)
    basis = image + preimages
    need(rank(basis) == 2 * q, 'chain independence')
    for vector in kernel:
        if rank(basis + [vector]) > len(basis):
            basis.append(vector)
    need(len(basis) == len(matrix), 'complete chain basis')
    return q, transpose(tuple(basis))


def reduce_basis(matrix):
    """Return literal scalar CNOTs whose product is matrix inverse."""
    rows, gates = list(matrix), []
    for j in range(len(rows)):
        pivot = next((i for i in range(j, len(rows)) if rows[i] & (1 << j)), None)
        need(pivot is not None, 'singular basis')
        if pivot != j:
            for dest, source in ((j, pivot), (pivot, j), (j, pivot)):
                rows[dest] ^= rows[source]
                gates.append(('xor', dest, source))
        for i in range(len(rows)):
            if i != j and rows[i] & (1 << j):
                rows[i] ^= rows[j]
                gates.append(('xor', i, j))
    need(rows == [1 << i for i in range(len(rows))], 'basis reduction')
    return gates


def odd_projectors(indices, q):
    mask = sum(1 << i for i in indices)
    result = [(1 << i, mask | (1 << (q + i)), i) for i in indices]
    result.append((mask, mask, indices[0]))
    return result


def canonical_projectors(q, n, clean=True):
    if q == 0:
        return []
    if q & 1:
        return odd_projectors(list(range(q)), q)
    if not clean:
        return odd_projectors(list(range(q - 1)), q) + odd_projectors([q - 1], q)
    h = 1 << n
    sources = ((1 << q) - 1) << q
    result = [((1 << i) | h, (sources ^ (1 << (q + i))) | h, n)
              for i in range(q)]
    result.append((((1 << q) - 1) | h, sources | h, n))
    return result


def projector_sum(projectors, width):
    rows = [0] * width
    for x, y, pivot in projectors:
        need(x and y and parity(x & y) == 1, 'non-idempotent call')
        need(((x & y) >> pivot) & 1, 'invalid reflection pivot')
        for i in range(width):
            if x & (1 << i):
                rows[i] ^= y
    return tuple(rows)


def lower_projectors(projectors, width):
    gates = []
    for x, y, pivot in projectors:
        need(parity(x & y) == 1 and ((x & y) >> pivot) & 1, 'lowering contract')
        b = [('xor', i, pivot) for i in range(width) if i != pivot and x & (1 << i)]
        a = [('xor', pivot, i) for i in range(width) if i != pivot and y & (1 << i)]
        gates.extend(b + a + [('reflect', pivot)] + list(reversed(a)) + list(reversed(b)))
    return gates


def compile_matrix(matrix):
    matrix_input(matrix)
    n = len(matrix)
    q, basis = chain_basis(matrix)
    changes = reduce_basis(basis)
    projectors = canonical_projectors(q, n)
    # shortcut: verifier emits finite-width words; the uniform proof is in PROOF.md.
    gates = changes + lower_projectors(projectors, n + 1) + list(reversed(changes))
    return q, basis, projectors, gates, len(changes)


def check_matrix(matrix):
    q, basis, projectors, gates, transport = compile_matrix(matrix)
    n = len(matrix)
    canonical = tuple((1 << (q + i)) if i < q else 0 for i in range(n))
    need(matrix_product(matrix, basis) == matrix_product(basis, canonical),
         'source-bound chain similarity')
    expected = canonical + ((1 << n) if q and not q & 1 else 0,)
    need(projector_sum(projectors, n + 1) == expected, 'full canonical formal endpoint')
    need(len(projectors) == (q + 1 if q else 0), 'clean reflection count')
    return q, gates, transport


def shortest_clean_checks():
    reports = []
    for q in (1, 2):
        data, width = 2 * q, 2 * q + 1
        endpoints = set()
        for x in range(1, 1 << width):
            for y in range(1 << width):
                if parity(x & y):
                    value = sum(((y & ((1 << data) - 1)) if x >> i & 1 else 0)
                                << (data * i) for i in range(width))
                    endpoints.add(value)
        target = sum((1 << (q + i)) << (data * i) for i in range(q))
        need(target not in endpoints, 'one-call clean obstruction')
        if q == 2:
            need(not any((target ^ p) in endpoints for p in endpoints),
                 'two-call clean obstruction')
        reports.append({'rank': q, 'all_projected_single_calls': len(endpoints),
                        'shorter_than': q + 1})
    return reports


def all_small_matrices():
    count = 0
    by_rank = {}
    for n in range(1, 5):
        for bits in range(1 << (n * n)):
            matrix = tuple((bits >> (n * i)) & ((1 << n) - 1) for i in range(n))
            if any(apply(matrix, col) for col in columns(matrix)):
                continue
            q, _, _ = check_matrix(matrix)
            count += 1
            by_rank[str(q)] = by_rank.get(str(q), 0) + 1
    return {'matrices': count, 'ranks': by_rank}


def larger_matrices():
    cases, rows = 0, []
    for q in range(1, 9):
        n = 2 * q + 2
        base = tuple((1 << (q + i)) if i < q else 0 for i in range(n))
        transform = [1 << i for i in range(n)]
        rng = random.Random(900 + q)
        for _ in range(n * 5):
            dest, source = rng.sample(range(n), 2)
            transform[dest] ^= transform[source]
        reduction = reduce_basis(tuple(transform))
        inverse = [1 << i for i in range(n)]
        for _, dest, source in reduction:
            inverse[dest] ^= inverse[source]
        matrix = matrix_product(matrix_product(tuple(transform), base), tuple(inverse))
        actual_q, word, transport = check_matrix(matrix)
        need(actual_q == q, 'conjugated rank')
        rows.append({'rank': q, 'data_roles': n, 'clean_roles': 1,
                     'reflections': q + 1, 'scalar_cnots': len(word) - q - 1,
                     'common_transport_cnots': 2 * transport})
        cases += 1
    return {'conjugated_cases': cases, 'words': rows}


def tariff_checks():
    result = []
    for q in range(2, 18, 2):
        new = lower_projectors(canonical_projectors(q, 2 * q), 2 * q + 1)
        old = lower_projectors(canonical_projectors(q, 2 * q, False), 2 * q + 1)
        new_cnot = sum(g[0] == 'xor' for g in new)
        old_cnot = sum(g[0] == 'xor' for g in old)
        need(new_cnot == 2 * q * (q + 2), 'clean scalar tariff')
        need(old_cnot == 2 * q * q - 4, 'dirty scalar tariff')
        need(new_cnot - old_cnot == 4 * (q + 1), 'full comparison')
        result.append({'rank': q, 'clean': [q + 1, new_cnot],
                       'dirty': [q + 2, old_cnot], 'extra_cnots': 4 * (q + 1)})
    return result


def reject_controls():
    bad = [(True,), (2,), (1,), (), (0, -1)]
    for matrix in bad:
        try:
            compile_matrix(matrix)
        except ValueError:
            pass
        else:
            raise ValueError('invalid input accepted')
    need(compile_matrix((0,))[3] == [], 'zero needs no paid work')
    return len(bad) + 1


def authenticate():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    manifest = json.loads((package / 'SOURCES.json').read_text())
    sources = {}
    for item in manifest['files']:
        if item['usage'] == 'input':
            data = (root / item['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == item['sha256'], 'source SHA256')
            need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                 == item['git_blob'], 'source Git blob')
            sources[item['path']] = item['sha256']
    return sources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='regenerate only RESULT.json')
    args = parser.parse_args()
    sources = authenticate()
    report = {'small': all_small_matrices(), 'larger': larger_matrices(),
              'shortest_clean_columns': shortest_clean_checks(),
              'tariffs': tariff_checks(), 'boundary_controls': reject_controls()}
    payload = json.dumps(report, sort_keys=True, indent=2) + '\n'
    receipt = Path(__file__).with_name('RESULT.json')
    if args.write:
        receipt.write_text(payload)
    need(receipt.read_text() == payload, 'typed scientific receipt mismatch')
    print(json.dumps({'result': report, 'live_source_sha256': sources}, sort_keys=True))
    print('PASS_CLEAN_SQUARE_ZERO_COMPILER rank2_calls=3 dirty_calls=4 no_new_kappa')


if __name__ == '__main__':
    main()
