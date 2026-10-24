"""Check port retirement after the common-F repair.

This binds native types and the parked original values to the actual
schedule. It does not assert an identity on the other data outputs.
"""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile


A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
V = A + T
U = tuple(p for p in range(112) if p not in V)
ARCHIVE = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBER = 'candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz'
MEMBER_SHA = '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'


def need(ok, text):
    if not ok:
        raise ValueError(text)


def pin(raw, expected):
    need(sha256(raw).hexdigest() == expected, 'Source pin')
    return raw


def field(replica, pair, side, port):
    return 896 * replica + 224 * pair + 112 * side + port


def add(a, b, c=1):
    row = dict(a)
    for key, value in b.items():
        row[key] = row.get(key, 0) + c * value
        if not row[key]:
            del row[key]
    return row


def swap_check(omit_sign=False):
    # Independent symbols include the two different physical frame factors.
    a0, b0 = {('a', 'F'): Fraction(1)}, {('b', 'FQ^-1'): Fraction(1)}
    a = add(a0, b0)
    b = add(b0, a, -1)
    a = add(a, b)
    b = b if omit_sign else {key: -value for key, value in b.items()}
    need(a == b0 and b == a0, 'Physical swap restores both arbitrary arrays')


def trace(template, ports=V, mutation=None):
    levels = {(r, b): -1 for r in range(16) for b in range(4)}
    code = {}
    protected = set()
    jobs = []
    calls = []
    swaps = []
    local_source_events = []
    record_slots = {}
    record_intervals = []
    peak_record_sets = 0
    other_ports = tuple(p for p in range(112) if p not in ports)
    returned = set(other_ports)
    if mutation == 'missing_U_return':
        returned.remove(other_ports[0])
    for at, event in enumerate(template['execution_schedule']):
        kind = event['kind']
        r = event.get('replica')
        if kind == 'local_cover_sweep':
            call = template['calls'][event['time']]
            stage, pair = call['stage'], call['pair']
            need(stage == event['stage'] and call['replica'] == r, 'Actual call lookup')
            need(stage == 0 or levels[r, pair] == stage - 1, 'Active completed prefix')
            owners = call['owners']
            active = {x[0] for x in owners[:224]}
            need(active == {field(r, pair, side, p) for side in range(2) for p in range(112)},
                 'Actual data owner set')
            need(all(not code.get(f, 0) for f in active), 'Active data has its original native type')
            if stage >= 2:
                need(not (active & protected), 'A later call reads the retired selected data')
            for local, owner in enumerate(owners[224:], 224):
                f = owner[0]
                if code.get(f, 0):
                    jobs.append([event['time'], local, f])
            levels[r, pair] = stage
            calls.append([at, event['time'], r, pair, stage])
            if stage == 0:
                used = {slot for slot, _ in record_slots.values()}
                slot = next(k for k in range(16) if k not in used)
                record_slots[r] = (slot, at)
                peak_record_sets = max(peak_record_sets, len(record_slots))
            if stage == 1:
                need(pair == 0, 'First-pair repair location')
                slot, start = record_slots.pop(r)
                record_intervals.append([r, slot, start, at])
                for p in range(112):
                    code[field(r, 0, 1, p)] = int(p not in returned)
                protected.update(field(r, 0, side, p) for side in range(2) for p in ports)
                local_source_events.append(at)
        elif kind == 'idle_cover_sweep':
            pair = event['pair']
            need(levels[r, pair] == event['from_level'], 'Actual idle input level')
            levels[r, pair] = event['to_level']
            # The completed intrinsic block commutes with every extra C_q.
        elif kind == 'bridge':
            dst, src = event['dst'], event['src']
            need(levels[r, dst] == levels[r, src], 'Bridge completed prefixes agree')
            for p in other_ports:
                need(code.get(field(r, dst, 1, p), 0) == code.get(field(r, src, 1, p), 0),
                     'Ordinary Y bridge phase equality')
            if event['source_event'] <= 18:
                skip = ((mutation == 'missing_first_selected_swap' and event['source_event'] == 3)
                        or (mutation == 'missing_second_selected_swap' and event['source_event'] == 6))
                if not skip:
                    for side in range(2):
                        for p in ports:
                            a, b = field(r, dst, side, p), field(r, src, side, p)
                            code[a], code[b] = code.get(b, 0), code.get(a, 0)
                            pa, pb = a in protected, b in protected
                            protected.discard(a)
                            protected.discard(b)
                            if pb:
                                protected.add(a)
                            if pa:
                                protected.add(b)
                    swaps.append([at, r, dst, src, event['source_event']])
            # The final three selected bridges are omitted by this interface.
        elif kind in ('terminal_Y_translations', 'terminal'):
            need(all(levels[r, b] == 8 for b in range(4)), 'All data have full completed prefix')
            # The selected translations and signed exchanges are omitted.
        else:
            need(kind in ('bank_padding_cover_sweep', 'translate_every_live_family'),
                 'Global event alphabet')
    need(not record_slots, 'All early records are retired')
    expected = {field(r, 0, side, p) for r in range(16) for side in range(2) for p in ports}
    need(protected == expected, 'Original selected pair0 values return to their old owners')
    need({f for f, e in code.items() if e} ==
         {field(r, 0, 1, p) for r in range(16) for p in ports}, 'Only parked Y has the extra line')
    need(len(calls) == 144 and len(swaps) == 96, 'All call and selected bridge instances')
    return {'global_events': len(template['execution_schedule']), 'local_calls': len(calls),
            'selected_bridge_instances': len(swaps), 'protected_raw_outputs': 32 * len(ports),
            'old_helper_jobs_on_extra_line_fields': len(jobs),
            'helper_job_rows_sha256': sha256(json.dumps(jobs, separators=(',', ':')).encode()).hexdigest(),
            'repair_event_positions': local_source_events,
            'owned_record_intervals': record_intervals,
            'peak_owned_record_sets': peak_record_sets,
            'peak_owned_whole_cover_records': 16 * peak_record_sets,
            'calls_sha256': sha256(json.dumps(calls, separators=(',', ':')).encode()).hexdigest(),
            'no_later_active_call_reads_the_protected_values': True}


