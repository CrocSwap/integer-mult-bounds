#!/usr/bin/env python3
"""Exact scalar relocation witnesses. Standard library; no predecessor imports."""
import argparse
from collections import deque
from hashlib import sha256
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = 'research/g20-isolated-exchange-floor/inputs/CONTROLLER.json'
SOURCE_HASH = '978536e852c0cfbc150f143e19d2cfddbb434bac6017d914974eb99f641593a8'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate(data):
    require(sha256(data).hexdigest() == SOURCE_HASH, 'source hash mismatch')
    return json.loads(data)['boundaries']


def matrix(word, n):
    rows = [1 << i for i in range(n)]
    for d, s in word:
        require(0 <= d < n and 0 <= s < n and d != s, 'invalid ADD')
        rows[d] ^= rows[s]
    return rows


def original_word(program):
    word = []
    for op, d, s in program:
        require(op in ('ADD', 'SWAP'), 'invalid source opcode')
        word.extend([(d, s)] if op == 'ADD' else [(d, s), (s, d), (d, s)])
    return word


def relocate(program, n):
    locations = list(range(n))
    word = []
    for op, d, s in program:
        if op == 'SWAP':
            locations[d], locations[s] = locations[s], locations[d]
        else:
            require(op == 'ADD', 'invalid source opcode')
            word.append((locations[d], locations[s]))
    return word, locations


def data_rows(word, n, locations):
    require(len(set(locations)) == len(locations), 'noninjective output locations')
    require(all(0 <= i < n for i in locations), 'output outside wire set')
    mask = (1 << len(locations)) - 1
    rows = matrix(word, n)
    return [rows[i] & mask for i in locations]


def nonunit_count(rows):
    return sum(r.bit_count() > 1 for r in rows)


def reject(call, reason):
    try:
        call()
    except ValueError as exc:
        require(str(exc) == reason, 'wrong rejection reason: ' + str(exc))
    else:
        raise ValueError('control accepted: ' + reason)


def check_endpoint(word, n, locations, expected):
    require(data_rows(word, n, locations) == expected, 'endpoint mismatch')


def quotient_census(n):
    # Row sorting represents free physical permutations. ADDs all have unit cost.
    start = tuple(1 << i for i in range(n))
    dist = {start: 0}
    queue = deque([start])
    while queue:
        rows = queue.popleft()
        require(nonunit_count(rows) <= dist[rows], 'quotient lower bound failed')
        for d in range(n):
            for s in range(n):
                if d == s:
                    continue
                nxt = list(rows)
                nxt[d] ^= nxt[s]
                nxt = tuple(sorted(nxt))
                if nxt not in dist:
                    dist[nxt] = dist[rows] + 1
                    queue.append(nxt)
    return len(dist)


