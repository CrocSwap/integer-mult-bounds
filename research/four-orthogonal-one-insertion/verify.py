#!/usr/bin/env python3
"""Certify the four-row orthogonal Boolean single-insertion tariff.

Produced by Nick Petalas. Apache-2.0.
"""

from array import array
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


SIZE = 1 << 16
VALID_STATES = 15**4
UNSEEN = 255


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def distances() -> tuple[bytearray, dict[str, object]]:
    """Rows are four nibbles; a gate toggles a subset of its donor nibble."""
    labels = bytearray([UNSEEN]) * SIZE
    queue = array('I', [0]) * VALID_STATES
    queue[0] = 15
    labels[15] = 0
    tail = 1
    edges = 0
    subsets = tuple(tuple(k for k in range(1, 16) if k & ~v == 0)
                    for v in range(16))
    for head in range(VALID_STATES):
        if head == tail:
            break
        state = queue[head]
        depth = labels[state]
        for donor in range(4):
            value = state >> (4 * donor) & 15
            for change in subsets[value]:
                for destination in range(4):
                    if destination == donor:
                        continue
                    edges += 1
                    following = state ^ (change << (4 * destination))
                    if labels[following] != UNSEEN:
                        continue
                    require(tail < VALID_STATES, 'BFS capacity exceeded')
                    labels[following] = depth + 1
                    queue[tail] = following
                    tail += 1
    require(tail == VALID_STATES, 'incomplete reachable graph')
    counts = Counter(v for v in labels if v != UNSEEN)
    return labels, {'states': tail, 'effective_edges': edges,
                    'layers': dict(sorted(counts.items()))}


def transpose(code: int) -> int:
    result = 0
    for row in range(4):
        for column in range(4):
            result |= ((code >> (4 * row + column)) & 1) << (4 * column + row)
    return result


def check_potential(labels: bytearray) -> dict[str, int]:
    """Check all coefficients using four independent binary component columns."""
    potential = bytearray([UNSEEN]) * SIZE
    valid = 0
    for code in range(SIZE):
        columns = tuple((code >> (4 * atom)) & 15 for atom in range(4))
        value = labels[transpose(code)]
        require((value != UNSEEN) == all(columns), 'wrong state domain')
        require(transpose(transpose(code)) == code, 'invalid coordinate conversion')
        potential[code] = value
        valid += int(all(columns))
    require(valid == VALID_STATES, 'wrong vertex count')
    toggles = tuple(tuple(sum(((pattern >> atom) & 1) << (4 * atom + row)
                              for atom in range(4)) for pattern in range(16))
                    for row in range(4))
    checked = 0
    for code in range(SIZE):
        value = potential[code]
        if value == UNSEEN:
            continue
        for donor in range(4):
            active = sum(((code >> (4 * atom + donor)) & 1) << atom
                         for atom in range(4))
            for destination in range(4):
                if donor == destination:
                    continue
                for coefficient in range(16):
                    following = code ^ toggles[destination][active & coefficient]
                    other = potential[following]
                    require(other != UNSEEN, 'gate left primitive-column domain')
                    require(abs(value - other) <= 1, 'invalid edge potential')
                    checked += 1
    require(potential[0x1111] == 0, 'wrong start potential')
    require(potential[0x8421] == 6, 'wrong target potential')
    return {'bellman_edges_with_noops': checked, 'target_distance': 6}


def column_word(root: int) -> list[tuple[int, int, int]]:
    require(0 <= root < 4, 'root outside four rows')
    others = [j for j in range(4) if j != root]
    return ([(j, root, 1 << j) for j in others]
            + [(root, j, 1 << j) for j in others])


def full_word(root: int) -> list[tuple[int, int, int]]:
    suffix = column_word(root)
    return list(reversed(suffix)) + [(root, -1, 15)] + suffix


def formal_endpoint(word: list[tuple[int, int, int]]) -> list[list[int]]:
    """Five atoms include the unused complement; column four is the source."""
    rows = [[31 * int(i == j) for j in range(4)] + [0] for i in range(4)]
    for destination, donor, coefficient in word:
        require(0 <= destination < 4 and 0 < coefficient < 32, 'invalid gate')
        if donor == -1:
            rows[destination][4] ^= coefficient
        else:
            require(0 <= donor < 4 and donor != destination, 'invalid ADD')
            rows[destination] = [a ^ (coefficient & b)
                                 for a, b in zip(rows[destination], rows[donor], strict=True)]
    return rows


