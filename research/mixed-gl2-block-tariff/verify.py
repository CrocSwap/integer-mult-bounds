#!/usr/bin/env python3
"""Check the mixed GL2-block tariff. Ali Romman with Codex assistance.

Apache-2.0. Formal diagonal words stay single group basis elements.
"""
from collections import deque
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import math
import sys

ELEMENTS = {'e': (1,2), 'a': (3,2), 'b': (1,3),
            'ab': (2,3), 'ba': (3,1), 's': (2,1)}
WORDS = {'e': (), 'a': ((0,1),), 'b': ((1,0),),
         'ab': ((1,0),(0,1)), 'ba': ((0,1),(1,0)),
         's': ((0,1),(1,0),(0,1))}
COSTS = {'e':0, 'a':1, 'b':1, 'ab':2, 'ba':2, 's':3}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tariffs():
    distance = {(1,2):0}
    queue = deque([(1,2)])
    while queue:
        state = queue.popleft()
        for i,j in ((0,1),(1,0)):
            nxt = list(state)
            nxt[i] ^= nxt[j]
            nxt = tuple(nxt)
            if nxt not in distance:
                distance[nxt] = distance[state]+1
                queue.append(nxt)
    require(set(distance) == set(ELEMENTS.values()), 'GL2 inventory differs')
    rows = {}
    for name, matrix in ELEMENTS.items():
        leave = 0
        for order in permutations((1,2,3)):
            positions = {q:i for i,q in enumerate(order)}
            leave += positions[1] < positions[2] and positions[matrix[0]] > positions[matrix[1]]
        require(leave == COSTS[name] == distance[matrix] == len(WORDS[name]), 'tariff differs')
        rows[name] = {'rows':matrix, 'leaving_orders':leave, 'orders':6, 'cost':COSTS[name]}
    return rows


def validate(labels, pairs, n, registers):
    require(type(n) is int and n >= 2 and type(registers) is int and registers >= max(1,len(labels)),
            'invalid dimension or register count')
    require(all(len(pair)==2 and all(type(i) is int and 0<=i<n for i in pair) for pair in pairs),
            'invalid coordinate pair')
    require(len({i for pair in pairs for i in pair}) == 2*len(pairs), 'coordinate pairs overlap')
    require(all(len(row)==len(pairs) and all(name in ELEMENTS for name in row) for row in labels),
            'invalid block labels')


def bill(labels, pairs, n, registers):
    validate(labels,pairs,n,registers)
    return sum(COSTS[name] for row in labels for name in row)


def program(labels, pairs):
    return [(r,pair[i],pair[j]) for r,row in enumerate(labels)
            for pair,name in zip(pairs,row) for i,j in WORDS[name]]


def execute(gates, n, registers, omit=None):
    state = [[1<<i for i in range(n)] for _ in range(registers)]
    for index,(r,i,j) in enumerate(gates):
        if index != omit:
            state[r][i] ^= state[r][j]
    return state


def target(labels, pairs, n, registers):
    state = [[1<<i for i in range(n)] for _ in range(registers)]
    for r,row in enumerate(labels):
        for (a,b),name in zip(pairs,row):
            x,y = ELEMENTS[name]
            state[r][a] = ((1<<a) if x&1 else 0) ^ ((1<<b) if x&2 else 0)
            state[r][b] = ((1<<a) if y&1 else 0) ^ ((1<<b) if y&2 else 0)
    return state


