"""Stdlib-only, independent dense CPU and direct Gaussian kernel checks.

The oracle uses sparse tensor matrix entries and inverse addresses. It does
not execute CNOT words, incremental phase counters or C butterfly rows.
"""
from pathlib import Path
import argparse
import hashlib
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import move as m


def require(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(n):
    bits = bin(n)[2:]
    return '0' * (len(bits) - 1) + bits


def header(shape):
    return ''.join(map(gamma, shape))


def signed(n, w):
    require(-(1 << (w - 1)) <= n < (1 << (w - 1)), 'fixture signed range')
    return format(n % (1 << w), '0' + str(w) + 'b')


def encode(values, w):
    return ''.join(signed(a, w) + signed(b, w) for a, b in values)


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def rotate(z, q):
    return (z, (-z[1], z[0]), (-z[0], -z[1]), (z[1], -z[0]))[q % 4]


def unpack(address, f):
    mask = (1 << f) - 1
    return tuple((address >> ((8 - i) * f)) & mask for i in range(9))


def pack(coordinates, f):
    out = 0
    for coordinate in coordinates:
        out = (out << f) | coordinate
    return out


def linear(rows, coordinates):
    result = []
    for row in rows:
        value = 0
        for i, coordinate in enumerate(coordinates):
            if row >> i & 1:
                value ^= coordinate
        result.append(value)
    return tuple(result)


def inverse(rows):
    aug = [row | (1 << (9 + i)) for i, row in enumerate(rows)]
    for i in range(9):
        pivot = next(j for j in range(i, 9) if aug[j] >> i & 1)
        aug[i], aug[pivot] = aug[pivot], aug[i]
        for j in range(9):
            if j != i and aug[j] >> i & 1:
                aug[j] ^= aug[i]
    require([row & 511 for row in aug] == [1 << i for i in range(9)], 'inverse')
    return tuple(row >> 9 for row in aug)


def phase(recipe, coordinates, f):
    value = f * recipe['phase']
    for i in range(9):
        value += recipe['linear_Z4'][i] * coordinates[i].bit_count()
        for j in range(i + 1, 9):
            if recipe['quadratic_rows'][i] >> j & 1:
                value += 2 * (coordinates[i] & coordinates[j]).bit_count()
    return value % 4


RECIPE = json.loads((HERE / 'reference/RECIPE.json').read_text())
RIGHT, LEFT = RECIPE['lowered_recipe']['right'], RECIPE['lowered_recipe']['left']
IRIGHT, ILEFT = inverse(RIGHT['matrix_rows']), inverse(LEFT['matrix_rows'])


def oracle(values, shape, *, omit_constant=False, first_axis=False):
    f, r, p, s, w, _ = shape
    q, tail = 1 << f, s * r
    block = 1 << (9 * f)
    weights = []
    for x in range(q):
        z = (1, 0)
        for j in range(f):
            z = mul(z, (1, -1 if x >> j & 1 else 1))
        weights.append(z)
    result = []
    for outer in range(p):
        for output in range(block):
            z = linear(ILEFT, unpack(output, f))
            for suffix in range(tail):
                total = (0, 0)
                for t0 in range(q):
                    t = (t0,) + z[1:]
                    translated = tuple(a ^ (q - 1 if RIGHT['offset'] >> i & 1 else 0)
                                       for i, a in enumerate(t))
                    source = linear(IRIGHT, translated)
                    exponent = phase(RIGHT, source, f) + phase(LEFT, z, f)
                    if omit_constant:
                        exponent -= f * RIGHT['phase']
                    coeff = rotate(weights[z[0] ^ t0], exponent)
                    original = values[(outer * block + pack(source, f)) * tail + suffix]
                    term = mul(coeff, original)
                    total = total[0] + term[0], total[1] + term[1]
                require(total[0] % q == total[1] % q == 0, 'oracle nonintegral final image')
                result.append((total[0] // q, total[1] // q))
    return encode(result, w)


SYMBOLS = {'_': 0, '0': 1, '1': 2, '|': 3}


def numeric(code):
    result = []
    for op, *args in code:
        if op == 'read':
            branch = [-1] * 4
            for symbol, target in args[1].items():
                branch[SYMBOLS[symbol]] = target
            result.append((0, args[0], branch))
        elif op == 'write':
            result.append((1, args[0], SYMBOLS[args[1]]))
        elif op == 'move':
            require(args[1] in (-1, 1), 'nonunit move')
            result.append((2, args[0], args[1]))
        elif op == 'goto':
            result.append((3, args[0], None))
        elif op == 'halt':
            result.append((4, 0, None))
        else:
            raise ValueError('nonliteral opcode')
    return tuple(result)


def packet(shape, word, *, tapes=None):
    e, v = len(header(shape)), len(word)
    capacity = 4 * (e + v + 10)
    if tapes is None:
        tapes = [bytearray(capacity + 7) for _ in range(m.TAPES)]
        for tape in tapes:
            tape[0:2] = b'\x02\x03'
            tape[-2:] = b'\x01\x03'
    for tape in tapes:
        require(len(tape) >= e + v + 20, 'fixture allocation')
    for index, text in enumerate((header(shape) + '|01|', word)):
        # Opaque tail starts after six codes. Only DATA's exact blank endpoint
        # belongs to packet geometry.
        tapes[index][2] = 2
        tapes[index][3:3 + len(text)] = bytes(SYMBOLS[x] for x in text)
        tapes[index][3 + len(text)] = 0
    return tapes


def execute(code, tapes, entries, *, budget):
    code = numeric(code)
    heads, lows, highs = [3] * m.TAPES, [3] * m.TAPES, [3] * m.TAPES
    milestones = sorted((pc, name) for name, pc in entries.items())
    next_mark, marked, cursor = milestones[0][0], {}, 0
    pc = steps = writes = early = 0
    rejected = False
    while True:
        if pc == next_mark:
            marked[milestones[cursor][1]] = steps
            cursor += 1
            next_mark = milestones[cursor][0] if cursor < len(milestones) else -1
        op, tape, arg = code[pc]
        steps += 1
        if steps > budget:
            raise ValueError('finite verifier budget')
        if op == 0:
            pc = arg[tapes[tape][heads[tape]]]
            if pc < 0:
                rejected = True
                break
        elif op == 1:
            tapes[tape][heads[tape]] = arg
            if tape == m.DATA:
                writes += 1
                early += pc < entries['commit']
            pc += 1
        elif op == 2:
            heads[tape] += arg
            if heads[tape] < lows[tape]:
                lows[tape] = heads[tape]
            if heads[tape] > highs[tape]:
                highs[tape] = heads[tape]
            require(0 <= heads[tape] < len(tapes[tape]), 'fixture boundary escaped')
            pc += 1
        elif op == 3:
            pc = tape
        else:
            break
    return dict(steps=steps, rejected=rejected, writes=writes, early=early,
                heads=heads, lows=lows, highs=highs, milestones=marked)


def run_case(name, shape, values, *, accept=True, mutation=None, expected=None, tapes=None):
    word = encode(values, shape[4])
    tapes = packet(shape, word, tapes=tapes)
    owners = tuple(map(id, tapes))
    before = tuple(bytes(tape) for tape in tapes)
    code, _, entries = m._compile_move(mutation)
    f, e, v = shape[0], len(header(shape)), len(word)
    receipt = execute(code, tapes, entries, budget=(1 << 24) * (f * v + e + 1))
    require(receipt['rejected'] != accept, name + ': unexpected acceptance')
    require(tuple(map(id, tapes)) == owners, name + ': owner replacement')
    require(bytes(tapes[0]) == before[0], name + ': public HEADER value changed')
    require(receipt['early'] == 0, name + ': early public DATA write')
    if accept:
        expected = oracle(values, shape) if expected is None else expected
        target = bytearray(before[1])
        target[3:3 + v] = bytes(SYMBOLS[x] for x in expected)
        require(tapes[1] == target, name + ': complete direct kernel mismatch')
        require(receipt['writes'] == v, name + ': incomplete public commit')
        require(receipt['heads'] == [3] * m.TAPES, name + ': head return')
        require(all(bytes(tape) == before[i] for i, tape in enumerate(tapes) if i != 1),
                name + ': private/header/exterior not restored')
        history = sum(hi - lo + 1 for lo, hi in zip(receipt['lows'], receipt['highs']))
        require(history <= m.TAPES + 1024 * (v + e + 1), name + ': historical charge')
        receipt['history'] = history
    else:
        require(bytes(tapes[1]) == before[1], name + ': rejection changed original DATA')
        require(receipt['writes'] == 0, name + ': rejecting public commit')
    return dict(name=name, shape=shape, bits=v, **receipt), tapes


def verify(quick=False):
    m.authenticate()
    require(RECIPE['base_commit'] == 'e54523517d0f03e58352e647c403a5af3e525a57', 'base pin')
    require(RECIPE['event'] == ['MOVE', 415, 3, 99, False] and RECIPE['native_event_index'] == 24472,
            'selected source event')
    require(RECIPE['rank'] == RECIPE['lowered_recipe']['rank'] == 1, 'positive child rank')
    code, alphabet, entries = m._compile_move()
    numeric(code)
    require(alphabet == ('_', '0', '1', '|'), 'alphabet')
    require(max(args[0] for op, *args in code if op in ('read', 'write', 'move')) == 30,
            'fixed owner inventory')
    for f in (1, 2, 3):
        q = 1 << f
        for address in range(1 << (9 * f)) if f < 3 else range(0, 1 << (9 * f), 131071):
            x = unpack(address, f)
            require(linear(IRIGHT, linear(RIGHT['matrix_rows'], x)) == x, 'right inverse address')
            require(linear(ILEFT, linear(LEFT['matrix_rows'], x)) == x, 'left inverse address')
            require(pack(x, f) == address and all(a < q for a in x), 'complete packing')
    rng = random.Random(24472)
    shape = (1, 1, 1, 1, 4, 1)
    values = [(2 * rng.randrange(-1, 2), 2 * rng.randrange(-1, 2)) for _ in range(512)]
    expected = oracle(values, shape)
    require(expected != oracle(values, shape, omit_constant=True), 'absolute phase control')
    require(len(expected) == 4096, 'complete m=9 field')
    summary = dict(marker='PASS_LITERAL_SELECTED_MOVE_JOIN', locations=len(code), tapes=m.TAPES,
                   alphabet=alphabet, graph_sha256=hashlib.sha256(repr(code).encode()).hexdigest(),
                   source_event=RECIPE['event'], source_index=24472,
                   finite_address_checks=512 + 262144 + 1025, receipts=[], controls=[])
    if quick:
        summary['marker'] = 'PASS_LITERAL_SELECTED_MOVE_JOIN_QUICK_ONLY'
        return summary
    receipt, tapes = run_case('complete_nonzero_f1', shape, values, expected=expected)
    summary['receipts'].append(receipt)
    # Same fixed physical owners, shorter signed fields, huge binary cutoff,
    # and a following opaque tail. Historical capacities are retained.
    short = (1, 1, 1, 1, 2, 1 << 257)
    # Restore the clean previous DATA origin before replacing its supplied body.
    tapes[1][3:3 + len(expected)] = bytes(len(expected))
    receipt, _ = run_case('shorter_reuse_huge_cutoff', short, [(0, 0)] * 512, tapes=tapes)
    summary['receipts'].append(receipt)
    bad = [(0, 0)] * 512
    bad[0] = (1, 0)
    receipt, _ = run_case('child_nonintegral_after_three_completed_factors', (1, 1, 1, 1, 3, 1),
                          bad, accept=False)
    require('positive_child_' in receipt['milestones'], 'child rejection coverage')
    summary['receipts'].append(receipt)
    for mutation in ('drop_absolute_phase', 'swap_right_order', 'omit_offset', 'corrupt_commit'):
        try:
            run_case(mutation, shape, values, mutation=mutation, expected=expected)
        except ValueError as exc:
            require('complete direct kernel mismatch' in str(exc), 'unexpected mutation failure: ' + str(exc))
            summary['controls'].append(mutation)
        else:
            raise ValueError('undetected mutation: ' + mutation)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='assembly/address checks only; not full replay')
    parser.add_argument('--write', action='store_true', help='explicitly replace RESULT.json')
    args = parser.parse_args()
    require(not (args.quick and args.write), 'quick mode cannot write accepted evidence')
    result = verify(args.quick)
    rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE / 'RESULT.json').write_text(rendered)
    print(rendered, end='')
