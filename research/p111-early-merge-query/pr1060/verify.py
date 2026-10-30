#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the complete decoder word, frames, phases and cost."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import N, FULL, ZERO, basis, build, contained, distance, parity, perp, require, serializable


def load_clifford():
    path = HERE / 'vendor' / 'clifford_exact.py'
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    require(hashlib.sha256(path.read_bytes()).hexdigest() == pins['clifford']['sha256'], 'Clifford source pin')
    module = types.ModuleType('shared_decoder_clifford')
    sys.modules[module.__name__] = module
    # The retained compiler uses assertions. Keep them under an optimized parent.
    exec(compile(path.read_text(), str(path), 'exec', optimize=0), module.__dict__)
    return module


def axpy(rows, target, source, q):
    result = dict(rows[target])
    for column, value in rows[source].items():
        new = result.get(column, Q(0)) + q * value
        if new:
            result[column] = new
        else:
            result.pop(column, None)
    rows[target] = result


def expected_rows(word, transpose=False):
    n, v = word['n'], word['v']
    rows = [{i: Q(1)} for i in range(n)]
    gram = word['decoder']['expected']
    for t in range(v):
        for i in range(v):
            if gram[t][i]:
                if transpose:
                    rows[i][v + t] = -gram[t][i]
                else:
                    rows[v + t][i] = gram[t][i]
    return rows


def symbolic_replay(word):
    """Replay all original input columns, including each independent dirty helper."""
    rows = [{i: Q(1)} for i in range(word['n'])]
    peak = Q(1)
    active = None
    flattened = []
    for event in word['events']:
        op = event['op']
        if op == 'add':
            target, source, q = event['target'], event['source'], Q(event['q'])
            axpy(rows, target, source, q)
            flattened.append((target, source, q))
            peak = max(peak, sum(abs(x) for x in rows[target].values()))
        elif op == 'copy_begin':
            require(active is None, 'one temporary stream')
            active = (event['source'], dict(rows[event['source']]))
        elif op == 'copy_add':
            require(active is not None, 'copy read needs a live stream')
            source, frozen = active
            require(rows[source] == frozen, 'retained center changed before copy erasure')
            target, q = event['target'], Q(event['q'])
            axpy(rows, target, source, q)
            flattened.append((target, source, q))
            peak = max(peak, sum(abs(x) for x in rows[target].values()))
        elif op == 'copy_end':
            require(active is not None, 'copy erase needs a live stream')
            active = None
    require(active is None, 'temporary stream erased')
    require(rows == expected_rows(word), 'forward arbitrary-input map')
    reverse = [{i: Q(1)} for i in range(word['n'])]
    reverse_peak = Q(1)
    for target, source, q in flattened:
        axpy(reverse, source, target, -q)
        reverse_peak = max(reverse_peak, sum(abs(x) for x in reverse[source].values()))
    require(reverse == expected_rows(word, transpose=True), 'inverse-transpose arbitrary-input map')
    return dict(columns=word['n'], forward_peak_l1=str(peak), inverse_transpose_peak_l1=str(reverse_peak)), flattened


