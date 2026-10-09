"""Whole-word point conjugation; the framework follows PR74/78/82.

All source triples, terminal descriptors, frames and scatter ports are mapped
together. The I+J basis and I-J/9 metric commute with the permutation.
Integration for this fixed witness: huxint with OpenAI Codex assistance.
"""
from itertools import combinations


def relabel(word, permutation):
    h, v = word['h'], word['v']
    assert sorted(permutation) == list(range(h))
    triples = list(combinations(range(h), 3))
    index = {t: i for i, t in enumerate(triples)}
    mapping = [index[tuple(sorted(permutation[x] for x in t))] for t in triples]
    def mask(value):
        return sum(1 << permutation[i] for i in range(h) if value >> i & 1)
    result = dict(word)
    result['frames'] = [[mask(c), mask(u)] for c, u in word['frames']]
    result['sources'] = {mapping[int(i)]: s for i, s in word['sources'].items()}
    result['scatter'] = [[v+mapping[a-v], b] for a, b in word['scatter']]
    result['outputs'] = [[s, g, permutation[c], sorted(permutation[x] for x in t)]
                         for s, g, c, t in word['outputs']]
    return result
