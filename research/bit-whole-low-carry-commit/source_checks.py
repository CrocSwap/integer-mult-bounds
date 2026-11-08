# SPDX-License-Identifier: Apache-2.0
"""Bind the new stage to the exact addressed frame506 source convention.

The old schedule interpreter is an inherited operational-contract check, not
a physical implementation of its homogeneous or native instructions.
"""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import random

from compiler import column_specs, source_matrix
from source import require

FRAME_PATH = 'research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json'


def product(left, right, modulus=None):
    rows = [[sum(x*y for x, y in zip(row, column)) for column in zip(*right)]
            for row in left]
    return rows if modulus is None else [[x % modulus for x in row] for row in rows]


def residue(matrix, modulus):
    return [[Fraction(x).numerator*pow(Fraction(x).denominator, -1, modulus) % modulus
             for x in row] for row in matrix]


def source_binding(modules, raw):
    frame = json.loads(raw[FRAME_PATH])['frames']['506']
    fingerprint = hashlib.sha256(json.dumps(frame, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    require(fingerprint == '7462680ac7a7cbe7d098900c9b9d45e097db37c529c442ba2f88350e51ea8f67',
            'exact addressed source frame506')
    generator, interpreter = modules['route_generator'], modules['route_interpreter']
    column_receipts = []
    for inverse in (False, True):
        matrix = source_matrix(raw, inverse=inverse)
        specs, cells = column_specs(matrix)
        require(cells == 64 and len(specs) == 64, 'actual source has no padded payload or control digits')
        for column in range(8):
            weights = [int(4*matrix[row][column]) for row in range(8)]
            positive = sum(max(x, 0) for x in weights)
            negative = sum(max(-x, 0) for x in weights)
            require(positive <= (6 if inverse else 16) and negative <= 4,
                    'all-q actual source carry envelope')
            if not inverse:
                require(all(x % 4 == 0 for x in weights), 'integer forward source')
            tested = []
            for q in (3, 5, 7):
                totals = {0}
                for weight in weights:
                    totals = {old+weight*digit for old in totals for digit in range(q)}
                codes = sorted({(total-4*((total*pow(4, -1, q)) % q))//q for total in totals})
                require(all(-7 <= code <= 12 for code in codes), 'reachable source quarter-code domain')
                tested.append(dict(q=q, reachable_totals=len(totals), codes=codes))
            column_receipts.append(dict(inverse=inverse, column=column, weights=weights,
                                        positive=positive, negative=negative, tested=tested))

    route_receipts = []
    rng = random.Random(1204989)
    for lanes, q, w in ((1, 3, 2), (1, 5, 4), (2, 3, 2), (3, 5, 4)):
        source = generator.generate(frame, lanes, q, w)
        exported = json.loads(json.dumps(source.export()))
        n, modulus, Q = 8*lanes, q**w, q**(w-1)
        matrix, inverse_matrix = source_matrix(raw, lanes), source_matrix(raw, lanes, True)
        require(all(matrix[i][j] == (source.matcher[i//lanes][j//lanes]
                                    if i % lanes == j % lanes else 0)
                    for i in range(n) for j in range(n)), 'exact S8 tensor fixed-lane embedding')
        identity = tuple(tuple(Fraction(i == j) for j in range(n)) for i in range(n))
        require(tuple(map(tuple, product(matrix, inverse_matrix))) == identity,
                'source inverse including tensor-lane order')
        for direction in (1, -1):
            block = []
            active = False
            for step in exported['steps']:
                if step['op'] == 'route_enter' and step['direction'] == direction:
                    active = True
                elif active and step['op'] == 'route_return':
                    break
                elif active:
                    block.append(step)
            carry = [(j, step) for j, step in enumerate(block) if step['op'] == 'carry_shift']
            commit = [j for j, step in enumerate(block) if step['op'] == 'low_type_commit']
            clear = [j for j, step in enumerate(block) if step['op'] == 'cache_clear']
            require([tuple(step['addresses']) for _, step in carry] == [(i,) for i in range(n*n)],
                    'all original row-major carry occurrences')
            require(len(commit) == 1 and len(clear) == n*n and carry[-1][0] < commit[0] < clear[0],
                    'source whole carry/commit/cache order')
            require(all(step['direction'] == direction for _, step in carry), 'source carry orientation')

        low = [[int(i == j) for j in range(n)] for i in range(n)]
        for _ in range(3*n):
            i, j = rng.sample(range(n), 2)
            coefficient = rng.randrange(1, q)
            low[i] = [(x+coefficient*y) % q for x, y in zip(low[i], low[j])]
        high = [[rng.randrange(Q) for _ in range(n)] for _ in range(n)]
        combined = [[low[i][j]+q*high[i][j] for j in range(n)] for i in range(n)]
        flat = lambda rows: [x for row in rows for x in row]
        data = dict(low=flat(low), high=flat(high), h=[rng.randrange(modulus) for _ in range(n)],
                    d=[rng.randrange(modulus) for _ in range(n)], outer=[7, 2, 11], z=[9, 0, 4], tape_head=-13)
        state = dict(slots={'462': 2, '461': 9}, owners={'462': data, '461': deepcopy(data)})
        returned, receipt = interpreter.run(exported, state)
        forward = product(combined, residue(matrix, modulus), modulus)
        require(receipt['route_returns'] == [flat(forward), flat(combined)],
                'actual complete addressed source acts by right multiplication then its inverse')
        require(returned['owners']['461'] == state['owners']['461'], 'source complete spectator owner')
        for inverse in (False, True):
            selected = inverse_matrix if inverse else matrix
            matrix_mod = residue(selected, modulus)
            raw_low = product(low, matrix_mod)
            committed = [[x % q for x in row] for row in raw_low]
            carries = [[((x-y)//q) % Q for x, y in zip(row, out)]
                       for row, out in zip(raw_low, committed)]
            homogeneous = product(high, residue(selected, Q), Q)
            assembled = [[committed[i][j]+q*((homogeneous[i][j]+carries[i][j]) % Q)
                          for j in range(n)] for i in range(n)]
            require(assembled == product(combined, matrix_mod, modulus),
                    'whole-source homogeneous then B_M identity')
            for row in range(n):
                for column in range(n):
                    total = sum(4*selected[j][column]*low[row][j] for j in range(n))
                    require(total.denominator == 1, 'quarter numerator is integral')
                    low_digit = int(total)*pow(4, -1, q) % q
                    code = (int(total)-4*low_digit)//q
                    require(-7 <= code <= 12 and (code*pow(4, -1, Q)) % Q == carries[row][column],
                            'physical source quarter producer equals direct source carry')
        route_receipts.append(dict(lanes=lanes, n=n, q=q, w=w, Q=Q,
                                   source_steps=len(source.steps), carry_occurrences=2*n*n,
                                   source_route_sha256=hashlib.sha256(json.dumps(receipt['route_returns']).encode()).hexdigest()))

    require(source_matrix(raw) != tuple(zip(*source_matrix(raw))), 'source transpose mutant distinguishable')
    return dict(frame506_sha256=fingerprint, fixed_lane_route_checks=route_receipts,
                source_column_envelopes=column_receipts,
                scope='Source operational-contract binding only; no full GL8 payload execution')
