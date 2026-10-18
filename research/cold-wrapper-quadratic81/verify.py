#!/usr/bin/env python3
"""Symbolic affine-support and Z/4 quadratic-phase check for one cold wrapper.

No imports from Clifford, tableau, compiler or state-vector code.
Joshua Snider, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N, WIDTH, VARIABLES = 9, 4, 13
SIZE = 2 ** N
CONSTANT = 2 ** VARIABLES
X = [2 ** i for i in range(N)]
DELTA = [2 ** (N + i) for i in range(WIDTH)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def add(*polynomials):
    out = {}
    for polynomial in polynomials:
        for term, coefficient in polynomial.items():
            out[term] = (out.get(term, 0) + coefficient) % 4
    return {term: coefficient for term, coefficient in out.items() if coefficient}


def scale(polynomial, coefficient):
    return {term: value * coefficient % 4 for term, value in polynomial.items()
            if value * coefficient % 4}


def multiply(a, b):
    # Boolean quotient: X_i^2 = X_i, hence union of monomial supports.
    out = {}
    for left, av in a.items():
        for right, bv in b.items():
            term = left | right
            out[term] = (out.get(term, 0) + av * bv) % 4
    return {term: coefficient for term, coefficient in out.items() if coefficient}


def lift(form):
    """Lift an affine XOR to its exact degree <= 2 Boolean polynomial mod 4."""
    constant = int(bool(form & CONSTANT))
    indices = [i for i in range(VARIABLES) if form & (2 ** i)]
    sign = 1 - 2 * constant
    result = {0: constant} if constant else {}
    for i in indices:
        result[2 ** i] = sign % 4
    for position, i in enumerate(indices):
        for j in indices[position + 1:]:
            result[(2 ** i) | (2 ** j)] = (-2 * sign) % 4
    return result


def linear_map(rows, forms, offset=0):
    result = []
    for i, row in enumerate(rows):
        value = CONSTANT if offset & (2 ** i) else 0
        for j, form in enumerate(forms):
            if row & (2 ** j):
                value ^= form
        result.append(value)
    return result


def phase(quadratic, linear, forms, constant=0):
    terms = [{0: constant % 4}]
    lifted = [lift(form) for form in forms]
    terms.extend(scale(lifted[i], linear[i]) for i in range(N))
    terms.extend(scale(multiply(lifted[i], lifted[j]), 2)
                 for i in range(N) for j in range(i + 1, N)
                 if quadratic[i] & (2 ** j))
    result = add(*terms)
    require(all(mask.bit_count() <= 2 for mask in result), 'Phase exceeds quadratic degree')
    return result


def canonical_geometry(vectors):
    # Enumerate the span to choose the same specified greedy complement,
    # without importing rank, inverse, transpose or canonical_frame.
    basis, span = [], {0}
    for vector in vectors:
        require(type(vector) is int and 0 < vector < SIZE and vector not in span,
                'Invalid terminal basis')
        basis.append(vector)
        span |= {value ^ vector for value in span}
    for vector in (2 ** i for i in range(N)):
        if vector not in span:
            basis.append(vector)
            span |= {value ^ vector for value in span}
    require(len(vectors) == WIDTH and len(basis) == N, 'Wrong frame dimension')
    physical = []
    for mask in range(SIZE):
        value = 0
        for i, vector in enumerate(basis):
            if mask & (2 ** i):
                value ^= vector
        physical.append(value)
    require(len(set(physical)) == SIZE, 'Nonbijective coordinate map')
    inverse = [0] * SIZE
    for i, value in enumerate(physical):
        inverse[value] = i
    columns = [inverse[2 ** i] for i in range(N)]
    inverse_rows = [sum(2 ** j for j in range(N) if columns[j] & (2 ** i)) for i in range(N)]
    quadratic = [sum(((int(i == j) + (columns[i] & columns[j]).bit_count()) % 2) * (2 ** j)
                     for j in range(N)) for i in range(N)]
    linear = [(quadratic[i] >> i) & 1 for i in range(N)]
    return basis, inverse_rows, quadratic, linear


def validate_monomial(recipe):
    require(set(recipe) == {'matrix_rows', 'quadratic_rows', 'linear_Z4', 'offset', 'phase'},
            'Unexpected monomial fields')
    rows, q, alpha = (recipe[k] for k in ('matrix_rows', 'quadratic_rows', 'linear_Z4'))
    require(len(rows) == len(q) == len(alpha) == N, 'Wrong monomial dimension')
    require(all(type(v) is int and 0 <= v < SIZE for v in rows + q)
            and all(type(v) is int and 0 <= v < 4 for v in alpha), 'Invalid coefficients')
    require(type(recipe['offset']) is int and 0 <= recipe['offset'] < SIZE
            and type(recipe['phase']) is int and 0 <= recipe['phase'] < 4, 'Invalid affine phase')
    require(all(((q[i] >> j) & 1) == ((q[j] >> i) & 1) for i in range(N) for j in range(N)),
            'Nonsymmetric quadratic form')
    require(all(alpha[i] % 2 == ((q[i] >> i) & 1) for i in range(N)), 'Wrong diagonal lift')
    images = {sum(((row & x).bit_count() % 2) * (2 ** i) for i, row in enumerate(rows))
              for x in range(SIZE)}
    require(len(images) == SIZE, 'Noninvertible monomial')


def derive(recipe, terminal=None):
    require(recipe['rank'] == WIDTH, 'Wrong residual width')
    left, right = recipe['left'], recipe['right']
    validate_monomial(left)
    validate_monomial(right)
    basis, inverse, q, alpha = canonical_geometry(terminal or recipe['terminal_vectors'])
    right_output = linear_map(right['matrix_rows'], X, right['offset'])
    z = [form ^ (DELTA[i] if i < WIDTH else 0) for i, form in enumerate(right_output)]
    y = linear_map(left['matrix_rows'], z, left['offset'])
    displacement = [a ^ b for a, b in zip(y, X)]
    coordinates = linear_map(inverse, displacement)
    require(coordinates[WIDTH:] == [0] * (N - WIDTH), 'Output leaves canonical support')
    c = coordinates[:WIDTH]
    p_rows = [(form >> N) & (2 ** WIDTH - 1) for form in c]
    images = [sum(((row & delta).bit_count() % 2) * (2 ** i) for i, row in enumerate(p_rows))
              for delta in range(2 ** WIDTH)]
    require(len(set(images)) == 2 ** WIDTH, 'Path-to-kernel coordinates are not bijective')
    inverse_images = [images.index(value) for value in range(2 ** WIDTH)]
    components = {
        'right_phase_x': phase(right['quadratic_rows'], right['linear_Z4'], X, right['phase']),
        'left_phase_z': phase(left['quadratic_rows'], left['linear_Z4'], z, left['phase']),
        'minus_delta_weight': scale(add(*(lift(form) for form in DELTA)), -1),
        'minus_canonical_phase_y': scale(phase(q, alpha, y), -1),
        'canonical_phase_x': phase(q, alpha, X),
        'canonical_difference_weight': add(*(lift(form) for form in c)),
    }
    residual = add(*components.values())
    require(all(mask.bit_count() <= 2 for mask in residual), 'Residual exceeds quadratic degree')
    return {'completed_basis': basis, 'output_forms': y, 'kernel_difference_forms': c,
            'spectator_displacement_forms': coordinates[WIDTH:], 'delta_map_rows': p_rows,
            'delta_map_inverse_images': inverse_images, 'components': components,
            'residual': residual}


def witness(polynomial):
    mask = min(polynomial, key=lambda x: (x.bit_count(), x))
    value = sum(coefficient for term, coefficient in polynomial.items() if term & mask == term) % 4
    require(value != 0, 'Failed to extract phase counterexample')
    return {'assignment_mask': mask, 'input': mask & (SIZE - 1), 'delta': mask >> N,
            'phase_error_mod4': value}


def identity_monomial():
    return dict(matrix_rows=[2 ** i for i in range(N)], quadratic_rows=[0] * N,
                linear_Z4=[0] * N, offset=0, phase=0)


def controls(recipe):
    reports = []
    def reject(name, mutate, terminal=None):
        changed = deepcopy(recipe)
        mutate(changed)
        try:
            result = derive(changed, terminal)
        except ValueError as error:
            reports.append({'name': name, 'rejection': str(error)})
            return None
        require(result['residual'], 'Invalid wrapper accepted: ' + name)
        reports.append({'name': name, 'counterexample': witness(result['residual'])})
        return result
    for side in ('left', 'right'):
        reject(side + '_phase', lambda r, s=side: r[s].update(phase=(r[s]['phase'] + 1) % 4))
        reject(side + '_translation', lambda r, s=side: r[s].update(offset=r[s]['offset'] ^ 1))
        reject(side + '_linear', lambda r, s=side: r[s]['linear_Z4'].__setitem__(0, (r[s]['linear_Z4'][0] + 2) % 4))
        reject('missing_' + side, lambda r, s=side: r.update({s: identity_monomial()}))
    reject('swapped_wrappers', lambda r: r.update(left=recipe['right'], right=recipe['left']))
    def quadratic(r):
        r['right']['quadratic_rows'][0] ^= 2
        r['right']['quadratic_rows'][1] ^= 1
    reject('right_quadratic', quadratic)
    blind = reject('input_Z8', lambda r: r['right']['linear_Z4'].__setitem__(8, (r['right']['linear_Z4'][8] + 2) % 4))
    require(blind is not None and blind['residual'] == {2 ** 8: 2}, 'Unexpected Z8 residual')
    reports[-1]['residual'] = [[2 ** 8, 2]]
    reports[-1]['zero_input_column_unchanged'] = True
    reject('wrong_terminal_same_rank', lambda r: None, [269, 140, 45, 30])
    reject('wrong_width', lambda r: r.update(rank=3))
    return reports


def load_instance():
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    for name, expected in sources['sha256'].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected, 'Source bytes changed: ' + name)
    instance = json.loads((HERE / 'INSTANCE.json').read_bytes())
    require(instance['n'] == N and instance['seed'] == 81 and instance['helper'] == 442,
            'Wrong scoped instance')
    require(instance['providers'] == {'ck': '0:429', 'jp8': '0:413'}, 'Wrong selected providers')
    recipe = instance['recipe']
    require(recipe['vectors'] == [] and recipe['terminal_vectors'] == [268, 140, 45, 30]
            and recipe['terminal'] == 429, 'Wrong selected frame pair')
    bindings = []
    for provider, key in instance['providers'].items():
        package = ROOT / 'research/community-k492-audit/pr626/replay/mixed-global/base/providers' / provider
        word = json.loads(gzip.decompress((package / 'CANONICAL-WORD.json.gz').read_bytes()))
        recipes = json.loads((package / 'RESIDUAL-ADAPTERS.json').read_bytes())['recipes']
        candidates = sorted(k for k, value in recipes.items() if k.startswith('0:') and value['rank'] == WIDTH)
        require(len(candidates) == 14 and candidates[81 % len(candidates)] == key, 'Seeded selection changed')
        chosen = recipes[key]
        require(all(chosen[k] == recipe[k] for k in recipe if k != 'terminal'), 'Provider recipe changed')
        helper = instance['helper']
        require(word['start'][helper] == 0 and word['frames'][0] == []
                and word['final'][helper] == chosen['terminal']
                and word['frames'][chosen['terminal']] == recipe['terminal_vectors'], 'Detached helper')
        bindings.append({'provider': provider, 'recipe_key': key, 'helper': helper})
    return instance, bindings


def serial(polynomial):
    return [[mask, value] for mask, value in sorted(polynomial.items(), key=lambda item: (item[0].bit_count(), item[0]))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    instance, bindings = load_instance()
    certificate = derive(instance['recipe'])
    require(not certificate['residual'], 'Selected phase polynomial is not zero')
    certificate['components'] = {name: serial(poly) for name, poly in certificate['components'].items()}
    certificate['residual'] = serial(certificate['residual'])
    report = {'status': 'PASS_COLD_WRAPPER_QUADRATIC_CERTIFICATE', 'bindings': bindings,
              'variables': VARIABLES, 'coefficient_domain': 'Z/4Z; X_i^2=X_i',
              'phase_coefficient_positions': 1 + VARIABLES + VARIABLES * (VARIABLES - 1) // 2,
              'certificate': certificate, 'negative_controls': controls(instance['recipe'])}
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + '\n')
    else:
        require(report == json.loads((HERE / 'EXPECTED.json').read_bytes()), 'Recorded certificate changed')
    print(report['status'], '13 variables, 92 coefficient positions, 13 rejection controls')


if __name__ == '__main__':
    main()
