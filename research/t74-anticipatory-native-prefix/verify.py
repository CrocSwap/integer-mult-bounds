#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact checker for PR2339's grouped native initial prefix.

No emitter, Clifford compiler, numpy or predecessor checker is imported.
Arithmetic is integer Gaussian arithmetic with common denominator two.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 512


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def integer(value, lo, hi):
    return type(value) is int and lo <= value < hi


def linear(columns, x):
    result = 0
    for j, image in enumerate(columns):
        if x & (1 << j):
            result ^= image
    return result


def reference_actions(columns):
    """K|x> = i^q(Gx)|Gx>; invert G by enumerating its permutation.

    q uses I + G^{-T}G^{-1}, with diagonal coefficients lifted to {0,1}
    and off-diagonal coefficients doubled: the PR2226 phase convention.
    """
    require(len(columns) == 9 and all(integer(v, 0, N) for v in columns), 'G schema')
    perm = [linear(columns, x) for x in range(N)]
    require(len(set(perm)) == N, 'G invertibility')
    inverse = [0] * N
    for x, y in enumerate(perm):
        inverse[y] = x
    columns_i = [inverse[1 << j] for j in range(9)]
    q = [[((columns_i[i] & columns_i[j]).bit_count() & 1) ^ (i == j)
          for j in range(9)] for i in range(9)]
    phase = []
    for y in perm:
        bits = [j for j in range(9) if y >> j & 1]
        phase.append((sum(q[j][j] for j in bits)
                      + 2 * sum(q[i][j] for i in bits for j in bits if i < j)) % 4)
    return {
        'K': list(zip(perm, phase)),
        'inverse': [(inverse[y], -phase[inverse[y]] % 4) for y in range(N)],
        'conjugate': [(y, -p % 4) for y, p in zip(perm, phase)],
        'transpose': [(inverse[y], phase[inverse[y]]) for y in range(N)],
    }


def decode_recipe(rec):
    require(set(rec) == {'matrix_rows', 'quadratic_rows', 'linear_Z4', 'offset', 'phase'}, 'recipe fields')
    rows, q, a = rec['matrix_rows'], rec['quadratic_rows'], rec['linear_Z4']
    require(len(rows) == len(q) == len(a) == 9, 'recipe dimensions')
    require(all(integer(v, 0, N) for v in rows + q), 'recipe binary rows')
    require(all(integer(v, 0, 4) for v in a), 'recipe linear phases')
    require(integer(rec['phase'], 0, 4) and integer(rec['offset'], 0, N), 'recipe scalar fields')
    require(all((q[i] >> j & 1) == (q[j] >> i & 1) for i in range(9) for j in range(9)), 'symmetric Q')
    action = []
    for x in range(N):
        y = sum(((row & x).bit_count() & 1) << j for j, row in enumerate(rows)) ^ rec['offset']
        p = rec['phase'] + sum(a[j] for j in range(9) if x >> j & 1)
        p += 2 * sum(1 for i in range(9) for j in range(i + 1, 9)
                     if (x >> i & 1) and (x >> j & 1) and (q[i] >> j & 1))
        action.append((y, p % 4))
    require(len({y for y, _ in action}) == N, 'recipe permutation')
    return action


def decode_gates(gates):
    # Phase predicates use the current address, making gate order observable.
    for gate in gates:
        require(type(gate) is list and gate, 'gate schema')
        tag = gate[0]
        if tag in ('cnot', 'cz'):
            require(len(gate) == 3 and all(integer(v, 0, 9) for v in gate[1:])
                    and gate[1] != gate[2], 'two-coordinate gate')
        elif tag == 'z4':
            require(len(gate) == 3 and integer(gate[1], 0, 9) and integer(gate[2], 1, 4), 'z4 gate')
        elif tag == 'x':
            require(len(gate) == 2 and integer(gate[1], 0, 9), 'x gate')
        elif tag == 'phase':
            require(len(gate) == 2 and integer(gate[1], 1, 4), 'global phase gate')
        else:
            raise ValueError('non-monomial address gate')
    action = []
    for x in range(N):
        y, p = x, 0
        for gate in gates:
            tag = gate[0]
            if tag == 'cnot':
                y ^= ((y >> gate[2]) & 1) << gate[1]
            elif tag == 'cz':
                p += 2 * ((y >> gate[1]) & 1) * ((y >> gate[2]) & 1)
            elif tag == 'z4':
                p += gate[2] * ((y >> gate[1]) & 1)
            elif tag == 'x':
                y ^= 1 << gate[1]
            else:
                p += gate[1]
        action.append((y, p % 4))
    return action


