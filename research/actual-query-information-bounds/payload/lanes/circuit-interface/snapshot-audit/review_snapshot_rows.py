"""Rebuild all backward snapshot rows from the pinned scalar event word."""

from bisect import bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PINS = {
    'core': 'fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877',
    'word': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'interface': '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3',
    'snapshots': '3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c',
    'proof': 'be9575e1cac8706c42fddff243f435935e098d197edaf7f8689352c93b7e3961',
    'receipt': '35698700474f2309a4eea2f192a5afbd2f42f580a7e0e510a0bb5687a87fdc2d',
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def read(path, key, compressed=False, pin_compressed=False, parse=True):
    data = path.read_bytes()
    raw = gzip.decompress(data) if compressed else data
    require(sha256(data if pin_compressed else raw).hexdigest() == PINS[key], 'Source pin: '+key)
    return json.loads(raw) if parse else raw


def combine(target, source, coefficient):
    for col, value in source.items():
        new = target.get(col, Q(0))+coefficient*value
        if new:
            target[col] = new
        else:
            target.pop(col, None)


def index(token):
    require(isinstance(token, list) and len(token) == 2, 'A literal field token')
    namespace, position = token
    require((namespace == 'L' and 0 <= position < 704) or
            (namespace == 'C' and 0 <= position < 8), 'An original field index')
    return position+(704 if namespace == 'C' else 0)


def intervals_partition(intervals, first, last):
    by_wire = defaultdict(list)
    for lo, hi, wire, frame, row in intervals:
        require(first <= lo <= hi <= last and 0 <= wire < 704, 'A declared interval range')
        by_wire[wire].append((lo, hi))
    require(set(by_wire) == set(range(704)), 'Every persistent wire has an interval')
    for spans in by_wire.values():
        spans.sort()
        require(spans[0][0] == first and spans[-1][1] == last, 'The complete boundary range')
        require(all(a[1]+1 == b[0] for a, b in zip(spans, spans[1:])), 'No interval gap or overlap')


def reject(function, reason):
    try:
        function()
    except ValueError:
        return
    raise ValueError('The control was not rejected: '+reason)


def main():
    events = read(LANES/'circuit-interface/CENTRE-FREE-PROGRAMS.json.gz', 'core', True)['backward']
    word = read(LANES.parent/'upstream/CANONICAL-WORD.json.gz', 'word', True, True)
    interface = read(LANES/'circuit-interface/INTERFACE.json', 'interface')
    snapshots = read(LANES/'history-encoding/BACKWARD-SNAPSHOT-INTERVALS.json.gz', 'snapshots', True)
    source_receipt = read(LANES/'history-encoding/SNAPSHOT-CONE-OBSTRUCTION.json', 'receipt')
    read(LANES/'history-encoding/SNAPSHOT-CONE-OBSTRUCTION.md', 'proof', parse=False)
    require(snapshots['pins'] == {'word': PINS['word'], 'core': PINS['core'], 'R': PINS['interface']}, 'All snapshot source pins')
    require(snapshots['R'] == interface['R'] and snapshots['frames'] == word['frames'], 'Actual query and frame source equality')
    query = [{int(j): Q(v) for j, v in row.items()} for row in interface['R']]
    ports = interface['ports']
    j_rows = [{p: Q(1)} for p in range(112)]
    for p, row in enumerate(j_rows):
        for query_row in query:
            combine(row, query_row, -query_row.get(p, Q(0))/4)

    first, last = snapshots['first_canonical_boundary'], snapshots['last_canonical_boundary']
    require((first, last) == (8106, 24913), 'The complete pinned canonical range')
    intervals = snapshots['intervals']
    intervals_partition(intervals, first, last)
    updates = defaultdict(list)
    for t, event in enumerate(events):
        if event[0] == 'climb':
            updates[event[2]].append(t)
        elif event[0] == 'scalar':
            updates[index(event[1][1])].append(t)
    supplied_rows = [{int(j): Q(v) for j, v in row.items()} for row in snapshots['rows']]
    checks_at = defaultdict(list)
    for item in intervals:
        lo, hi, wire, frame, row = item
        require(0 <= frame < len(word['frames']) and 0 <= row < len(supplied_rows), 'An interval row and frame index')
        next_update = bisect_right(updates[wire], lo)
        require(next_update == len(updates[wire]) or updates[wire][next_update] > hi, 'No scalar or canonical-frame change inside a constant interval')
        checks_at[lo].append((wire, frame, row))
        if hi != lo:
            checks_at[hi].append((wire, frame, row))

    def support(row):
        reduced = {p-112: value for p, value in row.items() if 112 <= p < 224}
        for p, value in row.items():
            if p < 112:
                combine(reduced, j_rows[p], value)
        return reduced

    rows = [{i: Q(1)} for i in range(712)]
    frames = word['start'][:]+[0]*8
    profile, macros = Counter(), Counter()
    private_uses, checked_pairs, reduced_rows = [], set(), {}
    endpoint_checks = support_coefficients = 0
    last_scalar = -1
    check_example = None
    for t, event in enumerate(events):
        kind = event[0]
        if kind == 'climb':
            _, _, target, before, after, rank = event
            require(0 <= target < 704 and frames[target] == before, 'The original native source frame')
            require(len(word['frames'][after])-len(word['frames'][before]) == rank, 'The exact native rank increment')
            frames[target] = after
            profile[rank] += 1
        elif kind == 'scalar':
            op, frame = event[1:]
            target = index(op[1])
            require(frames[target] == frame, 'Every scalar target has the declared canonical frame')
            if target >= 704:
                private_uses.append((t, target, 'write'))
            macros[op[0]] += 1
            last_scalar = t
            if op[0] == 'clear':
                rows[target] = {}
            elif op[0] == 'scale':
                coefficient = Q(op[2], op[3])
                rows[target] = {p: coefficient*v for p, v in rows[target].items() if coefficient*v}
            else:
                require(op[0] in ('copy', 'add'), 'An allowed scalar operation')
                other = index(op[2])
                require(other != target and frames[other] == frame, 'A distinct source in the same canonical frame')
                if other >= 704:
                    private_uses.append((t, other, 'read'))
                if op[0] == 'copy':
                    rows[target] = rows[other].copy()
                else:
                    combine(rows[target], rows[other], Q(op[3], op[4]))
        else:
            require(kind in ('phase', 'adapter', 'residual_adapter'), 'A known inherited operator event')
        for wire, frame, row_index in checks_at.get(t, ()):
            require(frames[wire] == frame and rows[wire] == supplied_rows[row_index], 'A fresh full712 prefix row and frame match the interval endpoint')
            endpoint_checks += 1
            if check_example is None:
                check_example = (rows[wire].copy(), supplied_rows[row_index].copy(), frames[wire], frame)
            pair = frame, row_index
            if pair not in checked_pairs:
                checked_pairs.add(pair)
                if row_index not in reduced_rows:
                    reduced_rows[row_index] = support(rows[wire])
                for port, coefficient in reduced_rows[row_index].items():
                    require(all((ports[port] & u).bit_count() % 2 == 0 for u in word['frames'][frame]), 'The exact fresh-row support law')
                    support_coefficients += 1
        if t == 8702:
            require(all(not row for row in rows[704:]), 'All original private fields are zero after their last use')

    expected = [{i: Q(1)} for i in range(712)]
    for p in range(112):
        combine(expected[p], {112+q: v for q, v in j_rows[p].items()}, Q(-1))
    expected[704:] = [{} for _ in range(8)]
    require(rows == expected, 'All712 final columns of the clean backward map')
    require(rows == [{int(j): Q(v) for j, v in row.items()} for row in snapshots['final_rows']], 'The supplied full final rows')
    require(frames == word['final']+[0]*8, 'The complete inherited canonical endpoints')
    require(last_scalar == last and events[8703] == ['phase', 'A'], 'The exact final scalar cut and post-private phase')
    require(max(t for t, _, _ in private_uses) == 8702, 'No original private read or write after8702')
    require(all(not support(rows[p]) for p in list(range(112))+list(range(224, 712))), 'The completed X and all helper/private baselines vanish on the test family')
    require(len(checked_pairs) == source_receipt['distinct_frame_row_pairs'] == 16023 and
            support_coefficients == source_receipt['exact_nonzero_support_coefficients'] == 98056, 'The complete claimed support coverage')
    require(profile == {1:2412, 2:418, 3:432, 4:142, 5:82}, 'The native profile of the unchanged core')
    full_helpers = [p for p in range(224, 704) if frames[p] == 1]
    require(len(full_helpers) == 402, 'The exact number of FULL helper baseline fields')

    actual, supplied, actual_frame, supplied_frame = check_example
    wrong = supplied.copy()
    wrong[711] = wrong.get(711, Q(0))+1
    reject(lambda: require(actual == wrong, 'Changed arbitrary private coefficient'), 'A changed snapshot row')
    reject(lambda: intervals_partition(intervals[1:], first, last), 'A missing interval')
    reject(lambda: require(actual_frame == (supplied_frame+1) % len(word['frames']), 'Changed frame index'), 'A changed native frame')

    receipt = {
        'status': 'PASS_INDEPENDENT_BACKWARD_SNAPSHOT_ROWS', 'source_pins': PINS,
        'producer_or_checker_imports': [], 'all_formal_input_columns': 712,
        'constant_intervals': len(intervals), 'interval_endpoint_checks': endpoint_checks,
        'interval_interior_update_checks': len(intervals),
        'complete_interval_wire_count': 704, 'distinct_frame_row_support_checks': len(checked_pairs),
        'exact_nonzero_support_coefficients': support_coefficients,
        'native_profile': dict(sorted(profile.items())), 'scalar_macros': dict(sorted(macros.items())),
        'last_original_private_event': 8702, 'all_eight_private_fields_zero_after_last_use': True,
        'last_scalar_event': last_scalar, 'FULL_helper_baseline_fields': full_helpers,
        'controls': {'changed_private_coefficient': 'rejected', 'missing_interval': 'rejected', 'changed_frame': 'rejected'},
        'scope': 'Independent full712 scalar-row reconstruction, interval coverage, native canonical frame accesses and support law. The source minor/cone proof review is separate. Exact native phases for a new capture word, merged-flow synthesis, costs and hosting are not supplied.',
        'reviewer_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE/'SNAPSHOT-ROWS-REVIEW.json').write_text(json.dumps(receipt, sort_keys=True, indent=2)+'\n')
    print(receipt['status'])
    print(json.dumps({k:receipt[k] for k in ('constant_intervals', 'interval_endpoint_checks', 'distinct_frame_row_support_checks', 'exact_nonzero_support_coefficients', 'last_original_private_event', 'reviewer_sha256')}, sort_keys=True))


if __name__ == '__main__':
    main()
