#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact two-panel centre-return contract; no actual512-dimensional replay."""
import argparse
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
BASE = 'candidate/strict/global/base/providers/gauge44/'
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))
ROLES = 240
SOURCES = [92, 57, 81, 224, 11, 240, 9, 256]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def ga(a, b):
    return a[0] + b[0], a[1] + b[1]


def gm(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def gs(q, a):
    return q*a[0], q*a[1]


def adjoint(a):
    return tuple(tuple((a[j][i][0], -a[j][i][1]) for j in range(2)) for i in range(2))


def mm(a, b):
    return tuple(tuple(ga(gm(a[i][0], b[0][j]), gm(a[i][1], b[1][j]))
                       for j in range(2)) for i in range(2))


def mv(a, v):
    return tuple(ga(gm(a[i][0], v[0]), gm(a[i][1], v[1])) for i in range(2))


def operators():
    c = (((Q(1,2), Q(1,2)), (Q(1,2), Q(-1,2))),
         ((Q(1,2), Q(-1,2)), (Q(1,2), Q(1,2))))
    phases = (ONE, (Q(0), Q(1)), (Q(-1), Q(0)), (Q(0), Q(-1)))
    identity = ((ONE, ZERO), (ZERO, ONE))
    forward = []
    for k in range(8):
        diagonal = ((phases[k % 4], ZERO), (ZERO, phases[(k + 1) % 4]))
        f = mm(diagonal, c if k < 4 else adjoint(c))
        need(mm(adjoint(f), f) == mm(f, adjoint(f)) == identity, 'representative not unitary')
        forward.append(f)
    return forward, [adjoint(f) for f in forward]


def source_checks():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    inputs = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            path = (ROOT / row['path']).resolve()
            need(path.is_relative_to(ROOT) and path.is_file(), 'invalid input path')
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'source drift')
            inputs[row['path']] = row['sha256']
    need(ARCHIVE in inputs, 'archive not declared as input')
    return inputs


def selected_blocks():
    consumed, data = {}, {}
    with tarfile.open(ROOT / ARCHIVE, 'r:gz') as archive:
        for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json'):
            raw = archive.extractfile(BASE + name).read()
            payload = gzip.decompress(raw) if name.endswith('.gz') else raw
            consumed[BASE + name] = hashlib.sha256(payload).hexdigest()
            data[name] = json.loads(payload)
    canonical = data['CANONICAL-WORD.json.gz']
    programs, checks = data['LOCAL-PROGRAMS.json.gz'], data['LOCAL-CHECKS.json']
    need(canonical['v'] == 112 and canonical['centers'] == SOURCES and
         canonical['center_frames'] == list(range(415, 423)) and not canonical.get('target_levels'),
         'selected centre inventory changed')
    need(len(canonical['cut']) == 176, 'selected cut count changed')
    need(canonical['frames'][0] == [], 'ZERO frame is not empty')
    for frame in canonical['center_frames']:
        basis = {}
        for row in canonical['frames'][frame]:
            while row:
                pivot = row.bit_length() - 1
                if pivot in basis:
                    row ^= basis[pivot]
                else:
                    basis[pivot] = row
                    break
        need(len(basis) == len(canonical['frames'][frame]) == 8, 'centre frame lacks rank eight')
    for name in ('forward', 'backward'):
        need(digest(programs[name]) == checks[name]['sha256'], 'published complete event binding')
    events = programs['backward']
    first, last = events.index(['phase', 'centers']), events.index(['phase', 'B'])
    block = events[first+1:last]
    need(len(block) == 208, 'backward centre phase is not208 macros')
    coefficients = []
    for k, source in enumerate(SOURCES):
        part = block[26*k:26*(k+1)]
        need(part[0] == ['scalar', ['clear', ['C', k]], 0], 'initial centre CLEAR changed')
        row = []
        for event in part[1:23]:
            need(event[0] == 'scalar' and event[2] == 0 and event[1][0] == 'add'
                 and event[1][1] == ['C', k] and event[1][2][0] == 'L', 'gather event changed')
            op = event[1]
            j = op[2][1] - 112
            need(0 <= j < 112 and type(op[3]) is int and type(op[4]) is int and op[4] != 0,
                 'invalid gathered target/coefficient')
            row.append((j, Q(op[3], op[4])))
        cf = 415 + k
        need(part[23:] == [['center', k, 0, cf, 8],
                          ['scalar', ['add', ['L', source], ['C', k], -1, 1], cf],
                          ['scalar', ['clear', ['C', k]], cf]], 'return path changed')
        expected = [(e[1]-112, Q(e[3], e[4])) for e in canonical['cut'] if e[2] == source]
        need(row == expected and len(row) == 22, 'cut coefficient/target mismatch')
        coefficients.append(row)
    return coefficients, {'consumed_member_payload_sha256': consumed,
                          'source_registers': SOURCES, 'centre_frames': list(range(415, 423)),
                          'backward_phase_start': first, 'backward_phase_macros': 208,
                          'gathers_per_centre': 22, 'total_gathers_per_panel': 176,
                          'gather_rows_target_index_and_coefficient':
                              [[[j, str(q)] for j, q in row] for row in coefficients],
                          'centre_frame_vectors': [canonical['frames'][f] for f in range(415, 423)],
                          'complete_program_sha256': {n: checks[n]['sha256'] for n in checks}}