def extra_wire_census():
    # Full exact GL(4,2) distances, with every ordered choice of two output wires.
    start = (1, 2, 4, 8)
    dist = {start: 0}
    queue = deque([start])
    checks = 0
    while queue:
        rows = queue.popleft()
        for out in itertools.permutations(range(4), 2):
            block = [rows[i] & 3 for i in out]
            # This includes singular blocks and arbitrary dependence on extra inputs.
            require(nonunit_count(block) <= dist[rows], 'extra-wire lower bound failed')
            checks += 1
        for d in range(4):
            for s in range(4):
                if d == s:
                    continue
                nxt = list(rows)
                nxt[d] ^= nxt[s]
                nxt = tuple(nxt)
                if nxt not in dist:
                    dist[nxt] = dist[rows] + 1
                    queue.append(nxt)
    require(len(dist) == 20160, 'incomplete GL4 census')
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    raw = (ROOT / SOURCE).read_bytes()
    source = authenticate(raw)
    reject(lambda: authenticate(raw + b' '), 'source hash mismatch')
    certificate = {'source_sha256': SOURCE_HASH, 'sides': {}}
    omissions = map_mutants = 0
    for side in ('left', 'right'):
        program = source[side + '_program']
        expected = source[side + '_rows']
        full = original_word(program)
        require(matrix(full, 32) == expected and len(full) == 38, 'source word mismatch')
        word, locations = relocate(program, 32)
        require(len(word) == nonunit_count(expected) == 14, 'sharpness mismatch')
        check_endpoint(word, 32, locations, expected)
        # Independent bitwise execution, including all independent dirty extras.
        for column in range(36):
            state = [int(i == column) for i in range(36)]
            for d, s in word:
                state[d] ^= state[s]
            require([state[i] for i in locations] == [(r >> column) & 1 for r in expected], 'column mismatch')
            require(state[32:] == [int(i == column) for i in range(32, 36)], 'dirty extra changed')
        for i in range(14):
            reject(lambda i=i: check_endpoint(word[:i] + word[i+1:], 32, locations, expected), 'endpoint mismatch')
            omissions += 1
        expected_locations = list(range(32))
        for a, b in ((14,31),(15,30),(16,28),(17,29),(18,26),(19,27),(20,24),(21,25)):
            expected_locations[a], expected_locations[b] = b, a
        require(locations == expected_locations, 'unexpected relocation')
        for i, p in enumerate(locations):
            if p != i:
                bad = locations.copy()
                bad[i], bad[p] = bad[p], bad[i]
                reject(lambda bad=bad: check_endpoint(word, 32, bad, expected), 'endpoint mismatch')
                map_mutants += 1
        # Dirty restored relay replaces a real gate; clean relay and garbage output.
        d, s = word[0]
        dirty = [(d,32),(32,s),(d,32),(32,s)] + word[1:]
        check_endpoint(dirty, 33, locations, expected)
        require(matrix(dirty, 33)[32] == 1 << 32, 'dirty relay not restored')
        clean = [(32,s),(d,32),(32,s)] + word[1:]
        check_endpoint(clean, 33, locations, expected)
        require(matrix(clean, 33)[32] == 1 << 32, 'clean relay not restored')
        # Clean relay requires extra initially zero; dirty relay works for every extra.
        require(any(matrix(clean,33)[i] >> 32 & 1 for i in locations), 'clean/dirty distinction lost')
        garbage = word + [(32, locations[0])]
        check_endpoint(garbage, 33, locations, expected)
        moved = locations.copy()
        p = moved[0]
        moved[0] = 32
        moved_word = word + [(p,32),(32,p),(p,32)]
        check_endpoint(moved_word, 33, moved, expected)
        # Repair the location permutation as an explicit separate 24-ADD word.
        repair = [(a,b) for op,a,b in program if op == 'SWAP']
        repair_word = [g for a,b in repair for g in ((a,b),(b,a),(a,b))]
        require(len(repair_word) == 24, 'repair count mismatch')
        require(matrix(repair_word,32) == [1 << i for i in locations], 'repair map mismatch')
        check_endpoint(word + repair_word, 32, list(range(32)), expected)
        # Parallel witness and matching 14p nonunit-row bound.
        for ports in (1,2,3,111):
            parallel = [(d+32*j,s+32*j) for j in range(ports) for d,s in word]
            rows = matrix(parallel, 32*ports)
            loc = [p+32*j for j in range(ports) for p in locations]
            want = [r << (32*j) for j in range(ports) for r in expected]
            require([rows[p] for p in loc] == want, 'parallel endpoint mismatch')
            require(nonunit_count(want) == len(parallel) == 14*ports, 'parallel floor mismatch')
        certificate['sides'][side] = {'ADDs': word, 'output_locations': locations,
                                     'minimum_ADDs': 14, 'separate_label_repair_ADDs': 24}
    # Complete bilinear matrix identity for every formal core matrix entry.
    # Scalar verification only: the conjugated core's physical cost is unknown.
    left = matrix(original_word(source['left_program']), 32)
    right = matrix(original_word(source['right_program']), 32)
    tail = [(d,s) for op,d,s in source['left_program'] if op == 'ADD']
    a = matrix(tail, 32)
    ainv = matrix(list(reversed(tail)), 32)
    perm = certificate['sides']['left']['output_locations']
    def compose(x, y):
        result = []
        for row in x:
            out = 0
            for j in range(32):
                if row >> j & 1:
                    out ^= y[j]
            result.append(out)
        return result
    require(compose(left,right) == [1 << i for i in range(32)], 'source inverse mismatch')
    for i in range(32):
        for j in range(32):
            core = [0]*32
            core[i] = 1 << j
            changed_core = [0]*32
            changed_core[perm[i]] = 1 << perm[j]
            require(compose(left,compose(core,right)) == compose(a,compose(changed_core,ainv)), 'changed-core identity mismatch')
    reject(lambda: data_rows([], 2, [0,0]), 'noninjective output locations')
    reject(lambda: data_rows([], 2, [0,2]), 'output outside wire set')
    reject(lambda: matrix([(0,0)], 2), 'invalid ADD')
    # Support count alone is a lower bound, not a universal sharp distance formula.
    require(nonunit_count([3,1]) == 1, 'support control')
    require(quotient_census(4) == 840, 'incomplete permutation quotient')
    checks = extra_wire_census()
    expected_cert = json.loads((PACKAGE / 'WITNESSES.json').read_text())
    require(json.loads(json.dumps(certificate)) == expected_cert, 'committed witness mismatch')
    packet = {'status':'PASS_G20_RELOCATED_OUTPUT_FLOOR', 'side_minimum':14,
              'separate_repair_minimum':24, 'quotient_states':840,
              'GL4_states':20160, 'extra_output_checks':checks, 'formal_core_entries':1024,
              'omission_rejections':omissions, 'map_mutant_rejections':map_mutants,
              'certificate_sha256':sha256(json.dumps(certificate,sort_keys=True).encode()).hexdigest()}
    if args.output:
        require(not args.output.resolve().is_relative_to(ROOT), 'output must be outside checkout')
        args.output.write_text(json.dumps(packet,sort_keys=True,indent=2)+'\n')
    print(json.dumps(packet, sort_keys=True))


if __name__ == '__main__':
    main()