def input_contract(word):
    require(word['kind'] == 'BORROW-WORD' and word['report']['h'] == 9 and len(word['ports']) == 112, 'word boundary')
    require(len(word['warps']) == 80 and len(word['initial_corrections']) == 64, 'source counts')
    require(word['report']['R'] == 480 and len(word['removed']) == len(set(word['removed'])) == 80
            and all(integer(r, 224, 704) for r in word['removed']), '624 live input registers')
    terms = word['initial_corrections']
    for t in terms:
        require(set(t) == {'target', 'source', 'operator_word', 'coefficient'}, 'term schema')
        require(integer(t['target'], 112, 224) and integer(t['source'], 224, 704), 'bipartite initial roles')
        require(t['source'] not in word['removed'] and not word['start_extra'].get(str(t['source']), []), 'frame-zero lender')
        require(type(t['operator_word']) is list and len(t['operator_word']) == 1
                and integer(t['operator_word'][0], 1, 81), 'one forward operator')
        require(word['warps'][t['operator_word'][0] - 1][1] == t['source'], 'operator-to-lender binding')
        require(Fraction(t['coefficient']) in (1, -1, Fraction(1, 2), Fraction(-1, 2)), 'coefficient domain')
    sources = {t['source'] for t in terms}
    targets = {t['target'] for t in terms}
    ops = sorted({t['operator_word'][0] for t in terms})
    require(len(sources) == len(targets) == len(ops) == 32, 'active roles')
    require(set(Counter(t['operator_word'][0] for t in terms).values()) == {2}, 'two terms per operator')
    require(max(sources | targets) < min(word['removed']), 'prefix IDs unchanged by native compaction')
    return sorted(sources | targets), ops


def rotate(a, p):
    r, i = a
    return ((r, i), (-i, r), (-r, -i), (i, -r))[p % 4]


