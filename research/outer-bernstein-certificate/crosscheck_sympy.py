#!/usr/bin/env python3
"""Optional independent symbolic replay; requires SymPy, not package arithmetic.

This second implementation imports none of algebra.py, source_model.py or
verify.py. It expands the same source equations and the committed positive
basis certificate separately through SymPy's rational-polynomial machinery.
Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
import ast
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sympy as S

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def crosscheck():
    receipt = json.loads((HERE / 'EXPECTED.json').read_text())
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    path = 'research/complex-k492-owner-repair/vendor/multicold/engines/outer.py'
    raw = (ROOT / path).read_bytes()
    check(sha256(raw).hexdigest() == pins['files'][path], 'source hash differs')
    variables = S.symbols('u v w z t L R')
    u, v, w, z, t, literal, row = variables
    a = (1-u)*v*w/32
    b, eta = v/32, z/2
    q = a*(1-z)
    denominator = 1+q
    gain = (1-z/2)*q/denominator
    env = dict(bit_saving=a, complex_saving=b, eta=eta, beta=u, kappa=t*gain,
               bridge={'semantic': {'strict_literal_gap': literal},
                       'rows': {'degree_gap': row}})
    branches = {}

    def expression(node):
        if isinstance(node, ast.Constant):
            check(type(node.value) in (str, int), 'nonexact literal')
            return S.Integer(node.value) if type(node.value) is int else node.value
        if isinstance(node, ast.Name):
            return env[node.id]
        if isinstance(node, ast.Tuple):
            return tuple(expression(n) for n in node.elts)
        if isinstance(node, ast.Subscript):
            return expression(node.value)[expression(node.slice)]
        if isinstance(node, ast.BinOp):
            left, right = expression(node.left), expression(node.right)
            operations = {ast.Add: lambda: left+right, ast.Sub: lambda: left-right,
                          ast.Mult: lambda: left*right, ast.Div: lambda: left/right}
            return operations[type(node.op)]()
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name == 'dict':
                return {item.arg: expression(item.value) for item in node.keywords}
            args = [expression(item) for item in node.args]
            if name == 'Q':
                return args[0] if len(args) == 1 else args[0]/args[1]
            if name in ('min', 'max') and len(args) == 2:
                x, y = args
                branches[ast.unparse(node)] = y-x if name == 'max' else x-y
                return y
        raise ValueError('unsupported independent expression')

    function = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef))
    for node in function.body:
        if isinstance(node, ast.Assign):
            value = expression(node.value)
            for target in node.targets:
                if isinstance(target, ast.Tuple):
                    env.update(zip((n.id for n in target.elts), value))
                else:
                    env[target.id] = value
        elif isinstance(node, ast.Expr):
            # Construct the seven charged margins directly, independent of the
            # primary parser's dictionary-comprehension evaluation.
            env['slacks'].update({name+'_above_kappa': value-env['kappa']
                                  for name, value in env['margins'].items()})
        elif isinstance(node, ast.Assert):
            break
    check(len(env['slacks']) == 47 and len(branches) == 2, 'independent row census')
    polys = {'denominator': denominator}
    for prefix, values in (('slack', env['slacks']), ('branch', branches),
                           ('margin', {k: val-env['minimum'] for k, val in env['margins'].items()})):
        polys.update({prefix+':'+name: S.cancel(value*denominator) for name, value in values.items()})
    check(set(polys) == set(receipt['certificates']), 'certificate inventory differs')
    count = 0
    for name, expected in polys.items():
        cert = receipt['certificates'][name]
        degrees, scale, weights = (cert[k] for k in ('degrees', 'scale', 'weights'))
        check(len(degrees) == 7 and all(type(d) is int and 0 <= d <= 8 for d in degrees),
              'invalid certificate degrees')
        check(type(scale) is int and scale > 0, 'invalid certificate scale')
        check(len(weights) == S.prod(d+1 for d in degrees), 'coefficient count differs')
        check(all(type(c) is int and c >= 0 for c in weights), 'negative coefficient')
        check(name == 'margin:compact_phase_layer' or any(weights), 'missing strict term')
        total = S.Integer(0)
        for index, coefficient in zip(product(*(range(d+1) for d in degrees)), weights):
            term = S.Rational(coefficient, scale)
            for axis in range(7):
                term *= variables[axis]**index[axis]
                if axis < 5:
                    term *= S.binomial(degrees[axis], index[axis]) * (1-variables[axis])**(degrees[axis]-index[axis])
            total += term
        # A coefficient identity, not agreement at sampled evaluation points.
        check(S.Poly(S.expand(total-expected), *variables).is_zero, 'symbolic mismatch: '+name)
        count += len(weights)
    identities = [env['margins']['compact_phase_layer']-gain,
                  env['margins']['balanced_prefix']-gain-eta,
                  1-env['eps']-env['r']-eta/2,
                  1-env['eps']*(1+env['c'])-eta+env['eps']*eta/4]
    check(all(S.cancel(p) == 0 for p in identities), 'independent source identity')
    print(f'PASS_SYMPY_OUTER_CERTIFICATE rows={len(polys)} weights={count} identities=4 sympy={S.__version__}')


if __name__ == '__main__':
    crosscheck()
