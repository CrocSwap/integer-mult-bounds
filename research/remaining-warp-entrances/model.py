"""Exact single-entrance closure for the frozen nine-axis word.

Produced by Nick Petalas. Apache-2.0.
Capacity/least-closure contract: ToikY PR3933; word: Dugongue PR3929.
"""
from copy import deepcopy
from functools import lru_cache

FULL = (1 << 512) - 1
ZERO = 1


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(vectors):
    need(len(vectors) <= 18, 'basis capacity')
    need(all(type(v) is int and 0 <= v < 512 for v in vectors), 'binary vector')
    return cached_span(tuple(vectors))


@lru_cache(maxsize=4096)
def cached_span(vectors):
    mask = ZERO
    for vector in vectors:
        shifted = 0
        for point in range(512):
            if mask >> point & 1:
                shifted |= 1 << (point ^ vector)
        mask |= shifted
    return mask


def basis(mask):
    need(type(mask) is int and 0 < mask <= FULL and mask & 1, 'point mask')
    result, accumulated = [], ZERO
    for point in range(1, 512):
        if mask >> point & 1 and not accumulated >> point & 1:
            result.append(point)
            accumulated |= sum(1 << (p ^ point) for p in range(512)
                               if accumulated >> p & 1)
    need(accumulated == mask and len(result) <= 9, 'not a subspace')
    return result


def join(left, right):
    if left & ~right == 0:
        return right
    if right & ~left == 0:
        return left
    return span(basis(left) + basis(right))


def images(columns):
    need(len(columns) == 9, 'nine columns required')
    table = [0] * 512
    for point in range(1, 512):
        low = point & -point
        table[point] = table[point ^ low] ^ columns[low.bit_length() - 1]
    need(len(set(table)) == 512, 'singular native map')
    return table


def image(table, mask):
    return sum(1 << table[p] for p in range(512) if mask >> p & 1)


def touched(gate):
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def terminal(word):
    removed = set(word['removed'])
    caps = {r: FULL for r in range(704) if r not in removed}
    for r in range(112, 224):
        port = word['ports'][r - 112]
        caps[r] = sum(1 << p for p in range(512) if (p & port).bit_count() % 2 == 0)
    for r, frame in word['helper_final'].items():
        caps[int(r)] = span(frame)
    return caps


def events(word):
    at = {}
    for index, record in enumerate(word['warps']):
        at.setdefault(record[0], []).append(index)
    result = []
    for p in range(len(word['B']) + 1):
        result.extend(('warp', k) for k in at.get(p, ()))
        if p < len(word['B']):
            result.append(('B', p))
    result.extend(('restore', k) for k in range(len(word['restore'])))
    need(len(result) < 20000, 'event capacity')
    return result


def capacities(word, sequence, maps):
    caps, seeds = terminal(word), {}
    for kind, index in reversed(sequence):
        if kind == 'warp':
            record = word['warps'][index]
            lender = record[1]
            incoming = sum(1 << p for p, q in enumerate(maps[index])
                           if caps[lender] >> q & 1)
            need(span(record[3]) & ~incoming == 0, 'native floor exceeds capacity')
            caps[lender] = incoming
            seeds[index] = incoming
        else:
            gate = word[kind][index]
            incoming = FULL
            for r in touched(gate):
                incoming &= caps[r]
            need(span(gate[-1]) & ~incoming == 0, 'scalar floor exceeds capacity')
            for r in touched(gate):
                caps[r] = incoming
    return seeds


def initial(word):
    current = {r: ZERO for r in range(704) if r not in set(word['removed'])}
    current.update({r: span([port]) for r, port in enumerate(word['ports'])})
    current.update({int(r): span(f) for r, f in word['start_extra'].items()})
    for gate in word['A']:
        if gate[0] == 'warp':
            current[gate[1]] = span(gate[4])
        else:
            for r in touched(gate):
                current[r] = span(gate[-1])
    return current


