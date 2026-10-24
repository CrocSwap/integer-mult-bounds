#!/usr/bin/env python3
"""Exact paired-path thinning bound. Apache-2.0; OpenAI Codex assistance.

PROOF.md supplies the infinite-family argument; the census is a source check.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
import importlib.util
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
UPPER, LOWER = Q('0.0030217759'), Q('0.0030217758')
V, D = 112, 8


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Live source pin: '+row['path'])
    row = json.loads((HERE/'FROZEN-SOURCE.json').read_text())
    raw = (HERE/row['snapshot']).read_bytes()
    need(sha256(raw).hexdigest() == row['sha256'], 'Frozen PR4610 bytes')
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
         'Frozen PR4610 Git blob identity')
    source = json.loads(raw)
    h = {int(k): n for k, n in source['local_helpers'].items()}
    p = {int(k): n for k, n in source['local_paid'].items()}
    need(h == {4:28, 7:7, 8:47, 9:326}, 'Named productive profile')
    need(p == {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}, 'Named paid profile')
    return h, p


def interval_engine():
    path = ROOT/'research/higher-moment-strictification/verify.py'
    spec = importlib.util.spec_from_file_location('thinning_exact_intervals', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add(*intervals):
    return tuple(sum(x[i] for x in intervals) for i in (0, 1))


def optimal_sides(count, left, right):
    a = b = 0
    indices = []
    for _ in range(count):
        if left+a+1 <= right+b+1:
            a += 1
            indices.append(left+a)
        else:
            b += 1
            indices.append(right+b)
    return a, b, indices


def canonical(E, H, P, count, flags, saving):
    t, k = 1-saving, count+sum(flags)
    a, b, indices = optimal_sides(count, *flags[:2])
    local = add(E.moment(H, t), E.scale(E.moment(P, t), -1))
    terms = [E.power(1+D*k, t)]
    for j in indices:
        terms.append(add(E.power(1+D*j, t), E.scale(E.power(D*j, t), -1)))
    return add(E.scale(local, k), E.scale(add(*terms), 2*V),
               (Q(-V*(2*count+3-k)),)*2), (a, b)


def inverse(a):
    n = len(a)
    w = [list(map(Q, row))+[Q(i == j) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if w[i][j])
        w[j], w[pivot] = w[pivot], w[j]
        w[j] = [x/w[j][j] for x in w[j]]
        for i in range(n):
            if i != j:
                c = w[i][j]
                w[i] = [x-c*y for x, y in zip(w[i], w[j])]
    return [row[n:] for row in w]


def matmul(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def source_functions(path, names):
    tree = ast.parse(path.read_text())
    tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    need(len(tree.body) == len(names), 'Exact named source functions')
    env = {'Q': Q}
    exec(compile(tree, str(path), 'exec'), env)
    return env


def finite_source_binding():
    source = source_functions(ROOT/'research/kappa-rebuild/bit/complex_controller_factor.py',
                              {'plus', 'monomial_times', 'controller'})
    mask = source_functions(ROOT/'research/query-thinned-controllers/controller.py', {'keep_mask'})['keep_mask']
    cases = 0
    for p in range(1, 6):
        for a in range(p):
            b = p-1-a
            coefficients, _, idles = source['controller'](p, mask(p, a))
            n = 2*p
            total = [[sum(m[i][j] for m in coefficients.values()) for j in range(n)] for i in range(n)]
            inv = inverse(total)
            projectors = {key:matmul(inv, matrix) for key, matrix in coefficients.items()}
            for key, projection in projectors.items():
                need(matmul(projection, projection) == projection, 'Literal source projector')
                need(sum(projection[i][i] for i in range(n)) == 1, 'Rank-one source projector')
                for other, second in projectors.items():
                    if key != other:
                        need(not any(any(row) for row in matmul(projection, second)), 'Orthogonal source projectors')
            expected = [set(range(2*p+1))]+[set(range(2*j+1)) for j in range(1, a+1)]
            expected += [set(range(2*p-2*j, 2*p+1)) for j in range(1, b+1)]
            actual = Counter(tuple(i for i, v in enumerate(key[1:]) if v) for key in projectors)
            need(actual == Counter({tuple(sorted(s)):2 for s in expected}), 'Source diagonal stage sets')
            for bits in product((0, 1), repeat=2*p+1):
                full = {j for j, x in enumerate(bits) if x}
                main = Counter(1+D*len(full.intersection(s)) for s in expected)
                idle = Counter(D*len(full.intersection(row['stages'])) for row in idles if row['retained'])
                idle.pop(0, None)
                other_main, other_idle = Counter({1+D*sum(bits):1}), Counter()
                for end, length, reverse in [(bits[0], a, False), (bits[-1], b, True)]:
                    c = end
                    for j in range(1, length+1):
                        odd, even = ((2*p-2*j+1, 2*p-2*j) if reverse else (2*j-1, 2*j))
                        o, e = bits[odd], bits[even]
                        other_main[1+D*(c+o+e)] += 1
                        if c+o:
                            other_idle[D*(c+o)] += 1
                        c += o+e
                other_idle[D] += sum(bits[2:2*p:2])
                other_idle += Counter()
                need(main == other_main and idle == other_idle, 'Full arbitrary-mask invoice binding')
                surplus = 2*V*(sum(r*n for r, n in main.items())-sum(r*n for r, n in idle.items()))
                surplus -= 1856*sum(bits)+V*(2*p+1-sum(bits))
                need(surplus == 48*sum(bits)-V, 'Rank mass includes every thin query')
                cases += 1
    return cases


def certify():
    H, P = authenticate()
    E = interval_engine()
    derivative = (Q(0), Q(0))
    for r, n in {2:412, 3:510, 4:99, 5:40}.items():
        term = E.mul(E.divide(E.power(r, Q(1,4)), E.power(9, Q(1,4))), E.log_bounds(r))
        derivative = add(derivative, E.scale(term, n))
    for r, n in {7:7, 8:39, 9:326}.items():
        derivative = add(derivative, E.scale(E.log_bounds(r), -Q(n*r, 9)))
    need(derivative[1] < 0, 'Uniform local derivative sign on [1/4,1]')
    need(sum(P.values())-2*sum(H.values()) == 2482 > V+2*V*D*Q(1,4),
         'All 0<t<=1/4 excluded by rational concavity bound')
    maxima = []
    for encoded, count in enumerate([18, 17, 17, 16, 17, 16, 16, 15]):
        flags = tuple((encoded >> j) & 1 for j in range(3))
        current, sides = canonical(E, H, P, count, flags, UPPER)
        previous, _ = canonical(E, H, P, count-1, flags, UPPER)
        following, _ = canonical(E, H, P, count+1, flags, UPPER)
        need(current[0] > previous[1] and current[0] > following[1], 'Discrete concave maximum')
        need(current[1] < 0, 'Entire canonical family fails at upper endpoint')
        maxima.append({'flags':flags, 'side_windows':count, 'sides':sides,
                       'surplus':E.display(current),
                       'previous_difference':E.display(add(current, E.scale(previous, -1))),
                       'following_difference':E.display(add(following, E.scale(current, -1)))})
    low, _ = canonical(E, H, P, 15, (1,1,1), LOWER)
    need(low[0] > 0, 'Tight lower endpoint from p16')
    high, _ = canonical(E, H, P, 15, (1,1,1), UPPER)
    need(high[0]+15*V > 0, 'Control: unpaid queries would falsely pass')
    swap = add(E.power(8, Q(1,2)), E.power(8, Q(1,2)), E.scale(E.power(16,Q(1,2)), -1))
    need(swap[0] > 0, 'Strict even-to-odd swap control')
    # Optimistic relaxation: delete all eight owned rank-eight charges.
    # The local derivative becomes still smaller, so its proved sign persists.
    free_paid = dict(P)
    free_paid[8] -= 8
    need(sum(free_paid.values())-2*sum(H.values()) == 2474 > V+2*V*D*Q(1,4),
         'Small-exponent bound also covers free owned centres')
    free_lower, free_upper = Q('0.0080596238'), Q('0.0080596239')
    free_maxima = []
    for encoded, count in enumerate([7, 6, 6, 5, 6, 5, 5, 4]):
        flags = tuple((encoded >> j) & 1 for j in range(3))
        current, sides = canonical(E, H, free_paid, count, flags, free_upper)
        previous, _ = canonical(E, H, free_paid, count-1, flags, free_upper)
        following, _ = canonical(E, H, free_paid, count+1, flags, free_upper)
        need(current[0] > previous[1] and current[0] > following[1] and current[1] < 0,
             'Global maximum with free centres, not fixed-p lever pricing')
        free_maxima.append({'flags':flags, 'side_windows':count, 'sides':sides,
                            'surplus':E.display(current)})
    free_low, _ = canonical(E, H, free_paid, 4, (1,1,1), free_lower)
    need(free_low[0] > 0, 'Tight free-centre lower endpoint at p5')
    return {'status':'PASS_GLOBAL_PAIRED_PATH_THINNING_CEILING', 'source_pr':4610,
            'scope':'All pair counts, prefix/suffix splits, and binary full-stage subsets of the retained path',
            'raw_root_bracket':[str(LOWER), str(UPPER)], 'new_kappa':False,
            'local_derivative_upper':E.display(derivative), 'canonical_maxima':maxima,
            'lower_endpoint_surplus':E.display(low), 'exact_source_masks_checked':finite_source_binding(),
            'free_owned_centres':{'scope':'Unrealized optimistic relaxation; no higher K construction',
                'raw_root_bracket':[str(free_lower), str(free_upper)],
                'canonical_maxima':free_maxima, 'lower_endpoint_surplus':E.display(free_low),
                'conclusion':'Even free centres and arbitrary stage thinning cannot reach C=0.01'},
            'controls':['charged queries', 'strict even-to-odd swap', 'source and profile pins'],
            'proof':'PROOF.md supplies infinite-family dominance and concavity'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = certify()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == json.loads(json.dumps(result)),
             'Committed exact receipt')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
