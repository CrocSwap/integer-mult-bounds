# SPDX-License-Identifier: Apache-2.0
"""Source modular oracle, literal descriptor execution and semantic controls."""
from pathlib import Path
from fractions import Fraction
from hashlib import sha256
from copy import deepcopy
import gzip
import json
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'vendor/bit-row-route-generator'))
from controller import compile_frontend, run_tapes
from offset import compile_offset
from generator import inverse
from interpreter import invert, run


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for row in json.loads((HERE / 'RETAINED.json').read_text())['files']:
        need(sha256((HERE / row['retained']).read_bytes()).hexdigest() == row['sha256'], 'retained source bytes')


def binary(value):
    digits = bin(value)[2:][::-1]
    return {-1: 3, **{i: int(v) for i, v in enumerate(digits)}, len(digits): 2}


def output(tape):
    i = 0
    while tape.get(i) in (0, 1):
        i += 1
    need(i > 0 and tape.get(i) == 2 and tape[i - 1] == 1, 'canonical positive output')
    need(all(v is None or -1 <= j <= i for j, v in tape.items()), 'no stale output suffix')
    return sum(tape[j] << j for j in range(i))


def low_matrix(n, q, lane=0, f=1):
    a = [int(i == j) for i in range(n) for j in range(n)]
    a[lane * n + 5 * f + lane] = q - 2
    return a


def frontend_run(machine, low, Q):
    b = machine['bits']
    source = {i * b + j: (v >> j) & 1 for i, v in enumerate(low) for j in range(b)}
    source[len(low) * b] = 2
    tapes = [source, {}, {}, binary(Q), {}]
    old_q = dict(tapes[3])
    stats = run_tapes(machine, tapes)
    need(tapes[3] == old_q and all(v is None for v in tapes[2].values()), 'Q preserved and quarter code erased')
    new_low = sum(tapes[1][i] << i for i in range(b))
    return new_low, output(tapes[4]) - 1, stats


def reject(action, label):
    try:
        action()
    except (ValueError, IndexError, KeyError):
        return label
    raise ValueError('accepted control: ' + label)


