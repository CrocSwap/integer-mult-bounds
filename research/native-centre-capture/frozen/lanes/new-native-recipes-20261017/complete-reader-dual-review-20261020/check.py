#!/usr/bin/env python3
"""Check the complete routed inverse-adjoint service."""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
HELPER = HERE.parent/'row-capture-native-review-20261020/check.py'
PIN = '5b8f2839db4fd4b0e4b24d5b8f8938c74a15497ae0e58f324896cf431d3ecb84'
if sha256(HELPER.read_bytes()).hexdigest() != PIN:
    raise ValueError('Independent arithmetic helper pin')
spec = importlib.util.spec_from_file_location('independent_row_tools', HELPER)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
q.read(HELPER, PIN)
need = q.need
UNIT = tuple(1 << j for j in range(25))
SOURCE = LANES/'bridge-access-20261017/involution-reader-dual-20261020'
FORWARD = LANES/'bridge-access-20261017/involution-reader-20261020'


def act(columns, vector):
    result = 0
    for j, column in enumerate(columns):
        if vector >> j & 1:
            result ^= column
    return result


@lru_cache(maxsize=8192)
def compose(left, right):
    return tuple(act(left, column) for column in right)


def transpose(columns):
    return tuple(sum(((v >> i) & 1) << j for j, v in enumerate(columns)) for i in range(len(columns)))


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            j = row.bit_length()-1
            if j not in pivots:
                pivots[j] = row
                break
            row ^= pivots[j]
    return len(pivots)


def phase(factors, translation=0):
    """Expand each parity over the Boolean cube modulo four."""
    linear = [2*((translation >> j) & 1) for j in range(25)]
    quadratic = [0]*25
    for vector, power in factors:
        for j in range(25):
            if vector >> j & 1:
                linear[j] = (linear[j]+power) % 4
                if power % 2:
                    quadratic[j] ^= vector & ~((1 << (j+1))-1)
    return tuple(linear), tuple(quadratic)


def orthogonal(columns):
    need(len(columns) == 25 and all(0 <= c < 1 << 25 for c in columns), 'Actual25-axis route')
    need(compose(columns, transpose(columns)) == compose(transpose(columns), columns) == UNIT,
         'Exact orthogonal inverse')


def phase_bindings(bundle, records):
    counts = Counter()
    selected = set(bundle['pivots'])
    need(len(bundle['stage_views']) == 2, 'Both physical adjacent stages')
    for stage in bundle['stage_views']:
        t = stage['service_stage']
        need(t in (1, 2) and stage['physical_input_level'] == t-1 and
             stage['physical_output_level'] == t, 'Adjacent stage levels')
        before = [(v, 1) for v in UNIT[:9+8*(t-1)]]
        after = [(v, 1) for v in UNIT[:9+8*t]]
        exterior = [(v, 1) for v in UNIT[9:9+8*t]]
        need(stage['common_exterior_axes'] == list(UNIT[9:9+8*t]), 'Complete common exterior')
        for label in ('DATA_entry', 'DATA_exit'):
            fields = set()
            for view in stage[label]:
                p, side, field = view['port'], view['side'], view['field']
                need(side in ('X', 'Y') and field == p+(112 if side == 'Y' else 0) and
                     field not in fields, 'Exact physical DATA field')
                fields.add(field)
                original = records[t, p]
                rho = tuple(view['route_columns'])
                orthogonal(rho)
                need(view['route_columns'] == original['route_columns'] and
                     view['owner_from_body'] == 'h=d*rho' and
                     act(rho, original['q']) == original['q'], 'Actual owner route and intrinsic line')
                full = side == 'X' or p in selected
                align = original['literal_stage_alignment']
                if label == 'DATA_entry':
                    need(view['intrinsic_input'] == ('Q_p' if full else 'I'), 'Exact input type')
                    delta = act(rho, align['entry_'+side])
                    need(view['translation_before_route'] == align['entry_'+side] and
                         view['translation_after_route'] == delta, 'Entry translation order')
                    source = before+([] if full else [(original['q'], -1)])
                    target = exterior+([(original['q'], 1)] if full else [])
                else:
                    key = 'exit_X' if full else 'exit_Y'
                    delta = align[key]
                    need(view['literal_translation_key'] == key and
                         view['translation_after_route'] == delta and
                         view['global_output'] == ('FULL' if full else 'FULL*q_p'), 'Exact exit type')
                    source = target = after+([] if full else [(original['q'], -1)])
                need(phase([(act(rho, v), n) for v, n in source], delta) == phase(target),
                     'All Boolean Z4 phase coefficients')
                counts[label] += 1
            need(fields == set(range(224)), 'Every DATA field exactly once')
    need(counts == {'DATA_entry': 448, 'DATA_exit': 448}, 'All896 DATA equations')
    return dict(counts)


