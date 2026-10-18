"""Source-bound fixed precision planner; Python standard library, exact arithmetic."""
import argparse
import ast
import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
SOURCE = ROOT / 'research/cubic-cyclic-inverse'
REQUIRED = ('composition.py', 'source_scan.py', 'dense.py', 'check_composition.py',
            'COMPOSITION-PROOF.md', 'PROOF.md', 'README.md', 'NOTICE.md', 'SOURCE.json')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(json.loads(json.dumps(value)), sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def check_sources():
    pins = json.loads((P / 'SOURCES.json').read_text())
    names = {'research/cubic-cyclic-inverse/' + x for x in REQUIRED}
    need(set(pins['files']) == names, 'source inventory')
    for path, expected in pins['files'].items():
        need(digest(ROOT / path) == expected, 'source hash: ' + path)
    snapshot = json.loads((P / 'BASE-SELECTED.json').read_text())
    need(digest(P / 'BASE-SELECTED.json') == pins['selected_snapshot_sha256'], 'selected snapshot')
    need(pins['base_commit'] == '2921874911956718fcaaaf9396fe8267b3cfa9f0', 'base')
    return snapshot


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_stages():
    tree = ast.parse((SOURCE / 'check_composition.py').read_text())
    matches = [node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'stages' for t in node.targets)]
    need(len(matches) == 1, 'unique source word')
    stages = ast.literal_eval(matches[0])
    need(len(stages) == 6, 'source stage count')
    return stages


def recurrence(bounds, stages, registers, initial=F(1)):
    need(type(registers) is int and registers > 0 and initial >= 0, 'register contract')
    magnitude, error = [F(initial)] * registers, [F(0)] * registers
    rows = []
    for source, target, operator, sign in stages:
        need(type(source) is int and type(target) is int and 0 <= source < registers
             and 0 <= target < registers and source != target, 'distinct legal ports')
        need(type(operator) is int and 0 <= operator < len(bounds)
             and bounds[operator] >= 0 and sign in (-1, 1), 'operator contract')
        a = bounds[operator]
        magnitude[target] += a * magnitude[source] + 1
        error[target] += a * error[source] + 1
        rows.append(dict(magnitude=list(map(str, magnitude)), error_units=list(map(str, error))))
    need(rows, 'empty planned word')
    return max(magnitude), max(error), rows


def plan(c, operators, stages, registers, initial, target_bits):
    need(type(target_bits) is int and target_bits > 0, 'target precision')
    bounds = [c.operator_bound(*operator) for operator in operators]
    bound, units, rows = recurrence(bounds, stages, registers, initial)
    coarse = max(target_bits, 1)
    while 2 * units * F(1, 1 << coarse) > F(1, 1 << target_bits):
        coarse += 1
    working = max(c.s.working_bits(factors, scale, bound, coarse, coarse)
                  for factors, scale in operators)
    return dict(coarse_bits=coarse, working_bits=working, bound=bound,
                stage_error_bound=2 * F(1, 1 << coarse),
                total_error_bound=2 * units * F(1, 1 << coarse)), rows


def matrices(bounds, stages, registers, initial):
    """Independent affine matrix product; no use of the update recurrence."""
    size = registers + 1
    product = [[F(i == j) for j in range(size)] for i in range(size)]
    rows = []
    for source, target, operator, _ in stages:
        gate = [[F(i == j) for j in range(size)] for i in range(size)]
        gate[target][source] = bounds[operator]
        gate[target][-1] = 1
        product = [[sum(gate[i][k] * product[k][j] for k in range(size))
                    for j in range(size)] for i in range(size)]
        rows.append(dict(magnitude=[str(sum(row[:-1]) * initial + row[-1])
                                    for row in product[:-1]],
                         error_units=[str(row[-1]) for row in product[:-1]]))
    return rows


