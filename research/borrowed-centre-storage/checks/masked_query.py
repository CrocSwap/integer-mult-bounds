"""Check the input mask and the conditional F2 read with exact rows.

Do not import a producer or replay the complete native word.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1] / 'sources'
LANES = ROOT / 'work/centre-encoding-campaign-20261014/lanes'
SOURCE = LANES / 'paired-package-review/upstream-followthrough-20261015'
HERE = ROOT / 'work/centre-encoding-campaign-20261014/lanes/portable-source-codes/dirty-record-hosting-20261015/algebra/masked-query-review'
A = (0, 7, 20, 27, 36, 46, 57, 111)
TP = (21, 37, 47, 76, 81, 87, 92, 110)
V0 = A + TP
U = tuple(p for p in range(112) if p not in V0)
OFF_A = tuple(p for p in range(112) if p not in A)
H = (1, 6, 22, 28, 33, 49, 58, 109)
GREEDY = (1, 2, 3, 4, 5, 6, 8, 12)
PINS = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path, expected, compressed=False):
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    need(digest == expected, 'Source pin: ' + str(path))
    PINS[str(path.relative_to(ROOT))] = digest
    return gzip.decompress(raw) if compressed else raw


def add(a, b, c=Q(1)):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0) + c * value
        if not out[key]:
            del out[key]
    return out


def scale(row, c):
    return {key: c * value for key, value in row.items() if c * value}


def mm(a, b):
    result = []
    for row in a:
        out = {}
        for j, c in row.items():
            out = add(out, b[j], c)
        result.append(out)
    return result


def matadd(a, b, c=Q(1)):
    return [add(x, y, c) for x, y in zip(a, b)]


def ident(n):
    return [{i: Q(1)} for i in range(n)]


def parse(rows):
    return [{int(p): Q(v) for p, v in row.items()} for row in rows]


def serial(rows):
    return [{str(k): str(v) for k, v in sorted(row.items())} for row in rows]


def determinant(rows):
    rows = [list(row) for row in rows]
    result = Q(1)
    for j in range(len(rows)):
        k = next((k for k in range(j, len(rows)) if rows[k][j]), None)
        if k is None:
            return Q(0)
        if j != k:
            rows[j], rows[k] = rows[k], rows[j]
            result = -result
        pivot = rows[j][j]
        result *= pivot
        for k in range(j + 1, len(rows)):
            factor = rows[k][j] / pivot
            rows[k] = [a - factor * b for a, b in zip(rows[k], rows[j])]
    return result


def price(events):
    total = 0
    for event in events:
        if event[0] != 'scalar':
            continue
        gate = event[1]
        if gate[0] in ('clear', 'copy'):
            total += 2
            continue
        c = Q(*gate[-2:])
        a, b = abs(c.numerator), c.denominator
        need(a and b & (b - 1) == 0, 'Dyadic scalar')
        if gate[0] == 'scale':
            need(a & (a - 1) == 0, 'Power-of-two SCALE')
            total += 2 * (abs(a.bit_length() - b.bit_length()) + (c < 0))
        else:
            need(gate[0] == 'add', 'Known scalar gate')
            total += 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)
    return total


def scalar_replay(events, rows, required_frame=0):
    rows = {k: dict(v) for k, v in rows.items()}
    for kind, gate, frame in events:
        need(kind == 'scalar' and frame == required_frame, 'Scalar gate in the required frame')
        op, dst = gate[:2]
        dst = tuple(dst)
        if op == 'clear':
            need(dst[0] == 'C', 'Only owned scratch may be cleared')
            rows[dst] = {}
        elif op == 'scale':
            rows[dst] = scale(rows[dst], Q(*gate[-2:]))
        elif op == 'add':
            rows[dst] = add(rows[dst], rows[tuple(gate[2])], Q(*gate[-2:]))
        else:
            raise ValueError('Unexpected input gate')
    return rows


def basis(name):
    return {(name, ()): Q(1)}


def move(row, port):
    letter = (2, port)
    out = {}
    for (source, path), c in row.items():
        path = path[1:] if path and path[0] == letter else (letter,) + path
        key = source, path
        out[key] = out.get(key, 0) + c
    return {key: c for key, c in out.items() if c}


def query(bank, ports, matrix, routed):
    out = [{} for _ in range(8)]
    for p in ports:
        row = move(bank[p], p) if routed else bank[p]
        for k in range(8):
            out[k] = add(out[k], row, matrix[k].get(p, 0))
    return out


def scatter(rows, ports, matrix, routed):
    out = {}
    for p in ports:
        row = {}
        for k in range(8):
            row = add(row, rows[k], matrix[k].get(p, Q(0)) / 4)
        out[p] = move(row, p) if routed else row
    return out


def route_serial(rows):
    return [[p, [[name, [list(letter) for letter in path], str(c)]
                 for (name, path), c in sorted(row.items())]]
            for p, row in sorted(rows.items())]


def route_summary(rows):
    terms = [item for row in rows.values() for item in row.items()]
    return dict(rows=len(rows), terms=len(terms),
                distinct_source_columns=len({key[0] for key, _ in terms}),
                maximum_route_word_length=max((len(key[1]) for key, _ in terms), default=0),
                row_sha256=sha256(json.dumps(route_serial(rows), separators=(',', ':')).encode()).hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, 'At least three GiB free')
    current_dir = SOURCE / 'current-query-encoder'
    unit_raw = read(current_dir / 'UNIT-QUERY-PROGRAM.json.gz',
        '75e3e04f79d319f0024d9139d1dceaeeb2fb8e741f6e31a6079000c219c4eaa2', True)
    need(sha256(unit_raw).hexdigest() == '9cb744034b11ef515a9c429264199a03f02fd9c4cb408e6455021ce9c0802a9c', 'Unit payload')
    unit = json.loads(unit_raw)
    current_raw = read(current_dir / 'CURRENT-QUERY-PROGRAM.json.gz',
        'b4d5cba37c696d1c31f530b3aa4f01535718972227f8b63d626125f35046d09e', True)
    need(sha256(current_raw).hexdigest() == '75d7f083af8d5687b971aa0c012e201b922f5473a4080869b581b9ba8c195fea', 'Current payload')
    current = json.loads(current_raw)
    read(current_dir / 'UNIT-QUERY.md', '6f53e12ba5144c8eb9df5de7eb3e19e7e0c7c1e1119db3e8116a2e643662f3a7')
    read(SOURCE / 'full-exit-readers-review/check_review.py',
         'e59b1fe12a62e8de01eae9dd25b415524f8e43c56806f1e05a8d1d7d00b70168')
    read(HERE.parent / 'DIRTY-ECHO.md', 'a707837cd29f8cd157a35f666e27c354063a9b5e2c2e1f673f4121a3c3dc2dd2')
    inherited_review = json.loads(read(LANES / 'coherent-port/current-query-review-20261015/UNIT-REVIEW.json',
        '58620b41e6b6aef4250bea4c4b4e66ab4c8fd03cd8bdd1f438a61377f297e756'))
    need(inherited_review['status'] == 'PASS_UNIT_QUERY_REVIEW' and
         inherited_review['payload_sha256'] == sha256(unit_raw).hexdigest(), 'Exact inherited unit review')
    certificate = json.loads(read(SOURCE / 'base/research/joint-query/certificate.json.gz',
        'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7', True))
    R = parse(certificate['R_rows'])
    need(R == parse(current['R']), 'Actual R from both pinned sources')
    need(tuple(unit['selected_A']) == A and set(unit['other_Y']) == set(OFF_A), 'Literal selected set')
    I, I8 = ident(112), ident(8)
    K = [{k: R[k][p] / 4 for k in range(8) if p in R[k]} for p in range(112)]
    PA = [row if p in A else {} for p, row in enumerate(K)]
    KO = [row if p in OFF_A else {} for p, row in enumerate(K)]
    LA = [{p: c for p, c in row.items() if p in A} for row in R]
    RO = [{p: c for p, c in row.items() if p in OFF_A} for row in R]
    LV = [{p: c for p, c in row.items() if p in V0} for row in R]
    RU = [{p: c for p, c in row.items() if p in U} for row in R]
    need(mm(LA, PA) == I8 and mm(R, K) == [scale(row, 14) for row in I8], 'Actual A minor and RK')
    plus, minus = matadd(I, mm(PA, RO)), matadd(I, mm(KO, LA), -1)
    T = mm(minus, plus)
    Ti = mm(matadd(I, mm(PA, RO), -1), matadd(I, mm(KO, LA)))
    J = matadd(I, mm(K, R), -1)
    correction = matadd(T, J, -1)
    need(T == parse(unit['T']) and Ti == parse(unit['inverse_T']), 'Independent unit matrices')
    need(correction == parse(unit['S']), 'Independent source correction')
    need(mm(T, Ti) == mm(Ti, T) == I and mm(LA, T) == R, 'Unit inverse and query')
    need({p for p, row in enumerate(correction) if row} == set(A), 'Correction supported only on A')
    need(sum(map(len, correction)) == 424 and all(abs(c) == 1 for row in correction for c in row.values()), '424 unit source ADDs')
    need(set(H) <= set(U) and set(GREEDY) <= set(U), 'Both candidate minors avoid the mask')
    minor = [[R[k].get(p, Q(0)) for p in H] for k in range(8)]
    gram = [[sum(minor[i][p] * minor[j][p] for p in range(8)) for j in range(8)] for i in range(8)]
    need(gram == [[Q(4 * (i == j)) for j in range(8)] for i in range(8)], 'Orthogonal U minor')
    det_h = determinant(minor)
    det_g = determinant([[R[k].get(p, Q(0)) for p in GREEDY] for k in range(8)])
    need(det_h == -256 and det_g == -32, 'Actual minor determinants')
    PU = [row if p in H else {} for p, row in enumerate(K)]
    need(mm(RU, PU) == mm(R, PU) == I8, 'U section from transpose divided by four')
    need(not any(mm(LV, PU)), 'Disjoint source and destination support')
    N = mm(PU, LV)
    B, Bi = matadd(I, N, -1), matadd(I, N)
    need(not any(mm(N, N)), 'Mask square is zero')
    need(mm(B, Bi) == mm(Bi, B) == I and mm(R, B) == RU, 'Mask inverse and query')
    TB, TBi = mm(T, B), mm(Bi, Ti)
    need(mm(TB, TBi) == mm(TBi, TB) == I and mm(LA, TB) == RU, 'Ordered target precode')
    source_correction = mm(PA, matadd(RU, mm(LA, J), -1))
    source_code = matadd(J, source_correction)
    need(mm(LA, source_code) == RU, 'Independent source-query completion')
    need(source_code == matadd(T, mm(PA, LV), -1), 'Masked source code H_D')
    need({p for p, row in enumerate(source_correction) if row} == set(A), 'Source correction stays on A')
    source_census = Counter(str(abs(c)) for row in source_correction for c in row.values())
    need(source_census == Counter({'1': 384, '1/2': 32}), '384 unit and 32 half source ADDs')
    need(all(c.denominator & (c.denominator - 1) == 0 for rows in (B, Bi, TB, TBi) for row in rows for c in row.values()), 'All new matrices are dyadic')
    mask = [['scalar', ['add', ['L', 112 + p], ['L', 112 + q], -c.numerator, c.denominator], 0]
            for p, row in enumerate(N) for q, c in sorted(row.items())]
    need(len(mask) == 64 and Counter(str(-c) for row in N for c in row.values()) == Counter({'-1/2': 40, '1/2': 24}), '64 half ADDs')
    need(all(e[1][1][1] - 112 in H and e[1][2][1] - 112 in V0 for e in mask), 'Read-only mask sources and disjoint targets')
    start = {('L', 112 + p): {p: Q(1)} for p in range(112)}
    start[('C', 0)] = {112: Q(1)}
    masked = scalar_replay(mask, start)
    need([masked[('L', 112 + p)] for p in range(112)] == B and masked[('C', 0)] == start[('C', 0)], 'Literal mask and arbitrary scratch')
    prefix = scalar_replay(mask + unit['prefix'], start)
    need([prefix[('L', 112 + p)] for p in range(112)] == TB and not prefix[('C', 0)], 'Literal prefix order and owned scratch clear')
    need(unit['retained_core'] == current['retained_core'] and unit['native_normalizations'] == current['native_normalizations'], 'Unchanged core and eight positive lines')
    need(len(unit['native_normalizations']) == 8 and all(e[0] == 'intrinsic_line' and e[3] == 1 for e in unit['native_normalizations']), 'Eight positive selected lines')
    need(unit['program'] == unit['prefix'] + unit['retained_core'] + unit['native_normalizations'] + unit['suffix'], 'Exact unit block order')
    suffix = [['scalar', ['add', ['L', 112 + p], ['L', q], c.numerator, c.denominator], 1]
              for p, row in enumerate(source_correction) for q, c in sorted(row.items())]
    program = mask + unit['prefix'] + unit['retained_core'] + unit['native_normalizations'] + suffix
    after_core = {('L', p): {p: Q(1)} for p in range(112)}
    after_core.update({('L', 112 + p): add(J[p], {112 + q: c for q, c in TB[p].items()}) for p in range(112)})
    after_suffix = scalar_replay(suffix, after_core, 1)
    expected_data = [add(source_code[p], {112 + q: c for q, c in TB[p].items()}) for p in range(112)]
    need([after_suffix[('L', 112 + p)] for p in range(112)] == expected_data, 'Literal suffix on all 224 data columns')
    recovered_y = mm(TBi, [add(row, source_code[p], -1) for p, row in enumerate(expected_data)])
    need(recovered_y == [{112 + p: Q(1)} for p in range(112)], 'Full joint data inverse')
    pure_target_correction = mm(PA, [scale(row, -1) for row in mm(LA, J)])
    need(not any(mm(LA, matadd(J, pure_target_correction))), 'D equals zero consequence')
    pure_target_suffix = [['scalar', ['add', ['L', 112 + p], ['L', q], c.numerator, c.denominator], 1]
                          for p, row in enumerate(pure_target_correction) for q, c in sorted(row.items())]
    costs = dict(mask_scalar=price(mask), retained_unit_scalar=price(unit['program']),
                 selected_source_correction=price(suffix), complete_scalar=price(program),
                 events=len(program), new_native_children=0,
                 new_native_wrappers=0, new_cover_maps=0, new_private_fields=0,
                 pure_target_consequence_scalar=price(program) - price(suffix) + price(pure_target_suffix))
    need(costs['mask_scalar'] == 640 and costs['retained_unit_scalar'] == 212826 and
         costs['selected_source_correction'] == 3392 and costs['complete_scalar'] == 213466 and
         costs['events'] == 26587 and costs['pure_target_consequence_scalar'] == 214234, 'Local scalar invoice')
    masked_dir = HERE.parent.parent / 'masked-query'
    read(masked_dir / 'emit_masked_query.py', '809509a2c41c947a4ea64fcb579b739b24fe6020e59eaa1dae3d8f38e63cfaed')
    read(masked_dir / 'MASKED-QUERY.md', 'af7d8c132528da939a01bdbfa49a643697e4ef6c388642de6c8ca9f1fdc6fdd3')
    actual_raw = read(masked_dir / 'masked-sum/MASKED-QUERY-PROGRAM.json.gz',
        'a4fc54c4af9d3f65e60b025ee26a144d133ae935774d73bbb48d5c7d39ef8581', True)
    need(sha256(actual_raw).hexdigest() == '42a9d4bab68fe25f5592a4105b0b7cefa289187165f1d3dd0db6540afca98263', 'Final masked-sum payload')
    actual = json.loads(actual_raw)
    producer_receipt = json.loads(read(masked_dir / 'masked-sum/MASKED-QUERY.json',
        'b6ad9e6705aefb35e2f7ed621334151710b2a31765f4c51f76f26641394d2d0a'))
    need(actual['source_payload_sha256'] == sha256(unit_raw).hexdigest() and
         tuple(actual['selected_A']) == A and tuple(actual['masked_ports']) == V0 and
         tuple(actual['kept_ports']) == U and tuple(actual['section_ports']) == H, 'Final packet source and port bindings')
    for key, expected_matrix in (('R', R), ('section', PU), ('B', B), ('inverse_B', Bi), ('T', T),
                                 ('source_response', source_code), ('source_query', RU),
                                 ('target_code', TB), ('inverse_target_code', TBi)):
        need(parse(actual[key]) == expected_matrix, 'Final literal matrix: ' + key)
    for key, expected_events in (('mask_prefix', mask), ('retained_unit_prefix', unit['prefix']),
                                 ('retained_core', unit['retained_core']),
                                 ('native_normalizations', unit['native_normalizations']),
                                 ('suffix', suffix), ('program', program)):
        need(actual[key] == expected_events, 'Final literal event order: ' + key)
    for key in ('physical_input', 'physical_output', 'output_frames'):
        need(actual[key] == unit[key], 'Retained native interface: ' + key)
    need(producer_receipt['payload_sha256'] == sha256(actual_raw).hexdigest() and
         producer_receipt['program_events'] == len(program) and
         producer_receipt['costs']['complete_scalar'] == price(program), 'Final receipt bindings and costs')

    x = {p: basis('x:' + str(p)) for p in range(112)}
    y = {p: basis('y:' + str(p)) for p in range(112)}
    c = {p: basis('c:' + str(p)) for p in range(112)}
    beta = {p: basis('beta:' + str(p)) for p in V0}
    h = {p: basis('h:' + str(p)) for p in A}
    eh_t = scatter(query(h, A, R, False), TP, R, False)
    dx, dy = dict(x), dict(y)
    for p in A:
        dx[p], dy[p] = add(x[p], h[p], -1), add(y[p], h[p])
    for p in TP:
        dx[p], dy[p] = add(x[p], eh_t[p]), add(y[p], eh_t[p], -1)
    ell = {p: c[p] if p in V0 else add(x[p], c[p]) for p in range(112)}
    v = {p: beta[p] if p in V0 else y[p] for p in range(112)}
    q = matadd(query(ell, U, R, True), query(v, U, R, True))
    f = matadd(query({p: add(ell[p], c[p], -1) for p in U}, U, R, False),
               query(dx, V0, R, False))
    need(f == query(x, range(112), R, False), 'Old F0 query from current read sources')
    selected_sum = {p: add(dx[p], dy[p]) for p in TP}
    projected_f = scatter(f, OFF_A, R, False)
    answer = matadd(q, query(c, U, R, True), -1)
    answer = matadd(answer, query(selected_sum, TP, R, True))
    answer = matadd(answer, query(projected_f, OFF_A, R, True), -1)
    decoded = scatter(answer, A, R, True)
    need(all(isinstance(c, Q) for row in decoded.values() for c in row.values()), 'Exact rational routed coefficients')
    original_f = query(x, range(112), R, False)
    original_projection = scatter(original_f, OFF_A, R, False)
    virtual_y1 = {p: add(add(x[p], y[p]), original_projection[p], -1) for p in OFF_A}
    expected = scatter(query(virtual_y1, OFF_A, R, True), A, R, True)
    need(decoded == expected, 'Ordered F2 read equals the exact donor erase query')
    frozen_rows = json.loads(read(HERE.parent / 'FUTURE-READ-ROWS.json',
        'bce692e721ee7e0db485509cc12a3384a2e24ec2014626954aab5d4dde0059d5'))
    need(route_serial(decoded) == frozen_rows, 'Exact match to the frozen dirty erase rows')
    need(all(name.startswith(('x:', 'y:')) for row in decoded.values() for name, _ in row), 'All beta, c, and donor columns cancel')
    donors = {p: add(h[p], expected[p]) for p in A}
    restored_h = {p: add(donors[p], decoded[p], -1) for p in A}
    need(restored_h == h, 'All arbitrary donor baselines restored')
    final_x, final_y = dict(dx), dict(dy)
    final_t = scatter(query(restored_h, A, R, False), TP, R, False)
    for p in A:
        final_x[p], final_y[p] = add(dx[p], restored_h[p]), add(dy[p], restored_h[p], -1)
    for p in TP:
        final_x[p], final_y[p] = add(dx[p], final_t[p], -1), add(dy[p], final_t[p])
    need(final_x == x and final_y == y, 'All logical data restored after E correction')
    witness_y = {p: basis('witness') if p == 1 else {} for p in U}
    witness_query = query(witness_y, U, R, True)
    witness_beta = {p: scale(row, -1) for p, row in scatter(witness_query, A, R, True).items()}
    need(not any(matadd(witness_query, query(witness_beta, A, R, True))), 'Unmasked-query collision')
    need(any(scatter(witness_query, A, R, True).values()), 'Collision changes the required erase query')
    controls = dict(
        reversed_target_precode=mm(LA, mm(B, T)) != RU,
        wrong_mask_sign=mm(R, Bi) != RU,
        omitted_mask=matadd(q, query(v, V0, R, True)) != q,
        omitted_source_correction=mm(LA, J) != RU,
        omitted_old_query_subtraction=scatter(matadd(answer, query(projected_f, OFF_A, R, True)), A, R, True) != expected,
        omitted_other_pair_U=scatter(matadd(answer, query(c, U, R, True)), A, R, True) != expected,
        old_unmasked_source_correction=scatter(matadd(answer, query(ell, V0, R, True)), A, R, True) != expected,
        omitted_selected_Y=scatter(matadd(answer, query({p: dy[p] for p in TP}, TP, R, True), -1), A, R, True) != expected)
    need(all(controls.values()), 'All negative controls reject the changed word')
    receipt = dict(status='PASS_MASKED_QUERY_ALGEBRA_AND_CONDITIONAL_F2_READ',
        source_pins=PINS, selected_A=list(A), selected_T=list(TP), mask_ports=list(V0),
        section_ports=list(H), orthogonal_minor_determinant=str(det_h),
        greedy_minor=list(GREEDY), greedy_minor_determinant=str(det_g),
        mask_coefficient_census={'-1/2': 40, '1/2': 24},
        source_correction_absolute_coefficient_census=dict(source_census),
        selected_query='R_U(x+y)',
        final_masked_sum_payload_sha256=sha256(actual_raw).hexdigest(),
        final_literal_word_compared=True,
        unmasked_query_collision={'changed_original_Y_port': 1, 'compensation_ports': list(A),
                                  'all_named_FULL_observations_unchanged': True, 'erase_query_changed': True},
        input_prefix_sha256=sha256(json.dumps(mask, separators=(',', ':')).encode()).hexdigest(),
        target_precode_sha256=sha256(json.dumps(serial(TB), separators=(',', ':')).encode()).hexdigest(),
        target_inverse_sha256=sha256(json.dumps(serial(TBi), separators=(',', ':')).encode()).hexdigest(),
        source_code_sha256=sha256(json.dumps(serial(source_code), separators=(',', ':')).encode()).hexdigest(),
        new_prefix_and_suffix_all_224_data_columns=True,
        costs=costs, controls=controls, conditional_F2_independent_columns=360,
        conditional_F2_erase=route_summary(decoded),
        full_712_event_replay=False, native_kernel_replay=False, global_482_schedule_replay=False,
        later_B3_admission=False, mixed_target_code_retirement=False,
        inherited_contract='The accepted UNIT-QUERY core gives X=x and Y=T(x+y), with the stated mixed native frames and complete arbitrary-helper endpoint map.',
        conditional_entry='After selected-port swaps, l_V0=c_V0, l_U=x_U+c_U, v_U=y_U, and v_V0 is arbitrary; the stated current read fields have common F_U2.',
        limits=['The algebraic inverse does not admit cross-frame scalar gates.',
                'The old full-W all-output dirt receipt does not transfer to this selected-port substitution.',
                'No new global output map, recursive hosting, precision bound, supplier, or kappa claim.'])
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'])
    print(json.dumps(dict(costs=costs, conditional_F2_erase=receipt['conditional_F2_erase']), sort_keys=True))


if __name__ == '__main__':
    main()
