"""Independent integer-grid distance and dirty-macro checks for frozen CK words.

Eva Ayala / ToikY, with substantial OpenAI Codex assistance; Apache-2.0.
No constructor imports. Distances use synchronous Bellman relaxation rather
than the construction's breadth-first queue. Optimality is only in the stated
bounded, single-work-register graph with paid COPY before preparation.
"""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/LOCAL-PROGRAMS.json.gz'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory():
    payload = gzip.decompress(SOURCE.read_bytes())
    programs = json.loads(payload)
    require(set(programs) == {'forward', 'backward'}, 'source orientations')
    values = set()
    for events in programs.values():
        for event in events:
            if event[0] == 'scalar' and event[1][0] == 'add':
                q = abs(Fraction(event[1][3], event[1][4]))
                require(q > 0, 'source coefficient zero')
                values.add(q)
    require(len(values) == 103, 'frozen CK coefficient inventory')
    return values, hashlib.sha256(payload).hexdigest()


def transitions(x, denominator, bound):
    """Enumerate every labelled graph edge; duplicate endpoints stay distinct."""
    destinations = {
        'add': x + denominator, 'subtract': x - denominator,
        'double': x * 2, 'negate': -x, 'clear': 0, 'copy': denominator,
    }
    if x % 2 == 0:
        destinations['halve'] = x // 2
    return {tag: y for tag, y in destinations.items() if -bound <= y <= bound}