def unitary_records(word):
    records = []
    for recipe in word['native_recipes'].values():
        need(1 <= recipe['rank'] <= 9, 'Unitary native child')
        records.extend(recipe[key] for key in ('left', 'right') if recipe[key] is not None)
    for view in word['input_views']:
        need(view['rank'] == 0 and view['right'] is None, 'Monomial input adapter')
        records.append(view['left'])
    for view in word['output_views']:
        recipe = view['recipe']
        need(recipe['rank'] == 0 and recipe['right'] is None, 'Monomial output adapter')
        records.append(recipe['left'])
    for record in records:
        need(len(record['matrix_rows']) == 9 and binary_rank(record['matrix_rows']) == 9,
             'Unitary nine-axis address map')
        need(all(0 <= r < 512 for r in record['matrix_rows']) and
             0 <= record['offset'] < 512 and 0 <= record['phase'] < 4, 'Exact monomial domain')
        need(len(record['linear_Z4']) == len(record['quadratic_rows']) == 9 and
             all(0 <= x < 4 for x in record['linear_Z4']) and
             all(0 <= x < 512 for x in record['quadratic_rows']), 'Unit-modulus complete phase')
    return len(records)


def scalar_dual(gate):
    op, target, source, coefficient = gate
    c = F(coefficient)
    if op == 'add':
        return ['add', source, target, str(-c)]
    need(op == 'scale' and c, 'Invertible scalar gate')
    return ['scale', target, None, str(1/c)]


def native_prefix(word, original, a, pivots):
    need(set(word) == set(original), 'Complete native record keys')
    for key in original:
        if key != 'events':
            need(word[key] == original[key], 'Exact unchanged native metadata: '+key)
    need(len(word['events']) == len(original['events']) == 2406, 'Complete native event count')
    current, profile = list(word['start']), Counter()
    for new, old in zip(word['events'], original['events']):
        if old[0] == 'native':
            need(new == old, 'Every native occurrence and phase key is unchanged')
            _, field, before, after, rank, key = new
            need(0 <= field < 224 and current[field] == before and
                 word['native_recipes'][key]['rank'] == rank, 'Typed native occurrence')
            current[field] = after
            profile[rank] += 1
        else:
            need(new == ['scalar', scalar_dual(old[1]), old[2]], 'Same-order scalar inverse-adjoint')
            (op, target, source, _), frame = new[1:]
            need(0 <= target < 224 and current[target] == frame, 'Exact new scalar target frame')
            if op == 'add':
                need(0 <= source < 224 and source != target and current[source] == frame,
                     'Exact new scalar source frame')
    need(current == word['final'], 'All640 final frames')
    expected = q.unit(640)
    for p, row in enumerate(a):
        if p not in pivots:
            for j, c in row.items():
                q.add(expected[j], {112+p: -c})
    scalars = [e[1] for e in word['events'] if e[0] == 'scalar']
    need(q.reverse(scalars, 640) == q.transpose(expected, 640), 'All640 native reverse columns')
    rows, growth = q.prefix(scalars, 640)
    need(rows == expected and growth == {'row_one_norm': '12', 'binary_height': 1},
         'Native forward rows and exact prefixes')
    need(q.price(scalars) == 6456 and profile == {1: 1392, 2: 64, 3: 48, 8: 16},
         'Exact native scalar and child invoice')
    count = unitary_records(word)
    need(count == 3150, 'All stored unitary side-map and endpoint records')
    return scalars, {'columns': 640, 'unchanged_arbitrary_fields': 416, 'scalar': 6456,
                     'profile': dict(profile), 'native_children': 1520, 'native_mass': 1792,
                     'unitary_monomial_records': count, 'growth': growth}


