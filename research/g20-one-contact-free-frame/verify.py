#!/usr/bin/env python3
"""Exact one-contact A2 census with a freely chosen native correction frame.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Lead: local demand-trace mechanism; worker B: proof and packaging;
worker D: shared native floor and independent symbolic-frame verification.
Retains the source lineage of Ali Romman, unpaidmoon and Nick Petalas.
"""
import argparse
from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
WORD = 'research/g20-conjugation-admission/WORD.json.gz'
PATHS = 'research/g20-conjugation-admission/PATHS.json'
CURRENT_FRAMES = 'research/g20-conjugation-admission/prior/prior/prior/source/vendor/g20/inputs/FRAMES.json'
OLDER_FRAMES = 'research/bit-g20-contact-expansion-bound/FRAMES.json.gz'
WORD_SHA = '8dd441fdb9c8923df06eb5ebfda37d03e4539f2305763e688d8c7025d196c4b1'
PATHS_SHA = 'f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e'
METRIC_SHA = 'ef39ef8c66b715f36e81894797ec627f9f75b6db762497be084f42897733f2aa'
NATIVE_SHA = '2a9b4cc47ce8ad3a4ab1a0467dda2737202ef9f982da564bd64fe0d3fb9cb5d3'
RESULT_SHA = '11d4ad371f64d82821a7c31d5890ba84e74e2efbd8f0e54825b164fe49cdd2a7'
EXCEPTIONAL = [[2, -1], [3, 1], [4, 1], [5, -1]]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load_native():
    path = PACKAGE / 'native_floor.py'
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == NATIVE_SHA, 'shared native module bytes')
    module = ModuleType('free_frame_native')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def source():
    word_bytes = (ROOT / WORD).read_bytes()
    paths_bytes = (ROOT / PATHS).read_bytes()
    frames_bytes = (ROOT / CURRENT_FRAMES).read_bytes()
    need(sha256(word_bytes).hexdigest() == WORD_SHA, 'pinned source word')
    need(sha256(paths_bytes).hexdigest() == PATHS_SHA, 'pinned source paths')
    need(frames_bytes == gzip.decompress((ROOT / OLDER_FRAMES).read_bytes()), 'current and older frames byte-identical')
    need(sha256(frames_bytes).hexdigest() == '0d99fc6b8f45c03dfba5252a03dd9e7fe23be3a7593dfe15368e34da6629a654', 'pinned frames')
    return json.loads(gzip.decompress(word_bytes)), json.loads(paths_bytes), json.loads(frames_bytes)['frames']


def inspect_interval(records, left, right):
    a, b = records[left][1:3]
    need(records[left][:3] == records[right][:3], 'equal outer transvections')
    corrections = {}
    for index in range(left + 1, right):
        event = records[index]
        if event[0] in ('INIT', 'ERASE'):
            if event[1] in (a, b):
                return None, 'owned_operand_barrier'
        else:
            need(event[0] == 'ADD', 'scalar alphabet')
            destination, donor, frame = event[1:]
            if destination == b and donor == a:
                return None, 'reverse_contact'
            if destination == b:
                corrections[index] = ('ADD', a, donor, frame)
            elif donor == a:
                corrections[index] = ('ADD', destination, b, frame)
    return corrections, None


def domain(records):
    positions = defaultdict(list)
    for index, event in enumerate(records):
        if event[0] == 'ADD':
            positions[event[1:3]].append(index)
    selected, counts = [], Counter()
    for gate, indices in sorted(positions.items()):
        for offset, left in enumerate(indices):
            for right in indices[offset + 1:]:
                counts['equal_pairs'] += 1
                corrections, reason = inspect_interval(records, left, right)
                if reason:
                    counts[reason] += 1
                    continue
                counts['eligible'] += 1
                if len(corrections) == 1:
                    counts['one_contact'] += 1
                    selected.append((left, right, gate, corrections))
    need(counts == {'equal_pairs': 2787, 'eligible': 2270, 'reverse_contact': 517, 'one_contact': 184}, 'exact source interval domain')
    return selected, dict(sorted(counts.items()))


def rewrite_one(records, left, right, corrections):
    need(len(corrections) == 1, 'one correction only')
    changed, inserted = [], None
    for index, event in enumerate(records):
        if index in (left, right):
            continue
        changed.append(event)
        if index in corrections:
            inserted = len(changed)
            changed.append(corrections[index])
    need(inserted is not None, 'correction placement')
    return changed, inserted


def traces(records, start, final, owned):
    rows = [1 << index for index in range(len(start))]
    out = [[(frame, False, -1)] for frame in start]
    locations = {}
    for index, event in enumerate(records):
        op, destination = event[:2]
        if op in ('INIT', 'ERASE'):
            need(destination in owned and (op != 'INIT' or not rows[destination]), 'legal owned event')
            rows[destination] = 0
            out[destination].append((event[2], False, index))
            continue
        need(op == 'ADD' and destination != event[2], 'distinct scalar ADD roles')
        donor, frame = event[2:]
        if not rows[donor]:
            continue
        for role in (destination, donor):
            locations[index, role] = len(out[role])
            out[role].append((frame, bool(rows[role]), index))
        rows[destination] ^= rows[donor]
    for role, frame in enumerate(final):
        if role in owned:
            need(not rows[role], 'whole owned final return')
        else:
            out[role].append((frame, bool(rows[role]), len(records)))
    return out, locations, rows


