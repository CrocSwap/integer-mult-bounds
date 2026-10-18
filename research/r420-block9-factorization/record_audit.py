"""Independent column-by-column record interpreter; imports no project code.

New code: Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from math import gcd
import json
import struct


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    """Fraction-free elimination, independent of the predecessor's Q-RREF."""
    basis = {}
    for row in rows:
        row = list(row)
        for p, previous in sorted(basis.items()):
            if row[p]:
                a, b = previous[p], row[p]
                row = [a * x - b * y for x, y in zip(row, previous)]
                divisor = 0
                for value in row:
                    divisor = gcd(divisor, abs(value))
                if divisor:
                    row = [x // divisor for x in row]
        if any(row):
            p = next(i for i, x in enumerate(row) if x)
            basis[p] = row
    return len(basis)


def expected_records(word):
    frames = [[word['lines'][i] for i in f] for f in word['frames']]
    dims = [rank(f) for f in frames]
    current = list(word['start'])
    paths = [[f] for f in current]
    events, nested = [], {}
    n = 2 * word['v'] + word['R']
    zero = dims.index(0)

    def move(r, f):
        before = current[r]
        if before == f:
            return
        pair = (before, f)
        if pair not in nested:
            nested[pair] = rank(frames[before] + frames[f]) == dims[f]
        require(nested[pair] and dims[f] > dims[before], 'illegal frame climb')
        events.append((0, r, before, f, dims[f] - dims[before], 0))
        paths[r].append(f)
        current[r] = f

    def gates(name, phase):
        for f, d, sources in word[name]:
            for r in [d] + sources:
                move(r, f)
            for s in sources:
                events.append((1, d, s, 1, f, phase))

    gates('D', 1)
    gates('A', 2)
    for index, center in enumerate(word['ret']):
        frame = current[center]
        events.append((2, center, n, frame, zero, dims[frame]))
        for t, row in enumerate(word['scatter']):
            if index in row:
                events.append((1, word['v'] + t, n, 1, zero, 3))
        events.append((3, center, n, frame, zero, 0))
    gates('B', 4)
    gates('C', 5)
    for r, f in enumerate(word['final']):
        move(r, f)
    return events, paths


def interpret(events, n, v, replay_columns=True):
    """Check lifecycle and positive prefixes in both program orientations."""
    summaries = []
    scalar = [e for e in events if e[0] != 0]
    for reverse in [False, True]:
        stream = scalar[::-1] if reverse else scalar
        norms = [1] * n + [0]
        maximum, center, copies, additions = 1, None, 0, 0
        for op, a, b, c, _, _ in stream:
            if reverse and op in (2, 3):
                op = 5 - op
            if op == 1:
                require(0 <= a < n and 0 <= b <= n and a != b, 'ADD register')
                require(b != n or center is not None, 'read unopened COPY')
                require(center is None or a != center, 'modified copied center')
                norms[a] += abs(c) * norms[b]
                maximum = max(maximum, norms[a])
                additions += 1
            elif op == 2:
                require(center is None and b == n and 0 <= a < n, 'COPY lifecycle')
                center, norms[n] = a, norms[a]
                maximum = max(maximum, norms[n])
                copies += 1
            elif op == 3:
                require(center == a and b == n, 'ERASE lifecycle')
                center, norms[n] = None, 0
            else:
                raise ValueError('unknown record opcode')
        require(center is None and norms[n] == 0, 'unclosed COPY')
        if replay_columns:
            # One independent basis column at a time, represented by active rows.
            # The inherited checker instead propagates every row's bitmask at once.
            for column in range(n):
                active = {column}
                for op, a, b, c, _, _ in stream:
                    if reverse and op in (2, 3):
                        op = 5 - op
                    if op == 1:
                        if c % 2 and b in active:
                            if a in active:
                                active.remove(a)
                            else:
                                active.add(a)
                    elif op == 2:
                        active.discard(n)
                        if a in active:
                            active.add(n)
                    else:
                        active.discard(n)
                wanted = {column, v + column} if column < v else {column}
                require(active == wanted, f'wrong column {column}, reverse={reverse}')
        summaries.append({'reverse': reverse, 'additions': additions, 'copies': copies,
                          'norm_bound': maximum, 'columns_checked': n if replay_columns else 0})
    return summaries


def audit(word, raw):
    require(len(raw) % 24 == 0, 'unaligned record stream')
    records = list(struct.iter_unpack('<6i', raw))
    expected, paths = expected_records(word)
    require(records == expected, 'exported record stream differs from literal word')
    n, v = 2 * word['v'] + word['R'], word['v']
    directions = interpret(records, n, v)
    profile = Counter()
    for op, _, _, _, rank_delta, copy_rank in records:
        if op == 0:
            require(rank_delta > 0, 'nonpositive MOVE rank')
            profile[rank_delta] += 1
        elif op == 2:
            profile[copy_rank] += 1
    profile = {str(k): count for k, count in sorted(profile.items())}
    return {
        'records': len(records), 'moves': sum(e[0] == 0 for e in records),
        'directions': directions, 'rank_profile': profile,
        'rank_mass': sum(int(k) * count for k, count in profile.items()),
        'paths_sha256': sha256(json.dumps(paths, separators=(',', ':')).encode()).hexdigest(),
        'records_sha256': sha256(raw).hexdigest(),
    }, paths
