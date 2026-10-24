"""Trace the added dirty-record channels through the complete schedule.

Read pinned data only. Use exact scalar rows and native phase words.
The reference is the same full-W consumer with clean owned records.
"""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import shutil
import tarfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
LANES = HERE.parents[2]
PORTABLE = LANES / 'portable-source-codes/dirty-record-hosting-20261015'
LOCAL = HERE.parent / 'eight-record-review-20261015'
PINS = {}
AXES = tuple(1 << i for i in range(73))


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path, digest):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == digest, 'Source pin: ' + str(path))
    PINS[str(path.relative_to(ROOT))] = digest
    return raw


def act(columns, value):
    out = 0
    while value:
        bit = value & -value
        out ^= columns[bit.bit_length() - 1]
        value ^= bit
    return out


def plus_phase(left, right):
    out = Counter(left)
    out.update(right)
    return {v: c % 4 for v, c in out.items() if c % 4 and v}


def native(axes, shift=0):
    out = Counter(axes)
    if shift:
        out[shift] += 2
    return {v: c % 4 for v, c in out.items() if c % 4}


def signature(terms):
    low = high = cross = 0
    for v, c in terms.items():
        if c & 1:
            high ^= low & v
            low ^= v
            bits = v
            while bits:
                bit = bits & -bits
                j = bit.bit_length() - 1
                cross ^= (v & (bit - 1)) << (j * (j - 1) // 2)
                bits ^= bit
        if c & 2:
            high ^= v
    return low, high, cross


def view_phase(columns, terms):
    out = {}
    for v, c in terms.items():
        w = act(columns, v)
        out[w] = (out.get(w, 0) + c) % 4
    return {v: c for v, c in out.items() if c}


def axpy(left, right, c=Q(1)):
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, 0) + c * value
        if not out[key]:
            del out[key]
    return out


def rowmap(row, letter):
    out = {}
    for (source, word), c in row.items():
        key = source, word[1:] if word and word[0] == letter else (letter,) + word
        out[key] = out.get(key, 0) + c
    return {key: c for key, c in out.items() if c}


def run_local(word, rows, omit_error=False):
    rows = {name: dict(row) for name, row in rows.items()}
    private = False
    for event in word:
        op = event['op']
        if op == 'add':
            if omit_error and event['dst'] == 'X0' and event['src'] == 'R0':
                continue
            rows[event['dst']] = axpy(rows[event['dst']], rows[event['src']], Q(event['c']))
        elif op == 'scale':
            rows[event['field']] = axpy({}, rows[event['field']], Q(event['c']))
        elif op == 'map':
            rows[event['field']] = rowmap(rows[event['field']], tuple(event['letter']))
        elif op == 'line':
            # All repair lines precede creation of the donor error.
            need(not rows[event['field']], 'No unmodelled native line on a nonzero error')
        elif op == 'private_begin':
            need(not private, 'No nested private sweep')
            private = True
        elif op == 'private_end':
            need(private and not rows['C'], 'Owned scratch returns zero')
            private = False
        elif op == 'clear':
            need(private and event['field'] == 'C', 'Only the owned C can be cleared')
            rows['C'] = {}
        else:
            raise ValueError('Unknown local operation: ' + op)
    need(not private, 'Complete private sweep')
    return rows


def family(replica, pair, side, port):
    return 896 * replica + 224 * pair + 112 * side + port


