# SPDX-License-Identifier: Apache-2.0
"""Execute the literal physical word with exact Gaussian dyadic arrays."""
from collections import Counter
from fractions import Fraction as Q
from model import N, basis, distance, require

SIZE = 1 << N


class Array:
    def __init__(self, real, imag, denominator=0):
        self.real = list(real)
        self.imag = list(imag)
        self.denominator = denominator
        self.reduce()

    def copy(self):
        return Array(self.real, self.imag, self.denominator)

    def reduce(self):
        common = 0
        for part in (self.real, self.imag):
            for value in part:
                common |= value
        if not common:
            self.denominator = 0
            return
        zeros = (abs(common) & -abs(common)).bit_length() - 1
        shift = min(zeros, self.denominator)
        if shift:
            for part in (self.real, self.imag):
                for index, value in enumerate(part):
                    part[index] = value >> shift
            self.denominator -= shift

    def add(self, source, coefficient):
        power = coefficient.denominator.bit_length() - 1
        require(coefficient.denominator == 1 << power, 'physical dyadic scalar')
        denominator = max(self.denominator, source.denominator + power)
        left = denominator - self.denominator
        right = denominator - source.denominator - power
        num = coefficient.numerator
        for target, values in ((self.real, source.real), (self.imag, source.imag)):
            for index, value in enumerate(values):
                target[index] = (target[index] << left) + num * (value << right)
        self.denominator = denominator
        self.reduce()

    def same(self, other):
        return self.denominator == other.denominator and self.real == other.real and self.imag == other.imag


class Executor:
    def __init__(self):
        self.permutations = {}
        self.phases = {}
        self.counts = Counter()

    def apply(self, array, circuit):
        for gate in circuit:
            kind = gate[0]
            self.counts[kind] += 1
            if kind == 'P':
                rows = tuple(gate[1])
                if rows not in self.permutations:
                    indices = [sum(((row & x).bit_count() % 2) << bit for bit, row in enumerate(rows)) for x in range(SIZE)]
                    cycles, seen = [], set()
                    for start in range(SIZE):
                        if start in seen:
                            continue
                        cycle, current = [], start
                        while current not in seen:
                            seen.add(current)
                            cycle.append(current)
                            current = indices[current]
                        require(current == start, 'physical permutation cycle')
                        if len(cycle) > 1:
                            cycles.append(tuple(cycle))
                    self.permutations[rows] = cycles
                for cycle in self.permutations[rows]:
                    real, imag = array.real[cycle[-1]], array.imag[cycle[-1]]
                    for index in cycle:
                        array.real[index], real = real, array.real[index]
                        array.imag[index], imag = imag, array.imag[index]
            elif kind == 'X':
                offset = gate[1]
                for x in range(SIZE):
                    y = x ^ offset
                    if x < y:
                        array.real[x], array.real[y] = array.real[y], array.real[x]
                        array.imag[x], array.imag[y] = array.imag[y], array.imag[x]
            elif kind in ('D', 'phase'):
                if kind == 'phase':
                    phases = [gate[1]] * SIZE
                else:
                    quadratic, linear = tuple(gate[1]), tuple(gate[2])
                    key = (quadratic, linear)
                    if key not in self.phases:
                        values = []
                        for x in range(SIZE):
                            power = sum(linear[i] for i in range(N) if x & (1 << i))
                            power += 2 * sum(1 for i in range(N) for j in range(i + 1, N)
                                             if (x >> i) & (x >> j) & (quadratic[i] >> j) & 1)
                            values.append(power % 4)
                        self.phases[key] = values
                    phases = self.phases[key]
                for x, power in enumerate(phases):
                    a, b = array.real[x], array.imag[x]
                    array.real[x], array.imag[x] = ((a, b), (-b, a), (-a, -b), (b, -a))[power % 4]
            elif kind == 'C':
                mask, sign = gate[1], gate[2]
                require(mask > 0, 'physical C mask')
                for x in range(SIZE):
                    y = x ^ mask
                    if x < y:
                        a, b, c, d = array.real[x], array.imag[x], array.real[y], array.imag[y]
                        array.real[x] = a + c + sign * (d - b)
                        array.imag[x] = b + d + sign * (a - c)
                        array.real[y] = a + c + sign * (b - d)
                        array.imag[y] = b + d + sign * (c - a)
                array.denominator += 1
                array.reduce()
            else:
                raise ValueError('physical circuit primitive')
        return array


def input_array(role, trial=0):
    # This fixed input puts dense Gaussian values in every original role.
    real = [((37 * role + 11 * x + 3 * role * x + trial * (x * x + role)) % 31) - 15 for x in range(SIZE)]
    imag = [((19 * role + 7 * x + role * x * x + trial * (2 * x + role * role)) % 29) - 14 for x in range(SIZE)]
    return Array(real, imag)