def query_operations(word, original, pivots):
    need(set(word) == set(original), 'Complete query record keys')
    for key in original:
        if key != 'events':
            need(word[key] == original[key], 'Exact unchanged query metadata: '+key)
    need(len(word['events']) == len(original['events']), 'Complete query chronology')
    level = word['service_stage']
    full = [(v, 1) for v in UNIT[:9+8*level]]
    for record in word['maps']:
        route, inverse = tuple(record['columns']), tuple(record['inverse_columns'])
        orthogonal(route)
        need(inverse == transpose(route) and route[9+8*level:] == UNIT[9+8*level:],
             'Exact map inverse and future axes')
        need(record['inverse_translation'] == act(inverse, record['translation']), 'Inverse phase translation')
        need(phase([(act(route, v), 1) for v, _ in full], record['translation']) == phase(full),
             'Complete late FULL phase')
    operations, scalars, maps = [], [], 0
    for new, old in zip(word['events'], original['events']):
        if old[0] == 'map':
            need(new == old, 'Map stays on the same physical field at the same position')
            _, field, index = new
            need(field < 112 or field-112 in pivots, 'Map uses a FULL field')
            operations.append(('map', field, None, F(1), tuple(word['maps'][index]['columns'])))
            maps += 1
        else:
            need(old[0] == 'scalar' and new == ['scalar']+scalar_dual(old[1:]), 'Literal late scalar dual')
            op, target, source, coefficient = new[1:]
            need(target < 112 or target-112 in pivots, 'Late scalar target is FULL')
            need(source is None or source < 112 or source-112 in pivots, 'Late scalar source is FULL')
            operations.append((op, target, source, F(coefficient), UNIT))
            scalars.append(new[1:])
    need(maps == 672 and q.price(scalars) == 8440, 'Exact late query bill')
    need(len({(lo, hi) for lo, hi in word['stage_ranges'].values()}) == 4, 'Four query intervals')
    last = 0
    for name in ('apply_current_involution', 'old_reader_complement',
                 'selected_reader_copy', 'restore_current_involution'):
        lo, hi = word['stage_ranges'][name]
        need(lo == last and lo <= hi <= len(operations), 'No gap in the late query')
        last = hi
    need(last == len(operations), 'Every late operation is inside the query')
    return operations


def routed_unit():
    return [{(i, UNIT): F(1)} for i in range(640)]


def route_row(row, route, left=True):
    return {(field, compose(route, old) if left else compose(old, route)): value
            for (field, old), value in row.items()}


def forward_rows(operations, initial=None):
    rows = routed_unit() if initial is None else [dict(row) for row in initial]
    maximum = max(sum(map(abs, row.values()), F(0)) for row in rows)
    height = 0
    for op, target, source, coefficient, route in operations:
        if op == 'map':
            rows[target] = route_row(rows[target], route)
        elif op == 'scale':
            rows[target] = {key: coefficient*x for key, x in rows[target].items()}
        else:
            need(op == 'add' and source != target, 'Distinct routed ADD')
            q.add(rows[target], route_row(rows[source], route), coefficient)
        maximum = max(maximum, sum(map(abs, rows[target].values()), F(0)))
        for value in rows[target].values():
            d = value.denominator
            need(d & (d-1) == 0, 'Dyadic complete content')
            height = max(height, d.bit_length()-1)
    return rows, {'row_one_norm': str(maximum), 'binary_height': height}


def reverse_columns(operations):
    columns = routed_unit()
    for op, target, source, coefficient, route in reversed(operations):
        if op == 'map':
            columns[target] = route_row(columns[target], route, left=False)
        elif op == 'scale':
            columns[target] = {key: coefficient*x for key, x in columns[target].items()}
        else:
            q.add(columns[source], route_row(columns[target], route, left=False), coefficient)
    rows = [{} for _ in range(640)]
    for source, column in enumerate(columns):
        for (target, route), value in column.items():
            q.add(rows[target], {(source, route): value})
    return rows


def routed_product(left, right):
    result = []
    for row in left:
        target = {}
        for (j, a), c in row.items():
            for (k, b), d in right[j].items():
                q.add(target, {(k, compose(a, b)): c*d})
        result.append(target)
    return result


def route_matrix(matrix, ports, stage, routes):
    return [{(j, compose(transpose(routes[stage, p]), routes[stage, j])): c for j, c in row.items()}
            for p, row in zip(ports, matrix)]


