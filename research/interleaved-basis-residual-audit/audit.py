"""Check rational residual certificates for the three released split cases.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The retained constructor supplies graphs. Its witness evaluator is not used.
"""

from fractions import Fraction as F
from heapq import heappop, heappush
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'retained/source'
sys.path.insert(0, str(SOURCE))
import construction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    return json.loads((SOURCE / name).read_text())


def row(entries):
    result = {key: F(value) for key, value in entries}
    require(len(result) == len(entries) and all(result.values()), 'invalid sparse row')
    return result


def packed(values):
    return [[key, str(value)] for key, value in sorted(values.items()) if value]


def add(target, key, value):
    value += target.get(key, 0)
    if value:
        target[key] = value
    else:
        target.pop(key, None)


def difference(left, right):
    result = dict(left)
    for key, value in right.items():
        add(result, key, -value)
    return result


def graph(net, direction):
    first, size = net.first_output, len(net.initial)
    forms, moves = net.forms, net.moves
    initial, final = net.initial, net.final
    if direction == 'transpose':
        def reverse(key):
            return first + ~key if key < 0 else ~(key - first) if key >= first else key
        forms = {key: {} for key in net.forms}
        for target, terms in net.forms.items():
            for donor, coefficient in terms.items():
                forms[reverse(donor)][reverse(target)] = coefficient
        moves = {key: (b, a) for key, (a, b) in net.moves.items()}
        initial, final = final, initial
    else:
        require(direction == 'forward', 'unknown orientation')
    return dict(first=first, size=size, forms=forms, moves=moves, initial=initial, final=final)


def signature(g):
    data = dict(first=g['first'], initial=g['initial'], final=g['final'],
                moves=[[k, *v] for k, v in sorted(g['moves'].items())],
                forms=[[k, packed(v)] for k, v in sorted(g['forms'].items())])
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def bank_chart(g, key):
    if key < 0:
        require(~key < g['size'], 'unknown entrance')
        return g['initial'][~key]
    require(key in g['moves'], 'unknown received bank')
    return g['moves'][key][1]


def schedule(g):
    forms, moves, first, size = (g[k] for k in ('forms', 'moves', 'first', 'size'))
    require(set(forms) == set(moves) | set(range(first, first + size)), 'graph inventory')
    incoming, readers = {}, {key: [] for key in forms}
    ready = []
    for key, terms in forms.items():
        chart = moves[key][0] if key < first else g['final'][key - first]
        require(all(bank_chart(g, donor) == chart for donor in terms), 'nonlocal coefficient')
        incoming[key] = sum(donor >= 0 for donor in terms)
        for donor in terms:
            if donor >= 0:
                readers[donor].append(key)
        if not incoming[key]:
            heappush(ready, key)
    order = []
    while ready:
        key = heappop(ready)
        order.append(key)
        for target in readers[key]:
            incoming[target] -= 1
            if not incoming[target]:
                heappush(ready, target)
    require(len(order) == len(forms), 'cyclic graph')
    return order


def check_functional(g, observation, certificate):
    """Multiply the formal residual rows; do not propagate an observation."""
    multipliers, expansion = row(certificate['multipliers']), row(certificate['expansion'])
    require(multipliers.keys() <= g['forms'].keys(), 'unknown equation multiplier')
    require(all(key < 0 and ~key < g['size'] for key in expansion), 'invalid entrance expansion')
    residual = dict(multipliers)
    products = 0
    for key, factor in multipliers.items():
        for donor, coefficient in g['forms'][key].items():
            add(residual, donor, -factor * coefficient)
            products += 1
    require(residual == difference(observation, expansion), 'formal coefficient residual differs')
    return expansion, products


def check_response(g, pulse, entrance, certificate):
    """Substitute a proposed value into every equation, in arbitrary key order."""
    values = row(certificate)
    require(values.keys() <= g['forms'].keys(), 'unknown response bank')
    products = 0
    for key, terms in g['forms'].items():
        expected = pulse.get(key, 0)
        for donor, coefficient in terms.items():
            expected += coefficient * (entrance.get(~donor, 0) if donor < 0 else values.get(donor, 0))
            products += 1
        require(values.get(key, 0) == expected, 'response equation differs')
    terminal = {key - g['first']: value for key, value in values.items() if key >= g['first']}
    return values, terminal, products


def check_identity(g, role, certificate):
    expansion, products = check_functional(g, {g['first'] + role: F(1)}, certificate['row'])
    require(expansion == {~role: F(1)}, 'helper terminal is not its input')
    _, terminal, count = check_response(g, {}, {role: F(1)}, certificate['column'])
    require(terminal == {role: F(1)}, 'helper input affects another terminal')
    return products + count