def ambient_paid_checks():
    cases = orders_checked = 0
    domains = ((2,((0,1),)),(3,((0,2),)),(4,((0,1),(2,3))), (5,((0,3),(1,4))))
    for n,pairs in domains:
        identity = [1<<i for i in range(n)]
        changed = identity[:]
        for i in range(n-1):
            changed[i] ^= changed[i+1]
        for basis in (identity,changed):
            for write in range(n):
                for read in range(n):
                    if write == read:
                        continue
                    fresh = basis[write]^basis[read]
                    require(fresh not in basis and fresh != 0, 'fresh vector is not distinct')
                    after = basis[:]
                    after[write] = fresh
                    counts = [0]*len(pairs)
                    for order in permutations((*basis,fresh)):
                        position = {q:i for i,q in enumerate(order)}
                        for k,(a,b) in enumerate(pairs):
                            counts[k] += (position[basis[a]] < position[basis[b]]
                                          and position[after[a]] > position[after[b]])
                        orders_checked += 1
                    unit = math.factorial(n+1)//6
                    expected = [unit if write in pair else 0 for pair in pairs]
                    require(counts == expected and sum(counts) <= unit, 'ambient paid capacity differs')
                    cases += 1
    return {'cases':cases, 'relative_orders':orders_checked}


def upper_words():
    cases = omissions = total_calls = 0

    def check(labels,pairs,n,registers):
        nonlocal cases,omissions,total_calls
        price = bill(labels,pairs,n,registers)
        word = program(labels,pairs)
        wanted = target(labels,pairs,n,registers)
        require(len(word) == price and execute(word,n,registers) == wanted, 'formal endpoint differs')
        for omit in range(len(word)):
            require(execute(word,n,registers,omit) != wanted, 'omitted call accepted')
            omissions += 1
        cases += 1
        total_calls += len(word)

    for values in product(ELEMENTS,repeat=3):
        labels = [[v] for v in values]
        for n in (2,3,5):
            for registers in (3,4,5):
                check(labels,[(0,n-1)],n,registers)
    for values in product(ELEMENTS,repeat=4):
        labels = [list(values[:2]),list(values[2:])]
        for n,pairs in ((4,[(0,1),(2,3)]),(5,[(0,3),(1,4)])):
            for registers in (2,3):
                check(labels,pairs,n,registers)
    require((cases,omissions,total_calls)==(7128,39852,39852), 'word coverage differs')
    return {'endpoints':cases, 'omissions':omissions, 'paid_calls':total_calls}


def controls():
    invalid = [([['s','s']],[(0,1),(1,2)],3,1), ([['s']],[(0,0)],2,1),
               ([['s']],[(0,2)],2,1), ([['s'],['a']],[(0,1)],2,1),
               ([['unknown']],[(0,1)],2,1), ([[]],[(0,1)],2,1)]
    for args in invalid:
        try:
            bill(*args)
        except ValueError:
            continue
        raise ValueError('invalid contract accepted')
    require(bill([],[(0,1)],2,1)==0, 'empty target bill')
    require(bill([['a'],['b'],['s']],[(0,1)],5,5)==5, 'heterogeneous target bill')
    # Three different overlapping pairs on one register can cancel.
    long = [(0,i,j) for a,b in ((0,1),(1,2),(0,2))
            for i,j in ((a,b),(b,a),(a,b))]
    short = [(0,1,2),(0,2,1),(0,1,2)]
    require(len(long)==9 and len(short)==3 and execute(long,3,1)==execute(short,3,1),
            'overlapping-block boundary differs')
    return len(invalid)+3


def evidence():
    here = Path(__file__).resolve().parent
    result = {'schema':'mixed-gl2-block-tariff/v1', 'tariffs':tariffs(),
              'ambient_paid':ambient_paid_checks(), 'formal_diagonal_words':upper_words(),
              'boundary_controls':controls(), 'no_new_kappa':True}
    result['source_sha256'] = {name:hashlib.sha256((here/name).read_bytes()).hexdigest()
                              for name in ('README.md','verify.py','TASK.json','VERIFY.json','SOURCES.json')}
    return result


def main():
    encoded = json.dumps(evidence(),sort_keys=True,indent=2)+'\n'
    if sys.argv[1:] == ['--emit-receipt']:
        print(encoded,end='')
    else:
        require(not sys.argv[1:], 'unexpected argument')
        require(Path(__file__).with_name('RESULT.json').read_text(encoding='utf-8')==encoded, 'receipt differs')
        print('PASS_MIXED_GL2_BLOCK_TARIFF costs=0,1,1,2,2,3 no_new_kappa')


if __name__=='__main__':
    main()
