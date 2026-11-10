"""Independent literal-field oracle for raw first-success pencil witnesses.

Trial-division field definitions and actual matrix elimination; no author,
primary, Frobenius, polynomial-gcd or Berlekamp code is imported or executed.
Nick Petalas/6451 retains the threshold theorem and the motivating question.
ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
from itertools import permutations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = '457cd888ff00f2ac9726027b77b2ba5714f10cc92e533e87db7a778e490c930e'
PENCILS = '955e6a7de7dbff3727829d1e3489c954a3197701dd37fcc859744a8d725aaff3'
PINS = {
    'inputs/README-6451.md': (7679, '60ac95faa5792611fc244c8526bda0fc54e622ad6493aed6c8e0473474529dbc', 'a8fc09c7d540e48b2f88668f07b0f15f67b435c4'),
    'inputs/PROOF-6451.md': (6223, 'f02c3b99dd44ece33033749d8bbdc54cbfe21d122ee8412390ae35c7c12db5ef', 'b364f9c8085268211940194e9252db58b17b3bee'),
}
DOMAINS = ((2, 0, 'all'), (2, 1, 'all'), (2, 2, 'all'),
           (3, 1, 'all'), (3, 2, 'all'), (5, 1, 'all'), (2, 3, 'diagonal'))
FIELDS = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def decode(raw):
    def unique(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON receipt key')
            result[key] = value
        return result
    def forbidden(value):
        raise ValueError('noninteger or nonfinite JSON receipt number: ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_float=forbidden, parse_constant=forbidden)


def read(path):
    data = path.read_bytes()
    need(len(data) <= 2 * 1024 * 1024, 'bounded input/receipt bytes')
    return data


def authenticate():
    manifest = read(HERE / 'SOURCE-PINS.json')
    need(hashlib.sha256(manifest).hexdigest() == MANIFEST, 'source manifest SHA256')
    for path, (size, sha, blob) in PINS.items():
        data = read(HERE / path)
        need(len(data) == size and hashlib.sha256(data).hexdigest() == sha, 'source SHA256 ' + path)
        need(hashlib.sha1(b'blob ' + str(size).encode() + b'\0' + data).hexdigest() == blob, 'source Git blob ' + path)
    raw = read(HERE / 'PENCILS.json')
    need(hashlib.sha256(raw).hexdigest() == PENCILS, 'raw pencil SHA256')
    data = decode(raw)
    need(type(data['schema_version']) is int and data['schema_version'] == 1, 'raw pencil schema')
    need(len(data['pencils']) == 17, 'complete raw named domain')
    need(len({row['id'] for row in data['pencils']}) == 17, 'distinct raw pencil identities')
    return data['pencils']


def trim(poly):
    out = list(poly)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def poly_product(a, b, q):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % q
    return trim(out)


def remainder(poly, monic, q):
    work = trim(poly)
    need(monic[-1] == 1, 'literal monic divisor')
    for k in range(len(work) - 1, len(monic) - 2, -1):
        coefficient = work[k]
        for i, value in enumerate(monic):
            work[k - len(monic) + 1 + i] = (work[k - len(monic) + 1 + i] - coefficient * value) % q
    return trim(work[:max(1, len(monic) - 1)])


def digits(code, q, length):
    return [(code // q ** i) % q for i in range(length)]


def irreducible(poly, q):
    e = len(poly) - 1
    if e < 1 or poly[-1] != 1:
        return False
    for k in range(1, e // 2 + 1):
        for code in range(q ** k):
            if remainder(poly, digits(code, q, k) + [1], q) == [0]:
                return False
    return True


class Field:
    """Prime-base quotient field, with scalar fast path and no q-by-q tables."""
    def __init__(self, q, modulus):
        need(type(q) is int and q in (2, 3, 5, 1000003), 'bounded prime base')
        need(type(modulus) is list and 2 <= len(modulus) <= 6, 'bounded monic field degree')
        need(all(type(x) is int and 0 <= x < q for x in modulus), 'canonical modulus coefficients')
        need(q != 1000003 or len(modulus) == 2, 'large base only degree one')
        need(irreducible(modulus, q), 'trial-division irreducible field modulus')
        self.q, self.h, self.e = q, list(modulus), len(modulus) - 1
        self.size = q ** self.e
        need(self.e == 1 or self.size <= 256, 'bounded extension field size')

    def encode(self, coefficients):
        return sum(value * self.q ** i for i, value in enumerate(coefficients))

    def add(self, a, b):
        if self.e == 1:
            return (a + b) % self.q
        return self.encode([(x + y) % self.q for x, y in zip(digits(a, self.q, self.e), digits(b, self.q, self.e))])

    def neg(self, a):
        if self.e == 1:
            return (-a) % self.q
        return self.encode([(-x) % self.q for x in digits(a, self.q, self.e)])

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    def mul(self, a, b):
        if self.e == 1:
            return a * b % self.q
        product = poly_product(digits(a, self.q, self.e), digits(b, self.q, self.e), self.q)
        return self.encode(remainder(product, self.h, self.q))

    def power(self, a, exponent):
        out = 1
        while exponent:
            if exponent & 1:
                out = self.mul(out, a)
            a = self.mul(a, a)
            exponent //= 2
        return out

    def inverse(self, a):
        need(a != 0, 'nonzero field pivot')
        out = self.power(a, self.size - 2)
        need(self.mul(a, out) == 1, 'literal field inverse product')
        return out

    def external(self, value):
        return trim(digits(value, self.q, self.e))

    def internal(self, value):
        need(type(value) is list and 1 <= len(value) <= self.e, 'canonical field element array')
        need(all(type(x) is int and 0 <= x < self.q for x in value), 'field element coefficient type/range')
        need(value == trim(value), 'trimmed field element representation')
        return self.encode(value)


def field(q, e):
    key = (q, e)
    if key not in FIELDS:
        need(1 <= e <= 5 and (q ** e <= 256 or e == 1), 'small field search domain')
        for code in range(q ** e):
            h = digits(code, q, e) + [1]
            if irreducible(h, q):
                FIELDS[key] = Field(q, h)
                break
        need(key in FIELDS, 'trial-division field construction exists')
    return FIELDS[key]


def matrix_shape(A, B, q):
    need(type(A) is list and type(B) is list and len(A) == len(B) <= 17, 'square raw pencil dimension')
    n = len(A)
    need(all(type(row) is list and len(row) == n for M in (A, B) for row in M), 'raw square row dimensions')
    need(all(type(x) is int and 0 <= x < q for M in (A, B) for row in M for x in row), 'raw base-field coefficients')
    return n


def inverse_matrix(M, F):
    n = len(M)
    work = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(M)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if work[i][column]), None)
        if pivot is None:
            return None
        work[column], work[pivot] = work[pivot], work[column]
        scalar = F.inverse(work[column][column])
        work[column] = [F.mul(x, scalar) for x in work[column]]
        for row in range(n):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [F.sub(x, F.mul(scale, y)) for x, y in zip(work[row], work[column])]
    return [row[n:] for row in work]


def product_matrix(A, B, F):
    n = len(A)
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            value = 0
            for k in range(n):
                value = F.add(value, F.mul(A[i][k], B[k][j]))
            out[i][j] = value
    return out


def slice_matrix(A, B, alpha, F):
    return [[F.add(F.mul(alpha, x), y) for x, y in zip(a, b)] for a, b in zip(A, B)]


def check_inverse(M, inverse, F):
    n = len(M)
    identity = [[int(i == j) for j in range(n)] for i in range(n)]
    need(product_matrix(M, inverse, F) == identity, 'literal slice times inverse')
    need(product_matrix(inverse, M, F) == identity, 'literal inverse times slice')


def external_matrix(M, F):
    return [[F.external(x) for x in row] for row in M]


def answer(A, B, q, e, infinity, alpha, inverse):
    F = field(q, e)
    M = A if infinity else slice_matrix(A, B, alpha, F)
    check_inverse(M, inverse, F)
    return {'e': e, 'infinity': infinity, 'field_modulus': F.h,
            'alpha': None if infinity else F.external(alpha),
            'slice': external_matrix(M, F), 'inverse': external_matrix(inverse, F)}


def successful_slice(A, B, q, e):
    F = field(q, e)
    base_inverse = inverse_matrix(A, field(q, 1))
    if base_inverse is not None:
        return answer(A, B, q, 1, True, None, base_inverse)
    for alpha in range(F.size):
        M = slice_matrix(A, B, alpha, F)
        inverse = inverse_matrix(M, F)
        if inverse is not None:
            return answer(A, B, q, e, False, alpha, inverse)
    return None


def first_success(A, B, q):
    n = matrix_shape(A, B, q)
    limit = 1
    while q ** limit <= n:
        limit += 1
    for e in range(1, limit + 1):
        result = successful_slice(A, B, q, e)
        if result is not None:
            return result
    raise ValueError('no nonzero determinant witness within independent degree/root bound')


def determinant_polynomial(A, B, q):
    n = len(A)
    need(n <= 3, 'literal determinant permutation domain')
    result = [0] * (n + 1)
    for perm in permutations(range(n)):
        term = [1]
        for i, j in enumerate(perm):
            term = poly_product(term, [B[i][j], A[i][j]], q)
        sign = -1 if sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n)) % 2 else 1
        for i, value in enumerate(term):
            result[i] = (result[i] + sign * value) % q
    return trim(result)


def raw_matrix(code, q, n, shape):
    values = digits(code, q, n if shape == 'diagonal' else n * n)
    if shape == 'diagonal':
        return [[values[i] if i == j else 0 for j in range(n)] for i in range(n)]
    return [values[i * n:(i + 1) * n] for i in range(n)]


def census(q, n, shape):
    count = q ** (n if shape == 'diagonal' else n * n)
    transcript = bytearray()
    degrees, singular = Counter(), 0
    for acode in range(count):
        A = raw_matrix(acode, q, n, shape)
        for bcode in range(count):
            B = raw_matrix(bcode, q, n, shape)
            if determinant_polynomial(A, B, q) == [0]:
                transcript.append(0)
                singular += 1
            else:
                found = first_success(A, B, q)
                transcript.append(found['e'])
                degrees[found['e']] += 1
    return {'q': q, 'n': n, 'shape': shape, 'cases': count * count, 'singular': singular,
            'first_degree_counts': {str(e): degrees[e] for e in sorted(degrees)},
            'degree_sha256': hashlib.sha256(transcript).hexdigest()}


def verify_provided(A, B, q, provided, minimum):
    n = matrix_shape(A, B, q)
    need(type(provided['e']) is int and provided['e'] == minimum, 'witness least extension degree')
    need(type(provided['infinity']) is bool, 'literal infinity marker')
    F = Field(q, provided['field_modulus'])
    need(F.e == minimum, 'witness modulus degree')
    if provided['infinity']:
        need(minimum == 1 and provided['alpha'] is None, 'infinity belongs to base field')
        M = A
    else:
        alpha = F.internal(provided['alpha'])
        M = slice_matrix(A, B, alpha, F)
    supplied = []
    for name in ('slice', 'inverse'):
        value = provided[name]
        need(type(value) is list and len(value) == n and all(type(row) is list and len(row) == n for row in value), 'full witness matrix shape')
        supplied.append([[F.internal(x) for x in row] for row in value])
    need(supplied[0] == M, 'literal alpha A plus B source binding')
    check_inverse(M, supplied[1], F)
    return 'irreducible field, literal slice, both inverse products'


def reject(callback):
    try:
        callback()
    except ValueError as error:
        return str(error)
    raise ValueError('semantic counterfactual was accepted')


def controls(named):
    row = next(x for x in named if x['id'] == 'binary-first-2')
    A, B, q = row['A'], row['B'], row['q']
    original = row['answer']
    mutated = decode(canonical(original))
    mutated['field_modulus'] = [0, 0, 1]
    out = {'reducible_modulus': reject(lambda: verify_provided(A, B, q, mutated, 2))}
    mutated = decode(canonical(original))
    mutated['e'] = 1
    out['wrong_minimum'] = reject(lambda: verify_provided(A, B, q, mutated, 2))
    mutated = decode(canonical(original))
    value = mutated['inverse'][0][0]
    value[0] ^= 1
    mutated['inverse'][0][0] = trim(value)
    out['inverse_coefficient'] = reject(lambda: verify_provided(A, B, q, mutated, 2))
    mutated = decode(canonical(original))
    mutated['slice'][0][0] = [1] if mutated['slice'][0][0] == [0] else [0]
    out['wrong_literal_slice'] = reject(lambda: verify_provided(A, B, q, mutated, 2))
    inf = next(x for x in named if x['id'] == 'infinity-only')
    F = field(2, 1)
    need(all(inverse_matrix(slice_matrix(inf['A'], inf['B'], x, F), F) is None for x in range(2)), 'actual infinity-only affine failure')
    out['infinity_omission_affine_successes'] = 0
    zero = [[0, 0], [0, 0]]
    out['singular_polynomial'] = determinant_polynomial(zero, zero, 2)
    out['singular_fake_success'] = reject(lambda: first_success(zero, zero, 2))
    return out


def compute():
    inputs = authenticate()
    domains = [census(*spec) for spec in DOMAINS]
    need(sum(row['cases'] for row in domains) == 6920, 'complete frozen raw-pencil census')
    named = []
    for row in inputs:
        q, A, B = row['q'], row['A'], row['B']
        found = first_success(A, B, q)
        need(found['e'] == row['expected_first_degree'], 'source/declared attainer first-degree calibration')
        extra = None
        if row['id'].startswith('nonmonotone'):
            need(successful_slice(A, B, q, 4) is None, 'literal degree-four failure despite earlier success')
            extra = {'degree': 4, 'projective_successes': 0}
        named.append({'id': row['id'], 'q': q, 'A': A, 'B': B, 'answer': found, 'extra_failure': extra})
    return {'schema_version': 1, 'source_manifest_sha256': MANIFEST, 'raw_pencils_sha256': PENCILS,
            'method': 'trial-division irreducibles, literal quotient fields, complete projective slice search and Gaussian inversion; no author or primary imports',
            'domains': domains, 'total_cases': 6920, 'fixtures': named, 'controls': controls(named),
            'scope': 'Finite prime-base raw-pencil domains and all17named witnesses only; no new sharp-threshold theorem, uniform cost, field descent, native supplier or kappa admission.'}


def compare_primary(result):
    primary = decode(read(HERE / 'RESULT.json'))
    need(type(primary['schema_version']) is int and primary['schema_version'] == 1, 'primary receipt schema')
    need(primary['source_manifest_sha256'] == MANIFEST, 'primary receipt source binding')
    need(primary['pencils_sha256'] == PENCILS, 'primary receipt raw-pencil binding')
    keys = ('q', 'n', 'shape', 'cases', 'singular', 'first_degree_counts', 'degree_sha256')
    project = lambda r: [{key: row[key] for key in keys} for row in r['domains']]
    need(canonical(project(primary)) == canonical(project(result)), 'complete primary raw-pencil degree/status receipt')
    expected = {row['id']: row for row in result['fixtures']}
    seen = set()
    for row in primary['fixtures']:
        identity = row.get('id', row.get('name'))
        need(identity in expected and identity not in seen, 'distinct complete named primary witness domain')
        seen.add(identity)
        own = expected[identity]
        need(canonical([row['q'], row['A'], row['B']]) == canonical([own['q'], own['A'], own['B']]), 'named primary raw matrix binding')
        verify_provided(row['A'], row['B'], row['q'], row['answer'], own['answer']['e'])
    need(seen == expected.keys(), 'all17primary literal returned witnesses checked')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        retained = decode(read(HERE / 'ORACLE.json'))
        need(canonical(retained) == canonical(result), 'strict independent receipt drift')
        compare_primary(result)
        print('PASS_LITERAL_FIRST_PENCIL_SLICE_ORACLE')


if __name__ == '__main__':
    main()
