"""Small certificate checker: no optimizer, graph solver or predecessor import.

Proves a concrete optimum from restored-XOR semantics, cut-price feasibility,
and equality. The all-word cut inequality is justified in PROOF.md.
"""
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rational(text):
    need(type(text) is str, 'canonical rational string')
    value = Fraction(text)
    need(str(value) == text, 'canonical rational string')
    return value


def check(mu, add, certificate):
    n = len(mu)
    need(n >= 1 and len(add) == n and all(len(row) == n for row in add), 'tariff shape')
    need(all(type(v) in (int,Fraction) and v > 0 for v in mu), 'positive exact tariff')
    need(all(add[i][i] is None for i in range(n)), 'no self ADD tariff')
    need(all(type(add[i][j]) in (int,Fraction) and add[i][j] > 0
             for i in range(n) for j in range(n) if i != j), 'positive exact tariff')
    need(set(certificate) == {'schema_version','q','parents','cuts','cost','word'}, 'certificate fields')
    need(type(certificate['schema_version']) is int and certificate['schema_version'] == 1,
         'schema version')
    need(type(certificate['q']) is int and certificate['q'] == n, 'row count')
    parents = certificate['parents']
    need(type(parents) is list and len(parents) == n, 'parent list')
    need(all(j is None or (type(j) is int and 0 <= j < n and j != i)
             for i,j in enumerate(parents)), 'parent domain')
    for i in range(n):
        seen, j = set(), i
        while j is not None:
            need(j not in seen, 'parent cycle')
            seen.add(j)
            j = parents[j]
    cut_masks, weights = [], []
    need(type(certificate['cuts']) is list, 'cut list')
    for cut in certificate['cuts']:
        need(type(cut) is dict and set(cut) == {'rows','price'}, 'cut fields')
        rows = cut['rows']
        need(type(rows) is list and rows and all(type(i) is int and 0 <= i < n for i in rows)
             and rows == sorted(set(rows)), 'cut rows')
        mask = sum(1 << i for i in rows)
        need(mask not in cut_masks, 'duplicate cut')
        value = rational(cut['price'])
        need(value > 0, 'positive cut price')
        cut_masks.append(mask)
        weights.append(value)
    for i in range(n):
        root_load = sum(w for s,w in zip(cut_masks,weights) if s & (1 << i))
        need(root_load <= mu[i], 'root dual capacity')
        for j in range(n):
            if i != j:
                load = sum(w for s,w in zip(cut_masks,weights)
                           if s & (1 << i) and not s & (1 << j))
                need(load <= 2*add[i][j], 'ADD dual capacity')
    # Actual emitted gates, not the parent vector, establish the upper bound.
    state = [1 << i for i in range(n)]
    common = 1 << n
    bill = Fraction(0)
    word = certificate['word']
    need(type(word) is list and word, 'nonempty word')
    for gate in word:
        need(type(gate) is list and gate and gate[0] in ('P','ADD'), 'gate opcode')
        need(len(gate) == (2 if gate[0] == 'P' else 3) and
             all(type(i) is int and 0 <= i < n for i in gate[1:]), 'gate operands')
        i = gate[1]
        if gate[0] == 'P':
            state[i] ^= common
            bill += mu[i]
        else:
            j = gate[2]
            need(i != j, 'self ADD')
            state[i] ^= state[j]
            bill += add[i][j]
    need(state == [(1 << i) ^ common for i in range(n)], 'arbitrary-dirt endpoint')
    for gate in reversed(word):
        state[gate[1]] ^= common if gate[0] == 'P' else state[gate[2]]
    need(state == [1 << i for i in range(n)], 'literal inverse')
    forest_bill = sum(mu[i] if j is None else 2*add[i][j] for i,j in enumerate(parents))
    cost = rational(certificate['cost'])
    need(bill == forest_bill == cost == sum(weights), 'primal dual equality')
    # Laminarity is an optimizer property, deliberately not a validity premise.
    return dict(cost=str(cost), rows=n, cuts=len(weights),
                oracles=sum(g[0] == 'P' for g in word),
                adds=sum(g[0] == 'ADD' for g in word), inequalities=n*n)


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tariffs', type=Path)
    parser.add_argument('certificate', type=Path)
    args = parser.parse_args()
    def unique(pairs):
        result = {}
        for key,value in pairs:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    data = json.loads(args.tariffs.read_bytes(), object_pairs_hook=unique)
    need(set(data) == {'mu','add'}, 'tariff fields')
    def parse(v):
        need(type(v) in (int,str), 'exact JSON tariff')
        return Fraction(v)
    mu = list(map(parse, data['mu']))
    add = [[None if v is None else parse(v) for v in row] for row in data['add']]
    result = check(mu, add, json.loads(args.certificate.read_bytes(),object_pairs_hook=unique))
    print('PASS_DIRTY_FANOUT_CUT_CERTIFICATE', json.dumps(result,sort_keys=True))
