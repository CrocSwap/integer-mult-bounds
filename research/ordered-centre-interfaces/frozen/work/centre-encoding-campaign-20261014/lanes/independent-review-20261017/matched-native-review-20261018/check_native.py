#!/usr/bin/env python3
"""Review the full matched native word with a separate exact interpreter."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES/'oblique-native-20261017/matched-native-involution'
PINS = {
    'FREEZE.json': 'b35eae3fb4b53f51cfbed6bec8968b950c70e65bfe777cbe0d15e86c36dd4ab5',
    'MATCHED-NATIVE.md': '60f11b2f3f7a342f080e5715702a7cc8030e625211bac1787d728ffb72918664',
    'emit_matched_involution.py': '5f0e174607359ade1b25d01e9efb7816a2a2d7a4225a074d867652920bf3f460',
    'MATCHED-NATIVE-RECEIPT.json': '7bc873d627e022d4677b740633c9cd5f86c5e675d84460d538b4b6314c79536c',
}
INPUTS = {
    'native': ('oblique-native-20261017/matched-native-involution/MATCHED-NATIVE-PROGRAM.json.gz',
               '95f11d2b13fc75cb0d07e79ea17afdf3f46b4aca294117ffe1a988779e99f025'),
    'matching': ('controller-followthrough-20261017/matched-involution-20261018/MATCHED-INVOLUTION-PROGRAM.json',
                 'e2443eee2a7081ce3b57b9b7afcf4f1b061b9d8ddf0fbbeb5f7b29ce0d148902'),
    'small': ('history-encoding/permutation64-native-20261018/PERMUTATION64-PROGRAMS.json.gz',
              '87c76a500f8e22e4b500a5f5a64f23ef8cecadd0036785d7f54b2415972f1ff9'),
    'clean': ('new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz',
              'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'),
    'directions': ('history-encoding/independent-skeleton-20261018/fresh-three-child/FRESH-THREE-CHILD-PROGRAMS.json.gz',
                   'b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5'),
}
# The phase module was written for the preceding independent pair review.
# The native producer uses a different interpreter from an older lane.
PHASE_PATH = HERE.parent/'paired-centre-review-20261018/exact_phases.py'
PHASE_PIN = 'e1671c7c8129445aa0d9c324e377f9310d6e1c5dcdf566bd11ab90d17c47a305'
PEER_PATH = HERE.parent/'matched-involution-review-20261018/FREEZE.json'
PEER_PIN = '799f6849de59330a179f17f393c56f75d30df8844204cbfc6e9f3a6c867d74f6'


def need(test, message):
    if not test:
        raise ValueError(message)


def rows(value):
    return [{int(p): F(c) for p, c in row.items()} for row in value]


def add(target, source, scale=F(1)):
    for p, value in source.items():
        new = target.get(p, 0)+scale*value
        if new:
            target[p] = new
        else:
            target.pop(p, None)


def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in out}
    return out


def apply(matrix, vector):
    answer = {i: sum(c*vector.get(p, 0) for p, c in row.items()) for i, row in enumerate(matrix)}
    return {i: c for i, c in answer.items() if c}


def restrict(matrix, ports):
    index = {p: i for i, p in enumerate(ports)}
    return [{index[p]: c for p, c in matrix[r].items() if p in index} for r in ports]


def parse(event):
    gate, frame = event[1:]
    kind, target = gate[:2]
    need(kind in ('add', 'scale'), 'Only reversible scalar operations')
    origin = gate[2] if kind == 'add' else None
    return kind, target, origin, F(*gate[-2:]), frame


def price(kind, value):
    a, b = abs(value.numerator), value.denominator
    need(a and b & (b-1) == 0, 'Dyadic scalar coefficient')
    if kind == 'scale':
        need(a & (a-1) == 0, 'Unit dyadic scale')
        return 2*(abs(a.bit_length()-b.bit_length())+int(value < 0))
    return 2*(1+a.bit_length()+a.bit_count()+b.bit_length())


def reverse(events):
    columns = [{i: F(1)} for i in range(632)]
    for event in reversed(events):
        if event[0] == 'native':
            continue
        need(event[0] == 'scalar', 'No unlisted event')
        kind, target, origin, value, _ = parse(event)
        if kind == 'scale':
            columns[target] = {i: value*c for i, c in columns[target].items()}
        else:
            add(columns[origin], columns[target], value)
    return columns


def expected(response, backward):
    columns = [{i: F(1)} for i in range(632)]
    for target, row in enumerate(response):
        for origin, value in row.items():
            if backward:
                add(columns[112+target], {origin: -value})
            else:
                add(columns[origin], {112+target: value})
    return columns


def full_response(matching, small, q):
    mode_rows = [{int(p): F(c) for p, c in mode['coefficients'].items()} for mode in matching['modes']]
    matching_rows = rows(matching['mode_response'])
    little = rows(small['response'])
    large = set(matching['large_ports'])
    active = set(small['active_ports'])
    need(large.isdisjoint(active) and large | active == set(range(112)), 'Disjoint complete response support')
    for p in active:
        need(len(little[p]) == 1, 'One negative-permutation entry per small row')
        r, value = next(iter(little[p].items()))
        need(r != p and r in active and value == -1 and little[r] == {p: F(-1)}, '32 negative transpositions')
        need((q[p] & q[r]).bit_count() % 2 == 0, 'Actual small permutation source access')
    need(all(not little[p] for p in large), 'Small response vanishes on the large block')
    result = [{} for _ in range(112)]
    for column in range(112):
        code = {i: row[column] for i, row in enumerate(mode_rows) if column in row}
        routed = apply(matching_rows, code)
        decoded = defaultdict(F)
        for mode, value in routed.items():
            for p, coefficient in mode_rows[mode].items():
                decoded[p] += coefficient*value/2
        for p in active:
            decoded[p] += little[p].get(column, 0)
        for p, value in decoded.items():
            if value:
                result[p][column] = value
    need(all(result[p].get(r, 0) == result[r].get(p, 0) for p in range(112) for r in range(112)), 'Actual full symmetry')
    for column in range(112):
        unit = {column: F(1)}
        need(apply(result, apply(result, unit)) == unit, 'Actual full112 involution')
    return result


def ledger(word, source, matching, small_word, response, backward):
    frames = word['frames']
    current = list(word['start'])
    need(current == source['start'] and len(current) == 632, 'All actual entry frames')
    wanted = source['start'][:]
    wanted[:112] = [1]*112
    wanted[112:224] = source['final'][112:224]
    need(word['final'] == wanted, 'All actual final frames and unchanged helpers')
    state = [{i: F(1)} for i in range(632)]
    profile, progress, scalar_cost, maximum = Counter(), Counter(), 0, F(1)
    for event in word['events']:
        if event[0] == 'scalar':
            kind, target, origin, value, frame = parse(event)
            need(0 <= target < 224 and current[target] == frame, 'Scalar target is a productive field in its actual frame')
            if kind == 'add':
                need(0 <= origin < 224 and origin != target and current[origin] == frame, 'Equal-frame productive scalar source')
                add(state[target], state[origin], value)
            else:
                state[target] = {i: value*c for i, c in state[target].items()}
            scalar_cost += price(kind, value)
            maximum = max(maximum, sum(abs(c) for c in state[target].values()))
        else:
            need(event[0] == 'native', 'Only scalar and native events')
            _, target, old, new, rank, key = event
            need(0 <= target < 224 and current[target] == old, 'No helper or owned native access')
            need(key == str(old)+':'+str(new) and word['native_recipes'][key]['rank'] == rank, 'Literal native binding')
            need(span(frames[old]) < span(frames[new]), 'Strict monotone native progress')
            need(rank == len(frames[new])-len(frames[old]) and 1 <= rank <= 8, 'Exact proper-child rank')
            current[target] = new
            progress[target] += rank
            profile[rank] += 1
    need(current == word['final'], 'Complete final frame vector')
    need(all(progress[p] == 8 for p in range(224)), 'Exactly eight productive rank on every data field')
    need(profile == Counter({1: 160, 2: 48, 5: 48, 7: 112, 8: 64}), 'Complete native profile')
    need(scalar_cost == 3032 and maximum == 6, 'Complete scalar and top-level norm invoice')
    need(all(state[p] == {p: F(1)} for p in range(224, 632)), 'Every arbitrary helper is untouched')
    need(reverse(word['events']) == expected(response, backward), 'Independent all632 reverse columns')

    modes = matching['modes']
    seen = set()
    for pair in word['pair_codes']:
        a, b = pair['ports']
        need(not ({a, b} & seen), 'Disjoint pair code fields')
        seen |= {a, b}
        P = span([source['ports'][a], source['ports'][b]])
        need(span(frames[pair['plane']]) == P and len(P) == 4, 'Exact source pair plane')
        need(span(frames[pair['pair_hole']]) == {v for v in range(512) if all((v & p).bit_count() % 2 == 0 for p in P)}, 'Exact target pair perpendicular')
    need(seen == set(matching['large_ports']), 'All48 pair-coded ports')
    need(len(word['transfer_cuts']) == 48, 'All48 matching transfers')
    need(all({cut[key] for cut in word['transfer_cuts']} == set(range(48)) for key in ('source_mode', 'target_mode'))
         and len({cut['add_event'] for cut in word['transfer_cuts']}) == 48, 'Every mode is used once in the matching metadata')
    for cut in word['transfer_cuts']:
        i, j = cut['source_mode'], cut['target_mode']
        source_mode, target_mode = modes[i], modes[j]
        need(i != j and source_mode['vertex'] == target_mode['vertex'], 'Same-vertex off-diagonal matching')
        need(rows(matching['mode_response'])[j] == {i: F(cut['weight'])}, 'Actual matching coefficient')
        s, t = source_mode['carrier'], 112+target_mode['carrier']
        need(cut['source'] == s and cut['target'] == t, 'Literal carrier addresses')
        kind, target, origin, value, frame = parse(word['events'][cut['add_event']])
        need(kind == 'add' and frame == cut['frame'], 'Exact transfer event and frame')
        need((target, origin, value) == ((s, t, -F(cut['weight'])) if backward else (t, s, F(cut['weight']))), 'Ordered transpose shear transfer')
        P = span(source['ports'][p] for p in source_mode['ports'])
        Q = span(source['ports'][p] for p in target_mode['ports'])
        need(span(frames[frame]) == P and all((p & r).bit_count() % 2 == 0 for p in P for r in Q), 'Actual matched source access')

    inherited = word['events'][word['inherited_64_first_event']:]
    need(len(inherited) == len(small_word['events']), 'Complete inherited64 event suffix')
    for actual, prior in zip(inherited, small_word['events']):
        need(actual[0] == prior[0], 'Inherited event kind')
        if actual[0] == 'scalar':
            need(actual[1] == prior[1] and frames[actual[2]] == small_word['frames'][prior[2]], 'Inherited scalar event and literal basis')
        else:
            need(actual[1] == prior[1] and actual[4] == prior[4]
                 and frames[actual[2]] == small_word['frames'][prior[2]]
                 and frames[actual[3]] == small_word['frames'][prior[3]]
                 and word['native_recipes'][actual[5]] == small_word['native_recipes'][prior[5]], 'Inherited native event and full phase recipe')
    small_cost = sum(price(parse(e)[0], parse(e)[3]) for e in inherited if e[0] == 'scalar')
    need(small_cost == 512, 'All64 inherited signed ADDs are priced')
    matching_cost = sum(price('add', parse(word['events'][cut['add_event']])[3]) for cut in word['transfer_cuts'])
    pair_cost = scalar_cost-small_cost-matching_cost
    need(matching_cost == 384 and pair_cost == 2136, 'Independent scalar cost partition')
    return {'input_columns': 632, 'arbitrary_untouched_helpers': 408, 'native_profile': dict(sorted(profile.items())),
            'native_children': sum(profile.values()), 'native_mass': sum(k*v for k, v in profile.items()),
            'productive_rank_each': 8, 'query_rank': 0, 'owned_fields_used': 0, 'private_fields_used': 0,
            'scalar_real_primitives': scalar_cost, 'small64_scalar_real_primitives': small_cost,
            'pair_codes_and_inverse_scalar_real_primitives': pair_cost, 'matching_scalar_real_primitives': matching_cost,
            'top_level_array_l2_norm_bound': str(maximum), 'endpoint_maps': 224, 'native_side_map_bound': 864}


def main():
    for name, pin in PINS.items():
        need(sha256((SOURCE/name).read_bytes()).hexdigest() == pin, 'Producer source pin '+name)
    need(sha256(PEER_PATH.read_bytes()).hexdigest() == PEER_PIN, 'Independent matching matrix review')
    for name, pin in json.loads(PEER_PATH.read_bytes())['files'].items():
        need(sha256((PEER_PATH.parent/name).read_bytes()).hexdigest() == pin, 'Matching peer artifact '+name)
    need(sha256(PHASE_PATH.read_bytes()).hexdigest() == PHASE_PIN, 'Distinct exact phase interpreter pin')
    spec = importlib.util.spec_from_file_location('distinct_matched_phase', PHASE_PATH)
    phase = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase)
    data = {}
    for name, (relative, pin) in INPUTS.items():
        raw = (LANES/relative).read_bytes()
        if relative.endswith('.gz'):
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == pin, 'Pinned input '+name)
        data[name] = json.loads(raw)
    payload, matching, small = [data[k] for k in ('native', 'matching', 'small')]
    q = [r['q'] for r in data['directions']['transfers']]
    response = full_response(matching, small, q)
    need(response == rows(payload['response']), 'Actual merged full112 matrix')
    selected = payload['selected_ports']
    ordinary = payload['ordinary_ports']
    need(selected == matching['selected_ports'] and ordinary == sorted(set(range(112))-set(selected)), 'Exact selected partition')
    L, H = restrict(response, selected), restrict(response, ordinary)
    Linv, Hinv = rows(payload['selected_inverse']), rows(payload['ordinary_inverse'])
    need(L == rows(payload['selected_block']) == rows(matching['selected_block']), 'Unchanged selected block')
    for matrix, inverse in ((L, Linv), (H, Hinv)):
        for p in range(len(matrix)):
            unit = {p: F(1)}
            need(apply(matrix, apply(inverse, unit)) == apply(inverse, apply(matrix, unit)) == unit, 'Both principal inverse orders')
    need(all(c.denominator & (c.denominator-1) == 0 for matrix in (Linv, Hinv) for row in matrix for c in row.values()), 'Exact dyadic principal inverses')
    frame_cache, verified, reports = {}, set(), {}

    def frame(vectors):
        key = tuple(vectors)
        if key not in frame_cache:
            frame_cache[key] = phase.frame(key)
        return frame_cache[key]

    for provider, words in payload['providers'].items():
        source = data['clean']['providers'][provider]['canonical']
        need(source['ports'] == q, 'Provider and independent actual port directions agree')
        reports[provider] = {}
        for direction, word in words.items():
            backward = direction == 'backward'
            report = ledger(word, source, matching, small['providers'][provider][direction], response, backward)
            phase.equal(frame(word['frames'][0]), [], 'Actual I frame')
            phase.equal(frame(word['frames'][1]), phase.fourier(9), 'Actual FULL frame')
            for key, record in word['native_recipes'].items():
                old, new = map(int, key.split(':'))
                identity = (tuple(word['frames'][old]), tuple(word['frames'][new]), json.dumps(record, sort_keys=True))
                if identity not in verified:
                    phase.equal(phase.recipe(record), phase.adjoint(frame(word['frames'][old]))+frame(word['frames'][new]), 'Complete native edge '+key)
                    verified.add(identity)
            endpoints = word['endpoint_adapters']
            need(len(endpoints) == 224 and {(r['role'], r['port']) for r in endpoints}
                 == {(role, p) for role in ('source', 'target') for p in range(112)}, 'All224 endpoint records')
            for record in endpoints:
                p, role = record['port'], record['role']
                f = word['start'][p] if role == 'source' else word['final'][112+p]
                need(record['rank'] == 0 and record['frame'] == f, 'Exact endpoint rank and frame')
                conventional = [('C', q[p], 1)] if role == 'source' else [('C', q[p], -1)]+phase.fourier(9)
                identity = ('endpoint', role, q[p], tuple(word['frames'][f]), json.dumps(record, sort_keys=True))
                if identity not in verified:
                    phase.equal(phase.recipe(record), phase.adjoint(conventional)+frame(word['frames'][f]), 'Ordered endpoint '+role+' '+str(p))
                    verified.add(identity)
            report['native_recipe_records'] = len(word['native_recipes'])
            reports[provider][direction] = report
            print(provider, direction, 'all632 columns and full phases PASS', flush=True)
            if provider == 'base' and not backward:
                need(response != rows(matching['response'])
                     and reverse(word['events']) != expected(rows(matching['response']), False), 'The old64 Hadamard response is not substituted for the new permutation')
                mutation = json.loads(json.dumps(word['events']))
                cut = word['transfer_cuts'][0]['add_event']
                mutation[cut][1][-2] *= -1
                need(reverse(mutation) != expected(response, False), 'Wrong matching sign is rejected')
                large = set(matching['large_ports'])
                undo_first = max(i for i, e in enumerate(word['events'][:word['inherited_64_first_event']])
                                 if e[0] == 'native' and e[1] in large and e[3] == 1)+1
                undo_last = next(i for i in range(undo_first, len(word['events'])) if word['events'][i][0] == 'native')
                need(all(e[0] == 'scalar' for e in word['events'][undo_first:undo_last]) and undo_last > undo_first, 'Complete pair undo segment')
                need(reverse(word['events'][:undo_first]+word['events'][undo_last:]) != expected(response, False), 'Omitted source and target pair undo is rejected')
                first = next(iter(word['native_recipes'].values()))
                wrong = json.loads(json.dumps(first))
                wrong['left']['phase'] = (wrong['left']['phase']+1) % 4
                try:
                    phase.equal(phase.recipe(wrong), phase.recipe(first), 'Wrong global phase')
                except ValueError as error:
                    need('reference state' in str(error), 'Global phase mutation passes Pauli action but fails exact state')
                else:
                    raise ValueError('A wrong global phase was accepted')
    result = {'status': 'PASS_INDEPENDENT_FULL_MATCHED_NATIVE', 'producer_pins': PINS,
              'input_pins': {name: pin for name, (_, pin) in INPUTS.items()},
              'phase_interpreter_sha256': PHASE_PIN, 'matching_matrix_peer_freeze_sha256': PEER_PIN,
              'full_response_symmetric_involution': True, 'both_dyadic_principal_inverse_orders': True,
              'distinct_native_and_endpoint_phase_checks': len(verified), 'providers': reports,
              'method': 'Independent reverse columns; separate prefix frame and norm ledger; explicit mode routing; new direct Pauli and Gaussian-state interpreter, with no producer imports.',
              'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'scope': 'Complete full112 native data shears and exact exterior. Helper native progress, recursive hosting, routed controller, terminal, full precision, and supplier cost remain separate.'}
    (HERE/'CHECKS.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
