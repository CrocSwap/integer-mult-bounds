#!/usr/bin/env python3
"""Current-frame L2 realization with an explicitly charged ordinary-state consumer.

New code by ywz65 with substantial OpenAI Codex assistance, Apache-2.0.
Adapted from PR2492 and its PR2468 lineage, explicitly credited and retained.
The changed output frame is material. No complete controller is claimed.
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


def program(R, consumer=True):
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
    # Upgrade only the eight retained records to the common current frame.
    for p in N.T:
        add('stage', field=field('T', p), rank=8, sign=1)
    for side, ports in (('Z', N.U), ('T', N.T)):
        for p in ports:
            add('current_map', field=field(side, p), port=p, inverse=False)
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
            add('current_map', field=field(side, p), port=p, inverse=True)
    for p in N.T:
        add('stage', field=field('T', p), rank=8, sign=-1)
    add('checkpoint', name='x1_U_in_current_frame')
    if consumer:
        # The consumer is part of the literal bill. It uses no new output array.
        for p in N.U:
            add('add', dst=field('Z', p), src=field('X', p), coefficient='-1', consumer=True)
    else:
        # Fixed alternative epilogue: exactly the predecessor's F_L x1 output.
        for p in N.U:
            add('stage', field=field('Z', p), rank=8, sign=-1)
    return out


def output_rows(R, records, consumer):
    expected = {}
    for p in N.U:
        row = {(field('Y', p), N.AXES): Q(1)}
        if not consumer:
            row[(field('X', p), N.AXES)] = Q(1)
        for t in N.T:
            c = -sum(R[k][p]*R[k][t] for k in range(8))/4
            if c:
                row = N.combine(row, {(field('T', t), N.multiply(records[p]['g'], records[t]['g'])): c})
        expected[field('Z', p)] = row
    return expected


def current_maps(records):
    result = {}
    target = N.phase(N.START)
    for p, rec in records.items():
        g = rec['g']
        need(all((a & b).bit_count() % 2 == (i == j)
                 for i, a in enumerate(g) for j, b in enumerate(g)), 'actual orthogonal owner matrix')
        b = rec['shift'] ^ rec['inverse_shift']
        need(N.act(g, b) == b, 'current translation is fixed by the involution')
        need(N.phase(N.move_frame(N.START, (g, b))) == target, 'full current frame preserved')
        need(N.phase(N.move_frame(N.START, (g, rec['shift']))) != target, 'old translation is not the current map')
        result[str(p)] = {'owner_columns': list(g), 'translation': b, 'inverse_translation': N.act(g, b)}
    need(len(result) == 104, 'all current map ports')
    return result


def direct_current_frame_checks(records):
    """Independent parity evaluations; no phase-polynomial helper is called."""
    characters = [0] + list(N.AXES) + [a | b for i, a in enumerate(N.AXES) for b in N.AXES[i+1:]]
    checks, rejected = 0, {}
    for p, rec in records.items():
        b = rec['shift'] ^ rec['inverse_shift']
        vectors = rec['g'][:17]
        for w in characters:
            actual = (sum((w & v).bit_count() % 2 for v in vectors) + 2*((w & b).bit_count() % 2)) % 4
            expected = sum((w & e).bit_count() % 2 for e in N.AXES[:17]) % 4
            need(actual == expected, 'independent current-frame character check')
            checks += 1
        difference = b ^ rec['shift']
        w = difference & -difference
        actual = (sum((w & v).bit_count() % 2 for v in vectors) + 2*((w & rec['shift']).bit_count() % 2)) % 4
        expected = sum((w & e).bit_count() % 2 for e in N.AXES[:17]) % 4
        need(w and actual != expected, 'actual old-translation failure witness')
        rejected[str(p)] = {'character': w, 'old_phase': actual, 'required_phase': expected}
    need(checks == 281008, 'all zero/single/pair character checks')
    return {'independent_character_comparisons': checks, 'old_translation_witnesses': rejected}


def replay(word, R, records, fault=None, consumer=True):
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
    checkpoint = False
    l2_rows = output_rows(R, records, False)
    for index, e in enumerate(word):
        op = e['op']
        counts[op] += 1
        if op == 'line':
            if fault == 'omit_Y_normalization' and e['field'] == field('Y', N.U[0]) and e['sign'] == 1:
                continue
            frames[e['field']] += ((records[e['port']]['q'], e['sign']),)
        elif op == 'stage':
            if fault == 'omit_old_output_conversion' and e['field'].startswith('Z'):
                continue
            if fault == 'omit_T_upgrade' and e['sign'] == 1:
                continue
            if fault == 'omit_T_restoration' and e['sign'] == -1:
                continue
            sign = -e['sign'] if fault == 'wrong_T_stage_sign' else e['sign']
            frames[e['field']] += tuple((axis, sign) for axis in E1)
        elif op == 'current_map':
            rec = records[e['port']]
            shift = rec['shift'] ^ rec['inverse_shift']
            if e['inverse']:
                shift = N.act(rec['g'], shift)
            if fault == 'old_alignment_translation':
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
            frames[e['field']] = {'current': N.START, 'common': N.START, 'identity': ()}[e['frame']]
        elif op == 'add':
            if fault == 'omit_consumer' and e.get('consumer'):
                continue
            dst, src = e['dst'], e['src']
            need(N.phase(frames[dst]) == N.phase(frames[src]), f'native ADD frame mismatch at {index}')
            if 'C' in (dst, src):
                need(in_private, 'private ADD outside whole-owner body')
            c = Q(e['coefficient'])
            if fault == 'wrong_correction_sign' and dst.startswith('Z') and src == 'C':
                c = -c
            rows[dst] = N.combine(rows[dst], rows[src], c)
        elif op == 'checkpoint':
            need(not in_private and e['name'] == 'x1_U_in_current_frame', 'named completed checkpoint')
            for at, expected in l2_rows.items():
                need(N.phase(frames[at]) == N.phase(N.START), 'L2 current output frame')
                need(rows[at] == expected, 'L2 checkpoint operator or owned dirt mismatch')
            checkpoint = True
        elif op == 'private_sweep_begin':
            need(not in_private, 'nested private sweep')
            in_private = True
        else:
            need(op == 'private_sweep_end' and in_private, 'unknown event or private boundary')
            need(not rows['C'] and not frames['C'], 'private owner body not clean')
            in_private = False
    need(checkpoint and not in_private and not rows['C'] and not frames['C'], 'final checkpoint and scratch cleanup')
    for at, frame in original.items():
        need(N.phase(frames[at]) == N.phase(frame), 'borrowed source frame not restored: '+at)
        need(rows[at] == {(at, N.AXES): Q(1)}, 'borrowed source content not restored: '+at)
    expected = output_rows(R, records, consumer)
    for p in N.U:
        need(N.phase(frames[field('Z', p)]) == N.phase(N.START if consumer else OLD), 'declared final output frame')
        need(rows[field('Z', p)] == expected[field('Z', p)], 'declared final output operator')
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
    maps = current_maps(records)
    direct = direct_current_frame_checks(records)
    word = program(R)
    trace, expected = replay(word, R, records)
    old_word = program(R, False)
    old_trace, old_expected = replay(old_word, R, records, consumer=False)
    need(old_trace == {'line': 192, 'clear': 112, 'add': 608, 'stage': 112, 'current_map': 208,
                       'private_sweep_begin': 1, 'private_sweep_end': 1, 'checkpoint': 1}, 'old-frame alternative invoice')
    need(trace == {'line': 192, 'clear': 112, 'add': 704, 'stage': 16, 'current_map': 208,
                   'private_sweep_begin': 1, 'private_sweep_end': 1, 'checkpoint': 1}, 'literal invoice')
    controls = {}
    for fault in ('omit_Y_normalization', 'omit_T_restoration', 'omit_T_upgrade',
                  'wrong_T_stage_sign', 'old_alignment_translation', 'omit_payload_translation',
                  'wrong_inverse_translation', 'omit_owned_output_clear', 'wrong_correction_sign', 'omit_consumer'):
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
    try:
        replay(old_word, R, records, fault='omit_old_output_conversion', consumer=False)
    except ValueError as error:
        controls['omit_old_output_conversion'] = str(error)
    else:
        raise ValueError('old-frame conversion control ineffective')
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
    need(dict(scalar_coefficients) == {'1': 320, '1/4': 384} and scalar == 7392, 'source scalar allowance')
    old_scalar = sum(environment['scalar_cost'](['clear']) if e['op'] == 'clear' else
                     environment['scalar_cost'](['add', None, None, Q(e['coefficient']).numerator, Q(e['coefficient']).denominator])
                     for e in old_word if e['op'] in ('clear', 'add'))
    need(old_scalar == 6624, 'same-contract old-frame scalar bill')
    invoice = {'rank_one_children': 192, 'rank_eight_children': 16, 'native_rank_mass': 320,
               'native_wrapper_maps': 416, 'full_cover_maps': 208, 'ADD_macros': 704,
               'CLEAR_macros': 112, 'scalar_real_primitive_allowance': scalar,
               'absolute_ADD_coefficients': dict(scalar_coefficients),
               'owned_output_arrays_reused_by_consumer': 96, 'owned_private_scratch_arrays_per_owner': 1,
               'borrowed_source_arrays_unchanged': 200, 'retained_F0_T_source_arrays': 8,
               'post_B1_X_sources_read_only': 96, 'literal_events': len(word),
               'included_consumer_unit_ADDs': 96, 'included_consumer_real_primitive_allowance': 768,
               'reconstruction_before_consumer_real_primitive_allowance': 6624}
    operator = {at: [[v, list(g), str(c)] for (v, g), c in sorted(row.items())] for at, row in expected.items()}
    return {'status': 'PASS_QQ16_CURRENT_FRAME_CONSUMER', 'source_sha256': pins, 'member_sha256': N.MEMBERS,
            'contract': 'Checkpoint Z=x1_U; consumer Z-=X2_U yields y1_U, both in F_U1; all sources restored.',
            'source_variables': 200, 'invoice': invoice, 'trace': trace, 'controls': controls,
            'independent_phase_checks': direct,
            'old_frame_alternative': {'output': 'x1_U in F_L', 'rank_one_children': 192,
                'rank_eight_children': 112, 'native_rank_mass': 1088, 'native_wrapper_maps': 608,
                'full_cover_maps': 208, 'scalar_real_primitive_allowance': old_scalar,
                'owned_output_arrays': 96, 'borrowed_source_arrays_restored': 200,
                'trace': old_trace, 'literal_events': len(old_word),
                'predecessor_same_contract_rank_mass': 1168, 'rank_mass_reduction': 80},
            'current_frame_maps': maps, 'old_alignment_translations_rejected_ports': len(maps), 'native_kernels': kernels,
            'operator_sha256': hashlib.sha256(json.dumps(operator, sort_keys=True).encode()).hexdigest(),
            'scope': 'Current-frame output with one paid consumer, plus an exactly priced old-frame alternative. Earlier retained-source delivery, full decoder, physical map cost, output retirement, precision and supplier saving remain open.'}, word, old_word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result, word, old_word = calculate()
    for name, value in (('RESULT.json', result), ('WORD.json', word), ('OLD-FRAME-WORD.json', old_word)):
        path = HERE/name
        if args.write:
            with path.open('x', encoding='utf-8', newline='\n') as handle:
                json.dump(value, handle, sort_keys=True, indent=2)
                handle.write('\n')
        else:
            need(json.loads(path.read_text(encoding='utf-8')) == value, 'committed '+name+' differs')
    print('PASS_QQ16_CURRENT_FRAME_CONSUMER sources=200 outputs=96 current_rank=320 old_rank=1088 controls=12 no_new_kappa')


if __name__ == '__main__':
    main()