def dirty_macro(word, a, denominator, sign, terminal_sign):
    """All three arbitrary input columns, represented in integer units 1/D."""
    source = [0, denominator, 0]
    target = [denominator, 0, 0]
    work = source.copy()  # Paid COPY overwrites the arbitrary dirty work column.
    for tag in word:
        if tag == 'clear':
            work = [0, 0, 0]
        elif tag == 'copy':
            work = source.copy()
        elif tag == 'halve':
            require(all(v % 2 == 0 for v in work), 'macro leaves the grid')
            work = [v // 2 for v in work]
        elif tag == 'double':
            work = [2 * v for v in work]
        elif tag == 'negate':
            work = [-v for v in work]
        elif tag in ('add', 'subtract'):
            multiplier = 1 if tag == 'add' else -1
            work = [v + multiplier * s for v, s in zip(work, source)]
        else:
            raise ValueError('unknown preparation primitive')
    target = [t + sign * terminal_sign * w for t, w in zip(target, work)]
    work = [0, 0, 0]  # Paid final CLEAR.
    require(target == [denominator, sign * a, 0], 'dirty target map')
    require(source == [0, denominator, 0] and work == [0, 0, 0], 'dirty restoration')


def check_record(q, record):
    require(type(record) is dict and set(record) == {'a', 'D', 'bound', 'states', 'word', 'cost', 'terminal_sign'}, 'record schema')
    a, denominator = q.numerator, q.denominator
    for key, value in (('a', a), ('D', denominator), ('bound', a * denominator)):
        require(type(record[key]) is int and record[key] == value, 'parameter ' + key)
    bound = record['bound']
    vertices = list(range(-bound, bound + 1))
    require(type(record['states']) is list, 'state list')
    labels = {}
    for state in record['states']:
        require(type(state) is dict and set(state) == {'x', 'distance'}, 'state schema')
        x, distance = state['x'], state['distance']
        require(type(x) is int and type(distance) is int and distance >= 0, 'state integer labels')
        require(x not in labels, 'duplicate state')
        labels[x] = distance
    require(set(labels) == set(vertices), 'complete vertex inventory')
    edges = [(x, tag, y) for x in vertices for tag, y in transitions(x, denominator, bound).items()]

    # Complete synchronous shortest-distance recurrence. Each iteration admits
    # one further edge, so convergence requires at most |V| iterations.
    infinity = len(vertices) + 1
    distances = {x: infinity for x in vertices}
    distances[denominator] = 0
    for rounds in range(1, len(vertices) + 1):
        following = distances.copy()
        for x, _tag, y in edges:
            following[y] = min(following[y], distances[x] + 1)
        if following == distances:
            break
        distances = following
    else:
        raise ValueError('Bellman relaxation did not converge')
    require(all(d < infinity for d in distances.values()), 'unreachable graph vertex')
    require(labels == distances, 'independent distance labels')

    # Explicit certificate obligations: edge lower bounds and attainment.
    require(labels[denominator] == 0, 'start distance')
    attained = {denominator}
    for x, _tag, y in edges:
        require(labels[y] <= labels[x] + 1, 'Bellman edge inequality')
        if labels[y] == labels[x] + 1:
            attained.add(y)
    require(attained == set(vertices), 'shortest predecessor attainment')
    require(type(record['word']) is list, 'word list')
    x = denominator
    for tag in record['word']:
        require(type(tag) is str and tag in transitions(x, denominator, bound), 'witness edge')
        x = transitions(x, denominator, bound)[tag]
    terminal_sign = record['terminal_sign']
    require(type(terminal_sign) is int and terminal_sign in (-1, 1), 'terminal sign')
    require(x == terminal_sign * a, 'witness endpoint')
    shortest = min(labels[a], labels[-a])
    require(len(record['word']) == shortest, 'witness minimum length')
    require(type(record['cost']) is int and record['cost'] == shortest + 3, 'paid copy/add/clear cost')
    for sign in (1, -1):
        dirty_macro(record['word'], a, denominator, sign, terminal_sign)
    return len(vertices), len(edges), rounds, len(record['word'])


def negative_controls(census):
    q = Fraction(1, 64)
    original = census[str(q)]
    mutations = {}
    for name in ('wrong_bound', 'missing_vertex', 'duplicate_vertex', 'wrong_distance', 'boolean_distance', 'wrong_word', 'unknown_primitive', 'wrong_cost', 'wrong_terminal_sign'):
        mutations[name] = copy.deepcopy(original)
    mutations['wrong_bound']['bound'] += 1
    mutations['missing_vertex']['states'].pop()
    mutations['duplicate_vertex']['states'].append(mutations['duplicate_vertex']['states'][0].copy())
    mutations['wrong_distance']['states'][0]['distance'] += 1
    mutations['boolean_distance']['states'][0]['distance'] = True
    mutations['wrong_word']['word'].pop()
    mutations['unknown_primitive']['word'].append('unpaid_halve')
    mutations['wrong_cost']['cost'] -= 1
    mutations['wrong_terminal_sign']['terminal_sign'] *= -1
    rejected = []
    for name, mutation in mutations.items():
        try:
            check_record(q, mutation)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('accepted negative control: ' + name)
    return rejected


def check(census):
    values, source_hash = inventory()
    require(type(census) is dict and set(census) == {str(q) for q in values}, 'complete coefficient census')
    totals = [0, 0, 0, 0]
    for q in sorted(values):
        result = check_record(q, census[str(q)])
        totals = [x + y for x, y in zip(totals, result)]
    return {'coefficients': len(values), 'vertices': totals[0], 'labelled_edges': totals[1],
            'relaxation_rounds': totals[2], 'preparation_operations': totals[3],
            'signed_dirty_macro_columns': 6 * len(values), 'source_payload_sha256': source_hash,
            'census_sha256': hashlib.sha256(json.dumps(census, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
            'negative_controls': negative_controls(census)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', nargs='?', type=Path, default=HERE / 'CENSUS.json.gz')
    args = parser.parse_args()
    raw = args.certificate.read_bytes()
    if args.certificate.suffix == '.gz':
        raw = gzip.decompress(raw)
    result = check(json.loads(raw))
    print(json.dumps(result, sort_keys=True))
    print('PASS_INDEPENDENT_CK_GRID coefficients=103 vertices=' + str(result['vertices']))
