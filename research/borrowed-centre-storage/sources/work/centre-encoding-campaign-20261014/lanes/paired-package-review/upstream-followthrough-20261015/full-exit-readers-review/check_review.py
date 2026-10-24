#!/usr/bin/env python3
"""Review the FULL exit reader without a producer import."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import tarfile

ARCHIVE = 'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_PIN = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
LANES = 'work/centre-encoding-campaign-20261014/lanes/'
PACKET = LANES + 'cover-algebra/upstream-terminal-20261015/'
PINS = {
    'FULL-EXIT-READERS.md': '87e29b11bb77250b63c3d1218c9a5ff2015a2f25e3234a4fe8c4a55e2f6ac94f',
    'FULL-EXIT-READERS.json': 'bac80377e079538ee3d2c80deed9d8e15a9a5bc9683d6986a93f2652ad3b16b7',
    'FULL-EXIT-READERS-PROGRAMS.json.gz': 'af3fcff7f90c2d33d13f5a4f62af25a0138c5a2504c9e5a77f8d945bf955fc32',
    'emit_full_exit_readers.py': '3d85e0f63cfce884983e78e38a2e68bf0564a69fd00d1c827fd90b75b1d93b4d',
    'DIRTY-READER-REUSE.json': '53f3bc9891d560e60de374db099e7f588965091553fdc776230d96d8ae99f6c5',
}
MEMBERS = {
    'program': ('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz', '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
    'word': ('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
    'global': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz', '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
    'phases': ('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json', 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
}
INHERITED = {
    'PROOF.md': '410d540640137bdab6f80875c94eaed8a39e18c67539c882e74a31422ad6bd02',
    'NATIVE-LIFT-REVIEW.json': '61b3990c983b96b8bff01feab8c83a612ea41612b948b1059186ce9ffa9692ea',
    'FACTORIZATION.json': 'e723b841beb06dea26eab62328f36d37e67ee91fc1d5d69ea4bebbc6d60ce08e',
    'BRIDGE-REVIEW.md': 'd01b5f4959f7c91f835496d050dfae3eeab9dee2f581571c316a42571eaa1cd3',
    'BRIDGE-OPERATOR-REVIEW.json': 'c905a19d70f34c435c5f5454c6190bbfb1ce4594b1513bf76156acf620d7c6fc',
    'ORIGINAL-COMPLEX-MODES-REVIEW.json': '8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_pin(path, pin):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == pin, 'Pin: ' + str(path))
    return raw


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def wire(label):
    kind, index = label
    need(kind in ('L', 'C') and 0 <= index < (704 if kind == 'L' else 8), 'Wire label')
    return index + (704 if kind == 'C' else 0)


def add(row, source, factor=Q(1)):
    for column, value in source.items():
        total = row.get(column, 0) + factor * value
        if total:
            row[column] = total
        else:
            row.pop(column, None)


def scalar(event):
    gate = event[1]
    op, target = gate[0], wire(gate[1])
    if op in ('add', 'copy'):
        source = wire(gate[2])
        need(target != source, 'Distinct source and target')
        return op, target, source, Q(*gate[3:5]) if op == 'add' else Q(1)
    need(op in ('scale', 'clear'), 'Scalar grammar')
    return op, target, None, Q(*gate[2:4]) if op == 'scale' else Q(0)


def replay(events, initial=None):
    state = [{i: Q(1)} for i in range(712)] if initial is None else [dict(r) for r in initial]
    for event in events:
        if event[0] != 'scalar':
            continue
        op, target, source, coefficient = scalar(event)
        if op == 'clear':
            state[target] = {}
        elif op == 'scale':
            state[target] = {i: coefficient * v for i, v in state[target].items() if coefficient * v}
        elif op == 'copy':
            state[target] = dict(state[source])
        else:
            add(state[target], state[source], coefficient)
    return state


def backward_reader(prefix, output):
    row = {output: Q(1)}
    for event in reversed(prefix):
        if event[0] != 'scalar':
            continue
        op, target, source, coefficient = scalar(event)
        value = row.get(target, Q(0))
        if not value:
            continue
        if op == 'clear':
            del row[target]
        elif op == 'scale':
            row[target] = coefficient * value
        else:
            if op == 'copy':
                del row[target]
            add(row, {source: value}, coefficient)
    return {i: value for i, value in row.items() if value}


def frame_check(events, word):
    frames = word['start'][:] + [None] * 8
    gates = 0
    for event in events:
        kind = event[0]
        if kind in ('climb', 'center'):
            target = event[2] if kind == 'climb' else 704 + event[1]
            old, new = event[3:5] if kind == 'climb' else event[2:4]
            need(frames[target] == old, 'Native input frame')
            frames[target] = new
        elif kind == 'scalar':
            op, target, source, _ = scalar(event)
            common = event[2]
            if op == 'clear':
                frames[target] = common
            else:
                need(frames[target] == common, 'Scalar target frame')
                if source is not None:
                    need(frames[source] == common, 'Scalar source frame')
            gates += 1
        else:
            need(kind in ('adapter', 'residual_adapter', 'phase'), 'Native event grammar')
    return frames, gates


def cost(event):
    op, _, _, coefficient = scalar(event)
    if op in ('clear', 'copy'):
        return 2
    a, b = abs(coefficient.numerator), coefficient.denominator
    need(a and b & (b - 1) == 0, 'Nonzero dyadic scalar')
    if op == 'scale':
        need(a & (a - 1) == 0, 'Unit SCALE')
        return 2 * (abs(a.bit_length() - b.bit_length()) + (coefficient < 0))
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def polynomial(terms, dimension=25):
    linear, pairs = [0] * dimension, [0] * dimension
    for axis, coefficient in terms:
        bits = [j for j in range(dimension) if axis >> j & 1]
        for j in bits:
            linear[j] = (linear[j] + coefficient) % 4
            if coefficient % 2:
                for k in bits:
                    if k > j:
                        pairs[j] ^= 1 << k
    return linear, pairs


def check_transport(phases, recorded):
    axes = [1 << j for j in range(25)]
    rebuilt = []
    for item in phases['recipes']:
        b = item['idle_children'][0]['orthogonal_axes'][:8]
        delta = [v ^ axes[17 + j] for j, v in enumerate(b)]

        def move(v):
            result = v
            for d in delta:
                if (d & v).bit_count() % 2:
                    result ^= d
            return result

        need(all(move(move(v)) == v for v in axes), 'Actual stage-two involution')
        shift = item['stage_alignment'][2]['exit_X']
        need(move(shift) == shift, 'Transport translation is fixed')
        for depth, proposed in ((9, b + axes[9:17]), (17, b)):
            terms = [(v, 1) for v in axes] + [(move(v), -1) for v in axes[:depth]]
            need(polynomial(terms) == polynomial([(v, 1) for v in proposed] + [(shift, 2)]),
                 'Complete mod-four transport polynomial')
            need(all((v & w).bit_count() % 2 == (i == j)
                     for i, v in enumerate(proposed) for j, w in enumerate(proposed)),
                 'Orthogonal transport axes')
        rebuilt.append(dict(port=item['port'], q=item['q'], translation=shift,
                            FULL0_to_FULL2_axes=b + axes[9:17], X_level1_to_FULL2_axes=b))
    need(rebuilt == recorded['recipes'], 'All 112 transport recipes')
    return dict(ports=112, exact_quadratic_phase_identities=224, native_term_ranks=[16, 8])


def check_owners(template, phases, helpers, recorded):
    call = template['calls'][10]
    owners = {call['owners'][role][0]: role for role in helpers}
    need(len(owners) == 115, 'Distinct H owners')
    bases = [[r['q']] + r['idle_children'][0]['orthogonal_axes'][:8]
             + [1 << j for j in range(9, 73)] for r in phases['recipes']]
    axes = {family: ([bases[family % 112][0]] if (family // 112) % 2 == 0 else []) for family in owners}
    histories = defaultdict(list)
    slots = defaultdict(list)
    for index, item in enumerate(template['hosting']['pooled_slots']):
        slots[item['time']].append((index, item))
    for position, event in enumerate(template['execution_schedule']):
        if event['kind'] == 'local_cover_sweep':
            time = event['time']
            if time == 10:
                need(position == 18, 'Actual F2 invocation')
                break
            current = template['calls'][time]
            need(not owners.keys() & {r[0] for r in current['owners'][:224]}, 'No prior active H owner')
            for index, slot in slots[time]:
                family = slot['family']
                if family not in owners:
                    continue
                new = phases['recipes'][slot['port']]['idle_children'][slot['child']]['orthogonal_axes'][slot['offset']:slot['offset'] + slot['width']]
                need(len(new) == slot['width'] and all(not ((a & b).bit_count() % 2) for a in axes[family] for b in new),
                     'Disjoint prior H jobs')
                axes[family].extend(new)
                histories[family].append(index)
        else:
            need(event['kind'] in ('bridge', 'idle_cover_sweep'), 'Actual prefix event')
            pairs = [event['pair']] if event['kind'] == 'idle_cover_sweep' else [event['src'], event['dst']]
            touched = {896 * event['replica'] + 224 * pair + j for pair in pairs for j in range(224)}
            need(not owners.keys() & touched, 'No prior idle or bridge on H owner')
    old_records = {r['role']: r for r in recorded['H2_records']}
    ranks = Counter()
    for index, slot in slots[10]:
        role = 224 + slot['helper']
        if role not in helpers:
            continue
        family = slot['family']
        need(owners[family] == role and slot['width'] == 9, 'Actual full width-nine H job')
        route = call['owners'][role][1]
        need(route == [3, slot['child'], slot['offset']], 'Exact H owner route')
        pending = phases['recipes'][slot['port']]['idle_children'][slot['child']]['orthogonal_axes'][slot['offset']:slot['offset'] + 9]
        need(all(not ((a & b).bit_count() % 2) for a in axes[family] for b in pending),
             'No completed local H axis')
        sigma = pending + [v for v in bases[slot['port']] if v not in pending]
        need(len(set(sigma)) == 73, 'Complete H invocation chart')
        old = old_records[role]
        need(old['family'] == family and old['source_job'] == index and old['sigma_columns'] == sigma,
             'Source-bound H chart')
        need([item['source_job'] for item in old['history']] == histories[family], 'All prior H jobs')
        invocation = sum(1 << j for j, axis in enumerate(sigma) if axis in axes[family])
        need(old['invocation_axis_mask'] == invocation and not invocation & 511,
             'Exact exterior H frame')
        need(old['invocation_rank'] == len(axes[family]), 'Exact H exterior rank')
        ranks[len(axes[family])] += 1
    need(sum(map(len, histories.values())) == 142, 'All 142 prior H jobs')
    need(ranks == {0: 20, 1: 23, 9: 29, 10: 2, 14: 3, 15: 9, 24: 29}, 'H rank distribution')
    return dict(actual_call_time=10, schedule_position=18, helper_owners=115,
                prior_helper_jobs=142, prior_active_idle_bridge_uses=0,
                local_width=9, exterior_rank_counts=dict(sorted(ranks.items())))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    packet = args.repo / PACKET
    files = {name: read_pin(packet / name, pin) for name, pin in PINS.items()}
    for name, pin in INHERITED.items():
        read_pin(args.repo / LANES / 'interface-proof' / name, pin)
    raw = gzip.decompress(files['FULL-EXIT-READERS-PROGRAMS.json.gz'])
    need(sha256(raw).hexdigest() == '9f7a77d8cc2c2de149c8870c0223b7ce3c1ec754784725e2976bef75d1aeb422', 'Payload pin')
    payload, receipt = json.loads(raw), json.loads(files['FULL-EXIT-READERS.json'])
    archive_path = args.repo / ARCHIVE
    read_pin(archive_path, ARCHIVE_PIN)
    data = {}
    with tarfile.open(archive_path) as archive:
        for key, (name, pin) in MEMBERS.items():
            member = archive.extractfile(name).read()
            need(sha256(member).hexdigest() == pin, 'Member pin: ' + key)
            data[key] = json.loads(gzip.decompress(member) if name.endswith('.gz') else member)
    old, word = data['program']['forward'], data['word']
    begin, end = old.index(['phase', 'centers']), old.index(['phase', 'B'])
    readers = [backward_reader(old[:begin], target) for target in word['centers']]
    R = [{i: q for i, q in row.items() if i < 112} for row in readers]
    H = [{i: q for i, q in row.items() if 224 <= i < 704} for row in readers]
    need(all(set(row) <= set(r) | set(h) for row, r, h in zip(readers, R, H)), 'No target or private read')
    need(sum(map(len, R)) == 448 and sum(map(len, H)) == 404, 'Independent reader term counts')
    helper_support = set().union(*map(set, H))
    support = set(range(112)) | helper_support
    need(len(helper_support) == 115 and len(support) == 227, 'Exact reader support')
    need([{str(i): str(q) for i, q in row.items()} for row in readers] == payload['reader_rows'],
         'Reverse-derived reader rows equal the literal payload')
    cut = max(i for i, event in enumerate(old) if event[0] == 'scalar')
    need(cut == payload['insert_after_base_event'] == 24525, 'Exact scalar cut')
    frames, _ = frame_check(old[:cut + 1], word)
    need(all(frames[i] == word['final'][i] == 1 for i in support), 'Every read is at spatial FULL')
    need(all(word['start'][i] == 0 for i in helper_support), 'All used helpers start at local I')
    need(set(word['frames'][1]) == {1 << j for j in range(9)}, 'Exact FULL frame axes')
    tail = old[cut + 1:]
    need(len(tail) == 241 and sum(e[0] == 'residual_adapter' for e in tail) == 240,
         'Complete residual tail')
    need(all(e[0] == 'phase' or e[0] == 'residual_adapter' and e[2] not in support for e in tail),
         'No later adapter touches the read roles')
    recipe = []
    for k, row in enumerate(readers):
        recipe.append(['scalar', ['clear', ['C', k]], 1])
        recipe.extend(['scalar', ['add', ['C', k], ['L', i], q.numerator, q.denominator], 1]
                      for i, q in sorted(row.items()))
    need(recipe == payload['reader_recipe'], 'Independent literal reader reconstruction')
    need(sum(cost(e) for e in recipe) == receipt['reader_real_primitives'] == 6988, 'Complete reader scalar invoice')
    variants = {}
    baseline = {}
    for name, omit in (('original_with_owned_readers', False), ('centre_omitted_with_owned_readers', True)):
        base = [e for i, e in enumerate(old) if not (omit and begin <= i < end)]
        expected = [e for i, e in enumerate(old[:cut + 1]) if not (omit and begin <= i < end)] + recipe + tail
        program = payload['programs'][name]
        need(program == expected, 'Exact changed word and chronology')
        base_map, new_map = replay(base), replay(program)
        need(new_map[:704] == base_map[:704] and new_map[704:] == readers, 'All 712 columns and outputs')
        need(all(new_map[i] == {i: Q(1)} for i in support | set(range(224, 704))),
             'Source and arbitrary helper restoration')
        need(not any(i >= 704 for row in new_map for i in row), 'No arbitrary private input leak')
        final_frames, gate_count = frame_check(program, word)
        need(final_frames == word['final'] + [1] * 8, 'All persistent and private endpoint frames')
        native = lambda events: [e for e in events if e[0] in ('climb', 'adapter', 'residual_adapter')]
        need(native(program) == native(old) and len(native(program)) == 5056, 'Complete persistent native stream')
        counts = dict(scalar_real_primitives=sum(cost(e) for e in program if e[0] == 'scalar'),
                      centre_children=sum(e[0] == 'center' for e in program), persistent_native_events=5056)
        need(counts == receipt['variants'][name], 'Complete local scalar invoice')
        variants[name] = dict(**counts, scalar_frame_checks=gate_count, arbitrary_input_columns=712)
        baseline[name] = base_map
    original_map = baseline['original_with_owned_readers']
    omitted_map = baseline['centre_omitted_with_owned_readers']
    for p in range(112):
        need(original_map[p + 112] == {p: Q(1), p + 112: Q(1)}, 'Original identity shear')
        expected = dict(original_map[p + 112])
        for k in range(8):
            add(expected, readers[k], -R[k].get(p, 0) / 4)
        need(omitted_map[p + 112] == expected, 'Exact omitted-centre target debt')
    dirty = replay(recipe[1:], omitted_map)
    source_only = [e for e in recipe if e[1][0] == 'clear' or e[1][2][1] < 112]
    helper_only = [e for e in recipe if e[1][0] == 'clear' or e[1][2][1] >= 224]
    controls = dict(missing_private_clear=dirty[704].get(704) == 1,
                    missing_helper_part=replay(source_only, omitted_map)[704:] == R and R != readers,
                    missing_source_part=replay(helper_only, omitted_map)[704:] == H and H != readers,
                    private_exit_is_not_zero=any(readers))
    wrong_recipe = [e[:] for e in recipe]
    wrong_recipe[1] = [recipe[1][0], recipe[1][1], 0]
    try:
        frame_check(old[:cut + 1] + wrong_recipe + tail, word)
        controls['wrong_reader_frame_rejected'] = False
    except ValueError:
        controls['wrong_reader_frame_rejected'] = True
    need(all(controls.values()), 'Meaningful reader controls')
    owner_check = check_owners(data['global'], data['phases'], helper_support,
                               json.loads(files['DIRTY-READER-REUSE.json']))
    transport = check_transport(data['phases'], receipt['physical_transport_terms'])
    result = dict(status='PASS_INDEPENDENT_FULL_EXIT_READERS', packet_pins=PINS,
                  archive_sha256=ARCHIVE_PIN, members=MEMBERS, inherited_native_proofs=INHERITED,
                  reverse_derived_reader_count=8, source_terms=448, helper_terms=404,
                  full_read_roles=227, insert_after_base_event=cut, untouched_tail_adapters=240,
                  reader_ADDs=852, reader_CLEARs=8, reader_real_primitives=6988,
                  new_native_children=0, variants=variants, controls=controls,
                  actual_F2_owner_check=owner_check, exact_transport_check=transport,
                  reader_rows_sha256=sha256(encode(payload['reader_rows'])).hexdigest(),
                  review_scope='Exact local scalar maps, literal frames, new read placement, current F2 helper histories and transport phases. Old native kernels are inherited.',
                  open=['Cross-cover record allocation', 'Cross-call retention', 'Full changed controller',
                        'Physical recursive invoice and precision', 'Supplier or kappa improvement'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])
    print(json.dumps(dict(reader_real_primitives=6988, variants=variants, F2_helper_owners=115), sort_keys=True))


if __name__ == '__main__':
    main()
