"""Finite controls for the written all-p proofs; not a formal proof kernel.

Apache-2.0. Cinna Davis, with substantial OpenAI Codex assistance.
"""
import algebra as A
import ast
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dot(row, column):
    return (row & column).bit_count() % 2


def outer(column, row, n):
    return [row if column >> i & 1 else 0 for i in range(n)]


def apply(matrix, column):
    return sum(dot(row, column) << i for i, row in enumerate(matrix))


def check():
    paid = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
    source = Path(__file__).resolve().parents[1] / 'query-thinned-controllers/controller.py'
    literals = []
    for node in ast.walk(ast.parse(source.read_text())):
        if isinstance(node, ast.Assign):
            try:
                literals.append(ast.literal_eval(node.value))
            except (ValueError, TypeError):
                pass
    need(paid in literals and {8: 439} in literals, 'Actual pinned BIT inventory')
    need(sum(r*c for r, c in paid.items()) - 439*8 - 2*111*7 == 63,
         'Owned center debt is included')
    product = 1
    for r, count in paid.items():
        product *= r**count
    need(8**661 > product, 'Exact uniform positivity of B derivative')
    need(661*8 - sum(r*c for r, c in paid.items()) - 111 == 48,
         'Exact endpoint of all-t BIT bound')
    # Independently enumerate every nonzero rank-one nilpotent on two coordinates.
    nilpotents = set()
    for u in range(1, 4):
        for v in range(1, 4):
            if not dot(v, u):
                nilpotents.add(tuple(outer(u, v, 2)))
    need(nilpotents == {(2, 0), (0, 1), (3, 3)}, 'Three edge types')
    alphabet = sorted(nilpotents)
    for mask in range(8):
        rows = [0, 0]
        for i, item in enumerate(alphabet):
            if mask >> i & 1:
                rows = [x ^ y for x, y in zip(rows, item)]
        zero_offdiagonal = not (rows[0] & 2 or rows[1] & 1)
        need(zero_offdiagonal == (mask in (0, 7)), 'Complete edge parity table')
        if mask == 7:
            need(rows == [1, 2], 'Three calls contribute identity on their edge')
    pair_cases = interior_cases = endpoint_cases = 0
    for n in range(2, 65, 2):
        ones = (1 << n) - 1
        u = [1 << i for i in range(n)] + [ones]
        v = [ones ^ (1 << i) for i in range(n)] + [ones]
        need(all(dot(v[i], u[j]) == int(i != j)
                 for i in range(n+1) for j in range(n+1)), 'Simplex frame pairings')
        pair_cases += (n+1)**2
        projectors, sums_u, sums_v = {}, {}, {}
        for s in range(1, n):
            us = vs = 0
            for j in range(s+1, n+1):
                us ^= u[j]
                vs ^= v[j]
            sums_u[s], sums_v[s] = us, vs
            k = n-s
            gram = [dot(v[s], u[s]), dot(v[s], us), dot(vs, u[s]), dot(vs, us)]
            need(gram == [0, k % 2, k % 2, 0], 'Forced image/row-space pairing')
            if not k % 2:
                continue
            p = [a ^ b for a, b in zip(outer(u[s], vs, n), outer(us, v[s], n))]
            need(apply(p, u[s]) == u[s] and apply(p, us) == us,
                 'Odd interior projector is rank two and idempotent')
            projectors[s] = p
            interior_cases += 1
            if s > 1:
                w, z = u[s] ^ us, v[s] ^ vs
                need(w not in (0, u[0]) and z not in (0, v[0]), 'Initial forced pairs independent')
                need(not any(dot(a, b) for a in (v[0], z) for b in (u[0], w)),
                     'Initial endpoint pairing obstruction')
                endpoint_cases += 1
            if s < n-1:
                need(us not in (0, u[n]) and vs not in (0, v[n]), 'Final forced pairs independent')
                need(not any(dot(a, b) for a in (v[n], vs) for b in (u[n], us)),
                     'Final endpoint pairing obstruction')
                endpoint_cases += 1
        for s in projectors:
            for t in projectors:
                if s >= t:
                    continue
                ps, pt = projectors[s], projectors[t]
                need(apply(ps, u[t]) == sums_u[s], 'Earlier projector response')
                need(apply(pt, sums_u[s]) == 0 and apply(pt, u[t]) == u[t],
                     'Distinct interior projectors do not commute')
        if n == 2:
            need(projectors[1] == [1, 2], 'Three-call n=2 exception remains valid')
    # A two-native-call/five-query word saturates the all-p native upper bound.
    sharp = A.stats(A.literal(24, [7, 0, 39, 832, 384]))
    need(sharp['central_query_on_every_output'] and sharp['coefficient_rank_sum'] == 4,
         'Actual sharp n=4/f=2 word factors')
    return {'status': 'PASS_GLOBAL_BINARY_CONTROLLER_PROOF_CONTROLS',
            'largest_main_field_count': 64, 'simplex_pairings': pair_cases,
            'odd_projectors': interior_cases, 'endpoint_obstructions': endpoint_cases,
            'all_full_edge_parity_patterns': 8, 'minimum_query_native_bound_sharp': True,
            'bit_all_concave_moments_upper': -15,
            'log_product_inequality_exact': True, 'formal_kernel': False}


if __name__ == '__main__':
    import json
    print(json.dumps(check(), sort_keys=True))