def charge(before, after, paid, distances):
    if not paid or before == after:
        return 0
    need(before is not None and after is not None, 'paid initialized frame')
    return distances[before][after]


def histogram(trace, distances):
    result = Counter()
    for demands in trace:
        for before, after in zip(demands, demands[1:]):
            rank = charge(before[0], after[0], after[1], distances)
            if rank:
                result[rank] += 1
    return result


def local_neighbours(trace, locations, index, correction):
    _, destination, donor, oldframe = correction
    need((index, destination) in locations and (index, donor) in locations, 'nonzero correction donor')
    local = []
    for role in (destination, donor):
        position = locations[index, role]
        demands = trace[role]
        before, node = demands[position - 1], demands[position]
        need(node[0] == oldframe, 'actual correction node frame')
        after = demands[position + 1] if position + 1 < len(demands) else None
        local.append((before, node, after))
    return local


def moved_histogram(bill, local, oldframe, newframe, distances):
    result = bill.copy()
    for before, node, after in local:
        for rank, change in ((charge(before[0], oldframe, node[1], distances), -1),
                             (charge(before[0], newframe, node[1], distances), 1)):
            if rank:
                result[rank] += change
        if after is not None:
            for rank, change in ((charge(oldframe, after[0], after[1], distances), -1),
                                 (charge(newframe, after[0], after[1], distances), 1)):
                if rank:
                    result[rank] += change
    need(all(type(rank) is int and rank > 0 and count >= 0 for rank, count in result.items()), 'nonnegative complete invoice')
    return result


def sign(delta, native):
    if delta == EXCEPTIONAL:
        intervals = [[2, 3], [4, 5]]
        check_decreasing_increments(delta, intervals)
        return {'kind': 'strict_decreasing_increments', 'intervals': intervals}
    proof = native.partition(delta)
    need(native.check_partition(delta, proof) == 'strict_loss', 'strict partition sign')
    return {'kind': 'strict_partition', 'partition': proof}


def check_decreasing_increments(delta, intervals):
    need(len(intervals) == 2 and all(len(interval) == 2 for interval in intervals), 'two increment intervals')
    (a, b), (c, d) = intervals
    need(all(type(value) is int for value in (a, b, c, d)), 'integer increment endpoints')
    need(0 < a < b <= c < d and b - a == d - c, 'ordered equal-width positive intervals')
    expected = Counter()
    for rank, coefficient in ((a, -1), (b, 1), (c, 1), (d, -1)):
        expected[rank] += coefficient
    need(delta == [[rank, count] for rank, count in sorted(expected.items()) if count], 'exact increment identity')


def census(native):
    word, retained, frames = source()
    records = [tuple(event) for event in word['records'] if event[0] not in ('Q', 'ZERO_Q')]
    width, owned = len(word['start']), set(word['owned'])
    need(width == 685 and len(records) == 11930, 'exact source shape')
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0) for i in range(width)]
    edges, dimensions = native.native_graph(frames)
    need(len(dimensions) == 645 and len(edges) == 52624, 'complete proper nested graph')
    direct = {}
    for key, route in retained.items():
        need(len(route) == 1, 'retained singleton path')
        a, b, rank = route[0]
        need(key == f'{a}:{b}' and edges[a, b] == rank, 'retained native geometry')
        direct[a, b] = rank
    need(len(direct) == 2369, 'retained path inventory')
    distances = native.metric(edges, dimensions)
    need(native.metric_digest(distances) == METRIC_SHA, 'independently checked full rank metric')
    base = Counter(event[4] for event in word['records'] if event[0] == 'Q')
    source_trace, _, rows = traces(records, word['start'], word['final'], owned)
    need(rows == expected and histogram(source_trace, distances) == base, 'source all-column endpoint and exact paid invoice')
    candidates, domain_counts = domain(records)
    outcomes, shapes, exceptional_assignments = [], Counter(), []
    for left, right, gate, corrections in candidates:
        changed, index = rewrite_one(records, left, right, corrections)
        trace, locations, rows = traces(changed, word['start'], word['final'], owned)
        need(rows == expected, 'rewritten endpoint on all independent raw and dirty columns')
        bill = histogram(trace, distances)
        full, _, _ = native.invoice(changed, word['start'], word['final'], owned, distances, direct)
        need(bill == full, 'whole-word trace agrees with chronological invoice')
        correction = changed[index]
        oldframe = correction[3]
        local = local_neighbours(trace, locations, index, correction)
        for frame in sorted(dimensions):
            moved = moved_histogram(bill, local, oldframe, frame, distances)
            delta = native.signed_delta(moved, base)
            shapes[tuple(map(tuple, delta))] += 1
            outcomes.append([left, right, index, frame, delta])
            if delta == EXCEPTIONAL:
                exceptional_assignments.append([left, right, index, frame])
    need(len(outcomes) == 184 * 645 and len(shapes) == 245, 'complete assignment and shape domain')
    need(sorted(exceptional_assignments) == sorted([[6089, 6567, 6354, 338], [6074, 6582, 6401, 440], [6093, 6563, 6342, 410]]), 'exact balancing fixtures')
    proofs = [{'delta': list(map(list, delta)), 'count': count, 'proof': sign(list(map(list, delta)), native)}
              for delta, count in sorted(shapes.items())]
    proof_counts = Counter()
    for proof in proofs:
        proof_counts[proof['proof']['kind']] += proof['count']
    need(proof_counts == {'strict_partition': 118677, 'strict_decreasing_increments': 3}, 'all strict shape multiplicities')
    return {'schema': 'g20-one-contact-free-native-frame-v1', 'base_commit': '2485805a6d47f36ea83ddde6327d453ac82d44dc',
            'source_sha256': {'word': WORD_SHA, 'paths': PATHS_SHA, 'frames': native.FRAME_SHA},
            'metric_sha256': METRIC_SHA, 'domain': domain_counts,
            'counts': {'intervals': 184, 'frames': 645, 'assignments': len(outcomes), 'shapes': len(shapes),
                       'strict_partition': 118677, 'strict_decreasing_increments': 3, 'zero': 0},
            'base_paid': dict(sorted(base.items())), 'proofs': proofs,
            'exceptional_assignments': exceptional_assignments, 'outcomes': outcomes}


