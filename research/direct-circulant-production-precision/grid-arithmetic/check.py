#!/usr/bin/env python3
"""Independent rational oracles and literal-source integration checks."""

import argparse
import ast
from fractions import Fraction as Q
from hashlib import sha1, sha256
import importlib.util
from itertools import product
import json
from math import prod
import operator
from pathlib import Path
import sys
from types import SimpleNamespace

from grid_arithmetic import multiply_grid

HERE = Path(__file__).resolve().parent
RET = HERE / 'retained'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    rows = json.loads((HERE / 'SOURCES.json').read_text())['files']
    for row in rows:
        data = (HERE / row['local']).read_bytes()
        need(sha256(data).hexdigest() == row['sha256'], 'source SHA256 ' + row['local'])
        if 'git_blob' in row:
            actual = sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            need(actual == row['git_blob'], 'source Git blob ' + row['local'])
    return len(rows)


def literal_tensor():
    tree = ast.parse((RET / 'direct/tensor_word.py').read_text())
    names = {'Grid', 'product_diagonal', 'hadamard'}
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))
             and n.name in names]
    need(len(nodes) == 3, 'literal external arithmetic source inventory')
    namespace = {'Fraction': Q, 'word_product': operator.mul, 'prod': prod}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<literal tensor>', 'exec'), namespace)
    return namespace


def nearest(value):
    floor, remainder = divmod(value.numerator, value.denominator)
    return floor + int(remainder + remainder >= value.denominator)


def oracle(u, v, p):
    a, b = (Q(x, 1 << p) for x in u)
    c, d = (Q(x, 1 << p) for x in v)
    return nearest((a*c-b*d)*(1 << p)), nearest((a*d+b*c)*(1 << p))


def one_case(grid_type, b, p, values):
    u, v = tuple(values[:2]), tuple(values[2:])
    wanted = oracle(u, v, p)
    actual, frame = multiply_grid(u, v, p, b)
    need(actual == wanted == grid_type(p).multiply(u, v), 'independent/source/program agreement')
    need(frame.peak <= 2*b+1 and frame.iterations <= 4*b, 'arithmetic width and loop budget')
    need(frame.registers[2:] == [0]*5, 'five nonoutput scratch registers reset')
    need(u == tuple(values[:2]) and v == tuple(values[2:]), 'supplied inputs unchanged')
    return frame.peak


