"""Retained native replay with explicit compiler and checker inputs.

Ali Romman; David Arias; Cinna Davis; Gareth Davidson. Apache-2.0.
The only interface change is native(w,C,V); its checks are unchanged.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import json
def need(ok, why):
    if not ok:
        raise ValueError(why)

def span(basis):
    out = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and (v not in out), 'Independent binary basis')
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)

def native(w, C, V):
    n = w['public']

    @lru_cache(None)
    def chart(i):
        return C.canonical_frame(9, tuple(w['frames'][i]))
    recipes = {}

    def check(a, b):
        if (a, b) not in recipes:
            recipe, _ = C.lower_child(chart(a).adjoint().then(chart(b)))
            expected = V.adjoint(V.frame(w['frames'][a], 9)) + V.frame(w['frames'][b], 9)
            V.equal(V.recipe(recipe), expected, 'Native chart change and exact global phase')
            need(recipe['rank'] == abs(len(w['frames'][a]) - len(w['frames'][b])), 'Native boundary rank')
            recipes[a, b] = recipe
        return recipes[a, b]
    for e in w['program']:
        if e[0] == 'MOVE':
            check(e[2], e[3])
    main = set(w['live']) | {r + 112 for r in w['live']}
    helper_profile = Counter()
    for r in range(n):
        if r not in main:
            helper_profile[check(w['initial'][r], w['final'][r])['rank']] += 1
    adapters = []
    for r, q in zip(w['live'], w['ports']):
        need(w['frames'][w['initial'][r]] == [q], 'Literal central port')
        need(span(w['frames'][w['final'][r + 112]]) == frozenset((x for x in range(512) if not (x & q).bit_count() % 2)), 'Literal output hyperplane')
        tests = [(C.cgate(9, q, 1).adjoint().then(chart(w['initial'][r])), V.adjoint((('C', q, 1),)) + V.frame(w['frames'][w['initial'][r]], 9)), (chart(w['final'][r + 112]).adjoint().then(C.cgate(9, q, -1).then(C.fourier(9))), V.adjoint(V.frame(w['frames'][w['final'][r + 112]], 9)) + (('C', q, -1),) + V.fourier(9))]
        for actual, expected in tests:
            recipe, _ = C.lower_child(actual)
            need(recipe['rank'] == 0, 'Free intrinsic main adapter')
            V.equal(V.recipe(recipe), expected, 'Main endpoint phase')
            adapters.append(recipe)
    bad = json.loads(json.dumps(next(iter(recipes.values()))))
    bad['left']['phase'] = (bad['left']['phase'] + 1) % 4
    a, b = next(iter(recipes))
    try:
        V.equal(V.recipe(bad), V.adjoint(V.frame(w['frames'][a], 9)) + V.frame(w['frames'][b], 9), 'Wrong phase control')
    except ValueError:
        pass
    else:
        raise ValueError('Wrong native phase accepted')
    payload = [[a, b, recipes[a, b]] for a, b in sorted(recipes)] + adapters
    return {'distinct_maps': len(recipes), 'main_adapters': len(adapters), 'helper_normalizers': 2 * sum(helper_profile.values()), 'helpers': dict(helper_profile), 'recipe_payload_sha256': sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest(), 'wrong_phase_rejected': True, 'proof': 'Every signed Pauli image and exact global phase; frame induction at every positive tensor width'}
