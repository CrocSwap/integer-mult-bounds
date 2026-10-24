"""Build source-bound examples and the two obstruction families."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from native import Native, act, inverse
from reversible_cnf import cnf_problem

HERE = Path(__file__).resolve().parent


def diagonal(n, phase=0, linear=None, quadratic=None):
    return Native(tuple(1 << i for i in range(n)), 0, phase,
                  tuple(linear or [0] * n), tuple(quadratic or [0] * n)).json()


def source_conjugation(mutate=False):
    raw = json.loads((HERE / 'source/RIGHT-RECIPE.json').read_text())
    n = len(raw['matrix_rows'])
    rows = inverse(raw['matrix_rows'])
    shift = act(rows, raw['offset'])
    i = next(i for i in range(n) if shift >> i & 1)
    z = [0] * n
    z[i] = 2
    r = [2 * ((rows[i] >> j) & 1) for j in range(n)]
    generators = {'G': raw, 'Z': diagonal(n, linear=z),
                  'R': diagonal(n, phase=0 if mutate else 2, linear=r)}
    # G Z G^-1 is R. The source role is restored before the final subtraction.
    sequence = [{'op': 'apply', 'dst': 0, 'generator': 'G', 'inverse': True},
                {'op': 'apply', 'dst': 0, 'generator': 'Z'},
                {'op': 'apply', 'dst': 0, 'generator': 'G'},
                {'op': 'add', 'src': 0, 'dst': 1},
                {'op': 'apply', 'dst': 0, 'generator': 'G', 'inverse': True},
                {'op': 'apply', 'dst': 0, 'generator': 'Z', 'inverse': True},
                {'op': 'apply', 'dst': 0, 'generator': 'G'},
                {'op': 'query', 'src': 0, 'dst': 1, 'generator': 'R', 'coefficient': -1}]
    return {'axes': n, 'roles': 2, 'generators': generators, 'program': sequence, 'reference': []}


def late_projector(n):
    generators, code = {}, []
    for i in range(n):
        a = [0] * n
        a[i] = 1
        generators['S' + str(i)] = diagonal(n, linear=a)
        a[i] = 2
        generators['Z' + str(i)] = diagonal(n, linear=a)
        code.extend([{'op': 'query', 'src': 0, 'dst': 0, 'generator': 'S' + str(i), 'coefficient': [0, -1]},
                     {'op': 'query', 'src': 0, 'dst': 0, 'generator': 'Z' + str(i), 'coefficient': -1},
                     {'op': 'scale', 'dst': 0, 'coefficient': '1/4'}])
    for i in range(n):
        for j in range(i + 1, n):
            q = [0] * n
            q[i] = 1 << j
            name = f'CZ{i}_{j}'
            generators[name] = diagonal(n, quadratic=q)
            code.extend([{'op': 'query', 'src': 0, 'dst': 0, 'generator': name},
                         {'op': 'scale', 'dst': 0, 'coefficient': '1/2'}])
    return {'axes': n, 'roles': 1, 'generators': generators, 'program': code,
            'reference': [{'op': 'scale', 'dst': 0, 'coefficient': 0}]}


def write_examples():
    from native_identity import decide, digest
    cases = {'source-conjugation': source_conjugation(),
             'source-phase-error': source_conjugation(True),
             'cnf-unsatisfiable': cnf_problem(3, [[1], [-1]]),
             'cnf-satisfiable': cnf_problem(3, [[1, 2], [-1]])}
    for name, problem in cases.items():
        (HERE / 'examples' / (name + '.json')).write_text(json.dumps(problem, indent=2) + '\n')
        (HERE / 'examples' / (name + '.certificate.json')).write_text(json.dumps(decide(problem), indent=2) + '\n')
    problem = late_projector(9)
    points = [1 << i for i in range(9)] + [0] * 13
    certificate = {'schema': 'native-tensor-cutoff/v1', 'problem_sha256': digest(problem),
                   'status': 'COUNTEREXAMPLE', 'axes': 9, 'roles': 1, 'window': [22, 25],
                   'input_role': 0, 'output_role': 0, 'input_points': points,
                   'output_points': points, 'discrepancy': ['1', '0']}
    (HERE / 'examples/late-projector-9.json').write_text(json.dumps(problem, indent=2) + '\n')
    (HERE / 'examples/late-projector-9.certificate.json').write_text(json.dumps(certificate, indent=2) + '\n')


if __name__ == '__main__':
    write_examples()
