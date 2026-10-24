# SPDX-License-Identifier: Apache-2.0
"""Literal binary descriptor for C=k/4 mod Q, with fixed -7<=k<=12."""


def compile_offset(k):
    if type(k) is not int or not -7 <= k <= 12:
        raise ValueError('fixed source quarter code')
    code = [('reject',)]

    def emit(row):
        code.append(row)
        return len(code) - 1

    def chain(rows, destination):
        for row in reversed(rows):
            destination = emit(tuple(row) + (destination,))
        return destination

    def branch(tape, pairs):
        return emit(('branch', tape, tuple(pairs), 0))

    def rewind(tape, destination):
        loop = emit(())
        onward = chain([('move', tape, -1)], loop)
        returned = chain([('move', tape, 1)], destination)
        code[loop] = ('branch', tape, ((0, onward), (1, onward), (2, onward), (3, returned)), 0)
        return loop

    halt = emit(('halt',))
    returned = rewind(0, rewind(1, halt))
    trim = emit(())
    zero = chain([('write', 1, None), ('move', 1, -1)], trim)
    one = chain([('move', 1, 1), ('write', 1, 2)], returned)
    code[trim] = ('branch', 1, ((0, zero), (1, one)), 0)
    finish = chain([('write', 1, None), ('move', 1, -1)], trim)

    multiply_entries = {}

    def multiplication(t, initial):
        states = [(initial, 0)]
        pending = set(states)
        entries = {}
        while states:
            carry, skipped = states.pop()
            entries[carry, skipped] = emit(())
            for bit in (0, 1):
                total = t * bit + carry
                key = (total // 2, min(2, skipped + 1))
                if (skipped >= 2 or total % 2 == 0) and key not in pending:
                    pending.add(key)
                    states.append(key)
        for (carry, skipped), address in entries.items():
            pairs = []
            for bit in (0, 1):
                total = t * bit + carry
                if skipped < 2 and total % 2:
                    target = 0
                else:
                    rows = [('move', 0, 1)]
                    if skipped == 2:
                        rows += [('write', 1, total % 2), ('move', 1, 1)]
                    target = chain(rows, entries[total // 2, min(2, skipped + 1)])
                pairs.append((bit, target))
            if skipped == 2 and carry >= 0:
                rows = []
                for digit in bin(carry)[2:][::-1] if carry else '':
                    rows += [('write', 1, int(digit)), ('move', 1, 1)]
                pairs.append((2, chain(rows, finish)))
            code[address] = ('branch', 0, tuple(pairs), 0)
        return entries[initial, 0]

    scan_entries = {}
    states = [(0, 0, False, 0)]
    pending = set(states)
    while states:
        state = states.pop()
        scan_entries[state] = emit(())
        position, prefix, large, last = state
        for bit in (0, 1):
            nxt = (min(4, position + 1), prefix + (bit << position) if position < 4 else prefix,
                   large or (position == 4 and bit == 1), bit)
            if nxt not in pending:
                pending.add(nxt)
                states.append(nxt)
    for state, address in scan_entries.items():
        position, prefix, large, last = state
        pairs = []
        for bit in (0, 1):
            nxt = (min(4, position + 1), prefix + (bit << position) if position < 4 else prefix,
                   large or (position == 4 and bit == 1), bit)
            pairs.append((bit, chain([('move', 0, 1)], scan_entries[nxt])))
        if position >= 2 and prefix % 2 and last == 1:
            if not large and prefix < 13:
                value = k * pow(4, -1, prefix) % prefix + 1
                rows = []
                for digit in bin(value)[2:][::-1]:
                    rows += [('write', 1, int(digit)), ('move', 1, 1)]
                target = chain(rows, finish)
            else:
                t = (-k * pow(prefix % 4, -1, 4)) % 4
                if t == 0 and k < 0:
                    t = 4
                key = (t, k + 4)
                if key not in multiply_entries:
                    multiply_entries[key] = multiplication(*key)
                target = rewind(0, multiply_entries[key])
            pairs.append((2, target))
        code[address] = ('branch', 0, tuple(pairs), 0)
    start = chain([('move', 1, -1), ('write', 1, 3), ('move', 1, 1)], scan_entries[0, 0, False, 0])
    return {'code': code, 'start': start}
