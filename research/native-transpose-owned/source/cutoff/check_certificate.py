"""Check certificates without importing the producer or its native algebra."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact import QI, need, scalar, unit


def dot(row, x):
    return (row & x).bit_count() % 2


def image(g, x):
    return sum(dot(row, x) << i for i, row in enumerate(g[0])) ^ g[1]


def exponent(g, x):
    return (g[2] + sum(g[3][i] for i in range(len(g[0])) if x & (1 << i))
            + 2 * sum(1 for i in range(len(g[0])) for j in range(i + 1, len(g[0]))
                      if x & (1 << i) and x & (1 << j) and g[4][i] & (1 << j))) % 4


def invert_matrix(rows):
    size = len(rows)
    a, b = list(rows), [1 << i for i in range(size)]
    for col in range(size):
        choices = [i for i in range(col, size) if a[i] & (1 << col)]
        need(bool(choices), 'checker: singular matrix')
        i = choices[0]
        a[col], a[i], b[col], b[i] = a[i], a[col], b[i], b[col]
        for row in range(size):
            if row != col and a[row] & (1 << col):
                a[row] ^= a[col]
                b[row] ^= b[col]
    return tuple(b)


def normalize(data, n):
    need(isinstance(data, dict) and set(data) == {'matrix_rows', 'offset', 'phase', 'linear_Z4', 'quadratic_rows'},
         'checker: native fields')
    a, p, q = data['matrix_rows'], data['linear_Z4'], data['quadratic_rows']
    need(all(isinstance(x, list) and len(x) == n for x in (a, p, q)), 'checker: native dimensions')
    need(all(type(x) is int and 0 <= x < (1 << n) for x in a + q), 'checker: binary rows')
    need(all(type(x) is int and 0 <= x < 4 for x in p), 'checker: linear phases')
    need(type(data['offset']) is int and 0 <= data['offset'] < (1 << n), 'checker: offset')
    need(type(data['phase']) is int and 0 <= data['phase'] < 4, 'checker: phase')
    invert_matrix(a)
    return (tuple(a), data['offset'], data['phase'], tuple(p),
            tuple(q[i] & ~((1 << (i + 1)) - 1) for i in range(n)))


def problem_data(problem):
    need(isinstance(problem, dict) and set(problem) == {'axes', 'roles', 'generators', 'program', 'reference'},
         'checker: problem fields')
    n, r = problem['axes'], problem['roles']
    need(type(n) is int and 1 <= n <= 256 and type(r) is int and 1 <= r <= 4096,
         'checker: dimensions')
    need(isinstance(problem['generators'], dict), 'checker: generator table')
    gs = {}
    for name, value in problem['generators'].items():
        need(isinstance(name, str) and bool(name), 'checker: generator name')
        gs[name] = normalize(value, n)
    fields = {'add': {'op', 'src', 'dst', 'coefficient'},
              'query': {'op', 'src', 'dst', 'coefficient', 'generator', 'inverse'},
              'apply': {'op', 'dst', 'generator', 'inverse'},
              'scale': {'op', 'dst', 'coefficient'}, 'swap': {'op', 'src', 'dst'}}
    for code in (problem['program'], problem['reference']):
        need(isinstance(code, list), 'checker: instruction list')
        for ins in code:
            need(isinstance(ins, dict), 'checker: instruction object')
            op = ins.get('op')
            need(isinstance(op, str) and op in fields and set(ins) <= fields[op], 'checker: instruction fields')
            for key in (('src', 'dst') if op in ('add', 'query', 'swap') else ('dst',)):
                need(type(ins.get(key)) is int and 0 <= ins[key] < r, 'checker: role')
            if op in ('apply', 'query'):
                need(isinstance(ins.get('generator'), str) and ins['generator'] in gs, 'checker: generator')
                need(type(ins.get('inverse', False)) is bool, 'checker: inverse flag')
            if 'coefficient' in ins:
                scalar(ins['coefficient'])
    return gs


def compose(g, h):
    """Expand affine Boolean forms modulo four, without interpolation."""
    n = len(g[0])
    a = []
    for row in g[0]:
        out = 0
        for j in range(n):
            if row & (1 << j):
                out ^= h[0][j]
        a.append(out)
    constant = h[2] + g[2]
    linear = list(h[3])
    quad = [[2 * ((h[4][j] >> k) & 1) for k in range(n)] for j in range(n)]
    bits = [[(row >> j) & 1 for j in range(n)] for row in h[0]]
    shifts = [(h[1] >> i) & 1 for i in range(n)]
    for i in range(n):
        coefficient, t = g[3][i], shifts[i]
        constant += coefficient * t
        for j in range(n):
            linear[j] += coefficient * (1 - 2 * t) * bits[i][j]
            for k in range(j + 1, n):
                quad[j][k] -= 2 * coefficient * bits[i][j] * bits[i][k]
        for l in range(i + 1, n):
            if not (g[4][i] >> l & 1):
                continue
            u = shifts[l]
            constant += 2 * t * u
            for j in range(n):
                linear[j] += 2 * (t * bits[l][j] + u * bits[i][j] + bits[i][j] * bits[l][j])
                for k in range(j + 1, n):
                    quad[j][k] += 2 * (bits[i][j] * bits[l][k] + bits[i][k] * bits[l][j])
    return (tuple(a), image(g, h[1]), constant % 4, tuple(x % 4 for x in linear),
            tuple(sum(((quad[j][k] % 4) // 2) << k for k in range(j + 1, n)) for j in range(n)))


def inverse(g):
    n = len(g[0])
    rows = invert_matrix(g[0])
    offset = sum(dot(row, g[1]) << i for i, row in enumerate(rows))
    h = (rows, offset, 0, (0,) * n, (0,) * n)
    phase = compose(g, h)
    return (rows, offset, -phase[2] % 4, tuple(-x % 4 for x in phase[3]), phase[4])


def accumulate(row, key, value):
    if key in row:
        value = value + row[key]
    if value:
        row[key] = value
    elif key in row:
        del row[key]


def algebra_endpoint(problem, code, generators, max_terms):
    n, r = problem['axes'], problem['roles']
    need(type(max_terms) is int and max_terms >= r, 'checker: expanded-term limit; no decision')
    identity = (tuple(1 << i for i in range(n)), 0, 0, (0,) * n, (0,) * n)
    state = [{(i, identity): QI(1)} for i in range(r)]
    for ins in code:
        op, d = ins['op'], ins['dst']
        if op == 'swap':
            s = ins['src']
            state[s], state[d] = state[d], state[s]
        elif op == 'scale':
            c = scalar(ins.get('coefficient', 1))
            state[d] = {k: c * v for k, v in state[d].items()} if c else {}
        else:
            s = d if op == 'apply' else ins['src']
            old = list(state[s].items())
            if op != 'add':
                g = generators[ins['generator']]
                if ins.get('inverse', False):
                    g = inverse(g)
                old = [((i, compose(g, h)), c) for (i, h), c in old]
            if op == 'apply':
                state[d] = {}
            c = scalar(ins.get('coefficient', 1))
            for key, value in old:
                accumulate(state[d], key, c * value)
        need(sum(len(row) for row in state) <= max_terms, 'checker: expanded-term limit; no decision')
    return state


def literal_endpoint(problem, code, generators, input_role, points, max_terms):
    """Run literal tensor basis actions. No group products or Gram factors are used."""
    state = [{} for _ in range(problem['roles'])]
    state[input_role][tuple(points)] = QI(1)
    for ins in code:
        op, d = ins['op'], ins['dst']
        if op == 'swap':
            s = ins['src']
            state[s], state[d] = state[d], state[s]
        elif op == 'scale':
            c = scalar(ins.get('coefficient', 1))
            state[d] = {k: c * v for k, v in state[d].items()} if c else {}
        else:
            s = d if op == 'apply' else ins['src']
            old = list(state[s].items())
            if op != 'add':
                g = generators[ins['generator']]
                if ins.get('inverse', False):
                    rows = invert_matrix(g[0])
                    moved = []
                    for xs, value in old:
                        ys = tuple(sum(dot(row, x ^ g[1]) << j for j, row in enumerate(rows)) for x in xs)
                        moved.append((ys, value * unit(-sum(exponent(g, y) for y in ys))))
                else:
                    moved = [(tuple(image(g, x) for x in xs), value * unit(sum(exponent(g, x) for x in xs)))
                             for xs, value in old]
                old = moved
            if op == 'apply':
                state[d] = {}
            c = scalar(ins.get('coefficient', 1))
            for xs, value in old:
                accumulate(state[d], xs, c * value)
        need(sum(map(len, state)) <= max_terms, 'checker: literal-term limit; no decision')
    return state


def check(problem, certificate, max_terms=100000):
    need(isinstance(certificate, dict), 'checker: certificate object')
    need(type(max_terms) is int and max_terms >= 1, 'checker: positive term limit')
    generators = problem_data(problem)
    digest = hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    need(certificate.get('schema') == 'native-tensor-cutoff/v1' and certificate.get('problem_sha256') == digest,
         'checker: certificate binding')
    n, r = problem['axes'], problem['roles']
    need(certificate.get('axes') == n and certificate.get('roles') == r and
         certificate.get('window') == [2 * n + 4, 2 * n + 7], 'checker: certificate dimensions')
    if certificate.get('status') == 'IDENTITY_ALL_POSITIVE_WIDTHS':
        a = algebra_endpoint(problem, problem['program'], generators, max_terms)
        b = algebra_endpoint(problem, problem['reference'], generators, max_terms)
        need(a == b and certificate.get('residual_terms') == 0, 'checker: complete native endpoints differ')
        return 'PASS_NATIVE_IDENTITY_ALL_POSITIVE_WIDTHS'
    need(certificate.get('status') == 'COUNTEREXAMPLE', 'checker: status')
    xs, ys = certificate.get('input_points'), certificate.get('output_points')
    need(isinstance(xs, list) and isinstance(ys, list) and len(xs) == len(ys) and
         2 * n + 4 <= len(xs) <= 2 * n + 7, 'checker: witness width')
    need(all(type(x) is int and 0 <= x < 1 << n for x in xs + ys), 'checker: witness coordinates')
    i, o = certificate.get('input_role'), certificate.get('output_role')
    need(type(i) is int and 0 <= i < r and type(o) is int and 0 <= o < r, 'checker: witness roles')
    a = literal_endpoint(problem, problem['program'], generators, i, xs, max_terms)
    b = literal_endpoint(problem, problem['reference'], generators, i, xs, max_terms)
    observed = a[o].get(tuple(ys), QI()) - b[o].get(tuple(ys), QI())
    need(bool(observed) and observed == scalar(certificate.get('discrepancy')), 'checker: witness discrepancy')
    return 'PASS_NATIVE_TENSOR_COUNTEREXAMPLE'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem', type=Path)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--max-terms', type=int, default=100000)
    args = parser.parse_args()
    need(args.max_terms >= 1, 'positive checker term limit')
    print(check(json.loads(args.problem.read_text()), json.loads(args.certificate.read_text()), args.max_terms))


if __name__ == '__main__':
    main()
