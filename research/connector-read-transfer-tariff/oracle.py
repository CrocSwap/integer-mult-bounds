"""Physical formal rows, subset read search and separate dense execution."""
from collections import deque


def physical_rectangle():
    """All words with U<=4,V<=3, closed under every free legal B advance."""
    word, colors = (0, 0, 1, 1, 2, 2), (1, 1, 2)
    cells = {(u, v): set() for u in range(5) for v in range(4)}
    cells[0, 0].add((0, 8, 16, (8,)))
    for total in range(8):
        for u in range(5):
            v = total-u
            if (u, v) not in cells: continue
            current = cells[u, v]; queue = deque(current)
            while queue:
                cut, a, b, old = queue.popleft()
                if cut == 6: continue
                j = word[cut]; color = colors[j]
                if ((a >> 3)&color).bit_count() % 2 != 1 or ((b >> 3)&color).bit_count() % 2 != 0: continue
                aa = a ^ (1 << j)
                following = cut+1, aa, b, tuple(sorted(set(old) | {aa}))
                if following not in current: current.add(following); queue.append(following)
            for cut, a, b, old in current:
                if u < 4: cells[u+1, v].add((cut, a ^ b, b, tuple(sorted(set(old) | {a ^ b}))))
                if v < 3: cells[u, v+1].add((cut, a, b ^ a, old))
    counts = {}
    for (u, v), states in cells.items():
        for state in states: counts.setdefault(state, []).append((u, v))
    records = []
    for state, costs in counts.items():
        for u, v in costs:
            if any((a, b) != (u, v) and a <= u and b <= v for a, b in costs): continue
            cut, a, b, available = state
            records.append([cut, a, b, list(available), u, v])
    return sorted(records)


def subset_reads(available):
    best = {}
    for subset in range(1 << len(available)):
        value = 0
        for i, v in enumerate(available):
            if subset >> i & 1: value ^= v
        if 0 < value < 8:
            best[value] = min(best.get(value, 999), subset.bit_count())
    return best


def formal(program):
    # Coordinates: X0,X1,X2,d0,d1, then seven incoming dirty targets.
    roots, targets, calls = [8, 16], [1 << (m+4) for m in range(1, 8)], []
    invoice = [0]*9
    for kind, value in program:
        if kind == 'B':
            if not 0 <= value < 3: raise ValueError('source label')
            color = (1, 1, 2)[value]
            if ((roots[0] >> 3)&color).bit_count() % 2 != 1 or ((roots[1] >> 3)&color).bit_count() % 2:
                raise ValueError('fixed source color')
            roots[0] ^= 1 << value; calls.append(value)
        elif kind == 'C':
            if value not in (0, 1): raise ValueError('transfer destination')
            roots[value] ^= roots[1-value]; invoice[value] += 1
        elif kind == 'A':
            if not 1 <= value <= 7: raise ValueError('target label')
            targets[value-1] ^= roots[0]; invoice[value+1] += 1
        else: raise ValueError('operation alphabet')
    if calls != [0, 0, 1, 1, 2, 2]: raise ValueError('fixed source word')
    if roots != [8, 16]: raise ValueError('root return')
    if targets != [(1 << (m+4)) ^ m for m in range(1, 8)]: raise ValueError('dirty target endpoint')
    return invoice


def dense(program, width, matrices, state, reverse=False):
    source, roots, target = list(state[:3]), list(state[3:5]), list(state[5:])
    def apply(matrix, vector):
        return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(matrix))
    for kind, value in reversed(program) if reverse else program:
        if kind == 'B': roots[0] ^= apply(matrices[value], source[value])
        elif kind == 'A': target[value-1] ^= apply(matrices[value+2], roots[0])
        elif kind == 'C': roots[value] ^= roots[1-value]
        else: raise ValueError('dense alphabet')
    return source + roots + target


def expected(matrices, state):
    def apply(rows, value):
        out = 0
        for i, row in enumerate(rows):
            parity = 0
            for j in range(len(rows)): parity ^= (row >> j & 1) & (value >> j & 1)
            out |= parity << i
        return out
    out = list(state)
    for m in range(1, 8):
        value = 0
        for j in range(3):
            if m >> j & 1: value ^= apply(matrices[j], state[j])
        out[m+4] ^= apply(matrices[m+2], value)
    return out
