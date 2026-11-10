"""Independent reverse-functional oracle; no constructor imports.

Integer coefficients retain formal S**2=1 as a free rank-two algebra.
This checks an abstract atomic-body interface, not physical admission.
"""
from collections import Counter
from hashlib import sha256
import json

ONE = {(0, 0, 0): 1}
S = {(0, 0, 1): 1}
L = {(1, 0, 0): 1}
R = {(0, 1, 0): 1}

def add(a, b):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0) + value
    return {k: v for k, v in out.items() if v}

def mul(a, b):
    out = {}
    for (al, ar, ass), av in a.items():
        for (bl, br, bs), bv in b.items():
            key = al + bl, ar + br, (ass + bs) % 2
            out[key] = out.get(key, 0) + av * bv
    return {k: v for k, v in out.items() if v}

def scale(a, c):
    return {k: v*c for k, v in a.items() if v*c}

# Independently derived plane-word normalization, X,Y,A,B,E,F all arbitrary.
WORD = [
    ('idle',0,L),('idle',1,L),('native',2,3,L),
    ('query',3,2,-1),('query',2,3,1),('swap',2,3),('scale',2,-1),
    ('native',0,1,R),('idle',4,R),('idle',5,R),
]
# Author's literal positive-query program, copied from the displayed gate list.
AUTHOR_WORD = [
    ('idle',0,L),('idle',1,L),('native',3,2,L),('scale',2,-1),
    ('query',2,3,1),('add',2,3,-1),('add',3,2,1),('query',2,3,1),
    ('scale',2,-1),('add',2,3,1),('native',0,1,R),('idle',4,R),('idle',5,R),
]

def pullback(word):
    answer = []
    for output in range(6):
        row = [{} for _ in range(6)]
        row[output] = ONE.copy()
        for gate in reversed(word):
            op = gate[0]
            if op == 'idle':
                _, target, body = gate
                row[target] = mul(row[target], body)
            elif op == 'native':
                _, target, source, body = gate
                old_target, old_source = row[target], row[source]
                row[target] = mul(old_target, body)
                row[source] = mul(add(old_source, mul(S, old_target)), body)
            elif op in ('query', 'add'):
                _, target, source, coefficient = gate
                multiplier = S if op == 'query' else ONE
                row[source] = add(row[source], scale(mul(row[target], multiplier), coefficient))
            elif op == 'swap':
                _, a, b = gate
                row[a], row[b] = row[b], row[a]
            elif op == 'scale':
                _, target, coefficient = gate
                row[target] = scale(row[target], coefficient)
            else:
                raise ValueError(op)
        answer.append(row)
    return answer

def expected():
    result = [[{} for _ in range(6)] for _ in range(6)]
    result[0][0] = mul(L, R)
    result[0][1] = mul(S, mul(L, R))
    result[1][1] = mul(L, R)
    result[2][2] = mul(S, L)
    result[3][3] = mul(S, L)
    result[4][4] = R
    result[5][5] = R
    return result

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def normalized(counter):
    return {k: v for k, v in counter.items() if v}

def main():
    target = expected()
    require(pullback(WORD) == target, 'Independent plane-word endpoint')
    require(pullback(AUTHOR_WORD) == target, 'Author complete formal endpoint')
    inventory = Counter(g[0] for g in AUTHOR_WORD)
    require((inventory['native'],inventory['query'],inventory['idle']) == (2,2,4), 'Paid inventory')
    mutations = {}
    for label, position in [('omit_first_query',4),('omit_second_query',7),
                            ('omit_old_active_L',1),('omit_fresh_R',12),('omit_final_sign',8)]:
        changed = AUTHOR_WORD[:position] + AUTHOR_WORD[position+1:]
        require(pullback(changed) != target, label+' was accepted')
        mutations[label] = 'rejected'
    changed = list(WORD)
    changed[3] = ('query',3,2,1)
    require(pullback(changed) != target, 'Wrong lower-query sign')
    mutations['wrong_lower_sign'] = 'rejected'
    changed = list(AUTHOR_WORD)
    changed.insert(10, ('idle',2,R))
    require(pullback(changed) != target, 'Old auxiliary not retired')
    mutations['unfragmented_old_auxiliary'] = 'rejected'
    old = Counter({'h(a+b+1)':2,'h(a+b)':-2,'h(1)':-1})
    new = Counter({'h(a+1)':2,'h(b)':2})
    new.subtract(Counter({'h(a)':2,'h(b)':2,'h(1)':2}))
    require(normalized(new) == {'h(a+1)':2,'h(a)':-2,'h(1)':-2}, 'New node excess')
    delta = new.copy()
    delta.subtract(old)
    require(normalized(delta) == {'h(a+1)':2,'h(a)':-2,'h(a+b+1)':-2,'h(a+b)':2,'h(1)':-1}, 'Replacement gain')
    bad = new.copy()
    bad['h(b)'] += 2
    require(normalized(bad) != normalized(new), 'Missing fresh-idle charge')
    mutations['missing_fresh_idle_charge'] = 'rejected'
    encoded = [[[list(k)+[v] for k,v in sorted(p.items())] for p in row] for row in target]
    result = {'status':'PASS_INDEPENDENT_REVERSE_FOUR_QUERY',
              'all_arbitrary_input_coefficients':36,'native_children':2,'thin_queries':2,'paid_idles':4,
              'new_node_excess':'2*i(a)-2','replacement_gain':'2*(i(a)-i(a+b))-1',
              'endpoint_sha256':sha256(json.dumps(encoded,sort_keys=True).encode()).hexdigest(),
              'controls':mutations,
              'scope':'Formal central S, independent commuting L/R, scalar channels; no physical admission or new kappa'}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == '__main__':
    main()
