#!/usr/bin/env python3
"""Independent exact equality audit; Apache-2.0. See README for scope/credit."""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = ((0, 2), (0, 4), (2, 4))
ROOTS = (0, 2, 4)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def edges(p):
    return tuple((u, v) for u in range(2*p) for v in range(u+1, 2*p)
                 if u//2 != v//2)


def graph_oracle(p, retained):
    """Root-component condition, independent of modular elimination below."""
    adj = [[] for _ in range(2*p)]
    for u, v in retained:
        if (u, v) not in TARGET:
            adj[u].append(v)
            adj[v].append(u)
    seen = set()
    active = set()
    for root in ROOTS:
        if root in seen:
            return None
        colors = {root: 0}
        todo = [root]
        for u in todo:
            for v in adj[u]:
                if v in colors:
                    if colors[v] == colors[u]:
                        return None
                else:
                    colors[v] = 1-colors[u]
                    todo.append(v)
        if len(set(colors) & set(ROOTS)) != 1:
            return None
        seen.update(colors)
        active.update(colors)
    return tuple(sorted(active))


def column_rank(columns, n, prime=3):
    """Ordinary Gaussian elimination, no graph-component formula."""
    pivots = [None] * n
    count = 0
    for col in columns:
        v = list(col)
        for i in range(n):
            if not v[i]:
                continue
            if pivots[i] is None:
                if v[i] != 1:
                    inverse = pow(v[i], -1, prime)
                    v = [(z*inverse) % prime for z in v]
                pivots[i] = v
                count += 1
                break
            factor = v[i]
            old = pivots[i]
            for j in range(i, n):
                v[j] = (v[j]-factor*old[j]) % prime
    return count


def algebra_oracle(p, retained, observed=None, prime=3):
    observed = tuple(range(2*p)) if observed is None else tuple(observed)
    cols = [tuple(int(v == u or v == w) for v in observed)
            for u, w in retained if (u, w) not in TARGET]
    rank0 = column_rank(cols, len(observed), prime)
    cols += [tuple(int(v == u or v == w) for v in observed) for u, w in TARGET]
    return column_rank(cols, len(observed), prime) == rank0+3


def fraction_oracle(p, retained, observed):
    """Third engine: reduce observation rows, then test the three unit rows."""
    retained = tuple(retained)
    basis = {}
    for vertex in observed:
        row = [Fraction(vertex in e) for e in retained]
        for i in range(len(row)):
            if row[i] == 0:
                continue
            if i not in basis:
                v = row[i]
                basis[i] = [x/v for x in row]
                break
            v = row[i]
            row = [x-v*y for x, y in zip(row, basis[i])]
    for target in TARGET:
        row = [Fraction(e == target) for e in retained]
        for i in sorted(basis):
            v = row[i]
            row = [x-v*y for x, y in zip(row, basis[i])]
        if any(row):
            return False
    return True


def classified_optima(p):
    all_edges = edges(p)
    output = set()
    if p >= 4:
        output.add(tuple(e for e in all_edges if e in TARGET or not set(e)&set(ROOTS)))
    if p in (3, 4):
        for root in ROOTS:
            component = set(range(2*p)) - (set(ROOTS)-{root})
            # Canonical orientation puts the root in the left side.
            for others in combinations(sorted(component-{root}), p-2):
                left = {root, *others}
                right = component-left
                cross = {tuple(sorted((u, v))) for u in left for v in right}
                if cross.issubset(all_edges):
                    output.add(tuple(sorted(set(TARGET)|cross)))
    return tuple(sorted(output))


def graph_census(p):
    all_edges = edges(p)
    rest = tuple(e for e in all_edges if e not in TARGET)
    retained_size = 7 if p == 3 else 12
    accepted = []
    checked = 0
    for extra in combinations(rest, retained_size-3):
        retained = tuple(sorted(TARGET+extra))
        graph = graph_oracle(p, retained)
        algebra = algebra_oracle(p, retained)
        require(algebra == (graph is not None), f'oracle disagreement: {retained}')
        if algebra:
            accepted.append(retained)
        checked += 1
    require(tuple(sorted(accepted)) == classified_optima(p), 'incomplete equality classification')
    return checked, accepted


def source_check():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for item in pins['files']:
        if item['usage'] == 'input':
            require(sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'],
                    'source pin mismatch')


def echo_invoice(p, retained):
    """One fully paid literal dirty-helper echo, not a circuit minimum."""
    active = graph_oracle(p, retained)
    signs = {}
    root_signs = ((1, 1, -1), (1, -1, 1), (-1, 1, 1))
    for root, triple in zip(ROOTS, root_signs):
        signs[root] = triple
        todo = [root]
        for u in todo:
            for e in retained:
                if e in TARGET or u not in e:
                    continue
                v = e[0] if e[1] == u else e[1]
                if v not in signs:
                    signs[v] = tuple(-x for x in signs[u])
                    todo.append(v)
    source_count = len(retained)
    helpers = {v: source_count+i for i, v in enumerate(active)}
    out0 = source_count+len(active)
    gates = []
    kinds = {'source_ADD': 0, 'output_ADD': 0, 'SCALE': 0}

    def add(dst, src, coefficient, kind):
        gates.append(('ADD', dst, src, Fraction(coefficient)))
        kinds[kind] += 1

    def gather(sign):
        for v in active:
            for i, e in enumerate(retained):
                if v in e:
                    add(helpers[v], i, sign, 'source_ADD')

    def decode(sign):
        for v in active:
            gates.append(('SCALE', helpers[v], helpers[v], Fraction(1, 2)))
            kinds['SCALE'] += 1
        for v in active:
            for j, coefficient in enumerate(signs[v]):
                add(out0+j, helpers[v], sign*coefficient, 'output_ADD')
        for v in active:
            gates.append(('SCALE', helpers[v], helpers[v], Fraction(2)))
            kinds['SCALE'] += 1

    gather(1)
    decode(1)
    gather(-1)
    decode(-1)
    n = out0+3

    def execute(omit=None):
        matrix = [[Fraction(i == j) for j in range(n)] for i in range(n)]
        for index, (op, dst, src, coefficient) in enumerate(gates):
            if index == omit:
                continue
            if op == 'SCALE':
                matrix[dst] = [coefficient*x for x in matrix[dst]]
            else:
                matrix[dst] = [x+coefficient*y for x, y in zip(matrix[dst], matrix[src])]
        return matrix

    expected = [[Fraction(i == j) for j in range(n)] for i in range(n)]
    for j, target in enumerate(TARGET):
        expected[out0+j][retained.index(target)] += 1
    require(execute() == expected, 'dirty echo full basis map failed')
    for omit in range(len(gates)):
        require(execute(omit) != expected, 'one-gate omission did not fail')
    return {'helpers': len(active), **kinds, 'total': len(gates),
            'basis_columns': n, 'single_gate_omissions_rejected': len(gates),
            'word_sha256': sha256(json.dumps([[a, b, c, str(d)] for a, b, c, d in gates]).encode()).hexdigest()}


def receipt():
    source_check()
    result = {'scope': 'all-p written equality theorem; finite independent census below',
              'new_kappa': False, 'census': [], 'controls': {}}
    omit = restore = subsets = characteristic_two = 0
    for p in (3, 4):
        checked, accepted = graph_census(p)
        fixtures = []
        for retained in accepted:
            active = graph_oracle(p, retained)
            require(fraction_oracle(p, retained, range(2*p)), 'rational replay failed')
            require(not algebra_oracle(p, retained, prime=2), 'characteristic-two failure absent')
            characteristic_two += 1
            good = 0
            for size in range(2*p+1):
                for observed in combinations(range(2*p), size):
                    predicted = set(active).issubset(observed)
                    actual = fraction_oracle(p, retained, observed)
                    require(actual == predicted, 'raw-observation criterion false')
                    require(algebra_oracle(p, retained, observed) == actual, 'field disagreement')
                    good += actual
                    subsets += 1
            for vertex in active:
                observed = [v for v in range(2*p) if v != vertex]
                require(not fraction_oracle(p, retained, observed), 'missing raw observation accepted')
                omit += 1
            for e in edges(p):
                if e not in retained:
                    require(not algebra_oracle(p, retained+(e,)), 'one-edge restoration accepted')
                    restore += 1
            fixtures.append({'edges': [list(e) for e in retained], 'raw_observations': list(active),
                             'minimum_observations': len(active), 'recovering_observation_subsets': good})
        result['census'].append({'p': p, 'graphs': checked, 'optima': len(accepted), 'fixtures': fixtures})
    inequalities = 0
    for p in range(3, 65):  # seed 64 determines diagnostic endpoint only
        n = 2*p
        bound = lambda b: (n-b-2)**2//4 + b*(b-1)//2-max(0, b-p)
        vals = [bound(b) for b in range(n-2)]
        require(all(vals[i+2]-2*vals[i+1]+vals[i] >= 0 for i in range(len(vals)-2)), 'not convex')
        argmax = [i for i, v in enumerate(vals) if v == max(vals)]
        require(argmax == ([0] if p == 3 else [0, 5] if p == 4 else [n-3]), 'wrong equality endpoints')
        require((2*p*p-8*p+12)-((p-1)**2+3) == (p-2)*(p-4), 'endpoint identity')
        inequalities += len(vals)-2
    general = []
    for p in (5, 6, 8):
        retained, = classified_optima(p)
        require(len(edges(p))-len(retained) == 6*p-12, 'wrong general deletion bill')
        require(fraction_oracle(p, retained, ROOTS), 'isolated triangle did not recover')
        require(not fraction_oracle(p, retained, ROOTS[:-1]), 'two observations recovered triangle')
        general.append({'p': p, 'deleted': 6*p-12, 'raw_observations': 3})
    result['general_positive_fixtures'] = general
    p4 = classified_optima(4)
    standard = next(g for g in p4 if len(graph_oracle(4, g)) == 3)
    exceptional = next(g for g in p4 if len(graph_oracle(4, g)) == 8)
    result['literal_echo'] = {'p4_isolated': echo_invoice(4, standard),
                              'p4_K33': echo_invoice(4, exceptional)}
    result['controls'] = {'deleted_edges_restored_and_rejected': restore,
                          'necessary_observations_omitted_and_rejected': omit,
                          'all_observation_subsets': subsets,
                          'characteristic_two_rejections': characteristic_two,
                          'convex_second_differences': inequalities,
                          'general_two_observation_rejections': len(general)}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    parser.add_argument('--certificate', type=Path, default=HERE/'CERTIFICATE.json')
    args = parser.parse_args()
    actual = receipt()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
        return
    wanted = json.loads(args.certificate.read_text())
    require(json.dumps(wanted, sort_keys=True) == json.dumps(actual, sort_keys=True), 'certificate mismatch')
    print('PASS_TRIANGLE_EQUALITY_AUDIT graphs=294056 optima_p3=3 optima_p4=7 '
          'minimum_observations_p3=6 p4=3_or_8 p_ge_5=3 no_new_kappa')


if __name__ == '__main__':
    main()