def is_target(rows: list[list[int]]) -> bool:
    return rows == [[31 * int(i == j) for j in range(4)] + [1 << i]
                    for i in range(4)]


def literal_checks(word: list[tuple[int, int, int]]) -> int:
    """An independent bit interpreter covers every input on each atom."""
    count = 0
    for atom in range(5):
        for bits in range(32):
            data = [(bits >> j) & 1 for j in range(5)]
            original = data[:]
            for destination, donor, coefficient in word:
                factor = (coefficient >> atom) & 1
                source = data[4] if donor == -1 else data[donor]
                data[destination] = (data[destination] + factor * source) % 2
            wanted = original[:]
            if atom < 4:
                wanted[atom] ^= original[4]
            require(data == wanted, 'literal dirty endpoint mismatch')
            count += 1
    return count


def check_attainers(labels: bytearray) -> dict[str, int]:
    literal = 0
    omitted = 0
    for root in range(4):
        start = tuple(15 if row == root else 0 for row in range(4))
        state = list(start)
        for destination, donor, coefficient in column_word(root):
            state[destination] ^= state[donor] & coefficient
        require(state == [1, 2, 4, 8], 'six-ADD column attainer failed')
        require(labels[15] == 0 and labels[0x8421] == 6, 'wrong BFS endpoints')
        word = full_word(root)
        require(len(word) == 13, 'wrong complete word length')
        require(is_target(formal_endpoint(word)), 'formal dirty restoration failed')
        require(is_target(formal_endpoint(list(reversed(word)))), 'inverse failed')
        literal += literal_checks(word) + literal_checks(list(reversed(word)))
        for position in range(len(word)):
            mutant = word[:position] + word[position + 1:]
            require(not is_target(formal_endpoint(mutant)), 'omitted call accepted')
            omitted += 1
        without_prefix = word[6:]
        rows = formal_endpoint(without_prefix)
        require([row[4] for row in rows] == [1, 2, 4, 8], 'source control failed')
        require(not is_target(rows), 'unrestored dirt accepted')
        wrong_generator = word[:]
        wrong_generator[6] = (root, -1, 31)
        require(not is_target(formal_endpoint(wrong_generator)), 'complement leak accepted')
    return {'roots': 4, 'literal_atom_inputs': literal, 'omission_controls': omitted,
            'dirty_controls': 4, 'complement_controls': 4}


def corruption_controls(labels: bytearray) -> int:
    for index, value, message in ((0x8421, 7, 'invalid edge potential'),
                                  (0, 0, 'wrong state domain')):
        corrupted = labels[:]
        corrupted[index] = value
        try:
            check_potential(corrupted)
        except ValueError as error:
            require(str(error) == message, 'unexpected certificate failure')
        else:
            raise ValueError('corrupted certificate accepted')
    try:
        column_word(4)
    except ValueError as error:
        require(str(error) == 'root outside four rows', 'unexpected boundary failure')
    else:
        raise ValueError('invalid root accepted')
    return 3


def main() -> None:
    output = None
    if len(sys.argv) == 3 and sys.argv[1] == '--write-distances':
        output = Path(sys.argv[2]).resolve()
        repository = Path(__file__).resolve().parents[2]
        require(not output.is_relative_to(repository), 'export must be outside checkout')
    else:
        require(len(sys.argv) == 1, 'usage: verify.py [--write-distances PATH]')
    labels, graph = distances()
    proof = check_potential(labels)
    attainers = check_attainers(labels)
    controls = corruption_controls(labels)
    package = Path(__file__).resolve().parent
    paths = ('README.md', 'PROOF.md', 'SOURCES.json', 'TASK.json', 'VERIFY.json', 'verify.py')
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in paths}
    receipt = {'status': 'PASS_FOUR_ORTHOGONAL_ONE_INSERTION', 'graph': graph,
               'certificate': proof, 'attainers': attainers, 'other_controls': controls,
               'distance_sha256': hashlib.sha256(labels).hexdigest(), 'sources_sha256': hashes}
    if output is not None:
        with output.open('xb') as stream:
            require(stream.write(labels) == SIZE, 'incomplete certificate export')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