def run():
    check_sources()
    c = load('source_composition53', SOURCE / 'composition.py')
    oracle = load('source_dense53', SOURCE / 'dense.py')
    forward = source_stages()
    whole = forward + c.inverse_word(forward)
    units = [c.s.ONE, (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))]
    results, controls = [], []
    calls = dict(shears=0, inverse_factors=0, restoration_factors=0,
                 phase_evaluations=0, complex_add=0, complex_mul=0,
                 complex_div=0, complex_round=0)
    originals = {name: getattr(c.s, name) for name in ('add', 'mul', 'div', 'rnd')}
    for name, key in [('add', 'complex_add'), ('mul', 'complex_mul'),
                      ('div', 'complex_div'), ('rnd', 'complex_round')]:
        def wrapped(*args, _fn=originals[name], _key=key, **kwargs):
            calls[_key] += 1
            return _fn(*args, **kwargs)
        setattr(c.s, name, wrapped)
    for length in (1, 2, 3, 8, 17):
        for beta in (F(1, 2), F(1, 16)):
            for direction in (-1, 1):
                roots = [(F(3, 5)*(1-beta), F(4, 5)*(1-beta)),
                         c.s.div(c.s.ONE, (F(-5, 13)*(1-beta), F(12, 13)*(1-beta)))]
                def phase1(i): return units[(i*i+3*i+1) % 4]
                def phase2(i): return units[(3*i+2) % 4]
                factors = [(roots[0], beta, phase1, direction),
                           (roots[1], beta, phase2, -direction)]
                operators = [(factors, 3), (list(reversed(factors)), 2)]
                new, trace = plan(c, operators, whole, 3, F(1), 40)
                old = c.plan(operators, F(1), len(whole), 40)
                bounds = [c.operator_bound(*op) for op in operators]
                need(trace == matrices(bounds, whole, 3, F(1)), 'independent affine recurrence')
                need(new['coarse_bits'] < old['coarse_bits'] and
                     new['working_bits'] < old['working_bits'], 'strict bit-budget saving')
                need(new['total_error_bound'] <= F(1, 1 << 40), 'final accuracy admission')
                original = [[(F((i*5+j*3)%7-3, 16), F((i*7+j*2)%11-5, 16))
                             for i in range(length)] for j in range(3)]
                arrays, exact = [row[:] for row in original], [row[:] for row in original]
                prefix_checks = 0
                before = dict(calls)
                # Counter scope is literal execution including validation and phase reads.
                counted_operators = []
                for factor_list, scale in operators:
                    new_factors = []
                    for rho, margin, phase, sign in factor_list:
                        def counted_phase(i, _phase=phase):
                            calls['phase_evaluations'] += 1
                            return _phase(i)
                        new_factors.append((rho, margin, counted_phase, sign))
                    counted_operators.append((new_factors, scale))
                for k, stage in enumerate(whole):
                    src, dst, op, sign = stage
                    saved = arrays[src][:]
                    c.word(arrays, counted_operators, [stage], new)
                    calls['shears'] += 1
                    calls['inverse_factors'] += len(operators[op][0])
                    calls['restoration_factors'] += len(operators[op][0])
                    need(arrays[src] == saved, 'exact source restoration')
                    need(all(v == originals['rnd'](v, new['coarse_bits']) for row in arrays for v in row), 'coarse-grid closure')
                    for j, row in enumerate(arrays):
                        limit = F(trace[k]['magnitude'][j])
                        need(all(c.s.norm2(v) <= limit*limit for v in row), 'prefix magnitude')
                    if length <= 3:
                        value = oracle.oracle(exact[src], *operators[op])
                        exact[dst] = [oracle.plus(a, (sign*b[0], sign*b[1]))
                                      for a, b in zip(exact[dst], value)]
                        for j in range(3):
                            limit = F(trace[k]['error_units'][j]) * new['stage_error_bound']
                            oracle.close(arrays[j], exact[j], limit, 'dense prefix error')
                        prefix_checks += 1
                need(arrays == original, 'exact entire inverse restoration')
                invoice = {key: calls[key]-before[key] for key in calls}
                results.append(dict(length=length, beta=str(beta), direction=direction,
                                    old={key:str(value) for key,value in old.items()},
                                    new={key:str(value) for key,value in new.items()},
                                    prefix_trace=trace, dense_prefixes=prefix_checks,
                                    invoice=invoice, exact_restoration=True))
    def reject(name, fn):
        try: fn()
        except ValueError: controls.append(name)
        else: raise ValueError('accepted mutation: ' + name)
    reject('aliased_ports', lambda: recurrence([F(2)], [(0,0,0,1)], 2))
    reject('bad_operator', lambda: recurrence([F(2)], [(0,1,1,1)], 2))
    reject('negative_norm', lambda: recurrence([F(-1)], [(0,1,0,1)], 2))
    reject('zero_sign', lambda: recurrence([F(2)], [(0,1,0,0)], 2))
    # A two-gate dependency amplifies the first error; 1+1 is invalid.
    _, bound, _ = recurrence([F(3)], [(0,1,0,1),(1,0,0,1)], 2)
    reject('omit_propagated_error', lambda: need(bound == 2, 'propagation'))
    new, _ = plan(c, operators, whole, 3, F(1), 40)
    _, e, _ = recurrence([c.operator_bound(*op) for op in operators], whole, 3)
    reject('one_coarse_bit_too_few', lambda: need(2*e*F(1,1 << (new['coarse_bits']-1)) <= F(1,1 << 40), 'coarse admission'))
    short, _ = plan(c, operators, forward, 3, F(1), 40)
    reject('unplanned_inverse_budget', lambda: need(short['bound'] >= new['bound'], 'whole-word magnitude'))
    return dict(schema=1, status='passed', source_stages=[list(x) for x in forward],
                cases=results, mathematical_controls=controls,
                source_cases=len(results), dense_prefix_checks=sum(x['dense_prefixes'] for x in results),
                complete_planned_stages=12, new_kappa=False,
                physical_tape_invoice=False, arbitrary_dirty_low_bits=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-certificate', type=Path)
    args = parser.parse_args()
    result = run()
    if args.write_certificate:
        with args.write_certificate.open('x', encoding='utf-8', newline='\n') as f:
            json.dump(result, f, indent=2); f.write('\n')
    else:
        need(canonical(result) == canonical(json.loads((P / 'EXPECTED.json').read_text())), 'certificate mismatch')
    print('PASS_WORD_PRECISION53 cases=%d dense_prefixes=%d controls=%d' %
          (result['source_cases'], result['dense_prefix_checks'], len(result['mathematical_controls'])))


if __name__ == '__main__':
    main()
