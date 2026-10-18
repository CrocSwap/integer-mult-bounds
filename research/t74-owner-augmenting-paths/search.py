#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Deterministic greedy discovery of the published alternating paths.

This is a construction search, not an optimality proof. verify.py independently
checks the explicit output against the complete predecessor geometry.
"""
import argparse
import json
from collections import defaultdict, deque
from pathlib import Path
from verify import P, authenticate, family, key, read, require


def search():
    authenticate()
    plan = read(P / 'inputs/PLAN.json.gz')
    rows = read(P / 'inputs/OWNERS.json.gz')
    bins, by_time_width, occupied = defaultdict(list), defaultdict(list), defaultdict(set)
    location = {}
    for i, row in enumerate(rows):
        location[i] = key(row)
        bins[key(row)].append(i)
        by_time_width[row['time'], row['width']].append(i)
        occupied[row['time']].add(row['family'])
    windows = {tuple(map(int, k.split(','))): v for k, v in plan['windows'].items()}

    def capacity(bin_id):
        return windows[bin_id[:2]][0]

    def slack(bin_id):
        return capacity(bin_id) - sum(rows[i]['width'] for i in bins.get(bin_id, []))

    def paths(start, width, ends, first_only=False):
        queue = deque([start])
        previous, seen_calls, found = {start: None}, set(), []
        while queue:
            destination = queue.popleft()
            physical = family(plan, destination)
            for t in sorted(windows[destination[:2]][1]):
                if t in seen_calls or physical in occupied[t]:
                    continue
                seen_calls.add(t)
                for role in by_time_width[t, width]:
                    source = location[role]
                    if source in previous:
                        continue
                    previous[source] = destination, role
                    if source in ends:
                        path, current = [], source
                        while previous[current] is not None:
                            target, index = previous[current]
                            path.append((index, target))
                            current = target
                        found.append((source, list(reversed(path))))
                        if first_only:
                            return found
                    queue.append(source)
        return found

    def move(path):
        undo = []
        for role, target in path:
            source, t = location[role], rows[role]['time']
            require(rows[role]['width'] <= slack(target), 'Discovery capacity error')
            require(family(plan, target) not in occupied[t], 'Discovery family collision')
            undo.append((role, source))
            bins[source].remove(role)
            bins[target].append(role)
            location[role] = target
            occupied[t].remove(family(plan, source))
            occupied[t].add(family(plan, target))
        return list(reversed(undo))

    composites = []
    for _ in range(50):
        gaps = [b for b, ids in bins.items() if capacity(b) == 16 and len(ids) == 1
                and rows[ids[0]]['width'] == 9]
        pairs = {b for b, ids in bins.items() if capacity(b) == 32
                 and sorted(rows[i]['width'] for i in ids) == [7, 7, 9, 9]}
        found = False
        for first in gaps:
            for source, path1 in paths(first, 7, pairs):
                undo1 = move(path1)
                for second in gaps:
                    if second == first:
                        continue
                    candidates = paths(second, 7, {source}, True)
                    if not candidates:
                        continue
                    path2 = candidates[0][1]
                    undo2 = move(path2)
                    ends = {b for b, ids in bins.items() if b not in (first, second, source)
                            and ((capacity(b) == 48 and slack(b) >= 3)
                                 or (capacity(b) == 32 and slack(b) >= 5)
                                 or (capacity(b) == 16 and slack(b) == 7))
                            and any(rows[i]['width'] == 9 for i in ids)}
                    candidates = paths(source, 9, ends, True)
                    if candidates:
                        end, path9 = candidates[0]
                        move(path9)
                        composites.append(dict(gaps=[first, second], seven_bin=source,
                                               nine_end=end, paths=[path1, path2, path9]))
                        found = True
                        break
                    move(undo2)
                if found:
                    break
                move(undo1)
            if found:
                break
        if not found:
            break
    transfers = []
    for _ in range(500):
        found = False
        slacks = {b: slack(b) for b in bins}
        for width in (4, 5, 7, 8, 9):
            sources = {b for b, ids in bins.items() if any(rows[i]['width'] == width for i in ids)}
            maximum = max((slacks[b] for b in sources), default=0)
            targets = sorted((b for b, r in slacks.items() if width <= r < maximum + width),
                             key=lambda b: (slacks[b], b))
            for target in targets:
                before = slacks[target]
                ends = {b for b in sources if b != target and slacks[b] > before - width}
                candidates = paths(target, width, ends, True)
                if not candidates:
                    continue
                end, path = candidates[0]
                previous = slacks[end]
                move(path)
                transfers.append(dict(width=width, target=target, end=end,
                                      old_slacks=[before, previous],
                                      new_slacks=[before-width, previous+width], path=path))
                found = True
                break
            if found:
                break
        if not found:
            break
    result = dict(seven_nine=composites, single_width=transfers)
    # Normalize tuples exactly as the JSON witness does.
    result = json.loads(json.dumps(result))
    require(result == read(P / 'MOVES.json'), 'Discovery differs from the published witness')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = search()
    if args.out:
        with args.out.open('x') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print('PASS_REDISCOVERED_EXPLICIT_PATHS', len(result['seven_nine']),
          len(result['single_width']), flush=True)
