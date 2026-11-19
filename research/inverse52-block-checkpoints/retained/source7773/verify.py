"""Check source-bound finite-window sampling and every work wire.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The packed and scalar gate interpreters follow the credited source checks.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

from sources import authenticate, domain, entry
import window

ROOT = Path(__file__).resolve().parent
Q = 2704


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pack(values, width):
    return sum(value << (width*i) for i, value in enumerate(values))


def lanes(records, width):
    used = max(records, default=0).bit_length()
    result = []
    for wire in range(used):
        data = bytearray((len(records)+7)//8)
        for i, value in enumerate(records):
            data[i//8] |= ((value >> wire) & 1) << (i % 8)
        result.append(int.from_bytes(data, 'little'))
    return result+[0]*(width-used)


def run(gates, before, count):
    state = before.copy()
    full = (1 << count)-1
    for target, controls in gates:
        mask = full
        for wire in controls:
            mask &= state[wire]
        state[target] ^= mask
    return state


def scalar(gates, value):
    for target, controls in gates:
        if all((value >> wire) & 1 for wire in controls):
            value ^= 1 << target
    return value


def gate_check(gates, width):
    for target, controls in gates:
        require(0 <= target < width and len(controls) <= 2, 'gate range or arity')
        require(all(0 <= x < width for x in controls) and len(set((target, *controls))) == 1+len(controls),
                'gate control range or alias')


def oracle_check(circuit, targets, values, cases, input_width, name):
    gates = window.clean_oracle(circuit, targets, values)
    gate_check(gates, circuit.next_wire)
    before = [a for a, _ in cases]
    after = [a | (b << input_width) for a, b in cases]
    initial, expected = lanes(before, circuit.next_wire), lanes(after, circuit.next_wire)
    actual = run(gates, initial, len(cases))
    require(actual == expected, name+' full forward and cleanup')
    require(run(tuple(reversed(gates)), expected, len(cases)) == initial, name+' full inverse')
    for a, b in (cases[0], cases[-1], cases[len(cases)//2]):
        require(scalar(gates, a) == (a | (b << input_width)), name+' scalar replay')
    return len(cases)


def arithmetic_checks():
    params = (tuple(range(6)), tuple(range(6, 12)))
    targets = tuple(range(12, 63))
    circuit = window.Circuit(63)
    output = window.prepare(circuit, *params)
    cases = []
    columns = json.loads((ROOT/'retained/NORMALIZERS.json').read_text())['mode_columns']
    exclusive = domain.verify_basis(columns)
    owner_hash = sha256()
    for a in range(52):
        for b in range(52):
            weights = entry.weights(a, b)
            expected = pack([x % Q for x in weights], 12) | (int(a == b == 0) << 50)
            cases.append((a | (b << 6), expected))
            owner = domain.owner_for_pair(a, b, columns, exclusive)
            require(max(map(abs, owner)) <= 1 and
                    tuple(sum(x*y for x, y in zip(col, owner, strict=True)) % 52 for col in columns[:2]) == (a, b),
                    'actual bounded owner realization')
            owner_hash.update(bytes(x+1 for x in owner))
    preparation = oracle_check(circuit, targets, output, cases, 12, 'all runtime preparation')
    circuit = window.Circuit(25)
    residue, digit = window.double_residue(circuit, tuple(range(12)))
    cases = [(r, (2*r % Q) | ((2*r // Q) << 12)) for r in range(Q)]
    doubling = oracle_check(circuit, tuple(range(12, 25)), (*residue, digit), cases, 12, 'all residue doubling')
    # Check every one-bit full-adder row separately from the wide circuit.
    for x, y, carry in product((0, 1), repeat=3):
        total = x ^ y ^ carry
        next_carry = (x & y) ^ ((x ^ y) & carry)
        require(total+2*next_carry == x+y+carry, 'full-adder truth table')
    return {'runtime_pairs': preparation, 'bounded_owner_sha256': owner_hash.hexdigest(),
            'residue_doublings': doubling, 'full_adder_rows': 8}


def transition_checks():
    cases, phases = {}, {}
    visits = 0
    for a in range(52):
        for b in range(52):
            weights = entry.weights(a, b)
            for depth in range(160):
                scale = 1 << depth
                residues = tuple(scale*w % Q for w in weights)
                new_residues = tuple(2*scale*w % Q for w in weights)
                phases[residues] = new_residues
                live = scale-sum(scale*w//Q for w in weights)
                require(live == sum(residues)//Q and 0 <= live <= 3, 'source pool count')
                leaves = [i for i, w in enumerate(weights) if 2*scale*w//Q-2*(scale*w//Q)]
                for node in range(live):
                    for coin in (0, 1):
                        child = 2*node+coin
                        done = child < len(leaves)
                        value = leaves[child] if done else child-len(leaves)
                        old = pack(residues, 12) | (node << 48) | (coin << 51)
                        new = pack(new_residues, 12) | (value << 48) | (int(done) << 50)
                        require(old not in cases or cases[old] == new, 'source phase consistency')
                        cases[old] = new
                        visits += 1
            require(tuple((1 << 160)*w % Q for w in weights) == tuple(16*w % Q for w in weights),
                    'four-step prefix and full period close')
    live_unique = len(cases)
    for residues, new_residues in phases.items():
        for label in range(4):
            for coin in (0, 1):
                old = pack(residues, 12) | (label << 48) | (1 << 50) | (coin << 51)
                new = pack(new_residues, 12) | (label << 48) | (1 << 50)
                cases[old] = new
    ordered = sorted(cases.items())
    circuit = window.Circuit(103)
    values = window.advance(circuit, tuple(range(51)), 51)
    count = oracle_check(circuit, tuple(range(52, 103)), values, ordered, 52, 'all source and absorbed transitions')
    digest = sha256()
    for old, new in ordered:
        digest.update(old.to_bytes(7, 'little')+new.to_bytes(7, 'little'))
    return {'source_edge_visits': visits, 'distinct_live_edges': live_unique,
            'source_residue_phases': len(phases), 'absorbed_edges': count-live_unique,
            'distinct_checked_edges': count, 'edge_sha256': digest.hexdigest()}


def reference(a, b, coins, length):
    weights = entry.weights(a, b)
    if a == b == 0:
        return 1, 0, 0
    node = 0
    for depth in range(1, length+1):
        digit = [(2**depth*w//Q) % 2 for w in weights]
        child = 2*node+((coins >> (depth-1)) & 1)
        for label, bit in enumerate(digit):
            child -= bit
            if child < 0:
                return 1, label, depth
        node = child
    return 0, 0, length+1


def prefix_cases(a, b, length):
    if a == b == 0:
        return [0, (1 << length)-1]
    weights = entry.weights(a, b)
    live, result = [(0, 0)], []
    for depth in range(1, length+1):
        leaves = [i for i, w in enumerate(weights) if (2**depth*w//Q) % 2]
        following = []
        for node, prefix in live:
            for coin in (0, 1):
                value = prefix | (coin << (depth-1))
                child = 2*node+coin
                if child < len(leaves):
                    result.extend((value, value | (((1 << length)-(1 << depth)))))
                else:
                    following.append((child-len(leaves), value))
        live = following
    result.extend(value for _, value in live)
    return sorted(set(result))


def window_check(length, exhaustive):
    built = window.build(length)
    gates, width = built['gates'], built['wires']
    gate_check(gates, width)
    before, after = [], []
    summaries = []
    prefix_comparisons = 0
    for a in range(52):
        for b in range(52):
            coins_list = range(1 << length) if exhaustive else prefix_cases(a, b, length)
            labels = [0]*4
            censored = 0
            for coins in coins_list:
                done, label, depth = reference(a, b, coins, length)
                initial = a | (b << 6) | (coins << 12)
                encoded = done | (label << 1) | (depth << 3)
                before.append(initial)
                after.append(initial | (encoded << (12+length)))
                if done:
                    labels[label] += 1
                else:
                    censored += 1
                if length == 4:
                    source = entry.prefix(a, b, [(coins >> i) & 1 for i in range(4)])
                    require(source['label'] == (label if done else None) and source['used'] == (depth if done else 4),
                            'unchanged source prefix')
                    prefix_comparisons += 1
            if exhaustive:
                weights = entry.weights(a, b)
                expected_labels = [(1 << length)*w//Q for w in weights]
                require(labels == expected_labels and censored == (1 << length)-sum(expected_labels),
                        'complete finite-window distribution')
                require(censored <= 3, 'exact censoring bound')
            summaries.append([a, b, *labels, censored])
    initial, expected = lanes(before, width), lanes(after, width)
    actual = run(gates, initial, len(before))
    require(actual == expected, 'whole window output, inputs and all cleanup')
    require(run(tuple(reversed(gates)), expected, len(before)) == initial, 'whole window inverse')
    if length == 4:
        dirty = initial.copy()
        for wire in built['output']:
            dirty[wire] ^= (1 << len(before))-1
        target = expected.copy()
        for wire in built['output']:
            target[wire] ^= (1 << len(before))-1
        require(run(gates, dirty, len(before)) == target, 'arbitrary output XOR contract')
        for wire in (0, built['coins'][0], built['output'][-1], built['states'][0][0], width-1):
            changed = actual.copy()
            changed[wire] ^= (1 << len(before))-1
            require(changed != expected, 'input, coin, depth or work corruption accepted')
        wrong = (*gates, (built['output'][1], (built['output'][2],)),
                 (built['output'][2], (built['output'][1],)), (built['output'][1], (built['output'][2],)))
        require(run(wrong, initial, len(before)) != expected, 'wrong ordered labels accepted')
        prefix_length = built['bill']['preparation_oracle_gates']+length*built['bill']['draw_oracle_gates']
        require(run(gates[:-prefix_length], initial, len(before)) != expected, 'omitted history cleanup accepted')
    for i in (0, len(before)//2, len(before)-1):
        require(scalar(gates, before[i]) == after[i] and scalar(tuple(reversed(gates)), after[i]) == before[i],
                'separate scalar whole-window replay')
    return {'length': length, 'domain': 'all coin strings' if exhaustive else 'all stopping prefixes with zero/one suffixes and all live prefixes',
            'cases': len(before), 'source_prefix_comparisons': prefix_comparisons,
            'summary_sha256': sha256(json.dumps(summaries, separators=(',', ':')).encode()).hexdigest(),
            'bill': built['bill']}


def collect():
    count = authenticate()
    path = ROOT/'retained/arithmetic/verify.py'
    args = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []), '-B', str(path)]
    replay = subprocess.run(args, capture_output=True, text=True, check=True, timeout=60)
    require('PASS_PAIRED_DDG_ARITHMETIC_STEP' in replay.stdout, 'unchanged primitive source')
    arithmetic = arithmetic_checks()
    transitions = transition_checks()
    windows = [window_check(n, exhaustive) for n, exhaustive in [(1, True), (4, True), (8, True), (16, False)]]
    bills = []
    for length in (1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127):
        bill = window.build(length)['bill']
        pop = (length+1).bit_count()
        require(bill['gates'] == 3643+1956*length and bill['clean_work_bits'] == 610+51*length,
                'all-L total gate and work formula')
        require((bill['X'], bill['CNOT'], bill['Toffoli']) == (260+180*length+pop, 2449+1436*length-pop, 934+340*length),
                'all-L gate-type formula')
        require(bill['answer_oracle_gates'] == 2*length+5, 'telescoping depth bill')
        bills.append(bill)
    for length in (0, -1, True, 1.0):
        try:
            window.build(length)
        except ValueError:
            continue
        raise ValueError('invalid window accepted')
    return {'source_files': count, 'arithmetic': arithmetic, 'transitions': transitions,
            'windows': windows, 'bill_checks': bills,
            'gate_formula': '3643+1956*L', 'clean_work_formula': '610+51*L',
            'output_bits': '3+bit_length(L+1)', 'input_bits': '12+L',
            'censoring_probability': 'n_L/2^L <= 3/2^L; censored output is explicit'}


def main():
    actual = collect()
    require(actual == json.loads((ROOT/'RESULT.json').read_text()), 'saved result mismatch')
    print('PASS_INVERSE52_WINDOW_CIRCUIT')
    print('All 2704 source pairs; fixed-L ordered label/depth or explicit censoring; inputs and work restored')
    print('Exact gates 3643+1956*L; clean work bits 610+51*L; output bits 3+bit_length(L+1)')
    print('Complete prefix and periodic transition domain; full windows at L=1,4,8; all stopping prefixes at L=16')
    print('Literal forward/inverse, arbitrary output XOR, source prefix and censoring-law checks pass')


if __name__ == '__main__':
    main()
