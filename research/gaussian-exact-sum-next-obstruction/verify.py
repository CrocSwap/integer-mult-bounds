#!/usr/bin/env python3
"""Check the complete Hall witness and matching with integer arithmetic.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEN = 10**18
LOW = 605551275463989293
HIGH = LOW + 1
H = ((1, -1, 1, 1), (1, 1, -1, 1),
     (1, 1, 1, -1), (-1, 1, 1, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def norm(z):
    a, b = z
    return a*a + (1-a)*(1-a) + 2*b*b


def candidates(z):
    a, b = z
    return set(product((-b, 1-b), (a-1, a)))


def gap_at_most(a, b, numerator):
    """Compare sqrt(b)-sqrt(a) with the positive rational numerator/DEN."""
    remainder = (b-a)*DEN**2 - numerator**2
    return remainder <= 0 or remainder**2 <= 4*a*numerator**2*DEN**2


def category(a, b):
    """Return -1, 0 or 1 for a gap below, at or above sqrt(13)-3."""
    if (a, b) == (9, 13):
        return 0
    if gap_at_most(a, b, LOW):
        return -1
    require(not gap_at_most(a, b, HIGH), 'unresolved root comparison')
    return 1


def direct_edges(z):
    """Use the four real coordinates of the ideal pair as a second path."""
    a, b = z
    source = (a, b, 1-a, -b)
    twice_ideal = tuple(sum(row[j]*source[j] for j in range(4)) for row in H)
    edges = set()
    for c, e in product(range(-4, 5), repeat=2):
        target = (c, e, 1-c, -e)
        squared_error_times_four = sum((2*t-v)**2 for t, v in zip(target, twice_ideal))
        if squared_error_times_four <= 4:
            require(squared_error_times_four == 4, 'mixed-sum error must be one')
            edges.add((c, e))
    return edges


def validate_matching(rows, vertices, strict=False):
    inputs = [tuple(row['input']) for row in rows]
    outputs = [tuple(row['output']) for row in rows]
    require(len(inputs) == len(set(inputs)) and set(inputs) == vertices,
            'input coverage')
    require(len(outputs) == len(set(outputs)), 'output collision')
    for u, v in zip(inputs, outputs):
        require(v in direct_edges(u), 'illegal Gaussian edge')
        require(category(norm(u), norm(v)) < (0 if strict else 1),
                'radial threshold')


def maximum_matching(vertices, edges):
    """Check the graph by augmenting paths without the retained matching."""
    owner = {}

    def augment(u, visited):
        for v in sorted(edges[u]):
            if v in visited:
                continue
            visited.add(v)
            if v not in owner or augment(owner[v], visited):
                owner[v] = u
                return True
        return False

    for u in sorted(vertices):
        augment(u, set())
    return len(owner)


def verify():
    require((3*DEN+LOW)**2 < 13*DEN**2 < (3*DEN+HIGH)**2, 'root bracket')
    require(all(sum(H[k][i]*H[k][j] for k in range(4)) == (4 if i == j else 0)
                for i in range(4) for j in range(4)), 'ideal pair isometry')
    vertices = {z for z in product(range(-4, 5), repeat=2) if norm(z) <= 13}
    witness = {z for z in vertices if norm(z) <= 9} | {(-2, 0), (3, 0)}
    expected_neighbors = {z for z in vertices if norm(z) <= 9}
    strict, weak = {}, {}
    for u in vertices:
        formula = candidates(u)
        require(formula == direct_edges(u), 'candidate formula differs from ideal map')
        strict[u] = {v for v in formula if category(norm(u), norm(v)) == -1}
        weak[u] = {v for v in formula if category(norm(u), norm(v)) <= 0}
    neighbors = set().union(*(strict[u] for u in witness))
    require(neighbors == expected_neighbors, 'complete strict neighborhood')
    require((len(vertices), len(witness), len(neighbors)) == (22, 18, 16), 'Hall counts')
    rows = json.loads((ROOT/'MATCHING.json').read_text())
    validate_matching(rows, vertices)
    require(maximum_matching(vertices, strict) == 20, 'strict matching size')
    require(maximum_matching(vertices, weak) == 22, 'threshold matching size')
    faults = []
    bad = deepcopy(rows); bad[0]['output'] = bad[1]['output']
    faults.append(('collision', bad, False))
    faults.append(('missing input', rows[1:], False))
    bad = deepcopy(rows); bad[0]['output'] = [99, 99]
    faults.append(('illegal error', bad, False))
    faults.append(('strict threshold', rows, True))
    for name, bad, strict_flag in faults:
        try:
            validate_matching(bad, vertices, strict_flag)
        except ValueError:
            pass
        else:
            raise ValueError('control was not rejected: '+name)
    output = {
        'status': 'PASS_GAUSSIAN_EXACT_SUM_NEXT_OBSTRUCTION',
        'claim': 'global forward slack >= sqrt(13)-3; exact optimum on N<=13',
        'ball_inputs': len(vertices), 'hall_inputs': len(witness),
        'strict_neighbors': len(neighbors), 'strict_matching_size': 20,
        'threshold_matching_size': 22, 'all_error_one_edges': 4*len(vertices),
        'threshold_edges': sum(len(weak[u]-strict[u]) for u in vertices),
        'hall_shell_counts': dict(sorted(Counter(map(norm, witness)).items())),
        'hall_inputs_explicit': sorted(witness), 'strict_neighbors_explicit': sorted(neighbors),
        'root_bracket_numerators': [LOW, HIGH], 'root_bracket_denominator': DEN,
        'fault_controls': [name for name, _, _ in faults],
    }
    retained = ROOT/'RESULT.json'
    require(json.loads(retained.read_text()) == json.loads(json.dumps(output)),
            'retained receipt differs')
    return output


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True, indent=2))
