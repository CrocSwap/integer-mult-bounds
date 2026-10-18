"""Small exact order/frame oracle; imports no predecessor implementation.

Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
The coordinate-frame oracle is for the synthetic fixture, not E8 geometry.
"""
from collections import Counter
from itertools import accumulate
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def operations(word):
    require(all(len(g[2]) == 1 for sec in 'AB' for g in word[sec]),
            'small oracle requires single-source gates')
    return {sec: tuple(((sec, i), t, us[0]) for i, (_, t, us) in enumerate(word[sec]))
            for sec in 'AB'}


def commuting(a, b):
    return a[1] != b[2] and b[1] != a[2]


def apply(state, move):
    sec, index, dst, slot = move
    result = {s: list(ops) for s, ops in state.items()}
    op = result[sec].pop(index)
    result[dst].insert(slot, op)
    return {s: tuple(ops) for s, ops in result.items()}


def moves(word, state, *, quotient, registers=None):
    """Brute insertion positions, then optional own-register trace quotient.

    Predecessor search.py walks outward and emits a position at each contact.
    Here every position is tested against all crossed gates before grouping.
    """
    result = []
    targets = set(range(word['v'], 2 * word['v']))
    for sec in 'AB':
        for index, op in enumerate(state[sec]):
            own = set(op[1:])
            if registers is not None and not own & registers:
                continue
            rest = state[sec][:index] + state[sec][index + 1:]
            original_signature = tuple(sum(r in x[1:] for x in rest[:index])
                                       for r in sorted(own))
            grouped = {}
            for slot in range(len(rest) + 1):
                if slot == index:
                    continue
                crossed = rest[min(slot, index):max(slot, index)]
                if not all(commuting(op, other) for other in crossed):
                    continue
                signature = tuple(sum(r in x[1:] for x in rest[:slot])
                                  for r in sorted(own))
                if quotient and signature == original_signature:
                    continue
                grouped.setdefault(signature, []).append(slot)
            for slots in grouped.values():
                selected = [min(slots, key=lambda q: (abs(q - index), q))] if quotient else slots
                result.extend((sec, index, sec, q) for q in selected)
            if op[1] in targets or op[1] in word['ret'] or op[2] in targets:
                continue
            crossed = rest[index:] if sec == 'A' else rest[:index]
            if not all(commuting(op, other) for other in crossed):
                continue
            dst = 'B' if sec == 'A' else 'A'
            grouped = {}
            for slot in range(len(state[dst]) + 1):
                crossed = state[dst][:slot] if sec == 'A' else state[dst][slot:]
                if not all(commuting(op, other) for other in crossed):
                    continue
                signature = tuple(sum(r in x[1:] for x in state[dst][:slot])
                                  for r in sorted(own))
                grouped.setdefault(signature, []).append(slot)
            for slots in grouped.values():
                selected = [min(slots) if sec == 'A' else max(slots)] if quotient else slots
                result.extend((sec, index, dst, q) for q in selected)
    require(len(result) == len(set(result)), 'duplicate independently generated move')
    return sorted(result)


def expanded(profile):
    return sorted((r for r, n in profile for _ in range(n)), reverse=True)


def majorizes(left, right):
    """Equal mass, larger prefix sums: smaller cost for every concave power."""
    a, b = expanded(left), expanded(right)
    if sum(a) != sum(b):
        return False
    size = max(len(a), len(b))
    a += [0] * (size - len(a))
    b += [0] * (size - len(b))
    return all(x >= y for x, y in zip(accumulate(a), accumulate(b)))


def frame_profiles(word, state):
    """Enumerate all closed coordinate frames, counting every climb and C.

    The eight independent coordinate lines make every mask a closed frame.
    This deliberately does not call the predecessor's optimum/cost routines.
    """
    degree = len(word['lines'])
    require(word['lines'] == [[int(i == j) for j in range(degree)] for i in range(degree)],
            'coordinate-frame domain changed')
    require(not word['D'] and not word['ret'], 'small oracle boundary domain changed')
    masks = [sum(1 << j for j in fr) for fr in word['frames']]
    full = (1 << degree) - 1
    current = [masks[f] for f in word['start']]
    final = [masks[f] for f in word['final']]
    gates = state['A'] + state['B']
    result = Counter()

    def visit(index, frames, histogram):
        if index == len(gates):
            frames = list(frames)
            counts = Counter(histogram)
            # Rebuild literal C: every non-target gate in reverse order at full.
            for _, t, u in reversed(gates):
                if word['v'] <= t < 2 * word['v']:
                    continue
                for r in (t, u):
                    jump = degree - frames[r].bit_count()
                    if jump:
                        counts[jump] += 1
                    frames[r] = full
            for r, end in enumerate(final):
                if frames[r] & ~end:
                    return
                jump = end.bit_count() - frames[r].bit_count()
                if jump:
                    counts[jump] += 1
            result[tuple(sorted(counts.items()))] += 1
            return
        _, t, u = gates[index]
        lower = frames[t] | frames[u]
        upper = final[t] & final[u]
        if index < len(state['A']) and any(word['v'] <= r < 2 * word['v'] for r in (t, u)):
            upper = 0
        if lower & ~upper:
            return
        optional = upper & ~lower
        subset = optional
        while True:
            frame = lower | subset
            updated = list(frames)
            counts = Counter(histogram)
            for r in (t, u):
                jump = frame.bit_count() - frames[r].bit_count()
                if jump:
                    counts[jump] += 1
                updated[r] = frame
            visit(index + 1, updated, counts)
            if subset == 0:
                break
            subset = (subset - 1) & optional

    visit(0, current, Counter())
    return result


