"""Two literal instruction paths for fifteen disjoint tape owners.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The dense path uses Jerry Chen's Tape operations. The sparse path does not.
"""


def check_owners(tapes):
    if len(tapes) != 15 or len({id(tape) for tape in tapes}) != 15:
        raise ValueError('fifteen distinct owners required')


def dense(code, tapes, limit):
    check_owners(tapes)
    pc = 0
    for steps in range(1, limit + 1):
        ins = code[pc]
        if ins[0] == 'R':
            pc = ins[2][tapes[ins[1]].read()]
        elif ins[0] == 'W':
            tapes[ins[1]].write(ins[2]); pc += 1
        elif ins[0] == 'M':
            tapes[ins[1]].move(ins[2]); pc += 1
        elif ins[0] == 'J':
            pc = ins[1]
        elif ins[0] == 'H':
            return dict(outcome=ins[1], steps=steps,
                        cells=[t.cells[:] for t in tapes], heads=[t.head for t in tapes],
                        low=[t.low for t in tapes], high=[t.high for t in tapes],
                        writes=[t.writes for t in tapes])
        else:
            raise ValueError('unknown dense instruction')
    raise TimeoutError('dense instruction limit')


def sparse(code, tapes, limit):
    check_owners(tapes)
    heads = [t.origin for t in tapes]
    low, high, writes = heads[:], heads[:], [0] * 15
    sizes = [len(t.cells) for t in tapes]
    cells = {(owner, position): value for owner, tape in enumerate(tapes)
             for position, value in enumerate(tape.cells) if value != 2}
    pc = 0
    for steps in range(1, limit + 1):
        op, *args = code[pc]
        if op == 'H':
            return dict(outcome=args[0], steps=steps, heads=heads, low=low, high=high,
                        writes=writes, cells=[[cells.get((i, j), 2) for j in range(sizes[i])]
                                              for i in range(15)])
        if op == 'J':
            pc = args[0]; continue
        owner, operand = args
        position = heads[owner]
        if op == 'R':
            pc = operand[cells.get((owner, position), 2)]
        elif op == 'W':
            writes[owner] += 1
            if operand == 2:
                cells.pop((owner, position), None)
            else:
                cells[owner, position] = operand
            pc += 1
        elif op == 'M':
            if operand not in (-1, 1):
                raise ValueError('nonunit sparse move')
            heads[owner] += operand; position = heads[owner]; pc += 1
        else:
            raise ValueError('unknown sparse instruction')
        if not 0 <= position < sizes[owner]:
            raise ValueError('sparse window exceeded')
        low[owner] = min(low[owner], position); high[owner] = max(high[owner], position)
    raise TimeoutError('sparse instruction limit')
