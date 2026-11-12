#!/usr/bin/env python3
"""Root review by literal words and a separately materialized owner graph.

Written without using the predecessor oracle or the codec's interval formula.
Apache-2.0; prepared for CubeJerry with substantial OpenAI assistance.
"""
import hashlib
import itertools
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
raw = (HERE / 'codec.py').read_bytes()
C = types.ModuleType('root_review_codec')
sys.modules[C.__name__] = C
exec(compile(raw, str(HERE / 'codec.py'), 'exec'), C.__dict__)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    rule = C.Rule((('a', 3), ('b', 3), ('c', 5)),
                  ((1, 'a'), (2, 'bank'), (2, 'b')))
    names = tuple(name for name, _ in rule.roles)
    types_ = (3, 5)
    type_index = {'a': 0, 'b': 0, 'c': 1}
    role_index = {'a': 0, 'b': 1, 'c': 0}

    def order(word):
        if not word:
            return ()
        return (type_index[word[-1]], order(word[:-1]), role_index[word[-1]])

    def words(point):
        return sorted((word for word in itertools.product(names, repeat=sum(point))
                       if tuple(sum(type_index[x] == i for x in word)
                                for i in range(2)) == point), key=order)

    word_cases = 0
    for degree in range(1, 7):
        for first in range(degree + 1):
            point = (first, degree-first)
            literal = words(point)
            need(len(literal) == C.multiplicity(rule, point), 'literal word count')
            for index, word in enumerate(literal):
                child, ordinal, role = C.decode(rule, point, index)
                need(words(child)[ordinal] + (role,) == word, 'literal decode')
                need(C.encode(rule, point, ordinal, role) == index, 'literal encode')
                word_cases += 1

    owner_cases = 0
    for rank in (5, 15, 24, 45, 80):
        flow, owners = C.FlowCodec(rule, rank), {}
        for depth in range(flow.height + 1):
            for path in itertools.product(range(3), repeat=depth):
                dilation = 1
                for site in path:
                    dilation *= rule.rounds[site][0]
                degree = flow.height-depth
                class_fields = []
                for first in range(degree + 1):
                    point = (first, degree-first)
                    if 5*dilation*3**point[0]*5**point[1] > rank:
                        continue
                    for ordinal, word in enumerate(words(point)):
                        unit = C.Unit(path, point, ordinal)
                        for role in names:
                            parent = tuple(point[i] + (i == type_index[role]) for i in range(2))
                            parent_scale = dilation//rule.rounds[path[-1]][0] if path else None
                            if not path or 5*parent_scale*3**parent[0]*5**parent[1] > rank:
                                expected = ('flow', 0, 'source', path, point, ordinal, role)
                            else:
                                parent_ordinal = words(parent).index(word + (role,))
                                owner = rule.rounds[path[-1]][1]
                                expected = (('flow', 0, 'owned', path[:-1], parent,
                                             parent_ordinal, owner) if owner == 'bank' else
                                            owners[(path[:-1], parent, parent_ordinal, owner)])
                            need(flow.owner(unit, role) == expected, 'literal owner graph')
                            owners[(path, point, ordinal, role)] = expected
                            class_fields.append(expected)
                            owner_cases += 1
                need(len(class_fields) == len(set(class_fields)), 'class owner alias')
    print(json.dumps({'status': 'PASS_INDEPENDENT_PASCAL_REVIEW',
                      'word_cases': word_cases, 'owner_cases': owner_cases,
                      'codec_sha256': hashlib.sha256(raw).hexdigest()}, sort_keys=True))


if __name__ == '__main__':
    main()
