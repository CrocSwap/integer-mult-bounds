#!/usr/bin/env python3
"""Independent all-column XOR replay of the freshly emitted gen4 word.

Imports no contributor code. COPY is scalar-projected to its source; address
geometry and the physical copy implementation remain separately checked.
Douglas Colkitt, with OpenAI Codex assistance; Apache-2.0.
"""
from array import array
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

N, V = 19930, 1760


def read(path):
    result = array('i')
    result.frombytes(gzip.decompress(path.read_bytes()))
    assert result.itemsize == 4 and len(result) % 6 == 0
    return [tuple(result[i:i+6]) for i in range(0, len(result), 6)]


def projection(rows, filter_even=False):
    return [(op,a,b,c,z) for op,a,b,c,f,z in rows
            if op and (op != 1 or not filter_even or c%2)]


def scalar_events(rows):
    copy = None
    events = []
    for op,a,b,c,f,z in rows:
        if op == 2:
            assert copy is None and b == N
            copy = a
        elif op == 3:
            assert copy == a and b == N
            copy = None
        elif op == 1:
            assert c%2
            if b == N:
                assert copy is not None
                b = copy
            assert 0 <= a < N and 0 <= b < N and a != b
            events.append((a,b,c))
        else:
            assert op == 0
    assert copy is None
    return events


def execute(events, omit=None):
    values = [1 << i for i in range(N)]
    norms = [1]*N
    largest = 1
    for i,(a,b,c) in enumerate(events):
        if i == omit:
            continue
        values[a] ^= values[b]
        norms[a] += abs(c)*norms[b]
        largest = max(largest,norms[a])
    wanted = [1 << i for i in range(N)]
    for i in range(V):
        wanted[V+i] ^= 1 << i
    return values == wanted, largest


def main():
    root = Path(sys.argv[1])
    old = read(root/'producer-bit/records.bin.gz')
    new = read(root/'records.bin.gz')
    assert projection(old,True) == projection(new)
    events = scalar_events(new)
    assert len(events) == 626360
    assert Counter(abs(c) for a,b,c in events) == {1:624600,3:1760}
    assert execute(events) == (True,21725)
    assert execute([(a,b,-c) for a,b,c in reversed(events)]) == (True,1850360)
    assert not execute(events,omit=len(events)-1)[0]
    print(json.dumps(dict(status='PASS_INDEPENDENT_LITERAL_WORD_REPLAY',
        formal_columns=N, dirty_registers=N-2*V, forward_and_inverse=True,
        scalar_and_copy_projection_unchanged=True, emitted_additions=len(events),
        forward_prefix_l1=21725, inverse_prefix_l1=1850360,
        omitted_addition_rejected=True,
        emitted_records_sha256=hashlib.sha256(gzip.decompress((root/'records.bin.gz').read_bytes())).hexdigest(),
        scope='Scalar projection only; full rational geometry and finite transfer are separate obligations.'),indent=2))


if __name__ == '__main__':
    main()
