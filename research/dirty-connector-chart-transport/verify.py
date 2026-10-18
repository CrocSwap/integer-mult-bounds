#!/usr/bin/env python3
"""Independent finite checks of the stated F2 chart-transport contract."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def apply(matrix, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(matrix))

def compose(left, right):
    return tuple(sum(((apply(left, apply(right, 1 << j)) >> i) & 1) << j
                     for j in range(3)) for i in range(3))

def kernel(matrix):
    return frozenset(x for x in range(8) if apply(matrix, x) == 0)

def gates(matrix, source, target):
    return [(source+j, target+i) for i, row in enumerate(matrix)
            for j in range(3) if (row >> j) & 1]

def run(word, value):
    for source, target in word:
        value ^= ((value >> source) & 1) << target
    return value

def desired(value, b0, b1):
    x = value & 7
    return value ^ (apply(b0, x) << 6) ^ (apply(b1, x) << 9)

def main():
    for source in json.loads((HERE/'SOURCES.json').read_text())['files']:
        require(hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()
                == source['sha256'], 'source hash mismatch: '+source['path'])
    matrices = list(itertools.product(range(8), repeat=3))
    invertibles = [m for m in matrices if len({apply(m,x) for x in range(8)}) == 8]
    require(len(invertibles) == 168, 'GL3 census')
    kernels = {m: kernel(m) for m in matrices}
    pairs = 0
    for b0 in matrices:
        orbit = {compose(r,b0) for r in invertibles}
        expected = {b1 for b1 in matrices if kernels[b1] == kernels[b0]}
        require(orbit == expected, 'kernel/orbit criterion')
        pairs += len(expected)
    require(pairs == 40916, 'kernel-equivalent pair count')
    require(kernels[(1,0,0)] != kernels[(2,0,0)], 'equal rank is insufficient')
    b0, b1, identity, r = (7,6,1), (1,6,1), (1,2,4), (3,2,4)
    require(compose(r,b0) == b1 and compose(r,r) == identity, 'pilot chart')
    a1, a2 = gates(identity,3,6), gates(identity,3,9)
    g0, g1, transport = gates(b0,0,3), gates(b1,0,3), [(4,3)]
    baseline = a1+g0+a1+g0+a2+g1+a2+g1
    candidate = a1+g0+a1+transport+a2+g1+a2+transport
    require(len(baseline)==32 and len(candidate)==24, 'paid gate counts')
    for value in range(1<<12):
        expected = desired(value,b0,b1)
        require(run(baseline,value)==expected, 'baseline map')
        require(run(candidate,value)==expected, 'candidate map')
        require(run(list(reversed(candidate)),expected)==value, 'literal inverse')
    mutants = {
        'omit_transport': a1+g0+a1+a2+g1+a2+transport,
        'omit_final_inverse': a1+g0+a1+transport+a2+g1+a2,
        'wrong_closing_map': a1+g0+a1+transport+a2+g0+a2+transport,
    }
    witnesses = {}
    for label, word in mutants.items():
        bad = next((v for v in range(1<<12) if run(word,v)!=desired(v,b0,b1)), None)
        require(bad is not None, 'surviving semantic mutant: '+label)
        witnesses[label] = {'input':bad,'actual':run(word,bad),'expected':desired(bad,b0,b1)}
    # Optional explicitly defined fixed-port tariff: home is one cell before bit0;
    # each scalar XOR pays round-trip movement plus five instruction/access units.
    cost = lambda word: sum(2*(max(s,t)+1)+5 for s,t in word)
    require(cost(candidate)<cost(baseline), 'fixed-port tariff saving')
    result = {'matrices':512,'invertible_charts':168,'ordered_pairs_checked':512**2,
              'admissible_pairs':pairs,'dirty_inputs':4096,
              'scalar_xors':{'baseline':len(baseline),'transport':len(candidate)},
              'fixed_port_tariff':{'baseline':cost(baseline),'transport':cost(candidate)},
              'negative_controls':witnesses}
    print(json.dumps(result,sort_keys=True))
    print('PASS_DIRTY_CONNECTOR_CHART_TRANSPORT')

if __name__ == '__main__':
    main()
