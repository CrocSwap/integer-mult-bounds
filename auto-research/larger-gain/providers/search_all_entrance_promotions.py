#!/usr/bin/env python3
"""Promote every existing entrance through a complete coupled frame closure.

Uses the credited, unchanged earlier frame-search implementation retained as
coupled_frames_base.py, SHA256 b6033cd2959297a624b557f3d04665c8fbb680a4c0987daf0704ef93711700bd.
Source: indexing-frontier/frame-screens/frame_search.py. Entrances may change;
scalar operations, cuts, target levels, centre frames and exits remain fixed.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

from coupled_frames_base import Chains, basis, span
from search_suffix_kernels import entropy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__ and not args.out.exists()
    args.out.mkdir(parents=True)
    sys.path.insert(0, str(args.gk_dir.resolve()))
    import gk_word as g
    import gk_common as co
    g.V = co.V = 112
    g.DATA = co.DATA = 7168
    raw = gzip.decompress(args.word.read_bytes())
    word = json.loads(raw)
    graph = Chains(word)
    original = g.profile(word)
    assert original == graph.profile()
    records, counts = [], Counter()
    for pivot_text, old_frame in word['start_extra'].items():
        pivot = int(pivot_text)
        old_frame = basis(tuple(old_frame))
        counts['entrances'] += 1
        start = graph.regs[pivot][0]
        seed = graph.next[start, pivot]
        maximum = graph.upper[seed]
        candidates = {basis(old_frame + (x,)) for x in span(maximum) - span(old_frame)}
        for frame in sorted(candidates):
            counts['admissible_covers'] += 1
            changed = graph.closure(seed, frame, 'raise', len(graph.nodes))
            assert changed is not None
            candidate = copy.deepcopy(word)
            candidate['start_extra'][pivot_text] = list(frame)
            for node, value in changed.items():
                point = graph.nodes[node]
                candidate[point['section']][point['index']][-1] = list(value)
            profile = g.profile(candidate)
            delta = {r: profile[r] - original[r] for r in set(profile) | set(original)
                     if profile[r] != original[r]}
            assert sum(r * n for r, n in delta.items()) == -1
            candidate['report']['local_profile'] = dict(profile)
            record = dict(pivot=pivot, old_frame=old_frame, new_frame=frame,
                          width_before=9 - len(old_frame), width_after=9 - len(frame),
                          changed_gates=len(changed), profile_delta=delta,
                          local_entropy_delta=entropy(delta),
                          optimistic_entropy_gain=entropy(delta) + 1 + math.log(48))
            records.append((record, candidate))
    records.sort(key=lambda pair: (-pair[0]['optimistic_entropy_gain'], pair[0]['changed_gates']))
    for index, (record, candidate) in enumerate(records[:20]):
        name = 'candidate-%03d' % index
        (args.out / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
        (args.out / (name + '.json.gz')).write_bytes(g.dump(candidate))
    report = dict(status='PASS_EXACT_ALL_ENTRANCE_PROMOTION_SCREEN',
                  source_content_sha256=hashlib.sha256(raw).hexdigest(), counts=dict(counts),
                  candidates=[record for record, _ in records],
                  scope='All one-dimensional entrance extensions below exact dependency-graph '
                        'upper bounds are tested. Forward joins pay every changed gate frame. '
                        'Cut frames and target levels remain frozen; no arbitrary scalar rewrite '
                        'or hosting improvement is ruled out.')
    (args.out / 'SEARCH.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(counts=dict(counts), best=records[0][0] if records else None), indent=2))


if __name__ == '__main__':
    main()
