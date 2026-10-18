"""Second implementation: enumerated spaces and dense scaled-integer rows.

No imports from build.py or verify.py. Same AI-assisted author, not human review.
Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from functools import cache
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def check(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


@cache
def span(basis):
    result = {0}
    for b in basis:
        check(type(b) is int and 0 < b < 512, 'basis scalar')
        result.update(x ^ b for x in list(result))
    check(len(result) == 2**len(basis), 'basis rank')
    return frozenset(result)


def main():
    for pin in read(P/'SOURCES.json')['files']:
        if pin['usage'] == 'input':
            check(hashlib.sha256((ROOT/pin['path']).read_bytes()).hexdigest()
                  == pin['sha256'], 'source digest')
    ip = ROOT/'research/p104-native-channel/inputs'
    original = read(ip/'LOWRANK-WITNESS.json')
    f = read(ip/'P104-FIXTURE.json')['section4_explicit_P104']
    roots = []
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            root = [0]*8
            root[i], root[j] = a, b
            roots.append(tuple(root))
    roots.extend(r for r in product((-1, 1), repeat=8) if sum(x < 0 for x in r) % 2 == 0)
    positive = {r for r in roots if next(x for x in r if x) > 0}
    check(len(roots) == 240 and len(positive) == 120, 'full root enumeration')
    rr = sorted(positive - set(map(tuple, f['F0']+f['C'])))
    g8 = [[sum(a*b for a, b in zip(x, y)) for y in rr] for x in rr]
    cert = read(P/'CERTIFICATE.json')['targets']
    check([r['target'] for r in cert] == list(range(104)), 'target coverage')
    original_names = list(original['initial_frames'])
    total, distribution = 0, Counter()
    for rec in cert:
        t, paths = rec['target'], rec['paths']
        n, h = len(paths), span(tuple(original['final_frames'][f'Y{t}']))
        correction8 = [8*(s == t)-g8[t][s] for s in range(104)]
        # Check all source-frame possibilities without using the primary episode builder.
        families = {s: {span(tuple(original['initial_frames'][f'X{s}']))}
                    for s in range(104)}
        for e in original['program']:
            if e[0] == 'transport' and e[1].startswith('X'):
                families[int(e[1][1:])].add(span(tuple(e[3])))
        families = {s: [a for a in fam if a <= h] for s, fam in families.items()}
        anti = rec['antichain_sources']
        check(len(set(anti)) == n == rec['lower_bound'] == rec['upper_bound'], 'matched witnesses')
        check(all(correction8[s] and families[s] for s in anti), 'necessary source witnesses')
        for a, b in combinations(anti, 2):
            check(all(not (x <= y or y <= x) for x in families[a] for y in families[b]),
                  'source-family antichain')
        names = original_names + [f'L{i}' for i in range(n)]
        index = {name:i for i, name in enumerate(names)}
        width, scale = len(names), 16
        states = {name:[scale*int(i == j) for j in range(width)]
                  for name, i in index.items()}
        frames = {name:span(tuple(b)) for name, b in original['initial_frames'].items()}
        frames.update({f'L{i}':frozenset({0}) for i in range(n)})
        captures = {}
        for i, path in enumerate(paths):
            for source, cut, basis in path:
                captures.setdefault(cut, []).append((i, source, tuple(basis)))
        selected = sorted(s for path in paths for s, _, _ in path)
        check(selected == [s for s in range(104) if correction8[s]], 'capture partition')
        target = f'Y{t}'
        # All initial dirt cancellation occurs before any capture or old event.
        for i in range(n):
            states[target][index[f'L{i}']] -= scale
        # Exact dense integer ADD with an explicit divisibility check.
        def add(dst, src, numerator, denominator):
            check(frames[dst] == frames[src], 'common frame')
            scaled = [numerator*x for x in states[src]]
            check(all(x % denominator == 0 for x in scaled), 'exact fixed-grid arithmetic')
            states[dst] = [a+b//denominator for a, b in zip(states[dst], scaled)]
        for cut in range(len(original['program'])+1):
            for i, s, basis in captures.get(cut, []):
                helper, sf = f'L{i}', span(basis)
                check(frames[helper] <= sf <= h and frames[f'X{s}'] == sf, 'chronological acquisition')
                frames[helper] = sf
                add(helper, f'X{s}', correction8[s], 8)
            if cut == len(original['program']):
                break
            e = original['program'][cut]
            op, dst = e[:2]
            if op == 'transport':
                a, b = span(tuple(e[2])), span(tuple(e[3]))
                check(frames[dst] == a and (a < b or b < a), 'original frame transport')
                frames[dst] = b
            elif op == 'add':
                check(frames[dst] == span(tuple(e[4])), 'original ADD frame')
                q = Fraction(e[3])
                add(dst, e[2], q.numerator, q.denominator)
            elif op == 'zero':
                check(dst not in states and dst == 'C', 'private allocation')
                states[dst], frames[dst] = [0]*width, span(tuple(e[2]))
            elif op == 'copy':
                check(not any(states[dst]) and frames[dst] == frames[e[2]] == span(tuple(e[3])), 'private copy')
                states[dst] = states[e[2]].copy()
            elif op == 'erase':
                check(dst == 'C' and frames[dst] == span(tuple(e[2])), 'private discard')
                del states[dst], frames[dst]
            else:
                raise ValueError('unknown event')
        full = frozenset(range(512))
        for i, path in enumerate(paths):
            helper = f'L{i}'
            check(frames[helper] <= h and frames[target] == h, 'target arrival')
            frames[helper] = h
            add(target, helper, 1, 1)
            frames[helper] = full
            for s, _, _ in path:
                add(helper, f'X{s}', -correction8[s], 8)
        check(set(states) == set(names), 'private closure')
        for name, i in index.items():
            expected = [scale*int(i == j) for j in range(width)]
            if name.startswith('Y'):
                y = int(name[1:])
                for s in range(104):
                    expected[index[f'X{s}']] += scale*int(s == y) if y == t else 2*g8[y][s]
            check(states[name] == expected, 'dense all-input endpoint')
            expected_frame = full if name.startswith('L') else span(tuple(original['final_frames'][name]))
            check(frames[name] == expected_frame, 'dense final frame')
        total += width**2
        distribution[n] += 1
    check({str(k):v for k,v in sorted(distribution.items())} == read(P/'RESULT.json')['distribution'], 'distribution')
    check(total == read(P/'RESULT.json')['total_endpoint_coefficients'], 'endpoint coverage')
    print('PASS_P104_SINGLE_TARGET_DENSE targets=104 coefficients=' + str(total))


if __name__ == '__main__':
    main()
