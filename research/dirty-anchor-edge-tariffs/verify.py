#!/usr/bin/env python3
"""Exact bounded forest construction, dirty maps, tariffs and defect controls.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
Written all-parameter optimality additionally uses Edmonds' branching theorem.
"""
import argparse
import importlib.util
import itertools
import json
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def depths(parent):
    q = len(parent)
    result = []
    for start in range(q):
        seen = set()
        vertex = start
        depth = 0
        while parent[vertex] != -1:
            if vertex in seen:
                return None
            seen.add(vertex)
            source = parent[vertex]
            if source < 0 or source >= q or source == vertex:
                return None
            vertex = source
            depth += 1
        result.append(depth)
    return result


def forests(q):
    choices = [tuple([-1] + [j for j in range(q) if j != i]) for i in range(q)]
    for parent in itertools.product(*choices):
        if depths(parent) is not None:
            yield parent


def word(parent, private=False):
    dep = depths(parent)
    require(dep is not None, 'parent relation is not a rooted forest')
    preparation = [('A', i, parent[i]) for i in
                   sorted(range(len(parent)), key=lambda j: (-dep[j], j))
                   if parent[i] != -1]
    result = preparation + [('P', i) for i, p in enumerate(parent) if p == -1]
    result += list(reversed(preparation))
    if private:
        result += [('T', i) for i in range(len(parent))]
    return result


def symbolic(q, gates):
    rows = [1 << i for i in range(q)]
    for gate in gates:
        if gate[0] == 'A':
            _, dst, src = gate
            require(dst != src, 'aliased row ADD')
            rows[dst] ^= rows[src]
        elif gate[0] == 'P':
            rows[gate[1]] ^= 1 << q
        elif gate[0] == 'T':
            rows[gate[1]] ^= 1 << (q + 1 + gate[1])
        else:
            raise ValueError('unknown gate')
    return rows


def target(q, private):
    return [(1 << i) | (1 << q) | ((1 << (q + 1 + i)) if private else 0)
            for i in range(q)]


def tariff(gates, common, edge, private=None):
    total = 0
    for gate in gates:
        if gate[0] == 'A':
            total += edge[gate[1]][gate[2]]
        elif gate[0] == 'P':
            total += common[gate[1]]
        else:
            require(private is not None, 'unpriced private call')
            total += private[gate[1]]
    return total


def forest_bill(parent, common, edge):
    return sum(common[i] if p == -1 else 2 * edge[i][p]
               for i, p in enumerate(parent))


def optimum(common, edge, height_one=False):
    candidates = []
    for parent in forests(len(common)):
        if height_one and max(depths(parent)) > 1:
            continue
        candidates.append((forest_bill(parent, common, edge), parent))
    return min(candidates)


def check_forest(parent):
    q = len(parent)
    gates = word(parent, private=True)
    require(symbolic(q, gates) == target(q, True), 'wrong arbitrary-dirty endpoint')
    require(symbolic(q, gates + list(reversed(gates))) == [1 << i for i in range(q)],
            'literal inverse failed')
    roots = parent.count(-1)
    require(sum(g[0] == 'A' for g in gates) == 2 * (q - roots), 'ADD count')
    require(sum(g[0] == 'P' for g in gates) == roots, 'common-call count')
    require(sum(g[0] == 'T' for g in gates) == q, 'private-call count')
    mu = [1 + (5 * i + q) % 17 for i in range(q)]
    nu = [1 + (3 * i + q) % 11 for i in range(q)]
    edge = [[0 if i == j else 1 + (7 * i + 11 * j) % 13
             for j in range(q)] for i in range(q)]
    require(tariff(gates, mu, edge, nu) == forest_bill(parent, mu, edge) + sum(nu),
            'actual literal word differs from complete graph bill')


def concrete(q, gates, bits):
    rows = list(bits[:q])
    p = bits[q]
    private = bits[q + 1:]
    for gate in gates:
        if gate[0] == 'A':
            rows[gate[1]] ^= rows[gate[2]]
        elif gate[0] == 'P':
            rows[gate[1]] ^= p
        else:
            rows[gate[1]] ^= private[gate[1]]
    return rows