def closure(word, sequence, maps, target, seed):
    current, assigned = initial(word), {}
    changed = False
    for kind, index in sequence:
        if kind == 'warp':
            record = word['warps'][index]
            lender, floor = record[1], span(record[3])
            if index == target:
                need(not changed and current[lender] == floor, 'frozen entrance')
                need(floor & ~seed == 0, 'seed loses original entrance')
                changed = True
                entrance = seed
            elif changed:
                entrance = join(floor, current[lender])
            else:
                need(current[lender] == floor, 'frozen native prefix')
                entrance = floor
            if changed:
                assigned[kind, index] = entrance
            current[lender] = image(maps[index], entrance)
        else:
            gate = word[kind][index]
            frame = span(gate[-1])
            if changed:
                for r in touched(gate):
                    frame = join(frame, current[r])
                assigned[kind, index] = frame
            for r in touched(gate):
                current[r] = frame
    need(changed, 'target missing')
    caps = terminal(word)
    need(all(f & ~caps[r] == 0 for r, f in current.items()), 'terminal cap')
    return assigned


def compile_word(word, assigned, maps, audit):
    result, current, output, scales = deepcopy(word), initial(word), [], []
    at = {}
    for k, rec in enumerate(word['warps']):
        at.setdefault(rec[0], []).append(k)
    for p in range(len(word['B']) + 1):
        for k in at.get(p, ()):
            rec = word['warps'][k]
            lender = rec[1]
            entrance = assigned.get(('warp', k), span(rec[3]))
            need(current[lender] & ~entrance == 0, 'native shrink')
            if current[lender] != entrance:
                scales.append((len(output), lender))
                output.append(['scale', lender, 1, 1, basis(entrance)])
            exit_frame = image(maps[k], entrance)
            result['warps'][k] = [len(output), lender, rec[2], basis(entrance), basis(exit_frame)]
            current[lender] = exit_frame
        if p < len(word['B']):
            gate = deepcopy(word['B'][p])
            frame = assigned.get(('B', p), span(gate[-1]))
            if frame != span(gate[-1]):
                gate[-1] = basis(frame)
            output.append(gate)
            for r in touched(gate):
                current[r] = frame
    for k, gate in enumerate(result['restore']):
        if ('restore', k) in assigned and assigned['restore', k] != span(gate[-1]):
            gate[-1] = basis(assigned['restore', k])
    result['B'] = output
    result['cleanup'] = audit.derive_cleanup(result)
    return result, scales


def reduced_basis(vectors):
    """Separate row-elimination representation for annihilator certificates."""
    pivots = [0] * 9
    for value in vectors:
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    for bit in range(9):
        if pivots[bit]:
            for high in range(bit + 1, 9):
                if pivots[high] >> bit & 1:
                    pivots[high] ^= pivots[bit]
    return tuple(p for p in pivots if p)


def annihilator(vectors):
    return reduced_basis([p for p in range(512)
                          if all((p & v).bit_count() % 2 == 0 for v in vectors)])


def dual_capacities(word, sequence):
    constraints = {r: annihilator(basis(c)) for r, c in terminal(word).items()}
    seeds = {}
    for kind, k in reversed(sequence):
        if kind == 'warp':
            rec = word['warps'][k]
            transformed = [sum(((h & col).bit_count() % 2) << j
                               for j, col in enumerate(rec[2]))
                           for h in constraints[rec[1]]]
            constraints[rec[1]] = reduced_basis(transformed)
            seeds[k] = span(annihilator(constraints[rec[1]]))
        else:
            gate = word[kind][k]
            common = reduced_basis([h for r in touched(gate) for h in constraints[r]])
            for r in touched(gate):
                constraints[r] = common
    return seeds


def delta(new, old):
    return {r: new.get(r, 0) - old.get(r, 0) for r in sorted(set(new) | set(old))
            if new.get(r, 0) != old.get(r, 0)}


def power_class(change):
    """Match the finite deltas to the positive expressions proved in README."""
    if not change:
        return 'equal'
    one, two = change.get(1, 0), change.get(2, 0)
    if set(change) == {1, 2} and one == -2 * two and two < 0:
        return 'multiple_of_2_minus_2q'
    classes = {
        (12, -8, -4, 4): 'four_times_square_plus_concavity',
        (13, -7, -1, 1): 'positive_product_plus_d3',
        (12, -9, -2, 3): 'd3_lower_bound',
        (20, -13, -2, 3): 'd3_lower_bound_plus_4d2',
        (21, -12, 1, 0): '12d2_minus_d3',
        (13, -8, 1, 0): '8d2_minus_d3',
        (20, -14, 0, 2): 'two_positive_products',
    }
    need(set(change) <= {1, 2, 3, 4}, 'unproved rank support')
    key = tuple(change.get(r, 0) for r in range(1, 5))
    need(key in classes, 'unproved power sign')
    return classes[key]
