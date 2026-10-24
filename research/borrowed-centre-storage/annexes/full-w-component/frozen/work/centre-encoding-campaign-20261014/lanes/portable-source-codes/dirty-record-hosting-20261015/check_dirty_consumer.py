"""Bind the dirty repair, two-cut donor paths, and delayed full-W erase.

Keep the exact local programs as shared procedures. Emit their physical
owner bindings and order in the actual schedule. Do not claim new child
hosting or a complete supplier invoice.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
REPO = HERE.parents[4]
MATH = LANES / 'paired-package-review/upstream-followthrough-20261015/check_restoration.py'
CLEANUP = LANES / 'residual-syndrome/physical-algebra/eight-record-review-20261015/DELAYED-CLEANUP-ONE-C-WORD.json'
ARCHIVE = REPO / 'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz'
PINS = {
    'source_math': (MATH, '8c6fb324aa898f86b3edbd85252570a2dc43c40455887f789a153191645686ca'),
    'local_words': (HERE / 'eight-records/EIGHT-RECORD-WORDS.json', '8dcb0f29d2b0275e5d5395511d10451b8675c9ffe37ebdbd452c0132a17b15f4'),
    'donor_paths': (HERE / 'TWO-CUT-DONORS.json', '1769aa102c41b5d81dfc463a64eacb6742601b52c30d566ed0222d8ac99e2d70'),
    'cleanup': (CLEANUP, 'bddba461c6f06213c7ab938d24993ac6d5ea44169f9705594227acfdc5b6e880'),
    'archive': (ARCHIVE, 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'),
}


def need(ok, text):
    if not ok:
        raise ValueError(text)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()+b'\n'


def price(word):
    scalar = 0
    counts = Counter(e['op'] for e in word)
    for e in word:
        if e['op'] == 'clear':
            scalar += 2
        elif e['op'] in ('add', 'scale'):
            c = Q(e['c'])
            a, b = abs(c.numerator), c.denominator
            if e['op'] == 'add':
                scalar += 2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)
            else:
                scalar += 2*(abs(a.bit_length()-b.bit_length())+(c < 0))
    return {'scalar_allowance': scalar, 'cover_maps': counts['map'],
            'event_counts': dict(sorted(counts.items()))}


def replay(m, programs, R, A, T, U, routes, mutation=None):
    x, y = m.unit_bank('x:'), m.unit_bank('y:')
    x1, y1 = m.forward(x, y, R, A, T, U)
    rows = {f'X{p}': x1[p] for p in range(112)}
    rows.update({f'Y{p}': y1[p] for p in range(112)})
    frames = {f'X{p}': m.OLD for p in range(112)}
    frames.update({f'Y{p}': m.OLD+((routes[1, p]['q'], -1),) for p in range(112)})
    h = {p: {(f'donor:{p}', ()): Q(1)} for p in A}
    for p in A:
        rows[f'R{p}'], frames[f'R{p}'] = h[p], m.OLD
    rows['C'], frames['C'] = {('private:', ()): Q(1)}, ()
    helpers = {f'H{p}': {(f'helper:{p}', ()): Q(1)} for p in range(480)}
    rows.update(helpers)
    frames.update({field: () for field in helpers})
    m.execute(programs['capture'], rows, frames, routes, set())
    x2, y2 = m.backward(x1, y1, R, A, T, U, 1, 2)
    for p in range(112):
        rows[f'X{p}'], frames[f'X{p}'] = x2[p], m.CURRENT
        rows[f'Y{p}'], frames[f'Y{p}'] = y2[p], m.CURRENT+((routes[1, p]['q'], -1),)
    # A1 K1 supplies this frame. No synthetic E1 child is run here.
    for p in A:
        frames[f'R{p}'] = m.CURRENT
    m.execute(programs['repair'], rows, frames, routes, set())
    full2 = tuple((v, 1) for v in m.AXES[:25])
    for field in rows:
        if field[0] in ('X', 'Y', 'R'):
            frames[field] = full2
    if mutation == 'missing_second_donor_advance':
        frames[f'R{A[0]}'] = m.CURRENT
    # This is the logical content after the proved whole-pair parking.
    # Only the owned scratch is discarded. The donor values stay arbitrary.
    private = False
    for event in programs['cleanup']:
        op = event['op']
        if op == 'private_begin':
            need(not private, 'One private cleanup body')
            private = True
        elif op == 'private_end':
            need(private and not rows['C'] and m.phase(frames['C']) == m.phase(()), 'Cleanup scratch return')
            private = False
        elif op == 'clear':
            need(private and event['field'] == 'C', 'No borrowed CLEAR')
            need(event['frame'] in ('common_F_U2', 'identity'), 'Exact cleanup frame label')
            rows['C'] = {}
            frames['C'] = full2 if event['frame'] == 'common_F_U2' else ()
        elif op == 'add':
            dst, src = event['dst'], event['src']
            need('C' not in (dst, src) or private, 'Owned scratch access')
            need(m.phase(frames[dst]) == m.phase(frames[src]), 'Cleanup physical ADD frame')
            if mutation == 'omit_data_error_correction' and dst == f'X{A[0]}' and src == f'R{A[0]}':
                continue
            rows[dst] = m.rowadd(rows[dst], rows[src], Q(event['c']))
        elif op == 'map':
            need(not private, 'Complete cover map outside private sweep')
            field, letter = event['field'], tuple(event['letter'])
            r = routes[letter]
            need(tuple(event['g']) == r['g'], 'Actual cleanup owner map')
            frames[field] = m.transport(frames[field], tuple(event['g']), event['shift'])
            rows[field] = m.route(rows[field], letter)
        else:
            raise ValueError('Unexpected cleanup operation')
    need(not private, 'Complete cleanup')
    for p in range(112):
        need(rows[f'X{p}'] == x[p] and rows[f'Y{p}'] == y[p], 'All data and donor coefficients return')
    need(all(rows[f'R{p}'] == h[p] for p in A), 'All arbitrary donors return')
    need(not rows['C'] and all(rows[field] == value for field, value in helpers.items()), 'Scratch and inherited helper endpoints')
    need(all(m.phase(frames[field]) == m.phase(full2) for field in rows if field[0] in ('X', 'Y', 'R')), 'All local common F_U2 endpoints')
    result = {field: [[source, list(word), str(c)] for (source, word), c in sorted(row.items())]
              for field, row in sorted(rows.items())}
    return sha256(encoded(result)).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    raw = {}
    for name, (path, digest) in PINS.items():
        raw[name] = path.read_bytes()
        need(sha256(raw[name]).hexdigest() == digest, 'Pinned source '+name)
    spec = importlib.util.spec_from_file_location('retained_math', MATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    _, R, A, T, U, routes = m.load()
    source = json.loads(raw['local_words'])['dirty_eight_A_before_cleanup']
    cleanup = json.loads(raw['cleanup'])
    procedures = {'capture': source['capture'],
                  'repair': [event for event in source['repair'] if event['op'] != 'stage'],
                  'cleanup': cleanup['cleanup']}
    removed = [event for event in source['repair'] if event['op'] == 'stage']
    need(len(removed) == 8 and all(event['stage'] == 1 and event['rank'] == 8 and event['sign'] == 1 for event in removed), 'Replace exactly eight E1 record children')
    local_hash = replay(m, procedures, R, A, T, U, routes)
    controls = {}
    for label in ('missing_second_donor_advance', 'omit_data_error_correction'):
        try:
            replay(m, procedures, R, A, T, U, routes, label)
        except ValueError as error:
            controls[label] = str(error)
        else:
            raise ValueError('Ineffective composition control')
    with tarfile.open(ARCHIVE) as archive:
        member = archive.extractfile(MEMBER).read()
    need(sha256(member).hexdigest() == '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760', 'Pinned selected template')
    template = json.loads(gzip.decompress(member))
    need(template['private_namespace']['centers'] == [14336, 14344], 'Old owned private namespace')
    donors = json.loads(raw['donor_paths'])
    chosen = donors['allocations']['all']
    by_replica = {replica: sorted((row for row in chosen['selected'] if row['role']//8 == replica), key=lambda row: row['role']) for replica in range(16)}
    need(len({row['family'] for row in chosen['selected']}) == 128, 'Distinct donor families')
    schedule, intervals = [], []
    protected = {}
    captured, cleaned = set(), set()
    live, peak = set(), 0
    levels = {(r, pair): -1 for r in range(16) for pair in range(4)}

    def bindings(replica, pair):
        out = {f'{side}{p}': 896*replica+224*pair+112*index+p for index, side in enumerate(('X', 'Y')) for p in range(112)}
        out.update({f'R{p}': row['family'] for p, row in zip(A, by_replica[replica])})
        out['C'] = 14336
        return out

    def donor_block(replica, phase):
        rows = by_replica[replica]
        if phase == 'capture':
            return [{'op': 'donor_cover_map', 'field': row['family'], 'columns': row['U_inverse_columns']} for row in rows]
        return [{'op': 'donor_cover_map', 'field': row['family'], 'columns': row['U_columns']} for row in rows]

    def adapter_block(replica, index):
        return [{'op': 'native_adapter', 'field': row['family'], 'recipe': row['adapters'][index]}
                for row in by_replica[replica] if row['adapters'][index]['axes'] or row['adapters'][index]['translation']]

    for at, event in enumerate(template['execution_schedule']):
        kind, replica = event['kind'], event.get('replica')
        if kind == 'local_cover_sweep':
            call = template['calls'][event['time']]
            stage, pair = call['stage'], call['pair']
            need(stage == event['stage'] and call['replica'] == replica, 'Literal active call binding')
            need(stage == 0 or levels[replica, pair] == stage-1, 'Actual active entrance level')
            need(stage < 2 or protected.get(replica) != pair, 'No later active call reads parked pair')
            levels[replica, pair] = stage
        elif kind == 'idle_cover_sweep':
            need(levels[replica, event['pair']] == event['from_level'], 'Actual idle entrance level')
            levels[replica, event['pair']] = event['to_level']
        if kind == 'bridge':
            src, dst = event['src'], event['dst']
            need(levels[replica, src] == levels[replica, dst], 'Physical bridge native levels')
            if event['source_event'] <= 18:
                schedule.append({'op': 'physical_pair_swap', 'old_event': at, 'replica': replica,
                                 'src_pair': src, 'dst_pair': dst, 'ports': list(range(112)),
                                 'ordered_scalar_word': ['a+=b', 'b-=a', 'a+=b', 'b=-b']})
                if protected.get(replica) == src:
                    protected[replica] = dst
                elif protected.get(replica) == dst:
                    protected[replica] = src
            else:
                schedule.append({'op': 'omit_full_W_bridge', 'old_event': at})
        elif kind in ('terminal', 'terminal_Y_translations'):
            schedule.append({'op': 'omit_full_W_terminal', 'old_event': at})
        else:
            if kind == 'translate_every_live_family':
                need(len(cleaned) == 16 and all(protected[r] == 0 for r in range(16)), 'All original first pairs return before endpoint correction')
                schedule.append({'op': 'positive_X_lines', 'replicas': list(range(16)), 'pair': 0,
                                 'ports': list(range(112)), 'rank': 1})
            schedule.append({'op': 'retained_event', 'old_event': at})
        row = donors['rows'][replica] if replica is not None else None
        if row is not None and at == row['capture_after_event']:
            need(kind == 'local_cover_sweep' and event['stage'] == 0, 'Capture after actual F0')
            schedule += donor_block(replica, 'capture')
            schedule.append({'op': 'call_procedure', 'name': 'capture', 'bindings': bindings(replica, 0)})
            schedule += donor_block(replica, 'return')
            captured.add(replica)
            live.add(replica)
            peak = max(peak, 8*len(live))
        if row is not None and at == row['repair_after_event']:
            need(replica in captured and kind == 'local_cover_sweep' and event['stage'] == 1, 'Repair after actual B1')
            schedule += adapter_block(replica, 0)
            schedule += donor_block(replica, 'capture')
            schedule.append({'op': 'call_procedure', 'name': 'repair', 'bindings': bindings(replica, 0)})
            schedule += donor_block(replica, 'return')
            protected[replica] = 0
        if row is not None and at == row['cleanup_after_event']:
            need(kind == 'idle_cover_sweep' and event['source_event'] == 5 and levels[replica, 1] == 2, 'Actual delayed full-U2 cut')
            need(protected[replica] == 1, 'The whole coded pair is in the idle bank')
            schedule += adapter_block(replica, 1)
            schedule += donor_block(replica, 'capture')
            schedule.append({'op': 'call_procedure', 'name': 'cleanup', 'bindings': bindings(replica, 1)})
            schedule += donor_block(replica, 'return')
            schedule += adapter_block(replica, 2)
            cleaned.add(replica)
            live.remove(replica)
            intervals.append([replica, row['capture_after_event'], row['repair_after_event'], at])
    need(not live and len(cleaned) == 16, 'Every donor use ends')
    need(sum(event['op'] == 'physical_pair_swap' for event in schedule) == 96, 'All six pair swaps per replica')
    need(sorted(event['old_event'] for event in schedule if 'old_event' in event) == list(range(482)),
         'Every old event has one retained or replacement entry')
    bills = {name: price(word) for name, word in procedures.items()}
    need(bills['capture']['scalar_allowance']+bills['repair']['scalar_allowance'] == 20322, 'Dirty repair scalar bill')
    need(bills['cleanup']['scalar_allowance'] == 23780, 'One-C erase scalar bill')
    profile = Counter()
    scalar = maps = bridge_scalar = translations = standalone = 0
    for event in schedule:
        op = event['op']
        if op == 'call_procedure':
            word = procedures[event['name']]
            scalar += bills[event['name']]['scalar_allowance']
            maps += bills[event['name']]['cover_maps']
            profile.update(e['rank'] for e in word if e['op'] in ('line', 'stage'))
        elif op == 'native_adapter':
            recipe = event['recipe']
            if recipe['axes']:
                profile[len(recipe['axes'])] += 1
            translations += int(recipe['translation'] != 0)
            standalone += int(recipe['translation'] != 0 and not recipe['axes'])
        elif op == 'positive_X_lines':
            profile[1] += len(event['replicas'])*len(event['ports'])
        elif op == 'donor_cover_map':
            maps += 1
        elif op == 'physical_pair_swap':
            bridge_scalar += 2*len(event['ports'])*(3*8+2)
    invoice = {'added_native_profile': dict(sorted(profile.items())),
               'added_native_mass': sum(rank*count for rank, count in profile.items()),
               'added_native_wrappers': 2*sum(profile.values()),
               'ordinary_and_donor_cover_maps': maps,
               'local_scalar_allowance': scalar,
               'full_modified_bridge_scalar_allowance': bridge_scalar,
               'added_owned_record_families': 0, 'distinct_borrowed_donors': 128,
               'peak_borrowed_donors': peak, 'reused_old_owned_C_field': 14336,
               'new_adapter_translation_components': translations,
               'standalone_adapter_translation_maps': standalone}
    need(invoice['added_native_mass'] == 3798 and invoice['added_native_wrappers'] == 7582
         and invoice['ordinary_and_donor_cover_maps'] == 8192 and invoice['local_scalar_allowance'] == 705632, 'Complete added component counts')
    packet = {'schema': 'exact_procedure_table_and_owner_schedule_v1', 'procedures': procedures,
              'schedule': schedule, 'source_pins': {name: digest for name, (_, digest) in PINS.items()},
              'scope': 'Full-W first-pair retirement with arbitrary borrowed records. Other outputs and new recursive child hosting are not proved.'}
    args.out.mkdir(parents=True, exist_ok=True)
    payload = encoded(packet)
    (args.out / 'DIRTY-CONSUMER-WORD.json').write_bytes(payload)
    result = {'status': 'PASS_TWO_CUT_DIRTY_RECORD_CONSUMER', 'source_pins': packet['source_pins'],
              'word_sha256': sha256(payload).hexdigest(), 'all_local_output_rows_sha256': local_hash,
              'local_data_columns': 224, 'arbitrary_donor_columns': 8, 'arbitrary_owned_C_columns': 1,
              'inherited_helper_columns': 480, 'raw_completed_first_pair_outputs': 3584,
              'original_schedule_events': 482, 'record_intervals': intervals,
              'procedure_invoices': bills, 'component_invoice': invoice, 'negative_controls': controls,
              'inherited_premises': ['Exact QQ16 F0/B1 source and complete arbitrary helper contracts',
                                     'Whole-pair common-F consumer and final raw-X line correction',
                                     'Pinned two-cut native owner transport and phase identities'],
              'not_proved': ['New recursive child workspace hosting', 'Other three-pair output map',
                             'Complete scalar/native stream and control invoice', 'Rounding and recursive precision',
                             'Complete supplier or kappa change']}
    (args.out / 'DIRTY-CONSUMER.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': result['status'], 'component_invoice': invoice}, sort_keys=True))


if __name__ == '__main__':
    main()
