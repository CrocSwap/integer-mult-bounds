#!/usr/bin/env python3
"""A complete raw-port expansion and paid-path support certificate.

Cinna Davis, with OpenAI Codex assistance. Apache-2.0. No new kappa.
"""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_sources():
    inventory = json.loads((HERE/'SOURCES.json').read_text())
    authenticated = {}
    for row in inventory['files']:
        if row['usage'] == 'input':
            data = (ROOT/row['path']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == row['sha256'], 'pinned source bytes')
            authenticated[row['path']] = data

    def module(path):
        m = types.ModuleType('authenticated_dependency')
        m.__file__ = str(ROOT/path)
        exec(compile(authenticated[path], m.__file__, 'exec'), m.__dict__)
        return m

    # Only field arithmetic and coordinate monomial action are reused.
    helper = module('research/two-image-compensated-pair/verify.py')
    source = module('research/complex-block3-five-in-fourteen/verify_schedule.py')
    return helper, source, {p: hashlib.sha256(b).hexdigest() for p, b in authenticated.items()}


def program(upgrade_closing=False, reuse_updated_fifth=False):
    p = []
    S = ['S0', 'S1', 'S2']
    for port in range(5):
        source, target = (port, port+1) if port < 4 else (4, 0)
        t, u = 5+2*port, 6+2*port
        if port == 4 and reuse_updated_fifth:
            source = 12  # fourth port's updated target, instead of original x5.
        p += [{'op': 'copy', 'destination': t, 'source': source},
              {'op': 'copy', 'destination': u, 'source': target},
              {'op': 'paid', 'bank': t, 'axis': 0},
              {'op': 'add_word', 'destination': u, 'source': t,
               'word': S+['U']+S, 'coefficient': 1},
              {'op': 'add_word', 'destination': u, 'source': t,
               'word': S+['V']+S, 'coefficient': 2},
              {'op': 'paid', 'bank': u, 'axis': 0}]
        if port < 4 or upgrade_closing:
            p += [{'op': 'monomial', 'bank': u, 'word': ['S0', 'S0', 'S2', 'S2']},
                  {'op': 'paid', 'bank': u, 'axis': 2},
                  {'op': 'monomial', 'bank': u, 'word': ['V', 'S1', 'S1']}]
    return p


def polyadd(a, b):
    return tuple((a[i] if i < len(a) else 0)+(b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b))))


def degree(p):
    return len(p)-1


def support_trace(ir):
    state = [[(1,) if bank == original else () for original in range(5)]
             for bank in range(15)]
    maximum = [0]*5; trace = []
    for index, event in enumerate(ir):
        op = event['op']
        if op == 'copy':
            state[event['destination']] = list(state[event['source']])
        elif op == 'add_word':
            d, s = event['destination'], event['source']
            state[d] = [polyadd(a, b) for a, b in zip(state[d], state[s])]
        elif op == 'paid':
            bank = event['bank']
            state[bank] = [(0,)+p if p else () for p in state[bank]]
        else:
            need(op == 'monomial', 'declared support operation')
        current = [max(degree(row[j]) for row in state) for j in range(5)]
        maximum = [max(a, b) for a, b in zip(maximum, current)]
        trace.append({'event': index, 'operation': op, 'max_paid_depth_by_input': current})
    total_fifth = ()
    for row in state:
        total_fifth = polyadd(total_fifth, row[4])
    return {'final_support_polynomials_by_bank_and_input': state,
            'max_paid_depth_by_input': maximum, 'total_fifth_polynomial': total_fifth,
            'prefix_depths': trace}


def paid(v, axis, width, field):
    result = list(v)
    a = field.div(field.add(field.one, field.i), field.scalar(2))
    b = field.div(field.add(field.one, field.neg(field.i)), field.scalar(2))
    for column in range(width):
        bit = 1 << (3*column+axis)
        for x in range(len(v)):
            if x & bit:
                continue
            y = x ^ bit; left, right = result[x], result[y]
            result[x] = field.add(field.mul(a, left), field.mul(b, right))
            result[y] = field.add(field.mul(b, left), field.mul(a, right))
    return result


