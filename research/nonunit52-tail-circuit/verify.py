"""Check all runtime tails and actual source cases. Ali Romman, with Codex. Apache-2.0."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

import tail
from sources import authenticate, domain, entry

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def packet(phase, node, done=False):
    return phase | (node << 4) | (int(done) << 6)


def resident(coin, u, v, orientation, mixed):
    return (coin << 7) | (u << 8) | (v << 12) | (orientation << 16) | (mixed << 17)


def weights(mixed, orientation, u, v):
    row = (13-u, u, 13-v, v) if mixed else (13-u, u, 0, 0)
    return (row[0], row[2], row[1], row[3]) if orientation else row


def comparisons():
    pairs, scalar_cases, summaries = [], [], []
    for mixed in range(2):
        for orientation in range(2):
            for u in range(1, 13):
                for v in range(1, 13):
                    values = weights(mixed, orientation, u, v)
                    start = len(pairs)
                    phases = set()
                    for depth in range(12):
                        power = 1 << depth
                        phase = power % 13
                        require(phase not in phases, 'complete phase period')
                        phases.add(phase)
                        leaves = [j for j, value in enumerate(values)
                                  if 2 * power * value // 13 - 2 * (power * value // 13)]
                        require(len(leaves) == mixed + 1, 'constant live pool')
                        for node in range(mixed + 1):
                            for coin in (0, 1):
                                child = 2 * node + coin
                                done = child < len(leaves)
                                output = leaves[child] if done else child - len(leaves)
                                fixed = resident(coin, u, v, orientation, mixed)
                                pairs.append((packet(phase, node) | fixed,
                                              packet(2 * phase % 13, output, done) | fixed))
                    require((1 << 12) % 13 == 1 and len(phases) == 12, 'period closes')
                    scalar_cases.extend((pairs[start], pairs[-1]))
                    rows = pairs[start:]
                    summaries.append(dict(mixed=mixed, orientation=orientation, u=u, v=v,
                                          edges=len(rows), sha256=sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()))
    return pairs, scalar_cases, summaries


def lanes(records, width):
    result = []
    for wire in range(18):
        data = bytearray((len(records) + 7) // 8)
        for index, record in enumerate(records):
            data[index // 8] |= ((record >> wire) & 1) << (index % 8)
        result.append(int.from_bytes(data, 'little'))
    return result + [0] * (width - 18)


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


def addition_check():
    builder = tail.Circuit()
    output = tail.add_mod(builder, tuple(range(4)), tuple(range(8, 12)))
    cases = [(a, b) for a in range(13) for b in range(13)]
    initial = lanes([a | (b << 8) for a, b in cases], builder.next_wire)
    actual = run(builder.gates, initial, len(cases))
    full = (1 << len(cases)) - 1
    values = [full if signal is True else 0 if signal is False else actual[signal] for signal in output]
    expected = lanes([(a+b) % 13 for a, b in cases], builder.next_wire)
    require(values == expected[:4], 'all modular additions')
    require(run(tuple(reversed(builder.gates)), actual, len(cases)) == initial, 'adder uncomputation')
    return len(cases)


def actual_sources(lookup):
    raw = (ROOT / 'retained/NORMALIZERS.json').read_bytes()
    manifest = json.loads((ROOT / 'retained/inverse-domain/SOURCES.json').read_text())
    pin = next(row for row in manifest['files'] if row['path'] == 'research/coded-native-caller/NORMALIZERS.json')
    domain.authenticate(raw, pin)
    columns = json.loads(raw)['mode_columns']
    exclusive = domain.verify_basis(columns)
    records, counts, edges = [], Counter(), 0
    for a in range(52):
        for b in range(52):
            original = ((52-a)*(52-b), (52-a)*b, a*(52-b), a*b)
            source = entry.describe(a, b)
            if source['kind'] not in ('mixed', 'endpoint'):
                try:
                    tail.recipe(a, b)
                except ValueError:
                    continue
                raise ValueError('wrong source domain accepted')
            recipe = tail.recipe(a, b)
            mixed, orientation, u, v = (recipe[k] for k in ('mixed', 'orientation', 'u', 'v'))
            reduced = weights(mixed, orientation, u, v)
            require(tuple(value % 169 for value in original) == tuple(13 * value for value in reduced),
                    'exact original tail residues')
            require(source['roots'] == mixed + 1, 'source live pool')
            owner = domain.owner_for_pair(a, b, columns, exclusive)
            require(max(map(abs, owner)) <= 1 and
                    tuple(sum(c*x for c, x in zip(col, owner, strict=True)) % 52 for col in columns[:2]) == (a, b),
                    'actual bounded owner realization')
            for depth in range(12):
                power = 1 << (4 + depth)
                live = power - sum(power * value // 2704 for value in original)
                leaves = [j for j, value in enumerate(original)
                          if 2 * power * value // 2704 - 2 * (power * value // 2704)]
                require(live == mixed + 1, 'original pool at every phase')
                for node in range(live):
                    for coin in (0, 1):
                        child = 2 * node + coin
                        done = child < len(leaves)
                        output = leaves[child] if done else child - len(leaves)
                        phase = (1 << depth) % 13
                        fixed = resident(coin, u, v, orientation, mixed)
                        old = packet(phase, node) | fixed
                        new = packet(2 * phase % 13, output, done) | fixed
                        require(lookup[old] == new, 'ordered original denominator-2704 edge')
                        edges += 1
            counts[source['kind']] += 1
            records.append(dict(a=a, b=b, **recipe, roots=mixed+1))
    require(counts == {'endpoint': 96, 'mixed': 288} and edges == 16128, 'complete actual source coverage')
    for a, b in ((-1, 0), (52, 0), (0, 52), (True, 0)):
        try:
            tail.recipe(a, b)
        except ValueError:
            continue
        raise ValueError('invalid residue accepted')
    return records, edges


def collect():
    source_files = authenticate()
    gates, width = tail.reversible_step()
    for target, controls in gates:
        require(0 <= target < width and target not in tail.READ_ONLY, 'gate target and read-only inputs')
        require(len(controls) <= 2 and len(set(controls)) == len(controls), 'gate arity')
        require(all(0 <= wire < width and wire != target for wire in controls), 'gate controls')
    pairs, scalar_cases, summaries = comparisons()
    before, after = zip(*pairs, strict=True)
    require(len(pairs) == len(set(before)) == len(set(after)) == 20736, 'complete injective runtime domain')
    initial, expected = lanes(before, width), lanes(after, width)
    actual = run(gates, initial, len(pairs))
    require(actual == expected, 'forward outputs, resident inputs and complete cleanup')
    inverse = tuple(reversed(gates))
    require(run(inverse, expected, len(pairs)) == initial, 'complete inverse')
    for old, new in scalar_cases:
        require(scalar(gates, old) == new and scalar(inverse, new) == old, 'separate scalar replay')
    for wire in (6, 8, 17, tail.FIRST_SCRATCH):
        require(run((*gates, (wire, ())), initial, len(pairs)) != expected, 'changed stop, parameter, mode or workspace')
    exchange = ((4, (5,)), (5, (4,)), (4, (5,)))
    swapped = run((*gates, *exchange), initial, len(pairs))
    require(swapped != expected, 'changed output order')
    source_rows, source_edges = actual_sources(dict(pairs))
    source_mode = ['-O'] if sys.flags.optimize else []
    replay = subprocess.run([sys.executable, '-W', 'error', *source_mode, '-B',
                             str(ROOT / 'retained/arithmetic/verify.py')], check=True,
                            capture_output=True, text=True, timeout=30)
    require('PASS_PAIRED_DDG_ARITHMETIC_STEP' in replay.stdout, 'unchanged primitive source replay')
    counts = Counter(len(controls) for _, controls in gates)
    require((counts[0], counts[1], counts[2], width) == (70, 895, 312, 400), 'exact complete circuit bill')
    return dict(schema_version=1, source_files=source_files, runtime_parameter_graphs=len(summaries), runtime_edges=len(pairs),
                x=counts[0], cnot=counts[1], toffoli=counts[2], gates=len(gates),
                packet_bits=7, parameter_bits=10, resident_coin_bits=1,
                temporary_bits=width-tail.FIRST_SCRATCH, clean_backing_bits=7,
                clean_work_bits=width-18, total_wires=width,
                gate_sha256=sha256(json.dumps(gates, separators=(',', ':')).encode()).hexdigest(),
                modular_addition_cases=addition_check(), scalar_forward_inverse_cases=len(scalar_cases),
                gate_fault_controls=5, actual_pairs=len(source_rows), actual_tail_edges=source_edges,
                source_receipt=replay.stdout.strip().splitlines(),
                runtime_certificates=summaries, source_recipes=source_rows)


def main():
    require(collect() == json.loads((ROOT / 'RESULT.json').read_text()), 'complete tail certificate')
    print('PASS_NONUNIT52_TAIL_CIRCUIT')
    print('288 mixed and 96 endpoint source pairs; 16128 exact source-tail edges')
    print('576 runtime parameter graphs; 20736 full forward/inverse transitions')
    print('70 X; 895 CNOT; 312 Toffoli; 1277 gates; 375 temporary + 7 backing = 382 clean bits')


if __name__ == '__main__':
    main()
