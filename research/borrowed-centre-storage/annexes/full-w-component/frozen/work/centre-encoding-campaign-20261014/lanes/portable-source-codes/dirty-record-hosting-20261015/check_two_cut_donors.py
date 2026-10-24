"""Check two-cut dirty donor paths in the pinned owner schedule.

Use complete helper jobs. Keep arbitrary donor values. This file does
not prove the delayed data consumer or the new child hosting contract.
"""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent / 'common-f-independent-review-20261015/review_followthrough.py'
PIN = 'c0dba20c069fa72c4d50df808649110b9b18c660c6e43efdea041fc5bca8d647'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if sha256(REVIEW.read_bytes()).hexdigest() != PIN:
        raise ValueError('Review source pin')
    spec = importlib.util.spec_from_file_location('source_review', REVIEW)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    data = m.source_data()
    _, _, partition = m.prepare_jobs(data)
    template = data['template']
    recipes = data['phases']['recipes']
    events, calls = template['execution_schedule'], template['calls']
    position = {e['time']: i for i, e in enumerate(events) if e['kind'] == 'local_cover_sweep'}
    deadlines = {(e['replica'], child): i for i, e in enumerate(events)
                 if e['kind'] == 'idle_cover_sweep' for child in e['child_indices']}
    histories = defaultdict(list)
    for index, job in enumerate(template['hosting']['pooled_slots']):
        child = recipes[job['port']]['idle_children'][job['child']]
        axes = child['orthogonal_axes'][job['offset']:job['offset']+job['width']]
        histories[job['family']].append({'event': position[job['time']], 'kind': 'helper',
                                        'index': index, 'axes': axes, 'translation': 0})
    for index, job in enumerate(template['idle_children']):
        child = recipes[job['port']]['idle_children'][job['child']]
        axes = child['orthogonal_axes'][job['pending_offset']:]
        histories[job['family']].append({'event': deadlines[job['replica'], job['child']],
                                        'kind': 'suffix', 'index': index,
                                        'axes': axes, 'translation': 0})
    touches = defaultdict(set)
    for at, e in enumerate(events):
        kind = e['kind']
        if kind == 'local_cover_sweep':
            for family, _ in calls[e['time']]['owners'][:224]:
                touches[family].add(at)
        elif kind == 'idle_cover_sweep':
            for side, child in enumerate(e['child_indices']):
                for port in range(112):
                    family = m.family(e['replica'], e['pair'], side, port)
                    histories[family].append({'event': at, 'kind': 'translation', 'index': child,
                                              'axes': [], 'translation': recipes[port]['idle_children'][child]['translation_after']})
        elif kind == 'bridge':
            for pair in (e['src'], e['dst']):
                for side in range(2):
                    for port in range(112):
                        touches[m.family(e['replica'], pair, side, port)].add(at)
        elif kind in ('terminal', 'terminal_Y_translations'):
            for family in range(896*e['replica'], 896*(e['replica']+1)):
                touches[family].add(at)
    for family in histories:
        histories[family].sort(key=lambda row: (row['event'], row['kind'] == 'translation'))

    # The proposed full-W erase writes the parked pair at this idle cut.
    # These are new scalar uses. The donor census must exclude them.
    for at, e in enumerate(events):
        if e['kind'] == 'idle_cover_sweep' and e['source_event'] == 5:
            for side in range(2):
                for port in range(112):
                    touches[m.family(e['replica'], 1, side, port)].add(at)

    rows = []
    for replica in range(16):
        low, cut = [next(i for i, e in enumerate(events) if e['kind'] == 'local_cover_sweep'
                        and e['replica'] == replica and e['stage'] == stage) for stage in (0, 1)]
        high = next(i for i, e in enumerate(events) if e['kind'] == 'idle_cover_sweep'
                    and e['replica'] == replica and e['source_event'] == 5)
        candidates = []
        for family in range(14336):
            if any(low < at <= high for at in touches[family]):
                continue
            parts = [[row for row in histories[family] if a < row['event'] <= b]
                     for a, b in ((low, cut), (cut, high))]
            axes = [[v for row in part for v in row['axes']] for part in parts]
            flat = axes[0]+axes[1]
            m.need(len(flat) == len(set(flat)), 'No repeated donor native axis')
            m.need(all((a & b).bit_count() % 2 == int(i == j)
                       for i, a in enumerate(flat) for j, b in enumerate(flat)), 'Orthogonal donor paths')
            ranks = list(map(len, axes))
            extra = sum(max(r-8, 0) for r in ranks)
            missing = sum(max(8-r, 0) for r in ranks)
            candidates.append({'family': family, 'ranks': ranks,
                               'minimum_adapter_mass': 2*max(extra, missing),
                               'paths': parts})
        candidates.sort(key=lambda row: (row['minimum_adapter_mass'], row['family']))
        safe = [row for row in candidates if (row['family']//224) % 4 in (2, 3)]
        histogram = Counter(tuple(row['ranks']) for row in candidates)
        rows.append({'replica': replica, 'capture_after_event': low, 'repair_after_event': cut,
                     'cleanup_after_event': high, 'candidate_count': len(candidates),
                     'zero_adapter_count': sum(row['minimum_adapter_mass'] == 0 for row in candidates),
                     'safe_zero_adapter_count': sum(row['minimum_adapter_mass'] == 0 for row in safe),
                     'best_mass': candidates[0]['minimum_adapter_mass'],
                     'safe_best_mass': safe[0]['minimum_adapter_mass'],
                     'rank_histogram': {','.join(map(str, key)): value for key, value in sorted(histogram.items())},
                     'best_candidates': candidates[:256], 'safe_best_candidates': safe[:256]})

    # Distinct families are sufficient. This does not rely on interval reuse.
    allocations = {}
    for name, field in [('all', 'best_candidates'), ('pair23', 'safe_best_candidates')]:
        for bound in range(0, 33, 2):
            selected = {}
            candidates = {8*row['replica']+k: [r['family'] for r in row[field]
                          if r['minimum_adapter_mass'] <= bound] for row in rows for k in range(8)}

            def augment(role, seen):
                for family in candidates[role]:
                    if family in seen:
                        continue
                    seen.add(family)
                    if family not in selected or augment(selected[family], seen):
                        selected[family] = role
                        return True
                return False

            if all(augment(role, set()) for role in range(128)):
                allocation = []
                profile = Counter()
                inherited_profile = Counter()
                maps = translations = standalone_translations = 0
                for family, role in sorted(selected.items(), key=lambda item: item[1]):
                    replica, k = divmod(role, 8)
                    row = next(r for r in rows[replica][field] if r['family'] == family)
                    recipe = recipes[family % 112]
                    basis = [recipe['q']]+recipe['idle_children'][0]['orthogonal_axes'][:8]+[1 << i for i in range(9, 73)]
                    actual = [set(v for job in part for v in job['axes']) for part in row['paths']]
                    wanted = [set(sorted(part, key=basis.index)[:8]) for part in actual]
                    for side in (0, 1):
                        spare = sorted(actual[1-side]-wanted[1-side], key=basis.index)
                        wanted[side].update(spare[:8-len(wanted[side])])
                    unused = [v for v in basis if v not in actual[0] | actual[1]]
                    for side in (0, 1):
                        take = 8-len(wanted[side])
                        wanted[side].update(unused[:take])
                        del unused[:take]
                    m.need(len(wanted[0]) == len(wanted[1]) == 8 and not wanted[0] & wanted[1], 'Two disjoint desired advances')
                    shift = []
                    for part in row['paths']:
                        value = 0
                        for job in part:
                            value ^= job['translation']
                        shift.append(value)

                    def adapter(positive, negative, translation):
                        axes = sorted(positive ^ negative, key=basis.index)
                        for v in negative-positive:
                            translation ^= v
                        return {'axes': axes, 'translation': translation,
                                'phase': list(m.polynomial(tuple((v, 1) for v in axes)+((translation, 2),)))}

                    adapters = [adapter(wanted[s], actual[s], shift[s]) for s in (0, 1)]
                    adapters.append(adapter(actual[0] | actual[1], wanted[0] | wanted[1], shift[0] ^ shift[1]))
                    native = [m.polynomial(tuple((v, 1) for v in actual[s])+((shift[s], 2),)) for s in (0, 1)]
                    desired = [m.polynomial(tuple((v, 1) for v in wanted[s])) for s in (0, 1)]
                    m.need(all(m.phase_sum(native[s], tuple(adapters[s]['phase'])) == desired[s] for s in (0, 1)), 'Exact phase at both repair cuts')
                    m.need(m.phase_sum(m.phase_sum(*desired), tuple(adapters[2]['phase'])) == m.phase_sum(*native), 'Exact donor restoration phase')
                    mass = sum(len(a['axes']) for a in adapters)
                    m.need(mass == row['minimum_adapter_mass'], 'Constructive adapter bound')
                    for a in adapters:
                        if a['axes']:
                            profile[len(a['axes'])] += 1
                            maps += 2
                            a['left_columns'] = a['axes']+[v for v in basis if v not in a['axes']]
                            a['right_columns'] = [sum(((v >> i) & 1) << j for j, v in enumerate(a['left_columns'])) for i in range(73)]
                            m.need(all((a['left_columns'][i] & a['left_columns'][j]).bit_count() % 2 == int(i == j)
                                       for i in range(73) for j in range(73)), 'Canonical native adapter isometry')
                        translations += int(a['translation'] != 0)
                        standalone_translations += int(a['translation'] != 0 and not a['axes'])
                    for part in row['paths']:
                        for job in part:
                            if job['axes']:
                                inherited_profile[len(job['axes'])] += 1
                    source_indices = list(range(9, 25))+list(range(9))+list(range(25, 73))
                    target_axes = sorted(wanted[0], key=basis.index)+sorted(wanted[1], key=basis.index)+[v for v in basis if v not in wanted[0] | wanted[1]]
                    columns = [0]*73
                    for index, vector in zip(source_indices, target_axes):
                        columns[index] = vector
                    m.need(all((a & b).bit_count() % 2 == int(i == j) for i, a in enumerate(columns) for j, b in enumerate(columns)), 'One exact orthogonal cover map')
                    allocation.append({'role': role, **row, 'U_columns': columns,
                                       'U_inverse_columns': [sum(((v >> i) & 1) << j for j, v in enumerate(columns)) for i in range(73)],
                                       'desired_axes': [sorted(part, key=basis.index) for part in wanted],
                                       'adapters': adapters})
                allocations[name] = {'maximum_adapter_mass': bound, 'profile': dict(sorted(profile.items())),
                                     'mass': sum(rank*count for rank, count in profile.items()),
                                     'native_wrappers': maps, 'translations': translations,
                                     'standalone_translation_maps': standalone_translations,
                                     'record_cover_maps': 6*128,
                                     'inherited_profile': dict(sorted(inherited_profile.items())),
                                     'inherited_mass': sum(rank*count for rank, count in inherited_profile.items()),
                                     'selected': allocation}
                break
        m.need(name in allocations, 'Distinct donor allocation')
    controls = []
    for index, label in [(0, 'drop_first_cut_adapter'), (1, 'drop_second_cut_adapter'),
                         (2, 'drop_donor_restoration')]:
        witness = next(row for row in allocations['all']['selected'] if row['adapters'][index]['phase'] != [0, 0, 0])
        m.need(tuple(witness['adapters'][index]['phase']) != (0, 0, 0), label)
        controls.append({'mutation': label, 'role': witness['role'], 'detected_phase': witness['adapters'][index]['phase']})
    witness = allocations['all']['selected'][0]
    first = m.polynomial(tuple((v, 1) for v in witness['desired_axes'][0]))
    second = m.polynomial(tuple((v, 1) for v in witness['desired_axes'][1]))
    m.need(first != second, 'Interchanged cut advances fail')
    controls.append({'mutation': 'interchange_two_cut_assignments', 'role': witness['role'],
                     'first_phase': list(first), 'wrong_phase': list(second)})
    output = {'status': 'PASS_TWO_CUT_DONOR_CENSUS', 'source_review_sha256': PIN,
              'scope': 'Native path and conditional adapter count only; no delayed consumer or new child hosting.',
              'partition': partition, 'rows': rows, 'allocations': allocations, 'negative_controls': controls}
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': output['status'], 'zero_adapter_counts': [r['zero_adapter_count'] for r in rows],
                      'safe_zero_adapter_counts': [r['safe_zero_adapter_count'] for r in rows],
                      'best_masses': [r['best_mass'] for r in rows],
                      'safe_best_masses': [r['safe_best_mass'] for r in rows],
                      'allocations': {name: {key: value for key, value in packet.items() if key != 'selected'}
                                      for name, packet in allocations.items()}}, sort_keys=True))


if __name__ == '__main__':
    main()
