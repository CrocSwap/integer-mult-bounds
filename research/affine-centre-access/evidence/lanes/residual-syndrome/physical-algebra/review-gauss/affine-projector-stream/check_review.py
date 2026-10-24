"""Check the Haar shear with exact symbolic rows and pinned source text."""

from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
PHYS = HERE.parents[1]
ROOT = next(p for p in HERE.parents if (p / 'RESEARCH-START-HERE.txt').is_file())
SOURCE = PHYS / 'affine-projector-stream'
BASE = 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f'
PINS = {
    'STREAM.md': '1351e6171fc7b9ac778363dc208665aa83e9176f84213c8aac34326cd71ad12e',
    'STREAM.json': 'a28edcef2f093326efec312b74d36c3ec55c26d2a92ae40144d610574affabc3',
    'check_stream.py': '5a4c6e572e5b8d93e20efece6d8f43b242f66da751bf65ad5345432350abfd35',
    'AMENDMENT.md': '12836faac08e0edc9a7d746eb5b1be7f62f9c72e17ed1f8a02629c5375db6479',
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def add(a, b, scale=F(1)):
    result = dict(a)
    for i, v in b.items():
        t = result.get(i, 0) + scale * v
        if t:
            result[i] = t
        else:
            result.pop(i, None)
    return result


def times(a, scale):
    return {i: v * scale for i, v in a.items() if v * scale}


def case(n, width, chunk, offset, protected, poly):
    half = width // 2
    bit = lambda i, j: (n * width - 1 - i * width - j) * chunk + offset
    pairs = [(bit(i, j), bit(i, j + half)) for i in range(n) for j in range(half)]
    axes = [b for _, b in pairs]
    selected = sum(1 << b for b in axes)
    native_bits = n * width * chunk
    addresses = 1 << (native_bits + protected)
    size = addresses * poly
    identity = [{j: F(1)} for j in range(2 * size)]
    max_norm, max_denominator = F(0), 1

    def observe(row):
        nonlocal max_norm, max_denominator
        max_norm = max(max_norm, sum(abs(v) for v in row.values()))
        max_denominator = max(max_denominator, max((v.denominator for v in row.values()), default=1))

    def permute(rows):
        result = [None] * size
        for address in range(addresses):
            new = address
            for a, b in pairs:
                if address & (1 << b):
                    new ^= 1 << a
            need(new >> native_bits == address >> native_bits, 'Protected fields stay fixed')
            for coefficient in range(poly):
                result[new * poly + coefficient] = rows[address * poly + coefficient]
        return result

    def haar(rows, inverse=False):
        rows = list(rows)
        steps, previous = [], 0
        for b in axes:
            steps.append((b, previous))
            previous |= 1 << b
        operations = 0
        for b, mask in reversed(steps) if inverse else steps:
            for address in range(addresses):
                if address & (mask | (1 << b)):
                    continue
                for coefficient in range(poly):
                    a = address * poly + coefficient
                    d = (address | (1 << b)) * poly + coefficient
                    u, v = rows[a], rows[d]
                    if inverse:
                        rows[a], rows[d] = add(u, v), add(v, u, -1)
                    else:
                        difference, total = add(u, v, -1), add(u, v)
                        observe(difference)
                        observe(total)
                        rows[a], rows[d] = times(difference, F(1, 2)), times(total, F(1, 2))
                    observe(rows[a])
                    observe(rows[d])
                    operations += 1
        need(operations == size - size // (1 << len(axes)), 'Geometric pair count')
        return rows

    def shear(rows, sign=1, omit_detail=False):
        x, y = permute(rows[:size]), permute(rows[size:])
        x, y = haar(x), haar(y)
        if omit_detail:
            y[next(a for a in range(size) if a // poly & selected)] = {}
        for address in range(addresses):
            if not address & selected:
                for coefficient in range(poly):
                    i = address * poly + coefficient
                    y[i] = add(y[i], x[i], sign)
                    observe(y[i])
        return permute(haar(x, True)) + permute(haar(y, True))

    expected = identity[:size]
    for address in range(addresses):
        for coefficient in range(poly):
            row = dict(identity[size + address * poly + coefficient])
            for subset in range(1 << len(pairs)):
                translated = address
                for j, (a, b) in enumerate(pairs):
                    if subset & (1 << j):
                        translated ^= (1 << a) | (1 << b)
                value = F((-1) ** subset.bit_count(), 1 << len(pairs))
                row = add(row, identity[translated * poly + coefficient], value)
            expected.append(row)

    actual = shear(identity)
    need(actual == expected, 'All arbitrary source and target columns')
    forward_norm, forward_denominator = max_norm, max_denominator
    need(forward_norm <= 2 and forward_denominator <= 1 << len(axes), 'Forward prefix bounds')
    need(shear(actual, -1) == identity, 'Exact inverse on the correlated code')
    need(shear(shear(identity, -1)) == identity, 'Both inverse orders')
    need(shear(identity, omit_detail=True) != expected, 'Omitted detail is detected')
    need(shear(identity, -1) != expected, 'Wrong leaf sign is detected')

    encoded = haar(identity[:size])
    need(haar(encoded, True) == identity[:size], 'Full Haar inverse with all details')
    leaf = [row if (i // poly) & selected == 0 else {} for i, row in enumerate(encoded)]
    projection = haar(leaf, True)
    for address in range(addresses):
        for coefficient in range(poly):
            row = {}
            for subset in range(1 << len(axes)):
                translated = address
                for j, b in enumerate(axes):
                    if subset & (1 << j):
                        translated ^= 1 << b
                row[translated * poly + coefficient] = F((-1) ** subset.bit_count(), 1 << len(axes))
            need(projection[address * poly + coefficient] == row, 'B inverse E B is the coordinate projector')

    leaf_count = size // (1 << len(axes))
    details = [size // (1 << (j + 1)) for j in range(len(axes))]
    need(sum(details) + leaf_count == size, 'No independent extra signal records')
    inverse_rows = haar(identity[:size], True)
    unrelated_norm = max(sum(abs(v) for v in row.values()) for row in inverse_rows)
    need(unrelated_norm == len(axes) + 1, 'Unrelated detail norm is not the shear prefix bound')
    return {
        'n': n, 'width': width, 'chunk_bits': chunk, 'selected_offset': offset,
        'protected_bits': protected, 'polynomial_coefficients': poly,
        'arbitrary_input_columns': 2 * size, 'k': len(axes),
        'forward_prefix_row_norm': str(forward_norm),
        'forward_max_denominator': forward_denominator,
        'detail_records': sum(details), 'leaf_records': leaf_count,
        'unrelated_Haar_inverse_norm': str(unrelated_norm),
    }


def phase_cases():
    count = 0
    for n, f in [(2, 1), (2, 2), (3, 1), (3, 2)]:
        omega = (1 << n) - 1
        odds = [q for q in range(1 << n) if q.bit_count() % 2]
        bases = [basis for rank in range(n + 1) for basis in combinations(odds, rank)
                 if all((a & b).bit_count() % 2 == 0 for a, b in combinations(basis, 2))]
        for first in product(range(1 << n), repeat=f):
            chars = first + tuple(c ^ omega for c in first)
            for basis in bases:
                for delta in range(1 << n):
                    for gamma in range(4):
                        actual = gamma + sum((q & c).bit_count() % 2 for q in basis for c in chars)
                        actual += 2 * sum((delta & c).bit_count() % 2 for c in chars)
                        wanted = gamma + len(basis) * f + 2 * f * ((omega & delta).bit_count() % 2)
                        need(actual % 4 == wanted % 4, 'Completed-owner total phase')
                        count += 1
    need((1 + 1) % 4 != (2 * 1 + 1) % 4, 'One-column phase ambiguity is material')
    return count


def main():
    for name, pin in PINS.items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, 'Pin: ' + name)
    receipt = json.loads((SOURCE / 'STREAM.json').read_text())
    sources = dict(receipt['source_files'])
    sources['notes/bulk-complex-guard.tex'] = '2e5f923dfdb38aba99262e08fa265a75f2f15934d31a9bacec0830b47bf72c37'
    source_hashes = {}
    for path, pin in sources.items():
        data = subprocess.check_output(['git', '-C', str(ROOT / 'worktrees/k5-centre-sharing'), 'show', BASE + ':' + path])
        actual = sha256(data).hexdigest()
        need(actual == pin, 'Source pin: ' + path)
        source_hashes[path] = actual
    cases = [case(*v) for v in [(1, 4, 2, 1, 0, 1), (2, 2, 1, 0, 2, 2), (2, 4, 1, 0, 0, 1)]]
    result = {
        'status': 'PASS_INDEPENDENT_HAAR_STREAM_IDENTITIES_AND_PREFIXES',
        'producer_imported_or_executed': False, 'source_commit': BASE,
        'producer_pins': PINS, 'git_source_pins': source_hashes,
        'cases': cases, 'completed_phase_equalities': phase_cases(),
        'negative_controls': 7,
        'scope': 'Small exact symbolic rows and phase checks. The fixed-tape and recursive claims require the proof hypotheses.',
    }
    (HERE / 'CHECK.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])
    print(json.dumps({'input_columns': sum(c['arbitrary_input_columns'] for c in cases), 'phase_equalities': result['completed_phase_equalities']}))


if __name__ == '__main__':
    main()
