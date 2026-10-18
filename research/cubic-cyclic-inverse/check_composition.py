"""Dense exact-reference composition and cancellation checks, no floats."""
import hashlib
import importlib.util
import json
import argparse
from pathlib import Path

P = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = load('composition', P/'composition.py')
s, F = c.s, c.F
# Separate already-tested matrix implementation; it does not import composition.
o = load('oracle', P/'dense.py')


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    out = parser.parse_args().out.resolve()
    s.need(not out.is_relative_to(P), 'output must be outside the source package')
    out.mkdir(parents=True, exist_ok=False)
    source = json.loads((P/'SOURCE.json').read_text())
    for path, digest in source['files'].items():
        s.need(hashlib.sha256((P/path).read_bytes()).hexdigest() == digest, 'source hash')
    units = [s.ONE, (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))]
    stages = [(0, 1, 0, 1), (1, 2, 1, -1), (2, 0, 0, 1),
              (0, 2, 1, 1), (2, 1, 0, -1), (1, 0, 1, 1)]
    results, controls = [], []
    for n in (1, 2, 3, 8, 17):
        for beta in (F(1, 2), F(1, 16)):
            for direction in (-1, 1):
                roots = [(F(3, 5)*(1-beta), F(4, 5)*(1-beta)),
                         s.div(s.ONE, (F(-5, 13)*(1-beta), F(12, 13)*(1-beta)))]
                factors = [(roots[0], beta, lambda i: units[(i*i+3*i+1) % 4], direction),
                           (roots[1], beta, lambda i: units[(3*i+2) % 4], -direction)]
                operators = [(factors, 3), (list(reversed(factors)), 2)]
                # Cover the six-stage word and its six-stage cancellation.
                budget = c.plan(operators, F(1), 12, 40)
                original = [[(F((i*5+j*3)%7-3, 16), F((i*7+j*2)%11-5, 16))
                             for i in range(n)] for j in range(3)]
                arrays = [row[:] for row in original]
                c.word(arrays, operators, stages, budget)
                s.need(all(v == s.rnd(v, budget['coarse_bits']) for row in arrays for v in row), 'closed coarse grid')
                if n <= 3:
                    expected = [row[:] for row in original]
                    for src, dst, op, sign in stages:
                        factors, scale = operators[op]
                        value = o.oracle(expected[src], factors, scale)
                        expected[dst] = [o.plus(a, (sign*b[0], sign*b[1])) for a, b in zip(expected[dst], value)]
                    for a, b in zip(arrays, expected):
                        o.close(a, b, budget['total_error_bound'], 'dense composed shear error')
                c.word(arrays, operators, c.inverse_word(stages), budget)
                s.need(arrays == original, 'exact whole-word cancellation')
                results.append(dict(length=n, beta=str(beta), direction=direction,
                                    dense=n<=3, exact_cancellation=True,
                                    budget={key:str(value) for key, value in budget.items()}))
    def reject(name, fn):
        try: fn()
        except ValueError as error: controls.append(dict(name=name, rejected=str(error)))
        else: raise ValueError('accepted '+name)
    operators = [([((F(4), F(0)), F(1, 2), lambda i:s.ONE, 1)], 1)]
    budget = c.plan(operators, F(1), 4, 40)
    original = [[(F(1, 4), F(0))], [(F(1, 2), F(0))]]
    two = [(0, 1, 0, 1), (1, 0, 0, 1)]
    arrays = [row[:] for row in original]
    c.word(arrays, operators, two, budget)
    c.word(arrays, operators, [(a,b,k,-sign) for a,b,k,sign in two], budget)
    reject('inverse_signs_without_reversing_order', lambda:s.need(arrays == original, 'cancellation mismatch'))
    a = original[0][:]
    reject('aliased_registers', lambda:c.word([a,a], operators, two, budget))
    bad = [[(F(1, 1 << (budget['coarse_bits']+1)), F(0))], original[1][:]]
    reject('fine_grid_source', lambda:c.word(bad, operators, two, budget))
    bad = [original[0][:], [(F(1, 1 << (budget['coarse_bits']+1)), F(0))]]
    reject('fine_grid_target', lambda:c.word(bad, operators, two, budget))
    result = dict(status='passed', cases=results, controls=controls,
                  constant_working_precision_per_word=True, borrowed_arrays=0,
                  reserved_low_zero_bits_required=True, common_label_compilation=False,
                  new_kappa=False)
    (out/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status='passed', cases=len(results), dense=sum(r['dense'] for r in results), controls=len(controls))))


if __name__ == '__main__': run()
