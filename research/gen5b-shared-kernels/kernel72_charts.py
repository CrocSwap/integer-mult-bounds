"""Exact changed-chart constructions for union72 and final12.

Every member receives its new first-frame quotient chart. All 72 pivot bank
residuals and 93 donor line entrances are bound to reusable exact programs.
"""
from collections import Counter
from fractions import Fraction as F

import chart_bounds as base
import source_data as sd
from kernel72_pricing import measured_kernel_delta


def gram(a, b):
    return 9 * sum(x * y for x, y in zip(a, b)) - sum(a) * sum(b)


def checked_chart(columns, residual_rank):
    assert len(columns) == 24 and all(len(c) == 24 for c in columns)
    assert 0 < residual_rank < 24
    assert all(gram(a, b) == 0 for a in columns[:residual_rank]
               for b in columns[residual_rank:])
    matrix = [list(row) for row in zip(*columns)]
    assert len(base.rref(matrix)[1]) == 24
    f = base.factor(matrix)  # Includes an exact inverse-program replay.
    assert f['determinant'] and f['count'] <= 576
    assert f['max_numerator'] < 2**80 and f['max_denominator'] < 2**80
    return dict(basis_columns=columns, residual_rank=residual_rank,
                completion_rank=24-residual_rank, **f)


def line_chart(i, j, residual_rank):
    assert type(i) is int and type(j) is int and 0 <= i < j < 24
    line = [int(k == i) - int(k == j) for k in range(24)]
    complement = [[int(k == r) for k in range(24)] for r in range(24) if r not in (i, j)]
    complement.append([int(k == i or k == j) for k in range(24)])
    assert gram(line, line) == 18
    if residual_rank == 1:
        columns = [line] + complement
    elif residual_rank == 23:
        columns = complement + [line]
    else:
        raise ValueError('A line chart has residual rank 1 or 23')
    return dict(line=[i, j], **checked_chart(columns, residual_rank))


def first_frame_chart(frame, line):
    """F/L from ker(A) intersect L-perp; completion is L direct-sum F-perp."""
    ann = frame['a'] if 'a' in frame else base.nullspace(frame['b'])
    d = frame['dim']; i, j = line
    assert len(base.rref(ann)[1]) == 24 - d
    v = [int(k == i) - int(k == j) for k in range(24)]
    assert all(sum(a * b for a, b in zip(row, v)) == 0 for row in ann)
    assert gram(v, v) == 18
    # Since sum(v)=0, the weighted condition <v,x>=0 is x_i=x_j.
    residual = base.nullspace(ann + [v])
    assert len(residual) == d - 1
    # (9I-J)^(-1) a is proportional to 15*a-sum(a).
    exterior = [base.primitive([15 * x - sum(row) for x in row]) for row in ann]
    assert len(exterior) == 24 - d
    assert all(sum(a * b for a, b in zip(row, col)) == 0
               for row in ann for col in residual + [v])
    assert all(gram(col, other) == 0 for col in residual + [v] for other in exterior)
    out = checked_chart(residual + [v] + exterior, d - 1)
    out.update(first_dimension=d, line=line)
    return out


def run(bridge=None, final12_charts=None, literal_stock=1229555):
    sd.verify_all()
    if bridge is None:
        import check_shared_kernel
        bridge = check_shared_kernel.run(selection='union72')
    measured_kernel_delta(bridge)
    if final12_charts is None:
        final12_charts = base.run()
    frames = sd.read_json('gen5bit/selected/bit/frames_p12.json.gz')['frames']
    programs = []; uses = []; index = {}
    def put(key, builder):
        if key not in index:
            index[key] = len(programs)
            programs.append(dict(program_id=len(programs), **builder()))
        return index[key]
    for p in sorted(bridge['paths'], key=lambda p: p['role']):
        line = tuple(p['line']); frame_id = p['old_frames'][0]
        first = frames[str(frame_id)]
        assert first['dim'] == p['first_dimension']
        program = put(('first_frame', frame_id, line),
                      lambda: dict(kind='first_frame_quotient', frame=frame_id,
                                   **first_frame_chart(first, list(line))))
        uses.append(dict(kind='first_frame_quotient', role=p['role'], stream=p['stream'],
                         frame=frame_id, rank=p['first_dimension']-1, program_id=program))
        rank = 23 if p['kind'] == 'pivot' else 1
        program = put(('line', line, rank),
                      lambda: dict(kind='pivot_residual' if rank == 23 else 'donor_line_entrance',
                                   **line_chart(*line, rank)))
        uses.append(dict(kind='pivot_residual' if rank == 23 else 'donor_line_entrance',
                         role=p['role'], stream=p['stream'], rank=rank, program_id=program))
    assert Counter(u['kind'] for u in uses) == {
        'first_frame_quotient': 165, 'pivot_residual': 72, 'donor_line_entrance': 93}
    assert final12_charts['charts'] == 18
    for program in final12_charts['factor_programs']:
        programs.append(dict(program, program_id=len(programs), scope='final12'))
    pins = sd.read_json('expected/kernel-pins.json')
    largest = max(p['count'] for p in programs)
    retained = pins['max_chart_factors']
    bound = max(largest, retained) + 119 + 120
    assert retained == 576 and bound == pins['normalizer_factor_bound'] == 815
    assert literal_stock == pins['literal_stock'] - 195
    selectors = 600 * ((literal_stock - 1) + pins['physical_R'] * 120 * bound)
    assert selectors < 2**40
    return dict(status='PASS_UNION72_FINAL12_CHANGED_CHARTS', source_head=sd.HEAD,
                selection='union72', with_final12=True, charts=len(programs),
                kernel_programs=len(programs)-18, final12_charts=18,
                first_frame_quotient_demands=165, donor_line_entrance_demands=93,
                pivot_residual_demands=72, role_chart_uses=uses,
                max_changed_chart_factors=largest,
                max_factor_numerator=max(p['max_numerator'] for p in programs),
                max_factor_denominator=max(p['max_denominator'] for p in programs),
                retained_chart_factor_bound=retained,
                combined_normalizer_factor_bound=bound, literal_stock=literal_stock,
                selector_calls_bound=selectors, factor_programs=programs,
                scope='Every changed union72 first-frame quotient, donor line entrance and rank23 pivot residual is bound to an exactly factored weighted chart; final12 charts are included. Unchanged chart admission and finite-compiler interfaces remain inherited.')