def frame_replay(word):
    frames = [basis(x) for x in word['initial_frames']]
    n, v = word['n'], word['v']
    require(n == 2 * v + word['helper_stock'] == 674, 'full matched stock')
    require(frames == [(p,) for p in word['geometry']['ports']] + [ZERO] * (n - v), 'input frames')
    active = None
    profile, copies, moves = Counter(), Counter(), Counter()
    source_reads, restoration, coefficients = Counter(), Counter(), Counter()
    transitions = []
    for index, event in enumerate(word['events']):
        op = event['op']
        if op == 'move':
            role = event['role']
            before, after = basis(event['before']), basis(event['after'])
            require(frames[role] == before, f'frame state at event {index}')
            require(before != after and contained(before, after), f'monotone frame at event {index}')
            if v <= role < 2 * v:
                require(contained(after, perp(word['geometry']['ports'][role - v])), 'target frame exceeds its sink')
            r = distance(before, after)
            profile[r] += 1
            moves[r] += 1
            transitions.append((before, after, r))
            frames[role] = after
        elif op == 'add':
            target, source, q, frame = event['target'], event['source'], Q(event['q']), basis(event['frame'])
            require(target != source and q != 0, 'nonzero scalar shear')
            require(frames[target] == frames[source] == frame, f'common frame at event {index}')
            require(q.denominator & (q.denominator - 1) == 0, 'dyadic coefficient')
            coefficients[str(q)] += 1
            if event['phase'] == 'source_read':
                require(source < v and target >= 2 * v and frame == (word['geometry']['ports'][source],), 'source read contract')
                source_reads[source] += 1
            if event['phase'] == 'restore_source':
                require(source < v and target >= 2 * v and frame == FULL, 'source restoration contract')
                restoration[source] += 1
        elif op == 'copy_begin':
            require(active is None, 'copy stream overlap')
            source, before, after = event['source'], basis(event['before']), basis(event['after'])
            require(frames[source] == before, 'copied source frame')
            require(contained(after, before), 'copy endpoint outside source span')
            r = distance(before, after)
            require(r > 0, 'nontrivial copied child')
            profile[r] += 1
            copies[r] += 1
            transitions.append((before, after, r))
            active = (event['term'], source, after)
        elif op == 'copy_add':
            require(active is not None and event['term'] == active[0], 'copy term lifetime')
            target, q, frame = event['target'], Q(event['q']), basis(event['frame'])
            require(v <= target < 2 * v and q != 0, 'copy target')
            require(frames[target] == active[2] == frame, f'copy common frame at event {index}')
            coefficients[str(q)] += 1
        elif op == 'copy_end':
            require(active is not None and event['term'] == active[0], 'copy erasure term')
            active = None
        else:
            raise ValueError('unknown event')
    require(active is None and source_reads == restoration, 'complete source and stream lifecycle')
    expected = [FULL] * v + [perp(p) for p in word['geometry']['ports']] + [FULL] * (n - 2 * v)
    require(frames == expected == [basis(x) for x in word['final_frames']], 'all physical sink frames')
    require(sum(copies.values()) == 8, 'all eight copied children')
    idle_moves = [e for e in word['events'] if e['op'] == 'move' and e['role'] in word['unused']]
    require(len(idle_moves) == len(word['unused']) and all(e['before'] == [] and basis(e['after']) == FULL for e in idle_moves), 'unused helper tails')
    return dict(profile=dict(sorted(profile.items())), copy_profile=dict(sorted(copies.items())),
                move_profile=dict(sorted(moves.items())), rank_mass=sum(r * z for r, z in profile.items()),
                source_reads=sum(source_reads.values()), source_restoration_reads=sum(restoration.values()),
                unused_helper_tails=len(idle_moves), coefficients=dict(sorted(coefficients.items()))), transitions


class CliffordAudit:
    def __init__(self):
        self.cx = load_clifford()
        self.frames = {}
        self.transitions = {}

    def frame(self, space):
        if space not in self.frames:
            operator = self.cx.canonical_frame(N, space)
            lagrangian = [(u, u) for u in space] + [(0, z) for z in self.cx.nullspace(space, N)]
            require(len(lagrangian) == N, 'Lagrangian dimension')
            for x, z in lagrangian:
                require(self.cx.apply(operator.tab, (x, z, 0))[0] == 0, 'exact frame preimage')
            self.frames[space] = operator
        return self.frames[space]

    def transition(self, before, after, expected_rank):
        key = (before, after)
        if key not in self.transitions:
            original = self.frame(before).adjoint().then(self.frame(after))
            record, compiled = self.cx.lower_child(original)
            require(record['rank'] == expected_rank, 'native Fourier rank')
            require(compiled.tab == original.tab, 'native Pauli equality')
            require(compiled.zero_state() == original.zero_state(), 'native exact global phase')
            require(sum(gate[0] == 'C' for gate in compiled.circuit) == expected_rank, 'one rank-r coordinate child')
            positions = [i for i, gate in enumerate(compiled.circuit) if gate[0] == 'C']
            require(positions == list(range(positions[0], positions[0] + expected_rank)), 'contiguous recursive child')
            self.transitions[key] = (record, original, compiled)
        require(self.transitions[key][0]['rank'] == expected_rank, 'cached rank contract')
        return self.transitions[key]

    def invoice(self, transitions):
        gates = Counter()
        for before, after, rank in transitions:
            _, _, compiled = self.transition(before, after, rank)
            gates.update(gate[0] for gate in compiled.circuit)
        return dict(positive_children=len(transitions), monomial_adapters=2 * len(transitions),
                    permutation_scans=gates['P'], diagonal_phase_scans=gates['D'],
                    xor_translation_scans=gates['X'], global_phase_scans=gates['phase'],
                    coordinate_C_factors=gates['C'])


def transpose_operator(cx, operator):
    result = cx.ident(N)
    for gate in reversed(operator.circuit):
        if gate[0] == 'P':
            part = cx.perm(N, cx.inv(gate[1], N))
        elif gate[0] == 'D':
            part = cx.diag(N, gate[1], gate[2])
        elif gate[0] == 'C':
            part = cx.cgate(N, gate[1], gate[2])
        elif gate[0] == 'X':
            part = cx.xgate(N, gate[1])
        elif gate[0] == 'phase':
            part = cx.Op(N, cx.identity(N), [gate])
        else:
            raise ValueError('transpose primitive')
        result = result.then(part)
    return result


