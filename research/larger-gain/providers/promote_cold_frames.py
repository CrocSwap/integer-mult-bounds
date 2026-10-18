#!/usr/bin/env python3
"""Promote cold entrances using exact coupled forward frame closures.

The dependency-closure method extends the earlier indexing-frontier frame
search. Scalar gates and order are unchanged; every added frame dimension is
priced by the complete chain. Prepared with OpenAI Codex. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

from search_suffix_kernels import basis, span, inside, entropy


class ForwardFrames:
    def __init__(self, word):
        self.word = word
        self.regs = [[] for _ in range(728)]
        self.frames, self.roles = [], []
        self.next = {}
        for event in word['B']:
            roles = event[1:3] if event[0] == 'add' else event[1:2]
            self.add(roles, basis(tuple(event[-1])))
        self.gates = len(self.frames)
        full = basis(tuple(1 << j for j in range(9)))
        for register in range(728):
            final = full
            if 112 <= register < 224:
                port = word['ports'][register - 112]
                final = basis(tuple(x for x in range(1, 512) if not (x & port).bit_count() % 2))
            self.add([register], final)

    def add(self, roles, frame):
        index = len(self.frames)
        self.frames.append(frame)
        self.roles.append(roles)
        for register in roles:
            if self.regs[register]:
                self.next[self.regs[register][-1], register] = index
            self.regs[register].append(index)

    def raise_frame(self, changed, seed, frame):
        queue = [(seed, frame)]
        while queue:
            index, wanted = queue.pop()
            old = changed.get(index, self.frames[index])
            new = basis(old + wanted)
            if new == old:
                continue
            if index >= self.gates:
                return False
            changed[index] = new
            for register in self.roles[index]:
                following = self.next[index, register]
                other = changed.get(following, self.frames[following])
                if not inside(new, other):
                    queue.append((following, new))
        return True

    def apply(self, promotions):
        changed = {}
        for pivot, frame in promotions.items():
            if not self.raise_frame(changed, self.regs[pivot][0], frame):
                return None
        result = copy.deepcopy(self.word)
        for index, frame in changed.items():
            result['B'][index][-1] = list(frame)
        for pivot, frame in promotions.items():
            result['start_extra'][str(pivot)] = list(frame)
        return result, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--gk-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--pivot', type=int, action='append', required=True)
    parser.add_argument('--retain', type=int, default=8)
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
    frames = ForwardFrames(word)
    before = g.profile(word)
    results, counts = [], Counter()
    start = time.monotonic()
    for pivot in args.pivot:
        current = basis(tuple(word['start_extra'][str(pivot)]))
        assert len(current) == 1
        assert not any(pivot in (event[1:3] if event[0] == 'add' else event[1:2])
                       for event in word['A'] + word['cut'])
        candidates = {basis(current + (vector,)) for vector in range(1, 512)} - {current}
        for frame in sorted(candidates):
            counts['frame_covers'] += 1
            result = frames.apply({pivot: frame})
            if result is None:
                counts['incompatible_target_final'] += 1
                continue
            changed_word, changed = result
            profile = g.profile(changed_word)
            delta = {r: profile[r] - before[r] for r in set(profile) | set(before)
                     if profile[r] != before[r]}
            assert sum(r * n for r, n in delta.items()) == -1
            changed_word['report']['local_profile'] = dict(profile)
            estimate = entropy(delta) + 1 + __import__('math').log(48)
            record = dict(pivot=pivot, entrance_frame=frame,
                          changed_gates=len(changed), profile_delta=delta,
                          local_entropy_delta=entropy(delta),
                          optimistic_entropy_gain=estimate)
            results.append((record, changed_word))
        print(json.dumps(dict(pivot=pivot, counts=dict(counts),
                              seconds=time.monotonic() - start)), flush=True)
    results.sort(key=lambda pair: (-pair[0]['optimistic_entropy_gain'], pair[0]['changed_gates']))
    for index, (record, changed_word) in enumerate(results[:args.retain]):
        name = 'candidate-%03d' % index
        (args.out / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
        (args.out / (name + '.json.gz')).write_bytes(g.dump(changed_word))
    report = dict(status='PASS_EXACT_COUPLED_ENTRANCE_FRAME_SCREEN',
                  source_content_sha256=hashlib.sha256(raw).hexdigest(),
                  counts=dict(counts), candidates=[record for record, _ in results],
                  seconds=time.monotonic() - start,
                  scope='Every rank-two cover of each supplied entrance line is tested. '
                        'Only forward frame joins and the entrance are changed. Exact full-chain '
                        'profiles are recomputed; hosting, phases and moments are separate.')
    (args.out / 'SEARCH.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['candidates'][:8], indent=2))


if __name__ == '__main__':
    main()