def complete_response(a, reader, pivots, s, t, routes):
    at = route_matrix(a, range(112), t, routes)
    ls = route_matrix(reader, pivots, s, routes)
    direct = routed_product(ls, at)
    need(sum(map(len, direct)) == 3824, 'Actual ordered selected response terms')
    response = [dict(row) for row in at]
    for p, row in zip(pivots, direct):
        response[p] = row
    return response, direct


def upper_negative_adjoint(response, ports):
    result = routed_unit()
    for p, row in zip(ports, response):
        for (j, route), c in row.items():
            q.add(result[j], {(112+p, transpose(route)): -c})
    return result


def lower(response):
    result = routed_unit()
    for p, row in enumerate(response):
        q.add(result[112+p], row)
    return result


def adjoint(rows):
    result = [{} for _ in rows]
    for i, row in enumerate(rows):
        for (j, route), c in row.items():
            q.add(result[j], {(i, transpose(route)): c})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    q.frozen(SOURCE, 'FREEZE.json', '09ad251a968be73fe95eefb05f57b842eb9f55e43822f029505256705120c811')
    q.frozen(FORWARD, 'FREEZE.json', '3ba792d18fbd57122ab4ae3301a3ff74b81751cf03fd2b7e8f9dc632759364e6')
    q.frozen(LANES/'bridge-review-20261017/involution-reader-review-20261020', 'FREEZE.json',
             'b4770cbd56bc8b115728529ab218d60ca2bd1a385896ba78cfdf374f04370c97')
    q.frozen(HERE.parent/'line-entry-reuse-review-20261020', 'FREEZE.json',
             'cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c')
    payload = json.loads(q.read(SOURCE/'final-normal/COMPLETE-DUAL.json.gz',
                                'f307406b952957ebcb2ce847da97e0d3f42c21ff340843755c6aa6de387321be', True))
    original = json.loads(q.read(FORWARD/'final-normal/INVOLUTION-READER.json.gz',
                                 '35f3735f1e2f9693c1b65aa292736d927dc38cbf0670af5e469097803187f091', True))
    capture = json.loads(q.read(q.ALG/'run-normal/ROW-CAPTURE.json',
                                '4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7'))
    algebra = json.loads(q.read(LANES/'controller-followthrough-20261017/row-involution-20261020/run-normal/ROW-INVOLUTION.json',
                                'a25551b3b99b82477fde561a742fabe1114acbfe6c67cd14284747aaac3dd95b'))
    views = json.loads(q.read(LANES/'bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json',
                              '125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473'))
    need(payload['pivots'] == original['pivots'] == q.P and
         payload['response'] == original['response'] == algebra['response'], 'Actual response and pivot binding')
    need(payload['stage_views'] == original['stage_views'] and
         payload['helper_hosting'] == original['helper_hosting'], 'Exact retained DATA and helper contracts')
    a, reader = q.rows(algebra['response']), q.rows(capture['centre_reader'])
    need(q.mul(a, a) == q.unit(112) and
         q.mul(reader, a) == [{j: -c for j, c in row.items()} for row in reader], 'Actual involution and reader')
    records = {(v['stage'], v['port']): v for v in views['entries']}
    need(len(records) == 336, 'Complete actual stage-port source')
    routes = {key: tuple(v['route_columns']) for key, v in records.items()}
    for route in routes.values():
        orthogonal(route)
    phase_report = phase_bindings(payload, records)
    selected = set(q.P)
    prefix_scalars, prefix_reports = {}, {}
    need(set(payload['native_prefixes']) == {'base', 'extra'}, 'Both native providers')
    for provider, word in payload['native_prefixes'].items():
        prefix_scalars[provider], prefix_reports[provider] = native_prefix(
            word, original['native_prefixes'][provider], a, selected)
    need(set(payload['queries']) == {'0:1', '0:2', '1:2'}, 'All three reader/service pairs')
    reports, late_reports = {}, {}
    for key, word in payload['queries'].items():
        s, t = word['reader_stage'], word['service_stage']
        need(key == str(s)+':'+str(t), 'Actual pair labels')
        late = query_operations(word, original['queries'][key], selected)
        response, direct = complete_response(a, reader, q.P, s, t, routes)
        expected = upper_negative_adjoint(response, range(112))
        expected_late = upper_negative_adjoint(direct, q.P)
        late_rows, late_growth = forward_rows(late)
        need(late_rows == reverse_columns(late) == expected_late and
             late_growth == {'row_one_norm': '30', 'binary_height': 2}, 'Independent complete late dual')
        late_reports[key] = {'columns': 640, 'scalar': 8440, 'maps': 672,
                             'phase_records': len(word['maps']), 'growth': late_growth}
        for provider, scalars in prefix_scalars.items():
            operations = []
            for op, target, source, coefficient in scalars:
                route = (UNIT if source is None else
                         compose(transpose(routes[t, target % 112]), routes[t, source % 112]))
                operations.append((op, target, source, F(coefficient), route))
            complete = operations+late
            actual = reverse_columns(complete)
            forward, growth = forward_rows(complete)
            need(actual == forward == expected, 'All640 columns of the complete physical splice')
            need(growth == {'row_one_norm': '40', 'binary_height': 2}, 'Complete emitted-boundary content peak')
            need(actual[112:] == routed_unit()[112:] and
                 all(j < 224 for row in actual[:112] for j, _ in row), 'All target baselines and416 outside fields')
            forward_star = adjoint(lower(response))
            need(routed_product(actual, forward_star) == routed_product(forward_star, actual) == routed_unit(),
                 'Both full operator inverse-adjoint products')
            without_prefix = reverse_columns(late)
            need(without_prefix != expected, 'A late dual alone is not the full service')
            wrong = list(complete)
            index = next(i for i, (op, _, source, _, route) in enumerate(wrong)
                         if op == 'add' and source >= 112 and route != UNIT)
            op, target, source, coefficient, route = wrong[index]
            wrong[index] = op, target, source, -coefficient, route
            need(reverse_columns(wrong) != expected, 'A wrong transferred sign fails')
            reports[key+':'+provider] = {'input_columns': 640, 'unchanged_arbitrary_fields': 416,
                'scalar_primitives': 14896, 'native_mass': 1792, 'native_children': 1520,
                'map_call_bound': 4384, 'growth': growth, 'both_inverse_products': True}
        print('Independent complete pair', key, flush=True)
    need(len(payload['invocations']) == len(original['invocations']) == 6, 'All six invocations')
    seen = set()
    for call, old in zip(payload['invocations'], original['invocations']):
        wanted = json.loads(json.dumps(old))
        wanted['ordered_blocks'][-1]['op'] = 'inverse_adjoint_fixed_past_reader_query'
        need(call == wanted, 'Exact complete dispatcher and changed query binding')
        s, t, provider = call['reader_stage'], call['service_stage'], call['provider']
        key = str(s)+':'+str(t)
        need(key+':'+provider in reports and (key, provider) not in seen, 'Unique complete resolved call')
        seen.add((key, provider))
        need(call['physical_input_level'] == t-1 and call['physical_output_level'] == t and
             call['stage_view_record'] == t-1 and call['query_key'] == key, 'Actual adjacent physical level')
        need([b['op'] for b in call['ordered_blocks']] == [
            'DATA_entry', 'native_input_adapters', 'complete_native_carrier_cover_sweep',
            'ordinary_output_adapters', 'DATA_exit', 'complete_cover_barrier',
            'inverse_adjoint_fixed_past_reader_query'], 'Exact physical order and whole-cover barrier')
        need(call['map_call_bound'] == {'DATA': 448, 'local_endpoint_adapters': 224,
                                       'native_side_maps': 3040, 'late_query': 672, 'total': 4384}
             and call['scalar_primitives'] == 14896, 'Full invocation bill')
    report = {'status': 'PASS_INDEPENDENT_COMPLETE_READER_DUAL',
        'native_prefixes': prefix_reports, 'late_queries': late_reports, 'services': reports,
        'DATA_phase_equations': phase_report, 'new_native_phase_operators': 0,
        'method': 'Independent full reverse coefficient columns, forward prefixes, and Boolean Z4 phase coefficients.',
        'scope': 'Six complete typed data services. No new recursive helper host, finite map cost, closed caller, or supplier claim.'}
    args.out.mkdir(parents=True, exist_ok=True)
    for name, value in [('REVIEW-CHECKS.json', report), ('INPUTS.json', q.INPUTS)]:
        (args.out/name).write_text(json.dumps(value, sort_keys=True, indent=2)+'\n')
    print(report['status'], flush=True)


if __name__ == '__main__':
    main()
