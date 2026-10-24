"""Lower a literal five-symbol program to aligned three-bit blocks.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""

ENCODING = ((0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (0, 0, 0))
STATUSES = ('initialized', 'returned', 'consumed', 'installed', 'closed', 'rejected')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def admit(code, entries, roles, alphabet):
    """Check the finite instruction alphabet and exclude control-only cycles."""
    for pc, row in enumerate(code):
        op, *args = row
        targets = []
        if op == 'test':
            need(len(args) == 4 and args[0] in roles and type(args[1]) is int
                 and args[1] in alphabet, 'test domain')
            targets = args[2:]
        elif op == 'write':
            need(len(args) == 2 and args[0] in roles and type(args[1]) is int
                 and args[1] in alphabet, 'write domain')
        elif op == 'move':
            need(len(args) == 2 and args[0] in roles and type(args[1]) is int
                 and args[1] in (-1, 1), 'move domain')
        elif op == 'jump':
            need(len(args) == 1, 'jump arity')
            targets = args
        else:
            need(op == 'halt' and len(args) == 1 and args[0] in STATUSES, 'halt domain')
        if op in ('write', 'move'):
            need(pc+1 < len(code), 'fallthrough boundary')
        need(all(type(t) is int and 0 <= t < len(code) for t in targets), 'target domain')
    need(code and all(type(v) is int and 0 <= v < len(code) for v in entries.values()), 'entry')
    longest = 0
    for start, row in enumerate(code):
        if row[0] != 'jump':
            continue
        seen, pc = set(), start
        while code[pc][0] == 'jump':
            need(pc not in seen, 'control-only cycle')
            seen.add(pc)
            pc = code[pc][1]
        longest = max(longest, len(seen))
    return longest+1


def lower(code, entries, roles):
    """Compile once; the output has no source executor or runtime callback."""
    admit(code, entries, roles, range(5))
    output, labels = [], {}
    def emit(*row):
        output.append(row)
    def mark(label):
        labels[label] = len(output)
    for pc, row in enumerate(code):
        mark(('source', pc))
        op = row[0]
        if op == 'test':
            _, role, symbol, yes, no = row
            def decode(prefix):
                if len(prefix) == 3:
                    emit('move', role, -1)
                    emit('move', role, -1)
                    if prefix not in ENCODING:
                        emit('halt', 'rejected')
                    else:
                        emit('jump', ('source', yes if prefix == ENCODING[symbol] else no))
                    return
                zero, one = ('bit', pc, prefix, 0), ('bit', pc, prefix, 1)
                emit('test', role, 1, one, zero)
                for bit, label in ((0, zero), (1, one)):
                    mark(label)
                    if len(prefix) < 2:
                        emit('move', role, 1)
                    decode(prefix+(bit,))
            decode(())
        elif op == 'write':
            _, role, symbol = row
            for offset, bit in enumerate(ENCODING[symbol]):
                emit('write', role, bit)
                if offset < 2:
                    emit('move', role, 1)
            emit('move', role, -1)
            emit('move', role, -1)
            emit('jump', ('source', pc+1))
        elif op == 'move':
            for _ in range(3):
                emit(*row)
            emit('jump', ('source', pc+1))
        elif op == 'jump':
            emit('jump', ('source', row[1]))
        else:
            emit(*row)
    resolved = []
    for row in output:
        if row[0] == 'test':
            row = (*row[:3], labels[row[3]], labels[row[4]])
        elif row[0] == 'jump':
            row = ('jump', labels[row[1]])
        resolved.append(row)
    lowered_entries = {name: labels[('source', pc)] for name, pc in entries.items()}
    result = tuple(resolved)
    admit(result, lowered_entries, roles, (0, 1))
    return result, lowered_entries


def execute(code, tapes, heads, entry, max_steps=10000000):
    """Interpret only binary local-cell instructions; count every instruction."""
    pc = entry
    counts = dict(steps=0, reads=0, writes=0, moves=0, jumps=0)
    while counts['steps'] < max_steps:
        row = code[pc]
        op = row[0]
        counts['steps'] += 1
        if op == 'test':
            _, role, bit, yes, no = row
            head, cells = heads[role], tapes[role]
            value = cells[head] if head < len(cells) else 0
            need(value in (0, 1), 'nonbinary cell')
            counts['reads'] += 1
            pc = yes if value == bit else no
        elif op == 'write':
            _, role, bit = row
            head, cells = heads[role], tapes[role]
            if head >= len(cells):
                cells.extend([0]*(head+1-len(cells)))
            cells[head] = bit
            counts['writes'] += 1
            pc += 1
        elif op == 'move':
            _, role, step = row
            need(heads[role]+step >= 0, 'left boundary')
            heads[role] += step
            counts['moves'] += 1
            pc += 1
        elif op == 'jump':
            counts['jumps'] += 1
            pc = row[1]
        elif op == 'halt':
            return dict(counts, status=row[1])
        else:
            raise ValueError('invalid opcode')
    raise ValueError('observer watchdog')
