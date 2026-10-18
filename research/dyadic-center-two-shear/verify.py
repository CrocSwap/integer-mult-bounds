#!/usr/bin/env python3
"""Source-pinned finite verification; not a full multiplication proof."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from circuit import candidate, shear, price, second_shear_census, require


def canonical(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): canonical(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical(v) for v in value]
    return value


def encoded(value):
    return json.dumps(canonical(value), sort_keys=True, separators=(',', ':')).encode()


def check_pins():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    require(pins['base_commit'] == '91a2094f2e022930069e8cfdc810a3ea1b81cd09', 'wrong base pin')
    require(sha256((HERE/'BASE-SELECTED.json').read_bytes()).hexdigest() == pins['base_selected_sha256'], 'base selection snapshot mismatch')
    for name, digest in pins['sha256'].items():
        path = (ROOT/name).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'invalid source path')
        require(sha256(path.read_bytes()).hexdigest() == digest, 'source mismatch: '+name)
    return pins


class Linear:
    """One sparse rational execution represents all independent input columns."""
    def __init__(self, values):
        self.values = {k: Q(v) for k, v in values.items() if v}
    def __add__(self, other):
        if other == 0:
            return self
        result = dict(self.values)
        for k, v in other.values.items():
            result[k] = result.get(k, 0) + v
        return Linear(result)
    __radd__ = __add__
    def __mul__(self, value):
        return Linear({k: v*value for k, v in self.values.items()})
    __rmul__ = __mul__
    def __sub__(self, other):
        return self + other*(-1)
    def __eq__(self, other):
        return isinstance(other, Linear) and self.values == other.values


def rejection(fn, label):
    try:
        fn()
    except (ValueError, AssertionError):
        return label
    raise ValueError('control unexpectedly accepted: '+label)


def run():
    check_pins()
    # Keep inherited assertion-based admission checks enabled even if the
    # public command is invoked with Python -O (handled by main below).
    require(not sys.flags.optimize, 'inherited checks require normal Python')
    sys.path.insert(0, str(ROOT/'scripts'))
    from experiments.complex_centers import factor, verify_factor, counts, invoke
    from experiments.disjoint_tensor import DisjointTensor, scalar_program
    from complex_compression import saving_bounds, matching, LeaveOneCircuit
    from general_network_guard import guard
    from independent import verify as independent_verify
    from cost_census import census as instruction_census

    original = factor(26)
    new = candidate(original)
    old_check, new_check = verify_factor(original), verify_factor(new)
    old_price, new_price = price(original), price(new)
    previous = price(shear(original, 1, 2, -1))
    census = second_shear_census(original)
    require(census['domain'] == 1300 and census['admissible'] == 602 and
            census['best_cost'] == 43128 and census['best_moves'] == [[2, 0, 1]],
            'second-shear census changed')
    # The further algebraic simplification is not part of that finite search.
    via_discovery = shear(shear(shear(original, 1, 2, -1), 2, 0, 1), 1, 2, 1)
    require(via_discovery == new, 'discovery and direct two-shear words disagree')
    require(new_price == {'G': 10100, 'H': 32500, 'G_plus_H': 42600}, 'price changed')

    tensor = DisjointTensor(26)
    side = tensor.verify()
    frames = tensor.verify_frames()
    code = scalar_program(tensor)
    n = counts(26, side['roles'])
    M = sum(len(ins)+len(outs)-2 for ins, outs in code['gates'])
    C, J = len(code['sources']), len(code['outputs'])
    def steps(p):
        return 3*n['v']**2*(4*M+2*C+4*J+2*p['G']+2*p['H'])
    old_steps, new_steps = steps(old_price), steps(new_price)
    emitted_counts = {}
    for label, f, bound in [('baseline', original, old_steps), ('candidate', new, new_steps)]:
        for inverse in (False, True):
            emitted = instruction_census(invoke, code, f, inverse=inverse)
            require(3*n['v']**2*emitted['total'] == bound, 'emitted instruction invoice mismatch')
            emitted_counts[label+('_inverse' if inverse else '_forward')] = emitted
    E = 64*(n['W']+n['m']+1)**3
    slack = E-(4*new_steps+8*n['s']+8*n['W']+8*n['m'])
    require(slack > 0 and new_steps < old_steps, 'complete cost not improved')
    recurrence = guard(n['m'], n['s'], E, Q(1,100), Q(1,1000), Q(5))
    bounds = saving_bounds(n)
    labels, pi = matching(26)
    require(len(set(pi)) == n['v'] and all(any(i not in S and i not in labels[j]
            for i in range(26)) for S,j in zip(labels, pi)), 'shared matching fails')

    symbolic = []
    for h in (8, 10):
        f = candidate(factor(h))
        c = scalar_program(DisjointTensor(h))
        v, r = len(f['triples']), c['roles']
        for inverse in (False, True):
            values = [Linear({i:1}) for i in range(2*v+r+h)]
            banks = [values[:v], values[v:2*v], values[2*v:2*v+r], values[2*v+r:]]
            old = [list(b) for b in banks]
            invoke(*banks, c, f, inverse=inverse)
            require(banks[0] == old[0] and banks[2:] == old[2:], 'dirty restoration fails')
            sign = -1 if inverse else 1
            require(banks[1] == [b+sign*a for a,b in zip(old[0],old[1])], 'full scalar identity fails')
            symbolic.append({'h':h, 'inverse':inverse, 'independent_columns':len(values)})

    dense = []
    for trial in range(2):
        for inverse in (False, True):
            sizes = [n['v'], n['v'], code['roles'], 26]
            banks = [[Q(((i+1)*(17+trial*6)+j*11)%41-20, 8) for i in range(size)]
                     for j,size in enumerate(sizes)]
            old = [list(b) for b in banks]
            invoke(*banks, code, new, inverse=inverse)
            sign = -1 if inverse else 1
            require(banks[0] == old[0] and banks[2:] == old[2:] and
                    banks[1] == [b+sign*a for a,b in zip(old[0],old[1])], 'h26 dense replay fails')
            dense.append({'trial':trial,'inverse':inverse,'sha256':sha256(encoded(banks)).hexdigest()})

    # Three signed stages, including actual reuse of the first dirty bank.
    h = 8; f = candidate(factor(h)); c = scalar_program(DisjointTensor(h)); v = len(f['triples'])
    x = [Q(i-7,8) for i in range(v)]; y = [Q(2*i+3,4) for i in range(v)]
    a = [Q(i%17-8,16) for i in range(c['roles'])]; z = [Q(i-3,8) for i in range(h)]
    b = [Q(i%13+2,8) for i in range(c['roles'])]; w = [Q(i+2,4) for i in range(h)]
    old = [list(row) for row in (x,y,a,z,b,w)]
    invoke(x,y,a,z,c,f); invoke(y,x,b,w,c,f,inverse=True); invoke(x,y,a,z,c,f)
    require(x == [-v for v in old[1]] and y == old[0] and [a,z,b,w] == old[2:], 'reused-bank stages fail')

    controls = []
    for label, field in [('missing_conjugate_scatter','scatter'), ('missing_gather_change','gather')]:
        f = candidate(factor(8)); f[field] = factor(8)[field]
        controls.append(rejection(lambda: verify_factor(f), label))
    f = candidate(factor(8)); f['scatter'][0] = (0,)+f['scatter'][0][1:]
    controls.append(rejection(lambda: verify_factor(f), 'wrong_origin_coefficient'))
    f = candidate(factor(8)); f['gather'][0] = ((0,2),)
    controls.append(rejection(lambda: price(f), 'unpriced_gather_double'))
    f = candidate(factor(8)); f['scatter'][0] = (3,)+f['scatter'][0][1:]
    controls.append(rejection(lambda: price(f), 'unpriced_scatter_triple'))
    controls.append(rejection(lambda: shear(original,0,0,1), 'self_shear'))
    # A reversed noncommuting discovery order is a valid factor, but differs
    # from the claimed witness. Do not mislabel it an invalid mathematical map.
    wrong_order = shear(shear(shear(original,1,2,-1),1,2,1),2,0,1)
    require(wrong_order != new, 'order control failed to distinguish witness')

    independent = independent_verify()
    return canonical({'status':'finite historical complex-supplier construction; no new kappa',
        'base_commit':'91a2094f2e022930069e8cfdc810a3ea1b81cd09',
        'selected_kappa':json.loads((HERE/'BASE-SELECTED.json').read_text())['kappa'],
        'baseline':old_price, 'pr809':previous, 'candidate':new_price,
        'factor_sha256':sha256(encoded(new)).hexdigest(),
        'original_coefficient_check':old_check, 'candidate_coefficient_check':new_check,
        'census':{k:v for k,v in census.items() if k != 'rows'},
        'census_rows_sha256':sha256(encoded(census['rows'])).hexdigest(),
        'counts_unchanged':n, 'side':side, 'side_frames':frames,
        'intersection_two':LeaveOneCircuit(24).verify(),
        'emitted_instruction_census':emitted_counts,
        'scalar_invoice':{'M':M,'C':C,'J':J,'before':old_steps,'after':new_steps,
                          'saved':old_steps-new_steps,'saved_vs_pr809':steps(previous)-new_steps,
                          'signed_invocation_saved':2*(old_price['G_plus_H']-new_price['G_plus_H']),
                          'E':E,'slack':slack,'guard':recurrence},
        'historical_saving_bounds_unchanged':bounds,
        'symbolic_full_invocations':symbolic,'dense_h26':dense,'three_stage_reused_bank':True,
        'rejection_controls':controls,'valid_different_order_control':True,'independent':independent})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='write the local EXPECTED.json receipt')
    args = parser.parse_args()
    if sys.flags.optimize:
        subprocess.run([sys.executable,'-I','-B',str(Path(__file__).resolve()), *(['--write'] if args.write else [])], check=True)
        return
    receipt = run()
    path = HERE/'EXPECTED.json'
    if args.write:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    else:
        expected = json.loads(path.read_text())
        require(encoded(receipt) == encoded(expected), 'receipt mismatch')
    print('PASS_DYADIC_CENTER_TWO_SHEAR h=26 G+H=45381->42600 saved=112797360000 no_new_kappa')


if __name__ == '__main__':
    main()
