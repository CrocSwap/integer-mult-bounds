"""Check the frozen all-output difference by separate window audits."""

from collections import Counter, defaultdict
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path
import shutil
import tarfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[6]
LANES = HERE.parents[3]
SOURCE = HERE.parents[1] / 'full-output-dirt-20261015'
PORTABLE = LANES / 'portable-source-codes/dirty-record-hosting-20261015'
AXES = tuple(1 << j for j in range(73))
PINS = {}


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path, digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, 'Source pin: ' + str(path))
    PINS[str(path.relative_to(ROOT))] = digest
    return raw


def family(replica, pair, side, port):
    return replica * 896 + pair * 224 + side * 112 + port


def action(columns, value):
    result = 0
    for j, column in enumerate(columns):
        if value >> j & 1:
            result ^= column
    return result


def product(left, right):
    return tuple(action(left, column) for column in right)


def native(axes, shift=0):
    result = Counter(axes)
    if shift:
        result[shift] += 2
    return {v: c % 4 for v, c in result.items() if v and c % 4}


def add_phase(left, right):
    result = dict(left)
    for v, c in right.items():
        result[v] = (result.get(v, 0) + c) % 4
        if not result[v]:
            del result[v]
    return result


def transform(columns, phase):
    result = {}
    for v, c in phase.items():
        result = add_phase(result, {action(columns, v): c})
    return result


def polynomial(phase):
    # Keep explicit linear coefficients and quadratic adjacency rows.
    linear, pairs = [0] * 73, [0] * 73
    for v, c in phase.items():
        bits = [j for j in range(73) if v >> j & 1]
        for j in bits:
            linear[j] = (linear[j] + c) % 4
        if c % 2:
            for at, j in enumerate(bits):
                for k in bits[at + 1:]:
                    pairs[j] ^= 1 << k
    return tuple(linear), tuple(pairs)


