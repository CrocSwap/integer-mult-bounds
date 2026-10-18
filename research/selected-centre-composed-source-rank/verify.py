#!/usr/bin/env python3
"""Selected time0/time1 scalar projection only; not native frame admission."""
import argparse
import gzip
import hashlib
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent

ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
PINS = {
    ARCHIVE: 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6',
    'certificates/selected-result.json': '10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32',
}
MEMBERS = {
    'global': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz', '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
    'program': ('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
    'word': ('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def add(row, source, q):
    for key, value in list(source.items()):
        new = row.get(key, Q(0)) + q * value
        if new:
            row[key] = new
        else:
            row.pop(key, None)


def rank(rows):
    pivots = {}
    for original in rows:
        row = dict(original)
        while row:
            col = min(row)
            if col not in pivots:
                q = row[col]
                pivots[col] = {k: v / q for k, v in row.items()}
                break
            add(row, pivots[col], -row[col])
    return len(pivots), sorted(pivots)


def replay(program, call, physical, source_roles, stop_at_cut=False):
    owners = [entry[0] for entry in call['owners']]
    require(len(owners) == len(set(owners)) == 704, 'noninjective local owner map')
    state = {('L', i): dict(physical[owner]) for i, owner in enumerate(owners)}
    sources = None
    bill = Counter()
    phase = None
    for event in program:
        tag = event[0]
        if tag == 'phase':
            phase = event[1]
            if phase == 'centers':
                sources = [dict(state['L', i]) for i in source_roles]
                if stop_at_cut:
                    return sources, bill
            continue
        if tag == 'scalar':
            op = event[1]
            name, dest = op[0], tuple(op[1])
            if phase == 'centers':
                bill[name] += 1
            if name == 'clear':
                state[dest] = {}
            elif name == 'copy':
                state[dest] = dict(state[tuple(op[2])])
            elif name == 'scale':
                q = Q(op[2], op[3])
                require(q != 0, 'singular scale')
                state[dest] = {k: q*v for k, v in state[dest].items()}
            elif name == 'add':
                add(state[dest], state[tuple(op[2])], Q(op[3], op[4]))
            else:
                raise ValueError('unknown scalar operation')
        elif tag == 'center':
            require(phase == 'centers' and event[4] == 8, 'unexpected centre')
            bill['rank8'] += 1
        else:
            # This is the declared projection, not an implementation of these maps.
            require(tag in ('climb', 'adapter', 'residual_adapter'), 'unknown event')
    require(sources is not None, 'missing source cut')
    require(all(not row for key, row in state.items() if key[0] == 'C'), 'dirty private exit')
    before = {i: dict(physical[owner]) for i, owner in enumerate(owners)}
    for i, owner in enumerate(owners):
        expected = dict(before[i])
        if 112 <= i < 224:
            add(expected, before[i-112], Q(1))
        require(state['L', i] == expected, f'full scalar endpoint mismatch on role {i}')
        physical[owner] = state['L', i]
    return sources, bill


def solve_minor(rows, columns, target):
    """Exact Gauss-Jordan solve; returned witness is checked by direct evaluation."""
    matrix = [[row.get(col, Q(0)) for col in columns] + [Q(value)]
              for row, value in zip(rows, target)]
    n = len(columns)
    for col in range(n):
        pivot = next((i for i in range(col, n) if matrix[i][col]), None)
        require(pivot is not None, 'singular source-data minor')
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        divisor = matrix[col][col]
        matrix[col] = [value / divisor for value in matrix[col]]
        for i in range(n):
            if i != col:
                q = matrix[i][col]
                matrix[i] = [x - q*y for x, y in zip(matrix[i], matrix[col])]
    return {column: matrix[i][-1] for i, column in enumerate(columns) if matrix[i][-1]}


def evaluate(row, values):
    return sum((q * values.get(col, Q(0)) for col, q in row.items()), Q(0))


def check_semantic_controls(program, call, owners, source_roles):
    start = program.index(['phase', 'centers'])
    end = program.index(['phase', 'B'])
    scatter = next(i for i in range(start, end)
                   if program[i][0] == 'scalar' and program[i][1][0] == 'add')
    final_clear = end - 1
    require(program[final_clear][1][0] == 'clear', 'final centre clear position')
    for label, omitted in [('omitted_scatter', scatter), ('omitted_final_clear', final_clear)]:
        state = {owner: {owner: Q(1)} for owner in owners}
        try:
            replay(program[:omitted] + program[omitted+1:], call, state, source_roles)
        except ValueError as error:
            expected = 'endpoint mismatch' if label == 'omitted_scatter' else 'dirty private exit'
            require(expected in str(error), 'control failed for an unrelated reason')
        else:
            raise ValueError(f'accepted {label}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=PACKAGE.parents[1])
    parser.add_argument('--write', action='store_true', help='regenerate the exact result receipt')
    args = parser.parse_args()
    for path, digest in PINS.items():
        require(hashlib.sha256((args.root/path).read_bytes()).hexdigest() == digest, path)
    data = {}
    with tarfile.open(args.root/ARCHIVE, 'r:gz') as archive:
        for key, (path, digest) in MEMBERS.items():
            raw = archive.extractfile(path).read()
            require(hashlib.sha256(raw).hexdigest() == digest, path)
            data[key] = json.loads(gzip.decompress(raw))
    calls = sorted(data['global']['calls'], key=lambda c: c['time'])[:2]
    require([(c['time'], c['stage'], c['replica'], c['orientation']) for c in calls]
            == [(0, 0, 0, 'forward'), (1, 0, 8, 'forward')], 'selected pair drift')
    program = data['program']['forward']
    digest = hashlib.sha256(json.dumps(program, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    require(all(c['local_program_sha256'] == digest for c in calls), 'program binding')
    source_roles = data['word']['centers']
    require(source_roles == [92, 57, 81, 224, 11, 240, 9, 256], 'source role drift')
    owner_sets = [{entry[0] for entry in c['owners']} for c in calls]
    sweeps = [e for e in data['global']['execution_schedule'] if e.get('kind') == 'local_cover_sweep']
    require(len(sweeps) >= 2, 'missing scheduled sweeps')
    for call, sweep in zip(calls, sweeps[:2]):
        require(all(call[key] == sweep[key] for key in ('time', 'replica', 'stage', 'provider_id')),
                'call order differs from scheduled sweeps')
    physical = {owner: {owner: Q(1)} for owner in set.union(*owner_sets)}
    source_a, bill_a = replay(program, calls[0], physical, source_roles)
    source_b, bill_b = replay(program, calls[1], physical, source_roles)
    # Independent initialization is a control, not the main experiment.
    independent = {owner: {owner: Q(1)} for owner in owner_sets[1]}
    source_b_independent, _ = replay(program, calls[1], independent, source_roles, True)
    rows = source_a + source_b
    joint_rank, pivots = rank(rows)
    data_owners = {entry[0] for c in calls for entry in c['owners'][:112]}
    require(len(data_owners) == 224, 'source-data owner count changed')
    clean_rows = [{k: v for k, v in row.items() if k in data_owners} for row in rows]
    clean_rank, clean_pivots = rank(clean_rows)
    scatter = []
    for offset in (0, 8):
        for target in sorted({edge[1] for edge in data['word']['cut']}):
            row = {}
            for edge in data['word']['cut']:
                if edge[1] == target:
                    index = offset + source_roles.index(edge[2])
                    add(row, rows[index], Q(edge[3], edge[4]))
            scatter.append(row)
    scatter_rank, _ = rank(scatter)
    require(joint_rank == scatter_rank == 16, 'joint source or output rank differs from16')
    require(rank(source_a + source_a)[0] == 8, 'equal-source control')
    require(rank(source_a + list(reversed(source_a)))[0] == 8, 'distinct-dependent control')
    require(rank([{k:v for k,v in row.items() if k in pivots} for row in rows])[0] == 16,
            'pivot-minor certificate')
    require(clean_rank == 16, 'source-data-only rank changed')
    desired = [1] + [0]*7 + [-1] + [0]*7
    witness = solve_minor(rows, clean_pivots, desired)
    values = [evaluate(row, witness) for row in rows]
    require(values == desired, 'direct source witness check failed')
    require(all(values[i] + values[i+8] == 0 for i in range(8)), 'pooled sums not zero')
    require(any(evaluate(row, witness) for row in scatter), 'pooled witness has no output error')
    check_semantic_controls(program, calls[0], owner_sets[0], source_roles)
    bill = dict(bill_a + bill_b)
    require(bill == {'clear':32, 'copy':16, 'rank8':16, 'add':352}, 'phase invoice')
    result = {
        'status': 'PASS_SELECTED_PAIR_SCALAR_SOURCE_RANK',
        'scope': 'Scalar common-frame projection only; adapters and frame moves are not native replayed.',
        'times': [0,1], 'replicas': [0,8],
        'physical_owner_union': len(physical), 'shared_owner_count': len(owner_sets[0] & owner_sets[1]),
        'source_support_sizes': [len(row) for row in rows],
        'source_rank': joint_rank, 'scatter_rank': scatter_rank,
        'rank_restricted_to_224_source_data_owners': clean_rank,
        'pivot_owner_ids': pivots, 'source_data_pivot_owner_ids': clean_pivots,
        'call1_source_changed_by_complete_call0': source_b != source_b_independent,
        'equal_map_rank':8, 'distinct_permuted_map_rank':8,
        'centre_phase_bill': bill, 'paid_rank_mass':128,
        'source_maps': [{str(k): str(v) for k,v in sorted(row.items())} for row in rows],
        'pooled_sum_kernel_witness': {str(k): str(v) for k, v in sorted(witness.items())},
        'pooled_sum_source_values': desired,
        'controls': ['equal_maps_rank8', 'distinct_permuted_maps_rank8',
                     'pooled_sum_loses_nonzero_output', 'omitted_scatter_rejected',
                     'omitted_final_clear_rejected'],
        'unproved': 'Lift scalar source-map rank to native 512-address charted frame maps at the two noncoincident cuts, with transport/hosting/precision and complete-call continuation.'
    }
    receipt = PACKAGE / 'RESULT.json'
    if args.write:
        receipt.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    else:
        require(result == json.loads(receipt.read_text(encoding='utf-8')), 'result receipt differs')
    print('PASS_SELECTED_PAIR_SCALAR_SOURCE_RANK source_rank=16 scatter_rank=16 '
          'data_rank=16 shared_owners=30 rank_mass=128 controls=5')


if __name__ == '__main__':
    main()