def main():
    need(shutil.disk_usage(HERE).free >= 3 * 1024 ** 3, 'At least three GiB free')
    word = json.loads(read(PORTABLE / 'consumer/DIRTY-CONSUMER-WORD.json',
        '4d2c2ec96d2f9978df0396ce66d6640a061459fbf9f84b10fd7f0556c7117e6c'))
    donors = json.loads(read(PORTABLE / 'TWO-CUT-DONORS.json',
        '1769aa102c41b5d81dfc463a64eacb6742601b52c30d566ed0222d8ac99e2d70'))
    local_words = json.loads(read(PORTABLE / 'eight-records/EIGHT-RECORD-WORDS.json',
        '8dcb0f29d2b0275e5d5395511d10451b8675c9ffe37ebdbd452c0132a17b15f4'))
    cleanup = json.loads(read(LOCAL / 'DELAYED-CLEANUP-ONE-C-WORD.json',
        'bddba461c6f06213c7ab938d24993ac6d5ea44169f9705594227acfdc5b6e880'))
    read(HERE.parent / 'review-gauss/delayed-dirty-cleanup/REVIEW.json',
        '74f7f7e2dd1eb4c36762b315f32b8a2462a9ab5dcd44d7378adea5a5a29ed993')
    read(LOCAL / 'REVIEW.json',
        '17b03e51d1a3ca9a8628bfcebc4e8b52208a77741ce2d7ed8c62cf89d57605b4')
    packet = LANES / 'paired-package-review/upstream-followthrough-20261015'
    read(packet / 'common-frame-source/evidence/NATIVE-REVIEW.json',
        'e9e9287a4a4d1be3c802899a42f70ff5dd5efd1e144a48bd585386fe234832e5')
    read(LANES / 'portable-source-codes/common-f-independent-review-20261015/REVIEW.json',
        'a930a9cda3f573f16b59d4538bc2920d9d22a8ba0e74e4a0e5ad6ce926a16fef')
    read(LANES / 'source-domain/two-cut-donor-review/REVIEW.json',
        '4b5d9f7d52df8db7a25d67c645c5b638af08a263b3ce6da69cdf7c20c58a1ce8')
    read(PORTABLE / 'algebra/composition-review/REVIEW.json',
        '0e7648b9b4a957b7e142830bebb44485771fa46f5e40a305791b98d37ae8bac3')
    cert = json.loads(gzip.decompress(read(packet / 'base/research/joint-query/certificate.json.gz',
        'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7')))
    archive = ROOT / 'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
    read(archive, 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6')
    members = {
        'template': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz',
                     '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
        'phases': ('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json',
                   'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa')}
    data = {}
    with tarfile.open(archive) as stream:
        for name, (member, pin) in members.items():
            raw = stream.extractfile(member).read()
            need(sha256(raw).hexdigest() == pin, 'Pinned archive member: ' + member)
            PINS['archive-member:' + member] = pin
            data[name] = json.loads(gzip.decompress(raw) if member.endswith('.gz') else raw)
    template, phases = data['template'], data['phases']['recipes']
    events, calls = template['execution_schedule'], template['calls']
    need(len(events) == 482 and len(calls) == 144, 'Complete original schedule')
    source = local_words['dirty_eight_A_before_cleanup']
    need(word['procedures']['capture'] == source['capture'], 'Literal capture binding')
    need(word['procedures']['repair'] == [e for e in source['repair'] if e['op'] != 'stage'],
         'Literal repair and exact removal of synthetic record advances')
    need(word['procedures']['cleanup'] == cleanup['cleanup'], 'Literal cleanup binding')
    a, t = tuple(cert['A_ports']), tuple(cert['T_ports'])
    r = [[Q(row.get(str(p), 0)) for p in range(112)] for row in cert['R_rows']]
    dot = lambda p, q: sum(r[k][p] * r[k][q] for k in range(8)) / 4
    need(all(sum(r[i][p] * r[j][p] for p in t) == 4 * (i == j)
             for i in range(8) for j in range(8)), 'Actual selected right inverse')

    selected = sorted(donors['allocations']['all']['selected'], key=lambda row: row['role'])
    need([row['role'] for row in selected] == list(range(128)), 'All 128 donor roles')
    need(len({row['family'] for row in selected}) == 128, 'Distinct physical donors')
    by_replica = {replica: selected[8 * replica:8 * replica + 8] for replica in range(16)}
    by_family = {row['family']: row for row in selected}
    position = {event['time']: at for at, event in enumerate(events) if event['kind'] == 'local_cover_sweep'}
    deadlines = {(event['replica'], child): at for at, event in enumerate(events)
                 if event['kind'] == 'idle_cover_sweep' for child in event['child_indices']}
    jobs = defaultdict(list)
    for index, job in enumerate(template['hosting']['pooled_slots']):
        child = phases[job['port']]['idle_children'][job['child']]
        axes = child['orthogonal_axes'][job['offset']:job['offset'] + job['width']]
        need(len(axes) == job['width'], 'Complete hosted helper width')
        call = calls[job['time']]
        need(call['owners'][224 + job['helper']][0] == job['family'], 'Actual helper owner binding')
        jobs[position[job['time']]].append((job['family'], axes, 0, 'helper', index))
    for index, job in enumerate(template['idle_children']):
        child = phases[job['port']]['idle_children'][job['child']]
        axes = child['orthogonal_axes'][job['pending_offset']:]
        need(len(axes) == job['rank'], 'Complete retained idle suffix')
        jobs[deadlines[job['replica'], job['child']]].append((job['family'], axes, 0, 'suffix', index))
    for at, event in enumerate(events):
        if event['kind'] == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                for port in range(112):
                    shift = phases[port]['idle_children'][child]['translation_after']
                    jobs[at].append((family(event['replica'], event['pair'], side, port),
                                     [], shift, 'translation', child))
    need(len(template['hosting']['pooled_slots']) == 69120, 'All complete helper jobs')
    need(len(template['idle_children']) == 7526, 'All retained idle suffixes')

    # E is an exact eight-column operator. Its stage-0 coefficients are scalar.
    local_error = {f'{side}{p}': {} for side in ('X', 'Y') for p in range(112)}
    for p in a:
        local_error['X' + str(p)] = {(p, ()): Q(-1)}
    for p in t:
        local_error['X' + str(p)] = {(q, ()): dot(p, q) for q in a if dot(p, q)}
    for p in range(112):
        local_error['Y' + str(p)] = axpy({}, local_error['X' + str(p)], Q(-1))
    probe = {name: {} for name in local_error}
    probe.update({'R' + str(p): {(p, ()): Q(1)} for p in a})
    probe['C'] = {}
    repaired = run_local(word['procedures']['repair'], probe)
    need(all(repaired[name] == row for name, row in local_error.items()), 'Literal repair creates exactly E h')
    need(all(repaired['R' + str(p)] == {(p, ()): Q(1)} for p in a), 'No extra donor-baseline query in the repair')
    clean = run_local(word['procedures']['cleanup'], repaired)
    need(all(not clean[name] for name in local_error), 'Literal cleanup removes every baseline direction')
    need(all(clean['R' + str(p)] == {(p, ()): Q(1)} for p in a), 'Cleanup preserves every arbitrary baseline')

    def trace(mutation=None):
        errors, frames, live, baseline = {}, {}, {}, {}
        statuses, cover_count = {}, Counter()
        closing = set()
        counts = Counter()
        log = []
        seen_old = []
        current_old = -1

        def close_windows():
            for replica in sorted(closing):
                for row in by_replica[replica]:
                    field = row['family']
                    need(signature(live[field]) == signature(baseline[field]), 'Final physical donor baseline phase')
                    need(cover_count[field] == 6, 'All three donor view pairs')
                    del live[field]
                    del baseline[field]
                statuses[replica] = 'closed'
            closing.clear()

        def advance(field, axes, shift, kind):
            phase = native(axes, shift)
            if field in errors:
                frames[field] = plus_phase(frames[field], phase)
                counts['dirty_data_' + kind] += 1
            if field in live:
                live[field] = plus_phase(live[field], phase)
                baseline[field] = plus_phase(baseline[field], phase)
                counts['live_donor_' + kind] += 1

        for index, event in enumerate(word['schedule']):
            op = event['op']
            if 'old_event' in event:
                close_windows()
                current_old = event['old_event']
                seen_old.append(current_old)
                old = events[current_old]
            if op == 'retained_event':
                kind = old['kind']
                if kind == 'local_cover_sweep':
                    call = calls[old['time']]
                    active = {item[0] for item in call['owners'][:224]}
                    need(not active & errors.keys(), 'Dirty data enters an active local core at event ' + str(current_old))
                    need(not active & live.keys(), 'A live borrowed query enters an active local core')
                    need(len({item[0] for item in call['owners']}) == 704, 'Distinct owners inside each complete core')
                    counts['clean_active_calls'] += 1
                elif kind == 'bank_padding_cover_sweep':
                    need(not template['bank_padding']['children'], 'No untracked padding work')
                elif kind == 'translate_every_live_family':
                    need(not errors and not live, 'All extra channels close before the final cover correction')
                else:
                    need(kind == 'idle_cover_sweep', 'Retained operation is field-diagonal or a complete core')
                for field, axes, shift, kind, _ in jobs[current_old]:
                    advance(field, axes, shift, kind)
            elif op == 'physical_pair_swap':
                need(old['kind'] == 'bridge' and old['source_event'] <= 18, 'Exact early bridge replacement')
                need(event['ports'] == list(range(112)), 'Full-W swap on every port')
                replica, left, right = event['replica'], event['src_pair'], event['dst_pair']
                touched = {family(replica, pair, side, p) for pair in (left, right)
                           for side in range(2) for p in range(112)}
                need(not touched & live.keys(), 'Modified bridge cannot read or write a live donor')
                wrong = mutation == 'keep_first_bridge' and old['replica'] == 0 and old['source_event'] == 3
                for side in range(2):
                    for p in range(112):
                        f, g = family(replica, left, side, p), family(replica, right, side, p)
                        if wrong:
                            continue
                        ef, eg, pf, pg = errors.pop(f, None), errors.pop(g, None), frames.pop(f, None), frames.pop(g, None)
                        if ef:
                            errors[g], frames[g] = ef, pf
                        if eg:
                            errors[f], frames[f] = eg, pg
                counts['complete_pair_swaps'] += 1
            elif op in ('omit_full_W_bridge', 'omit_full_W_terminal'):
                counts[op] += 1
            elif op == 'positive_X_lines':
                need(not errors and not live, 'No unremoved error at final positive X lines')
                counts['final_positive_lines'] += 16 * 112
            elif op == 'donor_cover_map':
                field, columns = event['field'], event['columns']
                row = by_family[field]
                expected = row['U_inverse_columns'] if cover_count[field] % 2 == 0 else row['U_columns']
                need(columns == expected, 'Actual alternating donor cover directions')
                need(field not in errors, 'A new donor view touches another live dirty data channel')
                if field in live:
                    live[field] = view_phase(columns, live[field])
                cover_count[field] += 1
            elif op == 'native_adapter':
                field, recipe = event['field'], event['recipe']
                need(field in live and field not in errors, 'Adapter acts only on its live donor')
                phase = native(recipe['axes'], recipe['translation'])
                need(signature(phase) == tuple(recipe['phase']), 'Literal exact native adapter phase')
                live[field] = plus_phase(live[field], phase)
            elif op == 'call_procedure':
                name, bind = event['name'], event['bindings']
                replica = bind['X0'] // 896
                own = {row['family'] for row in by_replica[replica]}
                data_fields = {bind[f'{side}{p}'] for side in ('X', 'Y') for p in range(112)}
                need(len(data_fields) == 224 and not data_fields & own, 'Distinct data and donor bindings')
                need(bind['C'] == 14336, 'Only the old owned C is used')
                need({bind['R' + str(p)] for p in a} == own, 'All eight actual donors')
                need(not data_fields & live.keys(), 'A procedure cannot use another live donor as data')
                need(not own & errors.keys(), 'No live donor aliases any dirty data channel')
                if name == 'capture':
                    need(not data_fields & errors.keys(), 'Capture source has no older baseline error')
                    need(not own & live.keys(), 'No overlapping donor lifetime')
                    need(current_old == donors['rows'][replica]['capture_after_event'], 'Actual capture cut')
                    for row in by_replica[replica]:
                        field = row['family']
                        need(cover_count[field] == 1, 'Capture is after its first gather')
                        live[field] = native(AXES[:9])
                        baseline[field] = native(row['U_columns'][:9])
                    statuses[replica] = 'captured'
                elif name == 'repair':
                    need(statuses[replica] == 'captured', 'Repair follows capture')
                    need(current_old == donors['rows'][replica]['repair_after_event'], 'Actual repair cut')
                    need(not data_fields & errors.keys(), 'No older data error enters a new repair')
                    need(all(signature(live[f]) == signature(native(AXES[:17])) for f in own), 'Every repair donor has the exact F17 phase')
                    for label, row in local_error.items():
                        if row:
                            field = bind[label]
                            errors[field] = {(8 * replica + a.index(p), route): c for (p, route), c in row.items()}
                            frames[field] = native(AXES[:17])
                    statuses[replica] = 'dirty'
                elif name == 'cleanup':
                    need(statuses[replica] == 'dirty', 'Cleanup follows repair')
                    need(current_old == donors['rows'][replica]['cleanup_after_event'], 'Actual cleanup cut')
                    need(all(signature(live[f]) == signature(native(AXES[:25])) for f in own), 'Every cleanup donor has the exact F25 phase')
                    for label, row in local_error.items():
                        expected = {(8 * replica + a.index(p), route): c for (p, route), c in row.items()}
                        field = bind[label]
                        need(errors.get(field, {}) == expected, 'All ordered dirty coefficients reach the correct parked field')
                        if expected:
                            need(signature(frames[field]) == signature(native(AXES[:25])), 'Exact dirty data F25 phase')
                    erase = run_local(word['procedures']['cleanup'], repaired,
                                      omit_error=mutation == 'omit_E_correction' and replica == 0)
                    need(all(not erase[label] for label in local_error), 'All-output cleanup removes every donor-baseline column')
                    for field in data_fields:
                        errors.pop(field, None)
                        frames.pop(field, None)
                    closing.add(replica)
                    statuses[replica] = 'closing'
                else:
                    raise ValueError('Unknown procedure')
                counts['procedure_' + name] += 1
            else:
                raise ValueError('Unknown global operation: ' + op)
            need(not errors.keys() & live.keys(), 'Data-error and live-donor supports remain disjoint')
            counts['peak_dirty_fields'] = max(counts['peak_dirty_fields'], len(errors))
            counts['peak_live_donors'] = max(counts['peak_live_donors'], len(live))
            log.append([index, current_old, op, len(errors), len(live)])
        close_windows()
        need(seen_old == list(range(482)), 'Every original event appears in order exactly once')
        need(not errors and not live and len(statuses) == 16, 'No added channel in any final output')
        need(all(state == 'closed' for state in statuses.values()), 'All cache windows close')
        return {'counts': dict(sorted(counts.items())),
                'boundary_trace_sha256': sha256(json.dumps(log, separators=(',', ':')).encode()).hexdigest(),
                'final_added_baseline_coefficients': 0,
                'checked_output_fields': 14336, 'other_three_pair_fields': 10752,
                'checked_baseline_directions': 128}

    result = trace()
    controls = {}
    for mutation in ('keep_first_bridge', 'omit_E_correction'):
        try:
            trace(mutation)
        except ValueError as error:
            controls[mutation] = str(error)
        else:
            raise ValueError('Ineffective global control: ' + mutation)
    output = {'status': 'PASS_COMPLETE_DIRTY_RECORD_NONINTERFERENCE',
              'comparison': 'Frozen dirty consumer minus the same full-W consumer with clean owned records',
              'source_pins': PINS, 'trace': result, 'negative_controls': controls,
              'literal_repair_and_cleanup_baseline_columns': 8,
              'all_size_method': 'Free ordered route rows plus exact mod-four physical native phases; no constant-cover restriction',
              'native_helper_contract': 'Inherited complete two-sided arbitrary-input endpoint; no internal cut used',
              'extra_correction_scalar_cost': 0, 'extra_correction_native_cost': 0,
              'not_proved': ['The clean reference has the required other three-pair output map',
                             'New recursive child hosting', 'Complete stream and precision invoice',
                             'Complete supplier or kappa improvement']}
    (HERE / 'CHECK.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': output['status'], **result, 'negative_controls': controls}, sort_keys=True))


if __name__ == '__main__':
    main()
