"""Exact signed rank transport in the pinned three-register Clifford model.

The general theorem is in PROOF.md. Potential values do not certify endpoints.
Apache-2.0; substantial OpenAI Codex assistance; see NOTICE.md.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import permutations

from field import E, ZERO, ONE
import model


def require(condition, message):
    if not condition:
        raise ValueError(message)


def determinant(matrix):
    total = ZERO
    for p in permutations(range(3)):
        term = E((-1)**sum(p[i] > p[j] for i in range(3) for j in range(i+1, 3)))
        for r, c in enumerate(p):
            term *= matrix[3*r+c]
        total += term
    return total


def inverse_matrix(matrix):
    d = determinant(matrix)
    require(bool(d), 'Singular scalar block')
    out = []
    for r in range(3):
        for c in range(3):
            rr = [i for i in range(3) if i != c]
            cc = [i for i in range(3) if i != r]
            minor = (matrix[3*rr[0]+cc[0]]*matrix[3*rr[1]+cc[1]]
                     - matrix[3*rr[0]+cc[1]]*matrix[3*rr[1]+cc[0]])
            out.append(((-1)**(r+c))*minor/d)
    return tuple(out)


def inverse_word(word):
    result = []
    for gate in reversed(word):
        if gate[0] == 'mix3':
            result.append(('mix3', *inverse_matrix(gate[1:])))
        elif gate[0] == 'free':
            result.extend([gate]*(3 if gate[2] < 3 else 1))
        else:
            # C_v^2=X_v and C_v^-1=C_v X_v, with X_v free.
            result.append(gate)
            result.extend(('free', gate[1], 3+bit) for bit in range(3) if gate[2] >> bit & 1)
    return tuple(result)


@lru_cache(maxsize=10000)
def inverse_group(g):
    """Invert signed Pauli conjugation, including its central i phases."""
    result = [None]*6
    for v in range(1, 64):
        x = z = p = 0
        for bit in range(6):
            if v >> bit & 1:
                a = g[bit]
                ax, az, ap = a & 7, (a >> 3) & 7, a >> 6
                p = (p+ap+2*((z & ax).bit_count() % 2)) % 4
                x ^= ax
                z ^= az
        unsigned = x | (z << 3)
        if unsigned and unsigned & (unsigned-1) == 0:
            result[unsigned.bit_length()-1] = v | (((-p) % 4) << 6)
    require(all(x is not None for x in result), 'Invalid Pauli action')
    return tuple(result)


def point(word, independent=False):
    word = tuple(word)
    for gate in word:
        if gate[0] == 'mix3':
            require(len(gate) == 10, 'Wrong scalar block size')
        else:
            require(len(gate) == 3 and gate[0] in ('paid', 'free'), 'Unknown unary gate')
            require(type(gate[1]) is int and 0 <= gate[1] < 3, 'Invalid register')
            require(type(gate[2]) is int and
                    (1 <= gate[2] <= 7 if gate[0] == 'paid' else 0 <= gate[2] < 18),
                    'Invalid unary operator')
    ring = model.Engine()
    rows = model.execute(ring, word)
    back = inverse_word(word)
    inverse = model.execute(ring, back)
    if independent:
        import dense
        for program, wanted in ((word, rows), (back, inverse)):
            actual = dense.execute(program)
            symbolic = [{(key & 3, ring.groups[key >> 2]): E.cast(value)
                         for key, value in row.items()} for row in wanted]
            require(actual == symbolic, 'Independent dense coefficient mismatch')
        # Full formal identities, rather than only the identity coefficient.
        for program in (word+back, back+word):
            engine = model.Engine()
            actual = model.execute(engine, program)
            require(actual == ({0: ONE}, {1: ONE}, {2: ONE}), 'Forward/inverse identity failed')
    potential = Q(0)
    row_mass = [ZERO]*3
    negative = [Q(0)]*3
    weights = []
    forward_norm = [sum((E.cast(a).norm() for a in row.values()), Q(0)) for row in rows]
    inverse_norm = [sum((E.cast(a).norm() for row in inverse for key, a in row.items()
                        if key & 3 == r), Q(0)) for r in range(3)]
    for r, row in enumerate(rows):
        for key, a in row.items():
            col, group = key & 3, key >> 2
            gid = ring.ids.get(inverse_group(ring.groups[group]))
            b = inverse[col].get((gid << 2) | r, ZERO) if gid is not None else ZERO
            mass = E.cast(a)*b
            rank = model.fourier_rank(ring.groups[group])
            row_mass[r] += mass
            negative[r] += max(Q(0), -mass.real())
            potential += rank*mass.real()
            weights.append((r, col, ring.groups[group], mass, rank))
    require(row_mass == [ONE]*3, 'Forward/inverse row mass is not one')
    return {'potential': potential, 'negative': negative, 'weights': weights,
            'condition_squared': [a*b for a, b in zip(forward_norm, inverse_norm)],
            'endpoint': model.endpoint_frames(ring, rows),
            'terms': sum(map(len, rows))}


def audit(word, independent=False):
    """Exact prefix budget; a rank-one paid call has delta <= 1+2*N_before."""
    before = point((), independent)
    paid, controls = [], 0
    for i, gate in enumerate(word):
        after = point(word[:i+1], independent)
        delta = after['potential']-before['potential']
        if gate[0] == 'paid':
            negativity = before['negative'][gate[1]]
            condition_squared = before['condition_squared'][gate[1]]
            require(abs(delta) <= 1+2*negativity, 'Signed paid-call budget failed')
            require(delta*delta <= condition_squared, 'Coefficient-norm paid-call budget failed')
            paid.append({'gate': i, 'delta': str(delta), 'negative_before': str(negativity),
                         'condition_squared': str(condition_squared)})
        else:
            require(delta == 0, 'Free scalar/monomial step changed rank potential')
            controls += 1
        before = after
    require(sum(Q(p['delta']) for p in paid) == before['potential'], 'Telescoping mismatch')
    total_negative = sum(Q(p['negative_before']) for p in paid)
    if before['endpoint'] is not None:
        require(before['potential'] == 9, 'Full-rank endpoint potential mismatch')
        require(2*total_negative >= 9-len(paid), 'Necessary negativity threshold failed')
    return {'potential': str(before['potential']), 'paid_calls': len(paid),
            'paid_negative_mass': str(total_negative), 'endpoint': before['endpoint'],
            'paid_steps': paid, 'free_steps_checked': controls, 'prefixes': len(word)+1}


def check_metrics(matrices, metrics):
    """Check B_k* D_{k+1} B_k = D_k with strictly positive diagonal D_k."""
    require(len(metrics) == len(matrices)+1, 'Wrong metric count')
    require(all(len(d) == 3 and all(type(x) is int or isinstance(x, Q) for x in d)
                and min(d) > 0 for d in metrics), 'Metrics must be positive exact rationals')
    for k, matrix in enumerate(matrices):
        require(len(matrix) == 9, 'Wrong matrix size')
        for i in range(3):
            for j in range(3):
                value = sum((E.cast(matrix[3*r+i]).conjugate()*metrics[k+1][r]
                             *matrix[3*r+j] for r in range(3)), ZERO)
                require(value == E(metrics[k][i] if i == j else 0),
                        'Diagonal metric transport identity failed')
    return True
