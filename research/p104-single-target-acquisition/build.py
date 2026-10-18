"""Search for acquisition certificates; the verifier imports none of this code.

Extends ywz65/PR2496's all-episode antichain and chronological path method.
Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


@lru_cache(None)
def span(basis):
    space = {0}
    for vector in basis:
        space |= {x ^ vector for x in list(space)}
    return frozenset(space)


def data():
    pins = json.loads((PACKAGE/'SOURCES.json').read_text())
    for pin in pins['files']:
        if pin['usage'] == 'input':
            digest = hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()
            if digest != pin['sha256']:
                raise ValueError('source digest: ' + pin['path'])
    ip = ROOT/'research/p104-native-channel/inputs'
    word = json.loads((ip/'LOWRANK-WITNESS.json').read_text())
    fixture = json.loads((ip/'P104-FIXTURE.json').read_text())['section4_explicit_P104']
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0]*8
            row[i], row[j] = 2, 2*sign
            roots.add(tuple(row))
    for tail in product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            roots.add((1, *tail))
    roots = sorted(roots - set(map(tuple, fixture['F0']+fixture['C'])))
    paths = {s:[[0, None, tuple(word['initial_frames'][f'X{s}'])]] for s in range(104)}
    for i, event in enumerate(word['program']):
        if event[0] == 'transport' and event[1].startswith('X'):
            s = int(event[1][1:])
            paths[s][-1][1] = i
            paths[s].append([i+1, None, tuple(event[3])])
    for path in paths.values():
        path[-1][1] = len(word['program'])
    return word, roots, paths


def instance(t, word, roots, paths):
    hyperplane = span(tuple(word['final_frames'][f'Y{t}']))
    required = [s for s in range(104) if 8*(s == t) != sum(a*b for a, b in zip(roots[s], roots[t]))]
    allowed = {s:[e for e in paths[s] if span(e[2]) <= hyperplane] for s in required}
    adjacent = {s:set() for s in required}
    for a, b in combinations(required, 2):
        if any(span(x[2]) <= span(y[2]) or span(y[2]) <= span(x[2])
               for x in allowed[a] for y in allowed[b]):
            adjacent[a].add(b)
            adjacent[b].add(a)
    components, todo = [], set(required)
    while todo:
        stack = [min(todo)]
        todo.remove(stack[0])
        component = []
        while stack:
            x = stack.pop()
            component.append(x)
            for y in adjacent[x] & todo:
                todo.remove(y)
                stack.append(y)
        components.append(sorted(component))
    return allowed, adjacent, components


def component_solution(component, allowed, adjacent):
    n = len(component)
    if n > 12:
        raise ValueError('outside the declared finite search domain')
    full = (1 << n)-1
    # For each acquired subset and current frame, an earlier time dominates a later one.
    states = [{} for _ in range(1 << n)]
    states[0][()] = (0, [])
    feasible = {}
    for mask in range(1 << n):
        for frame, (cut, path) in list(states[mask].items()):
            feasible.setdefault(mask, path)
            for j, source in enumerate(component):
                if mask >> j & 1:
                    continue
                for lo, hi, next_frame in allowed[source]:
                    when = max(cut, lo)
                    if when > hi or not span(frame) <= span(next_frame):
                        continue
                    next_mask = mask | (1 << j)
                    old = states[next_mask].get(next_frame)
                    if old is None or when < old[0]:
                        states[next_mask][next_frame] = (
                            when, path + [[source, when, list(next_frame)]])
    best, parts = [n+1]*(1 << n), [None]*(1 << n)
    best[0], parts[0] = 0, []
    for mask in range(1, 1 << n):
        first = mask & -mask
        for subset, path in feasible.items():
            if subset & first and subset & mask == subset and best[mask ^ subset]+1 < best[mask]:
                best[mask] = best[mask ^ subset]+1
                parts[mask] = parts[mask ^ subset]+[path]
    antichain = []
    for mask in range(1 << n):
        if mask.bit_count() <= len(antichain):
            continue
        sources = [component[j] for j in range(n) if mask >> j & 1]
        if all(b not in adjacent[a] for a, b in combinations(sources, 2)):
            antichain = sources
    return antichain, parts[full]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    word, roots, paths = data()
    records = []
    for target in range(104):
        allowed, adjacent, components = instance(target, word, roots, paths)
        antichain, chains = [], []
        for component in components:
            if len(component) == 1:
                antichain += component
                source = component[0]
                lo, _, basis = allowed[source][0]
                chains.append([[source, lo, list(basis)]])
            else:
                lower, upper = component_solution(component, allowed, adjacent)
                antichain += lower
                chains += upper
        records.append({'target':target, 'lower_bound':len(antichain),
                        'upper_bound':len(chains), 'antichain_sources':sorted(antichain),
                        'paths':chains})
    result = {'schema_version':1, 'targets':records}
    with args.out.open('x', encoding='utf-8') as out:
        json.dump(result, out, indent=2)
        out.write('\n')
    print('GENERATED_P104_SINGLE_TARGET_CERTIFICATE targets=104')


if __name__ == '__main__':
    main()
