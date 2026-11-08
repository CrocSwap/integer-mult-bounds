# SPDX-License-Identifier: Apache-2.0
"""Complete-payload fixtures and independent modular coordinate oracle."""
from fractions import Fraction
import hashlib
import itertools
import json
from math import gcd
import random
import time

from compiler import compile_program
from bounds import ledger
from source import load, require

# Determinant one, nontrivial first-coordinate carry, and nonintegral carries
# in the opposite source direction. This is an explicitly reduced fixture.
MATRIX = ((1, Fraction(1, 2)), (1, Fraction(3, 2)))


def modular_inverse(a, modulus):
    n = len(a)
    x = [list(row)+[int(i == j) for j in range(n)] for i, row in enumerate(a)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if gcd(x[r][col], modulus) == 1), None)
        require(pivot is not None, 'oracle invertible matrix')
        x[col], x[pivot] = x[pivot], x[col]
        unit = pow(x[col][col], -1, modulus)
        x[col] = [v*unit % modulus for v in x[col]]
        for r in range(n):
            if r != col:
                factor = x[r][col]
                x[r] = [(v-factor*w) % modulus for v, w in zip(x[r], x[col])]
    return [row[n:] for row in x]


def complete_gl2(q):
    return tuple(g for g in itertools.product(range(q), repeat=4) if (g[0]*g[3]-g[1]*g[2]) % q)


