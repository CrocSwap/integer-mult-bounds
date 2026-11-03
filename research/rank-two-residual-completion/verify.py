"""Replay the complete finite corpus and the independent shortest-word controls.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, deque
from pathlib import Path
import hashlib
import itertools
import json
import random
import runpy
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
C = runpy.run_path(str(ROOT / 'completion.py'))


def check(ok, message):
    if not ok:
        raise ValueError(message)


def pairing(x, y, n):
    total = 0
    for j in range(n):
        total += ((x >> j) & 1) * ((y >> (j+n)) & 1)
        total += ((y >> j) & 1) * ((x >> (j+n)) & 1)
    return total % 2


def turn(x, a, n):
    return x ^ (a if pairing(x, a, n) else 0)


def act(x, word, n):
    for a in word:
        check(0 < a < 1 << (2*n), 'oracle axis outside V')
        x = turn(x, a, n)
    return x


def lin(columns, x):
    y = 0
    for j, c in enumerate(columns):
        if x & (1 << j):
            y ^= c
    return y


def rank(vectors, width):
    rows = list(vectors)
    pivot = 0
    for j in range(width):
        selected = next((k for k in range(pivot, len(rows)) if rows[k] >> j & 1), None)
        if selected is None:
            continue
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        for k in range(len(rows)):
            if k != pivot and rows[k] >> j & 1:
                rows[k] ^= rows[pivot]
        pivot += 1
    return pivot


def inspect(n, source, image):
    answer = C['complete'](n, source, image)
    word = answer['word']
    columns = tuple(act(1 << j, word, n) for j in range(2*n))
    check(tuple(lin(columns, x) for x in source) == image, 'independent endpoint')
    for i in range(2*n):
        for j in range(2*n):
            check(pairing(columns[i], columns[j], n) == pairing(1 << i, 1 << j, n),
                  'independent full symplectic matrix')
    check(answer['upper'] == len(word), 'wrong word invoice')
    return answer


def embedding(rows):
    r = len(rows)
    n = 2*r
    displacement = []
    for i in range(r):
        v = 1 << i
        for j in range(i):
            if ((rows[i] >> j) ^ (rows[j] >> i)) & 1:
                v ^= 1 << (n+j)
        displacement.append(v)
    source = tuple((1 << (r+i)) ^ (row << n) for i, row in enumerate(rows))
    image = tuple(u ^ v for u, v in zip(source, displacement))
    # These prescribed spectators have zero pairing with the displacement.
    fixed = tuple(1 << (n+r+i) for i in range(r))
    return n, source + fixed, image + fixed


def rank_two_forms(r):
    forms = set()
    pairs = [(a, b) for a in range(1, 1 << r) for b in range(1, 1 << r) if a != b]
    for a, b in pairs:
        for c, d in pairs:
            forms.add(tuple((c if a >> i & 1 else 0) ^ (d if b >> i & 1 else 0)
                            for i in range(r)))
    return sorted(forms)


def full_group(n):
    identity = tuple(1 << i for i in range(2*n))
    distance = {identity: 0}
    queue = deque([identity])
    while queue:
        s = queue.popleft()
        for a in range(1, 1 << (2*n)):
            t = tuple(turn(x, a, n) for x in s)
            if t not in distance:
                distance[t] = distance[s] + 1
                queue.append(t)
    return distance


def subspaces(width):
    spaces = {frozenset([0])}
    for x in range(1, 1 << width):
        for space in tuple(spaces):
            spaces.add(space | frozenset(y ^ x for y in space))
    for space in sorted(spaces, key=lambda s: (len(s), sorted(s))):
        basis = []
        for x in sorted(space):
            if rank(basis + [x], width) > len(basis):
                basis.append(x)
        yield tuple(basis)


def ball_two(n, source):
    seen = {source: ()}
    for a in range(1, 1 << (2*n)):
        x = tuple(turn(v, a, n) for v in source)
        seen.setdefault(x, (a,))
        for b in range(1, 1 << (2*n)):
            y = tuple(turn(v, b, n) for v in x)
            seen.setdefault(y, (a, b))
    return seen


def run():
    counts = Counter()
    cases = Counter()
    for r in (3, 4):
        forms = rank_two_forms(r)
        check(len(forms) == ((2**r-1)*(2**r-2))**2 // 6, 'incomplete matrix census')
        for i, rows in enumerate(forms):
            check(rank(rows, r) == 2, 'independent form rank')
            n, source, image = embedding(rows)
            answer = inspect(n, source, image)
            cases[answer['case']] += 1
            counts['rank_two_forms'] += 1
            counts['fixed_spectators'] += r
            if not any(rows[j] >> j & 1 for j in range(r)) and C['anisotropic'](rows) is not None:
                counts['zero_diagonal_nonalternating'] += 1
            if i < 12:
                word = answer['word']
                for j in range(len(word)):
                    bad = word[:j] + word[j+1:]
                    check(tuple(act(x, bad, n) for x in source) != image, 'omitted turn survived')
                    counts['omitted_turns'] += 1
    rng = random.Random(20261103)
    for r in (5, 6, 7, 8):
        for _ in range(16):
            a, b = rng.sample(range(1, 1 << r), 2)
            c, d = rng.sample(range(1, 1 << r), 2)
            rows = tuple((c if a >> i & 1 else 0) ^ (d if b >> i & 1 else 0) for i in range(r))
            n, source, image = embedding(rows)
            axes = tuple(rng.randrange(1, 1 << (2*n)) for _ in range(5))
            source = tuple(act(x, axes, n) for x in source)
            image = tuple(act(x, axes, n) for x in image)
            inspect(n, source, image)
            counts['larger_conjugated'] += 1
    for n in (1, 2):
        group = full_group(n)
        check(len(group) == (6 if n == 1 else 720), 'incomplete symplectic group')
        for source in subspaces(2*n):
            minima = {}
            for matrix, distance in group.items():
                image = tuple(lin(matrix, x) for x in source)
                minima[image] = min(minima.get(image, distance), distance)
            for image, distance in minima.items():
                basis, _, rows = C['residual'](n, source, image)
                if rank(rows, len(rows)) > 2:
                    continue
                answer = inspect(n, source, image)
                check(answer['lower'] <= distance <= answer['upper'], 'wrong exact-distance interval')
                if answer['lower'] == answer['upper']:
                    check(answer['lower'] == distance, 'wrong claimed optimum')
                counts['exhaustive_small_partial_maps'] += 1
    boundaries = []
    for n, source, image, optimum in [
            (3, (16, 8, 1), (17, 10, 5), 5),
            (4, (32, 16, 128), (33, 18, 132), 4),
            (4, (32, 16, 8, 12), (33, 18, 12, 4), 6)]:
        answer = inspect(n, source, image)
        if optimum == 5:
            left, right = ball_two(n, source), ball_two(n, image)
            check(not left.keys() & right.keys(), 'four-turn obstruction failed')
            counts['mitm_endpoint_states'] = len(left) + len(right)
            counts['mitm_literal_words'] = 2*(1+63+63**2)
        if optimum == 6:
            word = (69, 71, 70, 76, 136, 140)
            check(tuple(act(x, word, n) for x in source) == image, 'six-turn closed witness')
            check(tuple(act(1 << i, word, n) for i in range(8)) ==
                  (1, 2, 8, 12, 18, 33, 192, 64), 'full closed witness')
            check(answer['escape_lift'] is None, 'false escape in closed witness')
        boundaries.append({'n': n, 'source': list(source), 'image': list(image),
                           'optimum': optimum, 'constructor': answer})
    invalid = [(0, (), ()), (17, (), ()), (True, (), ()), (2, [1], (1,)),
               (2, (1,), ()), (2, (1, 1), (1, 1)), (2, (1, 2), (1, 1)),
               (2, (1, 4), (1, 2)), (2, (-1,), (1,)), (2, (16,), (1,)),
               (3, (8, 16, 32), (9, 18, 36))]
    for args in invalid:
        try:
            C['complete'](*args)
        except ValueError:
            counts['invalid_contracts'] += 1
        else:
            raise ValueError('invalid contract accepted')
    for row in json.loads((ROOT / 'ORIGINS.json').read_text()):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            shutil.copytree(ROOT / 'inputs', dest / 'inputs')
            (dest / 'inputs').chmod(0o700)
            shutil.copyfile(ROOT / 'ORIGINS.json', dest / 'ORIGINS.json')
            shutil.copyfile(ROOT / 'completion.py', dest / 'completion.py')
            path = dest / row['local']
            path.chmod(0o600)
            path.write_bytes(path.read_bytes() + b'\n# source mutation\n')
            try:
                runpy.run_path(str(dest / 'completion.py'))
            except ValueError as error:
                check(str(error) == 'retained source hash mismatch', 'wrong source rejection')
                counts['source_corruptions'] += 1
            else:
                raise ValueError('damaged source accepted')
    names = ['completion.py', 'verify.py', 'PROOF.md', 'ORIGINS.json']
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in names}
    return {'status': 'PASS_RANK_TWO_RESIDUAL_COMPLETION', 'counts': dict(counts),
            'cases': dict(cases), 'sharp_boundaries': boundaries, 'source_hashes': hashes,
            'scope': 'All-size written bound; finite replay. Closed alternating classification remains open. No kappa.'}


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write']:
        (ROOT / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        check(not sys.argv[1:], 'unknown command option')
        check(result == json.loads((ROOT / 'RESULT.json').read_text()), 'receipt differs')
    print(json.dumps(result, sort_keys=True))
