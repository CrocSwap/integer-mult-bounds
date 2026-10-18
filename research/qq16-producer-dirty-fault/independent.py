#!/usr/bin/env python3
"""Reverse linear-functional check; imports no primary or predecessor code.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def address(token):
    kind, number = token
    check(kind in ('L', 'C') and type(number) is int, 'address kind')
    check(0 <= number < (704 if kind == 'L' else 8), 'address range')
    return number if kind == 'L' else number + 704


def pullback(gates, output):
    # A row covector is propagated backward; an ADD changes its source weight.
    row = [Fraction(0)] * 712
    row[output] = Fraction(1)
    for gate in reversed(gates):
        destination = address(gate[1])
        weight = row[destination]
        if not weight:
            continue
        if gate[0] == 'add':
            row[address(gate[2])] += weight * Fraction(gate[3], gate[4])
        elif gate[0] == 'scale':
            row[destination] *= Fraction(gate[2], gate[3])
        elif gate[0] == 'clear':
            row[destination] = Fraction(0)
        else:
            raise ValueError('unknown scalar instruction')
    return row


def verify(root):
    raw = (root / 'research/joint-query/certificate.json.gz').read_bytes()
    check(hashlib.sha256(raw).hexdigest() ==
          'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7',
          'certificate source hash')
    packet = json.loads(gzip.decompress(raw))
    # Construct the scalar chronology independently, locating the marked core
    # event before filtering. Do not trust the primary's flattened word.
    before, after, found = [], [], False
    for block in packet['programs']['F_0']:
        if block[0] == 'retained_core':
            check(block[1:3] == ['forward', 0], 'forward zero-stage')
            events = packet['core_words']['forward']
            for index, event in enumerate(events):
                if index == 24438:
                    check(event == ['scalar', ['add', ['L', 39], ['L', 359], 4, 1], 1],
                          'marked cancellation event')
                    found = True
                    continue
                if event[0] == 'scalar':
                    (after if found else before).append(event[1])
        elif block[0] in ('cover_sweep', 'private_sweep'):
            check(found, 'F0 wrappers follow core')
            for event in block[2]:
                if event[0] == 'scalar':
                    after.append(event[1])
                else:
                    check(event[0] == 'native_line', 'scalar-specialized wrapper line')
        else:
            raise ValueError('unexpected F0 block')
    check(found, 'fault found')
    target, source = pullback(before, 39), pullback(before, 359)
    check((target[359], source[359]) == (-4, 1), 'prefix dirty coefficients')
    check((target[112], source[112]) == (0, 0), 'prefix data coefficients')
    response = []
    for output in range(712):
        coefficient = pullback(after, output)[39]
        if coefficient:
            response.append([output, str(coefficient)])
    receipt = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    check(response == receipt['unit_fault_final_response'], 'all 712 adjoint responses')
    check(len(response) == 52 and all(i < 224 for i, _ in response), 'data-only response')
    check(all(abs(Fraction(value)) == Fraction(1, 2) for _, value in response),
          'unit response magnitude')
    print('PASS_QQ16_DIRTY_FAULT_ADJOINT: 712 reverse suffix functionals; two prefix rows')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    verify(args.root.resolve())


if __name__ == '__main__':
    main()