def run():
    spec = importlib.util.spec_from_file_location('owned_cut_check', PACKAGE / 'cut_check.py')
    cut = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cut)
    cut_result = cut.cut_result()
    with tempfile.TemporaryDirectory(prefix='dirty-cut-') as temporary:
        cut_path = Path(temporary) / 'cut.json'
        cut_path.write_text(json.dumps(cut_result, indent=2, sort_keys=True) + '\n')
        cut_controls = cut.control_result(cut_path)
    all_counts = []
    for q in range(1, 7):
        count = 0
        for parent in forests(q):
            check_forest(parent)
            count += 1
        require(count == (q + 1) ** (q - 1), 'rooted-forest domain incomplete')
        all_counts.append({'q': q, 'forests': count})

    structured = concrete_cases = 0
    for q in range(1, 113):
        examples = [tuple([-1] * q), tuple([-1] + [0] * (q - 1)),
                    tuple([-1] + list(range(q - 1))),
                    tuple([-1] + [(i - 1) // 2 for i in range(1, q)]),
                    tuple(-1 if i % 4 == 0 else i - 1 for i in range(q))]
        for parent in examples:
            check_forest(parent)
            structured += 1
            if q <= 4:
                gates = word(parent, private=True)
                for bits in itertools.product([0, 1], repeat=2 * q + 1):
                    got = concrete(q, gates, bits)
                    require(got == [bits[i] ^ bits[q] ^ bits[q + 1 + i] for i in range(q)],
                            'concrete dirty/private/common state failed')
                    concrete_cases += 1

    destination_cases = 0
    for q in range(1, 5):
        inventory = list(forests(q))
        for price_bits in itertools.product([0, 1], repeat=2 * q):
            alpha = tuple(1 + 2 * bit for bit in price_bits[:q])
            mu = tuple(1 + 6 * bit for bit in price_bits[q:])
            edge = [[0 if i == j else alpha[i] for j in range(q)] for i in range(q)]
            graph = min(forest_bill(parent, mu, edge) for parent in inventory)
            subset = min(sum(mu[i] if mask >> i & 1 else 2 * alpha[i] for i in range(q))
                         for mask in range(1, 1 << q))
            require(graph == subset, 'PR3063 destination-price reduction failed')
            destination_cases += 1

    mu = (1, 100, 100)
    chain_edges = [[0 if i == j else 100 for j in range(3)] for i in range(3)]
    chain_edges[1][0] = chain_edges[2][1] = 1
    chain = (-1, 0, 1)
    require(optimum(mu, chain_edges) == (5, chain), 'directed chain optimum')
    require(optimum(mu, chain_edges, height_one=True)[0] == 103, 'multi-root star price')
    single_star = min(mu[r] + 2 * sum(chain_edges[i][r] for i in range(3) if i != r)
                      for r in range(3))
    require(single_star == 203 and sum(mu) == 201, 'single-star/direct comparator')

    proper = word(chain)
    require(symbolic(3, proper[:-1]) != target(3, False), 'missing return accepted')
    wrong_order = [('A', 1, 0), ('A', 2, 1), ('P', 0), ('A', 2, 1), ('A', 1, 0)]
    require(symbolic(3, wrong_order) != target(3, False), 'wrong tree order accepted')
    clean = symbolic(2, [('P', 0), ('A', 1, 0)])
    require(all(row >> 2 & 1 for row in clean), 'clean-map defect is not active')
    require(clean != target(2, False), 'unrestored dirt accepted')
    require(depths((-1, 2, 1)) is None, 'rootless cycle accepted as a forest')
    reversed_bill = mu[0] + 2 * chain_edges[0][1] + 2 * chain_edges[1][2]
    require(reversed_bill != tariff(proper, mu, chain_edges), 'arc reversal not detected')
    cycle_edges = [[0 if i == j else 100 for j in range(3)] for i in range(3)]
    cycle_edges[1][2] = cycle_edges[2][1] = 1
    actual_cycle = optimum(mu, cycle_edges)[0]
    alpha_min = [min(cycle_edges[i][j] for j in range(3) if j != i) for i in range(3)]
    false_destination_price = min(
        sum(mu[i] if mask >> i & 1 else 2 * alpha_min[i] for i in range(3))
        for mask in range(1, 8))
    require(actual_cycle == 103 and false_destination_price == 5,
            'ignoring directed root reachability accepted')

    return {'status': 'PASS_DIRTY_ANCHOR_EDGE_TARIFFS',
            'source_bindings': cut_result['source_bindings'],
            'finite_subset_cut': cut_result['domains'],
            'partial_cut_controls': cut_controls,
            'all_rooted_forests': all_counts,
            'structured_forests_q1_to112': structured,
            'exhaustive_one_bit_dirty_common_private_assignments': concrete_cases,
            'destination_tariff_reductions_q1_to4': destination_cases,
            'destination_tariff_domain': {'alpha': [1, 3], 'mu': [1, 7]},
            'chain_witness': {'parents': list(chain), 'complete_price': 5,
                              'best_height_one_forest': 103, 'best_single_root_star': 203,
                              'direct_calls': 201},
            'rejected_defects': ['omitted inverse ADD', 'parent-first preparation',
                                 'clean map with wrong dirt', 'rootless directed cycle',
                                 'reversed directed tariff', 'row-minimum tariff loses reachability'],
            'proof_level': 'Finite exact checks plus a separate written all-parameter proof using Edmonds branching. No formal kernel, physical supplier, new kappa or hosted CI.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write absent RESULT.json')
    parser.add_argument('--output', type=Path, help='write an absent external result')
    args = parser.parse_args()
    require(not (args.write and args.output), 'choose one output mode')
    result = run()
    destination = PACKAGE / 'RESULT.json' if args.write else args.output
    if destination:
        with destination.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    elif (PACKAGE / 'RESULT.json').is_file():
        require(json.loads((PACKAGE / 'RESULT.json').read_text()) == result,
                'stored result differs from complete recomputation')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