def accumulate(row, source, numerator, denominator):
    for column, (r, i) in source.items():
        require(r * numerator % denominator == i * numerator % denominator == 0, 'common exact denominator')
        a, b = row.get(column, (0, 0))
        value = (a + r * numerator // denominator, b + i * numerator // denominator)
        if value == (0, 0):
            row.pop(column, None)
        else:
            row[column] = value


def identity_state(active):
    return {r: [{r * N + x: (2, 0)} for x in range(N)] for r in active}


def scalar_macro(row, source, instructions):
    # One owned coefficient scalar, reused at successive addresses. It is
    # not an arbitrary dirty helper and cannot be retained across macros.
    temporary = {}
    for e in instructions:
        if e == ['clear']:
            temporary = {}
        elif e == ['read_source']:
            accumulate(temporary, source, 1, 1)
        elif e == ['half']:
            divided = {}
            accumulate(divided, temporary, 1, 2)
            temporary = divided
        elif len(e) == 2 and e[0] == 'write_target' and type(e[1]) is int and e[1] in (-1, 1):
            accumulate(row, temporary, e[1], 1)
        else:
            raise ValueError('unknown scalar primitive')
    require(not temporary, 'coefficient scratch not cleared')


def replay(program, actions, active, scalar_lowerings):
    state = identity_state(active)
    for event in program:
        require(type(event) is list and event, 'event schema')
        if event[0] == 'monomial':
            require(len(event) == 3 and event[1] in state and event[2] in actions, 'monomial event')
            values = [None] * N
            for x, (y, p) in enumerate(actions[event[2]]):
                values[y] = {col: rotate(value, p) for col, value in state[event[1]][x].items()}
            state[event[1]] = values
        elif event[0] == 'scalar':
            require(len(event) == 3 and event[2] == 0, 'scalar boundary')
            e = event[1]
            require(len(e) == 5 and e[0] == 'add' and e[1][0] == e[2][0] == 'L', 'scalar vocabulary')
            t, s, a, b = e[1][1], e[2][1], e[3], e[4]
            require(t in state and s in state and t != s and type(a) is type(b) is int and b > 0, 'scalar operands')
            for row, src in zip(state[t], state[s]):
                scalar_macro(row, src, scalar_lowerings[str(Fraction(a, b))])
        else:
            raise ValueError('unpriced/unsupported event')
    return state


def direct_boundary(word, active, refs, backward):
    expected = identity_state(active)
    for term in word['initial_corrections']:
        t, s, op = term['target'], term['source'], term['operator_word'][0]
        q = Fraction(term['coefficient'])
        for x, (y, p) in enumerate(refs[op]['K']):
            unit = rotate((2, 0), p)
            if backward:
                # Ordinary transpose, NOT conjugate transpose.
                accumulate(expected[s][x], {t * N + y: unit}, -q.numerator, q.denominator)
            else:
                accumulate(expected[t][y], {s * N + x: unit}, q.numerator, q.denominator)
    return expected


def ungrouped(word, backward):
    events = []
    for term in word['initial_corrections']:
        t, s, op = term['target'], term['source'], term['operator_word'][0]
        q = Fraction(term['coefficient'])
        before, after = ('conjugate', 'transpose') if backward else ('K', 'inverse')
        events.append(['monomial', s, f'{op}:{before}'])
        events.append(['scalar', ['add', ['L', s if backward else t], ['L', t if backward else s],
                                 -q.numerator if backward else q.numerator, q.denominator], 0])
        events.append(['monomial', s, f'{op}:{after}'])
    return events


def billed(program, recipes, scalar_lowerings):
    bill, gates, phases = Counter(), Counter(), Counter()
    for e in program:
        if e[0] == 'monomial':
            bill['monomial_applications'] += 1
            rec = recipes[e[2]]
            gates.update(g[0] for g in rec['address_gates'])
            action = decode_recipe(rec['monomial'])
            bill['moved_address_entries'] += sum(y != x for x, (y, _) in enumerate(action))
            phases.update(str(p) for _, p in action)
        else:
            bill['scalar_add_macros'] += 1
            q = Fraction(e[1][3], e[1][4])
            bill['real_component_scalar_primitive_bound'] += 2 * len(scalar_lowerings[str(q)])
    bill['positive_recursive_children'] = 0
    bill['indexed_complex_additions_at_512'] = N * bill['scalar_add_macros']
    return {'operations': dict(sorted(bill.items())), 'address_gate_applications': dict(sorted(gates.items())),
            'monomial_entry_phase_histogram': dict(sorted(phases.items()))}


def check_provider(word, data, baseline=True):
    active, ops = input_contract(word)
    require(set(data['scalar_lowerings']) == {'1', '-1', '1/2', '-1/2'}, 'scalar lowering inventory')
    require(data['address_bits'] == 9 and data['operators'] == ops, 'operator inventory')
    refs = {op: reference_actions(word['warps'][op - 1][2]) for op in ops}
    require(set(data['recipes']) == {f'{op}:{name}' for op in ops for name in refs[op]}, 'recipe inventory')
    actions = {}
    for key, rec in data['recipes'].items():
        op, kind = key.split(':')
        action = decode_recipe(rec['monomial'])
        require(action == refs[int(op)][kind], 'Gaussian recipe equality: ' + key)
        require(decode_gates(rec['address_gates']) == action, 'primitive address equality: ' + key)
        actions[key] = action
    receipts = {}
    for backward in (False, True):
        name = 'backward' if backward else 'forward'
        stream = data['programs'][name]
        actual = replay(stream, actions, active, data['scalar_lowerings'])
        expected = direct_boundary(word, active, refs, backward)
        require(actual == expected, 'complete arbitrary-input prefix: ' + name)
        if baseline:
            require(replay(ungrouped(word, backward), actions, active, data['scalar_lowerings']) == expected, 'ungrouped positive control')
        bill = billed(stream, data['recipes'], data['scalar_lowerings'])
        claimed = data['bill_per_orientation']
        for key in ('positive_recursive_children', 'monomial_applications', 'scalar_add_macros', 'real_component_scalar_primitive_bound'):
            require(bill['operations'][key] == claimed[key], 'bill mismatch: ' + key)
        require(bill['operations']['monomial_applications'] == 64 and len(stream) == 128, 'grouping count')
        require(claimed['ungrouped_monomial_applications'] == 128 and claimed['coefficient_streams_peak'] == 1
                and claimed['scalar_bound_excludes_monomial_routing'] is True, 'bill interpretation')
        encoded_rows = [[r, [[[col, *a] for col, a in sorted(row.items())] for row in actual[r]]] for r in active]
        receipts[name] = {'events': len(stream), 'active_input_columns': len(active) * N,
                          'untouched_input_columns_by_footprint': (624 - len(active)) * N,
                          'boundary_sha256': sha(canonical(encoded_rows)), **bill}
    return receipts


def controls(word, data):
    rejected = []

    def reject(name, reason, alter, use_word=False):
        w, d = copy.deepcopy(word), copy.deepcopy(data)
        alter(w if use_word else d)
        try:
            check_provider(w, d, baseline=False)
        except ValueError as error:
            require(str(error).startswith(reason), 'wrong rejection reason: ' + name + ': ' + str(error))
            rejected.append(name)
        else:
            raise ValueError('negative control accepted: ' + name)

    key = next(k for k in data['recipes'] if k.endswith(':K'))
    reject('wrong global phase', 'Gaussian recipe equality', lambda d: d['recipes'][key]['monomial'].__setitem__('phase', 1))
    reject('wrong permutation', 'Gaussian recipe equality', lambda d: d['recipes'][key]['monomial']['matrix_rows'].reverse())
    reject('wrong address phase gate', 'primitive address equality', lambda d: d['recipes'][key]['address_gates'].insert(0, ['phase', 1]))
    reject('wrong coefficient sign', 'complete arbitrary-input prefix', lambda d: d['programs']['forward'][1][1].__setitem__(3, -d['programs']['forward'][1][1][3]))
    reject('omitted restoration', 'complete arbitrary-input prefix', lambda d: d['programs']['forward'].pop(3))
    reject('addition before warp', 'complete arbitrary-input prefix', lambda d: d['programs']['forward'].__setitem__(slice(0, 2), list(reversed(d['programs']['forward'][:2]))))
    reject('wrong dual conjugation', 'complete arbitrary-input prefix', lambda d: d['programs']['backward'][0].__setitem__(2, d['programs']['backward'][0][2].replace('conjugate', 'K')))
    reject('wrong real-component bill', 'bill mismatch', lambda d: d['bill_per_orientation'].__setitem__('real_component_scalar_primitive_bound', 571))
    reject('uncleared coefficient scratch', 'coefficient scratch not cleared', lambda d: d['scalar_lowerings']['1/2'].pop())
    reject('omitted scalar halving', 'complete arbitrary-input prefix', lambda d: d['scalar_lowerings']['1/2'].remove(['half']))
    first = word['initial_corrections'][0]
    reject('nonzero lender entrance', 'frame-zero lender', lambda w: w['start_extra'].__setitem__(str(first['source']), [1]), True)
    reject('wrong source-to-operator binding', 'operator-to-lender binding', lambda w: w['initial_corrections'][0].__setitem__('source', word['initial_corrections'][1]['source']), True)
    return rejected


def verify():
    upstream = json.loads((HERE / 'UPSTREAM.json').read_bytes())
    for record in upstream['files']:
        data = (HERE / record['path']).read_bytes()
        require(sha(data) == record['sha256'], 'upstream SHA256: ' + record['path'])
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == record['git_blob'], 'upstream Git blob: ' + record['path'])
    prefix = json.loads(gzip.decompress((HERE / 'PREFIX.json.gz').read_bytes()))
    require(prefix['kind'] == 'PR2339_NATIVE_INITIAL_PREFIX' and prefix['schema_version'] == 1
            and set(prefix['providers']) == {'base', 'extra'}, 'certificate schema')
    result = {'status': 'PASS_T74_ANTICIPATORY_NATIVE_PREFIX', 'providers': {},
              'prefix_sha256': sha(canonical(prefix)), 'upstream_sha256': sha(canonical(upstream))}
    for provider in ('base', 'extra'):
        raw = (HERE / 'inputs' / f'BORROW-WORD-80{provider}.json.gz').read_bytes()
        word = json.loads(gzip.decompress(raw))
        data = prefix['providers'][provider]
        require(data['word_sha256'] == sha(raw), 'source word binding')
        result['providers'][provider] = {
            'operator_count': 32, 'recipes_checked_on_512_columns': 128,
            'orientations': check_provider(word, data), 'controls_rejected': controls(word, data),
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='write receipt exclusively to a new file')
    args = parser.parse_args()
    result = verify()
    if args.out:
        with args.out.open('x') as f:
            f.write(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        require(result == json.loads((HERE / 'EXPECTED.json').read_bytes()), 'complete receipt drift')
    print('PASS_T74_ANTICIPATORY_NATIVE_PREFIX providers=2 orientations=2 terms=64 monomials=64 scalar_bound=572 controls=24 no_new_kappa')


if __name__ == '__main__':
    main()