def main():
    authenticate()
    started = time.monotonic()
    program = json.loads(gzip.decompress((HERE / 'vendor/bit-row-route-generator/PROGRAM.json.gz').read_bytes()))
    S = [[Fraction(x) for x in row] for row in program['matcher']]
    directions = {1: S, -1: inverse(S)}
    cases = []
    for q in (3, 5, 7):
        for direction, matrix in directions.items():
            for col in range(8):
                weights = [int(4 * matrix[j][col]) for j in range(8)]
                machine = compile_frontend(q, weights, cells=64)
                low = low_matrix(8, q)
                for w in (2, 4, 9):
                    Q = q ** (w - 1)
                    M = q * Q
                    source_matrix = [[v.numerator * pow(v.denominator, -1, M) % M for v in row] for row in S]
                    if direction == -1:
                        source_matrix = invert(source_matrix, M)
                    total = sum(low[j] * source_matrix[j][col] for j in range(8))
                    expected = (total % q, total // q % Q)
                    new, carry, stats = frontend_run(machine, low, Q)
                    need((new, carry) == expected, 'independent source modular representative')
                    need(stats['steps'] <= 64 * 64 * machine['bits'] + 256 * Q.bit_length() + 2048, 'literal complete transition bound')
                    cases.append({'q': q, 'w': w, 'direction': direction, 'col': col, **stats})
    for direction, matrix in directions.items():
        q, f, n, row, lane, col = 5, 2, 16, 1, 1, 5
        positions = [row * n + j * f + lane for j in range(8)]
        machine = compile_frontend(q, [int(4 * matrix[j][col]) for j in range(8)], positions, n * n)
        low = low_matrix(n, q, lane, f)
        rational = sum(Fraction(low[pos]) * matrix[j][col] for j, pos in enumerate(positions))
        for w in (2, 4):
            Q = q ** (w - 1)
            full = rational.numerator * pow(rational.denominator, -1, q * Q) % (q * Q)
            got = frontend_run(machine, low, Q)
            need(got[:2] == (full % q, full // q), 'actual f2 strided old-cache addressing')
            cases.append({'q': q, 'w': w, 'direction': direction, 'f': f, **got[2]})
    offset_cases = 0
    for k in range(-7, 13):
        machine = compile_offset(k)
        for Q in (3, 5, 7, 9, 11, 13, 15, 17, 31, 125, 1025, 2**40 - 1):
            tapes = [binary(Q), {}]
            stats = run_tapes(machine, tapes)
            need(output(tapes[1]) == k * pow(4, -1, Q) % Q + 1, 'quarter descriptor exact modular output')
            need(stats['steps'] <= 256 * Q.bit_length() + 1024, 'binary descriptor transition bound')
            offset_cases += 1
    # Run the unchanged actual source, including its full forward/inverse route.
    low = low_matrix(8, 5)
    old = {'low': low, 'high': [(3*i*i+i+1) % 125 for i in range(64)], 'h': list(range(8)), 'd': list(range(8,16)), 'outer': [91,13,5], 'z': [-17,3,1], 'tape_head': 9}
    state = {'slots': {'462': 7, '461': 11}, 'owners': {'462': old, '461': {'arbitrary': [7,-12,999], 'tape_head': 4}}}
    result, trace = run(program, state)
    need(result['owners']['462']['low'] == low and result['owners']['462']['high'] == old['high'], 'actual source round trip')
    cell0 = compile_frontend(5, [int(4*S[j][0]) for j in range(8)], cells=64)
    need(frontend_run(cell0, low, 125)[:2] == (1, 1), 'admitted GL cell0 carry counterexample')
    original = [int(i == j) for i in range(8) for j in range(8)]
    original[1], original[10] = 1, 4
    cell5 = compile_frontend(5, [int(4*S[j][5]) for j in range(8)], cells=64)
    need(frontend_run(cell5, original, 125)[:2] == (4, 124), 'assigned original nonzero carry fixture')
    controls = []
    bad = original[:]
    bad[1] = 7
    controls.append(reject(lambda: frontend_run(cell5, bad, 125), 'out of radix low digit'))
    controls.append(reject(lambda: frontend_run(cell5, original[:-1], 125), 'incomplete old cache'))
    controls.append(reject(lambda: run_tapes(compile_offset(-3), [binary(4), {}]), 'even modulus'))
    controls.append(reject(lambda: run_tapes(compile_offset(-3), [{-1:3,0:1,1:0,2:2}, {}]), 'noncanonical modulus'))
    need(frontend_run(cell5, [0]*64, 125)[:2] != (4,124), 'premature cache retirement detected by source oracle')
    controls.append('premature cache retirement changes actual carry')
    forward = frontend_run(cell5, original, 125)[:2]
    inverse_machine = compile_frontend(5, [int(4*directions[-1][j][5]) for j in range(8)], cells=64)
    need(frontend_run(inverse_machine, original, 125)[:2] != forward, 'stale forward coefficient on inverse')
    controls.append('stale forward coefficient on inverse')
    new_low = [sum(original[r*8+j]*int(S[j][c]) for j in range(8)) % 5 for r in range(8) for c in range(8)]
    need(frontend_run(cell5, new_low, 125)[:2] != forward, 'new low used as carry source')
    controls.append('new low used as carry source')
    need((-3 // 4) % 125 != (-3 * pow(4, -1, 125)) % 125, 'ordinary division differs from modular representative')
    controls.append('rational floor before modular representative')
    source_state = deepcopy(state)
    source_state['owners']['462']['low'] = original
    _, complete_trace = run(program, source_state)
    omitted = deepcopy(program)
    omitted['steps'].remove(next(step for step in omitted['steps'] if step['op'] == 'carry_shift' and step['addresses'] == [5]))
    _, missing_trace = run(omitted, source_state)
    need(complete_trace['route_returns'][0][5] != missing_trace['route_returns'][0][5], 'actual omitted nonzero carry reaches route endpoint')
    controls.append('omitted actual nonzero carry cell5')
    overwritten = deepcopy(cell5)
    overwritten['code'].append(('write', 0, 0, overwritten['start']))
    overwritten['start'] = len(overwritten['code']) - 1
    controls.append(reject(lambda: frontend_run(overwritten, original, 125), 'owned old-cache overwrite'))
    mutant = deepcopy(cell5)
    # Corrupt every quarter dispatch branch so the mutation is reached.
    for i, op in enumerate(mutant['code']):
        if op[0] == 'branch' and op[1] == 2:
            mutant['code'][i] = ('branch', op[1], (), op[3])
    controls.append(reject(lambda: frontend_run(mutant, original, 125), 'missing paid quarter dispatch'))
    receipt = {'status': 'PARTIAL_ACTUAL_LOW_CACHE_TO_CARRY_DESCRIPTOR', 'actual_helper': 462, 'frame': 506, 'source_route_restored': True, 'actual_cell5': {'new_low':4,'carry':124}, 'admitted_GL_cell0': {'new_low':1,'carry':1}, 'frontend_cases':len(cases), 'offset_cases':offset_cases, 'peak_instructions':max(x['instructions'] for x in cases), 'peak_steps':max(x['steps'] for x in cases), 'controls':controls, 'full_payload_low_permutation_implemented':False, 'full_route_fixed_tape_closed':False, 'new_kappa':False}
    target = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        target.write_text(json.dumps(receipt, indent=2)+'\n')
    else:
        need(json.loads(target.read_text()) == receipt, 'result receipt')
    authenticate()
    print(json.dumps(receipt, indent=2))
    print('elapsed_seconds', round(time.monotonic()-started, 4))

if __name__ == '__main__':
    main()
