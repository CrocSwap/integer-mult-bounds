#!/usr/bin/env python3
"""Bounded coupled frame search on the pinned PR531 scalar word.

Extends the frame-chain idea in icekylinx's coalesce_frames.py (retained in
research/direct-delivery504-global/code) to both propagation directions and
all A/B gates. Scalar coefficients/order, entrances, exits and cut frames stay
fixed. Exact entropy comparisons guide discovery; a new nonlinear moment,
Clifford recipes and global binding must still be checked independently.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
import math
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'research/direct-delivery504-global/evidence/local/FULL-WORD.json.gz'


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


@lru_cache(None)
def basis(vectors):
    pivots = {}
    for x in vectors:
        for p in sorted(pivots, reverse=True):
            if x >> p & 1:
                x ^= pivots[p]
        if x:
            p = x.bit_length() - 1
            for q in pivots:
                if pivots[q] >> p & 1:
                    pivots[q] ^= x
            pivots[p] = x
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


@lru_cache(None)
def span(frame):
    values = {0}
    for x in frame:
        values |= {y ^ x for y in values}
    return frozenset(values)


@lru_cache(None)
def meet(a, b):
    return basis(tuple(sorted(span(a) & span(b))))


@lru_cache(None)
def join(a, b):
    return basis(a + b)


def contained(a, b):
    return join(a, b) == b


def exact_gain(delta):
    """exp(old entropy - new entropy), using unchanged total rank mass."""
    require(sum(r * n for r, n in delta.items()) == 0, 'rank mass changed')
    result = Fraction(1)
    for r, n in delta.items():
        result *= Fraction(r) ** (r * n)
    return result


class Chains:
    def __init__(self, word):
        self.word = word
        self.v = len(word['ports'])
        self.h = word['report']['h']
        self.full = basis(tuple(1 << i for i in range(self.h)))
        self.nodes = []
        self.regs = [[] for _ in range(2 * self.v + word['report']['R'])]
        self.mutable = []
        starts = [(p,) for p in word['ports']] + [()] * (self.v + word['report']['R'])
        for r, frame in word.get('start_extra', {}).items():
            starts[int(r)] = tuple(frame)
        levels = {int(t): basis(tuple(f)) for t, f in word.get('target_levels', {}).items()}
        for r, f in enumerate(starts):
            self.add([r], f, 'start', None)
        for section in ('A', 'B'):
            if section == 'B':
                for r, f in zip(word['centers'], word['center_frames']):
                    self.add([r], f, 'barrier', None)
                for t in range(self.v):
                    self.add([self.v + t], levels.get(t, ()), 'barrier', None)
            for i, event in enumerate(word[section]):
                regs = event[1:3] if event[0] == 'add' else event[1:2]
                self.mutable.append(self.add(regs, event[-1], section, i))
        for r in range(len(self.regs)):
            f = self.full
            if self.v <= r < 2 * self.v:
                port = word['ports'][r - self.v]
                f = basis(tuple(x for x in range(1, 1 << self.h) if not (x & port).bit_count() % 2))
            self.add([r], f, 'final', None)
        self.prev, self.next = {}, {}
        for r, chain in enumerate(self.regs):
            for x, y in zip(chain, chain[1:]):
                self.next[x, r] = y
                self.prev[y, r] = x
        # The emitter has no implicit climb at a cut: lock its actual final
        # incident gate too. This prevents free unbilled barrier transitions.
        self.locked = {k for k, n in enumerate(self.nodes) if n['section'] not in ('A', 'B')}
        for k, n in enumerate(self.nodes):
            if n['section'] == 'barrier':
                for r in n['regs']:
                    p = self.prev[k, r]
                    require(self.nodes[p]['F'] == n['F'], 'initial cut mismatch')
                    self.locked.add(p)
        self.lower, self.upper = {}, {}
        for k, n in enumerate(self.nodes):
            value = ()
            if k in self.locked:
                value = n['F']
            else:
                for r in n['regs']:
                    value = join(value, self.lower[self.prev[k, r]])
            self.lower[k] = value
        for k in reversed(range(len(self.nodes))):
            n = self.nodes[k]
            value = self.full
            if k in self.locked:
                value = n['F']
            else:
                for r in n['regs']:
                    value = meet(value, self.upper[self.next[k, r]])
            self.upper[k] = value
        self.center_profile = Counter()
        for r, f in zip(word['centers'], word['center_frames']):
            current = basis(tuple(f))
            served = {levels.get(e[1] - self.v, ()) for e in word['cut'] if e[2] == r}
            for g in sorted(served, key=lambda x: (-len(x), x)):
                require(contained(g, current), 'center descent not nested')
                if current != g:
                    self.center_profile[len(current) - len(g)] += 1
                current = g

    def add(self, regs, frame, section, index):
        k = len(self.nodes)
        self.nodes.append(dict(regs=list(regs), F=basis(tuple(frame)), section=section, index=index))
        for r in regs:
            self.regs[r].append(k)
        return k

    def profile(self):
        result = self.center_profile.copy()
        for r, chain in enumerate(self.regs):
            for x, y in zip(chain, chain[1:]):
                f, g = self.nodes[x]['F'], self.nodes[y]['F']
                require(contained(f, g), ('nonmonotone', r, x, y))
                if self.nodes[y]['section'] == 'barrier':
                    require(f == g, 'unbilled cut transition')
                if f != g:
                    result[len(g) - len(f)] += 1
        return result

    def closure(self, seed, wanted, direction, limit):
        changed, queue = {}, [(seed, wanted)]
        links = self.next if direction == 'raise' else self.prev
        operation = join if direction == 'raise' else meet
        while queue:
            k, want = queue.pop()
            old = changed.get(k, self.nodes[k]['F'])
            new = operation(old, want)
            if new == old:
                continue
            if k in self.locked:
                return None
            changed[k] = new
            if len(changed) > limit:
                return None
            for r in self.nodes[k]['regs']:
                j = links[k, r]
                neighbor = changed.get(j, self.nodes[j]['F'])
                valid = contained(new, neighbor) if direction == 'raise' else contained(neighbor, new)
                if not valid:
                    queue.append((j, new))
        return changed

    def delta(self, changed):
        edges = {(self.prev[k, r], k, r) for k in changed for r in self.nodes[k]['regs']}
        edges |= {(k, self.next[k, r], r) for k in changed for r in self.nodes[k]['regs']}
        result = Counter()
        for x, y, _ in edges:
            f, g = self.nodes[x]['F'], self.nodes[y]['F']
            nf, ng = changed.get(x, f), changed.get(y, g)
            require(contained(nf, ng), 'invalid closure')
            if f != g:
                result[len(g) - len(f)] -= 1
            if nf != ng:
                result[len(ng) - len(nf)] += 1
        return {r: n for r, n in result.items() if n}

    def options(self, seed, direction, depth, lattice=False):
        links = self.next if direction == 'raise' else self.prev
        options = []
        for r in self.nodes[seed]['regs']:
            found, k, steps = [], seed, 0
            while (k, r) in links and steps < 128:
                k = links[k, r]
                f = self.nodes[k]['F']
                if f not in found:
                    found.append(f)
                steps += 1
                if len(found) >= depth or k in self.locked:
                    break
            options.append(found)
        result = set(x for row in options for x in row)
        if len(options) == 2:
            operation = meet if direction == 'raise' else join
            result |= {operation(a, b) for a in options[0] for b in options[1]}
        f = self.nodes[seed]['F']
        if lattice:
            if direction == 'raise':
                # All covers of F in the allowed subspace interval.
                result |= {join(f, (x,)) for x in span(self.upper[seed]) - span(f)}
            else:
                # Every codimension-one subspace is the kernel of a nonzero
                # functional in F's basis coordinates. Keep the fixed lower.
                for functional in range(1, 1 << len(f)):
                    pivot = (functional & -functional).bit_length() - 1
                    kernel = basis(tuple(f[i] ^ (f[pivot] if functional >> i & 1 else 0)
                                         for i in range(len(f)) if i != pivot))
                    if contained(self.lower[seed], kernel):
                        result.add(kernel)
        return sorted({join(f, g) if direction == 'raise' else meet(f, g) for g in result} - {f},
                      key=lambda g: (len(g), g))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, default=SOURCE)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--passes', type=int, default=3)
    parser.add_argument('--depth', type=int, default=4)
    parser.add_argument('--closure-limit', type=int, default=256)
    parser.add_argument('--lattice', action='store_true')
    parser.add_argument('--neutral-rounds', type=int, default=0,
                        help='Seeded equal-entropy moves between strict descent passes.')
    parser.add_argument('--seed', type=int, default=12026)
    args = parser.parse_args()
    require(args.passes > 0 and args.depth > 0 and args.closure_limit > 0, 'positive limits required')
    require(args.neutral_rounds >= 0, 'neutral rounds must be nonnegative')
    require(not args.out.exists(), 'use a new output directory')
    source = args.word.read_bytes()
    original = json.loads(gzip.decompress(source))
    word = copy.deepcopy(original)
    graph = Chains(word)
    before = graph.profile()
    require(dict(before) == {int(r): n for r, n in word['report']['local_profile'].items()}, 'input profile mismatch')
    trace, attempts, blocked, feasible = [], 0, 0, 0
    rng = random.Random(args.seed)
    seen = {tuple(n['F'] for n in graph.nodes)}
    neutral_moves = 0
    for pass_number in range(args.passes + args.neutral_rounds):
        accepted = 0
        for direction in ('raise', 'lower'):
            order = reversed(graph.mutable) if direction == 'raise' else iter(graph.mutable)
            for k in order:
                if k in graph.locked:
                    continue
                best = None
                for target in graph.options(k, direction, args.depth, args.lattice):
                    attempts += 1
                    changed = graph.closure(k, target, direction, args.closure_limit)
                    if not changed:
                        blocked += 1
                        continue
                    feasible += 1
                    delta = graph.delta(changed)
                    ratio = exact_gain(delta)
                    if ratio > 1 and (best is None or ratio > best[0]):
                        best = ratio, changed, delta
                if best is None:
                    continue
                ratio, changed, delta = best
                updates = []
                for j, frame in sorted(changed.items()):
                    node = graph.nodes[j]
                    updates.append(dict(section=node['section'], index=node['index'],
                                        old=list(node['F']), new=list(frame)))
                    node['F'] = frame
                trace.append(dict(pass_number=pass_number, direction=direction,
                                  entropy_gain_ratio=str(ratio), delta=delta, updates=updates))
                accepted += 1
        print(json.dumps(dict(pass_number=pass_number, accepted=accepted, attempts=attempts,
                              profile=dict(sorted(graph.profile().items())))), flush=True)
        if not accepted:
            if pass_number >= args.neutral_rounds:
                break
            choices = list(graph.mutable)
            rng.shuffle(choices)
            moved = False
            for k in choices:
                if k in graph.locked:
                    continue
                directions = ['raise', 'lower']
                rng.shuffle(directions)
                for direction in directions:
                    candidates = graph.options(k, direction, args.depth, args.lattice)
                    rng.shuffle(candidates)
                    for target in candidates:
                        attempts += 1
                        changed = graph.closure(k, target, direction, args.closure_limit)
                        if not changed:
                            blocked += 1
                            continue
                        feasible += 1
                        delta = graph.delta(changed)
                        if exact_gain(delta) != 1:
                            continue
                        state = tuple(changed.get(j, n['F']) for j,n in enumerate(graph.nodes))
                        if state in seen:
                            continue
                        seen.add(state)
                        updates = []
                        for j, frame in sorted(changed.items()):
                            n = graph.nodes[j]
                            updates.append(dict(section=n['section'], index=n['index'], old=list(n['F']), new=list(frame)))
                            n['F'] = frame
                        trace.append(dict(pass_number=pass_number, direction=direction,
                                          entropy_gain_ratio='1', delta=delta, updates=updates))
                        neutral_moves += 1
                        moved = True
                        break
                    if moved:
                        break
                if moved:
                    break
            if not moved:
                break
    after = graph.profile()
    for k in graph.mutable:
        node = graph.nodes[k]
        word[node['section']][node['index']][-1] = list(node['F'])
    for section in ('A', 'B'):
        require([e[:-1] for e in word[section]] == [e[:-1] for e in original[section]], 'scalar word changed')
    require(all(word[k] == original[k] for k in original if k not in ('A', 'B', 'report')), 'fixed data changed')
    require(sum(r*n for r,n in before.items()) == sum(r*n for r,n in after.items()), 'rank mass changed')
    word['report']['local_profile'] = dict(sorted(after.items()))
    word['report']['status'] = 'COUPLED_FRAME_SEARCH_CANDIDATE_REQUIRES_PHASE_AND_GLOBAL_REPLAY'
    payload = gzip.compress(json.dumps(word, sort_keys=True, separators=(',', ':')).encode(), mtime=0)
    gain = exact_gain({r:after[r]-before[r] for r in before.keys() | after.keys()})
    result = dict(status='LOCAL_CANDIDATE' if gain > 1 else 'NO_GAIN_IN_BOUNDED_SEARCH',
                  source_sha256=hashlib.sha256(source).hexdigest(), output_sha256=hashlib.sha256(payload).hexdigest(),
                  parameters=dict(passes=args.passes, depth=args.depth, closure_limit=args.closure_limit,
                                  lattice=args.lattice, neutral_rounds=args.neutral_rounds, seed=args.seed),
                  attempts=attempts, blocked=blocked, feasible=feasible, accepted_groups=len(trace),
                  neutral_moves=neutral_moves,
                  profile_before=dict(sorted(before.items())), profile_after=dict(sorted(after.items())),
                  entropy_saving=sum(r*(before[r]-after[r])*math.log(73/r) for r in before.keys() | after.keys()),
                  trace=trace, scope='Scalar word and frame chains only; phases, ownership bindings and exact assembly remain separate.')
    args.out.mkdir(parents=True)
    (args.out / 'FULL-WORD.json.gz').write_bytes(payload)
    (args.out / 'SEARCH.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'trace'}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