def expected_target(word, target, trial, inverse_transpose=False):
    initial = input_array(target if inverse_transpose else word['v'] + target, trial)
    real = [2 * x for x in initial.real]
    imag = [2 * x for x in initial.imag]
    root_t = word['geometry']['live'][target]
    for source, root_i in enumerate(word['geometry']['live']):
        weight = word['geometry']['gram'][root_t][root_i]
        if weight:
            values = input_array(word['v'] + source if inverse_transpose else source, trial)
            if inverse_transpose:
                weight = -weight
            real = [a + weight * b for a, b in zip(real, values.real)]
            imag = [a + weight * b for a, b in zip(imag, values.imag)]
    return Array(real, imag, 1)


def whole_word(word, audit, trial=0, inverse_transpose=False):
    from verify import transpose_operator
    dual_frames = {}
    dual_moves = {}
    def frame_operator(frame):
        original = audit.frame(frame)
        if not inverse_transpose:
            return original
        if frame not in dual_frames:
            dual_frames[frame] = transpose_operator(audit.cx, original.adjoint())
        return dual_frames[frame]
    def move_operator(before, after, copy=False):
        rank = distance(before, after)
        _, original, compiled = audit.transition(before, after, rank)
        if not inverse_transpose:
            return compiled
        key = (before, after, copy)
        if key not in dual_moves:
            dual = transpose_operator(audit.cx, original if copy else original.adjoint())
            receipt, lowered = audit.cx.lower_child(dual)
            require(receipt['rank'] == rank, 'dual physical recursive rank')
            require(lowered.tab == dual.tab and lowered.zero_state() == dual.zero_state(), 'dual physical exact phase')
            dual_moves[key] = lowered
        return dual_moves[key]
    executor = Executor()
    arrays = [input_array(role, trial) for role in range(word['n'])]
    for role, frame in enumerate(word['initial_frames']):
        executor.apply(arrays[role], frame_operator(basis(frame)).circuit)
    executor.counts.clear()
    temporary = None
    copied = None
    for event in word['events']:
        op = event['op']
        if op in ('move', 'copy_begin'):
            before, after = basis(event['before']), basis(event['after'])
            compiled = move_operator(before, after, copy=(op == 'copy_begin'))
            if op == 'move':
                executor.apply(arrays[event['role']], compiled.circuit)
            else:
                require(temporary is None, 'physical temporary overlap')
                copied = (event['source'], compiled)
                if inverse_transpose:
                    temporary = Array([0] * SIZE, [0] * SIZE)
                    executor.counts['copy_zero'] += 1
                else:
                    temporary = arrays[event['source']].copy()
                    executor.apply(temporary, compiled.circuit)
                    executor.counts['copy_assign'] += 1
        elif op == 'add':
            if inverse_transpose:
                arrays[event['source']].add(arrays[event['target']], -Q(event['q']))
            else:
                arrays[event['target']].add(arrays[event['source']], Q(event['q']))
            executor.counts['axpy'] += 1
        elif op == 'copy_add':
            require(temporary is not None, 'physical missing copy')
            if inverse_transpose:
                temporary.add(arrays[event['target']], -Q(event['q']))
            else:
                arrays[event['target']].add(temporary, Q(event['q']))
            executor.counts['axpy'] += 1
        elif op == 'copy_end':
            require(temporary is not None, 'physical missing erase')
            if inverse_transpose:
                executor.apply(temporary, copied[1].circuit)
                arrays[copied[0]].add(temporary, Q(1))
                executor.counts['center_injection'] += 1
            temporary = None
            copied = None
            executor.counts['copy_erase'] += 1
        else:
            raise ValueError('physical word event')
    require(temporary is None, 'physical final temporary')
    word_counts = dict(sorted(executor.counts.items()))
    for role, final in enumerate(word['final_frames']):
        if inverse_transpose and role < word['v']:
            logical = expected_target(word, role, trial, inverse_transpose=True)
        elif not inverse_transpose and word['v'] <= role < 2 * word['v']:
            logical = expected_target(word, role - word['v'], trial)
        else:
            logical = input_array(role, trial)
        expected = executor.apply(logical, frame_operator(basis(final)).circuit)
        require(arrays[role].same(expected), f'whole physical output role {role}')
    return dict(original_roles=word['n'], addresses_per_role=SIZE,
                exact_gaussian_values=word['n'] * SIZE, trial=trial, inverse_transpose=inverse_transpose,
                operations=word_counts, temporary_streams_peak=1,
                scope='One dense Gaussian input across every physical stream and address; all-input coverage comes from the symbolic composition proof.')


def copy_matrix(word, audit):
    event = next(e for e in word['events'] if e['op'] == 'copy_begin' and distance(basis(e['before']), basis(e['after'])) == 7)
    _, original, compiled = audit.transition(basis(event['before']), basis(event['after']), 7)
    executor = Executor()
    for column in range(SIZE):
        values = [0] * SIZE
        values[column] = 1
        left = executor.apply(Array(values, [0] * SIZE), original.circuit)
        right = executor.apply(Array(values, [0] * SIZE), compiled.circuit)
        require(left.same(right), f'full rank-seven copy matrix column {column}')
    return dict(columns=SIZE, matrix_entries=SIZE * SIZE, rank=7)
