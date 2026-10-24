"""Rebuild the complete scalar catalogue and run two exact relation checks."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time

SOURCE = Path(__file__).resolve().parent
OFF = 0x7bde
PERMUTATIONS = list(itertools.permutations(range(4)))
EXPECTED_INPUTS = {
    2: (27156, 'f185daf27eb890d75698c14f8ce83e954fd2fc6ed07188908378fac44a2789ee'),
    3: (1901600, '97ba623789da03fb0b83bc038d1e235691d96dcbb5c028ff72f0c108b2d71911'),
}


def outer(x, y):
    return sum(y << (4*i) for i in range(4) if x >> i & 1)


def rank(vectors):
    pivots = {}
    for v in vectors:
        while v:
            k = v.bit_length()-1
            if k in pivots:
                v ^= pivots[k]
            else:
                pivots[k] = v
                break
    return len(pivots)


def strong(space):
    edges = 0
    for v in space:
        edges |= v
    for start in range(4):
        seen = 1 << start
        while True:
            nxt = seen
            for j in range(4):
                if seen >> j & 1:
                    nxt |= (edges >> (4*j)) & 15
            if nxt == seen:
                break
            seen = nxt
        if seen != 15:
            return False
    return True


def canonical(space):
    return min(tuple(sorted(sum(((v >> (4*i+j)) & 1) << (4*p[i]+p[j])
               for i in range(4) for j in range(4)) for v in space))
               for p in PERMUTATIONS)


def catalogue():
    projectors = [(x, y, outer(x, y)) for x in range(1, 16)
                  for y in range(1, 16) if (x & y).bit_count() % 2]
    patterns = sorted({m & OFF for x, y, m in projectors}-{0})
    spaces = {(0,)}
    levels = []
    for dimension in range(1, 4):
        nxt = set()
        for space in spaces:
            for v in patterns:
                if v not in space:
                    nxt.add(tuple(sorted(space+tuple(x ^ v for x in space))))
        spaces = nxt
        irred = [s for s in spaces if strong(s)]
        reps = sorted({canonical(s) for s in irred})
        levels.append({'dimension': dimension, 'spaces': len(spaces),
                       'irreducible_spaces': len(irred),
                       'representatives': [{'space': s, 'projectors': [(x, y) for x, y, m in projectors if m & OFF in s]} for s in reps]})
        print('Catalogue:', dimension, len(spaces), len(irred), len(reps), flush=True)
    assert [(r['spaces'], r['irreducible_spaces'], len(r['representatives'])) for r in levels] == [(104, 0, 0), (4964, 634, 45), (140281, 63567, 2846)]
    return levels


def irreducible(projectors):
    for start in range(1, 16):
        span = {0, start}
        while True:
            old = set(span)
            for x, y in projectors:
                if x not in span and any((v & y).bit_count() % 2 for v in span):
                    span |= {v ^ x for v in tuple(span)}
            if span == old:
                break
        if len(span) < 16:
            return False
    return True


def normalize(word, commute):
    left = list(range(len(word)))
    result = []
    while left:
        choices = [i for i in left if all(commute[word[j]][word[i]] for j in left if j < i)]
        i = min(choices, key=lambda j: (word[j], j))
        result.append(word[i])
        left.remove(i)
    return tuple(result)


def orders(counts, commute, word=()):
    if not any(counts):
        if word <= normalize(word[::-1], commute):
            yield word
        return
    for j, count in enumerate(counts):
        if not count:
            continue
        blocked = False
        for old in reversed(word):
            if not commute[old][j]:
                break
            if old > j:
                blocked = True
                break
        if blocked:
            continue
        counts[j] -= 1
        yield from orders(counts, commute, word+(j,))
        counts[j] += 1


def rank_two(pools, build):
    families = []
    multisets = 0
    for pool_index, pool in enumerate(pools):
        ns = pool['projectors']
        cached = {}
        for choice in itertools.combinations_with_replacement(range(len(ns)), 8):
            multisets += 1
            counts = [choice.count(i) for i in range(len(ns))]
            support = tuple(i for i, c in enumerate(counts) if c)
            if rank([outer(*ns[i]) & OFF for i in support]) != 2:
                continue
            allowed = set(range(4))
            for side in (0, 1):
                for r in range(1, 16):
                    if sum(counts[i]*((r & ns[i][side]).bit_count() % 2) for i in support) < 3:
                        allowed &= {r.bit_length()-1} if r.bit_count() == 1 else set()
            if not allowed:
                continue
            if support not in cached:
                cached[support] = irreducible([ns[i] for i in support])
            if not cached[support]:
                continue
            allowed = [a for a in sorted(allowed) if rank([outer(*ns[i]) & (OFF | 1 << (5*a)) for i in support]) <= 3]
            if allowed:
                families.append({'pool': pool_index, 'projectors': ns, 'counts': counts, 'ancillas': allowed})
    assert multisets == 61347 and len(families) == 103
    count = 0
    with (build/'rank2.bin').open('wb') as f:
        for family in families:
            ns = family['projectors']
            commute = [[a == b or (not ((a[0] & b[1]).bit_count() % 2) and not ((b[0] & a[1]).bit_count() % 2)) for b in ns] for a in ns]
            for word in orders(list(family['counts']), commute):
                f.write(struct.pack('<9H', *(outer(*ns[i]) for i in word), sum(1 << a for a in family['ancillas'])))
                count += 1
    return {'multisets': multisets, 'families': len(families), 'words': count}


def run(command, output, errors):
    with output.open('w') as out, errors.open('w') as err:
        subprocess.run([str(x) for x in command], stdout=out, stderr=err, check=True)


def rank_three(pools, build):
    with (build/'pools.txt').open('w') as f:
        f.write(f'{len(pools)}\n')
        for pool in pools:
            s = pool['space']
            assert all(s[i] ^ s[j] == s[i ^ j] for i in range(8) for j in range(8))
            f.write(f"{len(pool['projectors'])}\n")
            for x, y in pool['projectors']:
                f.write(f'{x} {y} {s.index(outer(x, y) & OFF)}\n')
    run([build/'multisets', build/'pools.txt'], build/'multisets.jsonl', build/'multisets.log')
    families = [json.loads(line) for line in (build/'multisets.jsonl').read_text().splitlines()]
    with (build/'orders.txt').open('w') as f:
        f.write(f'{len(families)}\n')
        for family in families:
            ns = pools[family['class']]['projectors']
            f.write(f"{len(ns)} {family['possible_ancilla']}\n")
            for (x, y), count in zip(ns, family['counts']):
                f.write(f'{x} {y} {count}\n')
    run([build/'orders', build/'orders.txt'], build/'orders.jsonl', build/'orders.log')
    count = 0
    with (build/'rank3.bin').open('wb') as out, (build/'orders.jsonl').open() as inp:
        for line in inp:
            row = json.loads(line)
            ns = pools[families[row['family']]['class']]['projectors']
            out.write(struct.pack('<9H', *(outer(*ns[i]) for i in row['order']), row['ancilla_mask']))
            count += 1
    multiset_stats = json.loads((build/'multisets.log').read_text().splitlines()[-1])
    order_stats = json.loads((build/'orders.log').read_text().splitlines()[-1])
    assert multiset_stats == {'classes': 2846, 'multisets': 11210628, 'distance_ok': 8623, 'rank_ok': 4020, 'irreducible': 4020}
    assert order_stats == {'families': 4020, 'prefixes': 28785353, 'commutation_orders': 7121514, 'reversal_orders': 3560923, 'parity_survivors': 1901600}
    assert count == order_stats['parity_survivors']
    return {'multisets': multiset_stats, 'orders': order_stats}


def json_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path, help='New directory for all generated files')
    args = parser.parse_args()
    build = args.build.resolve()
    build.mkdir(parents=True, exist_ok=False)
    compiler = os.environ.get('CXX') or shutil.which('clang++') or shutil.which('g++')
    if not compiler:
        raise RuntimeError('A C++17 compiler is required')
    started = time.time()
    for name in ('multisets', 'orders', 'rational', 'field101'):
        subprocess.run([compiler, '-O3', '-std=c++17', str(SOURCE/(name+'.cpp')), '-o', str(build/name)], check=True)
    levels = catalogue()
    result = {'rank2': rank_two(levels[1]['representatives'], build),
              'rank3': rank_three(levels[2]['representatives'], build), 'inputs': {}, 'engines': {}}
    for dimension in (2, 3):
        inp = build/f'rank{dimension}.bin'
        count, digest = EXPECTED_INPUTS[dimension]
        actual = hashlib.sha256(inp.read_bytes()).hexdigest()
        assert inp.stat().st_size == 18*count and actual == digest
        result['inputs'][str(dimension)] = {'records': count, 'sha256': actual}
        rational = build/f'rational{dimension}'
        field = build/f'field{dimension}.jsonl'
        run([build/'rational', inp, rational, 'dirty'], build/f'rational{dimension}.summary.json', build/f'rational{dimension}.log')
        run([build/'field101', inp, field], build/f'field{dimension}.stdout', build/f'field{dimension}.log')
        a = json_lines(Path(str(rational)+'.chunks.jsonl'))
        b = json_lines(field)
        ta = json_lines(Path(str(rational)+'.terminals.jsonl'))
        tb = json_lines(Path(str(field)+'.terminals.jsonl'))
        assert ta == tb
        assert [(r['end'], r['terminals'], r['robust']) for r in a] == [(r['words'], r['terminals'], r['robust']) for r in b]
        assert a[-1]['end'] == count and a[-1]['terminals'] == (0 if dimension == 2 else 538) and a[-1]['robust'] == 0
        result['engines'][str(dimension)] = {'rational': a[-1], 'field101': b[-1], 'terminal_word_agreement': True, 'chunk_agreement': True}
        print('Exact checks:', dimension, count, a[-1]['terminals'], 0, flush=True)
    result['catalogue'] = [{k: v for k, v in r.items() if k != 'representatives'} | {'classes': len(r['representatives'])} for r in levels]
    result['source_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(SOURCE.iterdir()) if p.suffix in ('.cpp', '.py')}
    result['seconds'] = time.time()-started
    result['status'] = 'PASS_COMPLETE_FINITE_CHECKS'
    (build/'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Receipt:', build/'receipt.json', flush=True)


if __name__ == '__main__':
    main()