def endpoint_check(omit=False):
    def mul(a, b):
        return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]
    # On a translation orbit, raw X first has the virtual C_q^-1 factor.
    inverse = ((1, -1), (1, 1))
    positive = ((1, 1), (1, -1))
    if omit:
        need(inverse == ((2, 0), (0, 0)), 'Raw X endpoint still has C_q^-1')
    else:
        result = []
        for i in range(2):
            terms = [mul(positive[i ^ j], inverse[j]) for j in range(2)]
            result.append(tuple(sum(z[k] for z in terms) for k in range(2)))
        need(result == [(4, 0), (0, 0)], 'Raw X endpoint exact Gaussian inverse')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--lanes', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    archive = args.repo / 'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
    pin(archive.read_bytes(), ARCHIVE)
    with tarfile.open(archive) as data:
        template = json.loads(gzip.decompress(pin(data.extractfile(MEMBER).read(), MEMBER_SHA)))
    source = args.lanes / 'paired-package-review/upstream-followthrough-20261015'
    raw = pin((source / 'base/research/joint-query/certificate.json.gz').read_bytes(),
              'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7')
    packet = json.loads(gzip.decompress(raw))
    proof_path = args.lanes / 'encoded-controller/QQ16-CONSERVED-CONTROLLER.md'
    proof_raw = pin(proof_path.read_bytes(),
                    'e18594af767a26b0202e857d45202f5f563db2a190b81a7ade8fd62fcef850b9')
    need(b'each of the first six bridges swaps' in proof_raw and
         b'final three selected bridges and selected' in proof_raw, 'Selected bridge source')
    swap_check()
    choices = {'selected_16': V, 'whole_pair_112': tuple(range(112))}
    checks = {name: trace(template, ports) for name, ports in choices.items()}
    controls = {}
    for label in ('missing_U_return', 'missing_first_selected_swap',
                  'missing_second_selected_swap'):
        try:
            trace(template, V, label)
        except ValueError as error:
            controls[label] = str(error)
        else:
            raise ValueError('Ineffective schedule control: ' + label)
    try:
        swap_check(True)
    except ValueError as error:
        controls['missing_swap_sign'] = str(error)
    else:
        raise ValueError('Ineffective swap sign control')
    endpoint_check()
    try:
        endpoint_check(True)
    except ValueError as error:
        controls['missing_final_X_line'] = str(error)
    else:
        raise ValueError('Ineffective raw X endpoint control')
    routes = packet['map_registry']
    native_raw = pin((source / 'common-frame-results/COMMON-F-NATIVE-RECIPES.json').read_bytes(),
                     '8b58ab9d9983d8b105387923464e8c7a5639b95b1efbe193aa83e9de18949e6e')
    native = json.loads(native_raw)
    fixed_normals = []
    for p in range(112):
        recipe = native['line_' + str(p)]
        q = recipe['label']
        event = next(e for e in packet['programs']['F_2'] if e[0] == 'cover_map' and e[1] == ['L', p])
        g = routes[event[2]]['owner_right_matrix_columns']
        gq = 0
        for j, column in enumerate(g):
            if q >> j & 1:
                gq ^= column
        need(gq == q, 'F2 fixes the extra line')
        fixed_normals.append(q)
    inherited = args.lanes / 'interface-proof/ORIGINAL-COMPLEX-MODES-REVIEW.json'
    inherited_raw = pin(inherited.read_bytes(),
                        '8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d')
    content_raw = pin((source / 'common-frame-source/evidence/NATIVE-REVIEW.json').read_bytes(),
                      'e9e9287a4a4d1be3c802899a42f70ff5dd5efd1e144a48bd585386fe234832e5')
    common_raw = pin((source / 'common-frame-results/COMMON-F-RESTORATION-WORD.json').read_bytes(),
                     'c1fa3fe3596d939bbc42c0a41ad0078b43b74dca51fa41d7e3407736af07a74e')
    common = json.loads(common_raw)
    variants = {}
    comparisons = {}
    bridge_costs = {}
    for name, ports in choices.items():
        others = tuple(p for p in range(112) if p not in ports)
        return_word = [dict(op='line', field='Y' + str(p), port=p, sign=-1, rank=1) for p in others]
        endpoint_word = [dict(op='line', field='X' + str(p), port=p, sign=1, rank=1) for p in ports]
        added_events = common['capture_after_F0'] + common['repair_after_B1'] + return_word + endpoint_word
        rank_profile = Counter(e['rank'] for e in added_events if e['op'] in ('line', 'stage'))
        need(rank_profile == {1: 224, 8: 16}, 'Derived complete retirement profile')
        selected_swap = []
        for side in ('X', 'Y'):
            for p in ports:
                a, b = side + '_dst:' + str(p), side + '_src:' + str(p)
                selected_swap.extend([dict(op='add', dst=a, src=b, c=1),
                                      dict(op='add', dst=b, src=a, c=-1),
                                      dict(op='add', dst=a, src=b, c=1),
                                      dict(op='scale', field=b, c=-1)])
        variants[name] = {'retired_ports': list(ports), 'return_after_repair': return_word,
                          'port_swap_each_first_six_bridge': selected_swap,
                          'final_pair0_X_correction': endpoint_word}
        bridge_costs[name] = {'ordinary_complex_ADDs': 4 * len(others),
                             'physical_SWAPS': 4 * len(ports),
                             'real_scalar_allowance': 32 * len(others) + 104 * len(ports),
                             'new_native_children': 0}
        variants[name]['all_nine_bridge_invoice'] = {
            'ordinary_complex_ADDs': 18 * len(others),
            'physical_SWAPS': 12 * len(ports),
            'real_scalar_allowance': 144 * len(others) + 312 * len(ports),
            'new_native_children': 0}
        comparisons[name] = {'old_interface_mass': 352 + 2 * len(ports),
                             'old_interface_wrappers': 480 + 4 * len(ports),
                             'new_interface_mass': 352, 'new_interface_wrappers': 480,
                             'saved_redundant_rank_one_calls': 2 * len(ports)}
    word = {'schema': 'common-f-port-retirement-consumer-v1',
            'source_schedule_member_sha256': MEMBER_SHA,
            'common_F_word_sha256': sha256(common_raw).hexdigest(),
            'variants': variants,
            'final_three_bridges_on_retired_ports': [], 'terminal_on_retired_ports': [],
            'bridges_and_terminal_off_retired_ports': 'Retain the exact source schedule.',
            'placement': 'One repair after F0/B1 in each replica; final X correction before the last common cover translation.',
            'scope': 'Typed consumer and pair0 chosen-port retirement; other output content remains open.'}
    word_raw = json.dumps(word, sort_keys=True, separators=(',', ':')).encode() + b'\n'
    result = {'status': 'PASS_PORT_RETIREMENT_TYPED_CONSUMER', 'checks': checks,
              'source_pins': {'archive': ARCHIVE, 'template_member': MEMBER_SHA,
                              'selected_bridge_proof': sha256(proof_raw).hexdigest(),
                              'original_helper_phase_review': sha256(inherited_raw).hexdigest(),
                              'local_QQ16_whole_word_review': sha256(content_raw).hexdigest(),
                              'common_F_word': 'c1fa3fe3596d939bbc42c0a41ad0078b43b74dca51fa41d7e3407736af07a74e'},
              'negative_controls': controls, 'F2_fixed_normals': fixed_normals,
              'word_sha256': sha256(word_raw).hexdigest(),
              'per_replica_added_native_profile': dict(sorted(rank_profile.items())),
              'per_replica_added_native_mass': 352,
              'per_replica_added_native_wrappers': 480,
              'per_replica_added_scalar_allowance': 16338,
              'per_replica_added_cover_maps': 208,
              'per_replica_two_boundary_bridges': bridge_costs,
              'per_replica_all_nine_bridges': {name: value['all_nine_bridge_invoice']
                                              for name, value in variants.items()},
              'comparison_old_interface_then_endpoint': comparisons,
              'whole_controller_content_proved': False,
              'open': ['The data outputs outside the chosen pair0 port subset',
                       'New record storage and recursive child hosting',
                       'Stream access and finite precision', 'Complete supplier invoice'],
              'scope': 'The altered first pair has an exact typed continuation through all old data events; only the chosen pair0 raw outputs have the full completed transform.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.with_suffix('.word.json').write_bytes(word_raw)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'receipt_sha256': sha256(args.out.read_bytes()).hexdigest(),
                      'coded_helper_jobs': {name: value['old_helper_jobs_on_extra_line_fields']
                                           for name, value in checks.items()}}))


if __name__ == '__main__':
    main()
