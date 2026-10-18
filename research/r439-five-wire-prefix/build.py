#!/usr/bin/env python3
"""Bounded five-wire phase-A nomination on the pinned PR904 R439 word.

Ross Richardson, substantial OpenAI Codex assistance; Apache-2.0.
Extends Gareth Davidson's PR904 and Jeffrey Cox's PR754 local-circuit method.
One path per state is retained: this is not a search of all circuit words.
"""
import argparse
from collections import Counter, defaultdict, deque
import copy
import gzip
from pathlib import Path
import random
import runpy

C = runpy.run_path(str(Path(__file__).resolve().with_name('common.py')))
N = 5
IDENTITY = tuple(1 << i for i in range(N))
GENERATORS = [(d, s) for d in range(N) for s in range(N) if d != s]
random.Random(10).shuffle(GENERATORS)


def ball(start):
    paths = {start: ()}
    pending = deque([start])
    while pending:
        state = pending.popleft()
        path = paths[state]
        if len(path) == 3:
            continue
        for d, s in GENERATORS:
            nxt = list(state)
            nxt[d] ^= nxt[s]
            nxt = tuple(nxt)
            if nxt not in paths:
                paths[nxt] = path + ((d, s),)
                pending.append(nxt)
    return paths


def image(ops, positive=False):
    if positive:
        rows = [[int(i == j) for j in range(N)] for i in range(N)]
        for d, s in ops:
            rows[d] = [a + b for a, b in zip(rows[d], rows[s])]
    else:
        rows = list(IDENTITY)
        for d, s in ops:
            rows[d] ^= rows[s]
    return tuple(rows)


def guard(old, new):
    if {r for op in new for r in op} != set(range(N)):
        return False
    for a, b in ((old, new), (old[::-1], new[::-1])):
        if any(y > x for ar, br in zip(image(a, True), image(b, True)) for x, y in zip(ar, br)):
            return False
    return True


def construct(word):
    forward = ball(IDENTITY)
    cache = {}
    counts = Counter()
    lengths = Counter()
    candidates = []
    flat = [(f, d, s) for f, d, srcs in word['A'] for s in srcs]
    for start, (frame, _, _) in enumerate(flat):
        registers = set()
        for last in range(start, min(len(flat), start + 12)):
            f, d, s = flat[last]
            if f != frame:
                break
            registers.update((d, s))
            if len(registers) > N:
                break
            if len(registers) != N:
                continue
            counts['windows'] += 1
            labels = sorted(registers)
            index = {r: i for i, r in enumerate(labels)}
            old = tuple((index[d], index[s]) for _, d, s in flat[start:last + 1])
            lengths[len(old)] += 1
            target = image(old)
            if target not in cache:
                backward = ball(target)
                # The suffix path takes target -> meeting state. Each CNOT is
                # self-inverse, so reverse it to go meeting state -> target.
                nominees = []
                for meeting, suffix in backward.items():
                    if meeting in forward:
                        nominees.append(forward[meeting] + suffix[::-1])
                cache[target] = sorted(set(nominees), key=lambda p: (len(p), p))
            shorter = [p for p in cache[target] if len(p) < len(old)]
            counts['windows_with_shorter_nominee'] += bool(shorter)
            new = next((p for p in shorter if guard(old, p)), None)
            if new is None:
                continue
            counts['guarded_windows'] += 1
            candidates.append(dict(section='A', start=start, stop=last + 1,
                                   frame=frame, registers=labels,
                                   old=[list(x) for x in old], new=[list(x) for x in new],
                                   saving=len(old) - len(new)))
    ending = defaultdict(list)
    for item in candidates:
        ending[item['stop']].append(item)
    dp = [(0, []) for _ in range(len(flat) + 1)]
    for i in range(1, len(dp)):
        dp[i] = dp[i - 1]
        for item in ending[i]:
            saving = dp[item['start']][0] + item['saving']
            if saving > dp[i][0]:
                dp[i] = (saving, dp[item['start']][1] + [item])
    saved, selected = dp[-1]
    candidate = copy.deepcopy(word)
    out, position = [], 0
    for item in selected:
        out.extend([f, d, [s]] for f, d, s in flat[position:item['start']])
        out.extend([item['frame'], item['registers'][d], [item['registers'][s]]] for d, s in item['new'])
        position = item['stop']
    out.extend([f, d, [s]] for f, d, s in flat[position:])
    candidate['A'] = out
    v = word['v']
    full = word['frames'].index(list(range(v)))
    candidate['C'] = [[full, d, srcs[:]] for _, d, srcs in reversed(candidate['A'] + candidate['B'])
                      if not v <= d < 2 * v]
    certificate = dict(format='r439-five-wire/1', seed=10,
                       baseline_sha256=C['digest'](word), candidate_sha256=C['digest'](candidate),
                       domain=dict(section='A', wires=5, max_window=12, forward_depth=3, backward_depth=3,
                                   representative_policy='first BFS path per state; seed-10 generator order; guarded nominees sorted by length then lexicographically'),
                       ball_states=len(forward), ball_histogram=dict(sorted(Counter(map(len, forward.values())).items())),
                       window_lengths=dict(sorted(lengths.items())), counts=dict(counts), distinct_window_maps=len(cache),
                       selected=selected, saved_A=saved, saved_with_cleanup=2 * saved)
    return candidate, certificate


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    C['pins'](C['ROOT'])
    args.output.mkdir(parents=True, exist_ok=False)
    baseline = C['load'](C['HERE'] / 'vendor/pr904/candidate.json.gz')
    word, certificate = construct(baseline)
    C['write'](args.output / 'CERTIFICATE.json', certificate)
    (args.output / 'candidate.json.gz').write_bytes(gzip.compress(C['canonical'](word), mtime=0))
    print('BUILT_R439_FIVE_WIRE', certificate['counts'], 'saved_with_cleanup=', certificate['saved_with_cleanup'])