def oracle(matrix, q, Q, z, payload, inverse=False):
    """Push by exact qQ arithmetic, independently of emitted source frontends."""
    n = len(matrix)
    require(n == 2, 'complete finite oracle uses independent GL2 determinant')
    d, modulus = n*n, q*Q
    a = [[Fraction(v).numerator*pow(Fraction(v).denominator, -1, modulus) % modulus for v in row]
         for row in matrix]
    if inverse:
        a = modular_inverse(a, modulus)
    types = complete_gl2(q)
    index = {g: i for i, g in enumerate(types)}
    H = Q**d*z
    require(len(payload) == len(types)*H, 'oracle complete payload')
    result = [None]*len(payload)
    for i, g in enumerate(types):
        raw = [sum(g[r*n+j]*a[j][col] for j in range(n)) for r in range(n) for col in range(n)]
        low = tuple(x % q for x in raw)
        carry = tuple(((x-y)//q) % Q for x, y in zip(raw, low))
        for ordinal, high in enumerate(itertools.product(range(Q), repeat=d)):
            target = 0
            for x, c in zip(high, carry):
                target = target*Q+(x+c) % Q
            for tail in range(z):
                j = index[low]*H+target*z+tail
                require(result[j] is None, 'oracle injective coordinate permutation')
                result[j] = payload[i*H+ordinal*z+tail]
    require(all(x is not None for x in result), 'oracle complete permutation')
    return result


def fixture(modules, program, Q, z, payload, translated=True):
    m = modules['machine']
    origins = [3*i-41 if translated else 0 for i in range(program.tapes)]
    bank = [({}, origin) for origin in origins]

    def marked(values, tape):
        origin = origins[tape]
        return ({origin: m.LEFT, **{origin+i+1: value for i, value in enumerate(values)},
                 origin+len(values)+1: m.RIGHT}, origin+1)

    bank[0] = marked([m.ONE if x else m.ZERO for x in payload], 0)
    for tape, value in ((5, Q), (20, z)):
        bank[tape] = marked([m.ONE if value >> i & 1 else m.ZERO for i in range(value.bit_length())], tape)
    # Independently owned unrelated tapes can hold arbitrary nonblank data.
    for tape in (6, 16):
        origin = origins[tape]
        bank[tape] = ({origin-2: m.MARK, origin: m.ONE, origin+4: m.ZERO}, origin)
    return bank


def inspect(modules, result, bank, expected):
    m = modules['machine']
    owner_origin = bank[0][1]-1
    cells = {owner_origin: m.LEFT, **{owner_origin+i+1: m.ONE if bit else m.ZERO for i, bit in enumerate(expected)},
             owner_origin+len(expected)+1: m.RIGHT}
    for i, tape in enumerate(result):
        got = tape.cells if isinstance(tape, m.Tape) else tape.snapshot()
        if i == 0:
            require(got == cells and tape.head == bank[i][1], 'complete original-owner endpoint')
        elif i in (5, 6, 16, 20):
            require(got == bank[i][0] and tape.head == bank[i][1], 'input/spectator return '+str(i))
        else:
            require(not got and tape.head == bank[i][1], 'all owned work erased/returned '+str(i))


def run_case(modules, program, metadata, Q, z, mode='sparse', seed=12, boundary_checks=False, pattern='random'):
    volume = len(metadata['types'])*Q**metadata['d']*z
    rng = random.Random(seed)
    require(pattern in ('random', 'zero', 'one'), 'bounded payload fixture pattern')
    payload = [rng.randrange(2) if pattern == 'random' else int(pattern == 'one') for _ in range(volume)]
    expected = oracle(MATRIX, metadata['q'], Q, z, payload, metadata['inverse'])
    bank = fixture(modules, program, Q, z, payload)
    cap = 100_000_000
    start = time.monotonic()
    if mode == 'sparse':
        machine = modules['machine']
        run = machine.Machine(program, [machine.Tape(cells, head) for cells, head in bank])
        boundary_counts = dict(fiber_entry=0, local_cache_last_use_boundary=0, commit_entry=0)
        if boundary_checks:
            original_cache = [((x >> bit) & 1) for g in complete_gl2(metadata['q'])
                              for x in g for bit in range((metadata['q']-1).bit_length())]
            cache_origin = bank[21][1]
            full_cache = {cache_origin: machine.LEFT,
                          **{cache_origin+j+1: machine.ONE if bit else machine.ZERO for j, bit in enumerate(original_cache)},
                          cache_origin+len(original_cache)+1: machine.RIGHT}
            H = Q**metadata['d']*z
            precommit = [bit for i in range(len(metadata['types']))
                         for bit in expected[metadata['permutation'][i]*H:(metadata['permutation'][i]+1)*H]]
            pc_names = {pc: name for name, pc in metadata['boundaries'].items() if name in boundary_counts}
            while not run.halted:
                require(run.steps < cap, 'bounded experimental step limit')
                name = pc_names.get(run.pc)
                if name:
                    require(run.tapes[21].cells == full_cache, 'entire old cache retained through its consumers')
                    i = boundary_counts[name]
                    if name == 'fiber_entry':
                        require(run.tapes[0].head == bank[0][1]+i*H, 'complete source fiber position')
                        require(run.tapes[21].head == cache_origin+1+i*metadata['d']*((metadata['q']-1).bit_length()),
                                'source low/cache ordinal agreement')
                    elif name == 'local_cache_last_use_boundary':
                        local_origin = bank[17][1]
                        low = complete_gl2(metadata['q'])[i]
                        local_bits = [(x >> bit) & 1 for x in low
                                      for bit in range((metadata['q']-1).bit_length())]
                        local_bits += [0]*((metadata['local_cells']-metadata['d'])*((metadata['q']-1).bit_length()))
                        expected_local = {local_origin+j: machine.ONE if bit else machine.ZERO for j, bit in enumerate(local_bits)}
                        expected_local[local_origin+len(local_bits)] = machine.RIGHT
                        require(run.tapes[17].cells == expected_local and run.tapes[17].head == local_origin,
                                'complete local old cache through final coordinate')
                        block = precommit[i*H:(i+1)*H]
                        origin = bank[19][1]
                        expected_block = {origin: machine.LEFT,
                                          **{origin+j+1: machine.ONE if bit else machine.ZERO for j, bit in enumerate(block)},
                                          origin+H+1: machine.RIGHT}
                        require(run.tapes[19].cells == expected_block and run.tapes[19].head == origin+1,
                                'complete staged fiber before source installation')
                    else:
                        origin = bank[0][1]-1
                        expected_precommit = {origin: machine.LEFT,
                                              **{origin+j+1: machine.ONE if bit else machine.ZERO for j, bit in enumerate(precommit)},
                                              origin+volume+1: machine.RIGHT}
                        require(run.tapes[0].cells == expected_precommit, 'all carries precede low commit')
                        require(run.tapes[21].head == cache_origin+1, 'complete old-cache return before commit')
                    boundary_counts[name] += 1
                run.step()
            require(boundary_counts == dict(fiber_entry=0 if Q == 1 else 48,
                                             local_cache_last_use_boundary=0 if Q == 1 else 48,
                                             commit_entry=1), 'all complete low-domain boundaries reached')
        else:
            run.run(cap)
        inspect(modules, run.tapes, bank, expected)
        spans = sum(max(v)-min(v)+1 if v else 1 for v in run.visits)
        steps = run.steps
    else:
        independent = modules['independent']
        independent.TAPES = program.tapes  # validator parameter only; no opcode semantics change
        table = dict(tapes=program.tapes, entry=program.entry, instructions=program.instructions)
        tapes, steps = independent.execute(table, bank, cap)
        inspect(modules, tapes, bank, expected)
        spans = sum(t.high-t.low+1 for t in tapes)
    invoice = ledger(metadata, Q, z)
    require(steps <= invoice['transitions'], 'complete written transition bill')
    require(spans <= invoice['visited_cells'], 'complete written visited-cell bill')
    return dict(Q=Q, z=z, inverse=metadata['inverse'], mode=mode, volume=volume, pattern=pattern, seed=seed,
                steps=steps, spans=spans, seconds=round(time.monotonic()-start, 4),
                boundaries=boundary_counts if mode == 'sparse' and boundary_checks else None,
                transition_bound=invoice['transitions'], visited_cell_bound=invoice['visited_cells'],
                input_sha256=hashlib.sha256(bytes(payload)).hexdigest(),
                output_sha256=hashlib.sha256(bytes(expected)).hexdigest())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--Q', type=int, default=1)
    parser.add_argument('--z', type=int, default=1)
    parser.add_argument('--inverse', action='store_true')
    parser.add_argument('--mode', choices=('sparse', 'dense'), default='sparse')
    parser.add_argument('--boundaries', action='store_true')
    args = parser.parse_args()
    modules, _raw = load()
    program, metadata = compile_program(modules, 3, MATRIX, args.inverse)
    print('COMPILED', len(program.instructions), 'instructions', program.tapes, 'tapes', flush=True)
    print(json.dumps(run_case(modules, program, metadata, args.Q, args.z, args.mode,
                             boundary_checks=args.boundaries), sort_keys=True), flush=True)