def arithmetic_cases(grid_type):
    count, peak = 0, 0
    for b in (2, 3):
        for p in range(1, b+1):
            for values in product(range(-(1 << (b-1)), 1 << (b-1)), repeat=4):
                peak = max(peak, one_case(grid_type, b, p, values)); count += 1
    for b in (4, 8, 17, 128):
        m = 1 << (b-1)
        for p in sorted({1, b//2, b}):
            for values in product((-m, -1, 0, 1, m-1), repeat=4):
                peak = max(peak, one_case(grid_type, b, p, values)); count += 1
    for b in (1024, 3433, 4924):
        m = 1 << (b-1)
        for p in (1, min(3438, b), b):
            for values in ((-m,)*4, (m-1,)*4, (-m, 0, m-1, 1), (1, -1, 0, 0)):
                peak = max(peak, one_case(grid_type, b, p, values)); count += 1
    return dict(cases=count, maximum_observed_bits=peak)


def scalar_rows(u, p):
    a, b = (Q(x, 1 << p) for x in u)
    values = ((a, -b, Q(0), Q(0)), (b, a, Q(0), Q(0)),
              (Q(0), Q(0), Q(1), Q(0)), (Q(0), Q(0), Q(0), Q(1)))
    return tuple(tuple((x.numerator, x.denominator) for x in row) for row in values)


def predecessor_cases(kernel, grid_type):
    count = 0
    for b in (3, 8, 18):
        for p in (1, b-1):
            for values in product((-3, 0, 3), repeat=4):
                u, v = values[:2], values[2:]
                rows = scalar_rows(u, p)
                c = max(max(abs(n).bit_length(), d.bit_length()) for row in rows for n, d in row)
                state = list(v) + [0, 0]
                kernel.apply_gate(rows, state, b, c)
                need(tuple(state[:2]) == oracle(u, v, p), 'unchanged predecessor scalar binding')
                count += 1
    return count


def compiler_fixture():
    modules = {}
    for name in ('exact', 'engine', 'triangular', 'generator', 'full'):
        modules[name] = load(RET / 'compiler' / (name + '.py'), name)
    g = modules['generator']
    raw = {g.SOURCE+'check_circuits.py': (RET/'compiler/check_circuits.py').read_bytes(),
           g.ORACLE: (RET/'compiler/interval_kernel.py').read_bytes(),
           g.PRODUCER: (RET/'compiler/stein_rational.py').read_bytes(),
           g.PROVENANCE: (RET/'compiler/STEIN-PROVENANCE.json').read_bytes()}
    e, f = modules['exact'], modules['full']
    matrix = e.Mat([[3, 1], [1, 3]])
    lam, q, _ = f.admission(matrix)
    compiler = f.Full(f.allocation(2, lam, q, 1, 1, 0), raw)
    plan = compiler.plan(matrix)
    return modules, compiler, plan


def gate_rows(gate):
    values = [[z for z in row] for row in gate]
    if len(values) == 1:
        zero = values[0][0] * 0
        values = [[values[0][0], zero], [zero, zero+1]]
    rows = []
    for row in values:
        for real in (True, False):
            parts = [v for z in row for v in ((z.re, -z.im) if real else (z.im, z.re))]
            rows.append(tuple((x.numerator, x.denominator) for x in parts))
    return tuple(rows)


def full_events(kernel, modules, compiler, plan):
    e = modules['exact']; f = compiler.bound['data_bits']; scale = 1 << f
    b = f + compiler.bound['integer_bits']; count = 0; maximum = 0
    for atom in plan.atoms:
        for layer in atom['local_plan']:
            for ids, gate in layer:
                h = max(max(abs(n).bit_length(), d.bit_length())
                        for row in gate_rows(gate) for n, d in row)
                need(h <= atom['coefficient_height'], 'actual atom coefficient height')
                maximum = max(maximum, h)
    for initial in ((-7, -2, 3, 4), (1, 0, 0, 1), (0, 0, 0, 0)):
        vector = e.Vec([e.C(Q(initial[j], scale), Q(initial[j+1], scale)) for j in (0, 2)])
        expected, _ = e.apply(plan, vector, f)
        state = [list(initial[:2]), list(initial[2:])]
        for layer in plan:
            for ids, gate in layer:
                rows = gate_rows(gate); before = [part for i in ids for part in state[i]]
                before += [0] * (4-len(before))
                c = max(max(abs(n).bit_length(), d.bit_length()) for row in rows for n, d in row)
                wanted = [nearest(sum((Q(n, d)*x for (n, d), x in zip(row, before)), Q()))
                          for row in rows]
                actual = list(before); kernel.apply_gate(rows, actual, b, c)
                need(actual == wanted, 'actual Full primitive independent row oracle')
                for j, wire in enumerate(ids):
                    state[wire] = actual[2*j:2*j+2]
                count += 1
        wanted = [[int(part*scale) for part in (z.re, z.im)] for z in expected]
        need(state == wanted, 'whole actual source Full word once-rounded replay')
    return dict(events=count, layers=len(plan), gates=sum(map(len, plan)),
                actual_coefficient_height=maximum, declared_height=compiler.bound['coefficient_height_bound'],
                initial_scalar_height=compiler.bound['scalar_height_bound'], data_bits=b, fractional_bits=f)


def chronology_control(grid_type, modules, plan):
    root = load(RET/'direct/root_gate_plan.py', 'binding_root_gate_plan')
    e = modules['exact']; gate = next(g for layer in plan for ids, g in layer if len(ids) == 2)
    grid = grid_type(2); initial = (-1, -1, -1, -1)
    vector = e.Vec([e.C(Q(-1, 4), Q(-1, 4))]*2)
    expected, _ = e.apply([[((0, 1), gate)]], vector, 2)
    once = tuple(int(v*4) for z in expected for v in (z.re, z.im))
    state = [initial[:2], initial[2:]]
    diagonals = [tuple(grid.word(z) for z in diag) for diag in root.lower_pair(gate)]
    need(len(diagonals) == 17, 'literal sixteen-H lowering')
    for j, diag in enumerate(diagonals):
        state = [grid.multiply(diag[k], state[k]) for k in range(2)]
        if j < 16:
            (a, b), (c, d) = state; state = [(a+c, b+d), (a-c, b-d)]
    lowered = tuple(v for z in state for v in z)
    need(once == initial and lowered == (0, 0, 0, 0), 'lowered and once-rounded semantics differ')
    return dict(gate=[[z.record() for z in row] for row in gate], fractional_bits=2,
                inputs=initial, once_rounded=once, lowered=lowered)


def cache_cases(namespace):
    base = namespace['Grid']; count = 0; calls = 0; zeros = 0
    class CheckedGrid(base):
        def multiply(self, u, v):
            nonlocal calls, zeros
            value, frame = multiply_grid(u, v, self.bits, self.bits+32)
            need(value == super().multiply(u, v), 'literal cache multiplication value')
            calls += 1; zeros += int(u == (0, 0) or v == (0, 0))
            return value
    for p in (2, 7):
        q = 1 << p
        factors = [(0, 0), (q, 0), (-q, 0), (0, q), (q//2, -q//2)]
        for offset in range(5):
            tables = [tuple(factors[(offset+j+k)%5] for j in range(size))
                      for k, size in enumerate((2, 3, 2))]
            before = [(q//4, -q//4)]*12
            reference, actual = list(before), list(before)
            namespace['product_diagonal'](reference, tables, base(p))
            earlier_calls = calls
            namespace['product_diagonal'](actual, tables, CheckedGrid(p))
            need(actual == reference, 'literal odometer output with replacement local arithmetic')
            need(calls-earlier_calls <= (len(tables)+1)*len(actual), 'literal per-scan call charge')
            count += 1
    return dict(scans=count, multiply_calls=calls, zero_factor_calls=zeros)


def semantic_controls(grid_type):
    g = grid_type(2)
    need(g.word(Q(1, 8)) == (0, 0) and g.multiply((1, 0), (2, 0)) == (1, 0),
         'coefficient ties-even cannot replace multiplication ties-positive')
    need(grid_type(1).multiply((-1, 0), (1, 0)) == (0, 0), 'negative halfway tie')
    need(g.multiply((0, 2), (0, 2)) == (-1, 0), 'real product sign')
    need(grid_type(1).multiply((1, 1), (1, 1)) == (0, 1), 'sum before rounding')
    need(nearest(Q(1, 2))+nearest(Q(1, 2)) == 2, 'per-product rounding mutation differs')
    need(grid_type(1).multiply((1, 2), (3, 4)) == (-2, 5), 'saved input example')
    need(((-2)*4+2*3+1) >> 1 == -1, 'premature overwrite mutation differs')
    for b in (2, 8, 128):
        m = 1 << (b-1)
        try:
            multiply_grid((-m, -m), (-m, -m), b, b, diagnostic_width=2*b)
        except OverflowError:
            continue
        raise ValueError('underallocated signed arithmetic word accepted')
    for args in (((1, 0), (1, 0), 0, 2), ((1, 0), (1, 0), 3, 2),
                 ((2, 0), (1, 0), 1, 2), ((True, 0), (1, 0), 1, 2)):
        try:
            multiply_grid(*args)
        except ValueError:
            continue
        raise ValueError('invalid new-program domain accepted')
    return dict(semantic=7, insufficient_width=3, invalid_domain=4)


def literal_mutants():
    source = (RET/'direct/tensor_word.py').read_text()
    recipes = [('word_product(a,d)+word_product(b,c)+half',
                'word_product(a,d)-word_product(b,c)+half', 2, (1, 2), (3, 4)),
               ('+half', '', 1, (1, 0), (1, 0)),
               ('word_product(a,d)', 'word_product(a,c)', 1, (1, 0), (0, 2)),
               ('>> self.bits', '>> (self.bits+1)', 1, (3, 0), (3, 0))]
    for old, new, p, u, v in recipes:
        need(old in source, 'literal mutation target exists')
        tree = ast.parse(source.replace(old, new))
        node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Grid')
        ns = {'Fraction': Q, 'word_product': operator.mul}
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<literal arithmetic mutant>', 'exec'), ns)
        need(ns['Grid'](p).multiply(u, v) != oracle(u, v, p), 'independent oracle kills literal mutant')
    return len(recipes)


def production_binding(kernel, grid_type):
    precision = load(RET/'precision.py', 'binding_precision')
    budget = precision.precision_budget(30, (1,)); p = budget.fractional_bits
    a, e = budget.local_error_exponent, budget.interval_exponent
    b = p+max(a, e)+3; w = 2*b+1
    tree = ast.parse((RET/'direct/product.py').read_text())
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Multiplier')
    operand = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == 'operand')
    helpers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('digits', 'ordinal')]
    ns = {'prod': prod}; exec(compile(ast.Module(body=helpers+[operand], type_ignores=[]),
                                   '<literal operand before routing>', 'exec'), ns)
    caller = SimpleNamespace(widths=(2,), sides=(2,), size=2, base=32,
                             grid=grid_type(p), crt=lambda x: x)
    field, used = ns['operand'](caller, 1)
    numerator = field[0][0]
    need(used == 1 and numerator == 1 << 3431 and p == 3438, 'literal production operand')
    state = [numerator, 0, 0, 0]; before = tuple(state)
    identity = tuple(tuple((int(i == j), 1) for j in range(4)) for i in range(4))
    try:
        kernel.apply_gate(identity, state, numerator.bit_length()+1, 1)
    except ValueError as exc:
        need(str(exc) == 'data width' and tuple(state) == before, 'literal finite API guard preserved')
    else:
        raise ValueError('capped predecessor incorrectly admitted production operand')
    value, frame = multiply_grid(field[0], (1 << p, 0), p, b)
    need(value == field[0] and frame.peak <= w, 'new all-width program production identity call')
    return dict(P=p, A=a, E=e, B=b, W=w, local_data_bits=4*b+7*w,
                operand_numerator_exponent=3431, required_signed_input_bits=numerator.bit_length()+1)


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path)
    args = parser.parse_args(); sources = authenticate(); namespace = literal_tensor()
    kernel = load(RET/'kernel.py', 'preserved_predecessor_kernel')
    modules, compiler, plan = compiler_fixture()
    receipt = dict(marker='PASS_SUPPLIED_GRID_ARITHMETIC_BINDING', sources=sources,
        arithmetic=arithmetic_cases(namespace['Grid']),
        predecessor_scalar_cases=predecessor_cases(kernel, namespace['Grid']),
        actual_full=full_events(kernel, modules, compiler, plan),
        chronology=chronology_control(namespace['Grid'], modules, plan),
        odometer=cache_cases(namespace), controls=semantic_controls(namespace['Grid']),
        literal_source_mutants=literal_mutants(),
        production=production_binding(kernel, namespace['Grid']))
    receipt['proof_sha256'] = sha256((HERE/'PROOF.md').read_bytes()).hexdigest()
    receipt['program_sha256'] = sha256((HERE/'grid_arithmetic.py').read_bytes()).hexdigest()
    payload = json.dumps(receipt, sort_keys=True, indent=2)+'\n'
    if args.output:
        args.output.write_text(payload)
    print(payload, end='')


if __name__ == '__main__':
    main()