def controls(native):
    checked = []
    def reject(label, operation):
        try:
            operation()
        except (ValueError, KeyError):
            checked.append(label)
        else:
            raise ValueError('Accepted negative control: ' + label)
    distances = {0: {0: 0, 1: 1, 2: 3}, 1: {0: 1, 1: 0, 2: 2}, 2: {0: 3, 1: 2, 2: 0}}
    need(histogram([[(0, False, -1), (2, True, 0)]], distances) == {3: 1}, 'final public return charged')
    checked.append('final_public_return_charged')
    trace, places, _ = traces([('ERASE', 1, 0), ('ADD', 0, 1, 2)], [0, 0], [0, None], {1})
    need(not places and not histogram(trace, distances), 'zero donor skips both demands')
    checked.append('zero_donor_skips_both_routes')
    local = [((0, False, -1), (1, True, 0), (2, True, 1))]
    need(moved_histogram(Counter({1: 1, 2: 1}), local, 1, 0, distances) == Counter({3: 1}), 'both neighbouring transitions updated')
    checked.append('both_neighbours_including_return_updated')
    reject('negative_invoice_rejected', lambda: moved_histogram(Counter(), local, 1, 2, distances))
    reject('paid_uninitialized_frame_rejected', lambda: charge(None, 1, True, distances))
    reject('dirty_owned_init_rejected', lambda: traces([('INIT', 0, 0)], [0], [None], {0}))
    reject('dirty_owned_return_rejected', lambda: traces([], [0], [None], {0}))
    reject('reverse_contact_rejected', lambda: need(inspect_interval([('ADD', 0, 1, 0), ('ADD', 1, 0, 0), ('ADD', 0, 1, 0)], 0, 2)[1] is None, 'reverse contact'))
    reject('uncovered_negative_rejected', lambda: native.check_partition([[1, 2], [2, -1]], {'groups': [], 'left': [1, 1]}))
    reject('double_used_positive_rejected', lambda: native.check_partition([[1, 2], [2, -1]], {'groups': [[2, [1, 1]]], 'left': [1]}))
    reject('unequal_increment_width_rejected', lambda: check_decreasing_increments(EXCEPTIONAL, [[2, 3], [4, 6]]))
    reject('reversed_increment_order_rejected', lambda: check_decreasing_increments(EXCEPTIONAL, [[4, 5], [2, 3]]))
    reject('incorrect_increment_identity_rejected', lambda: check_decreasing_increments([[2, 1], [3, -1], [4, -1], [5, 1]], [[2, 3], [4, 5]]))
    need(sign(EXCEPTIONAL, native)['kind'] == 'strict_decreasing_increments', 'balanced increment witness')
    checked.append('balanced_decreasing_increment_shape')
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    native = load_native()
    result = census(native)
    result['controls'] = controls(native)
    payload = canonical(result)
    if args.output:
        need(not args.output.resolve().is_relative_to(ROOT), 'generated output outside checkout')
        args.output.write_bytes(payload)
    else:
        frozen = gzip.decompress((PACKAGE / 'RESULT.json.gz').read_bytes())
        need(sha256(frozen).hexdigest() == RESULT_SHA, 'exact frozen certificate bytes')
        need(payload == frozen, 'complete moved-frame certificate replay')
    print(json.dumps({'counts': result['counts'], 'certificate_sha256': sha256(payload).hexdigest()}, sort_keys=True))
    print('PASS_G20_ONE_CONTACT_FREE_FRAME')


if __name__ == '__main__':
    main()
