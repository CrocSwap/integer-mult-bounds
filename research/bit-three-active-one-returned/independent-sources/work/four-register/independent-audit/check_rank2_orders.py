"""Check all rank-two orders with dependence signatures and reversal orbits."""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import struct

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def words(counts):
    def fill(letter, available, word):
        if letter == len(counts):
            yield tuple(word)
            return
        for places in combinations(available, counts[letter]):
            next_word = word[:]
            for position in places:
                next_word[position] = letter
            yield from fill(letter + 1, tuple(i for i in available if i not in places), next_word)
    yield from fill(0, tuple(range(8)), [None] * 8)


def outer(x, y):
    return tuple(((x >> i) & 1) * ((y >> j) & 1) for i in range(4) for j in range(4))


def product(a, b):
    return tuple(sum(a[4*i+k] * b[4*k+j] for k in range(4)) % 2
                 for i in range(4) for j in range(4))


def main():
    source = json.loads((BASE / 'dirty_rank2.json').read_text())['families']
    independent = [json.loads(line) for line in (HERE / 'rank2-multisets.jsonl').read_text().splitlines()]
    expected = {(row['pool'], tuple(row['counts']), sum(1 << a for a in row['ancillas'])) for row in source}
    actual = {(row['class'], tuple(row['counts']), row['possible_ancilla']) for row in independent}
    assert len(expected) == len(source) == len(actual) == len(independent) == 103
    assert actual == expected
    pools = json.loads((BASE / 'independent/off-pattern-spaces.json').read_text())['levels'][1]['representatives']
    raw = traces = representatives = 0
    binary = bytearray()
    for family in source:
        ns = family['projectors']
        assert ns == pools[family['pool']]['projectors']
        matrices = [outer(*xy) for xy in ns]
        pairs = [(i,j) for i in range(len(ns)) for j in range(i+1,len(ns))
                 if product(matrices[i], matrices[j]) != product(matrices[j], matrices[i])]
        def signature(word):
            return tuple(bytes(x for x in word if x == i or x == j) for i,j in pairs)
        least = {}
        for word in words(family['counts']):
            raw += 1
            key = signature(word)
            if key not in least or word < least[key]:
                least[key] = word
        traces += len(least)
        retained = []
        for key, word in least.items():
            if word <= least[tuple(part[::-1] for part in key)]:
                retained.append(word)
        representatives += len(retained)
        role = sum(1 << a for a in family['ancillas'])
        for word in sorted(retained):
            packed = [sum(bit << i for i,bit in enumerate(matrices[j])) for j in word]
            binary += struct.pack('<9H', *packed, role)
    saved = (BASE / 'independent/rank2-words.bin').read_bytes()
    assert binary == saved
    result = dict(status='PASS_INDEPENDENT_RANK2_FRONT_END', families=len(source),
                  raw_orders=raw, commutation_orders=traces, reversal_orders=representatives,
                  binary_word_and_role_stream_identical=True,
                  binary_bytes=len(binary), binary_sha256=hashlib.sha256(binary).hexdigest())
    (HERE / 'RANK2-FRONT-END-RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