def execute(ir, inputs, width, field, helper):
    n = 8**width
    state = [list(v) for v in inputs]+[[field.zero]*n for _ in range(10)]
    for event in ir:
        op = event['op']
        if op == 'copy':
            state[event['destination']] = list(state[event['source']])
        elif op == 'paid':
            bank = event['bank']
            state[bank] = paid(state[bank], event['axis'], width, field)
        elif op == 'monomial':
            bank = event['bank']
            for letter in event['word']:
                state[bank] = helper.address_vector(state[bank], letter, width, field)
        else:
            value = list(state[event['source']])
            for letter in event['word']:
                value = helper.address_vector(value, letter, width, field)
            c = field.scalar(event['coefficient']); bank = event['destination']
            state[bank] = [field.add(a, field.mul(c, b)) for a, b in zip(state[bank], value)]
    return state


def convert(matrix, field):
    if field.p is None:
        return matrix
    return [[field.add(field.scalar(a.numerator, a.denominator),
                      field.mul(field.i, field.scalar(b.numerator, b.denominator)))
             for a, b in row] for row in matrix]


def tensor_action(matrix, v, width, field):
    if not any(x != field.zero for x in v):
        return list(v)
    result = list(v); n = len(v)
    for column in range(width):
        stride = 8**column; out = [field.zero]*n
        for anchor in range(n):
            if (anchor//stride) % 8:
                continue
            for row in range(8):
                total = field.zero
                for k in range(8):
                    if matrix[row][k] != field.zero:
                        total = field.add(total, field.mul(matrix[row][k], result[anchor+k*stride]))
                out[anchor+row*stride] = total
        result = out
    return result


def oracle_matrices(source, field):
    o = source.load_operators()
    U = source.monomial([0, 5, 2, 7, 4, 1, 6, 3])
    V = source.monomial([0, 2, 1, 3, 4, 6, 5, 7]); S = source.s_letter(7)
    P, Q = source.word(S, U, S), source.word(S, V, S)
    matrices = {'A': o['A'], 'D': o['D'], 'K': o['K'], 'T': o['T'],
                'BP': source.word(o['D'], P, o['A']),
                'BQ': source.word(o['D'], Q, o['A']),
                'FP': source.word(o['A'], P, o['A']),
                'FQ': source.word(o['A'], Q, o['A'])}
    need(all(sum(x != (0, 0) for x in row) == 8 for row in o['K']), 'dense target base kernel')
    return {name: convert(matrix, field) for name, matrix in matrices.items()}


def oracle(inputs, width, field, matrices):
    output = [list(v) for v in inputs]
    for port in range(5):
        x, y = (port, port+1) if port < 4 else (4, 0)
        t = tensor_action(matrices['A'], inputs[x], width, field)
        u = tensor_action(matrices['D' if port < 4 else 'A'], inputs[y], width, field)
        for name, coefficient in [('BP' if port < 4 else 'FP', 1),
                                  ('BQ' if port < 4 else 'FQ', 2)]:
            term = tensor_action(matrices[name], inputs[x], width, field)
            u = [field.add(a, field.mul(field.scalar(coefficient), b)) for a, b in zip(u, term)]
        output += [t, u]
    return output


def calculate():
    helper, source, hashes = load_sources(); ir = program(); trace = support_trace(ir)
    need(dict(Counter(e['op'] for e in ir)) ==
         {'copy': 10, 'paid': 14, 'add_word': 10, 'monomial': 8}, 'literal caller invoice')
    need(trace['max_paid_depth_by_input'] == [3, 3, 3, 3, 2], 'complete input depth vector')
    need(trace['total_fifth_polynomial'] == (1, 1, 3), 'complete fifth-input support polynomial')
    checks = []; sector_witnesses = []
    for width, field in [(1, helper.Field()), (2, helper.Field(17))]:
        n = 8**width; matrices = oracle_matrices(source, field); columns = 0
        for bank in range(5):
            for index in range(n):
                inputs = [[field.zero]*n for _ in range(5)]
                inputs[bank][index] = field.one
                need(execute(ir, inputs, width, field, helper) == oracle(inputs, width, field, matrices),
                     'actual raw-port full input column')
                columns += 1
        checks.append({'width': width, 'field': 'Q(i)' if field.p is None else 'F17(i=4)',
                       'independent_input_columns': columns, 'output_banks_checked': 15})
        for sigma in (1, -1):
            vector = [field.zero]*n
            if sigma == 1:
                vector[0] = field.one
            else:
                vector[1], vector[4] = field.one, field.neg(field.one)
            need(tensor_action(matrices['T'], vector, width, field) ==
                 [field.mul(field.scalar(sigma), x) for x in vector], 'actual swap-sector input')
            actual = list(vector)
            for axis in (0, 1, 2):
                actual = paid(actual, axis, width, field)
            need(actual == tensor_action(matrices['K'], vector, width, field),
                 'ordinary three-call target positive control')
            support = sum(x != field.zero for x in actual)
            need(support == (8**width if sigma == 1 else 8**width//2),
                 'dense target on either swap-sector witness')
            sector_witnesses.append({'width': width, 'sigma': sigma,
                                     'input_support': 1 if sigma == 1 else 2,
                                     'target_support': support})
    upgraded = program(upgrade_closing=True); upgraded_trace = support_trace(upgraded)
    need(sum(e['op'] == 'paid' for e in upgraded) == 15 and
         upgraded_trace['max_paid_depth_by_input'] == [3]*5, 'changed paid closing removes depth obstruction')
    changed = program(reuse_updated_fifth=True); changed_trace = support_trace(changed)
    need(sum(e['op'] == 'paid' for e in changed) == 14 and
         changed_trace['max_paid_depth_by_input'][4] == 4, 'updated closing feed changes hypothesis')
    field = helper.Field(17); inputs = [[field.zero]*8 for _ in range(5)]; inputs[4][0] = field.one
    need(execute(changed, inputs, 1, field, helper) != execute(ir, inputs, 1, field, helper),
         'updated feed is not the declared raw snapshot')
    dominance = []
    for decoder_column_bound in (1, 2, 3, 16, 1000):
        width = (5*decoder_column_bound).bit_length(); z = 2**width
        bound = decoder_column_bound*(1+z+3*z*z)
        need(8**width > bound, 'strict target-support contradiction')
        dominance.append({'decoder_column_bound': decoder_column_bound, 'width': width,
                           'raw_and_decoder_support_bound': bound, 'target_support': 8**width})
        minus_width = (20*decoder_column_bound).bit_length(); mz = 2**minus_width
        need(8**minus_width//2 > 2*decoder_column_bound*(1+mz+3*mz*mz),
             'negative-sector support contradiction')
    receipt = {'schema_version': 1, 'claim': 'no_free_completion_of_the_stated_fresh_raw_schedule',
               'no_new_kappa': True, 'source_hashes': hashes,
               'caller_instruction_counts': dict(sorted(Counter(e['op'] for e in ir).items())),
               'support_certificate': trace, 'intended_caller_checks': checks,
               'sector_witness_supports': sector_witnesses,
               'support_dominance_examples': dominance,
               'fifteen_call_positive_control_depths': upgraded_trace['max_paid_depth_by_input'],
               'changed_fourteen_call_feed_depths': changed_trace['max_paid_depth_by_input'],
               'limits': 'No different query chronology or full five-in-fourteen exclusion; recording-only taps of this literal expansion remain depth<=2 on x5.'}
    return ir, receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-result', type=Path)
    args = ap.parse_args(); ir, actual = calculate()
    if args.write_result:
        with args.write_result.with_name('PROGRAM.json').open('x') as stream:
            json.dump(ir, stream, indent=2, sort_keys=True); stream.write('\n')
        with args.write_result.open('x') as stream:
            json.dump(actual, stream, indent=2, sort_keys=True); stream.write('\n')
    else:
        need(json.loads((HERE/'PROGRAM.json').read_text()) == ir, 'literal caller equality')
        need(json.loads(json.dumps(actual)) == json.loads((HERE/'RESULT.json').read_text()), 'receipt equality')
    print('PASS_FIVE_IN_FOURTEEN_PATH_DEPTH paid_calls=14 fifth_depth=2 '
          'raw_support=1+z+3z^2 input_columns=360 no_new_kappa')


if __name__ == '__main__':
    main()
