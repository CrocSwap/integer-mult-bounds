#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Matched exact-integer timing of the scalar projection; recursion is excluded.

conorholds, with substantial OpenAI Codex assistance.
Optional copy/unit lowering credits Sagar Thakrar, PR696.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import platform
import random
import statistics
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from network import construct, load, require, sha, splice, strict_json
from cleanup import construct_cleanup, json_bytes


def compile_projection(events, word, copy_unit):
    n = 2*word['v']+word['R']; work = n+len(word['centers']); instructions = []
    def reg(value):
        require(value[0] in ('L', 'C'), 'benchmark register kind')
        return value[1] if value[0] == 'L' else n+value[1]
    # clear, copy, add, subtract, double, halve, negate; one real component.
    for event in events:
        if event[0] != 'scalar':
            require(event[0] in ('phase', 'adapter', 'residual_adapter', 'climb', 'center'), 'benchmark event kind')
            continue
        e = event[1]; target = reg(e[1])
        if e[0] == 'clear':
            instructions.append((0, target, 0))
        elif e[0] == 'copy':
            instructions.append((1, target, reg(e[2])))
        elif e[0] == 'scale':
            q = Q(e[2], e[3]); a, b = abs(q.numerator), q.denominator
            require(a and a & (a-1) == 0 and b & (b-1) == 0, 'benchmark scale')
            exponent = a.bit_length()-b.bit_length()
            instructions.extend([(4 if exponent > 0 else 5, target, 0)]*abs(exponent))
            if q < 0:
                instructions.append((6, target, 0))
        else:
            require(e[0] == 'add', 'benchmark scalar opcode')
            source = reg(e[2]); q = Q(e[3], e[4]); bits = bin(abs(q.numerator))[2:]
            require(q and q.denominator & (q.denominator-1) == 0, 'benchmark dyadic coefficient')
            if copy_unit and abs(q) == 1:
                instructions.extend([(2 if q > 0 else 3, target, source), (0, work, 0)])
                continue
            instructions.append((1, work, source) if copy_unit else (0, work, 0))
            for i, bit in enumerate(bits):
                if i:
                    instructions.append((4, work, 0))
                if bit == '1' and not (copy_unit and i == 0):
                    instructions.append((2, work, source))
            instructions.extend([(5, work, 0)]*(q.denominator.bit_length()-1))
            instructions.extend([(2 if q > 0 else 3, target, work), (0, work, 0)])
    return instructions


def execute(instructions, incoming):
    values = incoming.copy()
    for op, target, source in instructions:
        if op == 0:
            values[target] = 0
        elif op == 1:
            values[target] = values[source]
        elif op == 2:
            values[target] += values[source]
        elif op == 3:
            values[target] -= values[source]
        elif op == 4:
            values[target] *= 2
        elif op == 5:
            require(values[target] & 1 == 0, 'benchmark inexact integer halving')
            values[target] >>= 1
        else:
            require(op == 6, 'benchmark primitive opcode'); values[target] = -values[target]
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=11)
    parser.add_argument('--repetitions', type=int, default=5)
    parser.add_argument('--bits', type=int, default=1024)
    parser.add_argument('--out', type=Path, help='fresh timing receipt')
    args = parser.parse_args()
    require(3 <= args.rounds <= 31 and 1 <= args.repetitions <= 30 and 64 <= args.bits <= 8192, 'benchmark bounds')
    word, recipe, baseline, _, _ = load(); compensation, _, _, _ = construct(word, recipe)
    cleanup, _ = construct_cleanup(word); candidate = splice(word, baseline, compensation, cleanup)
    certificate = strict_json((HERE / 'CERTIFICATE.json').read_bytes())
    independent = strict_json((HERE / 'INDEPENDENT.json').read_bytes())
    n = 2*word['v']+word['R']; size = n+len(word['centers'])+1; rng = random.Random(624)
    incoming = [((-1 if rng.randrange(2) else 1)*rng.getrandbits(args.bits)) << 192 for _ in range(size)]
    receipts = {}
    for orientation in ('forward', 'backward'):
        require(sha(json_bytes(candidate[orientation])) == certificate['native']['orientations'][orientation]['program_sha256'],
                'benchmark complete literal stream binding')
        expected = incoming.copy()
        for i in range(word['v']):
            if orientation == 'forward':
                expected[word['v']+i] += incoming[i]
            else:
                expected[i] -= incoming[word['v']+i]
        expected[n:] = [0]*(size-n)
        for model in ('native_horner', 'copy_unit'):
            suffix = '' if model == 'native_horner' else '_copy_unit'
            programs = {}
            for name, events in [('baseline', baseline[orientation]), ('candidate', candidate[orientation])]:
                instructions = compile_projection(events, word, model == 'copy_unit')
                require(2*len(instructions) == independent['programs'][name+suffix+'_'+orientation]['real_primitives'],
                        'benchmark literal primitive charge')
                require(execute(instructions, incoming) == expected, 'benchmark arbitrary-dirt/private endpoint')
                programs[name] = instructions
            elapsed = {'baseline': [], 'candidate': []}
            for round_index in range(args.rounds):
                order = ('baseline', 'candidate') if round_index % 2 == 0 else ('candidate', 'baseline')
                for name in order:
                    start = time.perf_counter_ns()
                    for _ in range(args.repetitions):
                        require(execute(programs[name], incoming) == expected, 'timed endpoint mismatch')
                    elapsed[name].append((time.perf_counter_ns()-start)/1e9/args.repetitions)
            medians = {name: statistics.median(samples) for name, samples in elapsed.items()}
            receipts[orientation+'_'+model] = dict(samples_seconds=elapsed, medians_seconds=medians,
                                                  median_speedup=medians['baseline']/medians['candidate'],
                                                  one_component_primitives={name: len(p) for name, p in programs.items()})
            print('PASS_SCALAR_PROJECTION_BENCHMARK', orientation, model,
                  'median_speedup', receipts[orientation+'_'+model]['median_speedup'], flush=True)
    result = dict(status='PASS_MATCHED_SCALAR_PROJECTION_BENCHMARK', python=sys.version,
                  platform=platform.platform(), processor=platform.machine(), bits=args.bits,
                  fractional_guard_bits=192, rounds=args.rounds, repetitions=args.repetitions,
                  timed_scope='Exact one-real-component scalar primitive projection only; frame operators, recursive children, compiler and integer multiplication excluded.',
                  alternating_order=True, endpoint_checked_every_run=True,
                  benchmark_source_sha256=sha(Path(__file__).read_bytes()),
                  candidate_word_payload_sha256=certificate['native']['candidate_word_payload_sha256'],
                  results=receipts)
    if args.out:
        with args.out.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
