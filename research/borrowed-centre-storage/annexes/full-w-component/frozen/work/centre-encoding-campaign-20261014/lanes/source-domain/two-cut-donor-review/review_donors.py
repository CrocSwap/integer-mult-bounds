"""Review the fixed two-cut donor certificate from source data only."""

import argparse
from bisect import bisect_left
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
import tarfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LANES = HERE.parents[1]
PRODUCER = LANES / 'portable-source-codes/dirty-record-hosting-20261015'
ARCHIVE = ROOT / 'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
MANIFEST_PIN = 'bae5f1cb0f3738b7246be3e26f88c8c872a0e17cf4054b527dc74d25cf2837b0'
MEMBERS = {
    'template': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz', '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
    'phases': ('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json', 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
    'word': ('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz', '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
}
PREMISES = {
    'interface-proof/ORIGINAL-COMPLEX-MODES-REVIEW.json': '8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d',
    'portable-source-codes/common-f-independent-review-20261015/REVIEW.json': 'a930a9cda3f573f16b59d4538bc2920d9d22a8ba0e74e4a0e5ad6ce926a16fef',
    'portable-source-codes/common-f-review-20261015/CONSUMER-MANIFEST.json': 'ca8f0cad4f445a8a13215a91b49f9cbfa9eb872e2bfed6b52feccdb948174419',
    'residual-syndrome/physical-algebra/eight-record-review-20261015/REVIEW.json': '17b03e51d1a3ca9a8628bfcebc4e8b52208a77741ce2d7ed8c62cf89d57605b4',
    'residual-syndrome/physical-algebra/eight-record-review-20261015/DELAYED-CLEANUP-MANIFEST.json': 'b23074aa39523c88da7fe5c27e26e63b2ffc36567762105e55ffad15999da405',
    'residual-syndrome/physical-algebra/review-gauss/delayed-dirty-cleanup/REVIEW.json': '74f7f7e2dd1eb4c36762b315f32b8a2462a9ab5dcd44d7378adea5a5a29ed993',
    'portable-source-codes/dirty-record-hosting-20261015/eight-records/EIGHT-RECORD-WORDS.json': '8dcb0f29d2b0275e5d5395511d10451b8675c9ffe37ebdbd452c0132a17b15f4',
    'residual-syndrome/physical-algebra/eight-record-review-20261015/DELAYED-CLEANUP-ONE-C-WORD.json': 'bddba461c6f06213c7ab938d24993ac6d5ea44169f9705594227acfdc5b6e880',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def checked(path, expected):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == expected, 'Pin: ' + str(path))
    return raw


def owner(replica, pair, side, port):
    return 896 * replica + 224 * pair + 112 * side + port


def parity(value):
    return value.bit_count() & 1


def act(columns, vector):
    result = 0
    while vector:
        low = vector & -vector
        result ^= columns[low.bit_length() - 1]
        vector ^= low
    return result


def inverse_check(columns, inverse):
    need(len(columns) == len(inverse) == 73, '73-axis map shape')
    for i in range(73):
        need(act(columns, inverse[i]) == act(inverse, columns[i]) == 1 << i,
             'Both inverse map orders')
        for j in range(73):
            need(parity(columns[i] & columns[j]) == int(i == j), 'Orthogonal map')


def signature(terms):
    """Use separate linear coefficients and quadratic adjacency rows."""
    linear = [0] * 73
    edges = [0] * 73
    for vector, coefficient in terms:
        for i in range(73):
            if vector >> i & 1:
                linear[i] = (linear[i] + coefficient) % 4
                if coefficient % 2:
                    edges[i] ^= vector & ((1 << i) - 1)
    return tuple(linear), tuple(edges)


def serialized_signature(value):
    low, high, cross = value
    return (tuple(((low >> i) & 1) + 2 * ((high >> i) & 1) for i in range(73)),
            tuple((cross >> (i * (i - 1) // 2)) & ((1 << i) - 1) for i in range(73)))


def zero(terms):
    linear, edges = signature(terms)
    return not any(linear) and not any(edges)


def witness(terms):
    linear, edges = signature(terms)
    for i, value in enumerate(linear):
        if value:
            return 1 << i, value
    for i, row in enumerate(edges):
        if row:
            bit = row & -row
            return (1 << i) | bit, 2
    raise ValueError('Expected a nonzero phase witness')


def path_terms(path):
    return [(v, 1) for row in path for v in row['axes']] + [(row['translation'], 2) for row in path]


def read_source():
    checked(ARCHIVE, 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6')
    source = {}
    with tarfile.open(ARCHIVE) as stream:
        for name, (member, pin) in MEMBERS.items():
            raw = stream.extractfile(member).read()
            need(sha256(raw).hexdigest() == pin, 'Archive member pin')
            source[name] = json.loads(gzip.decompress(raw) if member.endswith('.gz') else raw)
    return source


def reconstruct(source):
    template, recipes, word = source['template'], source['phases']['recipes'], source['word']
    events, calls = template['execution_schedule'], template['calls']
    need(len(events) == 482 and len(calls) == 144, 'Selected schedule size')
    call_at, deadline, pair_uses = {}, {}, defaultdict(list)
    barriers = [set() for _ in range(14336)]
    histories = [[] for _ in range(14336)]
    new_cleanup = []
    for at, event in enumerate(events):
        kind = event['kind']
        replica = event.get('replica')
        if kind == 'local_cover_sweep':
            call = calls[event['time']]
            call_at[event['time']] = at
            need((call['replica'], call['stage']) == (replica, event['stage']), 'Actual call identity')
            need(len(call['owners']) == len({f for f, route in call['owners']}) == 704, 'Whole-call owner uniqueness')
            need(all(0 <= f < 14336 for f, route in call['owners']), 'Private field used as an old helper')
            pair_uses[replica, call['pair']].append(at)
            for side in (0, 1):
                for port in range(112):
                    f = owner(replica, call['pair'], side, port)
                    need(call['owners'][112*side+port] == [f, [1, call['stage'], port]], 'Active owner address')
                    barriers[f].add(at)
        elif kind == 'bridge':
            for pair in (event['src'], event['dst']):
                pair_uses[replica, pair].append(at)
                for side in (0, 1):
                    for port in range(112):
                        barriers[owner(replica, pair, side, port)].add(at)
        elif kind == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                need((replica, child) not in deadline, 'Repeated idle deadline')
                deadline[replica, child] = (at, event['pair'], side)
                for port in range(112):
                    f = owner(replica, event['pair'], side, port)
                    histories[f].append({'event': at, 'kind': 'translation', 'index': child,
                        'axes': [], 'translation': recipes[port]['idle_children'][child]['translation_after']})
            if event['source_event'] == 5:
                need(event['pair'] == 1, 'Full-W cleanup location')
                new_cleanup.append(at)
                for side in (0, 1):
                    for port in range(112):
                        barriers[owner(replica, 1, side, port)].add(at)
        elif kind in ('terminal', 'terminal_Y_translations'):
            # This conservative barrier includes both sides for a Y translation.
            for f in range(896*replica, 896*(replica+1)):
                barriers[f].add(at)
        else:
            need(kind in ('bank_padding_cover_sweep', 'translate_every_live_family'), 'Unknown selected event')
            if kind == 'bank_padding_cover_sweep':
                need(event['families'] == [14336, 14336], 'Nonempty padding needs a donor history')
            else:
                need(at == 481, 'Final cover correction timing')
    need(len(new_cleanup) == 16, 'Sixteen new full-W cleanup writes')
    partition = defaultdict(dict)
    helper_roles = set()
    for index, job in enumerate(template['hosting']['pooled_slots']):
        at, pair, side = deadline[job['owner_replica'], job['child']]
        f = owner(job['owner_replica'], pair, side, job['port'])
        need(f == job['family'], 'Helper family from its deadline')
        role = 224 + job['helper']
        need((job['time'], role) not in helper_roles, 'Repeated local helper role')
        helper_roles.add((job['time'], role))
        width = len(word['frames'][word['final'][role]]) - len(word['frames'][word['start'][role]])
        need(width == job['width'], 'Complete canonical helper width')
        release_list = pair_uses[job['owner_replica'], pair]
        previous = bisect_left(release_list, at)
        release = release_list[previous-1] if previous else -1
        need(release < call_at[job['time']] < at, 'Strict old helper window')
        child = recipes[job['port']]['idle_children'][job['child']]
        axes = child['orthogonal_axes'][job['offset']:job['offset']+width]
        need(len(axes) == width, 'Helper native axis slice')
        start = 1 + 8*(events[at]['from_level']+1) + job['offset']
        spectator = [j for j in range(73) if j not in range(start, start+width)][:9-width]
        route = [3, job['child'], job['offset']] if width == 9 else [4, job['child'], job['offset'], width, spectator]
        need(calls[job['time']]['owners'][role] == [f, route], 'Literal helper owner route')
        key = job['owner_replica'], job['child'], job['port']
        for offset in range(job['offset'], job['offset']+width):
            need(offset not in partition[key], 'Repeated pending native axis')
            partition[key][offset] = ('helper', index)
        histories[f].append({'event': call_at[job['time']], 'kind': 'helper', 'index': index,
                            'axes': axes, 'translation': 0})
    need(len(helper_roles) == 144*480, 'All local helper roles')
    for index, job in enumerate(template['idle_children']):
        at, pair, side = deadline[job['replica'], job['child']]
        f = owner(job['replica'], pair, side, job['port'])
        child = recipes[job['port']]['idle_children'][job['child']]
        axes = child['orthogonal_axes'][job['pending_offset']:]
        need(f == job['family'] and len(axes) == job['rank'], 'Idle suffix family and rank')
        key = job['replica'], job['child'], job['port']
        for offset in range(job['pending_offset'], len(child['orthogonal_axes'])):
            need(offset not in partition[key], 'Suffix overlaps a helper job')
            partition[key][offset] = ('suffix', index)
        histories[f].append({'event': at, 'kind': 'suffix', 'index': index, 'axes': axes, 'translation': 0})
    for (replica, child), (at, pair, side) in deadline.items():
        for port in range(112):
            need(set(partition[replica, child, port]) == set(range(recipes[port]['idle_children'][child]['rank'])),
                 'Incomplete old native partition')
    for history in histories:
        history.sort(key=lambda row: (row['event'], row['kind'] == 'translation', row['index']))
    return histories, barriers, {'old_helper_jobs': len(helper_roles),
        'old_idle_suffixes': len(template['idle_children']), 'complete_pending_partitions': len(partition),
        'old_events': len(events), 'new_cleanup_cuts': new_cleanup}


def audit_allocation(name, allocation, packet, source, histories, barriers):
    events = source['template']['execution_schedule']
    records = allocation['selected']
    need(len(records) == 128 and [r['role'] for r in records] == list(range(128)), 'Eight records per replica')
    need(len({r['family'] for r in records}) == 128, 'Global donor distinctness')
    profile, inherited, per_replica = Counter(), Counter(), Counter()
    wrappers = translations = separate = inherited_jobs = 0
    overlap = Counter()
    cut_records, controls = [], []
    for row in records:
        replica, selected = divmod(row['role'], 8)
        family = row['family']
        need(0 <= family < 14336, 'Donor is an old productive field')
        if name == 'pair23':
            need(family//224 % 4 in (2, 3), 'Restricted alternative pair')
        cuts = [next(at for at, event in enumerate(events) if event['kind'] == 'local_cover_sweep'
                     and event['replica'] == replica and event['stage'] == stage) for stage in (0, 1)]
        cuts.append(next(at for at, event in enumerate(events) if event['kind'] == 'idle_cover_sweep'
                         and event['replica'] == replica and event['source_event'] == 5))
        entry = packet['rows'][replica]
        need(cuts == [entry['capture_after_event'], entry['repair_after_event'], entry['cleanup_after_event']], 'Three actual cuts')
        low, middle, high = cuts
        need(low < middle < high < 481, 'Ordered cuts before the final cover correction')
        need(not any(low < at <= high for at in barriers[family]), 'Donor scalar or active contamination')
        path = [[job for job in histories[family] if a < job['event'] <= b]
                for a, b in ((low, middle), (middle, high))]
        need(path == row['paths'], 'Complete actual donor path')
        flat = [v for part in path for job in part for v in job['axes']]
        need(len(flat) == len(set(flat)), 'Repeated donor line')
        need(all(parity(a & b) == int(i == j) for i, a in enumerate(flat) for j, b in enumerate(flat)), 'Orthogonal donor path')
        ranks = [sum(len(job['axes']) for job in part) for part in path]
        need(ranks == row['ranks'], 'Both interval ranks')
        need(2*max(sum(max(r-8, 0) for r in ranks), sum(max(8-r, 0) for r in ranks)) == row['minimum_adapter_mass'],
             'Fixed-basis adapter bound')
        wanted = row['desired_axes']
        need(list(map(len, wanted)) == [8, 8] and not set(wanted[0]) & set(wanted[1]), 'Disjoint desired advances')
        inverse_check(row['U_columns'], row['U_inverse_columns'])
        need([row['U_columns'][i] for i in range(9, 17)] == wanted[0] and
             [row['U_columns'][i] for i in range(17, 25)] == wanted[1], 'Same cover map at both cuts')
        terms = [path_terms(part) for part in path]
        desired = [[(v, 1) for v in part] for part in wanted]
        adapter_terms = []
        mass = 0
        for index, adapter in enumerate(row['adapters']):
            axes, translation = adapter['axes'], adapter['translation']
            term = [(v, 1) for v in axes] + [(translation, 2)]
            need(signature(term) == serialized_signature(adapter['phase']), 'Serialized adapter phase')
            adapter_terms.append(term)
            mass += len(axes)
            if axes:
                inverse_check(adapter['left_columns'], adapter['right_columns'])
                need(adapter['left_columns'][:len(axes)] == axes, 'Native child wrapper axes')
                profile[len(axes)] += 1
                wrappers += 2
            else:
                need('left_columns' not in adapter and 'right_columns' not in adapter, 'Empty native wrapper')
            translations += bool(translation)
            separate += bool(translation and not axes)
        need(mass == row['minimum_adapter_mass'], 'All three adapter ranks')
        for side in (0, 1):
            difference = terms[side] + adapter_terms[side] + [(v, -c) for v, c in desired[side]]
            need(zero(difference), 'Exact phase at a required intermediate cut')
        need(zero(desired[0] + desired[1] + adapter_terms[2] +
                  [(v, -c) for part in terms for v, c in part]), 'Exact arbitrary donor return')
        # This is the combined old-input operator after local cleanup.
        need(zero(terms[0] + adapter_terms[0] + terms[1] + adapter_terms[1] + adapter_terms[2] +
                  [(v, -c) for part in terms for v, c in part]), 'Complete baseline restoration')
        for index in range(3):
            if not zero(adapter_terms[index]) and not any(c['mutation'] == 'omit_adapter_'+str(index) for c in controls):
                character, error = witness([(v, -c) for v, c in adapter_terms[index]])
                controls.append({'mutation': 'omit_adapter_'+str(index), 'role': row['role'],
                                 'character': character, 'phase_error_mod4': error})
        need(not zero(desired[0] + [(v, -c) for v, c in desired[1]]), 'Two-cut interchange control')
        inverse_first = [(row['U_inverse_columns'][i], 1) for i in range(9, 17)]
        if not zero(inverse_first + [(v, -c) for v, c in desired[0]]) and not any(c['mutation'] == 'reverse_cover_map' for c in controls):
            character, error = witness(inverse_first + [(v, -c) for v, c in desired[0]])
            controls.append({'mutation': 'reverse_cover_map', 'role': row['role'],
                             'character': character, 'phase_error_mod4': error})
        for part in path:
            for job in part:
                if job['axes']:
                    inherited[len(job['axes'])] += 1
                    inherited_jobs += 1
        per_replica[replica] += mass
        for cut in range(low, high):
            overlap[cut] += 1
        cut_records.append({'role': row['role'], 'family': family, 'cuts': cuts,
                            'ranks': ranks, 'adapter_mass': mass})
    summary = {'profile': dict(sorted(profile.items())), 'mass': sum(r*c for r, c in profile.items()),
               'native_wrappers': wrappers, 'translations': translations,
               'standalone_translation_maps': separate, 'record_cover_maps': 6*128,
               'inherited_profile': dict(sorted(inherited.items())),
               'inherited_mass': sum(r*c for r, c in inherited.items())}
    need({control['mutation'] for control in controls} ==
         {'omit_adapter_0', 'omit_adapter_1', 'omit_adapter_2', 'reverse_cover_map'}, 'Four exact phase controls')
    for key, value in summary.items():
        original = allocation[key]
        if isinstance(value, dict):
            original = {int(k): v for k, v in original.items()}
        need(value == original, 'Allocation invoice: ' + key)
    summary.update({'distinct_families': 128, 'peak_live_records': max(overlap.values()),
                    'peak_after_event': min(k for k, v in overlap.items() if v == max(overlap.values())),
                    'per_replica_mass': [per_replica[i] for i in range(16)],
                    'inherited_whole_jobs': inherited_jobs, 'cut_records': cut_records,
                    'negative_controls': controls + [{'mutation': 'interchange_cut_advances', 'detected': True}]})
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(checked(PRODUCER/'TWO-CUT-MANIFEST.json', MANIFEST_PIN))
    for name, pin in manifest['files'].items():
        checked(PRODUCER/name, pin)
    for name, pin in PREMISES.items():
        checked(LANES/name, pin)
    local = json.loads((PRODUCER/'eight-records/EIGHT-RECORD-WORDS.json').read_text())['dirty_eight_A_before_cleanup']
    selected_ports = [0, 7, 20, 27, 36, 46, 57, 111]
    need(local['capture'] == [{'c': '1', 'dst': 'R'+str(p), 'op': 'add', 'src': 'X'+str(p)} for p in selected_ports],
         'Literal dirty capture without CLEAR')
    stages = [{'field': 'R'+str(p), 'op': 'stage', 'rank': 8, 'sign': 1, 'stage': 1} for p in selected_ports]
    need(local['repair'][:8] == stages and not any(e['op'] == 'stage' for e in local['repair'][8:]),
         'Exactly eight replaced record advances')
    cleanup = json.loads((LANES/'residual-syndrome/physical-algebra/eight-record-review-20261015/DELAYED-CLEANUP-ONE-C-WORD.json').read_text())['cleanup']
    for event in local['repair'][8:] + cleanup:
        for key in ('src', 'dst', 'field'):
            if key in event:
                field = event[key]
                need(field == 'C' or (field[0] in 'XYR' and field[1:].isdigit()), 'Boundary word accesses an old helper role')
        if event['op'] == 'clear':
            need(event['field'] == 'C', 'Borrowed donor CLEAR')
    need(sum(e['op'] == 'line' for e in local['repair']) == 112, 'Remaining positive Y lines')
    need(not any(e['op'] in ('line', 'stage', 'native') for e in cleanup), 'Cleanup native charge')
    packet = json.loads((PRODUCER/'TWO-CUT-DONORS.json').read_text())
    need(packet['status'] == 'PASS_TWO_CUT_DONOR_CENSUS', 'Producer status')
    source = read_source()
    histories, barriers, counts = reconstruct(source)
    census = []
    for entry in packet['rows']:
        low, middle, high = [entry[k] for k in ('capture_after_event', 'repair_after_event', 'cleanup_after_event')]
        histogram = Counter()
        for f in range(14336):
            if any(low < at <= high for at in barriers[f]):
                continue
            ranks = tuple(sum(len(job['axes']) for job in histories[f] if a < job['event'] <= b)
                          for a, b in ((low, middle), (middle, high)))
            histogram[ranks] += 1
        expected = {tuple(map(int, key.split(','))): count for key, count in entry['rank_histogram'].items()}
        need(histogram == expected and sum(histogram.values()) == entry['candidate_count'], 'Complete bounded donor census')
        census.append({'replica': entry['replica'], 'candidate_count': sum(histogram.values()),
                       'exact_eight_plus_eight_count': histogram[8, 8]})
    results = {name: audit_allocation(name, allocation, packet, source, histories, barriers)
               for name, allocation in packet['allocations'].items()}
    need(results['all']['profile'] == {1: 200, 2: 7} and results['all']['mass'] == 214, 'Primary native profile')
    need(results['all']['native_wrappers'] == 414 and results['all']['translations'] == 107 and
         results['all']['standalone_translation_maps'] == 0, 'Primary map counts')
    result = {'status': 'PASS_INDEPENDENT_TWO_CUT_DONOR_REVIEW',
              'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'producer_manifest_sha256': MANIFEST_PIN, 'producer_files': manifest['files'],
              'archive_members': MEMBERS, 'accepted_premises': PREMISES,
              'source_reconstruction': counts, 'bounded_census': census, 'allocations': results,
              'boundary_word_checks': {'source_ports': selected_ports, 'record_native_advances_replaced_per_replica': 8,
                  'retained_positive_Y_lines_per_replica': 112, 'boundary_old_helper_role_references': 0,
                  'borrowed_donor_CLEARs': 0, 'cleanup_new_native_children': 0},
              'primary_conditional_complete_added_native_profile': {'1': 200+16*224, '2': 7},
              'primary_conditional_complete_added_native_mass': 214+16*224,
              'producer_imported_or_executed': False,
              'scope': 'Fixed old-owner allocation and exact two-cut native transport. Local repair and full-W cleanup are pinned premises. New recursive child hosting, stream/precision invoice, other data outputs and supplier gain remain open.'}
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])
    print(json.dumps({'source': counts, 'primary': {k: results['all'][k] for k in
          ('profile', 'mass', 'native_wrappers', 'translations', 'record_cover_maps', 'peak_live_records', 'inherited_whole_jobs')}}))


if __name__ == '__main__':
    main()