def cases():
    journal, controls = read('EDITS.json'), read('data/RESTRICTION-CONTROLS.json')
    require([c['alternative']['role'] for c in controls] == [1400, 1401, 1409], 'three requested roles')
    for control in controls:
        role = control['alternative']['role']
        index, = [i for i, e in enumerate(journal) if e.get('role') == role]
        last, = [i for i, e in enumerate(journal) if e['event'] == 'split'
                 and (e['role'], e['split_chart'], e['direction'])
                 == (control['split_role'], control['split_chart'], control['direction'])]
        for variant, restriction in (('chosen', journal[index]), ('alternate', control['alternative'])):
            before, _ = construction.apply_edits(journal[:index])
            edits = list(journal[:last])
            edits[index] = restriction
            prefix, _ = construction.apply_edits(edits)
            yield role, variant, restriction, journal[last], graph(before, restriction['direction']), graph(prefix, journal[last]['direction'])


def observations(restriction):
    source = row(restriction['source'])
    require(all(key < 0 for key in source) and source.get(~restriction['role']), 'source pivot')
    bank, = restriction['banks']
    relation = row(bank['relation'])
    require(relation.get(bank['remove']), 'receiver pivot')
    return difference(relation, source)


def dot(left, right):
    return sum(value * right.get(key, 0) for key, value in left.items())


def check_case(g0, g, restriction, split, item):
    require(item['restriction_graph'] == signature(g0) and item['split_graph'] == signature(g), 'prefix graph differs')
    schedule(g0)
    schedule(g)
    bank, = restriction['banks']
    require(g0['moves'][bank['remove']][1] == bank['chart'], 'restriction receiver chart')
    require(all(bank_chart(g0, k) == g0['initial'][restriction['role']] for k, _ in restriction['source']), 'restriction source chart')
    require(all(bank_chart(g0, k) == bank['chart'] for k, _ in bank['relation']), 'restriction bank chart')
    expansion, products = check_functional(g0, observations(restriction), item['restriction'])
    require(not expansion, 'receiver and source restriction differ')
    products += check_identity(g0, restriction['role'], item['restriction_identity'])
    products += check_identity(g, split['role'], item['split_identity'])
    readout, calibration, pulse = (row(split[k]) for k in ('readout', 'calibration', 'pulse'))
    s, w, y, t = (row(split[k]) for k in ('source_covector', 'source_direction', 'return_covector', 'return_direction'))
    require(all(bank_chart(g, k) == split['split_chart'] for k in readout.keys() | calibration.keys()), 'split bank chart')
    require(all((g['moves'][k][0] if k < g['first'] else g['final'][k - g['first']]) == split['split_chart'] for k in pulse), 'pulse source chart')
    require(all(g['initial'][i] == split['source_chart'] for i in s.keys() | w.keys()), 'source direction chart')
    require(all(g['final'][i] == split['return_chart'] for i in y.keys() | t.keys()), 'return direction chart')
    actual, n = check_functional(g, readout, item['readout'])
    products += n
    decoded = {g['first'] + key: value for key, value in y.items()}
    calibration_error, n = check_functional(g, difference(calibration, decoded), item['calibration'])
    products += n
    values, response, n = check_response(g, pulse, {}, item['pulse'])
    products += n
    _, steered, n = check_response(g, {}, w, item['steering'])
    products += n
    errors = {'readout': {~k: v for k, v in difference(actual, {~k: v for k, v in s.items()}).items()},
              'calibration': {~k: v for k, v in calibration_error.items()},
              'response': difference(response, t), 'steering': difference(steered, t)}
    feedback = [dot(readout, values), dot(calibration, values)]
    factors = [dot(s, w), dot(y, t), t.get(split['role'], 0)]
    require(all(factors), 'zero split normalization')
    if item['variant'] == 'chosen':
        require(not any(errors.values()) and feedback == [0, 0], 'chosen split equation fails')
    failures = {name: dict(coordinates=len(error), first_coordinate=min(error),
                           difference=str(error[min(error)])) for name, error in errors.items() if error}
    return dict(restriction=restriction['role'], variant=item['variant'], split=split['role'],
                direction=split['direction'], input_symbols=g['size'], restriction_symbols=g0['size'],
                graph_equations=len(g['forms']), products=products, failures=failures,
                feedback=list(map(str, feedback)), normalizations=list(map(str, factors)))
