"""Exact generalized support of the selected owned summary code."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path
import sys

PIN = "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78"


def read_rows(path):
    compressed = path.read_bytes()
    assert sha256(compressed).hexdigest() == PIN
    word = json.loads(gzip.decompress(compressed))
    state = {i: (1 << i if i < 111 else 0) for i in range(word["public"])}
    summaries = {}
    for opcode, role, *operands in word["program"]:
        if opcode == "ADD":
            state[role] ^= state[operands[0]]
        elif opcode == "SWAP":
            other = operands[0]
            state[role], state[other] = state[other], state[role]
        elif opcode == "INIT":
            assert role not in state
            state[role] = 0
        elif opcode == "CLEAR":
            del state[role]
        else:
            assert opcode == "MOVE"
            source, dest = operands
            if role >= word["public"]:
                assert dest == 0 and word["frames"][str(source)]["dim"] == 7
                assert role not in summaries
                summaries[role] = state[role]
    assert set(summaries) == set(range(770, 779))
    return [summaries[i] for i in range(770, 779)]


def codewords(rows):
    words = [0]
    for row in rows:
        words += [word ^ row for word in words]
    return words


def audit(path):
    rows = read_rows(path)
    words = codewords(rows)
    assert len(set(words)) == 512
    assert len(set(codewords([rows[1], *rows[1:]]))) == 256
    d1 = min(word.bit_count() for word in words[1:])
    assert d1 == 48
    pairs = Counter()
    for a, b in combinations(words[1:], 2):
        pairs[(a | b).bit_count()] += 1
    assert pairs.total() == 130305
    d2 = min(pairs)
    assert pairs[d2] % 3 == 0
    columns = Counter(sum(((row >> i) & 1) << r for r, row in enumerate(rows))
                      for i in range(111))
    return dict(status="PASS_GENERALIZED_SUMMARY_SUPPORT", word_sha256=PIN,
                d1=d1, d2=d2, enumerated_pairs=pairs.total(),
                minimizing_subspaces=pairs[d2] // 3, union_weight_histogram=pairs,
                zero_columns=columns[0], distinct_columns=len(columns),
                maximum_column_multiplicity=max(columns.values()))


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Use assertions")
    print(json.dumps(audit(Path(sys.argv[1])), sort_keys=True, indent=2))
