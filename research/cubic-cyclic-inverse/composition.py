"""Fixed coarse-grid nonlinear shears with exact inverse cancellation."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('coarse_source', Path(__file__).with_name('source_scan.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
F = s.F


def shear(x, y, factors, scale, bound, coarse_bits, bits, sign=1):
    s.need(sign in (-1, 1), 'sign')
    s.need(all(v == s.rnd(v, coarse_bits) for v in y), 'target coarse grid')
    # Set inverse execution error <= one coarse ulp. Final increment rounding
    # adds at most one further coarse ulp in complex modulus.
    error, recovery = s.validate(x, y, factors, scale, bound, coarse_bits, bits, coarse_bits)
    for i in range(len(x)):
        x[i] = (x[i][0]*scale, x[i][1]*scale)
    for factor in factors:
        s.inverse_factor(x, factor, bits)
    for i in range(len(x)):
        increment = s.rnd(x[i], coarse_bits)
        y[i] = s.add(y[i], (sign*increment[0], sign*increment[1]))
    for factor in reversed(factors):
        s.forward_factor(x, factor, bits)
    for i in range(len(x)):
        x[i] = s.rnd(s.rnd((x[i][0]/scale, x[i][1]/scale), bits), coarse_bits)
    return error+F(1, 1 << coarse_bits), recovery


def operator_bound(factors, scale):
    result = F(scale)
    for _, beta, _, _ in factors:
        result /= beta
    return result


def plan(operators, initial_bound, stage_count, target_bits):
    """Uniform data-grid and working-grid budgets for any selected word.

    Operators are (factor_list, positive_integral_scale). The word's stages
    may target different arrays and use either sign; source/target differ.
    Bound and stage_count must cover the entire execution being planned.
    """
    s.need(operators and stage_count > 0 and initial_bound >= 0 and target_bits > 0, 'plan parameters')
    C = 1+max(operator_bound(factors, scale) for factors, scale in operators)
    bound = (C+1)**stage_count*(initial_bound+1)
    coarse_bits = target_bits
    while 2*stage_count*C**(stage_count-1)*F(1, 1 << coarse_bits) > F(1, 1 << target_bits):
        coarse_bits += 1
    bits = max(s.working_bits(factors, scale, bound, coarse_bits, coarse_bits)
               for factors, scale in operators)
    error = 2*stage_count*C**(stage_count-1)*F(1, 1 << coarse_bits)
    return dict(coarse_bits=coarse_bits, working_bits=bits, bound=bound,
                operator_growth=C, stage_error_bound=2*F(1, 1 << coarse_bits),
                total_error_bound=error)


def word(arrays, operators, stages, budget):
    s.need(len({id(a) for a in arrays}) == len(arrays), 'aliased register arrays')
    for source, target, which, sign in stages:
        s.need(source != target, 'self target')
        factors, scale = operators[which]
        shear(arrays[source], arrays[target], factors, scale, budget['bound'],
              budget['coarse_bits'], budget['working_bits'], sign)


def inverse_word(stages):
    return [(source, target, which, -sign) for source, target, which, sign in reversed(stages)]
