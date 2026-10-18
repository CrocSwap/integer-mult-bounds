#!/usr/bin/env python3
"""Compose paid entrance-frame promotions, preserving every scalar operation.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

from coupled_frames_base import Chains, basis
from search_suffix_kernels import entropy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--recipes', type=Path, required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    sys.path.insert(0, str(args.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    raw = gzip.decompress(args.word.read_bytes())
    original = json.loads(raw)
    word = copy.deepcopy(original)
    recipes = json.loads(args.recipes.read_text())
    assert len({recipe['pivot'] for recipe in recipes}) == len(recipes)
    graph = Chains(word)
    changed = set()
    for recipe in recipes:
        pivot = recipe['pivot']
        assert basis(tuple(word['start_extra'][str(pivot)])) == basis(tuple(recipe['old_frame']))
        frame = basis(tuple(recipe['new_frame']))
        assert len(frame) == len(recipe['old_frame']) + 1
        start = graph.regs[pivot][0]
        seed = graph.next[start, pivot]
        closure = graph.closure(seed, frame, 'raise', len(graph.nodes))
        assert closure is not None
        for node, value in closure.items():
            graph.nodes[node]['F'] = value
            changed.add(node)
        word['start_extra'][str(pivot)] = list(frame)
    for node in changed:
        point = graph.nodes[node]
        word[point['section']][point['index']][-1] = list(point['F'])
    before, after = g.profile(original), g.profile(word)
    delta = {r: after[r] - before[r] for r in set(after) | set(before) if after[r] != before[r]}
    assert sum(r * n for r, n in delta.items()) == -len(recipes)
    for section in ('A', 'cut', 'B', 'cleanup', 'precondition'):
        assert [event[:-1] for event in word[section]] == [event[:-1] for event in original[section]]
    widths = co.widths_of(word)
    word['report'].update(local_profile=dict(after), local_rank_mass=sum(r * n for r, n in after.items()),
                          entrance_rank=sum(9 - width for width in widths),
                          entering_helpers=sum(width < 9 for width in widths),
                          width_inventory=dict(Counter(widths)))
    args.out.mkdir(parents=True)
    encoded = g.dump(word)
    (args.out / 'FULL-WORD.json.gz').write_bytes(encoded)
    (args.out / 'RECIPES.json').write_text(json.dumps(recipes, indent=2) + '\n')
    receipt = dict(status='PASS_COUPLED_ENTRANCE_PROMOTION_CONSTRUCTION',
                   source_content_sha256=hashlib.sha256(raw).hexdigest(),
                   word_content_sha256=hashlib.sha256(gzip.decompress(encoded)).hexdigest(),
                   changed_gates=len(changed), promotions=len(recipes),
                   scalar_operations_unchanged=True, profile_before=dict(before), profile_after=dict(after),
                   profile_delta=delta, local_entropy_delta=entropy(delta),
                   widths_after=dict(Counter(widths)),
                   scope='Exact coupled frame-chain construction only; native, phase, hosting, '
                         'invoice and moment admission remain separate.')
    (args.out / 'CONSTRUCTION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