def order_key(state):
    return tuple(tuple(op[0] for op in state[sec]) for sec in 'AB')


def census(word, quotient):
    state = operations(word)
    cache = {}

    def profiles(s):
        key = order_key(s)
        if key not in cache:
            cache[key] = frame_profiles(word, s)
        return cache[key]

    first = moves(word, state, quotient=quotient)
    single_profiles = set(profiles(state))
    pair_profiles = set()
    pairs = []
    legal_first = 0
    for m1 in first:
        after = apply(state, m1)
        first_profiles = profiles(after)
        if not first_profiles:
            continue
        legal_first += 1
        single_profiles.update(first_profiles)
        registers = set(state[m1[0]][m1[1]][1:])
        for m2 in moves(word, after, quotient=quotient, registers=registers):
            end = apply(after, m2)
            final_profiles = profiles(end)
            require(bool(final_profiles), 'fixture unexpectedly has an illegal second order')
            pair_profiles.update(final_profiles)
            pairs.append((m1, m2, order_key(end)))
    return dict(first=first, legal_first=legal_first, pairs=pairs,
                single_profiles=sorted(single_profiles), pair_profiles=sorted(pair_profiles),
                orders=len(cache), frame_assignments=sum(sum(v.values()) for v in cache.values()),
                cached_profiles=cache)


def scalar_endpoint(word, sections=None, *, omit_last_cleanup=False):
    """All dirty-input columns at once over F2, including D, scatter and C."""
    n = len(word['start'])
    values = [1 << r for r in range(n)]
    sections = sections or {sec: [(t, tuple(us)) for _, t, us in word[sec]] for sec in 'AB'}

    def gate(t, us):
        for u in us:
            values[t] ^= values[u]

    for _, t, us in word['D']:
        gate(t, us)
    for t, us in sections['A']:
        gate(t, us)
    snap = [values[r] for r in word['ret']]
    for t, indices in enumerate(word.get('scatter', [])):
        for k in indices:
            values[word['v'] + t] ^= snap[k]
    for t, us in sections['B']:
        gate(t, us)
    cleanup = [(t, us) for t, us in reversed(sections['A'] + sections['B'])
               if not word['v'] <= t < 2 * word['v']]
    if omit_last_cleanup:
        cleanup = cleanup[:-1]
    for t, us in cleanup:
        gate(t, us)
    return values


def integer_basis(vectors):
    rows = []
    for vector in vectors:
        v = list(vector)
        require(all(type(x) is int for x in v), 'noninteger source coordinate')
        for pivot, basis in rows:
            if v[pivot]:
                a, b = basis[pivot], v[pivot]
                v = [a*x - b*y for x, y in zip(v, basis)]
                divisor = 0
                for x in v:
                    divisor = gcd(divisor, x)
                if divisor:
                    v = [x // divisor for x in v]
        pivot = next((i for i, x in enumerate(v) if x), None)
        if pivot is not None:
            rows.append((pivot, v))
            rows.sort()
    return rows


def framed_profile(word, sections):
    """Independent integer-rank invoice of a specified full framed word."""
    masks = [sum(1 << i for i in frame) for frame in word['frames']]
    full = (1 << len(word['lines'])) - 1
    ranks = {}

    def rank(mask):
        if mask not in ranks:
            ranks[mask] = len(integer_basis(v for i, v in enumerate(word['lines']) if mask >> i & 1))
        return ranks[mask]

    current = [masks[f] for f in word['start']]
    counts = Counter()

    def touch(r, frame):
        before = current[r]
        require(before & ~frame == 0, 'independent full-word frame descent')
        jump = rank(frame) - rank(before)
        if jump:
            counts[jump] += 1
        current[r] = frame

    for f, t, us in word['D']:
        for r in (t, *us):
            touch(r, masks[f])
    for f, t, u, _ in sections['A']:
        touch(t, f)
        touch(u, f)
    copies = {r: current[r] for r in word['ret']}
    for frame in copies.values():
        counts[rank(frame)] += 1
    for f, t, u, _ in sections['B']:
        touch(t, f)
        touch(u, f)
    for _, t, u, _ in reversed(sections['A'] + sections['B']):
        if not word['v'] <= t < 2 * word['v']:
            touch(t, full)
            touch(u, full)
    for r, f in enumerate(word['final']):
        touch(r, masks[f])
    counts.pop(0, None)
    return tuple(sorted(counts.items())), copies
