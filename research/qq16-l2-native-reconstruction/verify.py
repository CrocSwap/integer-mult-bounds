#!/usr/bin/env python3
"""Source-bound native realization of PR2470's L2 old-cut reconstruction.

New code by ywz65 with substantial OpenAI Codex assistance, Apache-2.0.
Source and phase helpers are adapted explicitly from PR2468, not an independent
reimplementation of that predecessor. No complete controller is claimed.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('l2_support', HERE/'native_support.py')
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)
need = N.need
OLD = tuple((e, 1) for e in N.AXES[:9])
E1 = tuple(N.AXES[9:17])


def field(side, p):
    return f'{side}{p}'


def program(R):
    out = []
    def add(op, **kwargs):
        out.append(dict(op=op, **kwargs))
    # First form the owned sum in the current X frame. X itself is read only.
    for p in N.U:
        add('line', field=field('Y', p), port=p, sign=1)
    for p in N.U:
        add('clear', field=field('Z', p), frame='current')
        add('add', dst=field('Z', p), src=field('X', p), coefficient='1')
        add('add', dst=field('Z', p), src=field('Y', p), coefficient='1')
    for p in N.U:
        add('line', field=field('Y', p), port=p, sign=-1)
    # The inherited positive rank-eight child, with a translated left wrapper,
    # removes F_E1. It acts on owned outputs only.
    for p in N.U:
        add('remove_stage', field=field('Z', p), rank=8)
    for side, ports in (('Z', N.U), ('T', N.T)):
        for p in ports:
            add('line', field=field(side, p), port=p, sign=-1)
        for p in ports:
            add('map', field=field(side, p), port=p, inverse=False)
    # Whole owner sweep: this body executes completely at one owner at a time.
    # C is one owned local scratch array; it is not a new cover-wide bank.
    add('private_sweep_begin')
    for k in range(8):
        add('clear', field='C', frame='common')
        for p in N.T:
            if R[k][p]:
                add('add', dst='C', src=field('T', p), coefficient=str(R[k][p]))
        for p in N.U:
            if R[k][p]:
                add('add', dst=field('Z', p), src='C', coefficient=str(-R[k][p]/4))
        add('clear', field='C', frame='identity')
    add('private_sweep_end')
    for side, ports in (('T', N.T), ('Z', N.U)):
        for p in ports:
            add('map', field=field(side, p), port=p, inverse=True)
        for p in ports:
            add('line', field=field(side, p), port=p, sign=1)
    return out


def replay(word, R, records, fault=None):
    original = {}
    for p in N.U:
        original[field('X', p)] = N.START
        original[field('Y', p)] = N.START + ((records[p]['q'], -1),)
    for p in N.T:
        original[field('T', p)] = OLD
    frames = dict(original)
    frames.update({field('Z', p): () for p in N.U})
    frames['C'] = ()
    rows = {key: {(key, N.AXES): Q(1)} for key in frames}
    counts = Counter()
    in_private = False
    for index, e in enumerate(word):
        op = e['op']
        counts[op] += 1
        if op == 'line':
            if fault == 'omit_Y_normalization' and e['field'] == field('Y', N.U[0]) and e['sign'] == 1:
                continue
            if fault == 'omit_T_restoration' and e['field'] == field('T', N.T[0]) and e['sign'] == 1:
                continue
            frames[e['field']] += ((records[e['port']]['q'], e['sign']),)
        elif op == 'remove_stage':
            if fault == 'omit_accumulated_E1_removal':
                continue
            sign = 1 if fault == 'use_positive_E1' else -1
            frames[e['field']] += tuple((axis, sign) for axis in E1)
        elif op == 'map':
            rec = records[e['port']]
            shift = rec['inverse_shift'] if e['inverse'] else rec['shift']
            if fault == 'omit_payload_translation' and e['port'] == N.U[0]:
                shift = 0
            if fault == 'wrong_inverse_translation' and e['inverse'] and e['port'] == N.U[0]:
                shift = rec['shift']
            frames[e['field']] = N.move_frame(frames[e['field']], (rec['g'], shift))
            rows[e['field']] = N.routed(rec['g'], rows[e['field']])
        elif op == 'clear':
            if fault == 'omit_owned_output_clear' and e['field'] == field('Z', N.U[0]):
                frames[e['field']] = N.START
                continue
            rows[e['field']] = {}
            frames[e['field']] = {'current': N.START, 'common': N.COMMON, 'identity': ()}[e['frame']]
        elif op == 'add':
            dst, src = e['dst'], e['src']
            need(N.phase(frames[dst]) == N.phase(frames[src]), f'native ADD frame mismatch at {index}')
            if 'C' in (dst, src):
                need(in_private, 'private ADD outside whole-owner body')
            c = Q(e['coefficient'])
            if fault == 'wrong_correction_sign' and dst.startswith('Z') and src == 'C':
                c = -c
            rows[dst] = N.combine(rows[dst], rows[src], c)
        elif op == 'private_sweep_begin':
            need(not in_private, 'nested private sweep')
            in_private = True
        else:
            need(op == 'private_sweep_end' and in_private, 'unknown event or private boundary')
            need(not rows['C'] and not frames['C'], 'private owner body not clean')
            in_private = False
    need(not in_private and not rows['C'] and not frames['C'], 'final owned scratch cleanup')
    for at, frame in original.items():
        need(N.phase(frames[at]) == N.phase(frame), 'borrowed source frame not restored: '+at)
        need(rows[at] == {(at, N.AXES): Q(1)}, 'borrowed source content not restored: '+at)
    expected = {}
    for p in N.U:
        row = {(field('X', p), N.AXES): Q(1), (field('Y', p), N.AXES): Q(1)}
        for t in N.T:
            c = -sum(R[k][p]*R[k][t] for k in range(8))/4
            if c:
                row = N.combine(row, {(field('T', t), N.multiply(records[p]['g'], records[t]['g'])): c})
        expected[field('Z', p)] = row
        need(N.phase(frames[field('Z', p)]) == N.phase(OLD), 'old-cut output frame')
        need(rows[field('Z', p)] == row, 'ordered L2 operator or owned dirt mismatch')
    return dict(counts), expected


def gaussian_multiply(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def native_kernels(records):
    lines = 0
    for p in N.U + N.T:
        q = records[p]['q']
        for sign in (-1, 1):
            recipe = N.line_recipe(q, sign)
            for address in range(512):
                need(N.kernel(recipe, address) == {address: (1, sign), address ^ q: (1, -sign)}, 'rank-one wrapper kernel')
                lines += 1
    # Embed canonical axes 0..7 into E1=9..16, leaving all other axes as
    # spectators. The wrapper is an involutive coordinate permutation.
    permutation = list(N.AXES)
    for j in range(8):
        permutation[j], permutation[j+9] = permutation[j+9], permutation[j]
    need(N.multiply(tuple(permutation), tuple(permutation)) == N.AXES, 'rank-eight inverse wrapper')
    shift = sum(E1)
    coefficients = 0
    for source in range(256):
        for destination in range(256):
            difference = source ^ destination
            actual = (1, 0)
            expected = (1, 0)
            for j in range(8):
                # Positive F8 followed by translation of all eight axes.
                bit = ((difference ^ 255) >> j) & 1
                actual = gaussian_multiply(actual, (1, -1) if bit else (1, 1))
                bit = (difference >> j) & 1
                expected = gaussian_multiply(expected, (1, 1) if bit else (1, -1))
            need(actual == expected, 'inverse rank-eight Gaussian coefficient')
            coefficients += 1
    need(gaussian_multiply((1, 1), (1, 1)) != gaussian_multiply((1, -1), (1, -1)), 'native inverse sign control')
    return {'rank_one_basis_columns': lines, 'rank_eight_matrix_coefficients': coefficients,
            'rank_eight_wrapper_columns': permutation, 'rank_eight_left_translation': shift,
            'rank_eight_denominator': 256}


def calculate():
    R, records, pins = N.load_sources()
    word = program(R)
    trace, expected = replay(word, R, records)
    need(trace == {'line': 400, 'clear': 112, 'add': 608, 'remove_stage': 96, 'map': 208,
                   'private_sweep_begin': 1, 'private_sweep_end': 1}, 'literal invoice')
    controls = {}
    for fault in ('omit_Y_normalization', 'omit_T_restoration', 'omit_accumulated_E1_removal',
                  'use_positive_E1', 'omit_payload_translation', 'wrong_inverse_translation',
                  'omit_owned_output_clear', 'wrong_correction_sign'):
        try:
            replay(word, R, records, fault)
        except ValueError as error:
            controls[fault] = str(error)
        else:
            raise ValueError('ineffective control: '+fault)
    # An inverse translated route must act on the logical owner too.
    bad_records = deepcopy(records)
    p = N.U[0]
    bad_records[p]['g'] = N.AXES
    try:
        replay(word, R, bad_records)
    except ValueError as error:
        controls['payload_only_owner_map'] = str(error)
    else:
        raise ValueError('owner-action control ineffective')
    kernels = native_kernels(records)
    # Use only the hash-authenticated scalar_cost function from the retained
    # QQ16 bill. In particular, a quarter coefficient costs12, not8 primitives.
    cost_path = N.ROOT/'research/joint-query/verify_scalar.py'
    parsed = ast.parse(cost_path.read_bytes())
    functions = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'scalar_cost']
    need(len(functions) == 1, 'retained scalar-cost function')
    environment = {'F': Q, 'need': need}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(cost_path), 'exec'), environment)
    scalar = 0
    scalar_coefficients = Counter()
    for event in word:
        if event['op'] == 'clear':
            scalar += environment['scalar_cost'](['clear'])
        elif event['op'] == 'add':
            c = Q(event['coefficient'])
            scalar_coefficients[str(abs(c))] += 1
            scalar += environment['scalar_cost'](['add', None, None, c.numerator, c.denominator])
    need(dict(scalar_coefficients) == {'1': 224, '1/4': 384} and scalar == 6624, 'source scalar allowance')
    # Explicit old/new-cut witness for the failed cheap route, on the full
    # 73-bit phase polynomial rather than owner/payload-constant inputs.
    failures = {}
    for p in N.U:
        rec = records[p]
        cheap = N.move_frame(N.START+((rec['q'], -1),), (rec['g'], rec['shift']))
        need(N.phase(cheap) != N.phase(N.COMMON), 'cheap alignment unexpectedly legal')
        failures[str(p)] = True
    invoice = {'rank_one_children': 400, 'rank_eight_children': 96, 'native_rank_mass': 1168,
               'native_wrapper_maps': 992, 'full_cover_maps': 208, 'ADD_macros': 608,
               'CLEAR_macros': 112, 'scalar_real_primitive_allowance': scalar,
               'absolute_ADD_coefficients': dict(scalar_coefficients),
               'owned_reconstruction_output_arrays': 96, 'owned_private_scratch_arrays_per_owner': 1,
               'borrowed_source_arrays_unchanged': 200, 'retained_F0_T_source_arrays': 8,
               'post_B1_X_sources_read_only': 96, 'literal_events': len(word)}
    operator = {at: [[v, list(g), str(c)] for (v, g), c in sorted(row.items())] for at, row in expected.items()}
    return {'status': 'PASS_QQ16_L2_NATIVE_RECONSTRUCTION', 'source_sha256': pins, 'member_sha256': N.MEMBERS,
            'contract': 'Z_U = X2_U + Y2_U - D1_U^-1 K_U R_T D1_T retained_x1_T; output frame F_L',
            'source_variables': 200, 'invoice': invoice, 'trace': trace, 'controls': controls,
            'cheap_current_alignment_rejected_ports': len(failures), 'native_kernels': kernels,
            'operator_sha256': hashlib.sha256(json.dumps(operator, sort_keys=True).encode()).hexdigest(),
            'scope': 'One local native reconstruction; retained source delivery, full decoder, physical cover cost, hosting and supplier saving remain open'}, word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result, word = calculate()
    for name, value in (('RESULT.json', result), ('WORD.json', word)):
        path = HERE/name
        if args.write:
            with path.open('x', encoding='utf-8', newline='\n') as handle:
                json.dump(value, handle, sort_keys=True, indent=2)
                handle.write('\n')
        else:
            need(json.loads(path.read_text(encoding='utf-8')) == value, 'committed '+name+' differs')
    print('PASS_QQ16_L2_NATIVE_RECONSTRUCTION sources=200 outputs=96 rank_mass=1168 controls=9 no_new_kappa')


if __name__ == '__main__':
    main()