def transpose_copy_checks(audit, word):
    records = []
    for event in word['events']:
        if event['op'] != 'copy_begin':
            continue
        before, after = basis(event['before']), basis(event['after'])
        record, original, _ = audit.transition(before, after, distance(before, after))
        transposed = transpose_operator(audit.cx, original)
        lowered, compiled = audit.cx.lower_child(transposed)
        require(lowered['rank'] == record['rank'], 'transpose copy rank')
        require(compiled.tab == transposed.tab and compiled.zero_state() == transposed.zero_state(), 'transpose copy phase')
        records.append(lowered['rank'])
    return records


def integer_column_replay(word):
    """Use scalar columns and fixed denominator four. Do not use row replay."""
    n, v = word['n'], word['v']
    for column in range(n):
        values = [0] * n
        values[column] = 4
        temporary = None
        for event in word['events']:
            op = event['op']
            if op == 'add':
                q = Q(event['q'])
                numerator = q.numerator * values[event['source']]
                require(numerator % q.denominator == 0, 'integer column denominator')
                values[event['target']] += numerator // q.denominator
            elif op == 'copy_begin':
                temporary = values[event['source']]
            elif op == 'copy_add':
                q = Q(event['q'])
                numerator = q.numerator * temporary
                require(numerator % q.denominator == 0, 'integer copied denominator')
                values[event['target']] += numerator // q.denominator
            elif op == 'copy_end':
                temporary = None
        expected = [0] * n
        expected[column] = 4
        if column < v:
            root_i = word['geometry']['live'][column]
            for t, root_t in enumerate(word['geometry']['live']):
                expected[v + t] += 2 * word['geometry']['gram'][root_t][root_i]
        require(values == expected, f'independent logical column {column}')
    return n


def uniform_gain(baseline, candidate):
    ranks = set(baseline) | set(candidate)
    delta = {r: candidate.get(r, 0) - baseline.get(r, 0) for r in sorted(ranks)}
    require(delta == {1: 49, 7: 53, 8: -56, 9: 3}, 'complete profile difference')
    require(1009 ** 256 > 8 * 1000 ** 256, 'first root upper bound')
    require(7 * 1001 ** 256 > 8 * 1000 ** 256, 'second root upper bound')
    margin = Q(421) - 49 * Q(1009, 1000) - 371 * Q(1001, 1000)
    require(margin == Q(47, 250) > 0, 'uniform recursive moment margin')
    selected_b = Q('0.001664727258740678855772')
    require(0 < selected_b < Q(1, 256), 'selected complex exponent inside interval')
    return dict(delta=delta, interval='0 <= b <= 1/256', bracket_upper_bound=str(-margin),
                selected_complex_b=str(selected_b), copied_rank='64 -> 63', rank_mass_saving=1)


def linear_invoice(word, frame_receipt, native):
    coefficients = Counter({Q(q): count for q, count in frame_receipt['coefficients'].items()})
    axpys = sum(coefficients.values())
    nonunit = sum(count for q, count in coefficients.items() if abs(q) != 1)
    reads = sum(event['op'] == 'copy_add' for event in word['events'])
    child_count = native['positive_children']
    adapter_scans = sum(native[key] for key in ('permutation_scans', 'diagonal_phase_scans', 'xor_translation_scans', 'global_phase_scans'))
    access_factor = 3 * axpys + 2 * adapter_scans + 2 * native['coordinate_C_factors'] + 3 * 8
    # A scale by 1/2 or 1/4 is charged as one scalar multiplication.
    return dict(original_streams=word['n'], dirty_helper_streams=word['helper_stock'],
                active_helper_streams=word['active_helpers'], sequential_temporary_streams=1,
                axpy_scans=axpys, scalar_additions_per_address=axpys,
                dyadic_scalar_multiplications_per_address=nonunit,
                source_read_scans=frame_receipt['source_reads'],
                source_restoration_scans=frame_receipt['source_restoration_reads'],
                copy_assign_scans=8, copy_erase_scans=8, copied_target_read_scans=reads,
                positive_recursive_children=child_count,
                inverse_transpose_zero_scans_instead_of_copy_assign=8,
                inverse_transpose_extra_center_injection_scans=8,
                emitted_events=len(word['events']),
                child_dispatches=child_count,
                maximum_live_complex_values_at_finite_size=675 * 512,
                address_bits=9,
                finite_complex_cell_accesses_per_address_bound=access_factor,
                inverse_transpose_extra_cell_accesses_per_address_bound=16,
                finite_tape_complex_cell_move_coefficient=2 * 675 * access_factor,
                finite_tape_bound_volume_power=2,
                fixed_address_metadata='Input-independent permutation cycles and phase tables; these contain no complex data.',
                permutation_bit_operations_per_value_bound=256,
                quadratic_phase_bit_operations_per_value_bound=144,
                finite_child_native_scans=native,
                route_contract='Every scan and child keeps the complete M-value stream. The full supplier must pay its retained row-routing interface.',
                literal_finite_tape_bound='With the 675 streams placed consecutively, each addressed read or write needs at most 2*675*M cell moves. Count these moves for every finite address access; no linear tape theorem is claimed.',
                stream_volume='M complex values, including every control and spectator value; M=512 in the finite replay.',
                clean_arithmetic_storage='O(1) Gaussian dyadic registers per scalar or adapter loop, plus the one temporary stream.',
                excluded='No global owner map, outer assembly, rounding implementation, or selected-supplier invoice is supplied.')


