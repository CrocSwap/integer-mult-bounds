"""Exact three-stream projective Clifford group-algebra model.

Apache-2.0. Substantial OpenAI Codex assistance; see NOTICE.md.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations

M = 3
IDENTITY = tuple([1 << i for i in range(M)] + [1 << (M+i) for i in range(M)])
Op = tuple[str, int, int]
PAIRS = ((0, 1), (0, 2), (1, 2))
FREE = tuple([('S', i, 0) for i in range(M)]
             + [('X', i, 0) for i in range(M)]
             + [('Z', i, 0) for i in range(M)]
             + [('CX', i, j) for i in range(M) for j in range(M) if i != j]
             + [('CZ', i, j) for i, j in combinations(range(M), 2)])


def pauli_image(op: Op, value: int) -> int:
    x, z, p = value & 7, (value >> 3) & 7, value >> 6
    name, a, b = op
    if name == "C":
        if (z & a).bit_count() & 1:
            x ^= a
            p -= 1
    elif name == "S":
        u = (x >> a) & 1
        p += u
        z ^= u << a
    elif name == "X":
        p += 2*((z >> a) & 1)
    elif name == "Z":
        p += 2*((x >> a) & 1)
    elif name == "CX":
        x ^= ((x >> a) & 1) << b
        z ^= ((z >> b) & 1) << a
    elif name == "CZ":
        u, v = (x >> a) & 1, (x >> b) & 1
        p += 2*u*v
        z ^= (u << b) | (v << a)
    else:
        raise ValueError(op)
    return x | (z << 3) | ((p % 4) << 6)


def rank_binary(values: list[int]) -> int:
    pivots: dict[int, int] = {}
    for value in values:
        while value:
            pivot = value.bit_length()-1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def fourier_rank(group: tuple[int, ...]) -> int:
    return rank_binary([value & 7 for value in group[M:]])


class Engine:
    def __init__(self):
        self.groups = [IDENTITY]
        self.ids = {IDENTITY: 0}
        self.transitions = lru_cache(maxsize=150_000)(self._transition)
        self.frames = lru_cache(maxsize=40_000)(self._frame)

    def _frame(self, group_id):
        g = self.groups[group_id]
        basis = [sum((((g[M+i] >> j) & 1) << i)
                     | (((g[i] >> j) & 1) << (M+i)) for i in range(M))
                 for j in range(M)]
        span = [0]
        for v in basis:
            span += [w ^ v for w in span]
        assert len(set(span)) == 8
        return sum(1 << v for v in span)

    def _transition(self, op, group_id):
        new = tuple(pauli_image(op, value) for value in self.groups[group_id])
        if new not in self.ids:
            self.ids[new] = len(self.groups)
            self.groups.append(new)
        return self.ids[new]

    def frame_info(self, group):
        return self.frames(group), fourier_rank(self.groups[group])


def add_poly(target, source, scalar=1, bit=0):
    for mask, coefficient in source.items():
        assert not mask & bit
        key = mask | bit
        value = target.get(key, 0)+scalar*coefficient
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def generic_paths(ring, program, kind):
    """One independent variable per matrix entry, one selected entry per path."""
    rows = [{i: {0: 1}} for i in range(3)]
    blocks = 0
    for gate in program:
        if gate[0] not in ('mix', 'mix3'):
            _, role, index = gate
            op = ('C', index, 0) if gate[0] == 'paid' else FREE[index]
            rows[role] = {(ring.transitions(op, key >> 2) << 2) | (key & 3): p
                          for key, p in rows[role].items()}
            continue
        assert gate[0] == ('mix' if kind == 2 else 'mix3')
        roles = PAIRS[gate[1]] if kind == 2 else range(3)
        changed = []
        for i in range(kind):
            row = {}
            for j, role in enumerate(roles):
                bit = 1 << (kind*kind*blocks+kind*i+j)
                for key, polynomial in rows[role].items():
                    add_poly(row.setdefault(key, {}), polynomial, bit=bit)
            changed.append(row)
        for role, row in zip(roles, changed):
            rows[role] = row
        blocks += 1
    return tuple(rows), blocks


def coefficient_records(ring, rows):
    records, targets = [], [set() for _ in range(3)]
    for output, row in enumerate(rows):
        # Interned integer IDs depend on what an Engine saw earlier. Proof
        # row IDs must instead follow stable Clifford tableaus and columns.
        for key, polynomial in sorted(row.items(), key=lambda item: (item[0] & 3, ring.groups[item[0] >> 2])):
            frame, rank = ring.frame_info(key >> 2)
            column = key & 3
            records.append({'output': output, 'column': column, 'frame': frame,
                            'rank': rank, 'poly': polynomial})
            if rank == 3:
                targets[column].add(frame)
    return records, targets


def decode(program):
    result = []
    for raw in program:
        kind = raw[0]
        if kind == 'mix3':
            assert len(raw) == 10
            gate = (kind, *(Q(x) for x in raw[1:]))
        else:
            assert kind in ('paid', 'free') and len(raw) == 3
            assert type(raw[1]) is int and 0 <= raw[1] < 3
            assert type(raw[2]) is int
            assert (1 <= raw[2] <= 7) if kind == 'paid' else (0 <= raw[2] < 18)
            gate = tuple(raw)
        result.append(gate)
    return tuple(result)


def execute(ring, program):
    rows = [{i: Q(1)} for i in range(3)]
    for gate in program:
        if gate[0] == 'mix3':
            changed = []
            for r in range(3):
                row = {}
                for c in range(3):
                    for key, value in rows[c].items():
                        row[key] = row.get(key, 0)+gate[1+3*r+c]*value
                changed.append({key: value for key, value in row.items() if value})
            rows = changed
        else:
            op = ('C', gate[2], 0) if gate[0] == 'paid' else FREE[gate[2]]
            rows[gate[1]] = {(ring.transitions(op, key >> 2) << 2) | (key & 3): value
                            for key, value in rows[gate[1]].items()}
    return tuple(rows)


def endpoint_frames(ring, rows):
    answer = []
    for column in range(3):
        values = {ring.frame_info(key >> 2) for row in rows for key, v in row.items()
                  if v and key & 3 == column}
        if len(values) != 1 or next(iter(values))[1] != 3:
            return None
        answer.append(next(iter(values))[0])
    return answer
