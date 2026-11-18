"""Check every runtime pair and transition. Ali Romman, with Codex. Apache-2.0."""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import parametric as circuit
from sources import graph

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packet(phase, node, done=False):
    return phase | (node << 8) | (int(done) << 10)


def comparisons():
    records = []
    summaries = []
    for a in range(1, 13):
        for b in range(1, 13):
            weights = ((13 - a) * (13 - b), (13 - a) * b, a * (13 - b), a * b)
            source_weights, counts, table, _ = graph.make(a, b)
            require(weights == source_weights, 'source weight order')
            states = [(k, j) for k, count in enumerate(counts) for j in range(count)]
            unfinished = 1
            powers = 1
            source_index = 0
            pair_rows = []
            phases = set()
            for depth in range(156):
                phase = powers % 169
                require(phase not in phases, 'phase repeated early')
                phases.add(phase)
                leaves = [i for i, w in enumerate(weights)
                          if (2 * powers * w) // 169 - 2 * ((powers * w) // 169)]
                require(unfinished == counts[depth], 'floor and source live counts')
                for node in range(unfinished):
                    for coin in (0, 1):
                        child = 2 * node + coin
                        done = child < len(leaves)
                        output = leaves[child] if done else child - len(leaves)
                        target = table[source_index + node][coin]
                        if target >= 312:
                            require(done and target - 312 == output, 'source leaf')
                        else:
                            require(not done and states[target] == ((depth + 1) % 156, output),
                                    'source continuation')
                        resident = (coin << circuit.COIN) | (a << 12) | (b << 16)
                        pair_rows.append((packet(phase, node) | resident,
                                          packet((2 * powers) % 169, output, done) | resident))
                source_index += unfinished
                unfinished = 2 * unfinished - len(leaves)
                powers *= 2
            require((powers % 169, unfinished, source_index, len(pair_rows)) == (1, 1, 312, 624),
                    'period closure')
            digest = sha256(json.dumps(pair_rows, separators=(',', ':')).encode()).hexdigest()
            summaries.append(dict(a=a, b=b, transitions=len(pair_rows), sha256=digest))
            records.extend(pair_rows)
    return records, summaries


def lanes(records, width, input_width=20):
    result = []
    for wire in range(input_width):
        data = bytearray((len(records) + 7) // 8)
        for i, record in enumerate(records):
            data[i // 8] |= ((record >> wire) & 1) << (i % 8)
        result.append(int.from_bytes(data, 'little'))
    return result + [0] * (width - input_width)


def run(gates, state, count):
    result = state.copy()
    full = (1 << count) - 1
    for target, controls in gates:
        flip = full
        for control in controls:
            flip &= result[control]
        result[target] ^= flip
    return result


def scalar(gates, record):
    for target, controls in gates:
        if all(record & (1 << control) for control in controls):
            record ^= 1 << target
    return record


def subtraction_check():
    builder = circuit.Circuit()
    output = circuit.subtract_mod(builder, tuple(range(8)), tuple(range(12, 20)))
    cases = [(a, b) for a in range(169) for b in range(169)]
    initial = lanes([a | (b << 12) for a, b in cases], builder.next_wire)
    actual = run(builder.gates, initial, len(cases))
    expected = lanes([(a - b) % 169 for a, b in cases], builder.next_wire)
    full = (1 << len(cases)) - 1
    values = [full if bit is True else 0 if bit is False else actual[bit] for bit in output]
    require(values == expected[:8], 'complete modular subtraction domain')
    require(run(tuple(reversed(builder.gates)), actual, len(cases)) == initial,
            'subtraction uncomputation')
    return len(cases)


def collect():
    gates, width = circuit.reversible_step()
    for target, controls in gates:
        require(0 <= target < width and target not in circuit.READ_ONLY, 'read-only input or gate target')
        require(len(controls) <= 2 and len(set(controls)) == len(controls), 'gate arity')
        require(all(0 <= wire < width and wire != target for wire in controls), 'gate controls')
    pairs, summaries = comparisons()
    before, after = zip(*pairs, strict=True)
    require(len(pairs) == 89856 and len(set(after)) == len(after), 'complete injective domain')
    initial, expected = lanes(before, width), lanes(after, width)
    actual = run(gates, initial, len(pairs))
    require(actual == expected, 'forward, parameters, coin or cleanup')
    require(run(tuple(reversed(gates)), expected, len(pairs)) == initial, 'full inverse')
    for wire in (10, 12, circuit.FIRST_SCRATCH):
        wrong = actual.copy()
        wrong[wire] ^= (1 << len(pairs)) - 1
        require(wrong != expected, 'fault control')
    swapped = run(((8, (9,)), (9, (8,)), (8, (9,))), actual, len(pairs))
    require(swapped != expected, 'output-order control')
    scalar_cases = [pairs[624 * i + j] for i in range(144) for j in (0, 623)]
    for old, new in scalar_cases:
        require(scalar(gates, old) == new, 'separate scalar forward')
        require(scalar(tuple(reversed(gates)), new) == old, 'separate scalar inverse')
    source_mode = ['-O'] if sys.flags.optimize else []
    source_run = subprocess.run([sys.executable, '-W', 'error', *source_mode, '-B',
                                 str(ROOT / 'retained/paired-ddg-arithmetic-step/verify.py')],
                                check=True, capture_output=True, text=True, timeout=30)
    require('PASS_PAIRED_DDG_ARITHMETIC_STEP' in source_run.stdout, 'unchanged fixed-pair replay')
    counts = Counter(len(controls) for _, controls in gates)
    return dict(schema_version=1, parameter_pairs=144, transitions=len(pairs),
                gates=len(gates), x=counts[0], cnot=counts[1], toffoli=counts[2],
                packet_bits=11, parameter_bits=8, resident_coin_bits=1,
                clean_backing_bits=11, temporary_bits=width - circuit.FIRST_SCRATCH,
                clean_work_bits=width - 20, total_wires=width,
                gate_sha256=sha256(json.dumps(gates, separators=(',', ':')).encode()).hexdigest(),
                subtraction_cases=subtraction_check(), scalar_forward_inverse_cases=len(scalar_cases),
                fault_controls=4, source_receipt=source_run.stdout.strip().splitlines(),
                pair_certificates=summaries)


def main():
    result = collect()
    require(result == json.loads((ROOT / 'RESULT.json').read_text()), 'result certificate')
    print('PASS_RUNTIME_PAIRED_DDG_ARITHMETIC')
    print(f"144 runtime pairs; {result['transitions']} complete forward/inverse transitions")
    print(f"{result['x']} X; {result['cnot']} CNOT; {result['toffoli']} Toffoli; {result['gates']} gates")
    print(f"{result['temporary_bits']} temporary bits + 11 clean backing bits = {result['clean_work_bits']} clean work bits")


if __name__ == '__main__':
    main()