def word(rows, fused):
    events = []
    for panel_group in ((0, 1),) if fused else ((0,), (1,)):
        for k, row in enumerate(rows):
            scratch = 232 + k
            events.append(('clear', scratch))
            for panel in panel_group:
                for j, q in row:
                    events.append(('add', scratch, 8 + 112*panel + j, q))
            events.extend((('R8', scratch, k, panel_group[0]),
                           ('add', k, scratch, Q(-1)), ('clear', scratch)))
    return events


def run(events, basis, ops):
    values = [(ZERO, ZERO)] * ROLES
    values[basis//2] = (ONE, ZERO) if basis % 2 == 0 else (ZERO, ONE)
    for event in events:
        tag, target = event[:2]
        if tag == 'clear':
            values[target] = (ZERO, ZERO)
        elif tag == 'R8':
            values[target] = mv(ops[event[3]][event[2]], values[target])
        elif tag == 'scale':
            values[target] = tuple(gs(event[2], z) for z in values[target])
        else:
            source, q = event[2:]
            values[target] = tuple(ga(a, gs(q, b)) for a, b in zip(values[target], values[source]))
    return values


def expected(rows, basis, ops):
    values = [(ZERO, ZERO)] * ROLES
    role, coordinate = divmod(basis, 2)
    unit = (ONE, ZERO) if coordinate == 0 else (ZERO, ONE)
    if role < 232:
        values[role] = unit
    if 8 <= role < 232:
        panel, j = divmod(role - 8, 112)
        for k, row in enumerate(rows):
            q = sum((q for index, q in row if index == j), Q(0))
            values[k] = tuple(gs(-q, z) for z in mv(ops[panel][k], unit))
    return values


def serial(values):
    return [[[str(a), str(b)] for a, b in vector] for vector in values]


def mismatch(actual_word, rows, ops, reference=None, expected_ops=None):
    for basis in list(range(464, 480)) + list(range(464)):
        actual = run(actual_word, basis, ops)
        want = run(reference, basis, ops) if reference is not None else expected(rows, basis, expected_ops or ops)
        if actual != want:
            out = next(i for i in range(ROLES) if actual[i] != want[i])
            return {'input_coordinate': basis, 'output_role': out,
                    'actual': serial([actual[out]])[0], 'expected': serial([want[out]])[0]}
    raise ValueError('control preserves complete typed endpoint')


def controls(rows, separate, fused, forward, backward):
    ops, result = [backward, backward], {}
    mutations = {}
    bad = list(fused); bad.pop(0); mutations['omitted_initial_clear'] = bad
    bad = list(fused); bad.pop(47); mutations['omitted_final_clear'] = bad
    bad = list(fused); bad.pop(1); mutations['omitted_panel_gather'] = bad
    bad = list(fused); bad[46] = ('add', 0, 232, Q(1)); mutations['flipped_source_sign'] = bad
    for name, events in mutations.items():
        result[name] = mismatch(events, rows, ops)
    result['wrong_forward_operator'] = mismatch(fused, rows, [forward, forward], expected_ops=ops)
    changed = copy.deepcopy(backward)
    changed[0] = tuple(tuple(gs(-1, z) for z in row) for row in changed[0])
    result['mismatched_second_operator'] = mismatch(fused, rows, [backward, changed])
    # Naive fusion across an intervening sink scale changes the second panel's weight.
    reference = separate[:208] + [('scale', 0, Q(2))] + separate[208:]
    result['intervening_sink_scale'] = mismatch(fused + [('scale', 0, Q(2))], rows, ops, reference)
    return result


def precision_and_cost(rows):
    single = [sum((abs(q) for _, q in row), Q(0)) for row in rows]
    need(all(value == Q(11, 2) for value in single), 'positive row-L1 inventory changed')
    prefixes = []
    for row in rows:
        total, peak = Q(0), Q(0)
        for _, q in row + row:
            total += abs(q)
            peak = max(peak, total)
        need(peak == total == 2*sum((abs(q) for _, q in row), Q(0)), 'two-panel positive prefix envelope')
        prefixes.append(str(peak))
    # Exact prefix counterexample: +1 and -1 cancel only after the first read.
    need(max(abs(Q(1)), abs(Q(1)-Q(1))) == 1 and abs(Q(1)-Q(1)) == 0,
         'observed-cancellation control')
    need(2*Q(1) == Q(2), 'tight two-panel envelope fixture')
    # Linear unit macro tariff, charging EVERY fused macro at the extra bit.
    need(416*12 == 384*13 and 416*13 - 384*14 == 32, 'illustrative weighted threshold')
    need(416*13 - 384*14 - 31 > 0 and 416*13 - 384*14 - 32 == 0
         and 416*13 - 384*14 - 33 < 0, 'overhead threshold control')
    return {'single_positive_row_L1': list(map(str, single)), 'fused_positive_row_L1': [str(2*x) for x in single],
            'fused_positive_prefix_peaks': prefixes,
            'scratch_envelope_multiplier': 2, 'additional_magnitude_bits_sufficient': 1,
            'tight_fixture': {'panel_a': 1, 'panel_b': 1, 'fused': 2},
            'cancellation_control': {'panel_a': 1, 'panel_b': -1, 'final': 0, 'prefix_peak': 1},
            'separate_bill': '16 R8(mu)+368 ADD(mu)+32 CLEAR(mu)',
            'fused_bill': '8 R8(mu+1)+360 ADD(mu+1)+16 CLEAR(mu+1)+DeltaH',
            'linear_unit_macro_saving': '32*mu-384-DeltaH', 'zero_overhead_tie_mu': 12,
            'first_positive_integer_mu': 13, 'mu13_overhead_threshold': 32,
            'admission': 'positive-envelope sufficiency only; no native precision/tape/hosting admission'}


def compute():
    pins = source_checks()
    rows, provenance = selected_blocks()
    forward, backward = operators()
    separate, fused = word(rows, False), word(rows, True)
    need(len(separate) == 416 and len(fused) == 384, 'complete macro counts')
    counts = lambda es: {tag: sum(e[0] == tag for e in es) for tag in ('clear', 'R8', 'add')}
    need(counts(separate) == {'clear': 32, 'R8': 16, 'add': 368}
         and counts(fused) == {'clear': 16, 'R8': 8, 'add': 360}, 'primitive inventory')
    transcript = hashlib.sha256()
    for basis in range(480):
        wanted = expected(rows, basis, [backward, backward])
        need(run(separate, basis, [backward, backward]) == wanted, 'separate signed-adjoint endpoint')
        need(run(fused, basis, [backward, backward]) == wanted, 'fused signed-adjoint endpoint')
        transcript.update(encoded(serial(wanted)))
    defects = controls(rows, separate, fused, forward, backward)
    need(source_checks() == pins, 'sources changed during replay')
    return {'status': 'PASS_CENTRE_SHARED_RETURN_GUARD', 'input_sha256': pins, 'provenance': provenance,
            'contract': {'shared_sink_rows': 8, 'panels': 2, 'targets_per_panel': 112, 'scratch_rows': 8,
                         'same_scratch_for_comparators': True, 'incoming_scratch': 'arbitrary, erased',
                         'final_scratch': 'zero', 'source_panels_and_scratch_disjoint': True},
            'finite_fixture': {'coordinates_per_row': 2, 'all_basis_inputs': 480,
                               'unitary_operators': 8, 'forward_operators': [serial(f) for f in forward],
                               'backward_operators': [serial(f) for f in backward],
                               'unitarity_and_inverse_checked': True,
                               'endpoint_sha256': transcript.hexdigest(),
                               'actual512_operator_replay': False},
            'separate_counts': counts(separate), 'fused_counts': counts(fused), 'controls': defects,
            'precision_and_bill': precision_and_cost(rows),
            'scope': 'Two-panel backward centre-phase contract; no full-call supplier admission or kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    if args.write_result:
        need(not args.write_result.exists(), 'output already exists')
    result = compute()
    if args.write_result:
        with args.write_result.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    else:
        need(encoded(result) == encoded(json.loads((HERE / 'RESULT.json').read_text())), 'receipt mismatch')
    print('PASS_CENTRE_SHARED_RETURN_GUARD basis=480 separate=416 fused=384 controls=7 no_new_kappa')


if __name__ == '__main__':
    main()