def verify_packed_recipe(recipe):
    linear, pairs = polynomial(native(recipe['axes'], recipe['translation']))
    low, high, packed = recipe['phase']
    require(all(linear[j] == ((low >> j & 1) + 2 * (high >> j & 1)) for j in range(73)),
            'Exact adapter linear phase')
    require(all((pairs[j] >> k & 1) == (packed >> (k * (k - 1) // 2 + j) & 1)
                for j in range(73) for k in range(j + 1, 73)), 'Exact adapter quadratic phase')


def axpy(left, right, scalar):
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, 0) + scalar * value
        if not out[key]:
            del out[key]
    return out


def local_replay(events, initial):
    rows = {name: dict(value) for name, value in initial.items()}
    private = False
    for event in events:
        op = event['op']
        if op == 'add':
            rows[event['dst']] = axpy(rows[event['dst']], rows[event['src']], F(event['c']))
        elif op == 'scale':
            rows[event['field']] = axpy({}, rows[event['field']], F(event['c']))
        elif op == 'map':
            letter = tuple(event['letter'])
            rows[event['field']] = {(p, w[1:] if w and w[0] == letter else (letter,) + w): c
                                    for (p, w), c in rows[event['field']].items()}
        elif op == 'line':
            require(not rows[event['field']], 'The repair line precedes donor-error creation')
        elif op == 'private_begin':
            require(not private, 'Local private entry')
            private = True
        elif op == 'private_end':
            require(private and not rows['C'], 'Local private zero exit')
            private = False
        elif op == 'clear':
            require(private and event['field'] == 'C', 'Only owned scratch is cleared')
            rows['C'] = {}
        else:
            raise ValueError('Unexpected local operation: ' + op)
    require(not private, 'Complete local private body')
    return rows


def main():
    require(shutil.disk_usage(HERE).free >= 3 * 1024 ** 3, 'Three GiB free')
    manifest = json.loads(read(SOURCE / 'MANIFEST.json',
        '9b5147aab388d5800f0bd2350fd1db3cc4694d0e4b8d5c762173d42c50f030af'))
    for name, digest in manifest['files'].items():
        read(SOURCE / name, digest)
    receipt = json.loads((SOURCE / 'CHECK.json').read_text())
    for path, digest in receipt['source_pins'].items():
        if not path.startswith('archive-member:'):
            read(ROOT / path, digest)
    word = json.loads((PORTABLE / 'consumer/DIRTY-CONSUMER-WORD.json').read_text())
    donors = json.loads((PORTABLE / 'TWO-CUT-DONORS.json').read_text())
    local = json.loads((PORTABLE / 'eight-records/EIGHT-RECORD-WORDS.json').read_text())
    cleanup = json.loads((SOURCE.parent / 'eight-record-review-20261015/DELAYED-CLEANUP-ONE-C-WORD.json').read_text())
    cert = json.loads(gzip.decompress((LANES / 'paired-package-review/upstream-followthrough-20261015/base/research/joint-query/certificate.json.gz').read_bytes()))
    archive = ROOT / 'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
    decoded = {}
    with tarfile.open(archive) as stream:
        for label, member in [('template', 'candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz'),
                              ('phases', 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json')]:
            raw = stream.extractfile(member).read()
            digest = receipt['source_pins']['archive-member:' + member]
            require(sha256(raw).hexdigest() == digest, 'Archive member: ' + member)
            PINS['archive-member:' + member] = digest
            decoded[label] = json.loads(gzip.decompress(raw) if member.endswith('.gz') else raw)
    template, phase_source = decoded['template'], decoded['phases']['recipes']
    events, calls = template['execution_schedule'], template['calls']
    require(template['live'] == 16 * 4 * 2 * 112 == 14336, 'All original output families')
    require(len(events) == 482 and len(calls) == 144 and len(word['schedule']) == 1506, 'Complete schedule sizes')
    require(word['procedures']['capture'] == local['dirty_eight_A_before_cleanup']['capture'], 'Capture bytes')
    require(word['procedures']['repair'] == [e for e in local['dirty_eight_A_before_cleanup']['repair'] if e['op'] != 'stage'], 'Repair bytes and removed synthetic lifts')
    require(word['procedures']['cleanup'] == cleanup['cleanup'], 'Cleanup bytes')
    a, t = tuple(cert['A_ports']), tuple(cert['T_ports'])
    r = [[F(row.get(str(p), 0)) for p in range(112)] for row in cert['R_rows']]
    dot = lambda p, q: sum(r[k][p] * r[k][q] for k in range(8)) / 4
    error = {f'{side}{p}': {} for side in ('X', 'Y') for p in range(112)}
    for p in a:
        error['X' + str(p)] = {(p, ()): F(-1)}
    for p in t:
        error['X' + str(p)] = {(q, ()): dot(p, q) for q in a if dot(p, q)}
    for p in range(112):
        error['Y' + str(p)] = axpy({}, error['X' + str(p)], -1)
    support = {name for name, row in error.items() if row}
    require(len(support) == 32, 'Exact error support')
    probe = {name: {} for name in error}
    probe.update({'R' + str(p): {(p, ()): F(1)} for p in a})
    probe['C'] = {}
    repaired = local_replay(word['procedures']['repair'], probe)
    require(all(repaired[name] == row for name, row in error.items()), 'Every local baseline column')
    require(all(repaired['R' + str(p)] == probe['R' + str(p)] for p in a), 'Local donor-baseline rows')
    restored = local_replay(word['procedures']['cleanup'], repaired)
    require(all(not restored[name] for name in error) and all(restored['R' + str(p)] == probe['R' + str(p)] for p in a), 'Literal baseline cleanup')
    no_e = local_replay(word['procedures']['cleanup'][:-len(cleanup['selected_error_correction'])], repaired)
    require(any(no_e[name] for name in error), 'Omission of the final E correction fails')

    outer = word['schedule']
    anchors = [(i, e['old_event']) for i, e in enumerate(outer) if 'old_event' in e]
    require([old for _, old in anchors] == list(range(482)), 'Every source event once and in order')
    outer_at = {old: i for i, old in anchors}
    old_at = {}
    for at, (begin, old) in enumerate(anchors):
        end = anchors[at + 1][0] if at + 1 < len(anchors) else len(outer)
        old_at.update({i: old for i in range(begin, end)})
    time_at = {e['time']: i for i, e in enumerate(events) if e['kind'] == 'local_cover_sweep'}
    active = {}
    for time, call in enumerate(calls):
        require(call['time'] == time, 'Original call index')
        expected = [[family(call['replica'], call['pair'], side, p), [1, call['stage'], p]]
                    for side in range(2) for p in range(112)]
        require(call['owners'][:224] == expected, 'All actual active owner bindings')
        require(len(call['owners']) == 704 and len({v[0] for v in call['owners']}) == 704, 'Distinct complete-core owners')
        active[time_at[time]] = {v[0] for v in expected}

    deadlines, partitions, jobs = {}, defaultdict(list), defaultdict(list)
    for old, event in enumerate(events):
        if event['kind'] == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                for p in range(112):
                    field = family(event['replica'], event['pair'], side, p)
                    require((field, child) not in deadlines, 'One pending-child deadline')
                    deadlines[field, child] = old
                    shift = phase_source[p]['idle_children'][child]['translation_after']
                    jobs[old].append((field, (), shift, 'translation'))
    for job in template['hosting']['pooled_slots']:
        field, child, offset, width = (job[k] for k in ('family', 'child', 'offset', 'width'))
        call = calls[job['time']]
        deadline = events[deadlines[field, child]]
        first_axis = 1 + 8 * (deadline['from_level'] + 1) + offset
        spectators = [j for j in range(73) if not first_axis <= j < first_axis + width][:9 - width]
        route = [3, child, offset] if width == 9 else [4, child, offset, width, spectators]
        require(call['owners'][224 + job['helper']] == [field, route], 'Full native helper owner route')
        require(job['port'] == field % 112 and job['owner_replica'] == field // 896, 'Helper family coordinates')
        axes = phase_source[job['port']]['idle_children'][child]['orthogonal_axes'][offset:offset + width]
        old = time_at[job['time']]
        require(len(axes) == width and old < deadlines[field, child], 'Complete helper axes before deadline')
        partitions[field, child].append((offset, width))
        jobs[old].append((field, tuple(axes), 0, 'helper'))
    for job in template['idle_children']:
        field, child, offset, width = (job[k] for k in ('family', 'child', 'pending_offset', 'rank'))
        axes = phase_source[job['port']]['idle_children'][child]['orthogonal_axes'][offset:]
        require(len(axes) == width, 'Complete idle suffix')
        partitions[field, child].append((offset, width))
        jobs[deadlines[field, child]].append((field, tuple(axes), 0, 'suffix'))
    require(len(deadlines) == 35840 and len(template['hosting']['pooled_slots']) == 69120
            and len(template['idle_children']) == 7526, 'Complete old pending-work census')
    for (field, child), deadline in deadlines.items():
        total = 0
        for offset, width in sorted(partitions[field, child]):
            require(offset == total and width > 0, 'Complete disjoint pending-child partition')
            total += width
        require(total == phase_source[field % 112]['idle_children'][child]['rank'], 'All pending axes accounted for')
    jobs_by_field = {(old, field): [(axes, shift, kind) for f, axes, shift, kind in group if f == field]
                     for old, group in jobs.items() for field in {x[0] for x in group}}

    selected = sorted(donors['allocations']['all']['selected'], key=lambda x: x['role'])
    require([x['role'] for x in selected] == list(range(128)) and len({x['family'] for x in selected}) == 128,
            'All distinct donor roles')
    by_family = {row['family']: row for row in selected}
    procedures, cuts = {}, {}
    for replica in range(16):
        cuts[replica] = [next(i for i, e in enumerate(events) if e.get('replica') == replica and
                             e['kind'] == kind and e.get('source_event') == source)
                         for kind, source in [('local_cover_sweep', 0), ('local_cover_sweep', 1), ('idle_cover_sweep', 5)]]
        require(cuts[replica] == [donors['rows'][replica][key] for key in
                                 ('capture_after_event', 'repair_after_event', 'cleanup_after_event')], 'Rebuilt three cuts')
        chosen = selected[replica * 8:replica * 8 + 8]
        for cut_number, name in enumerate(('capture', 'repair', 'cleanup')):
            old = cuts[replica][cut_number]
            pair = 1 if name == 'cleanup' else 0
            bind = {f'{side}{p}': family(replica, pair, j, p) for j, side in enumerate(('X', 'Y')) for p in range(112)}
            bind.update({'R' + str(p): row['family'] for p, row in zip(a, chosen)})
            bind['C'] = 14336
            expected = []
            if name != 'capture':
                for row in chosen:
                    recipe = row['adapters'][cut_number - 1]
                    if recipe['axes'] or recipe['translation']:
                        expected.append(dict(op='native_adapter', field=row['family'], recipe=recipe))
            expected += [dict(op='donor_cover_map', field=row['family'], columns=row['U_inverse_columns']) for row in chosen]
            expected += [dict(op='call_procedure', name=name, bindings=bind)]
            expected += [dict(op='donor_cover_map', field=row['family'], columns=row['U_columns']) for row in chosen]
            if name == 'cleanup':
                for row in chosen:
                    recipe = row['adapters'][2]
                    if recipe['axes'] or recipe['translation']:
                        expected.append(dict(op='native_adapter', field=row['family'], recipe=recipe))
            end = outer_at[old + 1]
            require(outer[outer_at[old] + 1:end] == expected, 'Exact outer boundary order and all field bindings')
            index = outer_at[old] + 1 + next(i for i, e in enumerate(expected) if e['op'] == 'call_procedure')
            procedures[replica, name] = index, bind

    swap_count = 0
    for index, event in enumerate(outer):
        if 'old_event' not in event:
            continue
        old = events[event['old_event']]
        if old['kind'] == 'bridge':
            if old['source_event'] <= 18:
                require(event == dict(op='physical_pair_swap', old_event=event['old_event'], replica=old['replica'],
                                     src_pair=old['src'], dst_pair=old['dst'], ports=list(range(112)),
                                     ordered_scalar_word=['a+=b', 'b-=a', 'a+=b', 'b=-b']), 'Actual complete swap word')
                swap_count += 1
            else:
                require(event['op'] == 'omit_full_W_bridge', 'Same clean-reference late bridge omission')
        elif old['kind'] in ('terminal_Y_translations', 'terminal'):
            require(event['op'] == 'omit_full_W_terminal', 'Same clean-reference terminal omission')
        else:
            require(event['op'] == 'retained_event', 'All other source events retained')
    require(swap_count == 96, 'All physical pair-swap blocks')

    dirty_at = [set() for _ in outer]
    live_at = [set() for _ in outer]
    counts = Counter()
    dirty_phase_checks = 0
    for replica in range(16):
        start, bind = procedures[replica, 'repair']
        stop, end_bind = procedures[replica, 'cleanup']
        places = {name: bind[name] for name in error}
        phases = {name: native(AXES[:17]) for name in error}
        moves = 0
        for index in range(start + 1, stop + 1):
            event = outer[index]
            current = {places[name] for name in support}
            dirty_at[index].update(current)
            if event['op'] == 'retained_event':
                old = event['old_event']
                require(not active.get(old, set()) & set(places.values()), 'Protected full pair enters active core at ' + str(old))
                reverse = {field: name for name, field in places.items()}
                for field, axes, shift, kind in jobs[old]:
                    if field in reverse:
                        name = reverse[field]
                        phases[name] = add_phase(phases[name], native(axes, shift))
                        if name in support:
                            counts['dirty_' + kind] += 1
                            if kind == 'translation' and shift:
                                counts['dirty_nonzero_translations'] += 1
            elif event['op'] == 'physical_pair_swap':
                if event['replica'] == replica:
                    left, right = event['src_pair'], event['dst_pair']
                    for name, field in list(places.items()):
                        pair = field % 896 // 224
                        if pair in (left, right):
                            places[name] += 224 * ((right if pair == left else left) - pair)
                    moves += 1
            elif event['op'] in ('donor_cover_map', 'native_adapter'):
                require(event['field'] not in current, 'New donor operation touches a dirty data field')
            elif event['op'] == 'call_procedure' and index != stop:
                touched = set(event['bindings'].values())
                require(not current & touched, 'A different procedure touches an older dirty row')
        require(moves == 1, 'Only the first swap moves dirty data before cleanup')
        require(places == {name: end_bind[name] for name in error}, 'All 224 parked fields at exact cleanup bindings')
        require(all(polynomial(p) == polynomial(native(AXES[:25])) for p in phases.values()), 'Full parked pair reaches exact F25')
        dirty_phase_checks += len(phases)

    donor_phase_checks = 0
    final_adapter_debts = 0
    for row in selected:
        role, field = row['role'], row['family']
        replica = role // 8
        first_old, _, last_old = cuts[replica]
        start, stop = outer_at[first_old] + 1, outer_at[last_old + 1]
        for index in range(start, stop):
            live_at[index].add(field)
        u, inverse_u = tuple(row['U_columns']), tuple(row['U_inverse_columns'])
        require(product(u, inverse_u) == AXES and product(inverse_u, u) == AXES, 'Both donor cover inverse orders')
        require(all((u[j] & u[k]).bit_count() % 2 == (j == k) for j in range(73) for k in range(73)), 'Orthogonal donor view')
        phase = reference = native(u[:9])
        net_owner = AXES
        seen_maps = 0
        phase_without_last = None
        for index in range(start, stop):
            event = outer[index]
            if event['op'] == 'retained_event':
                for axes, shift, kind in jobs_by_field.get((event['old_event'], field), ()):
                    increment = native(axes, shift)
                    phase, reference = add_phase(phase, increment), add_phase(reference, increment)
                    counts['donor_' + kind] += 1
            elif event['op'] == 'donor_cover_map' and event['field'] == field:
                phase = transform(event['columns'], phase)
                net_owner = product(event['columns'], net_owner)
                seen_maps += 1
            elif event['op'] == 'native_adapter' and event['field'] == field:
                verify_packed_recipe(event['recipe'])
                if index > procedures[replica, 'cleanup'][0]:
                    phase_without_last = dict(phase)
                phase = add_phase(phase, native(event['recipe']['axes'], event['recipe']['translation']))
            elif event['op'] == 'call_procedure' and index in [procedures[replica, name][0] for name in ('capture', 'repair', 'cleanup')]:
                width = {'capture': 9, 'repair': 17, 'cleanup': 25}[event['name']]
                require(polynomial(phase) == polynomial(native(AXES[:width])), 'Exact live donor phase at each named cut')
                donor_phase_checks += 1
        require(seen_maps == 6 and net_owner == AXES, 'Same donor cover values restored after all three views')
        require(polynomial(phase) == polynomial(reference), 'Every donor returns its old physical baseline operator')
        if phase_without_last is not None:
            require(polynomial(phase_without_last) != polynomial(reference), 'Final native adapter removes real baseline phase debt')
            final_adapter_debts += 1

    for index, event in enumerate(outer):
        dirty, live = dirty_at[index], live_at[index]
        require(not dirty & live, 'No cross-window dirty/live overlap')
        if event['op'] == 'retained_event':
            old = event['old_event']
            require(not active.get(old, set()) & (dirty | live), 'No added channel reaches an active input')
            if events[old]['kind'] in ('translate_every_live_family', 'bank_padding_cover_sweep'):
                require(not dirty and not live, 'All windows closed before the final correction')
        elif event['op'] == 'physical_pair_swap':
            touched = {family(event['replica'], pair, side, p) for pair in (event['src_pair'], event['dst_pair'])
                       for side in range(2) for p in range(112)}
            require(not touched & live, 'A complete swap cannot read a live donor')
        elif event['op'] == 'call_procedure':
            fields = event['bindings']
            data_fields = {fields[name] for name in error}
            record_fields = {fields['R' + str(p)] for p in a}
            require(not data_fields & live and not record_fields & dirty, 'No cross-window procedural access')
            if event['name'] != 'cleanup':
                require(not data_fields & dirty, 'New capture or repair has no old dirty input')
        elif event['op'] == 'positive_X_lines':
            require(not dirty and not live, 'All extra channels vanish before final positive lines')
    require(len(active) == 144 and counts['dirty_helper'] == 544 and counts['dirty_translation'] == 512
            and counts['donor_helper'] == 262, 'Independent support census')
    peak_dirty, peak_live = max(map(len, dirty_at)), max(map(len, live_at))
    require((peak_dirty, peak_live) == (128, 48), 'Peak support counts')
    unparked = {family(0, 0, int(name[0] == 'Y'), int(name[1:])) for name in support}
    require(unparked & active[18], 'Missing first swap exposes a dirty field to the actual F2 call')
    require(not dirty_at[-1] and not live_at[-1], 'No added channel at any final output')

    for path, digest in PINS.items():
        if not path.startswith('archive-member:'):
            require(sha256((ROOT / path).read_bytes()).hexdigest() == digest, 'Frozen source preserved')
    result = {'status': 'PASS_INDEPENDENT_ALL_OUTPUT_DIRTY_NONINTERFERENCE',
              'comparison': 'Same old productive inputs; dirty consumer minus the same full-W clean-owned-record consumer',
              'source_pins': PINS, 'method': 'Separate exact window audits, complete pending-work reconstruction, and explicit quadratic phases',
              'source_events': 482, 'outer_entries': 1506, 'active_cores': 144,
              'helper_jobs': 69120, 'idle_suffixes': 7526, 'pending_child_partitions': 35840,
              'pair_swap_blocks': swap_count, 'field_swaps': swap_count * 224,
              'donor_roles': 128, 'procedure_bindings': 48, 'local_baseline_columns': 8,
              'parked_field_phase_checks': dirty_phase_checks, 'donor_cut_phase_checks': donor_phase_checks,
              'donors_with_nonzero_final_adapter_debt': final_adapter_debts,
              'support_counts': dict(counts), 'peak_dirty_fields': peak_dirty, 'peak_live_donors': peak_live,
              'dirty_nonzero_translation_shifts': counts['dirty_nonzero_translations'],
              'final_difference_fields': 14336, 'final_added_coefficients': 0,
              'controls': ['No final E correction leaves a data column', 'Missing first swap exposes a dirty field at source event 18',
                           'Each nonempty final adapter removes a nonzero exact baseline phase'],
              'producer_imported_or_executed': False, 'full_native_core_replayed': False,
              'source_files_preserved': True,
              'excluded': ['Required other-three-pair target map', 'New recursive child hosting', 'Complete stream invoice',
                           'Rounding and complete supplier precision', 'Complete supplier or kappa gain']}
    (HERE / 'CHECK.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])
    print(json.dumps({k: result[k] for k in ('support_counts', 'parked_field_phase_checks', 'donor_cut_phase_checks',
                                           'donors_with_nonzero_final_adapter_debt', 'peak_dirty_fields', 'peak_live_donors')}, sort_keys=True))


if __name__ == '__main__':
    main()
