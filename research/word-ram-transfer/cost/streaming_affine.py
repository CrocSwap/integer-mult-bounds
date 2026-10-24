"""Portable exact model for the streaming affine-layout Word RAM lemma.
The interpreter is evidence about the displayed fixed program; the universal
invariant proof is in COST-THEOREMS.md. This is not a Lean certificate.
"""
from collections import Counter
import itertools
import json
import random
from pathlib import Path
COST = {'mov': 2, 'xor': 4, 'jnz': 2}

def program():
    code, labels = ([], {})

    def label(s):
        labels[s] = len(code)

    def emit(*s):
        code.append(s)
    emit('set', 'x', 0)
    emit('mov', 'y', 'bias')
    emit('mov', 'sp', 'src')
    label('outer')
    emit('shl', 'dp', 'y', 's')
    emit('add', 'dp', 'dp', 'dst')
    emit('set', 'j', 0)
    label('copy')
    emit('add', 'tmp', 'sp', 'j')
    emit('load', 'v', 'tmp')
    emit('add', 'tmp', 'dp', 'j')
    emit('store', 'tmp', 'v')
    emit('add', 'j', 'j', 'one')
    emit('sub', 'tmp', 'L', 'j')
    emit('jnz', 'tmp', 'copy')
    emit('add', 'xn', 'x', 'one')
    emit('sub', 'tmp', 'N', 'xn')
    emit('jzero', 'tmp', 'end')
    emit('set', 'k', 0)
    emit('set', 'mask', 1)
    label('toggle')
    emit('add', 'tmp', 'columns', 'k')
    emit('load', 'col', 'tmp')
    emit('xor', 'y', 'y', 'col')
    emit('and', 'bit', 'x', 'mask')
    emit('jzero', 'bit', 'last')
    emit('shl', 'mask', 'mask', 'one')
    emit('add', 'k', 'k', 'one')
    emit('jump', 'toggle')
    label('last')
    emit('mov', 'x', 'xn')
    emit('add', 'sp', 'sp', 'K')
    emit('jump', 'outer')
    label('end')
    emit('halt')
    return [(i[0], *(labels.get(v, v) if i[0] in ('jump', 'jzero', 'jnz') and j == len(i) - 2 else v for j, v in enumerate(i[1:]))) for i in code]
CODE = program()

def run(w, registers, memory):
    mask = (1 << w) - 1
    regs = dict(registers)
    mem = dict(memory)
    pc, ops, counts = (0, 0, Counter())
    while True:
        ins = CODE[pc]
        op, a = ins[:2] if len(ins) > 1 else (ins[0], None)
        counts[op] += 1
        ops += COST.get(op, 1)
        pc += 1
        if op == 'halt':
            break
        if op == 'jump':
            pc = a
            continue
        if op in ('jzero', 'jnz'):
            if (regs[a] == 0) == (op == 'jzero'):
                pc = ins[2]
            continue
        if op == 'store':
            mem[regs[a] & mask] = regs[ins[2]]
            continue
        if op == 'set':
            value = ins[2]
        elif op == 'mov':
            value = regs[ins[2]]
        elif op == 'load':
            value = mem.get(regs[ins[2]] & mask, 0)
        else:
            b, c = (regs[ins[2]], regs[ins[3]])
            if op == 'add':
                value = b + c
            elif op == 'sub':
                value = max(0, b - c)
            elif op == 'and':
                value = b & c
            elif op == 'xor':
                value = b ^ c
            elif op == 'shl':
                value = 0 if c >= w else b << c
            else:
                raise ValueError(op)
        regs[a] = value & mask
    return (mem, ops, counts)

def linear(columns, x):
    result = 0
    for j, column in enumerate(columns):
        if x & 1 << j:
            result ^= column
    return result

def independent(columns):
    return len({linear(columns, x) for x in range(1 << len(columns))}) == 1 << len(columns)

def instance(columns, bias, L, w=16):
    r, N = (len(columns), 1 << len(columns))
    if not all(0 <= c < N for c in columns):
        raise ValueError('column outside F2^r')
    if not independent(columns):
        raise ValueError('Singular matrix is not a permutation')
    if not (0 <= bias < N and L >= 1):
        raise ValueError('bad parameters')
    s = (L - 1).bit_length()
    K = 1 << s
    src, dst, table = (64, 64 + N * K, 64 + 2 * N * K)
    if table + r + 32 >= 1 << w:
        raise ValueError('address space insufficient')
    words = {src + x * K + j: ((x + 1) * 257 + j * 13) % (1 << w) for x in range(N) for j in range(L)}
    words.update({table + j: c for j, c in enumerate(columns)})
    for x in range(N):
        for j in range(L, K):
            words[dst + x * K + j] = (1 << w) - 1
    reg = dict(N=N, L=L, K=K, s=s, src=src, dst=dst, columns=table, bias=bias, one=1)
    result, ops, counts = run(w, reg, words)
    for x in range(N):
        y = linear(columns, x) ^ bias
        for j in range(L):
            if not result[dst + y * K + j] == words[src + x * K + j]:
                raise AssertionError('exact check failed')
    if not all((result[a] == v for a, v in words.items())):
        raise AssertionError('exact check failed')
    toggles = 2 * N - r - 2 if r else 0
    if not counts['xor'] == toggles:
        raise AssertionError('exact check failed')
    if not counts['store'] == N * L:
        raise AssertionError('exact check failed')
    if not ops <= 8 * N * L + 40 * N + 8:
        raise AssertionError('exact check failed')
    return dict(r=r, records=N, limbs=L, expanded_cost=ops, bound=8 * N * L + 40 * N + 8, toggles=toggles)

def verify():
    tests, max_ratio = (0, 0)
    checks = Counter()
    for r in range(4):
        N = 1 << r
        for columns in itertools.product(range(N), repeat=r):
            if not independent(columns):
                checks['singular_rejections'] += 1
                try:
                    instance(columns, 0, 1)
                except ValueError:
                    pass
                else:
                    raise AssertionError('singular accepted')
                continue
            for bias in range(N):
                for L in (1, 2, 3, 5):
                    z = instance(columns, bias, L)
                    tests += 1
                    max_ratio = max(max_ratio, z['expanded_cost'] / z['bound'])
    rng = random.Random(20261022)
    for r in range(4, 11):
        for _ in range(10):
            columns = [1 << j for j in range(r)]
            for _ in range(5 * r):
                a, b = rng.sample(range(r), 2)
                columns[a] ^= columns[b]
            z = instance(columns, rng.randrange(1 << r), rng.choice((1, 3, 7, 9)))
            tests += 1
            max_ratio = max(max_ratio, z['expanded_cost'] / z['bound'])
    for columns,bias,L,w in (([1],0,1,1), ([1,2],0,1,2), ([1<<8],0,1,16)):
        try:
            instance(columns,bias,L,w)
        except ValueError:
            checks['address_or_column_rejections'] += 1
        else:
            raise AssertionError('invalid instance accepted')
    report = dict(status='PASS', program_macro_instructions=len(CODE), permutation_cases=tests, negative_controls=dict(checks), max_observed_bound_ratio=max_ratio, scope='exact portable finite replay, not kernel proof or new kappa')
    return report
if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
