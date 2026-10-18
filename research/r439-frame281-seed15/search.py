"""Bounded exact synthesis for frame281's fixed positive six-wire transfer.

Adapted from Ross Richardson's PR925 r439-frame267-seed01/search.py
(Apache-2.0), with flat immutable matrices and an explicit incomplete outcome.
Prepared for @woklerx with substantial OpenAI Codex assistance.
No search over other frames or general Boolean circuits.
"""
import argparse
from collections import Counter
from functools import cache
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
PR952 = ROOT / 'research/r439-six-wire-boolean/candidate.json.gz'
REGS = [263, 275, 310, 374, 410, 491]
IDENTITY = bytes(int(i == j) for i in range(6) for j in range(6))


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError('invalid JSON constant: ' + value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid_constant)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def transfer(ops):
    rows = [[int(i == j) for j in range(6)] for i in range(6)]
    for dst, src in ops:
        rows[dst] = [x + y for x, y in zip(rows[dst], rows[src])]
    return rows


def source(path, start, stop):
    word = strict_json(gzip.decompress(path.read_bytes()))
    segment = word['A'][start:stop]
    if len(segment) != stop-start or any(f != 281 or len(ss) != 1 for f, _, ss in segment):
        raise ValueError('source slice changed')
    if [i for i, gate in enumerate(word['A']) if gate[0] == 281] != list(range(start, stop)):
        raise ValueError('slice is not the complete frame281 block')
    return [[REGS.index(dst), REGS.index(ss[0])] for _, dst, ss in segment]


def nominate(original, state_cap=1_000_000, reverse_guard=False):
    if type(state_cap) is not int or state_cap < 1:
        raise ValueError('state cap must be a positive integer')
    target = bytes(x for row in transfer(original) for x in row)
    choices, histogram = {}, Counter()
    edges = states = completed = 0
    infinity = 999

    @cache
    def distance(flat):
        nonlocal edges, states, completed
        if states >= state_cap:
            raise OverflowError('state budget reached; no optimum established')
        states += 1
        if flat == IDENTITY:
            histogram[0] += 1
            completed += 1
            return 0
        best = infinity
        for dst in range(6):
            d = 6 * dst
            row = flat[d:d+6]
            for src in range(6):
                if dst == src:
                    continue
                s = 6 * src
                other = flat[s:s+6]
                if row[dst] <= other[dst] or any(x < y for x, y in zip(row, other)):
                    continue
                previous = flat[:d] + bytes(x-y for x,y in zip(row,other)) + flat[d+6:]
                edges += 1
                length = 1 + distance(previous)
                if length < best:
                    best = length
                    choices[flat] = (dst, src, previous)
        completed += 1
        histogram[best] += 1
        return best

    try:
        minimum = distance(target)
    except OverflowError:
        return {'exhausted': False, 'minimum': None, 'replacement': original,
                'states': states, 'completed_states': completed, 'edges': edges,
                'state_cap': state_cap, 'distance_histogram': {str(k):v for k,v in sorted(histogram.items())},
                'dead_end_distance': infinity}
    if minimum >= infinity:
        raise ValueError('no positive-addition factorization found')
    backward, current = [], target
    while current != IDENTITY:
        dst, src, current = choices[current]
        backward.append([dst, src])
    result = {'replacement': list(reversed(backward)), 'minimum': minimum,
            'exhausted': True, 'states': states, 'completed_states': completed,
            'edges': edges, 'state_cap': state_cap,
            'distance_histogram': {str(k):v for k,v in sorted(histogram.items())}, 'dead_end_distance': infinity}
    if reverse_guard:
        bound = bytes(x for row in transfer(original[::-1]) for x in row)
        visited, guard_edges = 0, 0
        dead = set()

        def guarded(flat, reverse):
            nonlocal visited, guard_edges
            key = (flat, reverse)
            if key in dead:
                return None
            if visited >= state_cap:
                raise OverflowError('reverse guard state cap reached')
            visited += 1
            if flat == IDENTITY:
                return []
            remaining = distance(flat)
            for dst in range(6):
                d = 6*dst
                row = flat[d:d+6]
                for src in range(6):
                    if dst == src:
                        continue
                    s = 6*src
                    other = flat[s:s+6]
                    if row[dst] <= other[dst] or any(x < y for x,y in zip(row,other)):
                        continue
                    previous = flat[:d]+bytes(x-y for x,y in zip(row,other))+flat[d+6:]
                    if distance(previous) != remaining-1:
                        continue
                    summed = [x+y for x,y in zip(reverse[d:d+6],reverse[s:s+6])]
                    if any(x>y for x,y in zip(summed,bound[d:d+6])):
                        continue
                    next_reverse = reverse[:d]+bytes(summed)+reverse[d+6:]
                    guard_edges += 1
                    tail = guarded(previous,next_reverse)
                    if tail is not None:
                        return [[dst,src]] + tail
            dead.add(key)
            return None

        try:
            feasible = guarded(target, IDENTITY)
            result['reverse_guard'] = {'states':visited,'edges':guard_edges,
                'shortest_feasible':feasible is not None, 'exhausted_without_witness':feasible is None}
            if feasible is not None:
                result['replacement'] = list(reversed(feasible))
        except OverflowError:
            result['reverse_guard'] = {'states':visited,'edges':guard_edges,
                'shortest_feasible':None,'exhausted_without_witness':False}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-witness', action='store_true')
    args = parser.parse_args()
    old = source(WORD, 906, 927)
    retained = source(PR952, 825, 838)
    prior = strict_json((ROOT / 'research/r439-frame267-seed01/WITNESS.json').read_bytes())
    permutation = [3, 2, 0, 1, 4, 5]
    permuted_prior = [[permutation[d], permutation[s]] for d,s in prior['original']]
    if transfer(permuted_prior) != transfer(old):
        raise ValueError('selected-matrix PR925 conjugacy mismatch')
    selected = {'start':906, 'stop':927, 'original':old,
        'target_matrix':transfer(old), 'pr925_conjugacy':permutation, **nominate(old)}
    # Evidence-driven pivot within frame281: selected lift is conjugate to PR925.
    # The retained PR952 lift is different and gives the genuinely new boundary.
    result = {'phase': 'A', 'start': 825, 'stop': 838, 'frame': 281, 'quad': 15,
              'registers': REGS, 'assignment_seed': 15, 'source_pr':952,
              'original': retained, 'target_matrix': transfer(retained),
              'selected_reference':selected, **nominate(retained, reverse_guard=True)}
    result['reverse_original_matrix'] = transfer(retained[::-1])
    result['reverse_replacement_matrix'] = transfer(result['replacement'][::-1])
    result['reverse_dominated_by_parent'] = all(y <= x
        for a,b in zip(result['reverse_original_matrix'],result['reverse_replacement_matrix'])
        for x,y in zip(a,b))
    path = HERE / 'WITNESS.json'
    if args.write_witness:
        path.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
    elif canonical(result) != canonical(strict_json(path.read_bytes())):
        raise ValueError('search witness mismatch')
    print('PASS_FRAME281_SEARCH minimum={} states={} edges={} guarded_shortest={} selected_states={}'.format(
        result['minimum'], result['states'], result['edges'],
        result['reverse_guard']['shortest_feasible'], selected['states']), flush=True)


if __name__ == '__main__':
    main()
