"""Independent dense left-regular representation and symbolic proof checks.

Group elements here are actual two-by-two binary matrices, not permutation
table entries. Register projectors are enumerated as matrices, not outer pairs.
Every regular-representation column is retained; this representation of the
formal group algebra is faithful.
"""

import itertools


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parity(n):
    return n.bit_count() % 2


def apply(rows, x):
    return sum(parity(row & x) << i for i, row in enumerate(rows))


def multiply(left, right):
    """Exact matrix product from packed binary rows."""
    rows = []
    for mask in left:
        out = 0
        for i, row in enumerate(right):
            if mask >> i & 1:
                out ^= row
        rows.append(out)
    return tuple(rows)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            lead = row.bit_length()-1
            if lead in pivots:
                row ^= pivots[lead]
            else:
                pivots[lead] = row
                break
    return len(pivots)


def unit(n):
    return tuple(1 << i for i in range(n))


def address_group():
    candidates = (rows for rows in itertools.product(range(4), repeat=2)
                  if rank(rows) == 2)
    return tuple(sorted(candidates, key=lambda rows: tuple(apply(rows, x)-1
                                                         for x in (1, 2, 3))))


GROUP = address_group()
INDEX = {g: i for i, g in enumerate(GROUP)}
ID = (1, 2)
A = (3, 2)
B = (1, 3)
S = (2, 1)


def projectors(r):
    return tuple(n for n in itertools.product(range(1 << r), repeat=r)
                 if rank(n) == 1 and multiply(n, n) == n)


def represented_gate(n, g):
    r = len(n)
    out = list(unit(6*r))
    for i in range(r):
        for j in range(r):
            if n[i] >> j & 1:
                for h, matrix in enumerate(GROUP):
                    k = INDEX[multiply(g, matrix)]
                    out[6*i+h] ^= 1 << (6*j+h)
                    out[6*i+k] ^= 1 << (6*j+h)
    return tuple(out)


def formal_encoding(rows, r):
    """Recover coefficients from action on each register's identity basis."""
    eid = INDEX[ID]
    out = 0
    for i in range(r):
        for j in range(r):
            coefficient = sum(((rows[6*i+k] >> (6*j+eid)) & 1) << k
                              for k in range(6))
            out |= coefficient << (6*(i*r+j))
    return out


def dense_ball(r):
    gates = tuple(represented_gate(n, g) for n in projectors(r) for g in (A, B))
    states = {unit(6*r)}
    layer = states.copy()
    layers = [1]
    attempts = 0
    for _ in range(3):
        new = set()
        for state in layer:
            for gate in gates:
                attempts += 1
                nxt = multiply(gate, state)
                if nxt not in states:
                    new.add(nxt)
        states.update(new)
        layer = new
        layers.append(len(new))
    encoded = {formal_encoding(state, r) for state in states}
    require(len(encoded) == len(states), 'regular coefficient recovery not injective')
    return encoded, {'exact_distance_layers_0_to_3': layers,
                     'directed_transition_attempts': attempts,
                     'regular_dimension': 6*r}


def coefficient_polynomials(labels):
    """Expand product (I+([g]+1)N_i) over noncommuting indeterminates N_i.

Each group coefficient is a set of monomials (tuples of scalar-factor
indices), with symmetric difference performing addition in F2.
"""
    result = {g: set() for g in GROUP}
    result[ID].add(())
    for i, label in enumerate(labels):
        out = {g: set(poly) for g, poly in result.items()}
        for g, poly in result.items():
            for monomial in poly:
                term = monomial + (i,)
                for h in (g, multiply(g, label)):
                    if term in out[h]:
                        out[h].remove(term)
                    else:
                        out[h].add(term)
        result = out
    return result


def proof_checks():
    # Address matrices act as all permutations of the three nonzero vectors.
    require(len(GROUP) == 6 and GROUP[0] == ID, 'address group enumeration')
    require(multiply(multiply(A, B), A) == S, 'aba is not swap')
    require(multiply(multiply(B, A), B) == S, 'bab is not swap')
    require(multiply(A, B) != multiply(B, A), 'lost noncommutativity')
    cases = []
    for length in (0, 1, 2, 3, 4):
        for labels in itertools.product((A, B), repeat=length):
            poly = coefficient_polynomials(labels)
            text = ''.join('a' if g == A else 'b' for g in labels)
            if length <= 2:
                require(not poly[S], 'short word unexpectedly supports swap')
                method = 'swap coefficient zero'
            elif length == 3:
                if text in ('aba', 'bab'):
                    require(poly[S] == {(0, 1, 2)}, 'three-call coefficient identity')
                    method = 'swap coefficient has rank at most one'
                else:
                    require(not poly[S], 'nonalternating triple supports swap')
                    method = 'swap coefficient zero'
            elif text in ('abab', 'baba'):
                other = multiply(labels[1], labels[0])
                require(poly[S] ^ poly[other] == {(1, 2)},
                        'alternating coefficient obstruction identity')
                method = 'swap plus reverse-pair coefficient is N1 N2'
            else:
                # In three runs one block has length two; its expansion is a
                # sum of two triple products with a common exterior factor.
                if not poly[S]:
                    method = 'swap coefficient zero'
                else:
                    terms = sorted(poly[S])
                    require(all(len(t) == 3 for t in terms), 'run coefficient degree')
                    require(len(terms) == 2, 'run coefficient term count')
                    require(terms[0][0] == terms[1][0] or
                            terms[0][-1] == terms[1][-1],
                            'rank-one exterior factor missing')
                    method = 'swap coefficient has a common rank-one exterior factor'
            cases.append({'word': text, 'identity': method})
    # Verify the sign quotient on every group product. Encode 1 as zero parity,
    # t=1+epsilon as one parity; epsilon^2=0 in characteristic two.
    def sign(g):
        values = [apply(g, x) for x in (1, 2, 3)]
        return sum(values[i] > values[j] for i in range(3)
                   for j in range(i+1, 3)) % 2
    for g, h in itertools.product(GROUP, repeat=2):
        require(sign(multiply(g, h)) == sign(g) ^ sign(h), 'sign is not a homomorphism')
    require(sign(A) == sign(B) == sign(S) == 1, 'paid/target sign mismatch')
    return {'symbolic_label_patterns_through_four': len(cases),
            'sign_homomorphism_products': 36,
            'four_call_patterns': [c for c in cases if len(c['word']) == 4]}


def scalar_checks():
    # All GL(3,2) conjugations preserve exactly the allowed projector set.
    r = 3
    proj = set(projectors(r))
    invertible = [rows for rows in itertools.product(range(8), repeat=3)
                  if rank(rows) == 3]
    inverses = {m: next(n for n in invertible if multiply(m, n) == unit(r))
                for m in invertible}
    checks = 0
    for matrix in invertible:
        for n in proj:
            require(multiply(multiply(matrix, n), inverses[matrix]) in proj,
                    'scalar conjugation leaves generator domain')
            require(sum(n[i] >> i & 1 for i in range(r)) % 2 == 1,
                    'rank-one idempotent trace is not one')
            checks += 1
    return {'gl3_matrices': len(invertible), 'rank_one_idempotents': len(proj),
            'conjugations': checks}
