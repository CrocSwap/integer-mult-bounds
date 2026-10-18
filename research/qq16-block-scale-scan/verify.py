#!/usr/bin/env python3
"""Read-only scale/composition check. Arham Tahir / Codex. Apache-2.0."""
import argparse
from collections import Counter
from dataclasses import replace
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scan


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(path):
    require(path.stat().st_size < 200000, "JSON capacity")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def sources():
    pins = strict_json(HERE / 'PREDECESSOR.json')
    expected_paths = [('research/qq16-rounded-pair-bit-circuit/circuit.py', 'vendor/pair.py'),
                      ('research/qq16-rounded-pair-bit-circuit/README.md', 'vendor/pair-README.md'),
                      ('research/qq16-finite-dyadic-format/README.md', 'vendor/format-README.md')]
    require([(x['source'], x['snapshot']) for x in pins['files']] == expected_paths, 'source inventory')
    for item in pins['files']:
        data = (HERE / item['snapshot']).read_bytes()
        require(len(data) < 40000, 'source capacity')
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'source SHA256 mismatch')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == item['git_blob'], 'source Git blob mismatch')
    spec = importlib.util.spec_from_file_location('pinned_pair', HERE / 'vendor/pair.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def oracle(values, reserve):
    magnitude = max(map(abs, values))
    return (max(0, magnitude.bit_length() - 1 - reserve), int(magnitude == 0),
            int(magnitude == 0 or magnitude >= 1 << reserve))


def exhaust():
    cases = circuits = 0
    domains = [(w, 1) for w in range(1, 9)] + [(w, 2) for w in range(1, 7)] + [(w, 4) for w in range(1, 5)]
    for width, count in domains:
        size = 1 << (width * count)
        inputs = [bytearray((size + 7) // 8) for _ in range(width * count)]
        values = []
        for row in range(size):
            signed = []
            for component in range(count):
                unsigned = (row >> (component * width)) & ((1 << width) - 1)
                signed.append(unsigned - ((unsigned >> (width - 1)) << width))
            values.append(tuple(signed))
            for bit in range(width * count):
                if (row >> bit) & 1:
                    inputs[bit][row // 8] |= 1 << (row % 8)
        masks = [int.from_bytes(x, 'little') for x in inputs]
        for reserve in range(width):
            circuit = scan.compile_scan(width, count, reserve)
            expected = [bytearray((size + 7) // 8) for _ in range(width.bit_length() + 2)]
            for row, v in enumerate(values):
                exponent, zero, admissible = oracle(v, reserve)
                bits = [(exponent >> bit) & 1 for bit in range(width.bit_length())] + [zero, admissible]
                for bit, value in enumerate(bits):
                    if value:
                        expected[bit][row // 8] |= 1 << (row % 8)
            require(scan.evaluate(circuit, masks, size) == tuple(int.from_bytes(x, 'little') for x in expected), 'exhaustive scale mismatch')
            cases += size
            circuits += 1
    return {'assignments': cases, 'circuits': circuits}


def wide():
    rng = random.Random(20261016)
    checked = 0
    invoices = []
    for width in (9, 16, 65, 453, 1024, 4096):
        for reserve in sorted({0, width // 2, width - 1} | ({122} if width == 453 else set())):
            circuit = scan.compile_scan(width, 4, reserve)
            limit = 1 << (width - 1)
            fixtures = [(0, 0, 0, 0), (-limit, 0, 0, 0), (limit - 1, -1, 1, 0)]
            for bit in sorted({0, reserve, max(0, reserve - 1), width - 2}):
                power = 1 << bit
                if power < limit:
                    fixtures.extend([(-power, 0, 0, 0), (power - 1, -power, 0, 1)])
            fixtures.extend(tuple(rng.randrange(-limit, limit) for _ in range(4)) for _ in range(8))
            for values in fixtures:
                require(scan.run(circuit, values) == oracle(values, reserve), 'wide signed scan')
                checked += 1
            invoices.append({'width': width, 'reserve': reserve, 'components': 4,
                             'gates': len(circuit.gates), 'kinds': dict(sorted(Counter(g[0] for g in circuit.gates).items()))})
    require(all(scan.popcount_sum(n) == sum(i.bit_count() for i in range(n)) for n in range(1025)), 'popcount identity')
    return {'cases': checked, 'invoices': invoices}


def rounded(value, exponent):
    return round(Fraction(value, 1 << (exponent + 1))) * (1 << exponent)


def ideal_pair(values, sign, exponent):
    a, b, c, d = values
    return tuple(rounded(v, exponent) for v in (a+c-sign*(b-d), b+d+sign*(a-c),
                                               a+c+sign*(b-d), b+d-sign*(a-c)))


def line_oracle(values, sign, exponent, axes):
    result = list(values)
    for axis in axes:
        for i in range(len(result)):
            if not i & (1 << axis):
                j = i ^ (1 << axis)
                out = ideal_pair((*result[i], *result[j]), sign, exponent)
                result[i], result[j] = out[:2], out[2:]
    return result


def composition(pair):
    cases = 0
    rng = random.Random(2811)
    for width, dimension, axes in ((5, 2, (0,)), (7, 4, (0, 1)), (9, 8, (2, 0, 1))):
        circuit = scan.compile_scan(width, 2 * dimension, 1)
        for sign in (-1, 1):
            kernel = pair.compile_pair(width, sign)
            fixtures = [[(0, 0)] * dimension, [(2, 0)] + [(0, 0)] * (dimension-1),
                        [(-4, 1), (2, -3)] + [(0, 0)] * (dimension-2)]
            fixtures += [[(rng.randrange(-4, 5), rng.randrange(-4, 5)) for _ in range(dimension)] for _ in range(40)]
            for values in fixtures:
                flat = tuple(x for z in values for x in z)
                exponent, _, admissible = scan.run(circuit, flat)
                require(admissible == oracle(flat, 1)[2], 'composition validity')
                actual = list(values)
                # Keep the same entry scale through all tensor factors.
                for axis in axes:
                    for i in range(dimension):
                        if not i & (1 << axis):
                            j = i ^ (1 << axis)
                            out = pair.run(kernel, (*actual[i], *actual[j]), exponent)
                            actual[i], actual[j] = out[:2], out[2:]
                require(actual == line_oracle(values, sign, oracle(flat, 1)[0], axes), 'complete line composition')
                cases += 1
    block = [(8, 0), (0, 0), (3, 0), (0, 0)]
    expected = line_oracle(block, 1, oracle(tuple(x for z in block for x in z), 0)[0], (0,))
    local = []
    for i in (0, 2):
        values = (*block[i], *block[i+1])
        result = ideal_pair(values, 1, oracle(values, 0)[0])
        local += [result[:2], result[2:]]
    require(local != expected, 'local-scale negative control')
    return {'complete_lines': cases, 'pair_local_scale_rejected': True}


def controls():
    circuit = scan.compile_scan(4, 2, 1)
    fixtures = list(itertools.product(range(-8, 8), repeat=2))
    mutants = [replace(circuit, exponent=(0,) * len(circuit.exponent)),
               replace(circuit, zero=0), replace(circuit, admissible=1)]
    gates = list(circuit.gates)
    gates[2] = ('OR', gates[2][1], gates[2][2])
    mutants.append(replace(circuit, gates=tuple(gates)))
    # Replace the low-bit aggregate by the raw input signs.
    gates = list(circuit.gates)
    gates[24] = ('OR', 5, 9)
    mutants.append(replace(circuit, gates=tuple(gates)))
    for index, mutant in enumerate(mutants):
        require(any(scan.run(mutant, v) != oracle(v, 1) for v in fixtures), f'undetected mutation {index}')
    bad = [(0, 1, 0), (4, 0, 0), (4, 1, -1), (4, 1, 4), (True, 1, 0),
           (4, True, 0), (4, 1, False), (4097, 1, 0), (4096, 17, 0), (1, 1025, 0)]
    for args in bad:
        try:
            scan.compile_scan(*args)
        except ValueError:
            continue
        raise ValueError('invalid circuit admitted')
    for values in ((8, 0), (-9, 0), (True, 0), (0,)):
        try:
            scan.run(circuit, values)
        except ValueError:
            continue
        raise ValueError('invalid signed input admitted')
    return {'semantic_mutants': len(mutants), 'invalid_inputs': len(bad) + 4}


def receipt():
    pair = sources()
    exhaustive, wider = exhaust(), wide()
    composed, rejected = composition(pair), controls()
    width, reserve = 453, 122
    count = scan.popcount_sum(width - reserve)
    constant = 2 * width - 2 * reserve + count + 3
    require(pair.gate_count(width) == 124028, 'inherited pair invoice')
    return {'schema_version': 1, 'scope': 'local Boolean scale scan; no new kappa',
            'exhaustive': exhaustive, 'wide': wider, 'composition': composed, 'controls': rejected,
            'example': {'width': width, 'reserve': reserve, 'popcount_sum': count,
                        'scan_D_coefficient': 8 * width, 'scan_constant': constant,
                        'pair_gates': pair.gate_count(width),
                        'decoder_scan_ND_coefficient': 336 * 8 * width,
                        'decoder_scan_N_constant': 336 * constant,
                        'decoder_pairs_lambda_ND_coefficient': 168 * pair.gate_count(width)}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='create an absent receipt only')
    args = parser.parse_args()
    target = HERE / 'RESULT.json'
    if args.write:
        require(not target.exists(), 'refuse receipt overwrite')
    result = receipt()
    rendered = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.write:
        with target.open('x') as stream:
            stream.write(rendered)
    else:
        saved = strict_json(target)
        require(json.dumps(saved, sort_keys=True, indent=2) + '\n' == rendered, 'receipt mismatch')
    print(f"PASS_QQ16_BLOCK_SCALE_SCAN assignments={result['exhaustive']['assignments']} "
          f"scan=3624*D+{result['example']['scan_constant']} no_new_kappa")


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f'FAIL_QQ16_BLOCK_SCALE_SCAN: {error}') from error
