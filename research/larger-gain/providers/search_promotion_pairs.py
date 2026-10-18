#!/usr/bin/env python3
"""Price simultaneous entrance promotions from their exact shared chain edges.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip
import itertools
import json
import math
from pathlib import Path

from coupled_frames_base import Chains, basis, contained
from search_suffix_kernels import entropy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--screen', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    args.out.mkdir(parents=True)
    word = json.loads(gzip.decompress(args.word.read_bytes()))
    records = json.loads(args.screen.read_text())['candidates']
    graph = Chains(word)
    closures = []
    for record in records:
        pivot, frame = record['pivot'], basis(tuple(record['new_frame']))
        start = graph.regs[pivot][0]
        closure = graph.closure(graph.next[start, pivot], frame, 'raise', len(graph.nodes))
        assert closure is not None
        closure[start] = frame
        closures.append(closure)

    def delta(changed):
        edges = {(graph.prev[node, r], node, r) for node in changed for r in graph.nodes[node]['regs']
                 if (node, r) in graph.prev}
        edges |= {(node, graph.next[node, r], r) for node in changed for r in graph.nodes[node]['regs']
                  if (node, r) in graph.next}
        answer = Counter()
        for left, right, _ in edges:
            old_left, old_right = graph.nodes[left]['F'], graph.nodes[right]['F']
            new_left, new_right = changed.get(left, old_left), changed.get(right, old_right)
            assert contained(new_left, new_right)
            if old_left != old_right:
                answer[len(old_right) - len(old_left)] -= 1
            if new_left != new_right:
                answer[len(new_right) - len(new_left)] += 1
        return {rank: count for rank, count in answer.items() if count}

    for record, closure in zip(records, closures):
        assert delta(closure) == {int(r): n for r, n in record['profile_delta'].items()}
    found, count = [], 0
    for i, j in itertools.combinations(range(len(records)), 2):
        if records[i]['pivot'] == records[j]['pivot']:
            continue
        count += 1
        combined = closures[i].copy()
        for node, frame in closures[j].items():
            combined[node] = basis(combined.get(node, ()) + frame)
        change = delta(combined)
        assert sum(r * n for r, n in change.items()) == -2
        additive_entropy = records[i]['local_entropy_delta'] + records[j]['local_entropy_delta']
        synergy = entropy(change) - additive_entropy
        if abs(synergy) > 1e-10:
            found.append(dict(indices=[i, j], pivots=[records[i]['pivot'], records[j]['pivot']],
                              widths_before=[records[i]['width_before'], records[j]['width_before']],
                              profile_delta=change, entropy_synergy=synergy,
                              optimistic_entropy_gain=entropy(change) + 2 * (1 + math.log(48))))
    found.sort(key=lambda record: (-record['entropy_synergy'], -record['optimistic_entropy_gain']))
    report = dict(status='PASS_EXACT_SIMULTANEOUS_ENTRANCE_PAIR_SCREEN', pairs=count,
                  nonadditive_pairs=len(found), candidates=found,
                  scope='All pairs from the admissible single-entrance cover catalogue. '
                        'Shared dependency closures are joined and all affected chain edges repriced. '
                        'Higher-order changes and alternate scalar words remain outside this screen.')
    (args.out / 'SEARCH.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(pairs=count, nonadditive_pairs=len(found), best=found[:12]), indent=2))


if __name__ == '__main__':
    main()
