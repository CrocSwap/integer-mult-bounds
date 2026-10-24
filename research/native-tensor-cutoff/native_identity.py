"""Decide complete dirty endpoints and produce a short native tensor witness."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact import QI, need, scalar, unit
from native import Native, character_tuple


def digest(problem):
    return hashlib.sha256(json.dumps(problem, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate(problem):
    need(isinstance(problem, dict) and set(problem) == {'axes', 'roles', 'generators', 'program', 'reference'},
         'exact problem fields required')
    n, r = problem['axes'], problem['roles']
    need(type(n) is int and 1 <= n <= 256, 'axes must be in 1..256')
    need(type(r) is int and 1 <= r <= 4096, 'roles must be in 1..4096')
    need(isinstance(problem['generators'], dict), 'generator table required')
    generators = {}
    for name, data in problem['generators'].items():
        need(isinstance(name, str) and bool(name), 'generator name required')
        generators[name] = Native.parse(data, n)
    for program in (problem['program'], problem['reference']):
        need(isinstance(program, list), 'instruction list required')
        for instruction in program:
            need(isinstance(instruction, dict), 'instruction object required')
            op = instruction.get('op')
            fields = {'add': {'op', 'src', 'dst', 'coefficient'},
                      'query': {'op', 'src', 'dst', 'coefficient', 'generator', 'inverse'},
                      'apply': {'op', 'dst', 'generator', 'inverse'},
                      'scale': {'op', 'dst', 'coefficient'},
                      'swap': {'op', 'src', 'dst'}}
            need(isinstance(op, str) and op in fields and set(instruction) <= fields[op], 'instruction fields')
            need('dst' in instruction, 'destination required')
            if op in ('add', 'query', 'swap'):
                need('src' in instruction, 'source required')
            for key in ('src', 'dst'):
                if key in instruction:
                    need(type(instruction[key]) is int and 0 <= instruction[key] < r, 'role index')
            if op in ('query', 'apply'):
                need(isinstance(instruction.get('generator'), str) and instruction['generator'] in generators,
                     'known native generator required')
                need(type(instruction.get('inverse', False)) is bool, 'inverse flag')
            if 'coefficient' in instruction:
                scalar(instruction['coefficient'])
    return generators


def add_term(row, key, value):
    new = row.get(key, QI()) + value
    if new:
        row[key] = new
    else:
        row.pop(key, None)


def endpoint(problem, instructions, generators, max_terms=100000):
    need(type(max_terms) is int and max_terms >= problem['roles'], 'expanded-term limit exceeded; no decision')
    identity = Native.identity(problem['axes'])
    state = [{(i, identity): QI(1)} for i in range(problem['roles'])]
    inverses = {}
    peak = len(state)
    for instruction in instructions:
        op, d = instruction['op'], instruction['dst']
        if op == 'swap':
            s = instruction['src']
            state[s], state[d] = state[d], state[s]
        elif op == 'scale':
            c = scalar(instruction.get('coefficient', 1))
            state[d] = {key: c * value for key, value in state[d].items()} if c else {}
        else:
            s = d if op == 'apply' else instruction['src']
            old = list(state[s].items())
            c = scalar(instruction.get('coefficient', 1))
            if op in ('apply', 'query'):
                name = instruction['generator']
                g = generators[name]
                if instruction.get('inverse', False):
                    if name not in inverses:
                        inverses[name] = g.inv()
                    g = inverses[name]
                old = [((i, g.compose(h)), value) for (i, h), value in old]
            if op == 'apply':
                state[d] = {}
            for key, value in old:
                add_term(state[d], key, c * value)
        size = sum(map(len, state))
        need(size <= max_terms, 'expanded-term limit exceeded; no decision')
        peak = max(peak, size)
    return state, peak


def choose_character(table, n):
    """Choose a nonzero finite Fourier value without enumerating all characters."""
    moduli = [4] * (n + 1) + [2] * (n * (n - 1) // 2)
    chosen = []
    for modulus in moduli:
        for k in range(modulus):
            reduced = {}
            for key, coefficient in table.items():
                add_term(reduced, key[1:], coefficient * unit((4 // modulus) * k * key[0]))
            if reduced:
                table = reduced
                chosen.append(k)
                break
        else:
            raise ValueError('nonzero Fourier invariant failed')
    need(set(table) == {()}, 'complete Fourier projection')
    return chosen, table[()]


def decide(problem, max_terms=100000):
    need(type(max_terms) is int and max_terms >= 1, 'positive expanded-term limit')
    generators = validate(problem)
    left, p = endpoint(problem, problem['program'], generators, max_terms)
    right, q = endpoint(problem, problem['reference'], generators, max_terms)
    residual = []
    for a, b in zip(left, right):
        row = dict(a)
        for key, value in b.items():
            add_term(row, key, -value)
        residual.append(row)
    n = problem['axes']
    result = {'schema': 'native-tensor-cutoff/v1', 'problem_sha256': digest(problem),
              'axes': n, 'roles': problem['roles'], 'window': [2 * n + 4, 2 * n + 7],
              'peak_expanded_terms': max(p, q), 'residual_terms': sum(map(len, residual))}
    if not any(residual):
        result['status'] = 'IDENTITY_ALL_POSITIVE_WIDTHS'
        return result
    o = next(i for i, row in enumerate(residual) if row)
    source, g = next(iter(residual[o]))
    table = {h.phase_key(): value for (i, h), value in residual[o].items()
             if i == source and h.rows == g.rows and h.offset == g.offset}
    character, amplitude = choose_character(table, n)
    points = character_tuple(n, character)
    result.update(status='COUNTEREXAMPLE', input_role=source, output_role=o,
                  input_points=points, output_points=[g.image(x) for x in points],
                  character=character, discrepancy=amplitude.json())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-terms', type=int, default=100000)
    args = parser.parse_args()
    need(args.max_terms >= 1, 'positive expanded-term limit')
    result = decide(json.loads(args.problem.read_text()), args.max_terms)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