def compare_receipt(result, expected):
    """Compare JSON values without numeric or Boolean type coercion."""
    normalized = json.loads(json.dumps(result, allow_nan=False))
    actual_text = json.dumps(normalized, sort_keys=True, separators=(',', ':'), allow_nan=False)
    expected_text = json.dumps(expected, sort_keys=True, separators=(',', ':'), allow_nan=False)
    require(actual_text == expected_text, 'committed certificate agreement')


def run(out=None):
    audit = CliffordAudit()
    result = dict(base='8bddbee377e2f3ce1f1247196c4b290d55767d20', words={})
    words = []
    for replaced in (False, True):
        word = build(replaced)
        frames, transitions = frame_replay(word)
        scalar, _ = symbolic_replay(word)
        scalar['independent_integer_columns'] = integer_column_replay(word)
        native = audit.invoice(transitions)
        from physical import whole_word
        physical = whole_word(word, audit)
        dual_physical = whole_word(word, audit, inverse_transpose=True)
        for execution in (physical, dual_physical):
            require(execution['operations']['axpy'] == sum(frames['coefficients'].values()), 'physical scalar invoice')
            require(execution['operations']['C'] == frames['rank_mass'], 'physical recursive invoice')
            for gate, field in (('P', 'permutation_scans'), ('D', 'diagonal_phase_scans'), ('X', 'xor_translation_scans'), ('phase', 'global_phase_scans')):
                require(execution['operations'][gate] == native[field], 'physical adapter invoice')
            require(execution['operations']['copy_erase'] == 8, 'physical erasure invoice')
        require(physical['operations']['copy_assign'] == 8, 'physical allocation invoice')
        require(dual_physical['operations']['copy_zero'] == dual_physical['operations']['center_injection'] == 8, 'dual physical allocation invoice')
        transpose_ranks = transpose_copy_checks(audit, word)
        scalar_peak = max(Q(scalar['forward_peak_l1']), Q(scalar['inverse_transpose_peak_l1']))
        prefix = (1 << 22) * scalar_peak
        receipt = dict(frame=frames, scalar=scalar, physical=physical, inverse_transpose_physical=dual_physical, linear=linear_invoice(word, frames, native),
                       inverse_transpose_copy_ranks=transpose_ranks,
                       conservative_finite_component_prefix=str(prefix),
                       word_sha256=hashlib.sha256(json.dumps(serializable(word), sort_keys=True, separators=(',', ':')).encode()).hexdigest())
        result['words'][word['name']] = receipt
        words.append(word)
        print(f"PASS_{word['name'].upper()} columns={word['n']} profile={frames['profile']} axpys={receipt['linear']['axpy_scans']}", flush=True)
    result['uniform_gain'] = uniform_gain(result['words']['coordinate']['frame']['profile'], result['words']['one_replacement']['frame']['profile'])
    from physical import copy_matrix
    result['rank_seven_dense_copy'] = copy_matrix(words[1], audit)
    lowering_payload = [dict(before=before, after=after, native=record)
                        for (before, after), (record, _, _) in sorted(audit.transitions.items())]
    result['lowering_sha256'] = hashlib.sha256(json.dumps(lowering_payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    result['native_unique_frames'] = len(audit.frames)
    result['native_unique_transitions'] = len(audit.transitions)
    result['geometry'] = {k: words[1]['geometry'][k] for k in ('frame', 'extra', 'pivot', 'live', 'ports')}
    if out is not None:
        out.mkdir(parents=True, exist_ok=False)
        (out / 'CERTIFICATE.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
        for word in words:
            (out / (word['name'] + '-WORD.json')).write_text(json.dumps(serializable(word), indent=2, sort_keys=True) + '\n')
        (out / 'LOWERING.json').write_text(json.dumps(lowering_payload, indent=2, sort_keys=True) + '\n')
    return result, words, audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    expected_path = HERE / 'EXPECTED.json'
    require(expected_path.is_file(), 'committed certificate missing')
    expected = json.loads(expected_path.read_text())
    result, _, _ = run(args.out)
    compare_receipt(result, expected)
    print('PASS_SHARED_CARRIER_DECODER copies=64->63 columns=674 axpys=3552->3660 interval=[0,1/256] no_new_kappa')
