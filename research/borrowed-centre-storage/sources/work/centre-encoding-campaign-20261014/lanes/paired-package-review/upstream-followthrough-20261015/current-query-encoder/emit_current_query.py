#!/usr/bin/env python3
"""Emit a current sum query in eight completed target fields."""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('scalar_review', HERE.parent / 'full-exit-readers-review/check_review.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
A = (0, 7, 20, 27, 36, 46, 57, 111)
PINS = {
    'scalar_interpreter': 'e59b1fe12a62e8de01eae9dd25b415524f8e43c56806f1e05a8d1d7d00b70168',
    'interface': '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3',
    'clean_core_payload': 'fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877',
    'word_compressed': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'positive_lines': '500c09dfc1d27ffd107341adf4c3c6874ee2c84e1a8afad91d931ed9e88fd1d7',
    'physical_endpoint_review': '8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d',
}


def multiply(a, b):
    result = []
    for row in a:
        out = {}
        for j, coefficient in row.items():
            m.add(out, b[j], coefficient)
        result.append(out)
    return result


def serial(rows):
    return [{str(k): str(v) for k, v in sorted(row.items())} for row in rows]


def mv(rows, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(rows))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    lanes = args.repo / m.LANES
    m.read_pin(HERE.parent / 'full-exit-readers-review/check_review.py', PINS['scalar_interpreter'])
    interface = json.loads(m.read_pin(lanes / 'circuit-interface/INTERFACE.json', PINS['interface']))
    raw = gzip.decompress((lanes / 'circuit-interface/CENTRE-FREE-PROGRAMS.json.gz').read_bytes())
    m.need(sha256(raw).hexdigest() == PINS['clean_core_payload'], 'Clean core payload')
    core = json.loads(raw)['forward']
    word = json.loads(gzip.decompress(m.read_pin(args.repo / 'work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz', PINS['word_compressed'])))
    lines = json.loads(m.read_pin(lanes / 'coherent-port/INPUT-COMPENSATION.json', PINS['positive_lines']))
    m.read_pin(lanes / 'interface-proof/ORIGINAL-COMPLEX-MODES-REVIEW.json', PINS['physical_endpoint_review'])
    R = [{int(p): Q(v) for p, v in row.items()} for row in interface['R']]
    I = [{p: Q(1)} for p in range(112)]
    K = [{k: R[k].get(p, 0) / 4 for k in range(8) if R[k].get(p, 0)} for p in range(112)]
    KA = [row if p in A else {} for p, row in enumerate(K)]
    U = tuple(p for p in range(112) if p not in A)
    RU = [{p: v for p, v in row.items() if p not in A} for row in R]
    LA = [{p: v for p, v in row.items() if p in A} for row in R]
    m.need(multiply(R, K) == [{k: Q(14)} for k in range(8)], 'RK=14I')
    m.need(multiply(LA, KA) == [{k: Q(1)} for k in range(8)], 'Selected dual')
    m.need(multiply(RU, KA) == [{} for _ in range(8)], 'Selected shear square zero')
    P, Pinv, J, Jinv = [[dict(r) for r in I] for _ in range(4)]
    for p, row in enumerate(multiply(KA, RU)):
        m.add(P[p], row)
        m.add(Pinv[p], row, -1)
    for p, row in enumerate(multiply(K, R)):
        m.add(J[p], row, -1)
        m.add(Jinv[p], row, -Q(1, 13))
    target = multiply(P, J)
    inv = multiply(Jinv, Pinv)
    m.need(multiply(target, inv) == multiply(inv, target) == I, 'Both rational inverse orders')
    m.need(multiply(LA, target) == [{p: -13 * v for p, v in row.items()} for row in R], 'Clean full query')
    S = [dict(row) for row in target]
    for p in range(112):
        m.add(S[p], J[p], -1)
    m.need({p for p, row in enumerate(S) if row} == set(A), 'Only selected correction rows')
    m.need(Counter(v for row in S for v in row.values()) == Counter({Q(-13): 8, Q(-6): 264, Q(6): 152}), 'Exact correction coefficients')

    def scalar(gate, frame):
        return ['scalar', gate, frame]

    prefix = []
    for query, scatter, sign in ((R, K, -1), (RU, KA, 1)):
        for k, row in enumerate(query):
            prefix.append(scalar(['clear', ['C', 0]], 0))
            prefix.extend(scalar(['add', ['C', 0], ['L', 112 + p], v.numerator, v.denominator], 0)
                          for p, v in sorted(row.items()))
            prefix.append(scalar(['scale', ['C', 0], 1, 4], 0))
            prefix.extend(scalar(['add', ['L', 112 + p], ['C', 0], int(sign * 4 * col[k]), 1], 0)
                          for p, col in enumerate(scatter) if k in col)
            prefix.append(scalar(['clear', ['C', 0]], 0))
    pre_map = m.replay(prefix)
    m.need(pre_map[112:224] == [{112 + p: v for p, v in row.items()} for row in target], 'Ordered prefix PJ')

    selected_recipes = [item for item in lines['recipes'] if item['port'] in A]
    m.need(tuple(item['port'] for item in selected_recipes) == A, 'Selected native recipe order')
    native = []
    for item in selected_recipes:
        p, label, recipe = item['port'], item['label'], item['recipe']
        m.need(label == word['ports'][p], 'Actual selected native line')
        m.need(recipe['rank'] == 1, 'One rank-one child')
        for side in ('left', 'right'):
            block = recipe[side]
            m.need(block['offset'] == block['phase'] == 0 and not any(block['linear_Z4'] + block['quadratic_rows']), 'Exact zero wrapper phases')
        for x in range(512):
            middle = mv(recipe['right']['matrix_rows'], x)
            m.need(mv(recipe['left']['matrix_rows'], middle) == x, 'Kernel first Gaussian coefficient')
            m.need(mv(recipe['left']['matrix_rows'], middle ^ 1) == x ^ label, 'Kernel second Gaussian coefficient')
        native.append(['intrinsic_line', ['L', 112 + p], p, 1, recipe])

    post = [scalar(['clear', ['C', 0]], 1)]
    for q in U:
        entries = [(p, S[p].get(q, Q(0))) for p in A if S[p].get(q, 0)]
        m.need(len(entries) == 4 and all(abs(v) == 6 for p, v in entries), 'Four signed-six updates')
        post += [scalar(['copy', ['C', 0], ['L', q]], 1),
                 scalar(['scale', ['C', 0], 2, 1], 1),
                 scalar(['add', ['C', 0], ['L', q], 1, 1], 1),
                 scalar(['scale', ['C', 0], 2, 1], 1)]
        post.extend(scalar(['add', ['L', 112 + p], ['C', 0], int(v / 6), 1], 1) for p, v in entries)
    post.extend(scalar(['add', ['L', 112 + p], ['L', p], -13, 1], 1) for p in A)
    post.append(scalar(['clear', ['C', 0]], 0))
    program = prefix + core + native + post
    output = m.replay(program)
    expected = [{p: Q(1)} for p in range(712)]
    for p, row in enumerate(target):
        expected[112 + p] = dict(row)
        m.add(expected[112 + p], {112 + q: v for q, v in row.items()})
    expected[704:] = [{} for _ in range(8)]
    m.need(output == expected, 'All 712 arbitrary input columns')
    frames, frame_count = m.frame_check(prefix + core, word)
    m.need(frames == word['final'] + [0] * 8, 'Complete retained native endpoints')
    phase_checks = 0
    for p in A:
        q = word['ports'][p]
        for frequency in range(512):
            full = frequency.bit_count() % 4
            line = (frequency & q).bit_count() % 2
            m.need((full - line + line) % 4 == full, 'Positive line reaches exact FULL phase')
            phase_checks += 1
        frames[112 + p] = 1
    for event in post:
        op, target_wire, source, _ = m.scalar(event)
        if op == 'clear':
            frames[target_wire] = event[2]
        else:
            m.need(frames[target_wire] == event[2], 'Post target FULL access')
            if source is not None:
                m.need(frames[source] == event[2], 'Post source FULL access')
    m.need(frames[704:] == [0] * 8, 'All owned fields return zero/I')
    m.need(all(frames[p] == 1 for p in range(112)), 'All X remain FULL')
    m.need(all(frames[112 + p] == (1 if p in A else word['final'][112 + p]) for p in range(112)), 'Exact mixed Y frames')
    m.need([e for e in program if e[0] in ('climb', 'adapter', 'residual_adapter')] ==
           [e for e in core if e[0] in ('climb', 'adapter', 'residual_adapter')], 'All old native events unchanged')

    j_end = next(i for i in range(1, len(prefix)) if sum(e[1][0] == 'clear' for e in prefix[:i] if e[0] == 'scalar') == 16)
    # Each of the two serial blocks has eight query iterations.
    j_events = sum(3 + len(R[k]) + sum(k in col for col in K) for k in range(8))
    m.need(j_events == j_end, 'Exact split between J and P')
    price = lambda events: sum(m.cost(e) for e in events if e[0] == 'scalar')
    costs = dict(J_prefix=price(prefix[:j_events]), P_prefix=price(prefix[j_events:]),
                 retained_core=price(core), selected_FULL_correction=price(post),
                 complete_scalar=price(program), added_rank_one_children=8,
                 added_native_wrappers=16, native_mass=5530)
    m.need(costs == dict(J_prefix=7232, P_prefix=3648, retained_core=202138,
                        selected_FULL_correction=4932, complete_scalar=217950,
                        added_rank_one_children=8, added_native_wrappers=16, native_mass=5530), 'Complete exact local invoice')
    wrong_p = m.replay(prefix[:j_events] + core + native + post)
    wrong_s = m.replay(prefix + core + native)
    no_clear = m.replay(prefix[1:] + core + native + post)
    bad_line_phases = [(x.bit_count() - 2 * ((x & word['ports'][A[0]]).bit_count() % 2)) % 4 for x in range(512)]
    controls = dict(omitted_P=wrong_p != expected, omitted_FULL_correction=wrong_s != expected,
                    arbitrary_private_baseline=any(704 in row for row in no_clear[:704]),
                    wrong_inverse_line_has_translation=bad_line_phases != [x.bit_count() % 4 for x in range(512)],
                    uniform_hole_endpoint_is_false=any(frames[112 + p] != word['final'][112 + p] for p in A))
    m.need(all(controls.values()), 'Every negative control detects its fault')

    payload = dict(schema='current-query-encoder-v1', selected_A=list(A), other_Y=list(U), source_pins=PINS,
                   R=serial(R), J=serial(J), P=serial(P), PJ=serial(target), inverse_PJ=serial(inv),
                   S=serial(S), prefix=prefix, retained_core=core, native_normalizations=native, suffix=post,
                   program=program, output_frames=frames,
                   physical_input='X:C_q, Y:I, helpers:original; C:owned arbitrary',
                   physical_output='X:F, Y_A:F, Y_not_A:F C_q^-1, helpers:original complete jobs; C:zero/I')
    raw = m.encode(payload)
    receipt = dict(status='PASS_CURRENT_SUM_QUERY_ENCODER_712_COLUMNS', source_pins=PINS,
                   payload_sha256=sha256(raw).hexdigest(), selected_A=list(A), all_input_columns=712,
                   arbitrary_helper_rows=480, owned_private_rows_cleared=8,
                   new_native_kernel_columns=8 * 512, exact_output_phase_cases=phase_checks,
                   retained_scalar_frame_checks=frame_count, costs=costs, controls=controls,
                   target_code='P J (X+Y)', selected_query='L_A Y_out = -13 R (X+Y)',
                   open=['Whole changed controller and mixed-frame bridges', 'Old-stage query capture',
                         'Code retirement and arbitrary global owner restoration', 'New-child hosting',
                         'Full recursive streams, maps, precision and kappa invoice'])
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'CURRENT-QUERY-PROGRAM.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    (args.out / 'CURRENT-QUERY.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(receipt['status'])
    print(json.dumps(costs, sort_keys=True))


if __name__ == '__main__':
    main()
