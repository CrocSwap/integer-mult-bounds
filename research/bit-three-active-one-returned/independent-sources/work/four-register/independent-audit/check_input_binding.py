"""Bind the scalar catalogue, multiset rows, word stream, and binary input."""
from pathlib import Path
import hashlib
import json
import struct

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE / 'independent'


def matrix(x, y):
    return sum(((x >> i) & 1) * ((y >> j) & 1) << (4 * i + j)
               for i in range(4) for j in range(4))


def main():
    pools = json.loads((ROOT / 'off-pattern-spaces.json').read_text())['levels'][2]['representatives']
    tokens = iter(map(int, (ROOT / 'rank3-pools.txt').read_text().split()))
    assert next(tokens) == len(pools)
    for pool in pools:
        expected = pool['projectors']
        assert next(tokens) == len(expected)
        space = pool['space']
        for i in range(8):
            for j in range(8):
                assert space[i] ^ space[j] == space[i ^ j]
        for x, y in expected:
            assert (next(tokens), next(tokens), next(tokens)) == \
                   (x, y, space.index(matrix(x, y) & 0x7bde))
    assert next(tokens, None) is None

    original = [json.loads(line) for line in (ROOT / 'rank3-multisets.jsonl').open()]
    independent = [json.loads(line) for line in Path(__file__).with_name('rank3-multisets.jsonl').open()]
    key = lambda row: (row['class'], tuple(row['counts']), row['possible_ancilla'])
    assert len(set(map(key, original))) == len(original)
    assert set(map(key, original)) == set(map(key, independent))
    tokens = iter(map(int, (ROOT / 'rank3-word-input.txt').read_text().split()))
    assert next(tokens) == len(original)
    for record in original:
        ns = pools[record['class']]['projectors']
        assert next(tokens) == len(ns)
        assert next(tokens) == record['possible_ancilla']
        for (x, y), count in zip(ns, record['counts']):
            assert (next(tokens), next(tokens), next(tokens)) == (x, y, count)
    assert next(tokens, None) is None

    records = 0
    sha = hashlib.sha256()
    with (ROOT / 'rank3-words.bin').open('rb') as binary:
        for line in (ROOT / 'rank3-parity-survivors.jsonl').open():
            row = json.loads(line)
            family = original[row['family']]
            ns = pools[family['class']]['projectors']
            order = row['order']
            assert len(order) == 8
            assert [order.count(i) for i in range(len(ns))] == family['counts']
            roles = row['ancilla_mask']
            assert roles and not (roles & ~family['possible_ancilla'])
            expected = struct.pack('<9H', *(matrix(*ns[i]) for i in order), roles)
            assert binary.read(18) == expected
            sha.update(expected)
            records += 1
        assert not binary.read(1)
    result = dict(status='PASS_CATALOGUE_MULTISET_WORD_BINARY_BINDING',
                  pool_classes=len(pools), multiset_rows=len(original),
                  independent_multiset_rows=len(independent), binary_records=records,
                  binary_bytes=18*records, binary_sha256=sha.hexdigest())
    Path(__file__).with_name('INPUT-BINDING-RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
