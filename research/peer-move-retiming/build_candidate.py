#!/usr/bin/env python3
"""Emit the two-operand public MOVE retiming of the pinned #7003 word."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json


SOURCE_SHA = 'd0de7804e56b2c8fe6db9d323560e53041810fd0377b91680cbed19b5176ebc0'
SOURCE_HEAD = 'ec30476096b2f9aed718152a2fa3712d1c4e884d'
PEER, FIRST, ADD, LAST = 29706, 30463, 33688, 33689
EDITS = {
    PEER: ['MOVE', 972, 3, 105, False],
    FIRST: ['MOVE', 1317, 3, 105, False],
    ADD: ['ADD', 1317, 972, '1', 105],
    LAST: ['MOVE', 1317, 105, 1048, False],
}


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def canonical(word):
    return json.dumps(word, sort_keys=True, separators=(',', ':')).encode()


def roles(event):
    return set(event[1:3] if event[0] in ('ADD', 'COPY') else event[1:2])


def edit(source):
    require(sha256(canonical(source)).hexdigest() == SOURCE_SHA, 'Pinned #7003 word')
    program = source['program']
    require(all(program[i] == event for i, event in EDITS.items()), 'Literal events at their bound source indices')
    require(all(972 not in roles(e) for e in program[PEER+1:FIRST]), 'No peer contact while delaying its MOVE')
    require([i for i in range(FIRST+1, LAST) if 1317 in roles(program[i])] == [ADD], 'Every stop contact moved')
    a, b, c = (source['frames'][i] for i in (3, 105, 1048))
    def span(basis):
        space = {0}
        for v in basis:
            require(v not in space and 0 < v < 512, 'Valid binary basis')
            space.update(x ^ v for x in tuple(space))
        return space
    require(span(a) < span(b) < span(c), 'Fused MOVE has strictly nested spans')
    fused = ['MOVE', 1317, 3, 1048, False]
    moved_add = ['ADD', 1317, 972, '1', 3]
    tagged = []
    for i, event in enumerate(program):
        if i == FIRST:
            tagged.extend(((ADD, moved_add), (PEER, program[PEER]), (FIRST, fused)))
        elif i not in (PEER, ADD, LAST):
            tagged.append((i, event))
    locations = {i: p for p, (i, _) in enumerate(tagged)}
    require(len(locations) == len(tagged) == len(program)-1, 'Only one MOVE is removed')
    overlapping = []
    for i, _ in tagged:
        if i != ADD and (i < ADD) != (locations[i] < locations[ADD]) and roles(program[i]) & roles(program[ADD]):
            other = program[i]
            if other[0] != 'MOVE':
                require(other[0] == 'ADD' and moved_add[2] != other[1] and other[2] != moved_add[1],
                        ('Noncommuting source change', i, other))
                overlapping.append(i)
    require(overlapping == [33687], 'Exactly one shared-source scalar crossing')
    candidate = source | {'program': [event for _, event in tagged]}
    return candidate, tagged, {ADD, *overlapping}


def histogram(word):
    frames = word['frames']
    return Counter(abs(len(frames[e[3]])-len(frames[e[2]])) for e in word['program'] if e[0] == 'MOVE')


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('candidate', type=Path)
    args = parser.parse_args()
    source = json.loads(gzip.decompress(args.source.read_bytes()))
    candidate, _, checked = edit(source)
    delta = histogram(candidate)
    delta.subtract(histogram(source))
    delta = {r: n for r, n in sorted(delta.items()) if n}
    require(delta == {1: -1, 4: -1, 5: 1}, 'Expected complete local paid delta')
    raw = canonical(candidate)
    args.candidate.write_bytes(gzip.compress(raw, mtime=0))
    print(json.dumps({'source_head': SOURCE_HEAD, 'source_canonical_sha256': SOURCE_SHA,
                      'candidate_canonical_sha256': sha256(raw).hexdigest(),
                      'candidate_gzip_sha256': sha256(args.candidate.read_bytes()).hexdigest(),
                      'changed_scalar_source_versions': sorted(checked),
                      'local_paid_delta': delta, 'complete_paid_delta': {r: 18*n for r,n in delta.items()}},
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
